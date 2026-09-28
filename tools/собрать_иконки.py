# -*- coding: utf-8 -*-
"""Иконки интерфейса «Учёта занятий» из исходников Codex (docs/макеты-ui/иконки) — общие картинки расширения.

Исходники: <Имя>_16.png — 64×64, геометрия, нарисованная для 16 px; <Имя>_48.png — 256×256, подробная, для 32–48 px.
Картинка расширения — zip-архив с набором размеров под масштабы экрана (85…400 %) и манифестом:

  * малая УЗ_И<Имя>   — база 16 (14, 16, 20, 24, 28, 32, 48, 64) ТОЛЬКО из малого исходника: кнопки, команды форм;
  * большая УЗ_И<Имя>48 — база 48 (41 … 192) ТОЛЬКО из большого: общие команды навигации, где платформа
    рисует крупно (как значки разделов). Большую в 16 не масштабируем — детали сливаются в пятно (урок ПЛ).

Собираются только иконки из СОСТАВ — те, что реально стоят в формах и командах (расстановка — docs/визуал/
дизайнер.md, раздел «Иконки»). Идемпотентно: uuid — uuid5 от имени, повторный запуск даёт те же файлы.

    python tools/собрать_иконки.py
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
ИКОНКИ = os.path.join(КОРЕНЬ, "docs", "макеты-ui", "иконки")
ПРОСТРАНСТВО = uuid.UUID("6f1c2d3e-4a5b-4c6d-8e7f-90a1b2c3d4e5")   # то же, что у собрать_значки.py

# сюжет Codex -> (синоним, малая, большая)
СОСТАВ = {
    "Напомнить": ("Напомнить (иконка)", True, False),
    "Явка": ("Явка (иконка)", True, False),
    "КОплате": ("К оплате (иконка)", True, False),
    "Помощник": ("Помощник создания уроков (иконка)", True, False),
    "ПечатьПКО": ("Печать ПКО (иконка)", True, False),
    "Оплата": ("Принять оплату (иконка)", True, False),
    "Перемещение": ("Перемещение денег (иконка)", True, False),
    "Выплата": ("Выплата (иконка)", True, False),
    "Фото": ("Фото (иконка)", True, False),
    "Заморозка": ("Приостановить (иконка)", True, False),
    "Почта": ("Почта (иконка)", True, False),
    "Отчет": ("Отчёты (иконка)", False, True),
}
МАСШТАБЫ = (("85.png", "bldpi", 0.85), ("100.png", "ldpi", 1.0), ("125.png", "aldpi", 1.25),
            ("150.png", "mdpi", 1.5), ("175.png", "amdpi", 1.75), ("200.png", "hdpi", 2.0),
            ("300.png", "xdpi", 3.0), ("400.png", "udpi", 4.0))
ШАПКА = ('<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" '
         'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
         'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n')


def размер(база, доля):
    return int(round(база * доля))


def манифест(база):
    строки = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<Picture>"]
    for имя, плотность, доля in МАСШТАБЫ:
        р = размер(база, доля)
        строки.append('\t<PictureVariant name="%s" screenDensity="%s" glyphWidth="%d" glyphHeight="%d"/>'
                      % (имя, плотность, р, р))
    строки.append('\t<PictureVariant name="Picture.png" interfaceVariant="version8_2" '
                  'screenDensity="ldpi" glyphWidth="%d" glyphHeight="%d"/>' % (база, база))
    строки.append("</Picture>")
    return "\n".join(строки)


def записать(путь, текст):
    os.makedirs(os.path.dirname(путь), exist_ok=True)
    with open(путь, "w", encoding="utf-8-sig", newline="\n") as ф:   # с BOM — как выгружает платформа
        ф.write(текст)


def нарисовать(картинка, р, база):
    """Растр р×р. Малые исходники Codex нарисованы на сетке 16 от края до края: в кнопке такой значок
    упирается в соседей и выглядит срезанным (аудит малые_иконки) — у малой поле безопасности 1 px на 16."""
    if база != 16:
        return картинка if картинка.size == (р, р) else картинка.resize((р, р), Image.LANCZOS)
    поле = max(1, int(round(р / 16.0)))
    рисунок = картинка.crop(картинка.getchannel("A").getbbox() or (0, 0) + картинка.size)
    внутри = р - 2 * поле
    к = min(внутри / float(рисунок.width), внутри / float(рисунок.height))
    рисунок = рисунок.resize((max(1, int(round(рисунок.width * к))), max(1, int(round(рисунок.height * к)))),
                             Image.LANCZOS)
    холст = Image.new("RGBA", (р, р), (0, 0, 0, 0))
    холст.alpha_composite(рисунок, ((р - рисунок.width) // 2, (р - рисунок.height) // 2))
    return холст


def собрать(имя, синоним, исходник, база):
    картинка = Image.open(исходник).convert("RGBA")
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
        for файл, _, доля in МАСШТАБЫ + (("Picture.png", "", 1.0),):
            р = размер(база, доля)
            поток = io.BytesIO()
            нарисовать(картинка, р, база).save(поток, "PNG")
            # zip с постоянной датой — повторная сборка даёт тот же файл
            z.writestr(zipfile.ZipInfo(файл, (2026, 9, 28, 0, 0, 0)), поток.getvalue(), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("manifest.xml", (2026, 9, 28, 0, 0, 0)), манифест(база).encode("utf-8"),
                   zipfile.ZIP_DEFLATED)


def зарегистрировать(имена):
    путь = os.path.join(ИСХ, "Configuration.xml")
    т = open(путь, encoding="utf-8-sig", newline="").read()
    новые = [и for и in имена if "<CommonPicture>%s</CommonPicture>" % и not in т]
    if новые:
        последняя = list(re.finditer(r"\t\t\t<CommonPicture>[^<]+</CommonPicture>(\r?\n)", т))
        if not последняя:
            sys.exit("в Configuration.xml нет ни одной CommonPicture — некуда вставить (порядок типов строгий)")
        конец = последняя[-1].group(1)
        поз = последняя[-1].end()
        т = т[:поз] + "".join("\t\t\t<CommonPicture>%s</CommonPicture>%s" % (и, конец) for и in новые) + т[поз:]
        with open(путь, "w", encoding="utf-8-sig" if open(путь, "rb").read(3) == b"\xef\xbb\xbf" else "utf-8",
                  newline="") as ф:
            ф.write(т)
    return новые


def главная():
    имена = []
    for сюжет, (синоним, малая, большая) in СОСТАВ.items():
        if малая:
            собрать("УЗ_И" + сюжет, синоним, os.path.join(ИКОНКИ, "УЗ_И%s_16.png" % сюжет), 16)
            имена.append("УЗ_И" + сюжет)
        if большая:
            собрать("УЗ_И%s48" % сюжет, синоним, os.path.join(ИКОНКИ, "УЗ_И%s_48.png" % сюжет), 48)
            имена.append("УЗ_И%s48" % сюжет)
    новые = зарегистрировать(имена)
    print("иконок: %d, новых в Configuration.xml: %d" % (len(имена), len(новые)))


if __name__ == "__main__":
    главная()
