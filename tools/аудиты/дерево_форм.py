# -*- coding: utf-8 -*-
"""дерево_форм — элементы формы лежат в <ChildItems>, иначе платформа их молча выбрасывает.

Перенесено из «Путевых листов» (аудит_дерева_форм.py): там так пропали восемь полей
карточки автомобиля — XML правильный, конфигуратор грузит без жалоб, форма
открывается, а полей нет; код падает «Поле объекта не обнаружено», и виноватой
выглядит программа, а не разметка.

Правило платформы: дети группы, страницы, таблицы, командной панели — только внутри
<ChildItems>. Элемент — прямой потомок группы — не существует.

    python tools/аудиты/дерево_форм.py [каталог]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import общее  # noqa: E402

ИМЯ = "дерево_форм"
КОНТЕЙНЕРЫ = {"UsualGroup", "Page", "Pages", "Table", "ColumnGroup", "CommandBar", "AutoCommandBar",
              "ButtonGroup", "Popup"}
ЭЛЕМЕНТЫ = {"InputField", "CheckBoxField", "LabelField", "PictureField", "RadioButtonField",
            "HTMLDocumentField", "SpreadSheetDocumentField", "ProgressBarField", "TrackBarField",
            "TextDocumentField", "GeographicalSchemaField", "FormattedDocumentField", "PlannerField",
            "ChartField", "CalendarField", "PeriodField", "UsualGroup", "Page", "Pages", "Table", "Button",
            "ButtonGroup", "Popup", "ColumnGroup", "LabelDecoration", "PictureDecoration"}


def проверить(исх):
    р = общее.Результат(ИМЯ)
    форм = 0
    for ф in исх.формы():
        if not ф.своя:
            continue
        форм += 1
        for узел in ф.корень.iter():
            if общее.местное(узел.tag) not in КОНТЕЙНЕРЫ:
                continue
            for ребёнок in узел:
                тег = общее.местное(ребёнок.tag)
                if тег in ЭЛЕМЕНТЫ:
                    имя = ребёнок.get("name", "?")
                    р.ошибка(ф.отн, ф.строка_элемента(имя),
                             "%s «%s» лежит прямо в «%s», а не в его <ChildItems> — платформа его выбросит"
                             % (тег, имя, узел.get("name", "?")))
    р.проверено = "форм %d" % форм
    return р


if __name__ == "__main__":
    общее.запустить_один(sys.modules[__name__])
