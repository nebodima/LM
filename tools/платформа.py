"""Платформа 1С для инструментов УЗ_ext: ОДИН источник пути, версии и COM-класса (разработка ведётся на 8.3 и на 8.5).

Выбор линии: ключ `--платформа=8.3|8.5` в командной строке любого python-инструмента (модуль сам вырезает его из
sys.argv при импорте и кладёт в переменную среды), в ps1 — `-Платформа 8.3|8.5`, либо переменная среды
UZ_ПЛАТФОРМА; по умолчанию 8.3. Версия — самая новая установленная сборка выбранной линии в C:\\Program Files\\1cv8
(8.3.* или 8.5.*). Линии нет на стенде — ошибка «платформа 8.5 не установлена: C:\\Program Files\\1cv8\\8.5.*», код 1.

COM-класс не угадывается: V83.COMConnector для 8.3; для 8.5 — V85.COMConnector, если он есть в реестре (HKCR),
иначе V83.COMConnector — но только если он зарегистрирован на каталог 8.5; иначе ошибка.

Метка платформы базы: файл `.платформа` («8.3» / «8.5») в папке файловой базы. База, открытая новой платформой,
может перестать открываться старой — поэтому для 8.5 нужны ОТДЕЛЬНЫЕ копии (C:\\1c_bases\\UZ_BP_Q85). Метку ставит
первый деплой; запуск другой линией — отказ. База без метки: деплой на 8.3 метку ставит, на 8.5 — только если имя
базы кончается на «85» (иначе это старая база 8.3, её нельзя обновлять новой платформой).

    python tools\\платформа.py                        — JSON: линия, сборка, каталог, exe, COM-класс, модуль веб-сервера
    python tools\\платформа.py --платформа=8.5 --поле=exe      — одно поле (для ps1)
    python tools\\платформа.py --проверить=<база>     — отказ (код 1), если метка базы — другая линия
    python tools\\платформа.py --метка=<база>         — проверить и поставить метку (деплой)
"""
import json
import os
import re
import sys

КОРЕНЬ_1С = r"C:\Program Files\1cv8"
ЛИНИИ = ("8.3", "8.5")
ИМЯ_МЕТКИ = ".платформа"


def _вырезать_ключ():
    """--платформа=X из sys.argv → переменная среды (чтобы скрипты со своим разбором ключей его не видели)."""
    for а in list(sys.argv[1:]):
        if а.startswith("--платформа="):
            os.environ["UZ_ПЛАТФОРМА"] = а.split("=", 1)[1].strip()
            sys.argv.remove(а)


_вырезать_ключ()


class ОшибкаПлатформы(SystemExit):
    def __init__(self, текст):
        super().__init__("ОШИБКА: " + текст)


def линия():
    л = (os.environ.get("UZ_ПЛАТФОРМА") or "8.3").strip()
    if л not in ЛИНИИ:
        raise ОшибкаПлатформы("платформа «%s» не поддерживается (8.3 или 8.5)" % л)
    return л


def _ключ_версии(имя):
    return tuple(int(ч) for ч in re.findall(r"\d+", имя))


def сборка(л=None):
    """Самая новая установленная сборка линии: «8.3.27.1936»."""
    л = л or линия()
    найдено = []
    if os.path.isdir(КОРЕНЬ_1С):
        найдено = [п for п in os.listdir(КОРЕНЬ_1С)
                   if re.fullmatch(re.escape(л) + r"\.\d+\.\d+", п) and os.path.isdir(os.path.join(КОРЕНЬ_1С, п, "bin"))]
    if not найдено:
        raise ОшибкаПлатформы("платформа %s не установлена: %s\\%s.*" % (л, КОРЕНЬ_1С, л))
    return max(найдено, key=_ключ_версии)


def каталог_bin(л=None):
    return os.path.join(КОРЕНЬ_1С, сборка(л), "bin")


def exe(имя="1cv8.exe", л=None):
    """Путь к исполняемому файлу платформы: 1cv8.exe, 1cv8c.exe, ibcmd.exe, rac.exe …"""
    п = os.path.join(каталог_bin(л), имя)
    if not os.path.isfile(п):
        raise ОшибкаПлатформы("в платформе %s нет %s: %s" % (сборка(л), имя, п))
    return п


def модуль_веб(л=None):
    """wsap24.dll (Apache 2.4) выбранной платформы, со слэшами — как нужно httpd.conf."""
    return exe("wsap24.dll", л).replace("\\", "/")


def _реестр_com(класс):
    """Каталог, на который зарегистрирован COM-класс (InprocServer32), или None, если класса нет."""
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, класс + r"\CLSID") as к:
            clsid = winreg.QueryValue(к, "")
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"CLSID\%s\InprocServer32" % clsid) as к:
            return winreg.QueryValue(к, "")
    except OSError:
        return None


def com_класс(л=None):
    """ProgID COM-коннектора линии — по реестру, не по догадке."""
    л = л or линия()
    if л == "8.3":
        return "V83.COMConnector"
    if _реестр_com("V85.COMConnector"):
        return "V85.COMConnector"
    путь = _реестр_com("V83.COMConnector") or ""
    if путь and (os.sep + сборка(л) + os.sep).lower() in путь.lower():
        return "V83.COMConnector"
    raise ОшибкаПлатформы("COM-коннектор платформы 8.5 не зарегистрирован (нет V85.COMConnector, V83.COMConnector указывает на "
                          "%s): regsvr32 \"%s\"" % (путь or "—", os.path.join(каталог_bin(л), "comcntr.dll")))


def коннектор():
    """Новый объект COM-коннектора выбранной платформы (win32com)."""
    import win32com.client
    return win32com.client.Dispatch(com_класс())


def описание():
    л = линия()
    return {"линия": л, "сборка": сборка(л), "каталог": каталог_bin(л), "exe": exe("1cv8.exe", л),
            "com": com_класс(л)}


# ---- метка платформы базы ----------------------------------------------------------------------------------------------

def _файл_метки(база):
    if re.match(r"^\s*Srvr\s*=", база or "", re.I):
        return None                      # серверная база: метки нет, база в кластере своей версии
    return os.path.join(база, ИМЯ_МЕТКИ)


def метка_базы(база):
    п = _файл_метки(база)
    if п and os.path.isfile(п):
        return open(п, encoding="utf-8-sig").read().strip()
    return None


def проверить_базу(база, поставить=False):
    """Отказ, если метка базы — другая линия. поставить=True (деплой): ставит метку там, где её нет."""
    л = линия()
    п = _файл_метки(база)
    if not п or not os.path.isdir(база):
        return
    метка = метка_базы(база)
    if метка:
        if метка != л:
            raise ОшибкаПлатформы(
                "база %s открывалась платформой %s, запуск идёт платформой %s. Файловая база, открытая более новой платформой, "
                "может не открыться старой: для каждой линии — отдельная копия (для 8.5 — с суффиксом, например UZ_BP_Q85). "
                "Запустите нужной линией (--платформа=%s) или возьмите другую копию." % (база, метка, л, метка))
        return
    if not поставить:
        return
    if л == "8.5" and not os.path.basename(os.path.normpath(база)).upper().endswith("85"):
        raise ОшибкаПлатформы(
            "у базы %s нет метки платформы, а имя не оканчивается на «85»: похоже на базу 8.3, обновлять её платформой 8.5 "
            "нельзя. Сделайте копию, например C:\\1c_bases\\UZ_BP_Q85, и работайте в ней." % база)
    with open(п, "w", encoding="utf-8") as ф:
        ф.write(л + "\n")


def главная():
    a = sys.argv[1:]
    зн = lambda имя: next((х.split("=", 1)[1] for х in a if х.startswith("--%s=" % имя)), None)  # noqa: E731
    if зн("проверить"):
        проверить_базу(зн("проверить"))
        return
    if зн("метка"):
        проверить_базу(зн("метка"), поставить=True)
        return
    д = описание()
    if зн("поле"):
        print(д[зн("поле")])
    else:
        print(json.dumps(д, ensure_ascii=False))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    главная()
