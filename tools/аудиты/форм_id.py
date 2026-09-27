# -*- coding: utf-8 -*-
"""форм_id — дубли id и имён элементов внутри одной Form.xml.

Платформа различает элементы формы по числовому id. Два элемента с одним id —
не «лишняя строчка»: один из них платформа гасит (в ПЛ поле «Водитель» делило
id с подсказкой другой страницы и переставало показывать значение). Столкновения
появляются, когда форму правят руками или скриптом, — а при переносе форм
LM → УЗ_ext правка скриптом неизбежна.

Нумерации раздельные: элементы (вместе с командными панелями, подсказками,
контекстными меню), реквизиты формы, колонки каждого реквизита, команды формы.
Заодно Form.xml проверяется на правильность XML.

    python tools/аудиты/форм_id.py [каталог] [--только-продукт]
"""
import collections
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import общее  # noqa: E402

ИМЯ = "форм_id"
_ЭЛЕМЕНТ = re.compile(r'<(\w+) name="([^"]+)" id="(-?\d+)"')


def проверить(исх):
    р = общее.Результат(ИМЯ)
    форм = 0
    for путь in исх.файлы(".xml"):
        if os.path.basename(путь) != "Form.xml":
            continue
        форм += 1
        т = общее.читать(путь)
        отн = исх.отн(путь)
        try:
            ET.fromstring(т.encode("utf-8"))
        except ET.ParseError as е:
            р.ошибка(отн, getattr(е, "position", (0,))[0], "Form.xml — неверный XML: %s" % е)
            continue

        def строка(смещ):
            return т.count("\n", 0, смещ) + 1

        # границы разделов формы верхнего уровня
        разделы = []
        for тег in ("<Attributes>", "<Commands>", "<Parameters>", "<CommandInterface>"):
            н = т.find("\n\t" + тег)
            if н < 0:
                н = т.find(тег)
            if н >= 0:
                разделы.append((н, тег.strip("<>")))
        разделы.sort()

        def раздел(смещ):
            имя = "Elements"
            for н, тег in разделы:
                if смещ > н:
                    имя = тег
            return имя

        группы = collections.defaultdict(list)     # (нумерация) -> [(id, имя, смещ)]
        имена = collections.defaultdict(list)
        реквизит = None
        for найд in _ЭЛЕМЕНТ.finditer(т):
            тег, имя, номер = найд.groups()
            где = раздел(найд.start())
            if где == "Elements":
                группы["элементы"].append((номер, имя, найд.start()))
                имена["элементы"].append((имя, найд.start()))
            elif где == "Attributes":
                if тег == "Attribute":
                    реквизит = имя
                    группы["реквизиты"].append((номер, имя, найд.start()))
                    имена["реквизиты"].append((имя, найд.start()))
                elif тег == "Column" and реквизит:
                    группы["колонки " + реквизит].append((номер, имя, найд.start()))
            elif где == "Commands" and тег == "Command":
                группы["команды"].append((номер, имя, найд.start()))
                имена["команды"].append((имя, найд.start()))
        for нумерация, список in группы.items():
            по_id = collections.defaultdict(list)
            for номер, имя, смещ in список:
                по_id[номер].append((имя, смещ))
            for номер, кто in по_id.items():
                if len(кто) > 1:
                    р.ошибка(отн, строка(кто[1][1]), "id=%s (%s) у %d: %s" % (
                        номер, нумерация, len(кто), ", ".join(и for и, _ in кто)))
        for нумерация, список in имена.items():
            счёт = collections.Counter(и for и, _ in список)
            for имя, к in счёт.items():
                if к > 1:
                    второе = [с for и, с in список if и == имя][1]
                    р.ошибка(отн, строка(второе), "имя «%s» (%s) повторяется %d раза" % (имя, нумерация, к))
    р.проверено = "форм %d" % форм
    return р


if __name__ == "__main__":
    общее.запустить_один(sys.modules[__name__])
