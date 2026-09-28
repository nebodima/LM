"""Стенд формы отчёта: серверный код модуля формы — во внешней обработке, чтобы тест выполнил его через COM.

У трёх отчётов УЗ_ext нет СКД: всё формирование — в серверных процедурах модуля формы
(`УЗ_АналитикаПоУченикам`, `УЗ_ВедомостьПоКассеДляМенеджеров`, `УЗ_ДвиженияДокумента`). Во внешнем
соединении форм нет, поэтому раньше тест только читал макеты и писал `проверить(True)` — зелёный по
построению. Стенд берёт ТОТ ЖЕ текст модуля формы из src_ext и превращает его в модуль объекта внешней
обработки:
  * процедуры с директивой &НаКлиенте выбрасываются, остальные директивы снимаются, у каждой процедуры
    и функции — «Экспорт» (тест зовёт их по имени, как это делает форма: ПриСозданииНаСервере, затем
    команда «Сформировать»);
  * реквизиты формы (Form.xml → Attributes) — экспортные переменные модуля с начальным значением по
    типу (СтандартныйПериод, ТабличныйДокумент, СписокЗначений, число, булево; Отчет — объект отчёта);
    `Параметры` формы — Структура, её заполняет тест.
Логика не копируется руками: изменится модуль формы — изменится и стенд (кэш по хэшу текста).

Сборка .epf — пакетный конфигуратор (/LoadExternalDataProcessorOrReportFromFiles) на пустой файловой базе в
%TEMP%\\уз_прогон\\стенд_форм (создаётся один раз, ~3 с). Готовая обработка кэшируется по хэшу
сгенерированного текста: конфигуратор запускается, только когда модуль формы изменился (~5 с на отчёт).
"""
import hashlib
import os
import re
import subprocess
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

EXE = r"C:\Program Files\1cv8\8.3.27.1936\bin\1cv8.exe"
ИСХОДНИКИ = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src_ext")
ПАПКА = os.path.join(tempfile.gettempdir(), "уз_прогон", "стенд_форм")
ВЕРСИЯ_ГЕНЕРАТОРА = "1"      # сменить при правке генератора — кэш пересоберётся

_ЗАГОЛОВОК = re.compile(r"^\s*(Процедура|Функция)\s+([\wЁё]+)\s*\(", re.I)
_КОНЕЦ = re.compile(r"^\s*(КонецПроцедуры|КонецФункции)\b", re.I)
_НС = {"f": "http://v8.1c.ru/8.3/xcf/logform", "v8": "http://v8.1c.ru/8.1/data/core"}

# тип реквизита формы → начальное значение переменной стенда
_НАЧАЛО = {
    "v8:StandardPeriod": "Новый СтандартныйПериод",
    "mxl:SpreadsheetDocument": "Новый ТабличныйДокумент",
    "v8:ValueListType": "Новый СписокЗначений",
    "xs:decimal": "0",
    "xs:boolean": "Ложь",
    "xs:string": '""',
    "xs:dateTime": "'00010101'",
}


def _скобки(строка):
    """Баланс круглых скобок вне строковых литералов."""
    баланс, в_строке = 0, False
    for поз, знак in enumerate(строка):
        if знак == '"':
            в_строке = not в_строке
        elif not в_строке:
            if строка.startswith("//", поз):
                break
            баланс += (знак == "(") - (знак == ")")
    return баланс


def серверный_модуль(код):
    """Текст модуля формы → (текст для модуля объекта, [имена процедур])."""
    итог, имена = [], []
    директива, в_процедуре, клиентская, в_заголовке, баланс = None, False, False, False, 0
    for строка in код.splitlines():
        голая = строка.strip()
        if not в_процедуре:
            if голая.startswith("&"):
                директива = голая.lower()
                continue
            м = _ЗАГОЛОВОК.match(строка)
            if not м:
                if голая.lower().startswith("перем") and директива == "&наклиенте":
                    директива = None
                    continue
                if голая and not голая.startswith("//"):
                    директива = None
                итог.append(строка)
                continue
            в_процедуре, в_заголовке, баланс = True, True, 0
            клиентская = директива == "&наклиенте"
            директива = None
            if not клиентская:
                имена.append(м.group(2))
        if клиентская:
            if _КОНЕЦ.match(строка):
                в_процедуре = False
            continue
        if в_заголовке:
            баланс += _скобки(строка)
            if баланс <= 0:
                в_заголовке = False
                if not re.search(r"\)\s*Экспорт\b", строка, re.I):
                    поз = строка.rfind(")")
                    строка = строка[:поз + 1] + " Экспорт" + строка[поз + 1:]
        elif _КОНЕЦ.match(строка):
            в_процедуре = False
        итог.append(строка)
    return "\n".join(итог), имена


def реквизиты_формы(путь_формы):
    """[(имя, тип)] реквизитов формы из Form.xml."""
    корень = ET.parse(путь_формы).getroot()
    итог = []
    for р in корень.iter("{%s}Attribute" % _НС["f"]):
        тип = р.find("f:Type/v8:Type", _НС)
        итог.append((р.get("name"), тип.text if тип is not None else ""))
    return итог


def модуль_стенда(отчет, форма):
    """Полный текст модуля объекта обработки-стенда для формы отчёта."""
    каталог = os.path.join(ИСХОДНИКИ, "Reports", отчет, "Forms", форма, "Ext")
    with open(os.path.join(каталог, "Form", "Module.bsl"), encoding="utf-8-sig") as ф:
        код, имена = серверный_модуль(ф.read())
    переменные, начало = [], []
    for имя, тип in реквизиты_формы(os.path.join(каталог, "Form.xml")):
        if имя in имена:
            continue
        переменные.append("Перем %s Экспорт;" % имя)
        if тип.startswith("cfg:ReportObject."):
            начало.append("%s = Отчеты.%s.Создать();" % (имя, тип.split(".", 1)[1]))
        elif тип in _НАЧАЛО:
            начало.append("%s = %s;" % (имя, _НАЧАЛО[тип]))
    переменные.append("Перем Параметры Экспорт;   // параметры формы — заполняет тест")
    начало.append("Параметры = Новый Структура;")
    return "\n".join(["// Стенд формы Отчет.%s.Форма.%s — сгенерирован tools/тесты/стенд_форм.py, не править."
                      % (отчет, форма), ""] + переменные + ["", код, ""] + начало) + "\n"


def _xml(имя):
    ид = lambda соль: str(uuid.uuid5(uuid.NAMESPACE_URL, "уз-стенд/%s/%s" % (имя, соль)))  # noqa: E731
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:v8="http://v8.1c.ru/8.1/data/core" '
            'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n'
            '\t<ExternalDataProcessor uuid="%s">\n\t\t<InternalInfo>\n\t\t\t<xr:ContainedObject>\n'
            '\t\t\t\t<xr:ClassId>c3831ec8-d8d5-4f93-8a22-f9bfae07327f</xr:ClassId>\n'
            '\t\t\t\t<xr:ObjectId>%s</xr:ObjectId>\n\t\t\t</xr:ContainedObject>\n'
            '\t\t\t<xr:GeneratedType name="ExternalDataProcessorObject.%s" category="Object">\n'
            '\t\t\t\t<xr:TypeId>%s</xr:TypeId>\n\t\t\t\t<xr:ValueId>%s</xr:ValueId>\n'
            '\t\t\t</xr:GeneratedType>\n\t\t</InternalInfo>\n\t\t<Properties>\n\t\t\t<Name>%s</Name>\n'
            '\t\t\t<Synonym/>\n\t\t\t<Comment/>\n\t\t\t<DefaultForm/>\n\t\t\t<AuxiliaryForm/>\n'
            '\t\t</Properties>\n\t\t<ChildObjects/>\n\t</ExternalDataProcessor>\n</MetaDataObject>\n'
            % (ид("u"), ид("o"), имя, ид("t"), ид("v"), имя))


def _конфигуратор(аргументы, журнал, таймаут):
    if os.path.exists(журнал):
        os.remove(журнал)
    п = subprocess.Popen([EXE] + аргументы + ["/Out", журнал, "/DisableStartupDialogs", "/DisableStartupMessages"])
    try:
        код = п.wait(timeout=таймаут)
    except subprocess.TimeoutExpired:
        п.kill()
        raise RuntimeError("стенд: конфигуратор не уложился в %d с (%s)" % (таймаут, " ".join(аргументы[:2])))
    текст = open(журнал, encoding="utf-8-sig", errors="replace").read() if os.path.exists(журнал) else ""
    return код, текст


def собрать(отчет, форма):
    """Путь к .epf стенда (из кэша или свежесобранный) и секунд на сборку (0 — из кэша)."""
    модуль = модуль_стенда(отчет, форма)
    имя = "Стенд_" + отчет
    хэш = hashlib.sha1((ВЕРСИЯ_ГЕНЕРАТОРА + модуль).encode("utf-8")).hexdigest()[:12]
    epf = os.path.join(ПАПКА, "%s_%s.epf" % (имя, хэш))
    if os.path.exists(epf):
        return epf, 0.0
    # прогон идёт тремя процессами (УНФ/БП/УТ) над одной папкой стенда — собирает один,
    # остальные ждут и берут готовый .epf из кэша (иначе «файл занят другим процессом»)
    os.makedirs(ПАПКА, exist_ok=True)
    with _ЗамокСборки():
        if os.path.exists(epf):
            return epf, 0.0
        return _собрать(имя, хэш, модуль, epf)


class _ЗамокСборки:
    def __enter__(self):
        self.путь = os.path.join(ПАПКА, "сборка.lock")
        срок = time.time() + 180
        while True:
            try:
                self.ф = os.open(self.путь, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.путь) > 300:   # от упавшего процесса
                        os.remove(self.путь)
                        continue
                except FileNotFoundError:
                    continue            # замок сняли между попытками (сосед закончил) — взять заново
                if time.time() > срок:
                    raise RuntimeError("стенд: замок сборки занят дольше 180 с (%s)" % self.путь)
                time.sleep(0.2)

    def __exit__(self, *_):
        os.close(self.ф)
        try:
            os.remove(self.путь)
        except FileNotFoundError:
            return              # сосед снял замок как устаревший (сборка шла дольше 300 с)


def _собрать(имя, хэш, модуль, epf):
    н = time.time()
    база = os.path.join(ПАПКА, "база")
    if not os.path.exists(os.path.join(база, "1Cv8.1CD")):
        os.makedirs(ПАПКА, exist_ok=True)
        код, текст = _конфигуратор(["CREATEINFOBASE", "File=%s" % база], os.path.join(ПАПКА, "создание.log"), 60)
        if код != 0 or not os.path.exists(os.path.join(база, "1Cv8.1CD")):
            raise RuntimeError("стенд: пустая база не создана (код %s): %s" % (код, текст.strip()[:300]))
    хэш = os.path.basename(epf)[len(имя) + 1:-4]
    исходник = os.path.join(ПАПКА, "src_%s_%s" % (имя, хэш))
    os.makedirs(os.path.join(исходник, имя, "Ext"), exist_ok=True)
    with open(os.path.join(исходник, имя + ".xml"), "w", encoding="utf-8-sig") as ф:
        ф.write(_xml(имя))
    with open(os.path.join(исходник, имя, "Ext", "ObjectModule.bsl"), "w", encoding="utf-8-sig") as ф:
        ф.write(модуль)
    код, текст = _конфигуратор(["DESIGNER", "/F", база, "/LoadExternalDataProcessorOrReportFromFiles",
                                os.path.join(исходник, имя + ".xml"), epf],
                               os.path.join(ПАПКА, имя + ".log"), 90)
    if код != 0 or not os.path.exists(epf):
        raise RuntimeError("стенд %s не собран (код %s): %s" % (имя, код, текст.strip()[:300]))
    return epf, time.time() - н


def создать(c, отчет, форма, безопасный=False):
    """Объект обработки-стенда в сеансе c → (объект, секунд на сборку).
    безопасный=True — для сеанса сотрудника (тест прав): внешнюю обработку не в безопасном режиме создаёт только
    администратор; код модуля формы от безопасного режима не зависит (привилегий расширение из файла и так не имеет)."""
    epf, сек = собрать(отчет, форма)
    return c.ВнешниеОбработки.Создать(epf, безопасный), сек
