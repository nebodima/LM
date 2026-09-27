# -*- coding: utf-8 -*-
"""Сборка исходников расширения УЗ_ext («Учёт занятий») из XML-выгрузки конфигурации LM.

    python tools/собрать_src_ext.py            # сборка + проверки + самотест проверок
    python tools/собрать_src_ext.py --проверка # только проверки готового src_ext (без пересборки)

Что делает (этапы 1–2 плана docs/план_перевода_в_расширение.md):
  * src_ext пересобирается с нуля при каждом прогоне; uuid детерминированные
    (uuid5 от полного имени объекта/реквизита) — повторная сборка даёт те же файлы;
  * Configuration.xml расширения, язык, заимствованные Организации/Пользователи (без реквизитов);
  * перенос метаданных данных (справочники, документы, регистры, перечисление, журналы,
    регламентное) с переименованием LM_ -> УЗ_ по таблице ПЕРЕИМЕНОВАНИЯ; формы, макеты, команды
    и модули объектов пока НЕ переносятся (ПЕРЕНОСИТЬ_ФОРМЫ/МОДУЛИ — задел);
  * чистка ссылок на объекты, которых нет в расширении (БСП и пр.), точечные правки типов;
  * роль УЗ_ОсновнаяРоль, подсистемы УЗ_УчетЗанятий/*;
  * наложение src_manual (ручные объекты, uuid не трогаются) и регистрация в Configuration.xml;
  * офлайн-проверки (ИТОГО ошибок) и мутационный самотест проверок.

Конфигуратор 1С не запускается, базы не трогаются.
Заимствованные объекты — без ExtendedConfigurationObject: сопоставление с хозяином по имени
(как у ПЛ_ext, одна сборка на УНФ/БП/УТ — у хозяев разные uuid Организаций/Пользователей).
"""
import copy
import io
import os
import re
import shutil
import sys
import tempfile
import uuid

from lxml import etree

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

КОРЕНЬ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ИСТОЧНИК = КОРЕНЬ                                   # XML-выгрузка конфигурации LM
ЦЕЛЬ = os.path.join(КОРЕНЬ, "src_ext")
РУЧНЫЕ = os.path.join(КОРЕНЬ, "src_manual")

# Выгрузки хозяев — только для справки (проверка, что заимствуемое есть у всех по имени)
ХОЗЯЕВА = {
    "БП 3.0": r"C:\Users\User02\Documents\PRODIGY\cf_dump_bp",
    "УТ 11.5": r"C:\Users\User02\Documents\IMPORTTRADE\УТ_11_5",
    "УНФ 3.0": r"C:\Users\User02\Documents\dumps\UNF_3012",
}

# Фиксированное пространство имён для uuid5. НЕ МЕНЯТЬ: от него зависят все uuid расширения.
ПИ_UUID = uuid.UUID("5b0e3c1a-7d2f-4e6b-9a41-2c8f1d7e5a90")

ИМЯ_РАСШИРЕНИЯ = "УЗ_ext"
СИНОНИМ_РАСШИРЕНИЯ = "Учёт занятий"
ПРЕФИКС = "УЗ_"
ВЕРСИЯ_РАСШИРЕНИЯ = "0.1.0"
РОЛЬ = "УЗ_ОсновнаяРоль"
МОДУЛЬ_СЕРВЕР = "УЗ_Сервер"

# Версия формата перенесённых файлов: None — оставить как в выгрузке LM (2.11, 8.3.14).
ВЕРСИЯ_ФОРМАТА_ПЕРЕНОСА = None
ВЕРСИЯ_ФОРМАТА_НОВЫХ = "2.20"

ПЕРЕНОСИТЬ_ФОРМЫ = False     # задел: формы/макеты/команды объектов (этап 3)
ПЕРЕНОСИТЬ_МОДУЛИ = False    # задел: ObjectModule/ManagerModule/RecordSetModule (этап 3)

# ---------------------------------------------------------------------------------------------
# Таблица переноса: (класс, имя в LM) -> (новое имя, синоним или None — оставить, подсистема)
# Чтобы добавить отчёт/обработку/общий модуль — дописать строку (и включить перенос форм/модулей).
# ---------------------------------------------------------------------------------------------
ПЕРЕИМЕНОВАНИЯ = {
    ("Catalog", "LM_Абонемент"): ("УЗ_Абонемент", None, "УЗ_Справочники"),
    ("Catalog", "LM_ГруппыОбучения"): ("УЗ_ГруппыОбучения", None, "УЗ_Справочники"),
    ("Catalog", "LM_ДисконтныеКарты"): ("УЗ_ДисконтныеКарты", None, "УЗ_Справочники"),
    ("Catalog", "LM_ИсточникиИнформации"): ("УЗ_ИсточникиИнформации", None, "УЗ_Справочники"),
    ("Catalog", "LM_Подразделения"): ("УЗ_Подразделения", None, "УЗ_Справочники"),
    ("Catalog", "LM_Помещения"): ("УЗ_Помещения", None, "УЗ_Справочники"),
    ("Catalog", "LM_ПредметыОбучения"): ("УЗ_ПредметыОбучения", None, "УЗ_Справочники"),
    ("Catalog", "LM_Скидки"): ("УЗ_Скидки", None, "УЗ_Справочники"),
    ("Catalog", "LM_СтавкиПедагогов"): ("УЗ_СтавкиПедагогов", None, "УЗ_Справочники"),
    ("Catalog", "LM_Статусы"): ("УЗ_Статусы", None, "УЗ_Справочники"),
    ("Catalog", "LM_Тарифы"): ("УЗ_Тарифы", None, "УЗ_Справочники"),
    ("Catalog", "LM_ФизЛица"): ("УЗ_ФизЛица", None, "УЗ_Справочники"),
    ("Catalog", "LM_Фото"): ("УЗ_Фото", None, "УЗ_Служебные"),
    ("Catalog", "Кассы"): ("УЗ_Кассы", ("Кассы", "Касса", "Кассы"), "УЗ_Касса"),
    ("Catalog", "СтатьиЗатрат"): ("УЗ_СтатьиДвиженияДенег",
                                  ("Статьи движения денег", "Статья движения денег", "Статьи движения денег"),
                                  "УЗ_Касса"),
    ("Document", "LM_ГрафикРабочегоВремениПедагога"): ("УЗ_ГрафикРабочегоВремениПедагога", None, "УЗ_Документы"),
    ("Document", "LM_ДополнительныеРасходы"): ("УЗ_ДополнительныеРасходы", None, "УЗ_Касса"),
    ("Document", "LM_НачислениеБонусов"): ("УЗ_НачислениеБонусов", None, "УЗ_Документы"),
    ("Document", "LM_НачисленияПедагогам"): ("УЗ_НачисленияПедагогам", None, "УЗ_Документы"),
    ("Document", "LM_ПеремещениеДенег"): ("УЗ_ПеремещениеДенег", None, "УЗ_Касса"),
    ("Document", "LM_РасчетЗарплаты"): ("УЗ_РасчетЗарплаты", None, "УЗ_Документы"),
    ("Document", "LM_СписаниеОстатков"): ("УЗ_СписаниеОстатков", None, "УЗ_Документы"),
    ("Document", "LM_Урок"): ("УЗ_Урок", None, "УЗ_Документы"),
    ("Document", "ПриходныйКассовыйОрдер"): ("УЗ_ПриходДенег",
                                             ("Приход денег (ПКО)", "Приход денег", "Приходы денег"), "УЗ_Касса"),
    ("Document", "РасходныйКассовыйОрдер"): ("УЗ_РасходДенег",
                                             ("Расход денег (РКО)", "Расход денег", "Расходы денег"), "УЗ_Касса"),
    ("AccumulationRegister", "LM_ДвижениеДисконтныхКарт"): ("УЗ_ДвижениеДисконтныхКарт", None, "УЗ_Служебные"),
    ("AccumulationRegister", "LM_Касса"): ("УЗ_Касса", None, "УЗ_Служебные"),
    ("AccumulationRegister", "LM_Расходы"): ("УЗ_Расходы", None, "УЗ_Служебные"),
    ("AccumulationRegister", "LM_РасчетыПоЗарплате"): ("УЗ_РасчетыПоЗарплате", None, "УЗ_Служебные"),
    ("AccumulationRegister", "LM_СписанияСуммЗаУроки"): ("УЗ_СписанияСуммЗаУроки", None, "УЗ_Служебные"),
    ("InformationRegister", "LM_Настройки"): ("УЗ_Настройки", None, "УЗ_Настройки"),
    ("InformationRegister", "LM_Оповещения"): ("УЗ_Оповещения", None, "УЗ_Служебные"),
    ("InformationRegister", "LM_ЦеныТарифов"): ("УЗ_ЦеныТарифов", None, "УЗ_Справочники"),
    ("Enum", "LM_ВидыОпераций"): ("УЗ_ВидыОпераций", None, "УЗ_Служебные"),
    ("DocumentJournal", "LM_КассовыйЖурнал"): ("УЗ_КассовыйЖурнал", None, "УЗ_Касса"),
    ("DocumentJournal", "LM_ОбщийЖурнал"): ("УЗ_ОбщийЖурнал", None, "УЗ_Документы"),
    ("ScheduledJob", "LM_ПроверкаЗадолженности"): ("УЗ_ПроверкаЗадолженности", None, None),
}

# Заимствуются у хозяина без реквизитов (есть в УНФ/БП/УТ под этими именами)
ЗАИМСТВОВАННЫЕ = [("Catalog", "Организации"), ("Catalog", "Пользователи")]

# Подсистемы: (имя, синоним, в командном интерфейсе)
ПОДСИСТЕМА_КОРЕНЬ = ("УЗ_УчетЗанятий", "Учёт занятий")
ПОДСИСТЕМЫ = [
    ("УЗ_Документы", "Документы", True),
    ("УЗ_Касса", "Касса", True),
    ("УЗ_Справочники", "Справочники", True),
    ("УЗ_Отчеты", "Отчеты", True),
    ("УЗ_Настройки", "Настройки", True),
    ("УЗ_Служебные", "Служебные объекты", False),
]

# Порядок типов в ChildObjects Configuration.xml — как у платформы (сверено с выгрузками БП/УТ/LM)
ПОРЯДОК = [
    ("Language", "Languages"), ("Subsystem", "Subsystems"), ("StyleItem", "StyleItems"), ("Style", "Styles"),
    ("CommonPicture", "CommonPictures"), ("SessionParameter", "SessionParameters"), ("Role", "Roles"),
    ("CommonTemplate", "CommonTemplates"), ("FilterCriterion", "FilterCriteria"), ("CommonModule", "CommonModules"),
    ("CommonAttribute", "CommonAttributes"), ("ExchangePlan", "ExchangePlans"), ("XDTOPackage", "XDTOPackages"),
    ("WebService", "WebServices"), ("HTTPService", "HTTPServices"), ("WSReference", "WSReferences"),
    ("EventSubscription", "EventSubscriptions"), ("ScheduledJob", "ScheduledJobs"),
    ("SettingsStorage", "SettingsStorages"), ("FunctionalOption", "FunctionalOptions"),
    ("FunctionalOptionsParameter", "FunctionalOptionsParameters"), ("DefinedType", "DefinedTypes"),
    ("Bot", "Bots"), ("CommonCommand", "CommonCommands"), ("CommandGroup", "CommandGroups"),
    ("Constant", "Constants"), ("CommonForm", "CommonForms"), ("Catalog", "Catalogs"), ("Document", "Documents"),
    ("DocumentNumerator", "DocumentNumerators"), ("Sequence", "Sequences"), ("DocumentJournal", "DocumentJournals"),
    ("Enum", "Enums"), ("Report", "Reports"), ("DataProcessor", "DataProcessors"),
    ("InformationRegister", "InformationRegisters"), ("AccumulationRegister", "AccumulationRegisters"),
    ("ChartOfCharacteristicTypes", "ChartsOfCharacteristicTypes"), ("ChartOfAccounts", "ChartsOfAccounts"),
    ("AccountingRegister", "AccountingRegisters"), ("ChartOfCalculationTypes", "ChartsOfCalculationTypes"),
    ("CalculationRegister", "CalculationRegisters"), ("BusinessProcess", "BusinessProcesses"), ("Task", "Tasks"),
    ("ExternalDataSource", "ExternalDataSources"), ("IntegrationService", "IntegrationServices"),
]
ПАПКА = dict(ПОРЯДОК)
КЛАСС_ПО_ПАПКЕ = {п: к for к, п in ПОРЯДОК}
КЛАССЫ = sorted([к for к, _ in ПОРЯДОК] + ["Configuration"], key=len, reverse=True)
РЕ_КЛАСС = "|".join(КЛАССЫ)

NS = {
    "md": "http://v8.1c.ru/8.3/MDClasses",
    "xr": "http://v8.1c.ru/8.3/xcf/readable",
    "v8": "http://v8.1c.ru/8.1/data/core",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "pd": "http://v8.1c.ru/8.3/xcf/predef",
}
MD = "{%s}" % NS["md"]
XR = "{%s}" % NS["xr"]
V8 = "{%s}" % NS["v8"]
XSI = "{%s}" % NS["xsi"]

ШАПКА_MD = ('<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" '
            'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
            'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
            'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
            'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
            'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
            'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
            'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
            'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
            'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
            'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
            'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
            'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="%s">' % ВЕРСИЯ_ФОРМАТА_НОВЫХ)
ДЕКЛ = '<?xml version="1.0" encoding="UTF-8"?>\n'

ЖУРНАЛ = {"удалено_типов": [], "удалено_реквизитов": [], "удалено_ссылок": [], "правки": [],
          "формы": 0, "команды": 0, "макеты": 0, "очищено_ссылок_на_формы": 0}


# ------------------------------------------------------------------------------------------ утилиты
def ууид(ключ):
    return str(uuid.uuid5(ПИ_UUID, ключ))


def писать(путь, текст):
    os.makedirs(os.path.dirname(путь), exist_ok=True)
    with io.open(путь, "w", encoding="utf-8-sig", newline="\r\n") as ф:
        ф.write(текст)


def писать_дерево(путь, корень, версия=None):
    if версия:
        корень.set("version", версия)
    текст = etree.tostring(корень, encoding="unicode")
    писать(путь, ДЕКЛ + текст)


def читать_дерево(путь):
    парсер = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
    return etree.parse(путь, парсер).getroot()


def лок(тег):
    return etree.QName(тег).localname if isinstance(тег, str) else ""


def удалить(эл):
    """Удалить элемент, сохранив отступы соседей."""
    родитель = эл.getparent()
    пред = эл.getprevious()
    if пред is not None:
        пред.tail = эл.tail
    else:
        родитель.text = эл.tail
    родитель.remove(эл)


def синоним_xml(текст, отступ):
    return ("%s<Synonym>\n%s\t<v8:item>\n%s\t\t<v8:lang>ru</v8:lang>\n%s\t\t<v8:content>%s</v8:content>\n"
            "%s\t</v8:item>\n%s</Synonym>" % (отступ, отступ, отступ, отступ, текст, отступ, отступ))


def mdo(корень):
    for эл in корень:
        if isinstance(эл.tag, str):
            return эл
    return None


def имя_объекта(эл):
    н = эл.find(MD + "Properties/" + MD + "Name")
    return н.text if н is not None else None


# -------------------------------------------------------------------------- переименование ссылок
КАРТА_ИМЁН = {(к, с): н for (к, с), (н, _, _) in ПЕРЕИМЕНОВАНИЯ.items()}
РЕ_ССЫЛКА = re.compile(r"(?<![\w.])(cfg:)?(%s)(\w*)\.(\w+)" % РЕ_КЛАСС)


def переименовать_текст(т):
    if not т or "." not in т:
        return т

    def зам(м):
        кл, имя = м.group(2), м.group(4)
        нов = КАРТА_ИМЁН.get((кл, имя))
        if нов is None:
            return м.group(0)
        return (м.group(1) or "") + кл + м.group(3) + "." + нов
    return РЕ_ССЫЛКА.sub(зам, т)


def переименовать_дерево(корень):
    for эл in корень.iter():
        if not isinstance(эл.tag, str):
            continue
        if эл.text and эл.text.strip():
            эл.text = переименовать_текст(эл.text)
        for а, з in list(эл.attrib.items()):
            if а != "uuid":
                эл.set(а, переименовать_текст(з))


# ------------------------------------------------------------------------------ модель метаданных
class Модель:
    """Что определено в src_ext: объекты, их реквизиты, ТЧ, значения перечислений, предопределённые."""

    def __init__(self):
        self.объекты = {}      # (класс, имя) -> dict
        self.подсистемы = set()  # 'A', 'A.Subsystem.B'
        self.конфигурация = None
        self.методы = {}       # имя общего модуля -> set(экспортные методы)

    def добавить_дерево(self, корень, предопределённые=None, модуль_текст=None):
        эл = mdo(корень)
        кл, имя = лок(эл.tag), имя_объекта(эл)
        инфо = {"attrs": set(), "dims": set(), "res": set(), "ts": {}, "enum": set(), "cols": set(),
                "forms": set(), "cmds": set(), "tmpl": set(), "predef": set(предопределённые or []),
                "adopted": (эл.findtext(MD + "Properties/" + MD + "ObjectBelonging") == "Adopted")}
        дети = эл.find(MD + "ChildObjects")
        if дети is not None:
            for д in дети:
                т = лок(д.tag)
                if т in ("Form", "Template") and (д.text or "").strip():
                    инфо["forms" if т == "Form" else "tmpl"].add(д.text.strip())
                    continue
                дн = имя_объекта(д)
                if т == "Attribute":
                    инфо["attrs"].add(дн)
                elif т == "Dimension":
                    инфо["dims"].add(дн)
                elif т == "Resource":
                    инфо["res"].add(дн)
                elif т == "EnumValue":
                    инфо["enum"].add(дн)
                elif т == "Column":
                    инфо["cols"].add(дн)
                elif т == "Command":
                    инфо["cmds"].add(дн)
                elif т == "TabularSection":
                    рек = set()
                    тд = д.find(MD + "ChildObjects")
                    if тд is not None:
                        for р in тд:
                            if лок(р.tag) == "Attribute":
                                рек.add(имя_объекта(р))
                    инфо["ts"][дн] = рек
        if кл == "Configuration":
            self.конфигурация = имя
        else:
            self.объекты[(кл, имя)] = инфо
        if кл == "CommonModule":
            self.методы[имя] = set(re.findall(r"(?im)^\s*(?:Процедура|Функция|Procedure|Function)\s+(\w+)\s*\([^)]*\)\s*(?:Экспорт|Export)",
                                              модуль_текст or ""))
        return кл, имя

    def есть_объект(self, кл, имя):
        return (кл, имя) in self.объекты

    def разрешить(self, путь):
        """Путь вида Catalog.X[.Attribute.Y] / cfg:CatalogRef.X / CatalogObject.X / TabularSection-типы."""
        м = re.match(r"^(cfg:)?(%s)(\w*)\.(.+)$" % РЕ_КЛАСС, путь)
        if not м:
            return True  # не ссылка на метаданные
        кл, суф, хвост = м.group(2), м.group(3), м.group(4).split(".")
        if кл == "Configuration":
            return хвост == [self.конфигурация]
        if кл == "Subsystem":
            return ".".join(хвост) in self.подсистемы and not суф
        имя = хвост[0]
        if not self.есть_объект(кл, имя):
            return False
        инфо = self.объекты[(кл, имя)]
        ост = хвост[1:]
        if суф:
            if суф in ("TabularSection", "TabularSectionRow"):
                return len(ост) == 1 and ост[0] in инфо["ts"]
            return not ост
        if not ост:
            return True
        if ост == ["EmptyRef"]:
            return True
        if len(ост) == 2 and ост[0] == "StandardAttribute":
            return True
        if инфо["adopted"]:
            return False  # у заимствованных реквизиты не заимствуем
        if len(ост) == 2:
            вид, н = ост
            return н in {"Attribute": инфо["attrs"], "Dimension": инфо["dims"], "Resource": инфо["res"],
                         "EnumValue": инфо["enum"], "Column": инфо["cols"], "Form": инфо["forms"],
                         "Command": инфо["cmds"], "Template": инфо["tmpl"], "TabularSection": set(инфо["ts"])
                         }.get(вид, set())
        if len(ост) == 4 and ост[0] == "TabularSection" and ост[1] in инфо["ts"]:
            if ост[2] == "StandardAttribute":
                return True
            return ост[2] == "Attribute" and ост[3] in инфо["ts"][ост[1]]
        if len(ост) == 1:
            if кл == "CommonModule":
                return ост[0] in self.методы.get(имя, set())
            return ост[0] in инфо["predef"]
        return False


def читать_предопределённые(путь):
    if not os.path.exists(путь):
        return []
    к = читать_дерево(путь)
    return [э.text for э in к.iter("{%s}Name" % NS["pd"])]


def модель_каталога(каталог):
    """Модель по готовому дереву src_ext (для проверок)."""
    м = Модель()
    for кл, папка in ПОРЯДОК:
        п = os.path.join(каталог, папка)
        if not os.path.isdir(п):
            continue
        for ф in sorted(os.listdir(п)):
            if not ф.endswith(".xml"):
                continue
            имя = ф[:-4]
            try:
                к = читать_дерево(os.path.join(п, ф))
            except Exception:
                continue
            пред = читать_предопределённые(os.path.join(п, имя, "Ext", "Predefined.xml"))
            мод = ""
            пм = os.path.join(п, имя, "Ext", "Module.bsl")
            if os.path.exists(пм):
                мод = io.open(пм, encoding="utf-8-sig").read()
            м.добавить_дерево(к, пред, мод)
    пк = os.path.join(каталог, "Configuration.xml")
    if os.path.exists(пк):
        try:
            м.добавить_дерево(читать_дерево(пк))
        except Exception:
            pass
    # подсистемы (вложенные)
    def обход(папка, префикс):
        if not os.path.isdir(папка):
            return
        for ф in sorted(os.listdir(папка)):
            if ф.endswith(".xml"):
                имя = ф[:-4]
                полное = префикс + имя
                м.подсистемы.add(полное)
                обход(os.path.join(папка, имя, "Subsystems"), полное + ".Subsystem.")
    обход(os.path.join(каталог, "Subsystems"), "")
    return м


# ------------------------------------------------------------------------------- перенос объекта
def новые_uuid(корень, полное_имя):
    """Все uuid/TypeId/ValueId объекта — детерминированно от имён."""
    def путь(эл):
        части = []
        while эл is not None:
            if isinstance(эл.tag, str) and эл.get("uuid") is not None:
                части.append("%s:%s" % (лок(эл.tag), имя_объекта(эл)))
            эл = эл.getparent()
        return "/".join(reversed(части))
    for эл in корень.iter():
        if not isinstance(эл.tag, str):
            continue
        if эл.get("uuid") is not None:
            эл.set("uuid", ууид("UZ|" + путь(эл)))
        if лок(эл.tag) == "GeneratedType":
            ключ = "GT|%s|%s" % (эл.get("name"), эл.get("category"))
            for д in эл:
                if лок(д.tag) in ("TypeId", "ValueId"):
                    д.text = ууид(ключ + "|" + лок(д.tag))


def почистить_синонимы(корень):
    for эл in корень.iter(V8 + "content"):
        if эл.text and "LM" in эл.text:
            эл.text = re.sub(r"\s*\(LM\)", "", эл.text)


def убрать_формы_команды(эл_объекта, полное):
    дети = эл_объекта.find(MD + "ChildObjects")
    if дети is not None and not ПЕРЕНОСИТЬ_ФОРМЫ:
        for д in list(дети):
            т = лок(д.tag)
            if т in ("Form", "Template", "Command"):
                ЖУРНАЛ[{"Form": "формы", "Template": "макеты", "Command": "команды"}[т]] += 1
                удалить(д)
    if not ПЕРЕНОСИТЬ_ФОРМЫ:
        for эл in эл_объекта.iter():
            if isinstance(эл.tag, str) and эл.text and re.match(r"^\w+\.[^.\s]+\.Form\.\w+$|^CommonForm\.", эл.text.strip()):
                эл.text = None
                ЖУРНАЛ["очищено_ссылок_на_формы"] += 1


def задать_синоним(эл_объекта, синонимы):
    синоним, объект, список = синонимы
    св = эл_объекта.find(MD + "Properties")
    for тег, текст in (("Synonym", синоним), ("ObjectPresentation", объект), ("ListPresentation", список)):
        э = св.find(MD + тег)
        if э is None or текст is None:
            continue
        for с in э.iter(V8 + "content"):
            с.text = текст


def найти_реквизит(эл_объекта, имя, виды=("Attribute",)):
    for э in эл_объекта.iter():
        if isinstance(э.tag, str) and лок(э.tag) in виды and э.get("uuid") and имя_объекта(э) == имя:
            return э
    return None


# ---- точечные правки (ключ — новое имя объекта) -------------------------------------------------
def правка_урок(эл, полное):
    р = найти_реквизит(эл, "КоличествоЧасов")
    if р is None:
        ЖУРНАЛ["правки"].append("!! %s.КоличествоЧасов не найден" % полное)
        return
    св = р.find(MD + "Properties")
    тип = св.find(MD + "Type")
    for д in list(тип):
        тип.remove(д)
    тип.text = "\n" + "\t" * 6
    т = etree.SubElement(тип, V8 + "Type")
    т.text = "xs:decimal"
    т.tail = "\n" + "\t" * 6
    к = etree.SubElement(тип, V8 + "NumberQualifiers")
    к.text = "\n" + "\t" * 7
    for i, (тег, знач) in enumerate((("Digits", "10"), ("FractionDigits", "2"), ("AllowedSign", "Nonnegative"))):
        з = etree.SubElement(к, V8 + тег)
        з.text = знач
        з.tail = "\n" + "\t" * (7 if i < 2 else 6)
    к.tail = "\n" + "\t" * 5
    for тег in ("Format", "EditFormat"):
        ф = св.find(MD + тег)
        if ф is not None:
            for д in list(ф):
                ф.remove(д)
            ф.text = None
    ЖУРНАЛ["правки"].append("%s.КоличествоЧасов: тип Дата(время, ДФ=H:mm) -> Число(10,2) неотрицательное" % полное)


def правка_расчеты_по_зарплате(эл, полное):
    изм = найти_реквизит(эл, "Комментарий", ("Dimension",))
    if изм is None:
        ЖУРНАЛ["правки"].append("!! %s: измерение Комментарий не найдено" % полное)
        return
    рек = copy.deepcopy(изм)
    рек.tag = MD + "Attribute"
    св = рек.find(MD + "Properties")
    for тег in ("DenyIncompleteValues", "UseInTotals"):
        э = св.find(MD + тег)
        if э is not None:
            удалить(э)
    дети = изм.getparent()
    первое_изм = next(д for д in дети if лок(д.tag) == "Dimension")
    пред = первое_изм.getprevious()
    отступ = пред.tail if пред is not None else дети.text
    первое_изм.addprevious(рек)
    рек.tail = отступ
    удалить(изм)
    ЖУРНАЛ["правки"].append("%s: измерение Комментарий (Строка 255) -> реквизит регистра" % полное)


def правка_расчет_зарплаты(эл, полное):
    р = найти_реквизит(эл, "Пермещение")
    if р is None:
        ЖУРНАЛ["правки"].append("!! %s.Пермещение не найден" % полное)
        return
    for э in р.find(MD + "Properties").iter():
        if isinstance(э.tag, str) and э.text == "Пермещение":
            э.text = "Перемещение"
    ЖУРНАЛ["правки"].append("%s: реквизит Пермещение -> Перемещение (имя и синоним)" % полное)


def правка_регламентное(эл, полное):
    св = эл.find(MD + "Properties")
    св.find(MD + "MethodName").text = "CommonModule.%s.ПроверкаЗадолженности" % МОДУЛЬ_СЕРВЕР
    св.find(MD + "Description").text = "Проверка задолженности"
    св.find(MD + "Use").text = "false"
    ЖУРНАЛ["правки"].append("%s: метод -> CommonModule.%s.ПроверкаЗадолженности (заглушка), Использование=Ложь"
                            % (полное, МОДУЛЬ_СЕРВЕР))


ПРАВКИ = {
    "Document.УЗ_Урок": правка_урок,
    "AccumulationRegister.УЗ_РасчетыПоЗарплате": правка_расчеты_по_зарплате,
    "Document.УЗ_РасчетЗарплаты": правка_расчет_зарплаты,
    "ScheduledJob.УЗ_ПроверкаЗадолженности": правка_регламентное,
}
# Текстовые замены путей после точечных правок (ссылки на переименованные/перенесённые реквизиты)
ЗАМЕНЫ_ПУТЕЙ = [
    ("Document.УЗ_РасчетЗарплаты.Attribute.Пермещение", "Document.УЗ_РасчетЗарплаты.Attribute.Перемещение"),
    ("AccumulationRegister.УЗ_РасчетыПоЗарплате.Dimension.Комментарий",
     "AccumulationRegister.УЗ_РасчетыПоЗарплате.Attribute.Комментарий"),
]
ЗАМЕНЫ_ПУТЕЙ_БАЗА = list(ЗАМЕНЫ_ПУТЕЙ)
ЗАМЕТКИ = [
    "InformationRegister.УЗ_Настройки: фиктивное измерение Реквизит1 оставлено как есть (переделка — отдельно)",
]


def перенести_объект(кл, старое):
    """Прочитать объект LM, переименовать, убрать формы/команды, точечные правки. Возвращает запись."""
    новое, синонимы, _ = ПЕРЕИМЕНОВАНИЯ[(кл, старое)]
    папка = ПАПКА[кл]
    корень = читать_дерево(os.path.join(ИСТОЧНИК, папка, старое + ".xml"))
    эл = mdo(корень)
    полное = "%s.%s" % (кл, новое)
    переименовать_дерево(корень)
    эл.find(MD + "Properties/" + MD + "Name").text = новое
    почистить_синонимы(корень)
    if синонимы:
        задать_синоним(эл, синонимы)
    убрать_формы_команды(эл, полное)
    if полное in ПРАВКИ:
        ПРАВКИ[полное](эл, полное)
    # предопределённые
    пред = None
    пп = os.path.join(ИСТОЧНИК, папка, старое, "Ext", "Predefined.xml")
    if os.path.exists(пп):
        пред = читать_дерево(пп)
        for э in пред.iter("{%s}Item" % NS["pd"]):
            э.set("id", ууид("PRED|%s|%s" % (полное, э.findtext("{%s}Name" % NS["pd"]))))
    # расписание регламентного
    расп = None
    пр = os.path.join(ИСТОЧНИК, папка, старое, "Ext", "Schedule.xml")
    if os.path.exists(пр):
        расп = io.open(пр, encoding="utf-8-sig").read()
    return {"кл": кл, "имя": новое, "полное": полное, "корень": корень, "пред": пред, "расп": расп}


def снять_префикс_lm_у_реквизитов(запись):
    """Реквизиты с именем LM_X (у ПКО/РКО: LM_ФизЛицо) -> X; пути на них правятся через ЗАМЕНЫ_ПУТЕЙ."""
    эл = mdo(запись["корень"])
    for р in эл.iter():
        if not isinstance(р.tag, str) or р is эл or р.get("uuid") is None:
            continue
        имя = имя_объекта(р)
        if not имя or not имя.startswith("LM_"):
            continue
        новое = имя[3:]
        соседи = {имя_объекта(с) for с in р.getparent() if isinstance(с.tag, str) and с is not р}
        if новое in соседи:
            ЖУРНАЛ["правки"].append("!! %s.%s: имя %s занято, не переименован" % (запись["полное"], имя, новое))
            continue
        # в своём объекте — все вхождения имени словом (Name, DataPath, пути)
        ре = re.compile(r"(?<![\w])%s(?![\w])" % re.escape(имя))
        for э in запись["корень"].iter():
            if isinstance(э.tag, str) and э.text and имя in э.text:
                э.text = ре.sub(новое, э.text)
        ЗАМЕНЫ_ПУТЕЙ.append(("%s.%s.%s" % (запись["полное"], лок(р.tag), имя),
                             "%s.%s.%s" % (запись["полное"], лок(р.tag), новое)))
        ЖУРНАЛ["правки"].append("%s: %s %s -> %s" % (запись["полное"], лок(р.tag), имя, новое))


def текст_путей(корень):
    for эл in корень.iter():
        if isinstance(эл.tag, str) and эл.text:
            for с, н in ЗАМЕНЫ_ПУТЕЙ:
                if с in эл.text:
                    эл.text = re.sub(r"%s(?![\w])" % re.escape(с), н, эл.text)


def почистить_типы(запись, есть):
    """Удалить из составных типов ссылки на объекты, которых нет в расширении; пустой тип -> удалить реквизит."""
    корень = запись["корень"]
    for т in list(корень.iter(V8 + "Type", V8 + "TypeSet")):
        знач = (т.text or "").strip()
        м = re.match(r"^cfg:(%s)(\w*)\.(\w+)$" % РЕ_КЛАСС, знач)
        if not м or есть(м.group(1), м.group(3)):
            continue
        контейнер = т.getparent()
        владелец = контейнер
        while владелец is not None and владелец.get("uuid") is None:
            владелец = владелец.getparent()
        имя_вл = "%s.%s" % (запись["полное"], имя_объекта(владелец)) if владелец is not None else запись["полное"]
        удалить(т)
        ЖУРНАЛ["удалено_типов"].append("%s: из типа убран %s" % (имя_вл, знач))
        if not [д for д in контейнер if лок(д.tag) in ("Type", "TypeSet")]:
            if владелец is not None and владелец is not mdo(корень):
                удалить(владелец)
                ЖУРНАЛ["удалено_реквизитов"].append("%s (тип стал пустым)" % имя_вл)


def почистить_ссылки(запись, модель):
    """xr:Item/xr:Field/DesignTimeRef на то, чего нет (удалённые реквизиты, объекты БСП) — убрать."""
    корень = запись["корень"]
    for эл in list(корень.iter()):
        if not isinstance(эл.tag, str) or эл.getparent() is None:
            continue
        т = (эл.text or "").strip()
        if not т or len(эл):
            continue
        тип = эл.get(XSI + "type") or ""
        if лок(эл.tag) in ("Item", "Field") or тип == "xr:DesignTimeRef":
            if модель.разрешить(т) and not re.match(r"^[0-9a-f-]{36}\.[0-9a-f-]{36}$", т):
                continue
            if лок(эл.tag) == "FillValue":
                эл.text = None
                for а in list(эл.attrib):
                    del эл.attrib[а]
                эл.set(XSI + "nil", "true")
            else:
                удалить(эл)
            ЖУРНАЛ["удалено_ссылок"].append("%s: убрана ссылка %s" % (запись["полное"], т))


# ------------------------------------------------------------------------- генерация новых файлов
def файл_заимствованного(кл, имя):
    приставки = {"Catalog": ["Object", "Ref", "Selection", "List", "Manager"]}[кл]
    категории = {"Object": "Object", "Ref": "Ref", "Selection": "Selection", "List": "List", "Manager": "Manager"}
    гт = ""
    for п in приставки:
        н = "%s%s.%s" % (кл, п, имя)
        ключ = "GT|%s|%s" % (н, категории[п])
        гт += ('\t\t\t<xr:GeneratedType name="%s" category="%s">\n\t\t\t\t<xr:TypeId>%s</xr:TypeId>\n'
               '\t\t\t\t<xr:ValueId>%s</xr:ValueId>\n\t\t\t</xr:GeneratedType>\n'
               % (н, категории[п], ууид(ключ + "|TypeId"), ууид(ключ + "|ValueId")))
    return (ДЕКЛ + ШАПКА_MD + '\n\t<%s uuid="%s">\n\t\t<InternalInfo>\n%s\t\t</InternalInfo>\n\t\t<Properties>\n'
            '\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>\n\t\t\t<Name>%s</Name>\n\t\t\t<Comment/>\n'
            '\t\t</Properties>\n\t\t<ChildObjects/>\n\t</%s>\n</MetaDataObject>'
            % (кл, ууид("ADOPTED|%s.%s" % (кл, имя)), гт, имя, кл))


def файл_языка():
    return (ДЕКЛ + ШАПКА_MD + '\n\t<Language uuid="%s">\n\t\t<InternalInfo/>\n\t\t<Properties>\n'
            '\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>\n\t\t\t<Name>Русский</Name>\n\t\t\t<Comment/>\n'
            '\t\t\t<LanguageCode>ru</LanguageCode>\n\t\t</Properties>\n\t</Language>\n</MetaDataObject>'
            % ууид("ADOPTED|Language.Русский"))


def файл_модуля_сервер():
    xml = (ДЕКЛ + ШАПКА_MD + '\n\t<CommonModule uuid="%s">\n\t\t<Properties>\n\t\t\t<Name>%s</Name>\n%s\n'
           '\t\t\t<Comment/>\n\t\t\t<Global>false</Global>\n\t\t\t<ClientManagedApplication>false</ClientManagedApplication>\n'
           '\t\t\t<Server>true</Server>\n\t\t\t<ExternalConnection>false</ExternalConnection>\n'
           '\t\t\t<ClientOrdinaryApplication>false</ClientOrdinaryApplication>\n\t\t\t<Client>false</Client>\n'
           '\t\t\t<ServerCall>false</ServerCall>\n\t\t\t<Privileged>false</Privileged>\n'
           '\t\t\t<ReturnValuesReuse>DontUse</ReturnValuesReuse>\n\t\t</Properties>\n\t</CommonModule>\n</MetaDataObject>'
           % (ууид("UZ|CommonModule:" + МОДУЛЬ_СЕРВЕР), МОДУЛЬ_СЕРВЕР, синоним_xml("Учёт занятий: сервер", "\t\t\t")))
    бсл = ("// Заглушка. Код переносится на этапе 3 (docs/план_перевода_в_расширение.md).\n"
           "// Ручная версия модуля кладётся в src_manual\\CommonModules и заменяет эту целиком.\n\n"
           "// Метод регламентного задания УЗ_ПроверкаЗадолженности.\n"
           "Процедура ПроверкаЗадолженности() Экспорт\n\t\nКонецПроцедуры\n")
    return xml, бсл


def файл_подсистемы(имя, синоним, в_интерфейсе, состав, дети):
    сост = "".join('\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">%s</xr:Item>\n' % с for с in состав)
    сост_xml = ("\t\t\t<Content>\n%s\t\t\t</Content>" % сост) if состав else "\t\t\t<Content/>"
    дети_xml = ("\t\t<ChildObjects>\n%s\t\t</ChildObjects>" % "".join("\t\t\t<Subsystem>%s</Subsystem>\n" % д for д in дети)
                if дети else "\t\t<ChildObjects/>")
    return (ДЕКЛ + ШАПКА_MD + '\n\t<Subsystem uuid="%s">\n\t\t<Properties>\n\t\t\t<Name>%s</Name>\n%s\n'
            '\t\t\t<Comment/>\n\t\t\t<IncludeHelpInContents>true</IncludeHelpInContents>\n'
            '\t\t\t<IncludeInCommandInterface>%s</IncludeInCommandInterface>\n\t\t\t<UseOneCommand>false</UseOneCommand>\n'
            '\t\t\t<Explanation/>\n\t\t\t<Picture/>\n%s\n\t\t</Properties>\n%s\n\t</Subsystem>\n</MetaDataObject>'
            % (ууид("UZ|Subsystem:" + имя), имя, синоним_xml(синоним, "\t\t\t"), "true" if в_интерфейсе else "false",
               сост_xml, дети_xml))


ПРАВА = {
    "Catalog": (["Read", "Insert", "Update", "Delete", "View", "InteractiveInsert", "Edit",
                 "InteractiveSetDeletionMark", "InteractiveClearDeletionMark", "InputByString"],
                ["InteractiveDelete", "InteractiveDeleteMarked", "InteractiveDeletePredefinedData"]),
    "Document": (["Read", "Insert", "Update", "Delete", "Posting", "UndoPosting", "View", "InteractiveInsert", "Edit",
                  "InteractiveSetDeletionMark", "InteractiveClearDeletionMark", "InteractivePosting",
                  "InteractivePostingRegular", "InteractiveUndoPosting", "InteractiveChangeOfPosted", "InputByString"],
                 ["InteractiveDelete", "InteractiveDeleteMarked"]),
    "InformationRegister": (["Read", "Update", "View", "Edit", "TotalsControl"], []),
    "AccumulationRegister": (["Read", "Update", "View", "Edit", "TotalsControl"], []),
    "DocumentJournal": (["Read", "View"], []),
    "Report": (["Use", "View"], []),
    "DataProcessor": (["Use", "View"], []),
    "CommonForm": (["View"], []),
    "CommonCommand": (["View"], []),
    "Constant": (["Read", "Update", "View", "Edit"], []),
}


def файлы_роли(объекты, подсистемы):
    xml = (ДЕКЛ + ШАПКА_MD + '\n\t<Role uuid="%s">\n\t\t<Properties>\n\t\t\t<Name>%s</Name>\n%s\n\t\t\t<Comment/>\n'
           '\t\t</Properties>\n\t</Role>\n</MetaDataObject>'
           % (ууид("UZ|Role:" + РОЛЬ), РОЛЬ, синоним_xml("Учёт занятий: основная роль", "\t\t\t")))

    def объект(имя, да, нет=()):
        т = "\t<object>\n\t\t<name>%s</name>\n" % имя
        for п in да:
            т += "\t\t<right>\n\t\t\t<name>%s</name>\n\t\t\t<value>true</value>\n\t\t</right>\n" % п
        for п in нет:
            т += "\t\t<right>\n\t\t\t<name>%s</name>\n\t\t\t<value>false</value>\n\t\t</right>\n" % п
        return т + "\t</object>\n"
    тело = объект("Configuration." + ИМЯ_РАСШИРЕНИЯ,
                  ["MainWindowModeNormal", "MainWindowModeWorkplace", "MainWindowModeEmbeddedWorkplace",
                   "MainWindowModeFullscreenWorkplace", "MainWindowModeKiosk"])
    for п in подсистемы:
        тело += объект("Subsystem." + п, ["View"])
    for кл, имя, заимств in объекты:
        if заимств or кл not in ПРАВА:
            continue
        да, нет = ПРАВА[кл]
        тело += объект("%s.%s" % (кл, имя), да, нет)
    права = ('<?xml version="1.0" encoding="UTF-8"?>\n<Rights xmlns="http://v8.1c.ru/8.2/roles" '
             'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xsi:type="Rights" version="%s">\n\t<setForNewObjects>false</setForNewObjects>\n'
             '\t<setForAttributesByDefault>true</setForAttributesByDefault>\n'
             '\t<independentRightsOfChildObjects>false</independentRightsOfChildObjects>\n%s</Rights>'
             % (ВЕРСИЯ_ФОРМАТА_НОВЫХ, тело))
    return xml, права


CLASS_IDS = ["9cd510cd-abfc-11d4-9434-004095e12fc7", "9fcd25a0-4822-11d4-9414-008048da11f9",
             "e3687481-0a87-462c-a166-9f34594f9bba", "9de14907-ec23-4a07-96f0-85521cb6b53b",
             "51f2d5d8-ea4d-4064-8892-82951750031e", "e68182ea-4237-4383-967f-90c1e3370bc7",
             "fb282519-d103-4dd3-bc12-cb271d631dfc"]


def файл_конфигурации(объекты):
    вн = "".join("\t\t\t<xr:ContainedObject>\n\t\t\t\t<xr:ClassId>%s</xr:ClassId>\n\t\t\t\t<xr:ObjectId>%s</xr:ObjectId>\n"
                 "\t\t\t</xr:ContainedObject>\n" % (к, ууид("CFG|" + к)) for к in CLASS_IDS)
    порядок = {к: i for i, (к, _) in enumerate(ПОРЯДОК)}
    дети = "".join("\t\t\t<%s>%s</%s>\n" % (кл, имя, кл)
                   for кл, имя, _ in sorted(объекты, key=lambda о: (порядок[о[0]], о[1])))
    return (ДЕКЛ + ШАПКА_MD + '\n\t<Configuration uuid="%s">\n\t\t<InternalInfo>\n%s\t\t</InternalInfo>\n'
            '\t\t<Properties>\n\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>\n\t\t\t<Name>%s</Name>\n%s\n'
            '\t\t\t<Comment/>\n\t\t\t<ConfigurationExtensionPurpose>AddOn</ConfigurationExtensionPurpose>\n'
            '\t\t\t<KeepMappingToExtendedConfigurationObjectsByIDs>true</KeepMappingToExtendedConfigurationObjectsByIDs>\n'
            '\t\t\t<NamePrefix>%s</NamePrefix>\n'
            '\t\t\t<ConfigurationExtensionCompatibilityMode>Version8_3_24</ConfigurationExtensionCompatibilityMode>\n'
            '\t\t\t<ScriptVariant>Russian</ScriptVariant>\n\t\t\t<DefaultRoles>\n'
            '\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Role.%s</xr:Item>\n\t\t\t</DefaultRoles>\n'
            '\t\t\t<Vendor/>\n\t\t\t<Version>%s</Version>\n\t\t\t<DefaultReportForm/>\n'
            '\t\t\t<DefaultReportVariantForm/>\n\t\t\t<DefaultReportSettingsForm/>\n\t\t\t<BriefInformation/>\n'
            '\t\t\t<DetailedInformation/>\n\t\t\t<Copyright/>\n\t\t\t<VendorInformationAddress/>\n'
            '\t\t\t<ConfigurationInformationAddress/>\n\t\t</Properties>\n\t\t<ChildObjects>\n%s\t\t</ChildObjects>\n'
            '\t</Configuration>\n</MetaDataObject>'
            % (ууид("CFG|Configuration." + ИМЯ_РАСШИРЕНИЯ), вн, ИМЯ_РАСШИРЕНИЯ,
               синоним_xml(СИНОНИМ_РАСШИРЕНИЯ, "\t\t\t"), ПРЕФИКС, РОЛЬ, ВЕРСИЯ_РАСШИРЕНИЯ, дети))


# ----------------------------------------------------------------------------------- src_manual
def объекты_каталога(каталог, только_верхние=True):
    """[(класс, имя, заимствован)] по файлам верхнего уровня <Папка>/<Имя>.xml."""
    итог = []
    for кл, папка in ПОРЯДОК:
        п = os.path.join(каталог, папка)
        if not os.path.isdir(п):
            continue
        for ф in sorted(os.listdir(п)):
            if ф.endswith(".xml"):
                заимств = False
                try:
                    заимств = mdo(читать_дерево(os.path.join(п, ф))).findtext(
                        MD + "Properties/" + MD + "ObjectBelonging") == "Adopted"
                except Exception:
                    pass
                итог.append((кл, ф[:-4], заимств))
    return итог


def наложить_ручные():
    if not os.path.isdir(РУЧНЫЕ):
        return []
    наложено = []
    for кл, имя, _ in объекты_каталога(РУЧНЫЕ):
        папка = ПАПКА[кл]
        for п in (os.path.join(ЦЕЛЬ, папка, имя + ".xml"), os.path.join(ЦЕЛЬ, папка, имя)):
            if os.path.isdir(п):
                shutil.rmtree(п)
            elif os.path.exists(п):
                os.remove(п)
        наложено.append("%s.%s" % (кл, имя))
    for корень, _, файлы in os.walk(РУЧНЫЕ):
        отн = os.path.relpath(корень, РУЧНЫЕ)
        for ф in файлы:
            if отн == "." and ф == "Configuration.xml":
                print("  ВНИМАНИЕ: src_manual\\Configuration.xml пропущен — Configuration.xml генерируется")
                continue
            if ф.endswith((".bak", ".orig")):
                continue
            ц = os.path.join(ЦЕЛЬ, отн, ф)
            os.makedirs(os.path.dirname(ц), exist_ok=True)
            shutil.copy2(os.path.join(корень, ф), ц)
    return наложено


# ----------------------------------------------------------------------------------------- сборка
def собрать():
    for к in ЖУРНАЛ:
        ЖУРНАЛ[к] = [] if isinstance(ЖУРНАЛ[к], list) else 0
    if os.path.exists(ЦЕЛЬ):
        shutil.rmtree(ЦЕЛЬ)
    os.makedirs(ЦЕЛЬ)

    записи = [перенести_объект(кл, ст) for (кл, ст) in ПЕРЕИМЕНОВАНИЯ]
    del ЗАМЕНЫ_ПУТЕЙ[len(ЗАМЕНЫ_ПУТЕЙ_БАЗА):]
    for з in записи:
        снять_префикс_lm_у_реквизитов(з)
    for з in записи:
        текст_путей(з["корень"])

    ручные = {(кл, имя) for кл, имя, _ in объекты_каталога(РУЧНЫЕ)} if os.path.isdir(РУЧНЫЕ) else set()
    есть_имена = ({(з["кл"], з["имя"]) for з in записи} | set(ЗАИМСТВОВАННЫЕ) | ручные
                  | {("CommonModule", МОДУЛЬ_СЕРВЕР), ("Role", РОЛЬ)})

    def есть(кл, имя):
        return (кл, имя) in есть_имена
    for з in записи:
        почистить_типы(з, есть)

    # модель для чистки ссылок на реквизиты/объекты
    модель = Модель()
    for з in записи:
        модель.добавить_дерево(з["корень"], [э.text for э in з["пред"].iter("{%s}Name" % NS["pd"])] if з["пред"] is not None else [])
    for кл, имя in ЗАИМСТВОВАННЫЕ:
        модель.объекты[(кл, имя)] = {"adopted": True, "attrs": set(), "dims": set(), "res": set(), "ts": {},
                                     "enum": set(), "cols": set(), "forms": set(), "cmds": set(), "tmpl": set(),
                                     "predef": set()}
    for кл, имя in ручные:
        модель.объекты.setdefault((кл, имя), {"adopted": False, "attrs": set(), "dims": set(), "res": set(),
                                              "ts": {}, "enum": set(), "cols": set(), "forms": set(),
                                              "cmds": set(), "tmpl": set(), "predef": set()})
    for з in записи:
        почистить_ссылки(з, модель)

    # запись перенесённых
    for з in записи:
        новые_uuid(з["корень"], з["полное"])
        папка = os.path.join(ЦЕЛЬ, ПАПКА[з["кл"]])
        писать_дерево(os.path.join(папка, з["имя"] + ".xml"), з["корень"], ВЕРСИЯ_ФОРМАТА_ПЕРЕНОСА)
        if з["пред"] is not None:
            писать_дерево(os.path.join(папка, з["имя"], "Ext", "Predefined.xml"), з["пред"])
        if з["расп"] is not None:
            писать(os.path.join(папка, з["имя"], "Ext", "Schedule.xml"), з["расп"].lstrip("\ufeff"))

    # новые файлы
    писать(os.path.join(ЦЕЛЬ, "Languages", "Русский.xml"), файл_языка())
    for кл, имя in ЗАИМСТВОВАННЫЕ:
        писать(os.path.join(ЦЕЛЬ, ПАПКА[кл], имя + ".xml"), файл_заимствованного(кл, имя))
    xml, бсл = файл_модуля_сервер()
    писать(os.path.join(ЦЕЛЬ, "CommonModules", МОДУЛЬ_СЕРВЕР + ".xml"), xml)
    писать(os.path.join(ЦЕЛЬ, "CommonModules", МОДУЛЬ_СЕРВЕР, "Ext", "Module.bsl"), бсл)

    корень_п, син_п = ПОДСИСТЕМА_КОРЕНЬ
    писать(os.path.join(ЦЕЛЬ, "Subsystems", корень_п + ".xml"),
           файл_подсистемы(корень_п, син_п, True, [], [п for п, _, _ in ПОДСИСТЕМЫ]))
    for п, син, видна in ПОДСИСТЕМЫ:
        состав = sorted("%s.%s" % (кл, н) for (кл, _), (н, _, пп) in ПЕРЕИМЕНОВАНИЯ.items() if пп == п)
        писать(os.path.join(ЦЕЛЬ, "Subsystems", корень_п, "Subsystems", п + ".xml"),
               файл_подсистемы(п, син, видна, состав, []))

    наложено = наложить_ручные()

    объекты = объекты_каталога(ЦЕЛЬ)
    if ("Role", РОЛЬ) not in {(к, и) for к, и, _ in объекты}:
        подс = [корень_п] + ["%s.Subsystem.%s" % (корень_п, п) for п, _, _ in ПОДСИСТЕМЫ]
        xml, права = файлы_роли(объекты, подс)
        писать(os.path.join(ЦЕЛЬ, "Roles", РОЛЬ + ".xml"), xml)
        писать(os.path.join(ЦЕЛЬ, "Roles", РОЛЬ, "Ext", "Rights.xml"), права)
        объекты = объекты_каталога(ЦЕЛЬ)
    писать(os.path.join(ЦЕЛЬ, "Configuration.xml"), файл_конфигурации(объекты))
    return объекты, наложено


# --------------------------------------------------------------------------------------- проверки
РЕ_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
РЕ_ПУТЬ = re.compile(r"^(cfg:)?(%s)(\w*)\.\S+$" % РЕ_КЛАСС)


def проверить(каталог, тихо=False):
    ошибки = []

    def ош(т):
        ошибки.append(т)

    # 1. XML корректен
    деревья = {}
    for корень, _, файлы in os.walk(каталог):
        for ф in файлы:
            п = os.path.join(корень, ф)
            отн = os.path.relpath(п, каталог)
            if "LM_" in отн:
                ош("имя файла содержит LM_: %s" % отн)
            if ф.endswith(".xml"):
                try:
                    деревья[отн] = читать_дерево(п)
                except Exception as e:
                    ош("XML не разбирается: %s: %s" % (отн, e))
            if ф.endswith((".xml", ".bsl")):
                if "LM_" in io.open(п, encoding="utf-8-sig", errors="replace").read():
                    ош("подстрока LM_ в %s" % отн)
    модель = модель_каталога(каталог)

    # 2. uuid уникальны
    виденные = {}
    for отн, к in деревья.items():
        for эл in к.iter():
            if not isinstance(эл.tag, str):
                continue
            кандидаты = []
            if эл.get("uuid") is not None:
                кандидаты.append(эл.get("uuid"))
            if лок(эл.tag) == "Item" and эл.get("id") and отн.endswith("Predefined.xml"):
                кандидаты.append(эл.get("id"))
            if лок(эл.tag) in ("TypeId", "ValueId", "ObjectId"):
                кандидаты.append((эл.text or "").strip())
            for у in кандидаты:
                if not РЕ_UUID.match(у):
                    ош("не uuid: %r в %s" % (у, отн))
                    continue
                у = у.lower()
                if у in виденные and виденные[у] != (отн, id(эл)):
                    ош("uuid %s повторяется: %s и %s" % (у, виденные[у][0], отн))
                виденные.setdefault(у, (отн, id(эл)))

    # 3. ссылки разрешаются
    for отн, к in деревья.items():
        for эл in к.iter():
            if not isinstance(эл.tag, str):
                continue
            значения = [(эл.text or "").strip()] + [з for а, з in эл.attrib.items() if а not in ("uuid", "version")]
            for з in значения:
                if not з or not РЕ_ПУТЬ.match(з):
                    continue
                if not модель.разрешить(з):
                    ош("битая ссылка %s в %s" % (з, отн))
            if эл.get(XSI + "type") == "xr:DesignTimeRef" and re.match(r"^[0-9a-f-]{36}\.", (эл.text or "").strip()):
                ош("ссылка по uuid (объекта нет) %s в %s" % (эл.text.strip(), отн))

    # 4. состав Configuration.xml = файлы; 5. имена с префиксом
    пк = деревья.get("Configuration.xml")
    if пк is None:
        ош("нет Configuration.xml")
    else:
        заявлено = {(лок(д.tag), д.text) for д in mdo(пк).find(MD + "ChildObjects") if isinstance(д.tag, str)}
        файлы = {(кл, имя) for кл, имя, _ in объекты_каталога(каталог)}
        for о in sorted(заявлено - файлы):
            ош("в Configuration.xml есть %s.%s, файла нет" % о)
        for о in sorted(файлы - заявлено):
            ош("файл %s.%s не зарегистрирован в Configuration.xml" % о)
        св = mdo(пк).find(MD + "Properties")
        for тег, надо in (("Name", ИМЯ_РАСШИРЕНИЯ), ("NamePrefix", ПРЕФИКС),
                          ("ConfigurationExtensionPurpose", "AddOn"),
                          ("ConfigurationExtensionCompatibilityMode", "Version8_3_24"),
                          ("KeepMappingToExtendedConfigurationObjectsByIDs", "true")):
            if св.findtext(MD + тег) != надо:
                ош("Configuration.xml: %s != %s" % (тег, надо))
    for (кл, имя), инфо in модель.объекты.items():
        if not инфо["adopted"] and not имя.startswith(ПРЕФИКС):
            ош("имя без префикса %s: %s.%s" % (ПРЕФИКС, кл, имя))
    for п in модель.подсистемы:
        if not п.split(".")[-1].startswith(ПРЕФИКС):
            ош("подсистема без префикса: %s" % п)
    # 6. регламентные: метод существует
    for (кл, имя), _ in модель.объекты.items():
        if кл == "ScheduledJob":
            к = деревья.get(os.path.join("ScheduledJobs", имя + ".xml"))
            м = к is not None and mdo(к).findtext(MD + "Properties/" + MD + "MethodName")
            if м and not модель.разрешить(м):
                ош("регламентное %s: метод %s не найден" % (имя, м))
    if not тихо:
        for о in ошибки[:60]:
            print("  ОШИБКА:", о)
        if len(ошибки) > 60:
            print("  ... ещё", len(ошибки) - 60)
    return ошибки


def самотест():
    """Мутации: каждая должна дать >0 ошибок. Иначе проверкам не доверять."""
    мутации = [
        ("битая ссылка типа", "Documents/УЗ_Урок.xml", "cfg:CatalogRef.УЗ_ФизЛица", "cfg:CatalogRef.УЗ_НетТакого", 1),
        ("битая ссылка на реквизит", "DocumentJournals/УЗ_ОбщийЖурнал.xml", ".Attribute.", ".Attribute.Нет", 1),
        ("повтор uuid", None, None, None, 0),
        ("подстрока LM_", "Catalogs/УЗ_Тарифы.xml", "<Comment/>", "<Comment>LM_</Comment>", 1),
        ("регистрация без файла", "Configuration.xml", "<Catalog>УЗ_Тарифы</Catalog>",
         "<Catalog>УЗ_Тарифы</Catalog>\n\t\t\t<Catalog>УЗ_Призрак</Catalog>", 1),
        ("имя без префикса", "Catalogs/УЗ_Помещения.xml", "<Name>УЗ_Помещения</Name>", "<Name>Помещения</Name>", 1),
    ]
    пойманы = 0
    for назв, файл, было, стало, n in мутации:
        with tempfile.TemporaryDirectory() as тд:
            копия = os.path.join(тд, "src_ext")
            shutil.copytree(ЦЕЛЬ, копия)
            if файл is None:  # повтор uuid: второй справочник получает uuid первого
                а = io.open(os.path.join(копия, "Catalogs", "УЗ_Тарифы.xml"), encoding="utf-8-sig").read()
                у = re.search(r'<Catalog uuid="([^"]+)"', а).group(1)
                п = os.path.join(копия, "Catalogs", "УЗ_Скидки.xml")
                б = io.open(п, encoding="utf-8-sig").read()
                б = re.sub(r'<Catalog uuid="[^"]+"', '<Catalog uuid="%s"' % у, б, count=1)
                писать(п, б)
            else:
                п = os.path.join(копия, файл)
                т = io.open(п, encoding="utf-8-sig").read()
                if было not in т:
                    print("  САМОТЕСТ: мутация «%s» не применилась (нет подстроки)" % назв)
                    continue
                писать(п, т.replace(было, стало, n))
            ош = проверить(копия, тихо=True)
            if ош:
                пойманы += 1
            else:
                print("  САМОТЕСТ: мутация «%s» НЕ ПОЙМАНА" % назв)
    print("САМОТЕСТ проверок: поймано %d из %d мутаций" % (пойманы, len(мутации)))
    return пойманы == len(мутации)


def сверить_хозяев():
    """Справка: заимствуемые объекты есть у каждого хозяина (по имени), uuid у хозяев разные."""
    print("Заимствованные объекты у хозяев (сопоставление по имени, uuid хозяев не пишем):")
    for кл, имя in ЗАИМСТВОВАННЫЕ:
        строки = []
        for х, путь in ХОЗЯЕВА.items():
            ф = os.path.join(путь, ПАПКА[кл], имя + ".xml")
            if not os.path.isdir(путь):
                строки.append("%s: выгрузки нет" % х)
            elif not os.path.exists(ф):
                строки.append("%s: НЕТ ОБЪЕКТА" % х)
            else:
                с = io.open(ф, encoding="utf-8-sig").read(3000)
                м = re.search(r'uuid="([^"]+)"', с)
                строки.append("%s: %s" % (х, м.group(1)[:8] if м else "?"))
        print("  %s.%s — %s" % (кл, имя, "; ".join(строки)))


def main():
    только_проверка = "--проверка" in sys.argv
    if not только_проверка:
        объекты, наложено = собрать()
        print("Собрано: %s (%d объектов верхнего уровня)" % (ЦЕЛЬ, len(объекты)))
        if наложено:
            print("Наложено из src_manual:", ", ".join(наложено))
        print("Убрано из объектов (этап 3): форм %d, макетов %d, команд %d; очищено ссылок на формы %d"
              % (ЖУРНАЛ["формы"], ЖУРНАЛ["макеты"], ЖУРНАЛ["команды"], ЖУРНАЛ["очищено_ссылок_на_формы"]))
        for з in ЖУРНАЛ["правки"]:
            print("  ПРАВКА:", з)
        for з in ЗАМЕТКИ:
            print("  ЗАМЕТКА:", з)
        for з in ЖУРНАЛ["удалено_типов"]:
            print("  ТИП:", з)
        for з in ЖУРНАЛ["удалено_реквизитов"]:
            print("  УДАЛЁН РЕКВИЗИТ:", з)
        for з in ЖУРНАЛ["удалено_ссылок"]:
            print("  УДАЛЕНА ССЫЛКА:", з)
        print("Итого: убрано типов %d, удалено реквизитов %d, убрано ссылок %d"
              % (len(ЖУРНАЛ["удалено_типов"]), len(ЖУРНАЛ["удалено_реквизитов"]), len(ЖУРНАЛ["удалено_ссылок"])))
        сверить_хозяев()
    ошибки = проверить(ЦЕЛЬ)
    print("ИТОГО ошибок: %d" % len(ошибки))
    ок_самотест = самотест()
    sys.exit(0 if not ошибки and ок_самотест else 1)


if __name__ == "__main__":
    main()
