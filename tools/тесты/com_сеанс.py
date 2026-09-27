"""Общее для COM-тестов УЗ_ext: один сеанс на прогон, проверка PASS/FAIL, даты с tzinfo=utc.

База — своя файловая копия: --база=C:\\1c_bases\\UZ_UNF_B (вход Администратор без пароля).
"""
import datetime
import sys
import time

УТС = datetime.timezone.utc
_соединение = None
_провалы = []
_начало = time.time()


def настроить_вывод():
    for поток in (sys.stdout, sys.stderr):
        try:
            поток.reconfigure(encoding="utf-8")
        except Exception:
            pass


def база_из_аргументов(по_умолчанию=r"C:\1c_bases\UZ_UNF_B"):
    for арг in sys.argv[1:]:
        if арг.startswith("--база="):
            return арг.split("=", 1)[1]
    return по_умолчанию


def сеанс():
    """Один COM-сеанс на весь прогон."""
    global _соединение
    if _соединение is None:
        import win32com.client
        н = time.time()
        _соединение = win32com.client.Dispatch("V83.COMConnector").Connect(
            'File="%s";Usr="Администратор";' % база_из_аргументов())
        print("подключение %.1f с" % (time.time() - н))
    return _соединение


def дата(год, месяц, день, час=0, минута=0):
    # наивный datetime через COM сдвигается по поясу — только с tzinfo=utc
    return datetime.datetime(год, месяц, день, час, минута, tzinfo=УТС)


def как_дата(значение):
    """Дата 1С из COM → datetime.date; пустая дата 1С приходит 0100-01-01 → None."""
    if значение is None or значение.year < 1900:
        return None
    return datetime.date(значение.year, значение.month, значение.day)


def проверка(имя, условие, подробно=""):
    print("[%s] %s%s" % ("PASS" if условие else "FAIL", имя, ("  — " + str(подробно)) if подробно and not условие else ""))
    if not условие:
        _провалы.append(имя)
    return условие


def ошибка_записи(действие):
    """Текст ошибки, если действие упало, иначе None."""
    try:
        действие()
        return None
    except Exception as исключение:
        аргументы = getattr(исключение, "excepinfo", None) or исключение.args
        текст = аргументы[2] if isinstance(аргументы, tuple) and len(аргументы) > 2 else исключение
        return " ".join(str(текст).split())[:300]


def итог(бюджет):
    сек = time.time() - _начало
    метка = "  ПРЕДУПРЕЖДЕНИЕ: бюджет %d с превышен" % бюджет if сек > бюджет else ""
    print("ИТОГО: провалов %d, время %.1f с%s" % (len(_провалы), сек, метка))
    return 1 if _провалы else 0
