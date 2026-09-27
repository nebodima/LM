# -*- coding: utf-8 -*-
"""повторы_тегов — свойство задаётся в XML один раз; второй такой же тег побеждает молча.

Перенесено из «Путевых листов» (аудит_повторов_тегов.py). Конфигуратор грузит файл с
двумя <PasswordMode> или двумя <ToolTip> подряд без единого слова, и в базе оказывается
ПОСЛЕДНЕЕ значение: в ПЛ токен бота показывался открытым текстом (PasswordMode true, следом
false), у ОГРН была подсказка про ОКПО.

Правило: внутри контейнера свойств один тег — один раз. Контейнеры свойств — <Properties>
объекта метаданных, <xr:StandardAttribute>, любой элемент формы (у него есть name и id) и
корень <Form>. Коллекции (ChildItems, ChildObjects, Events, Type…) законно повторяют детей.

    python tools/аудиты/повторы_тегов.py [каталог]
"""
import collections
import os
import sys

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import общее  # noqa: E402

ИМЯ = "повторы_тегов"


def _имя(узел):
    return etree.QName(узел).localname


def проверить(исх):
    р = общее.Результат(ИМЯ)
    файлов = 0
    for путь in исх.файлы(".xml"):
        файлов += 1
        try:
            корень = etree.fromstring(общее.читать(путь).encode("utf-8"))
        except etree.XMLSyntaxError as е:
            р.ошибка(исх.отн(путь), 1, "XML не разбирается: %s" % е)
            continue
        for узел in корень.iter(etree.Element):
            тег = _имя(узел)
            if not (тег in ("Properties", "StandardAttribute") or (тег == "Form" and узел.getparent() is None)
                    or (узел.get("name") is not None and узел.get("id") is not None)):
                continue
            дети = [д for д in узел if isinstance(д.tag, str)]
            for т, сколько in collections.Counter(_имя(д) for д in дети).items():
                if сколько > 1:
                    строки = [д.sourceline for д in дети if _имя(д) == т]
                    владелец = узел.get("name") or узел.findtext("{*}Name") or тег
                    р.ошибка(исх.отн(путь), строки[1], "у «%s» тег <%s> %d раза (строки %s) — платформа возьмёт "
                             "последний" % (владелец, т, сколько, ", ".join(map(str, строки))))
    р.проверено = "XML-файлов %d" % файлов
    return р


if __name__ == "__main__":
    общее.запустить_один(sys.modules[__name__])
