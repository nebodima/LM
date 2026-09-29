"""Адрес базы 1С для инструментов УЗ_ext: файловая (путь к папке) или серверная («Srvr=localhost;Ref=uz_bp_srv»).

Все инструменты (деплой.ps1, итерация.py, прогон.py, агент_конфигуратора.py, отпечаток_src.py, тесты/сеанс.py)
принимают базу одной строкой — путь или строку серверной базы — и берут отсюда всё, что от вида базы зависит:
ключи конфигуратора (/F путь | /S сервер\\база), строку COM (File= | Srvr=;Ref=), короткое имя (папка агента,
журналы, пользователь по умолчанию), ключ сравнения и папку журнала регистрации. Пароли сюда не входят:
пользователи копий баз — без пароля (правило стенда).

    python tools\\адрес_базы.py "Srvr=localhost;Ref=uz_bp_srv"   — JSON: имя, ключ, серверная, ключи конфигуратора
"""
import glob
import json
import os
import re
import sys

СЕРВЕРНАЯ = re.compile(r'^\s*Srvr\s*=\s*"?([^";]+)"?\s*;\s*Ref\s*=\s*"?([^";]+)"?\s*;?\s*$', re.I)
SRVINFO = r"C:\Program Files\1cv8\srvinfo"


def серверная(база):
    """(сервер, имя базы в кластере) для строки «Srvr=…;Ref=…», иначе None (файловая)."""
    н = СЕРВЕРНАЯ.match(база or "")
    return (н.group(1).strip(), н.group(2).strip()) if н else None


def нормализовать(база):
    """Каноническая запись: файловая — абсолютный путь, серверная — «Srvr=сервер;Ref=база»."""
    с = серверная(база)
    return "Srvr=%s;Ref=%s" % с if с else os.path.abspath(база)


def ключ(база):
    """Для сравнения «та же база»: регистр и вид записи не важны."""
    с = серверная(база)
    return ("srvr=%s;ref=%s" % с).lower() if с else os.path.normcase(os.path.abspath(база))


def имя(база):
    """Короткое имя: папка файловой базы (UZ_BP_E) или имя серверной в кластере заглавными (UZ_BP_SRV).
    Идёт в путь папки агента — она обязана быть ASCII (грабля агента)."""
    с = серверная(база)
    return с[1].upper() if с else os.path.basename(os.path.normpath(база))


def строка_com(база, пользователь):
    с = серверная(база)
    if с:
        return 'Srvr="%s";Ref="%s";Usr="%s";' % (с[0], с[1], пользователь)
    return 'File="%s";Usr="%s";' % (база, пользователь)


def ключи_конфигуратора(база):
    """[/F, путь] или [/S, сервер\\база] для 1cv8 DESIGNER."""
    с = серверная(база)
    return ["/S", "%s\\%s" % с] if с else ["/F", база]


def из_ключей(ключ_вида, значение):
    """Обратно из командной строки процесса 1cv8: (/S, «localhost\\uz_bp_srv») → «Srvr=localhost;Ref=uz_bp_srv»."""
    if ключ_вида.lower() == "/s" and "\\" in значение:
        сервер, база = значение.split("\\", 1)
        return "Srvr=%s;Ref=%s" % (сервер, база)
    return значение


def папка_журнала(база):
    """Папка журнала регистрации: файловая — <база>\\1Cv8Log; серверная — srvinfo\\reg_<порт>\\<uuid базы>\\1Cv8Log
    (uuid — из реестра кластера 1CV8Clst.lst по имени базы). Не нашли — None."""
    с = серверная(база)
    if not с:
        return os.path.join(база, "1Cv8Log")
    for реестр in glob.glob(os.path.join(SRVINFO, "reg_*", "1CV8Clst.lst")):
        try:
            текст = open(реестр, encoding="utf-8-sig", errors="replace").read()
        except OSError:
            continue
        н = re.search(r'\{([0-9a-f-]{36}),"%s",' % re.escape(с[1]), текст, re.I)
        if н:
            return os.path.join(os.path.dirname(реестр), н.group(1), "1Cv8Log")
    return None


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    б = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    print(json.dumps({"база": нормализовать(б), "имя": имя(б), "ключ": ключ(б), "серверная": bool(серверная(б)),
                      "конфигуратор": ключи_конфигуратора(б)}, ensure_ascii=False))
