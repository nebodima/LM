"""Агент конфигуратора 1С (/AgentMode) для файловой базы: запуск, команды по SSH, остановка.

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

    python tools\\агент_конфигуратора.py старт  --база=C:\\1c_bases\\UZ_UNF_D [--пользователь=Администратор]
    python tools\\агент_конфигуратора.py команды --база=… "config load-files --dir=…" "config update-db-cfg --extension=УЗ_ext"
    python tools\\агент_конфигуратора.py стоп   --база=…
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

EXE = r"C:\Program Files\1cv8\8.3.27.1936\bin\1cv8.exe"
ПОРТЫ = range(1546, 1561)
ПРИГЛАШЕНИЕ = "designer> "
ОШИБКА = re.compile(r"^Ошибка \w+ - ", re.M)


def аргумент(имя, по_умолчанию=None):
    for а in sys.argv[1:]:
        if а.startswith("--%s=" % имя):
            return а.split("=", 1)[1]
    return по_умолчанию


def папка(база):
    п = os.path.join(tempfile.gettempdir(), "uz_agent", os.path.basename(os.path.normpath(база)))
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
    if с.get("база") != os.path.normcase(os.path.abspath(база)):
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


def старт(база, пользователь, ждать=True):
    порт = живой(база)
    if порт:
        return порт
    # агент, запущенный в фоне прошлым деплоем, может ещё подниматься (~5 с): процесс жив, порт пока не слушает —
    # дождаться его, а не убивать и стартовать заново
    import psutil
    с = _состояние(база)
    if (с.get("база") == os.path.normcase(os.path.abspath(база)) and с.get("pid") and psutil.pid_exists(с["pid"])
            and psutil.Process(с["pid"]).name().lower().startswith("1cv8") and _слушает(с.get("порт", 0)) is None):
        if not ждать or _ждать_порт(с["порт"], с["pid"], 20):
            return с["порт"]
    остановить(база)
    свободные = [п for п in ПОРТЫ if _слушает(п) is None]
    if not свободные:
        raise RuntimeError("агент: нет свободного порта в %d–%d" % (ПОРТЫ[0], ПОРТЫ[-1]))
    порт = свободные[0]
    аргументы = [EXE, "DESIGNER", "/F", база, "/N", пользователь, "/DisableStartupDialogs",
                 "/DisableStartupMessages", "/AgentMode", "/AgentPort", str(порт), "/AgentListenAddress",
                 "127.0.0.1", "/AgentBaseDir", папка(база), "/AgentSSHHostKeyAuto"]
    флаги = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    п = subprocess.Popen(аргументы, creationflags=флаги, close_fds=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    json.dump({"база": os.path.normcase(os.path.abspath(база)), "пользователь": пользователь, "порт": порт,
               "pid": п.pid}, open(os.path.join(папка(база), "агент.json"), "w", encoding="utf-8"))
    if not ждать or _ждать_порт(порт, п.pid, 20):
        return порт
    raise RuntimeError("агент: за 20 с не начал слушать порт %d" % порт)


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


def команды(база, список, таймаут=60):
    """Команды одной SSH-сессией после common connect-ib. [(команда, ок, сек, ответ)]; стоп на первой ошибке."""
    import paramiko
    порт = живой(база)
    if not порт:
        raise RuntimeError("агент базы %s не запущен" % база)
    пользователь = _состояние(база)["пользователь"]
    for попытка in range(5):
        к = paramiko.SSHClient()
        к.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            к.connect("127.0.0.1", порт, username=пользователь, password="", look_for_keys=False,
                      allow_agent=False, timeout=20)
            break
        except paramiko.ssh_exception.AuthenticationException:
            к.close()
            if попытка == 4:
                raise
            time.sleep(0.5)
    канал = к.get_transport().open_session()
    канал.invoke_shell()

    def прочитать(срок):
        буфер = b""
        канал.settimeout(max(1.0, срок - time.time()))
        while True:
            if time.time() > срок:
                raise TimeoutError("агент не ответил за %d с" % таймаут)
            кусок = канал.recv(65536)
            if not кусок:
                break
            буфер += кусок
            if буфер.decode("utf-8", "replace").endswith(ПРИГЛАШЕНИЕ):
                break
        return буфер.decode("utf-8", "replace")

    итог = []
    try:
        прочитать(time.time() + 20)
        for команда in ["common connect-ib"] + list(список):
            н = time.time()
            канал.send((команда + "\n").encode("utf-8"))
            ответ = прочитать(н + таймаут)
            дошёл = ответ.endswith(ПРИГЛАШЕНИЕ)          # нет приглашения — агент закрыл канал посреди команды
            ответ = ответ[:-len(ПРИГЛАШЕНИЕ)].strip() if дошёл else ответ.strip() + "\n(агент закрыл канал)"
            ок = дошёл and not ОШИБКА.search(ответ)
            итог.append((команда, ок, time.time() - н, ответ))
            if not ок:
                break
    finally:
        к.close()
    return итог


def main():
    for поток in (sys.stdout, sys.stderr):
        поток.reconfigure(encoding="utf-8")
    действие = sys.argv[1] if len(sys.argv) > 1 else ""
    база = аргумент("база")
    if not база or действие not in ("старт", "команды", "стоп"):
        sys.exit(__doc__)
    try:
        if действие == "старт":
            н = time.time()
            порт = старт(база, аргумент("пользователь", "Администратор"), ждать="--не-ждать" not in sys.argv)
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
