"""Руководство пользователя «Учёт занятий» в PDF — из встроенной справки F1 (образец — «Путевые листы»).

Источник — те же страницы, что открывает F1 в программе (`src_ext/**/Ext/Help/ru.html`): два отдельных текста
разошлись бы через месяц, и покупатель читал бы в PDF про кнопку, которой в продукте уже нет.

Порядок глав — по подсистемам «Учёт занятий»: страница раздела, затем страницы каждой подсистемы (Документы, Касса,
Справочники, Отчёты, Настройки, Служебные) и объектов в её составе — справка объекта, затем его форм. Страницы,
не попавшие ни в одну подсистему, идут в конце («Прочие формы»): в PDF входят все страницы справки. Ссылки между
страницами справки (`Document.УЗ_Урок/Help`) становятся переходами внутри PDF. Титул, оглавление и печатные стили
добавляет скрипт; печать — Chrome без окна и без колонтитулов (в руководстве для покупателя не должно быть пути
к файлу рабочего компьютера).

    python tools\\собрать_инструкцию.py

Готовые файлы: docs/инструкция/УчетЗанятий_2.0.html (открыть в браузере) и docs/инструкция/УчетЗанятий_2.0.pdf.
"""
import datetime
import html
import os
import re
import subprocess
import sys
import time

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(КОРЕНЬ, "src_ext")
ПАПКА = os.path.join(КОРЕНЬ, "docs", "инструкция")
HTML = os.path.join(ПАПКА, "УчетЗанятий_2.0.html")
PDF = os.path.join(ПАПКА, "УчетЗанятий_2.0.pdf")
ХРОМ = next((п for п in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") if os.path.isfile(п)), None)
ПАПКИ = {"Document": "Documents", "Catalog": "Catalogs", "DataProcessor": "DataProcessors", "Report": "Reports",
         "DocumentJournal": "DocumentJournals", "InformationRegister": "InformationRegisters",
         "AccumulationRegister": "AccumulationRegisters", "CommonForm": "CommonForms", "Enum": "Enums"}
ПЕРВЫЕ_ФОРМЫ = ("ФормаДокумента", "ФормаЭлемента", "ФормаЗаписи", "Форма", "ФормаОтчета", "ФормаСписка")
МЕСЯЦЫ = ("января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
          "ноября", "декабря")

СТИЛИ = """<style>
  @page { size: A4; margin: 18mm 16mm 20mm 16mm; }
  body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #222; }
  h1 { font-size: 19pt; margin: 0 0 10pt; break-before: page; page-break-before: always; }
  h2 { font-size: 14pt; margin-top: 20pt; border-bottom: 1px solid #d6dbe1; padding-bottom: 2pt;
       break-after: avoid; page-break-after: avoid; }
  h3 { font-size: 12pt; margin-top: 14pt; break-after: avoid; page-break-after: avoid; }
  h4 { font-size: 11pt; margin-top: 10pt; break-after: avoid; page-break-after: avoid; }
  table { border-collapse: collapse; margin: 6pt 0; break-inside: avoid; }
  td, th { border: 1px solid #c8ced6; padding: 3pt 6pt; vertical-align: top; }
  a { color: #1a4f8b; text-decoration: none; }
  .титул { break-after: page; page-break-after: always; padding-top: 70mm; text-align: center; }
  .титул .имя { font-size: 30pt; font-weight: 600; }
  .титул .подзаголовок { font-size: 13pt; margin-top: 10pt; color: #444; }
  .титул .версия { font-size: 11pt; margin-top: 40mm; color: #666; }
  .оглавление { break-after: page; page-break-after: always; }
  .оглавление ul { list-style: none; padding-left: 14pt; margin: 2pt 0; }
  .оглавление > ul { padding-left: 0; }
  .оглавление li.раздел { font-weight: 600; margin-top: 6pt; }
  .оглавление li li { font-weight: normal; }
  .сноска { margin-top: 26pt; padding-top: 8pt; border-top: 1px solid #d6dbe1; font-size: 9pt; color: #666; }
</style>"""


def читать(путь):
    with open(путь, encoding="utf-8-sig") as ф:
        return ф.read()


def тело(путь):
    """Содержимое <body> страницы справки без служебной ссылки на стиль 1С."""
    т = читать(путь)
    м = re.search(r"<body[^>]*>(.*)</body>", т, re.S)
    return (м.group(1) if м else т).strip()


def понизить(текст, на):
    """h1 → h(1+на) …: страница объекта внутри главы подсистемы."""
    return re.sub(r"<(/?)h([1-6])(\s[^>]*)?>",
                  lambda м: "<%sh%d%s>" % (м.group(1), min(6, int(м.group(2)) + на), м.group(3) or ""), текст)


def состав(xml):
    return re.findall(r"<xr:Item[^>]*>([^<]+)</xr:Item>", читать(xml))


def страницы_объекта(полное):
    """[(якорь, путь к ru.html)] — справка объекта и его форм (основные формы первыми)."""
    тип, имя = полное.split(".", 1)
    папка = ПАПКИ.get(тип)
    if папка is None:
        return []
    корень = os.path.join(SRC, папка, имя)
    итог = []
    своя = os.path.join(корень, "Ext", "Help", "ru.html")
    if os.path.isfile(своя):
        итог.append((полное, своя))
    формы = os.path.join(корень, "Forms")
    if os.path.isdir(формы):
        имена = sorted(os.listdir(формы), key=lambda ф: (ПЕРВЫЕ_ФОРМЫ.index(ф) if ф in ПЕРВЫЕ_ФОРМЫ else 99, ф))
        for ф in имена:
            п = os.path.join(формы, ф, "Ext", "Help", "ru.html")
            if os.path.isfile(п):
                итог.append(("%s.Form.%s" % (полное, ф), п))
    return итог


def заголовок(текст):
    м = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", текст, re.S)
    return re.sub(r"<[^>]+>", "", м.group(1)).strip() if м else "Без заголовка"


def версия():
    м = re.search(r"<Version>([^<]+)</Version>", читать(os.path.join(SRC, "Configuration.xml")))
    return м.group(1) if м else "—"


def собрать():
    корень_подсистем = os.path.join(SRC, "Subsystems")
    главная = os.path.join(корень_подсистем, "УЗ_УчетЗанятий")
    главы = []          # [(якорь главы, заголовок, html главы, [(якорь, заголовок)])]
    взято = set()

    т = тело(os.path.join(главная, "Ext", "Help", "ru.html"))
    главы.append(("Subsystem.УЗ_УчетЗанятий", заголовок(т), т, []))
    подсистемы = re.findall(r"<Subsystem>([^<]+)</Subsystem>", читать(os.path.join(корень_подсистем, "УЗ_УчетЗанятий.xml")))
    for под in подсистемы:
        якорь = "Subsystem.УЗ_УчетЗанятий.Subsystem.%s" % под
        справка = os.path.join(главная, "Subsystems", под, "Ext", "Help", "ru.html")
        т = тело(справка) if os.path.isfile(справка) else "<h1>%s</h1>" % под
        части, пункты = [т], []
        for полное in состав(os.path.join(главная, "Subsystems", под + ".xml")):
            for ак, путь in страницы_объекта(полное):
                if путь in взято:
                    continue
                взято.add(путь)
                страница = понизить(тело(путь), 1)
                пункты.append((ак, заголовок(страница)))
                части.append('<div id="%s">%s</div>' % (html.escape(ак), страница))
        главы.append((якорь, заголовок(т), "\n".join(части), пункты))

    прочие, пункты = [], []
    for папка, _, файлы in os.walk(SRC):
        if "ru.html" not in файлы or os.path.join(папка, "ru.html") in взято or "Subsystems" in папка:
            continue
        путь = os.path.join(папка, "ru.html")
        отн = os.path.relpath(путь, SRC).split(os.sep)
        тип = {в: к for к, в in ПАПКИ.items()}.get(отн[0], отн[0])
        ак = "%s.%s" % (тип, отн[1]) + (".Form.%s" % отн[3] if len(отн) > 5 and отн[2] == "Forms" else "")
        страница = понизить(тело(путь), 1)
        пункты.append((ак, заголовок(страница)))
        прочие.append('<div id="%s">%s</div>' % (html.escape(ак), страница))
        взято.add(путь)
    if прочие:
        главы.append(("прочие", "Прочие формы", "<h1>Прочие формы</h1>\n" + "\n".join(прочие), пункты))
    справок_подсистем = sum(1 for п, _, ф in os.walk(корень_подсистем) if "ru.html" in ф)
    return главы, len(взято) + справок_подсистем


def ссылки(текст, якоря):
    """href="Document.УЗ_Урок/Help" → переход внутри PDF; ссылки на то, чего нет в книжке, — просто текст."""
    def замена(м):
        цель = м.group(1)
        if цель in якоря:
            return 'href="#%s"' % html.escape(цель)
        return 'data-нет="%s"' % html.escape(цель)
    return re.sub(r'href="([^"#]+)/Help"', замена, текст)


def главный():
    for поток in (sys.stdout, sys.stderr):
        try:
            поток.reconfigure(encoding="utf-8")
        except Exception:
            pass
    н = time.time()
    главы, страниц = собрать()
    якоря = {г[0] for г in главы} | {п[0] for г in главы for п in г[3]}
    сегодня = datetime.date.today()
    дата = "%d %s %d" % (сегодня.day, МЕСЯЦЫ[сегодня.month - 1], сегодня.year)
    в = версия()

    оглавление = ['<div class="оглавление"><h2>Содержание</h2><ul>']
    for ак, заг, _, пункты in главы:
        оглавление.append('<li class="раздел"><a href="#%s">%s</a>' % (html.escape(ак), заг))
        if пункты:
            оглавление.append("<ul>" + "".join('<li><a href="#%s">%s</a></li>' % (html.escape(а), з)
                                                for а, з in пункты) + "</ul>")
        оглавление.append("</li>")
    оглавление.append("</ul></div>")

    части = []
    for ак, _, текст, _ in главы:
        части.append('<section id="%s">%s</section>' % (html.escape(ак), ссылки(текст, якоря)))
    титул = ('<div class="титул"><div class="имя">Учёт занятий 2.0</div>'
             '<div class="подзаголовок">Расширение для 1С:Управления нашей фирмой&nbsp;3.0, 1С:Бухгалтерии&nbsp;3.0 '
             'и 1С:Управления торговлей&nbsp;11.5</div>'
             '<div class="подзаголовок">Руководство пользователя</div>'
             '<div class="версия">Версия %s · %s</div></div>' % (в, дата))
    сноска = ('<div class="сноска">Руководство собрано из встроенной справки продукта версии %s (%s). В программе '
              'справка открывается клавишей F1 в любой форме и соответствует установленной версии. «1С», '
              '«1С:Предприятие» — товарные знаки ООО «1С»; «Учёт занятий» — разработка независимого автора.</div>'
              % (в, дата))
    страница = ('<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>Учёт занятий 2.0 — руководство '
                'пользователя</title>%s</head><body>%s%s%s%s</body></html>'
                % (СТИЛИ, титул, "".join(оглавление), "\n".join(части), сноска))
    os.makedirs(ПАПКА, exist_ok=True)
    with open(HTML, "w", encoding="utf-8") as ф:
        ф.write(страница)
    битых = len(re.findall(r"data-нет=", страница))
    print("страниц справки %d, глав %d, ссылок без цели %d; HTML %s (%.0f КБ)"
          % (страниц, len(главы), битых, HTML, os.path.getsize(HTML) / 1024))

    if ХРОМ is None:
        print("Chrome не найден — PDF собрать нечем")
        return 1
    if os.path.isfile(PDF):
        os.remove(PDF)
    subprocess.run([ХРОМ, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + PDF,
                    "file:///" + HTML.replace("\\", "/")], timeout=120, capture_output=True)
    if not os.path.isfile(PDF) or os.path.getsize(PDF) == 0:
        print("PDF не собрался")
        return 1
    with open(PDF, "rb") as ф:
        листов = len(re.findall(rb"/Type\s*/Page[^s]", ф.read()))
    print("PDF %s: %.0f КБ, листов %d, %.1f с" % (PDF, os.path.getsize(PDF) / 1024, листов, time.time() - н))
    return 0


if __name__ == "__main__":
    sys.exit(главный())
