"""Макет «Договор об оказании платных образовательных услуг» для Документ.УЗ_ДоговорОбучения.

Текст договора собирает код печати (Документы.УЗ_ДоговорОбучения.ПечатьДоговора) — абзац за абзацем, макет
даёт только оформление: заголовок, раздел, абзац (одна широкая колонка — строка сама растёт по тексту),
реквизиты и подписи сторон в две колонки. Собирается компилятором навыка mxl-compile, как макет справки
(tools/макеты/макет_справки.py). Высоты строк — в единицах макета, не в пунктах (строка с текстом 8–9 пт ≈ 32–47).
После сборки выгрузка платформы переставляет шрифты (индекс <font>): в src_ext лежит макет из выгрузки.

    python tools\\макеты\\макет_договора.py
"""
import json
import os
import subprocess
import sys

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ЦЕЛЬ = os.path.join(КОРЕНЬ, "src_ext", "Documents", "УЗ_ДоговорОбучения", "Templates", "ПечатьДоговора", "Ext",
                    "Template.xml")
КОМПИЛЯТОР = os.path.join(os.path.expanduser("~"), ".claude", "skills", "mxl-compile", "scripts", "mxl-compile.ps1")


def описание():
    return {
        "columns": 3,
        "columnWidths": {"1": 262, "2": 16, "3": 262},
        "columnSets": {"текст": {"columns": 1, "columnWidths": {"1": 540}}},
        "fonts": {
            "default": {"face": "Arial", "size": 9},
            "жирный": {"face": "Arial", "size": 9, "bold": True},
            "заголовок": {"face": "Arial", "size": 12, "bold": True},
        },
        "styles": {
            "заголовок": {"font": "заголовок", "horizontalAlignment": "Center", "textPlacement": "Wrap"},
            "подзаголовок": {"font": "жирный", "horizontalAlignment": "Center", "textPlacement": "Wrap"},
            "справа": {"horizontalAlignment": "Right"},
            "раздел": {"font": "жирный", "horizontalAlignment": "Center", "verticalAlignment": "Bottom",
                       "textPlacement": "Wrap"},
            "абзац": {"horizontalAlignment": "Justify", "verticalAlignment": "Top", "textPlacement": "Wrap"},
            "сторона": {"font": "жирный", "verticalAlignment": "Top", "textPlacement": "Wrap"},
            "реквизит": {"verticalAlignment": "Top", "textPlacement": "Wrap"},
        },
        "areas": [
            {"name": "Заголовок", "columnSet": "текст", "rows": [
                {"height": 52, "cells": [{"col": 1, "template": "ДОГОВОР № [НомерДоговора]", "style": "заголовок"}]},
                {"cells": [{"col": 1, "param": "ВидДоговора", "style": "подзаголовок"}]},
                {"height": 47, "cells": [{"col": 1, "param": "ДатаДоговора", "style": "справа"}]},
                {"height": 16},
            ]},
            {"name": "Раздел", "columnSet": "текст", "rows": [
                {"height": 57, "cells": [{"col": 1, "param": "ЗаголовокРаздела", "style": "раздел"}]},
            ]},
            {"name": "Абзац", "columnSet": "текст", "rows": [
                {"cells": [{"col": 1, "param": "ТекстАбзаца", "style": "абзац"}]},
            ]},
            {"name": "СтороныШапка", "rows": [
                {"height": 57, "cells": [{"col": 1, "param": "СторонаСлева", "style": "сторона"},
                                         {"col": 3, "param": "СторонаСправа", "style": "сторона"}]},
            ]},
            {"name": "СтороныРеквизиты", "rows": [
                {"cells": [{"col": 1, "param": "РеквизитыСлева", "style": "реквизит"},
                           {"col": 3, "param": "РеквизитыСправа", "style": "реквизит"}]},
            ]},
            {"name": "СтороныПодписи", "rows": [
                {"height": 78},
                {"cells": [{"col": 1, "template": "_______________ / [ПодписьСлева] /", "style": "реквизит"},
                           {"col": 3, "template": "_______________ / [ПодписьСправа] /", "style": "реквизит"}]},
            ]},
        ],
    }


def main():
    путь_json = os.path.join(os.environ.get("TEMP", "."), "макет_договора.json")
    with open(путь_json, "w", encoding="utf-8") as ф:
        json.dump(описание(), ф, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(ЦЕЛЬ), exist_ok=True)
    р = subprocess.run(["powershell.exe", "-NoProfile", "-File", КОМПИЛЯТОР, "-JsonPath", путь_json,
                        "-OutputPath", ЦЕЛЬ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(р.stdout.strip())
    if р.returncode:
        print(р.stderr.strip())
        sys.exit(р.returncode)


if __name__ == "__main__":
    main()
