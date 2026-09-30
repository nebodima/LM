"""Агент конфигуратора 1С (/AgentMode) для файловой или серверной базы (tools\\адрес_базы.py): запуск, команды по SSH, остановка.

Зачем: пакетный запуск конфигуратора стоит ~6 с только на старт; агент держит конфигуратор запущенным,
команды идут по SSH за доли секунды (эталон — C:\\1c_run\\designer_agent\\README.md, проект DO_3).
Грабли оттуда учтены:
  * папка агента (/AgentBaseDir) — только ASCII-путь: %TEMP%\\uz_agent\\UZ_UNF_D (по имени папки базы);
  * порт — свободный из 1546–1560; занятый порт проверяется по pid владельца (1543 — агент DO_3, 1545 — ras),
    чужой агент не используется никогда — иначе молча подключишься к чужой базе;
  * процесс стартует отвязанным (без наследования stdout), иначе конвейер «деплой | Out-String» висит;
  * SSH без PTY (open_session + invoke_shell), конец ответа — приглашение «designer> »; вход сразу после
    прошлой сессии иногда отказывает — до 5 попыток; каждая сессия начинается с common connect-ib;
  * после config update-db-cfg агент следующую load-files не выполняет («UnknownError») — перезапускать.
Ошибка команды определяется по формату ответа агента: строка вида «Ошибка ConfigFilesError - …», а не по словам.

Агенты не висят вечно (28.09.2026 насчитали 15 процессов 1cv8 — лицензии кончились, прогоны падали 0xC0000409
«Ключ защиты программы больше не доступен»). Вместе с агентом стартует СТОРОЖ — отвязанный процесс python:
раз в 15 с смотрит отметку активности (%TEMP%\\uz_agent\\<база>\\активность — её трогают старт и каждая команда);
агент без команд дольше --простой минут (по умолчанию 10; переменная UZ_АГЕНТ_ПРОСТОЙ_МИН) — остановлен, сторож
выходит. Сторож выходит и сам, если его агента уже нет или агент базы заменён новым (у нового свой сторож).
Страховка на случай убитого сторожа: каждый старт агента останавливает простаивающих агентов других баз.
Трогаются ТОЛЬКО свои агенты: процесс 1cv8 в /AgentMode, база C:\\1c_bases\\UZ_* или серверная uz_*, папка агента в %TEMP%\\uz_agent.
Агент DO_3 (docmngr3, порт 1543), пакетные конфигураторы и всё прочее — только в списке, «чужой», не останавливаются.

    python tools\\агент_конфигуратора.py старт  --база=C:\\1c_bases\\UZ_UNF_D [--пользователь=Администратор] [--простой=10]
    python tools\\агент_конфигуратора.py команды --база=… "config load-files --dir=…" "config update-db-cfg --extension=УЗ_ext"
    python tools\\агент_конфигуратора.py стоп   --база=…
    python tools\\агент_конфигуратора.py список                     — все процессы 1cv8: свои агенты (простой, сторож) и чужие
    python tools\\агент_конфигуратора.py остановить --все | --база=…  — свои агенты (ручное управление: tools\\агенты.ps1)
Код выхода 0 — всё выполнено, 1 — ошибка команды или агент недоступен (деплой тогда идёт пакетно).
Таймаут команды — --таймаут=сек (по умолчанию 60), каждая команда печатается с временем.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import адрес_базы
import платформа

EXE = платформа.exe()    # линия выбирается --платформа=8.3|8.5 / UZ_ПЛАТФОРМА (tools\платформа.py)
ПОРТЫ = range(1546, 1561)
ПРИГЛАШЕНИЕ = "designer> "
ОШИБКА = re.compile(r"^Ошибка \w+ - ", re.M)
КОРЕНЬ = os.path.join(tempfile.gettempdir(), "uz_agent")
БАЗЫ_СВОИ = os.path.normcase("C:\\1c_bases\\UZ_")      # чужое (не C:\1c_bases\UZ_*) не трогаем никогда
ПРОСТОЙ_МИН = float(os.environ.get("UZ_АГЕНТ_ПРОСТОЙ_МИН", "10"))
ОПРОС_СТОРОЖА = 15


def аргумент(имя, по_умолчанию=None):
    for а in sys.argv[1:]:
        if а.startswith("--%s=" % имя):
            return а.split("=", 1)[1]
    return по_умолчанию


def папка(база):
    п = os.path.join(tempfile.gettempdir(), "uz_agent", адрес_базы.имя(база))
    п.encode("ascii")          # кириллица в пути агента — «Directory access violation» при load-files
    os.makedirs(п, exist_ok=True)
    return п


def _состояние(база):
    try:
        return json.load(open(os.path.join(папка(база), "агент.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _слушает(порт):
    """pid процесса, который слушает порт на 127.0.0.1/0.0.0.0, или None."""
    import psutil
    for с in psutil.net_connections("tcp"):
        if с.laddr and с.laddr.port == порт and с.status == psutil.CONN_LISTEN:
            return с.pid
    return None


def живой(база):
    """Порт своего агента этой базы, если он запущен и порт слушает именно его pid; иначе None."""
    с = _состояние(база)
    if с.get("база") != адрес_базы.ключ(база):
        return None
    return с.get("порт") if с.get("pid") and _слушает(с.get("порт", 0)) == с["pid"] else None


def _ждать_порт(порт, pid, сек):
    срок = time.time() + сек
    while time.time() < срок:
        владелец = _слушает(порт)
        if владелец == pid:
            return True
        if владелец is not None:
            raise RuntimeError("агент: порт %d занял чужой процесс pid %d" % (порт, владелец))
        time.sleep(0.25)
    return False


def активность(база):
    """Отметка «агентом пользовались сейчас» — по ней сторож считает простой."""
    with open(os.path.join(папка(база), "активность"), "w", encoding="utf-8") as ф:
        ф.write(time.strftime("%d.%m.%Y %H:%M:%S"))


def _записать_состояние(база, с):
    with open(os.path.join(папка(база), "агент.json"), "w", encoding="utf-8") as ф:
        json.dump(с, ф, ensure_ascii=False)


def старт(база, пользователь, ждать=True, простой=None):
    """Порт агента базы (свой живой — переиспользуется). Вместе с агентом — сторож простоя."""
    простой = ПРОСТОЙ_МИН if простой is None else float(простой)
    try:
        _уборка_простаивающих(база)
    except Exception as е:              # уборка — страховка, старт агента из-за неё не падает
        print("агент: уборка простаивающих не выполнилась: %s" % е)
    порт = _старт(база, пользователь, ждать)
    активность(база)
    с = _состояние(база)
    с["простой_мин"] = простой
    _записать_состояние(база, с)
    if простой > 0:                   # 0 — агента остановит сам вызывающий (деплой -ПростойАгента 0), сторож не нужен
        _сторож_запустить(база)
    return порт


def _старт(база, пользователь, ждать):
    порт = живой(база)
    if порт:
        return порт
    # агент, запущенный в фоне прошлым деплоем, может ещё подниматься (~5 с): процесс жив, порт пока не слушает —
    # дождаться его, а не убивать и стартовать заново
    import psutil
    с = _состояние(база)
    if (с.get("база") == адрес_базы.ключ(база) and с.get("pid") and psutil.pid_exists(с["pid"])
            and psutil.Process(с["pid"]).name().lower().startswith("1cv8") and _слушает(с.get("порт", 0)) is None):
        if not ждать or _ждать_порт(с["порт"], с["pid"], 20):
            return с["порт"]
    остановить(база)
    with _замок_портов():
        # параллельный деплой трёх баз: без общего замка два агента выбрали бы один «свободный» порт.
        # Порт, выданный агенту, который ещё поднимается (не слушает), тоже занят — берём из агент.json всех баз
        занятые = _порты_других_агентов(база)
        свободные = [п for п in ПОРТЫ if п not in занятые and _слушает(п) is None]
        if not свободные:
            raise RuntimeError("агент: нет свободного порта в %d–%d" % (ПОРТЫ[0], ПОРТЫ[-1]))
        порт = свободные[0]
        п = _запустить(база, пользователь, порт)
    if not ждать or _ждать_порт(порт, п.pid, 20):
        return порт
    raise RuntimeError("агент: за 20 с не начал слушать порт %d" % порт)


def _запустить(база, пользователь, порт):
    платформа.проверить_базу(база)       # метка платформы базы: другой линией не открываем
    аргументы = [EXE, "DESIGNER"] + адрес_базы.ключи_конфигуратора(база) + ["/N", пользователь, "/DisableStartupDialogs",
                 "/DisableStartupMessages", "/AgentMode", "/AgentPort", str(порт), "/AgentListenAddress",
                 "127.0.0.1", "/AgentBaseDir", папка(база), "/AgentSSHHostKeyAuto"]
    флаги = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    п = subprocess.Popen(аргументы, creationflags=флаги, close_fds=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import psutil
    _записать_состояние(база, {"база": адрес_базы.ключ(база), "пользователь": пользователь,
                               "порт": порт, "pid": п.pid, "создан": psutil.Process(п.pid).create_time()})
    return п


class _замок_портов:
    """Замок выбора порта на всю машину: %TEMP%\\uz_agent\\порты.lock, байт 0 (ждём до 30 с)."""
    def __enter__(self):
        import msvcrt
        os.makedirs(os.path.join(tempfile.gettempdir(), "uz_agent"), exist_ok=True)
        self.ф = open(os.path.join(tempfile.gettempdir(), "uz_agent", "порты.lock"), "a+")
        self.ф.seek(0)
        срок = time.time() + 30
        while True:
            try:
                msvcrt.locking(self.ф.fileno(), msvcrt.LK_NBLCK, 1)
                return self
            except OSError:
                if time.time() > срок:
                    raise RuntimeError("агент: замок выбора порта занят дольше 30 с")
                time.sleep(0.1)

    def __exit__(self, *исключение):
        self.ф.close()


def _порты_других_агентов(база):
    """Порты живых агентов других баз по их агент.json (агент мог ещё не начать слушать)."""
    import psutil
    своя = os.path.normcase(os.path.abspath(папка(база)))
    итог = set()
    корень = os.path.join(tempfile.gettempdir(), "uz_agent")
    for имя in os.listdir(корень):
        путь = os.path.join(корень, имя, "агент.json")
        if os.path.normcase(os.path.join(корень, имя)) == своя or not os.path.exists(путь):
            continue
        try:
            с = json.load(open(путь, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if с.get("pid") and psutil.pid_exists(с["pid"]):
            итог.add(с.get("порт"))
    return итог


def остановить(база):
    с = _состояние(база)
    if с.get("pid"):
        subprocess.run(["taskkill", "/F", "/PID", str(с["pid"])], capture_output=True)
        срок = time.time() + 5
        while time.time() < срок and _слушает(с.get("порт", 0)) == с["pid"]:
            time.sleep(0.2)
    try:
        os.remove(os.path.join(папка(база), "агент.json"))
    except OSError:
        pass


# ───────────── сторож простоя, список и остановка своих агентов ─────────────

def _тот_же_процесс(pid, создан):
    """Жив ли ИМЕННО тот процесс (pid мог достаться другому процессу после смерти агента)."""
    import psutil
    try:
        п = psutil.Process(pid)
        return п.name().lower().startswith("1cv8") and (not создан or abs(п.create_time() - создан) < 1)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def _простой_сек(папка_агента):
    """Секунд без команд: по отметке активности; нет отметки — None (агент старого образца, не наш сторож)."""
    try:
        return time.time() - os.path.getmtime(os.path.join(папка_агента, "активность"))
    except OSError:
        return None


def _сторож_жив(с):
    import psutil
    pid = с.get("сторож")
    try:
        return bool(pid) and "сторож" in " ".join(psutil.Process(pid).cmdline())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def _сторож_запустить(база):
    """Отвязанный процесс «сторож» для агента базы (если его сторож ещё не жив)."""
    с = _состояние(база)
    if not с.get("pid") or _сторож_жив(с):
        return
    флаги = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    журнал = open(os.path.join(папка(база), "сторож.log"), "a", encoding="utf-8")   # только для падений сторожа
    # pid и время создания агента — аргументами: агент.json в этот момент может переписываться
    п = subprocess.Popen([sys.executable, os.path.abspath(__file__), "сторож", "--база=" + база,
                          "--pid=%d" % с["pid"], "--создан=%s" % с.get("создан", "")],
                         creationflags=флаги, close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=журнал, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    журнал.close()
    с["сторож"] = п.pid
    _записать_состояние(база, с)


def сторож(база):
    """Цикл сторожа: агент без команд дольше простой_мин — остановить. Выход, если агента нет или он заменён."""
    pid = int(аргумент("pid"))
    создан = float(аргумент("создан") or 0) or None

    def лог(текст):              # строка целиком за одну запись: журнал общий у сторожей одной базы
        with open(os.path.join(папка(база), "сторож.log"), "a", encoding="utf-8") as ф:
            ф.write("%s %s\n" % (time.strftime("%d.%m %H:%M:%S"), текст))

    лог("сторож: агент pid %d базы %s, простой %.1f мин" % (pid, база, _состояние(база).get("простой_мин", ПРОСТОЙ_МИН)))
    while True:
        с = _состояние(база)
        if not _тот_же_процесс(pid, создан):
            лог("сторож: агента pid %d больше нет — выхожу" % pid)
            return
        if с and с.get("pid") != pid:
            лог("сторож: агент pid %d заменён новым (pid %s, у него свой сторож) — выхожу" % (pid, с.get("pid")))
            return
        предел = 60 * float(с.get("простой_мин", ПРОСТОЙ_МИН))
        if предел <= 0:
            лог("сторож: у агента pid %d предел простоя 0 — его остановит деплой, выхожу" % pid)
            return
        простой = _простой_сек(папка(база))
        if простой is None:
            простой = time.time() - (создан or time.time())
        if простой > предел:
            остановить(база)
            лог("сторож: агент pid %d без команд %.0f с (предел %.0f с) — остановлен" % (pid, простой, предел))
            return
        time.sleep(min(ОПРОС_СТОРОЖА, max(1.0, предел - простой + 0.5)))


def _аргумент_процесса(команда, ключ):
    """Значение ключа командной строки 1cv8 (/F, /AgentBaseDir …) или ''."""
    for и, а in enumerate(команда[:-1]):
        if а.lower() == ключ.lower():
            return команда[и + 1]
    return ""


def процессы_1с():
    """Все процессы 1cv8*: [{pid, база, свой, агент, порт, папка, простой, сторож, создан, строка}]."""
    import psutil
    итог = []
    for п in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        if not (п.info["name"] or "").lower().startswith("1cv8"):
            continue
        команда = п.info["cmdline"] or []
        база = _аргумент_процесса(команда, "/F") or адрес_базы.из_ключей("/S", _аргумент_процесса(команда, "/S"))
        папка_агента = _аргумент_процесса(команда, "/AgentBaseDir")
        агент = any(а.lower() == "/agentmode" for а in команда)
        # свой: файловая C:\1c_bases\UZ_* или серверная, чьё имя в кластере начинается с uz_ (uz_bp_srv)
        свой = (агент and (os.path.normcase(база).startswith(БАЗЫ_СВОИ)
                          or (адрес_базы.серверная(база) or ("", ""))[1].lower().startswith("uz_"))
                and os.path.normcase(os.path.abspath(папка_агента)).startswith(os.path.normcase(КОРЕНЬ) + os.sep))
        с = {}
        if свой:
            try:
                с = json.load(open(os.path.join(папка_агента, "агент.json"), encoding="utf-8"))
            except (OSError, ValueError):
                с = {}
        итог.append({"pid": п.info["pid"], "база": база, "свой": свой, "агент": агент,
                     "порт": _аргумент_процесса(команда, "/AgentPort"), "папка": папка_агента,
                     "простой": _простой_сек(папка_агента) if свой else None,
                     "предел": с.get("простой_мин") if с.get("pid") == п.info["pid"] else None,
                     "сторож": _сторож_жив(с) if с.get("pid") == п.info["pid"] else False,
                     "создан": п.info["create_time"], "строка": " ".join(команда[1:6])})
    return итог


def _уборка_простаивающих(кроме):
    """Страховка к сторожу: свои агенты других баз, простоявшие дольше своего предела, — остановить.
    Агенты старого образца (без отметки активности) не трогаются: их простой неизвестен."""
    for п in процессы_1с():
        if not п["свой"] or адрес_базы.ключ(п["база"]) == адрес_базы.ключ(кроме):
            continue
        предел = 60 * float(п["предел"] if п["предел"] is not None else ПРОСТОЙ_МИН)
        # предел 0 — агент деплоя с -ПростойАгента 0: его останавливает сам деплой, возможно, он сейчас в работе
        if предел > 0 and п["простой"] is not None and п["простой"] > предел:
            _снять(п)
            print("агент: остановлен простаивающий агент базы %s (pid %d, без команд %.0f с)"
                  % (п["база"], п["pid"], п["простой"]))


def _снять(п):
    subprocess.run(["taskkill", "/F", "/PID", str(п["pid"])], capture_output=True)
    путь = os.path.join(п["папка"], "агент.json")
    try:
        if json.load(open(путь, encoding="utf-8")).get("pid") == п["pid"]:
            os.remove(путь)
    except (OSError, ValueError):
        pass


def печать_списка():
    процессы = процессы_1с()
    if not процессы:
        print("процессов 1cv8 нет")
    for п in sorted(процессы, key=lambda п: (not п["свой"], п["база"].lower())):
        возраст = (time.time() - п["создан"]) / 60
        if п["свой"]:
            простой = ("без команд %.1f мин" % (п["простой"] / 60)) if п["простой"] is not None else "простой неизвестен (агент старого образца)"
            предел = " из %s" % п["предел"] if п["предел"] is not None else ""
            print("СВОЙ   pid %-6d %-26s порт %-5s %s%s, сторож %s, запущен %.0f мин назад"
                  % (п["pid"], п["база"], п["порт"], простой, предел, "жив" if п["сторож"] else "НЕТ", возраст))
        else:
            вид = "агент" if п["агент"] else "процесс"
            print("чужой  pid %-6d %-26s %s, запущен %.0f мин назад — не трогаю  (%s)"
                  % (п["pid"], п["база"], вид, возраст, п["строка"]))
    return процессы


def остановить_свои(все=False, база=None):
    """Остановить свои агенты: все или одной базы. Чужие процессы не трогаются никогда. → сколько остановлено."""
    нужна = адрес_базы.ключ(база) if база else None
    снято = 0
    for п in процессы_1с():
        if not п["свой"]:
            continue
        if все or адрес_базы.ключ(п["база"]) == нужна:
            _снять(п)
            снято += 1
            print("остановлен агент pid %d базы %s" % (п["pid"], п["база"]))
    return снято


class Сессия:
    """SSH-сессия с агентом базы после common connect-ib. Долгоживущая — у tools\\итерация.py: вход по SSH (~1,6 с)
    и connect-ib (~0,8 с) платятся один раз, а не на каждую загрузку (замер 28.09.2026, UZ_BP_C)."""

    def __init__(self, база, таймаут_входа=20):
        import paramiko
        self.база = база
        порт = живой(база)
        if not порт:
            raise RuntimeError("агент базы %s не запущен" % база)
        активность(база)                     # сторож считает простой от последней команды
        пользователь = _состояние(база)["пользователь"]
        # только что стартовавший агент порт уже слушает, а вход отклоняет («Authentication failed: transport shut
        # down or saw EOF») — пока открывает базу. 29.09.2026 под нагрузкой соседних сессий это длилось дольше пяти
        # попыток по 0,5 с: итерация падала «агент не поднялся». Повторяем до 15 с
        срок = time.time() + 15
        while True:
            к = paramiko.SSHClient()
            к.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                к.connect("127.0.0.1", порт, username=пользователь, password="", look_for_keys=False,
                          allow_agent=False, timeout=таймаут_входа)
                break
            except paramiko.ssh_exception.AuthenticationException:
                к.close()
                if time.time() > срок:
                    raise
                time.sleep(0.5)
        self.клиент = к
        self.канал = к.get_transport().open_session()
        self.канал.invoke_shell()
        try:
            self._прочитать(time.time() + таймаут_входа, таймаут_входа)
            команда, ок, сек, ответ = self.выполнить("common connect-ib", таймаут_входа)
            if not ок:
                raise RuntimeError("агент: common connect-ib — %s" % ответ)
        except Exception:
            self.закрыть()
            raise

    def _прочитать(self, срок, таймаут):
        буфер = b""
        self.канал.settimeout(max(1.0, срок - time.time()))
        while True:
            if time.time() > срок:
                raise TimeoutError("агент не ответил за %d с" % таймаут)
            кусок = self.канал.recv(65536)
            if not кусок:
                break
            буфер += кусок
            if буфер.decode("utf-8", "replace").endswith(ПРИГЛАШЕНИЕ):
                break
        return буфер.decode("utf-8", "replace")

    def выполнить(self, команда, таймаут=60):
        """→ (команда, ок, сек, ответ). Ошибка — по формату ответа агента («Ошибка Xxx - …») или закрытый канал."""
        н = time.time()
        активность(self.база)
        self.канал.send((команда + "\n").encode("utf-8"))
        ответ = self._прочитать(н + таймаут, таймаут)
        дошёл = ответ.endswith(ПРИГЛАШЕНИЕ)          # нет приглашения — агент закрыл канал посреди команды
        ответ = ответ[:-len(ПРИГЛАШЕНИЕ)].strip() if дошёл else ответ.strip() + "\n(агент закрыл канал)"
        # «Ошибка UnknownError» — без « - текст»: так агент отвечает на load-files после update-db-cfg
        ок = дошёл and not ОШИБКА.search(ответ) and not re.match(r"^Ошибка \w+\s*$", ответ, re.M)
        активность(self.база)
        return команда, ок, time.time() - н, ответ

    def закрыть(self):
        try:
            self.клиент.close()
        finally:
            активность(self.база)


def команды(база, список, таймаут=60):
    """Команды одной SSH-сессией после common connect-ib. [(команда, ок, сек, ответ)]; стоп на первой ошибке."""
    н = time.time()
    с = Сессия(база)
    итог = [("common connect-ib", True, time.time() - н, "")]
    try:
        for команда in список:
            итог.append(с.выполнить(команда, таймаут))
            if not итог[-1][1]:
                break
    finally:
        с.закрыть()
    return итог


def main():
    for поток in (sys.stdout, sys.stderr):
        поток.reconfigure(encoding="utf-8")
    действие = sys.argv[1] if len(sys.argv) > 1 else ""
    база = аргумент("база")
    if действие == "список":
        печать_списка()
        return 0
    if действие == "остановить":
        if not база and "--все" not in sys.argv:
            sys.exit("остановить: нужен --все или --база=…")
        снято = остановить_свои("--все" in sys.argv, база)
        print("остановлено своих агентов: %d" % снято)
        return 0
    if not база or действие not in ("старт", "команды", "стоп", "сторож"):
        sys.exit(__doc__)
    try:
        if действие == "сторож":
            сторож(база)
        elif действие == "старт":
            н = time.time()
            порт = старт(база, аргумент("пользователь", "Администратор"), ждать="--не-ждать" not in sys.argv,
                         простой=аргумент("простой"))
            print("агент: порт %d, %.1f с" % (порт, time.time() - н))
        elif действие == "стоп":
            остановить(база)
            print("агент остановлен")
        else:
            список = [а for а in sys.argv[2:] if not а.startswith("--")]
            код = 0
            for команда, ок, сек, ответ in команды(база, список, int(аргумент("таймаут", "60"))):
                print("агент %s %5.1f с  %s" % ("ок    " if ок else "ОШИБКА", сек, команда.split(" --")[0]))
                if not ок or "--подробно" in sys.argv:
                    print("      " + ответ.replace("\n", "\n      "))
                код |= not ок
            return код
    except Exception as е:
        print("агент: ОШИБКА %s" % е)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
