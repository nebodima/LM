# -*- coding: utf-8 -*-
"""Справка F1: к каждому Ext/Help/ru.html положить Ext/Help.xml и привести оба файла к виду выгрузки платформы.

Справку пишут текстом (ru.html), а свойства страницы (Help.xml) одинаковые у всех — их незачем набирать руками.
Скрипт повторяемый: второй запуск ничего не меняет.

  * Help.xml — `<Help xmlns="http://v8.1c.ru/8.3/xcf/extrnprops" … version="…"><Page>ru</Page></Help>`, версия
    формата — как у Configuration.xml каталога (у src_ext 2.11);
  * у ru.html и Help.xml — метка UTF-8 (BOM), как в выгрузке платформы (иначе следующая выгрузка «изменит»
    файл целиком), переводы строк CRLF не навязываются.

Блок <Help> внутри Form.xml платформа молча выбрасывает — справка только так, отдельными файлами.

    python tools/справка_help_xml.py [каталог]          # по умолчанию src_ext
    python tools/справка_help_xml.py --проверка          # только сказать, что поменялось бы (код 1, если есть)
"""
import io
import os
import re
import sys

КОРЕНЬ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ШАБЛОН = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<Help xmlns="http://v8.1c.ru/8.3/xcf/extrnprops" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="%s">\n\t<Page>ru</Page>\n</Help>')
BOM = b"\xef\xbb\xbf"


def записать(путь, данные, только_проверка, изменено):
    старое = open(путь, "rb").read() if os.path.isfile(путь) else None
    if старое == данные:
        return
    изменено.append(путь)
    if not только_проверка:
        with open(путь, "wb") as ф:
            ф.write(данные)


def главный():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    аргументы = [а for а in sys.argv[1:] if not а.startswith("--")]
    только_проверка = "--проверка" in sys.argv
    каталог = os.path.abspath(аргументы[0]) if аргументы else os.path.join(КОРЕНЬ, "src_ext")
    конф = os.path.join(каталог, "Configuration.xml")
    версия = "2.11"
    if os.path.isfile(конф):
        м = re.search(r'<MetaDataObject[^>]*\bversion="([\d.]+)"', io.open(конф, encoding="utf-8-sig").read())
        версия = м.group(1) if м else версия
    изменено, страниц = [], 0
    for корень, _, файлы in os.walk(каталог):
        if os.path.basename(корень) != "Help" or "ru.html" not in файлы:
            continue
        ext = os.path.dirname(корень)
        if os.path.basename(ext) != "Ext":
            continue
        страниц += 1
        # версия формата — как у файла-владельца (Form.xml формы, XML объекта/раздела): пакетная загрузка
        # отказывает, если версия Help.xml «отличается от версии ранее загруженных файлов» (28.09.2026, 2.20
        # у справки формы с Form.xml 2.11), а агент конфигуратора на том же отказе молча отвечает «готово»
        владелец = os.path.join(ext, "Form.xml")
        if not os.path.isfile(владелец):
            владелец = os.path.dirname(ext) + ".xml"
        версия_файла = версия
        if os.path.isfile(владелец):
            м = re.search(r'<(?:MetaDataObject|Form)\b[^>]*\bversion="([\d.]+)"',
                          io.open(владелец, encoding="utf-8-sig").read(3000))
            версия_файла = м.group(1) if м else версия
        путь_html = os.path.join(корень, "ru.html")
        текст = open(путь_html, "rb").read()
        if текст.startswith(BOM):
            текст = текст[3:]
        записать(путь_html, BOM + текст, только_проверка, изменено)
        записать(os.path.join(ext, "Help.xml"), BOM + (ШАБЛОН % версия_файла).encode("utf-8"), только_проверка,
                изменено)
    for путь in изменено:
        print(("изменился бы: " if только_проверка else "записан: ") + os.path.relpath(путь, каталог))
    print("страниц справки %d, файлов %s %d" % (страниц, "к изменению" if только_проверка else "записано",
                                                 len(изменено)))
    sys.exit(1 if только_проверка and изменено else 0)


if __name__ == "__main__":
    главный()
