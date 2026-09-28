# -*- coding: utf-8 -*-
"""стандарт_форм — формы УЗ собраны по стандарту архитектора (docs/визуал/архитектор.md, разделы 1 и 3).

Повод — снимок формы урока от владельца (28.09.2026): «Длительность: 1,5000», заголовки «Явк/а»,
«Скидк/а», ярко-жёлтая колонка «К оплате», 13 колонок. Все причины видны в Form.xml, поэтому
проверяются здесь за миллисекунды, до конфигуратора. Номера — правила раздела 1 архитектора:

  п.1  у колонки таблицы Width=1 («сожми до минимума») — заголовок рвётся посреди слова;
       ширина колонки задаётся по смыслу (ссылка 20, число 10, дата 10, номер строки 3);
  п.2  длительность (часы) на экране — дробью «1,5000»: число часов вместо ч:мм, или время
       без формата ДФ=Ч:мм;
  п.3  EditFormat без Format — действует только при вводе, на экране формат по умолчанию;
  п.4  цвет вне палитры смыслов (docs/визуал/дизайнер.md, раздел 3): текст — только красный
       (минус, ошибка), серый (пояснение) и обычный; фон и рамка — только нейтральные; у кнопки
       фона нет вовсе (кнопку по умолчанию выделяет платформа);
  п.5  надпись вместо группы или подписи: надпись с шрифтом или цветом — самодельный заголовок
       раздела (нужна группа с заголовком); надпись «Подпись:» перед полем без заголовка;
  п.6  картинка в заголовке колонки (съедает 2–3 знака: «Скидк/а»);
  п.7  шапка документа: «Номер» и «Дата» — в одной горизонтальной группе, номер первым;
  п.9  поле шапки (вне таблицы) уже 10 знаков — число обрезается (кроме кода и номера);
  п.10 видимых колонок таблицы больше 8 — редкое скрыть (UserVisible=false);
  п.11 флажок вне таблицы подписью слева (у типовых — справа);
  п.12 сетка таблицы выключена (HorizontalLines/VerticalLines=false);
  п.14 HeaderHeight>1 или ручной перенос «\\n» в заголовке колонки;
  п.15 «Сформировать» у своей формы отчёта — не в командной панели формы или не кнопка по умолчанию;
  п.16 у карточки (элемент справочника, запись регистра, документ) нет стандартной кнопки по
       умолчанию «Записать и закрыть» / «Провести и закрыть»;
  п.17 путь к данным ведёт в никуда: «1/0:uuid…», «1/-2», несуществующий реквизит формы или объекта.

Временное исключение — ЗОНА_АГЕНТА: формы урока, календаря и панели ученика переделывает другой
агент (зона агента главных экранов, снять после слияния).

    python tools/аудиты/стандарт_форм.py [каталог]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import общее  # noqa: E402

ИМЯ = "стандарт_форм"
ЛФ = общее.ЛФ
V8 = "{http://v8.1c.ru/8.1/data/core}"
MD = "{http://v8.1c.ru/8.3/MDClasses}"

# зона агента главных экранов, снять после слияния
ЗОНА_АГЕНТА = set()   # снято 28.09 после слияния главных экранов

ПОЛЯ = ("InputField", "LabelField", "CheckBoxField", "PictureField", "RadioButtonField", "TextDocumentField",
        "SpreadSheetDocumentField", "HTMLDocumentField", "CalendarField", "ProgressBarField", "TrackBarField",
        "ChartField", "PlannerField", "FormattedDocumentField", "PeriodField")
КОЛОНКИ = ("InputField", "LabelField", "CheckBoxField", "PictureField")
ЦВЕТ_ТЕКСТА = ("TextColor", "TitleTextColor", "FooterTextColor", "HeaderTextColor")
ЦВЕТ_ФОНА = ("BackColor", "TitleBackColor", "FooterBackColor", "HeaderBackColor", "BorderColor")
ТЕКСТ_ПАЛИТРА = {"style:NegativeTextColor", "style:ToolTipTextColor", "style:FormTextColor", "style:FieldTextColor"}
ФОН_ПАЛИТРА = {"style:FormBackColor", "style:FieldBackColor", "style:TableHeaderBackColor"}
МАКС_КОЛОНОК = 8
ДЛИТЕЛЬНОСТЬ = re.compile(r"(Часов|Часы|Продолжительн|Длительн|ДлинаУрока)")
ФОРМАТ_ВРЕМЕНИ = re.compile(r"(ДФ|DF)\s*=\s*'?[^;']*([ЧH]{1,2}\s*:\s*мм|[ЧH]{1,2}\s*:\s*mm|[ЧH]{1,2} \"ч\.\")")

# стандартные реквизиты: имя -> вид значения
СТАНДАРТНЫЕ = {
    "Ref": "ссылка", "DeletionMark": "булево", "Code": "строка", "Description": "строка", "Parent": "ссылка",
    "Owner": "ссылка", "IsFolder": "булево", "Predefined": "булево", "PredefinedDataName": "строка",
    "Number": "строка", "Date": "дата", "Posted": "булево", "LineNumber": "число", "Period": "дата",
    "Recorder": "ссылка", "Active": "булево", "DataVersion": "строка", "RegisterRecords": "движения",
    "Type": "тип", "ValueType": "тип",
}


def _вид_типа(типы):
    """Вид значения по списку <v8:Type>: число/дата/время/строка/булево/ссылка/таблица/прочее."""
    if not типы:
        return None
    т = типы[0]
    if len(типы) > 1:
        return "составной"
    if т == "xs:decimal":
        return "число"
    if т == "xs:dateTime":
        return "дата"
    if т == "xs:string":
        return "строка"
    if т == "xs:boolean":
        return "булево"
    if "Ref." in т or т.startswith("cfg:EnumRef") or т.endswith("Ref"):
        return "ссылка"
    if т.endswith("ValueTable") or т.endswith("ValueTree") or т.endswith("DynamicList"):
        return "таблица"
    return "прочее"


def _типы_узла(узел):
    """[v8:Type…] из <Type> узла (форма или метаданные)."""
    for т in узел.iter():
        if общее.местное(т.tag) == "Type" and len(т):
            return [(в.text or "").strip() for в in т if общее.местное(в.tag) in ("Type", "TypeSet")]
    return []


def _типы_мд(т):
    return [(в.text or "").strip() for в in т if общее.местное(в.tag) in ("Type", "TypeSet")]


class Метаданные:
    """Реквизиты объекта с видами значений: {имя: вид}, {тч: {колонка: вид}}. Кэш на прогон."""

    def __init__(self, исх):
        self.исх = исх
        self.кэш = {}

    def объекта(self, тип, имя):
        к = (тип, общее.ключ(имя))
        if к in self.кэш:
            return self.кэш[к]
        о = self.исх.найти(тип, имя)
        итог = None
        if о is not None and о.xml and not о.заимствован:
            корень = self.исх.xml(о.xml)      # битый XML — None (его называют повторы_тегов, форм_id)
            if корень is not None:
                итог = self._разобрать(корень)
        self.кэш[к] = итог
        return итог

    def _разобрать(self, корень):
        рекв, тч = {}, {}
        узел = next(iter(корень), None)
        дети = узел.find(MD + "ChildObjects") if узел is not None else None
        if дети is None:
            return рекв, тч
        for р in дети:
            вид = общее.местное(р.tag)
            св = р.find(MD + "Properties")
            if св is None:
                continue
            имя = (св.findtext(MD + "Name") or "").strip()
            if вид in ("Attribute", "Dimension", "Resource", "AccountingFlag", "Column"):
                т = св.find(MD + "Type")
                рекв[имя] = _вид_типа(_типы_мд(т)) if т is not None else None
            elif вид == "TabularSection":
                колонки = {}
                вл = р.find(MD + "ChildObjects")
                if вл is not None:
                    for к in вл:
                        св2 = к.find(MD + "Properties")
                        if св2 is None:
                            continue
                        т = св2.find(MD + "Type")
                        колонки[(св2.findtext(MD + "Name") or "").strip()] = \
                            _вид_типа(_типы_мд(т)) if т is not None else None
                тч[имя] = колонки
        return рекв, тч


def _тип_ссылки(строка_типа):
    """«cfg:DocumentObject.УЗ_Урок» → («Document», «УЗ_Урок»)."""
    м = re.match(r"cfg:(\w+?)(Object|RecordManager|RecordSet|Manager)?\.(.+)$", строка_типа or "")
    if not м:
        return None
    return м.group(1), м.group(3)


class РазборФормы:
    def __init__(self, ф, мета):
        self.ф = ф
        self.мета = мета
        self.реквизиты = {}          # имя -> (вид, узел)
        self.колонки = {}            # реквизит -> {колонка: вид}
        self.объекты = {}            # реквизит -> (тип, имя) основного/объектного реквизита
        self.списки = {}             # реквизит-динсписок -> (главная таблица, текст запроса или "")
        self.доп = {}                # «Объект.ТЧ» -> {доп. колонка формы: вид}
        атр = ф.корень.find(ЛФ + "Attributes")
        if атр is None:
            return
        for а in атр.findall(ЛФ + "Attribute"):
            имя = а.get("name")
            типы = _типы_узла(а)
            self.реквизиты[имя] = (_вид_типа(типы), а)
            кол = {}
            колонки = а.find(ЛФ + "Columns")
            if колонки is not None:
                for к in колонки.iter(ЛФ + "Column"):
                    кол[к.get("name")] = _вид_типа(_типы_узла(к))
                for к in колонки.iter(ЛФ + "AdditionalColumns"):
                    self.доп[к.get("table")] = {кк.get("name"): _вид_типа(_типы_узла(кк))
                                                 for кк in к.iter(ЛФ + "Column")}
            self.колонки[имя] = кол
            if типы and типы[0].startswith("cfg:") and "DynamicList" not in типы[0]:
                т = _тип_ссылки(типы[0])
                if т:
                    self.объекты[имя] = т
            if типы and типы[0].endswith("DynamicList"):
                настр = а.find(ЛФ + "Settings")
                if настр is not None:
                    self.списки[имя] = ((настр.findtext(ЛФ + "MainTable") or "").strip(),
                                        (настр.findtext(ЛФ + "QueryText") or "")
                                        if (настр.findtext(ЛФ + "ManualQuery") or "") == "true" else "")

    def вид_пути(self, путь):
        """Вид значения по пути данных, None — не определить; «битый: …» — путь в никуда."""
        if re.match(r"^\d+/", путь or ""):
            return "битый: путь по внутренним номерам (реквизит удалён)"
        части = путь.split(".")
        if части[0] == "Items":
            return None
        if части[0] not in self.реквизиты:
            return "битый: нет реквизита формы «%s»" % части[0]
        вид, _ = self.реквизиты[части[0]]
        if len(части) == 1:
            return вид
        if части[0] in self.объекты:
            тип, имя = self.объекты[части[0]]
            м = self.мета.объекта(тип, имя)
            if м is None:
                return None
            рекв, тч = м
            п = части[1]
            if п in СТАНДАРТНЫЕ:
                return СТАНДАРТНЫЕ[п] if len(части) == 2 or п != "RegisterRecords" else None
            if п in рекв:
                return рекв[п] if len(части) == 2 else None
            if п in тч:
                if len(части) == 2:
                    return "таблица"
                к = части[2]
                if к in СТАНДАРТНЫЕ:
                    return СТАНДАРТНЫЕ[к]
                if к in тч[п]:
                    return тч[п][к] if len(части) == 3 else None
                доп = self.доп.get("%s.%s" % (части[0], п)) or {}
                if к in доп:
                    return доп[к] if len(части) == 3 else None
                return "битый: нет колонки «%s» в табличной части «%s»" % (к, п)
            if тип in ("Catalog", "Document", "InformationRegister") and п not in ("ТабличныйДокумент",):
                return "битый: нет реквизита «%s» у %s.%s" % (п, тип, имя)
            return None
        if части[0] in self.списки:
            таблица, запрос = self.списки[части[0]]
            п = части[1]
            if запрос:
                м = re.search(r"([^\n,]*?)\s+КАК\s+%s\b" % re.escape(п), запрос, re.I)
                if м and re.search(r"ДОБАВИТЬКДАТЕ|DATEADD|ДАТАВРЕМЯ\s*\(", м.group(1), re.I):
                    return "дата"
                if м and re.search(r"КАК\s+СТРОКА|AS\s+STRING|\"", м.group(1), re.I):
                    return "строка"
                if м and ДЛИТЕЛЬНОСТЬ.search(п):
                    return "число"      # длительность из запроса без перевода во время — число часов
            if п in СТАНДАРТНЫЕ:
                if запрос:      # в произвольном запросе поля — по его псевдонимам (Ссылка, Наименование, Код)
                    return "битый: в списке с произвольным запросом нет поля «%s» — имя поля из запроса" % п
                return СТАНДАРТНЫЕ[п]
            if "." in таблица:
                тип, имя = таблица.split(".", 1)
                м = self.мета.объекта(тип, имя)
                if м and п in м[0]:
                    return м[0][п]
            return None
        кол = self.колонки.get(части[0]) or {}
        if len(части) == 2 and части[1] in кол:
            return кол[части[1]]
        return None


def _в_таблице(узел, родители):
    р = родители.get(узел)
    while р is not None:
        if общее.местное(р.tag) == "Table":
            return р
        р = родители.get(р)
    return None


def _скрыт(узел):
    if общее.свойство(узел, "Visible") == "false":
        return True
    ув = узел.find(ЛФ + "UserVisible")
    if ув is not None:
        for у in ув.iter():
            if общее.местное(у.tag) == "Common" and (у.text or "").strip() == "false":
                return True
    return False


def _заголовок_сырой(узел):
    т = узел.find(ЛФ + "Title")
    if т is None:
        return ""
    for с in т.iter(V8 + "content"):
        return с.text or ""
    return ""


def _видимые_колонки(таблица):
    итог = []

    def обойти(узел):
        дети = узел.find(ЛФ + "ChildItems")
        if дети is None:
            return
        for д in дети:
            т = общее.местное(д.tag)
            if _скрыт(д):
                continue
            if т == "ColumnGroup":
                обойти(д)
            elif т in КОЛОНКИ:
                итог.append(д)
    обойти(таблица)
    return итог


def _вид_формы(ф):
    """«карточка»/«документ»/«отчёт»/None — для правил 7, 15, 16."""
    части = ф.имя.split("/")
    if части[0] == "Reports":
        return "отчёт"
    if части[0] == "CommonForms" and "Отчет" in части[-1]:
        return "отчёт"
    if части[0] == "Documents" and ф.вид == "ФормаДокумента":
        return "документ"
    if части[0] == "Catalogs" and ф.вид == "ФормаЭлемента":
        return "карточка"
    if части[0] == "InformationRegisters" and ф.вид == "ФормаЗаписи":
        return "карточка"
    return None


def _проводится(ф):
    о = ф.владелец
    if о is None or not о.xml:
        return False
    return "<Posting>Allow</Posting>" in общее.читать(о.xml).split("<ChildObjects>")[0]


def _в_панели_формы(узел, родители):
    р = родители.get(узел)
    while р is not None:
        if общее.местное(р.tag) == "AutoCommandBar":
            return р.get("id") == "-1"
        р = родители.get(р)
    return False


def проверить(исх):
    р = общее.Результат(ИМЯ)
    мета = Метаданные(исх)
    форм = элементов = 0
    for ф in исх.формы():
        if not ф.своя or ф.имя in ЗОНА_АГЕНТА:
            continue
        форм += 1
        разбор = РазборФормы(ф, мета)
        родители = ф.родители()
        отн = ф.отн

        def ош(имя, текст):
            р.ошибка(отн, ф.строка_элемента(имя) if имя else 1, текст)

        for у in ф.корень.iter():
            т = общее.местное(у.tag)
            имя = у.get("name")
            if not имя or т in ("Attribute", "Command", "Column", "ContextMenu", "ExtendedTooltip"):
                continue
            элементов += 1
            таблица = _в_таблице(у, родители) if т in КОЛОНКИ + ("ColumnGroup",) else None
            # п.1 Width=1 у колонки
            if таблица is not None and т != "PictureField" and общее.свойство(у, "Width") == "1":
                ош(имя, "п.1 колонка «%s»: Width=1 — заголовок рвётся посреди слова; ширина по смыслу "
                   "(ссылка 20, число 10, дата 10)" % имя)
            # п.9 узкая ширина поля в шапке (кроме кода): число обрезается, итоги — 12
            if таблица is None and т in ("InputField", "LabelField") and (общее.свойство(у, "Width") or "").isdigit()                     and int(общее.свойство(у, "Width")) < 10 and                     (общее.свойство(у, "DataPath") or "").rsplit(".", 1)[-1] not in ("Code", "Number"):
                ош(имя, "п.9 «%s»: Width=%s в шапке — ширину поля ставит платформа (итоги — 12)" % (
                    имя, общее.свойство(у, "Width")))
            # п.6 картинка в заголовке колонки
            if таблица is not None and т != "PictureField" and у.find(ЛФ + "HeaderPicture") is not None:
                ош(имя, "п.6 колонка «%s»: картинка в заголовке — съедает ширину заголовка" % имя)
            # п.14 ручной перенос в заголовке колонки
            if таблица is not None and "\n" in _заголовок_сырой(у):
                ош(имя, "п.14 колонка «%s»: ручной перенос «\\n» в заголовке — укоротить заголовок" % имя)
            # п.3 EditFormat без Format
            if у.find(ЛФ + "EditFormat") is not None and у.find(ЛФ + "Format") is None:
                ош(имя, "п.3 «%s»: EditFormat без Format — на экране формат по умолчанию" % имя)
            # п.4 цвет вне палитры
            for тег in ЦВЕТ_ТЕКСТА + ЦВЕТ_ФОНА:
                ц = общее.свойство(у, тег)
                if ц is None:
                    continue
                ц = ц.strip()
                if т in ("Button", "ButtonGroup") and тег in ЦВЕТ_ФОНА:
                    ош(имя, "п.4 кнопка «%s»: %s=%s — фон кнопке не задают, кнопку по умолчанию выделяет "
                       "платформа" % (имя, тег, ц))
                elif тег in ЦВЕТ_ТЕКСТА and ц not in ТЕКСТ_ПАЛИТРА:
                    ош(имя, "п.4 «%s»: %s=%s вне палитры (текст — только красный, серый, обычный)" % (имя, тег, ц))
                elif тег in ЦВЕТ_ФОНА and (ц not in ФОН_ПАЛИТРА or (тег == "BackColor" and ц == "style:TableHeaderBackColor")):
                    ош(имя, "п.4 «%s»: %s=%s — яркая заливка вне палитры (фон только нейтральный)" % (имя, тег, ц))
            # п.5 надпись вместо группы
            if т == "LabelDecoration":
                шрифт = у.find(ЛФ + "Font")
                if шрифт is not None and (шрифт.get("bold") == "true" or шрифт.get("height") or
                                          шрифт.get("scale")):
                    ош(имя, "п.5 надпись «%s» оформлена шрифтом как заголовок раздела — нужна группа "
                       "с заголовком (ShowTitle=true)" % (общее.заголовок(у) or имя))
                elif общее.свойство(у, "TextColor") in ("style:AccentColor", "style:SpecialTextColor"):
                    pass       # уже п.4
                else:
                    подпись = общее.заголовок(у)
                    сосед = _следующий(у, родители)
                    if подпись.endswith(":") and сосед is not None and \
                            общее.местное(сосед.tag) in ПОЛЯ and общее.свойство(сосед, "TitleLocation") == "None":
                        ош(имя, "п.5 надпись «%s» вместо подписи поля «%s» — задать заголовок самому полю"
                           % (подпись, сосед.get("name")))
            # п.11 флажок вне таблицы подписью слева
            if т == "CheckBoxField" and таблица is None and \
                    общее.свойство(у, "CheckBoxType") not in ("Switcher", "Tumbler") and \
                    общее.свойство(у, "TitleLocation") not in ("Right", "None"):
                ош(имя, "п.11 флажок «%s»: подпись слева — у типовых TitleLocation=Right" % имя)
            # п.12, п.14, п.10 — таблица
            if т == "Table":
                if общее.свойство(у, "HorizontalLines") == "false" or общее.свойство(у, "VerticalLines") == "false":
                    ош(имя, "п.12 таблица «%s»: сетка выключена (HorizontalLines/VerticalLines=false)" % имя)
                вв = общее.свойство(у, "HeaderHeight")
                if вв and вв.isdigit() and int(вв) > 1:
                    ош(имя, "п.14 таблица «%s»: HeaderHeight=%s — перенос заголовков посреди слова" % (имя, вв))
                видимых = _видимые_колонки(у)
                if len(видимых) > МАКС_КОЛОНОК and not _скрыт(у):
                    ош(имя, "п.10 таблица «%s»: видимых колонок %d > %d — редкое скрыть (UserVisible=false)"
                       % (имя, len(видимых), МАКС_КОЛОНОК))
            # п.2, п.17 путь к данным
            путь = общее.свойство(у, "DataPath")
            if путь and т in ПОЛЯ + ("Table",):
                вид = разбор.вид_пути(путь.strip())
                if вид and вид.startswith("битый"):
                    ош(имя, "п.17 «%s»: %s (DataPath %s)" % (имя, вид[7:], путь.strip()))
                elif т in ("InputField", "LabelField") and not _скрыт_насовсем(у) and \
                        ДЛИТЕЛЬНОСТЬ.search(путь.rsplit(".", 1)[-1]) and "ЗаЧас" not in путь:
                    if вид == "число":
                        ош(имя, "п.2 «%s»: длительность числом часов («1,5000») — показать ч:мм" % имя)
                    elif вид == "дата" and not ФОРМАТ_ВРЕМЕНИ.search(общее.заголовок(у, "Format") or ""):
                        ош(имя, "п.2 «%s»: время без формата ДФ=Ч:мм — на экране «1:30:00» или дата" % имя)
        вид_ф = _вид_формы(ф)
        if вид_ф in ("карточка", "документ"):
            _кнопка_по_умолчанию(ф, вид_ф, ош)
        if вид_ф == "документ":
            _шапка_документа(ф, разбор, родители, ош)
        if вид_ф == "отчёт":
            for у in ф.корень.iter(ЛФ + "Button"):
                команда = общее.свойство(у, "CommandName") or ""
                if команда.endswith("StandardCommand.Generate") or re.search(r"Command\.Сформировать\w*$", команда):
                    if not _в_панели_формы(у, родители):
                        ош(у.get("name"), "п.15 «Сформировать» («%s») не в командной панели формы" % у.get("name"))
                    elif общее.свойство(у, "DefaultButton") != "true":
                        ош(у.get("name"), "п.15 «Сформировать» («%s») не кнопка по умолчанию" % у.get("name"))
    р.проверено = "форм %d (без зоны агента главных экранов: %d), элементов %d" % (
        форм, len(ЗОНА_АГЕНТА), элементов)
    return р


def _скрыт_насовсем(у):
    return общее.свойство(у, "Visible") == "false"


def _следующий(у, родители):
    р = родители.get(у)
    if р is None:
        return None
    дети = list(р)
    i = дети.index(у)
    for д in дети[i + 1:]:
        if общее.местное(д.tag) in ПОЛЯ + ("LabelDecoration", "UsualGroup", "Button", "Table"):
            return д
    return None


def _кнопка_по_умолчанию(ф, вид_ф, ош):
    нужна = "StandardCommand.WriteAndClose"
    if вид_ф == "документ" and _проводится(ф):
        нужна = "StandardCommand.PostAndClose"
    по_умолчанию = [к for к in ф.корень.iter(ЛФ + "Button") if общее.свойство(к, "DefaultButton") == "true"]
    if not по_умолчанию:
        ош(None, "п.16 у формы нет кнопки по умолчанию «%s» (Button с DefaultButton=true и Form.%s)" % (
            "Провести и закрыть" if нужна.endswith("PostAndClose") else "Записать и закрыть", нужна))
        return
    главный = any((а.findtext(ЛФ + "MainAttribute") or "") == "true"
                  for а in ф.корень.iter(ЛФ + "Attribute"))
    for к in по_умолчанию:
        команда = общее.свойство(к, "CommandName") or ""
        if not главный and команда == "Form.Command.ЗаписатьИЗакрыть":
            continue        # форма без основного реквизита пишет сама (УЗ_Настройки: одна запись регистра)
        if not команда.endswith(нужна):
            ош(к.get("name"), "п.16 кнопка по умолчанию «%s» — не стандартная Form.%s" % (к.get("name"), нужна))


def _шапка_документа(ф, разбор, родители, ош):
    номер = дата = None
    for у in ф.корень.iter():
        п = общее.свойство(у, "DataPath") if общее.местное(у.tag) in ПОЛЯ else None
        if п == "Объект.Number" and номер is None:
            номер = у
        elif п == "Объект.Date" and дата is None:
            дата = у
    if номер is None and "<NumberLength>0</NumberLength>" in общее.читать(ф.владелец.xml).split("<ChildObjects>")[0]:
        return          # документ без номера (график работы педагога)
    if номер is None or дата is None:
        ош(None, "п.7 шапка документа: нет поля %s" % ("«Номер»" if номер is None else "«Дата»"))
        return
    группа = родители.get(родители.get(номер))
    if группа is not родители.get(родители.get(дата)) or общее.свойство(группа, "Group") not in (
            "Horizontal", "AlwaysHorizontal"):
        ош(номер.get("name"), "п.7 шапка документа: «Номер» и «Дата» не в одной горизонтальной группе "
           "(схема «Номер от Дата»)")
        return
    дети = list(родители.get(номер))
    if дети.index(номер) > дети.index(дата):
        ош(номер.get("name"), "п.7 шапка документа: «Дата» стоит перед «Номером» (схема «Номер от Дата»)")


if __name__ == "__main__":
    общее.запустить_один(sys.modules[__name__])
