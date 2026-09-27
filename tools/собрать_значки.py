# -*- coding: utf-8 -*-
"""Значки разделов «Учёта занятий» из исходников Codex (docs/макеты-ui/УЗ_Иконка*.png, 256×256).

Картинка расширения хранится zip-архивом с набором размеров под масштабы экрана и манифестом.
Базовый глиф — 48: панель разделов рисует картинку подсистемы от базового размера
(с базой 16 значок стоит рядом с «Главным» втрое мельче — урок Путевых листов).

    python tools/собрать_значки.py

Идемпотентно: uuid картинки — uuid5 от имени; повторный запуск даёт те же файлы XML.
"""
import io
import os
import re
import sys
import uuid
import zipfile

from PIL import Image

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ИСХ = os.path.join(КОРЕНЬ, "src_ext")
МАКЕТЫ = os.path.join(КОРЕНЬ, "docs", "макеты-ui")
ПРОСТРАНСТВО = uuid.UUID("6f1c2d3e-4a5b-4c6d-8e7f-90a1b2c3d4e5")

# значок -> (синоним, подсистема, к которой он ставится)
ЗНАЧКИ = {
    "УЗ_ИконкаРаздел": ("Учёт занятий (значок раздела)", "УЗ_УчетЗанятий"),
    "УЗ_ИконкаДокументы": ("Занятия (значок)", "УЗ_УчетЗанятий/Subsystems/УЗ_Документы"),
    "УЗ_ИконкаКасса": ("Касса (значок)", "УЗ_УчетЗанятий/Subsystems/УЗ_Касса"),
    "УЗ_ИконкаСправочники": ("Ученики и педагоги (значок)", "УЗ_УчетЗанятий/Subsystems/УЗ_Справочники"),
    "УЗ_ИконкаОтчеты": ("Отчёты (значок)", "УЗ_УчетЗанятий/Subsystems/УЗ_Отчеты"),
    "УЗ_ИконкаНастройки": ("Настройки (значок)", "УЗ_УчетЗанятий/Subsystems/УЗ_Настройки"),
}
ВАРИАНТЫ = (
    ("85.png", "bldpi", 41), ("100.png", "ldpi", 48), ("125.png", "aldpi", 60), ("150.png", "mdpi", 72),
    ("175.png", "amdpi", 84), ("200.png", "hdpi", 96), ("300.png", "xdpi", 144), ("400.png", "udpi", 192),
)
ШАПКА = ('<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" '
         'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
         'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n')


def манифест():
    строки = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<Picture>"]
    for имя, плотность, размер in ВАРИАНТЫ:
        строки.append('\t<PictureVariant name="%s" screenDensity="%s" glyphWidth="%d" glyphHeight="%d"/>'
                      % (имя, плотность, размер, размер))
    строки.append('\t<PictureVariant name="Picture.png" interfaceVariant="version8_2" '
                  'screenDensity="ldpi" glyphWidth="48" glyphHeight="48"/>')
    строки.append("</Picture>")
    return "\n".join(строки)


def записать(путь, текст):
    os.makedirs(os.path.dirname(путь), exist_ok=True)
    with open(путь, "w", encoding="utf-8", newline="\n") as ф:
        ф.write(текст)


def собрать_картинку(имя, синоним):
    исходник = Image.open(os.path.join(МАКЕТЫ, имя + ".png")).convert("RGBA")
    папка = os.path.join(ИСХ, "CommonPictures", имя)
    записать(os.path.join(ИСХ, "CommonPictures", имя + ".xml"), ШАПКА +
             '\t<CommonPicture uuid="%s">\n\t\t<Properties>\n\t\t\t<Name>%s</Name>\n\t\t\t<Synonym>\n'
             '\t\t\t\t<v8:item>\n\t\t\t\t\t<v8:lang>ru</v8:lang>\n\t\t\t\t\t<v8:content>%s</v8:content>\n'
             '\t\t\t\t</v8:item>\n\t\t\t</Synonym>\n\t\t\t<Comment/>\n\t\t</Properties>\n\t</CommonPicture>\n'
             '</MetaDataObject>\n' % (uuid.uuid5(ПРОСТРАНСТВО, имя), имя, синоним))
    записать(os.path.join(папка, "Ext", "Picture.xml"),
             '<?xml version="1.0" encoding="UTF-8"?>\n<ExtPicture xmlns="http://v8.1c.ru/8.3/xcf/extrnprops" '
             'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
             'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n\t<Picture>\n'
             '\t\t<xr:Abs>Picture.zip</xr:Abs>\n\t\t<xr:LoadTransparent>false</xr:LoadTransparent>\n'
             '\t</Picture>\n</ExtPicture>\n')
    os.makedirs(os.path.join(папка, "Ext", "Picture"), exist_ok=True)
    with zipfile.ZipFile(os.path.join(папка, "Ext", "Picture", "Picture.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for файл, _, размер in ВАРИАНТЫ + (("Picture.png", "", 48),):
            поток = io.BytesIO()
            исходник.resize((размер, размер), Image.LANCZOS).save(поток, "PNG")
            z.writestr(файл, поток.getvalue())
        z.writestr("manifest.xml", манифест().encode("utf-8"))


def зарегистрировать(имена):
    путь = os.path.join(ИСХ, "Configuration.xml")
    т = open(путь, encoding="utf-8-sig").read()
    новые = [и for и in имена if "<CommonPicture>%s</CommonPicture>" % и not in т]
    if новые:
        последняя = list(re.finditer(r"\t\t\t<CommonPicture>[^<]+</CommonPicture>\n", т))
        if not последняя:
            sys.exit("в Configuration.xml нет ни одной CommonPicture — некуда вставить (порядок типов строгий)")
        поз = последняя[-1].end()
        т = т[:поз] + "".join("\t\t\t<CommonPicture>%s</CommonPicture>\n" % и for и in новые) + т[поз:]
        записать(путь, т)
    return новые


def поставить_подсистеме(имя, подсистема):
    путь = os.path.join(ИСХ, "Subsystems", *подсистема.split("/")) + ".xml"
    т = open(путь, encoding="utf-8-sig").read()
    блок = ("<Picture>\n\t\t\t\t<xr:Ref>CommonPicture.%s</xr:Ref>\n\t\t\t\t<xr:LoadTransparent>true</xr:LoadTransparent>\n"
            "\t\t\t</Picture>" % имя)
    нов, n = re.subn(r"<Picture/>|<Picture>.*?</Picture>", блок, т, count=1, flags=re.S)
    if n != 1:
        sys.exit("нет свойства Picture в " + путь)
    записать(путь, нов)


def главная():
    for имя, (синоним, подсистема) in ЗНАЧКИ.items():
        собрать_картинку(имя, синоним)
        поставить_подсистеме(имя, подсистема)
    новые = зарегистрировать(list(ЗНАЧКИ))
    print("значков: %d, новых в Configuration.xml: %d" % (len(ЗНАЧКИ), len(новые)))


if __name__ == "__main__":
    главная()
