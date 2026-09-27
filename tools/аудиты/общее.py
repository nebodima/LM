# -*- coding: utf-8 -*-
"""Общая часть офлайн-аудитов исходников расширения УЗ_ext.

Здесь то, что нужно всем аудитам:

* обход исходников (XML-выгрузка конфигурации/расширения, иерархический формат)
  с фильтром «только продукт» — для прогона «как если бы» по выгрузке LM;
* разметка модуля BSL: строковые литералы и комментарии отделяются от кода,
  чтобы правила про код не срабатывали на тексты сообщений и закомментированное;
* разбор метаданных объекта (реквизиты, ТЧ, измерения, ресурсы, значения
  перечисления) — для проверки ссылок и полей в запросах;
* единый формат замечания и запуск одного аудита из командной строки.

Аудит — модуль с функцией `проверить(исх) -> Результат`, где `исх` — Исходники.
"""
import argparse
import bisect
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

ПАПКА_АУДИТОВ = os.path.dirname(os.path.abspath(__file__))
КОРЕНЬ_РЕПО = os.path.abspath(os.path.join(ПАПКА_АУДИТОВ, "..", ".."))
КАТАЛОГ_ПО_УМОЛЧАНИЮ = os.path.join(КОРЕНЬ_РЕПО, "src_ext")
ПРЕФИКС = "УЗ_"
СЛОЙ_СОВМЕСТИМОСТИ = "УЗ_Среда"      # единственный модуль, где живут вызовы хозяина строкой

# Папка выгрузки -> тип метаданных (как в ссылках XML «Catalog.Имя»)
ВИДЫ = {
    "Catalogs": "Catalog", "Documents": "Document", "Enums": "Enum",
    "InformationRegisters": "InformationRegister", "AccumulationRegisters": "AccumulationRegister",
    "AccountingRegisters": "AccountingRegister", "CalculationRegisters": "CalculationRegister",
    "Reports": "Report", "DataProcessors": "DataProcessor", "DocumentJournals": "DocumentJournal",
    "Constants": "Constant", "ChartsOfCharacteristicTypes": "ChartOfCharacteristicTypes",
    "ChartsOfAccounts": "ChartOfAccounts", "ChartsOfCalculationTypes": "ChartOfCalculationTypes",
    "ExchangePlans": "ExchangePlan", "BusinessProcesses": "BusinessProcess", "Tasks": "Task",
    "CommonModules": "CommonModule", "CommonForms": "CommonForm", "CommonCommands": "CommonCommand",
    "CommonPictures": "CommonPicture", "CommonTemplates": "CommonTemplate",
    "CommonAttributes": "CommonAttribute", "CommandGroups": "CommandGroup",
    "StyleItems": "StyleItem", "Styles": "Style", "DefinedTypes": "DefinedType",
    "SessionParameters": "SessionParameter", "FunctionalOptions": "FunctionalOption",
    "FunctionalOptionsParameters": "FunctionalOptionsParameter", "Roles": "Role",
    "Subsystems": "Subsystem", "EventSubscriptions": "EventSubscription",
    "ScheduledJobs": "ScheduledJob", "FilterCriteria": "FilterCriterion",
    "SettingsStorages": "SettingsStorage", "WebServices": "WebService",
    "HTTPServices": "HTTPService", "XDTOPackages": "XDTOPackage", "Languages": "Language",
    "Sequences": "Sequence", "DocumentNumerators": "DocumentNumerator",
}
ПАПКА_ВИДА = {т: п for п, т in ВИДЫ.items()}

# Коллекции менеджеров в коде BSL -> тип метаданных
КОЛЛЕКЦИИ_КОДА = {
    "Справочники": "Catalog", "Документы": "Document", "Перечисления": "Enum",
    "РегистрыСведений": "InformationRegister", "РегистрыНакопления": "AccumulationRegister",
    "РегистрыБухгалтерии": "AccountingRegister", "РегистрыРасчета": "CalculationRegister",
    "Отчеты": "Report", "Обработки": "DataProcessor", "ЖурналыДокументов": "DocumentJournal",
    "Константы": "Constant", "ПланыВидовХарактеристик": "ChartOfCharacteristicTypes",
    "ПланыСчетов": "ChartOfAccounts", "ПланыВидовРасчета": "ChartOfCalculationTypes",
    "ПланыОбмена": "ExchangePlan", "БизнесПроцессы": "BusinessProcess", "Задачи": "Task",
}
# Коллекции, доступные только как Метаданные.<Коллекция>.<Имя> (или глобально, где указано)
КОЛЛЕКЦИИ_МЕТАДАННЫХ = dict(КОЛЛЕКЦИИ_КОДА, **{
    "ОбщиеМодули": "CommonModule", "ОбщиеФормы": "CommonForm", "ОбщиеКоманды": "CommonCommand",
    "ОбщиеКартинки": "CommonPicture", "ОбщиеМакеты": "CommonTemplate",
    "ОбщиеРеквизиты": "CommonAttribute", "ЭлементыСтиля": "StyleItem",
    "ОпределяемыеТипы": "DefinedType", "ПараметрыСеанса": "SessionParameter",
    "ФункциональныеОпции": "FunctionalOption", "Роли": "Role", "Подсистемы": "Subsystem",
    "ПодпискиНаСобытия": "EventSubscription", "РегламентныеЗадания": "ScheduledJob",
    "КритерииОтбора": "FilterCriterion", "ХранилищаНастроек": "SettingsStorage",
    "WebСервисы": "WebService", "HTTPСервисы": "HTTPService", "ПакетыXDTO": "XDTOPackage",
    "ГруппыКоманд": "CommandGroup",
})
# Глобальные свойства, которые сами — коллекции объектов метаданных
ГЛОБАЛЬНЫЕ_КОЛЛЕКЦИИ = dict(КОЛЛЕКЦИИ_КОДА, **{
    "ПараметрыСеанса": "SessionParameter", "БиблиотекаКартинок": "CommonPicture",
    "ЦветаСтиля": "StyleItem", "ШрифтыСтиля": "StyleItem", "ЭлементыСтиля": "StyleItem",
    "РегламентныеЗадания": None,   # у менеджера регламентных заданий имён объектов нет
})

# Имя таблицы в тексте запроса (и в строках Тип("СправочникСсылка.X")) -> тип
ТАБЛИЦЫ_ЗАПРОСА = {
    "Справочник": "Catalog", "Документ": "Document", "Перечисление": "Enum",
    "РегистрСведений": "InformationRegister", "РегистрНакопления": "AccumulationRegister",
    "РегистрБухгалтерии": "AccountingRegister", "РегистрРасчета": "CalculationRegister",
    "ЖурналДокументов": "DocumentJournal", "Константа": "Constant",
    "ПланВидовХарактеристик": "ChartOfCharacteristicTypes", "ПланСчетов": "ChartOfAccounts",
    "ПланВидовРасчета": "ChartOfCalculationTypes", "ПланОбмена": "ExchangePlan",
    "БизнесПроцесс": "BusinessProcess", "Задача": "Task",
    "Отчет": "Report", "Обработка": "DataProcessor", "ОбщаяФорма": "CommonForm",
}

# Продукт LM внутри выгрузки LM: что переносим в УЗ_ext (режим --только-продукт)
ПРОДУКТ_ПО_ВИДАМ = {
    "Catalog": {"Кассы", "Организации", "СтатьиЗатрат"},
    "Document": {"ПриходныйКассовыйОрдер", "РасходныйКассовыйОрдер"},
    "CommonModule": {"LM", "LM_ОповещениеПоEmail"},
}
# У хозяина берём только эти два — в продукте они «заимствованы» заранее
ЗАИМСТВУЕМЫЕ_ПО_ПЛАНУ = {("Catalog", "Организации"), ("Catalog", "Пользователи")}

# Файлы, которые сами по себе — производные (перечень всего подряд), их не аудируем
НЕ_ИСХОДНИКИ = {"ConfigDumpInfo.xml"}


def в_продукте(тип, имя):
    return имя.startswith("LM_") or имя in ПРОДУКТ_ПО_ВИДАМ.get(тип, ())


def читать(путь):
    with io.open(путь, encoding="utf-8-sig", errors="replace") as ф:
        return ф.read()


def ключ(имя):
    """Имена в 1С регистронезависимы: сравниваем по casefold, ё == е."""
    return имя.casefold().replace("ё", "е")


# ─────────────────────────── замечания и результат ───────────────────────────

class Замечание:
    __slots__ = ("путь", "строка", "текст")

    def __init__(self, путь, строка, текст):
        self.путь, self.строка, self.текст = путь, строка, текст

    def __str__(self):
        if self.строка:
            return "%s:%d: %s" % (self.путь, self.строка, self.текст)
        return "%s: %s" % (self.путь, self.текст)


class Результат:
    def __init__(self, имя):
        self.имя = имя
        self.ошибки = []
        self.предупреждения = []
        self.сводка = []          # строки справки для человека (не замечания)
        self.проверено = ""

    def ошибка(self, путь, строка, текст):
        self.ошибки.append(Замечание(путь, строка, текст))

    def предупреждение(self, путь, строка, текст):
        self.предупреждения.append(Замечание(путь, строка, текст))


# ─────────────────────────── разметка BSL ───────────────────────────

class Модуль:
    """Модуль BSL, разложенный на код и строковые литералы.

    код       — текст той же длины и с теми же переводами строк, в котором
                строковые литералы, литералы дат и комментарии заменены пробелами;
    литералы  — [(номер_строки_начала, содержимое, смещение_открывающей_кавычки)];
    текст     — исходный текст.
    """

    def __init__(self, путь, текст):
        self.путь = путь
        self.текст = текст
        self._переводы = [м.start() for м in re.finditer("\n", текст)]
        self.код, self.литералы, self.комментарии = self._разметить(текст)

    def строка(self, смещение):
        return bisect.bisect_right(self._переводы, смещение - 1) + 1

    def строка_в_литерале(self, литерал, позиция):
        """Номер строки файла для позиции внутри содержимого литерала."""
        номер, содержимое, _ = литерал
        return номер + содержимое[:позиция].count("\n")

    def _разметить(self, т):
        выход = list(т)
        литералы, комментарии = [], []
        i, n = 0, len(т)

        def затереть(с, по):
            for к in range(с, по):
                if выход[к] != "\n":
                    выход[к] = " "

        while i < n:
            с = т[i]
            if с == '"':
                j = i + 1
                буфер = []
                while j < n:
                    if т[j] == '"':
                        if j + 1 < n and т[j + 1] == '"':
                            буфер.append('"')
                            j += 2
                            continue
                        break
                    буфер.append(т[j])
                    j += 1
                литералы.append((self.строка(i), "".join(буфер), i))
                затереть(i, min(j + 1, n))
                i = j + 1
            elif с == "/" and i + 1 < n and т[i + 1] == "/":
                j = т.find("\n", i)
                if j < 0:
                    j = n
                комментарии.append((self.строка(i), т[i:j]))
                затереть(i, j)
                i = j
            elif с == "'":
                j = т.find("'", i + 1)
                конец_строки = т.find("\n", i)
                if j < 0 or (0 <= конец_строки < j):
                    i += 1
                    continue
                затереть(i, j + 1)
                i = j + 1
            else:
                i += 1
        return "".join(выход), литералы, комментарии

    def локальные_имена(self):
        """Имена, которые модуль сам объявляет: переменные, параметры, счётчики.

        Нужны, чтобы не принять «Пользователи.Добавить(...)» у локального массива
        за вызов общего модуля БСП «Пользователи»."""
        к = self.код
        имена = set()
        for м in re.finditer(r"(?im)(?:^|;|\bТогда\b|\bИначе\b|\bЦикл\b|\bПопытка\b|\bИсключение\b)"
                             r"[ \t]*([А-Яа-яЁёA-Za-z_][\wЁё]*)[ \t]*=", к):
            имена.add(ключ(м.group(1)))
        for м in re.finditer(r"(?i)\bПерем\s+([^;]+);", к):
            for часть in м.group(1).split(","):
                слово = re.match(r"\s*([\wЁё]+)", часть)
                if слово:
                    имена.add(ключ(слово.group(1)))
        for м in re.finditer(r"(?i)\bДля\s+Каждого\s+([\wЁё]+)\s+Из\b", к):
            имена.add(ключ(м.group(1)))
        for м in re.finditer(r"(?i)\bДля\s+([\wЁё]+)\s*=", к):
            имена.add(ключ(м.group(1)))
        for _, _, параметры in self.объявления():
            for имя, _ in параметры:
                имена.add(ключ(имя))
        return имена

    def объявления(self):
        """[(смещение_имени, имя, [(параметр, смещение)])] процедур и функций."""
        к = self.код
        итог = []
        for м in re.finditer(r"(?im)^[ \t]*(?:Асинх[ \t]+)?(?:Процедура|Функция|Procedure|Function)"
                             r"[ \t]+([\wЁё]+)[ \t]*\(", к):
            начало = м.end()
            глубина, j = 1, начало
            while j < len(к) and глубина:
                if к[j] == "(":
                    глубина += 1
                elif к[j] == ")":
                    глубина -= 1
                j += 1
            параметры = []
            внутри = к[начало:j - 1]
            поз = 0
            for часть in внутри.split(","):
                п = re.match(r"\s*(?:(?:Знач|Val)\s+)?([\wЁё]+)", часть, re.I)
                if п:
                    параметры.append((п.group(1), начало + поз + п.start(1)))
                поз += len(часть) + 1
            итог.append((м.start(1), м.group(1), параметры))
        return итог


def это_запрос(текст):
    return bool(re.search(r"(?i)(?<![\wЁё])(ВЫБРАТЬ|SELECT)(?![\wЁё])", текст)) and \
        bool(re.search(r"(?i)(?<![\wЁё])(ИЗ|FROM|ГДЕ|WHERE)(?![\wЁё])", текст))


def очистить_запрос(текст):
    """Текст запроса без «|» в начале строк и без комментариев «//».
    Длина строк и их число сохраняются — позиции остаются верными."""
    строки = []
    for стр in текст.split("\n"):
        м = re.match(r"^(\s*)\|", стр)
        if м:
            стр = стр[:м.end() - 1] + " " + стр[м.end():]
        к = стр.find("//")
        if к >= 0:
            стр = стр[:к] + " " * (len(стр) - к)
        строки.append(стр)
    return "\n".join(строки)


# ─────────────────────────── метаданные объекта ───────────────────────────

def _без_пространства(тег):
    return тег.split("}", 1)[-1]


class Объект:
    def __init__(self, тип, имя, xml, каталог, заимствован=None):
        self.тип, self.имя, self.xml, self.каталог = тип, имя, xml, каталог
        self._заимствован = заимствован
        self._разобран = False
        self.реквизиты, self.тч, self.измерения, self.ресурсы = set(), {}, set(), set()
        self.значения, self.предопределенные, self.графы = set(), set(), set()
        self.вид_регистра = ""
        self.периодичность = ""
        self.дочерние = []        # [(вид, имя, заимствован)] — реквизиты, ТЧ, формы, команды

    @property
    def заимствован(self):
        if self._заимствован is None:
            if not self.xml:
                self._заимствован = False
            else:
                голова = читать(self.xml).split("<ChildObjects>")[0]
                self._заимствован = "<ObjectBelonging>Adopted</ObjectBelonging>" in голова
        return self._заимствован

    def разобрать(self):
        if self._разобран or not self.xml:
            return self
        self._разобран = True
        try:
            корень = ET.parse(self.xml).getroot()
        except ET.ParseError:
            return self
        узел = next(iter(корень), None)
        if узел is None:
            return self
        for св in узел.iter():
            т = _без_пространства(св.tag)
            if т == "RegisterType":
                self.вид_регистра = (св.text or "").strip()
            elif т == "InformationRegisterPeriodicity":
                self.периодичность = (св.text or "").strip()
        дети = next((р for р in узел if _без_пространства(р.tag) == "ChildObjects"), None)
        if дети is None:
            return self
        for ребёнок in дети:
            вид = _без_пространства(ребёнок.tag)
            if ребёнок.text and ребёнок.text.strip() and len(ребёнок) == 0:
                # <Form>Имя</Form>, <Template>Имя</Template> — только имя
                self.дочерние.append((вид, ребёнок.text.strip(), None))
                continue
            свойства = next((р for р in ребёнок if _без_пространства(р.tag) == "Properties"), None)
            if свойства is None:
                continue
            имя = заимств = None
            for р in свойства:
                т = _без_пространства(р.tag)
                if т == "Name":
                    имя = (р.text or "").strip()
                elif т == "ObjectBelonging":
                    заимств = (р.text or "").strip() == "Adopted"
            if not имя:
                continue
            self.дочерние.append((вид, имя, bool(заимств)))
            if вид == "Attribute":
                self.реквизиты.add(имя)
            elif вид == "Dimension":
                self.измерения.add(имя)
            elif вид == "Resource":
                self.ресурсы.add(имя)
            elif вид == "EnumValue":
                self.значения.add(имя)
            elif вид == "Column":
                self.графы.add(имя)
            elif вид == "TabularSection":
                колонки = set()
                вложенные = next((р for р in ребёнок if _без_пространства(р.tag) == "ChildObjects"), None)
                if вложенные is not None:
                    for кол in вложенные:
                        for н in кол.iter():
                            if _без_пространства(н.tag) == "Name":
                                колонки.add((н.text or "").strip())
                                break
                self.тч[имя] = колонки
        if self.каталог:
            предопр = os.path.join(self.каталог, "Ext", "Predefined.xml")
            if os.path.exists(предопр):
                self.предопределенные = set(re.findall(r"<Name>([^<]+)</Name>", читать(предопр)))
        return self


# ─────────────────────────── исходники ───────────────────────────

class Исходники:
    """Каталог исходников в XML-выгрузке. продукт=True — только объекты LM-продукта."""

    def __init__(self, корень, продукт=False):
        self.корень = os.path.abspath(корень)
        self.продукт = продукт
        self.объекты = []
        self.по_типу = {}
        if not os.path.isdir(self.корень):
            raise SystemExit("Нет каталога исходников: %s" % self.корень)
        for папка, тип in ВИДЫ.items():
            путь = os.path.join(self.корень, папка)
            if not os.path.isdir(путь):
                continue
            for файл in sorted(os.listdir(путь)):
                if not файл.endswith(".xml"):
                    continue
                имя = файл[:-4]
                if продукт and not в_продукте(тип, имя):
                    continue
                каталог = os.path.join(путь, имя)
                заимств = None
                if продукт:
                    заимств = (тип, имя) in ЗАИМСТВУЕМЫЕ_ПО_ПЛАНУ
                о = Объект(тип, имя, os.path.join(путь, файл),
                           каталог if os.path.isdir(каталог) else None, заимств)
                self.объекты.append(о)
                self.по_типу.setdefault(тип, {})[ключ(имя)] = о
        if продукт:
            # у хозяина они есть всегда: ссылка на них — не ошибка
            for тип, имя in ЗАИМСТВУЕМЫЕ_ПО_ПЛАНУ:
                if ключ(имя) not in self.по_типу.get(тип, {}):
                    self.по_типу.setdefault(тип, {})[ключ(имя)] = Объект(тип, имя, None, None, True)

    def найти(self, тип, имя):
        return self.по_типу.get(тип, {}).get(ключ(имя))

    def отн(self, путь):
        return os.path.relpath(путь, self.корень).replace("\\", "/")

    def файлы(self, *расширения):
        """Все файлы исходников с данными расширениями (в режиме продукта — только его объекты)."""
        расширения = tuple(р.lower() for р in расширения)
        видено = set()

        def годится(имя_файла):
            return имя_файла.lower().endswith(расширения) and имя_файла not in НЕ_ИСХОДНИКИ

        if not self.продукт:
            for файл in sorted(os.listdir(self.корень)):
                п = os.path.join(self.корень, файл)
                if os.path.isfile(п) and годится(файл):
                    yield п
            ext = os.path.join(self.корень, "Ext")
            if os.path.isdir(ext):
                for к, _, фф in os.walk(ext):
                    for ф in sorted(фф):
                        if годится(ф):
                            yield os.path.join(к, ф)
        for о in self.объекты:
            if о.xml and годится(os.path.basename(о.xml)) and о.xml not in видено:
                видено.add(о.xml)
                yield о.xml
            if о.каталог:
                for к, папки, фф in os.walk(о.каталог):
                    папки.sort()
                    for ф in sorted(фф):
                        if годится(ф):
                            yield os.path.join(к, ф)

    def модули(self):
        for путь in self.файлы(".bsl"):
            yield Модуль(путь, читать(путь))

    def объект_файла(self, путь):
        """Объект метаданных, которому принадлежит файл (или None)."""
        отн = os.path.relpath(путь, self.корень).split(os.sep)
        if len(отн) >= 2 and отн[0] in ВИДЫ:
            имя = отн[1][:-4] if отн[1].endswith(".xml") else отн[1]
            return self.найти(ВИДЫ[отн[0]], имя)
        return None


def это_слой_совместимости(путь):
    части = путь.replace("\\", "/").split("/")
    return "CommonModules" in части and СЛОЙ_СОВМЕСТИМОСТИ in части


def реквизиты_формы(путь_модуля):
    """Имена реквизитов формы для её модуля (…/Forms/Ф/Ext/Form/Module.bsl)."""
    путь_формы = os.path.join(os.path.dirname(os.path.dirname(путь_модуля)), "Form.xml")
    if not (путь_модуля.replace("\\", "/").endswith("/Ext/Form/Module.bsl") and os.path.exists(путь_формы)):
        return set()
    т = читать(путь_формы)
    н = т.find("<Attributes>")
    if н < 0:
        return set()
    return {ключ(и) for и in re.findall(r'<Attribute name="([^"]+)"', т[н:])}


# ─────────────────────────── запуск ───────────────────────────

def аргументы(описание, лишние=None):
    п = argparse.ArgumentParser(description=описание)
    п.add_argument("каталог", nargs="?", default=None, help="каталог исходников (по умолчанию src_ext)")
    п.add_argument("--каталог", dest="каталог_ключ", default=None)
    п.add_argument("--только-продукт", action="store_true",
                   help="только объекты LM-продукта (прогон «как если бы» по выгрузке LM)")
    п.add_argument("--все-строки", action="store_true", help="печатать все замечания без усечения")
    п.add_argument("--макс", type=int, default=60, help="замечаний на аудит в выводе (по умолчанию 60)")
    if лишние:
        лишние(п)
    а = п.parse_args()
    а.каталог = а.каталог_ключ or а.каталог or КАТАЛОГ_ПО_УМОЛЧАНИЮ
    return а


def настроить_вывод():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def напечатать(р, макс=60):
    print("=" * 78)
    print("АУДИТ %s%s" % (р.имя, (" — " + р.проверено) if р.проверено else ""))
    print("-" * 78)
    for заголовок, список in (("ошибки", р.ошибки), ("предупреждения", р.предупреждения)):
        if not список:
            continue
        print("[%s: %d]" % (заголовок, len(список)))
        for з in список[:макс] if макс else список:
            print("  " + str(з))
        if макс and len(список) > макс:
            print("  … и ещё %d (--все-строки покажет все)" % (len(список) - макс))
    for строка in р.сводка:
        print("  " + строка)
    print("замечаний: %d, предупреждений: %d" % (len(р.ошибки), len(р.предупреждения)))


def запустить_один(модуль):
    настроить_вывод()
    а = аргументы(модуль.__doc__.strip().splitlines()[0])
    исх = Исходники(а.каталог, а.только_продукт)
    if not исх.объекты:
        print("в %s нет ни одного объекта метаданных — проверять нечего" % а.каталог)
        sys.exit(1)
    р = модуль.проверить(исх)
    напечатать(р, 0 if а.все_строки else а.макс)
    print("ИТОГО замечаний: %d" % len(р.ошибки))
    sys.exit(1 if р.ошибки else 0)
