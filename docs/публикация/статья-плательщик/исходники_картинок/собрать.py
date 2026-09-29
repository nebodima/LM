# -*- coding: utf-8 -*-
"""Иллюстрации к статье «Платит бабушка, учится внук»: HTML → PNG headless Chrome."""
import os
import subprocess

ПАПКА = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # картинки кладём рядом со статьёй
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1024px;background:#f4f6f9;font-family:"Segoe UI",Arial,sans-serif;color:#1f2d3d}
.wrap{padding:34px 44px 26px}
h1{font-size:30px;color:#1f3a5f;text-align:center;font-weight:700}
.sub{text-align:center;color:#6b7785;font-size:16px;margin-top:6px}
.bar{width:210px;height:3px;background:#1f3a5f;margin:12px auto 26px;border-radius:2px}
.foot{text-align:center;color:#8a95a3;font-size:12.5px;margin-top:22px}
.card{background:#fff;border:1.5px solid #c9d3df;border-radius:10px;padding:16px 18px}
.g{border-color:#8cc59a;background:#eef8f0}.g b.t{color:#2e7d45}
.r{border-color:#e5a3a3;background:#fcf0f0}.r b.t{color:#b23b3b}
.o{border-color:#efc27f;background:#fdf5e8}.o b.t{color:#b86e12}
.b{border-color:#9db7d6;background:#edf3fa}.b b.t{color:#1f3a5f}
b.t{display:block;font-size:19px;margin-bottom:6px}
.txt{font-size:15px;line-height:1.4;color:#34465a}
.num{display:inline-flex;width:34px;height:34px;border-radius:50%;background:#1f3a5f;color:#fff;
     align-items:center;justify-content:center;font-weight:700;font-size:17px;margin-right:12px;flex:none}
.row{display:flex;gap:18px;align-items:stretch}
.ic{font-size:34px;margin-right:12px;flex:none;line-height:1}
.flex{display:flex;align-items:flex-start}
.arrow{color:#6b7785;font-size:26px;align-self:center}
.big{font-size:40px;font-weight:700;color:#1f3a5f}
.strike{text-decoration:line-through;color:#b23b3b}
"""


def страница(тело):
    return "<!DOCTYPE html><html><head><meta charset='utf-8'><style>%s</style></head><body><div class='wrap'>%s</div></body></html>" % (CSS, тело)


КАРТИНКИ = {}

# 1. Кто получит вычет
КАРТИНКИ["01_кто_получит_вычет"] = (strap := страница("""
<h1>Кто получит вычет за кружок</h1><div class='sub'>Платит бабушка от души — налоговая считает по документам</div><div class='bar'></div>
<div class='row'>
 <div class='card g' style='flex:1'><b class='t'>Вычет есть</b><div class='txt'>
  <div class='flex' style='margin:8px 0'><span class='ic'>👩</span><div><b>Родитель</b> — за ребёнка до 24 лет, очно</div></div>
  <div class='flex' style='margin:8px 0'><span class='ic'>🛡️</span><div><b>Опекун, попечитель</b> — в том числе бабушка, если оформлена</div></div>
  <div class='flex' style='margin:8px 0'><span class='ic'>🧑</span><div><b>Брат или сестра</b> — за младших до 24 лет</div></div>
  <div class='flex' style='margin:8px 0'><span class='ic'>💍</span><div><b>Супруг</b> — за обучение мужа или жены</div></div>
 </div></div>
 <div class='card r' style='flex:1'><b class='t'>Вычета нет</b><div class='txt'>
  <div class='flex' style='margin:8px 0'><span class='ic'>👵</span><div><b>Бабушка и дедушка</b> без опекунства — их нет в перечне</div></div>
  <div class='flex' style='margin:8px 0'><span class='ic'>🤷</span><div><b>Мама, если платила бабушка</b> — у мамы нет расходов</div></div>
  <div class='flex' style='margin:8px 0'><span class='ic'>📄</span><div><b>Кружок без лицензии</b> и самозанятый без ИП — справку не на что выдать</div></div>
 </div></div>
</div>
<div class='card b' style='margin-top:18px'><div class='flex'><span class='ic'>💡</span><div class='txt'><b>Совет семьям:</b> бабушка передаёт деньги маме, платит мама. Внук ходит на робототехнику, вычет не пропадает, бабушка всё равно любимая.</div></div></div>
<div class='foot'>НК РФ, ст. 219, подп. 2 п. 1 · лимит 110 000 руб. в год на ребёнка на обоих родителей</div>
"""))

# 2. Четыре правила справки
КАРТИНКИ["02_справка_четыре_правила"] = страница("""
<h1>Справка для вычета: четыре правила</h1><div class='sub'>С расходов 2024 года вместо договора, лицензии и чеков — одна справка КНД 1151158</div><div class='bar'></div>
<div class='row'>
 <div class='card b' style='flex:1'><div class='flex'><span class='num'>1</span><div><b class='t'>Тому, кто платил</b><div class='txt'>Или его супругу, по заявлению. Не «родителю из карточки ученика».</div></div></div></div>
 <div class='card b' style='flex:1'><div class='flex'><span class='num'>2</span><div><b class='t'>На каждого ребёнка</b><div class='txt'>Двое детей в одном центре — две справки, у каждого свой лимит.</div></div></div></div>
</div>
<div class='row' style='margin-top:18px'>
 <div class='card b' style='flex:1'><div class='flex'><span class='num'>3</span><div><b class='t'>За каждый год</b><div class='txt'>По году оплаты, не по учебному. Декабрьская предоплата за январь — в декабрьском году.</div></div></div></div>
 <div class='card o' style='flex:1'><div class='flex'><span class='num'>4</span><div><b class='t'>Исправлять нельзя</b><div class='txt'>Ошиблись или вернули деньги — корректирующая справка. Замазка не поможет.</div></div></div></div>
</div>
<div class='foot'>Приказ ФНС России от 18.10.2023 № ЕД-7-11/755@, порядок заполнения, пп. 2–5, 9</div>
""")

# 3. Один платёж на двоих
КАРТИНКИ["03_один_платеж_на_двоих"] = страница("""
<h1>Один платёж — двое детей</h1><div class='sub'>Маме удобно одним переводом, налоговой нужно по каждому ребёнку</div><div class='bar'></div>
<div class='row'>
 <div class='card b' style='flex:1;text-align:center'><div class='ic' style='margin:0 0 6px'>💳</div><div class='big'>12 000 ₽</div><div class='txt'>мама, один перевод по СБП</div></div>
 <div class='arrow'>➜</div>
 <div style='flex:1.4;display:flex;flex-direction:column;gap:12px'>
  <div class='card g'><div class='flex'><span class='ic'>🤖</span><div><b class='t'>Сын — 7 000 ₽</b><div class='txt'>робототехника · справка № 1</div></div></div></div>
  <div class='card g'><div class='flex'><span class='ic'>🎸</span><div><b class='t'>Дочь — 5 000 ₽</b><div class='txt'>рок-школа · справка № 2</div></div></div></div>
 </div>
</div>
<div class='card r' style='margin-top:18px'><div class='flex'><span class='ic'>⚠️</span><div class='txt'><b>Не разнесли по детям</b> — в январе администратор угадывает, чья гитара стоила сколько. А справку исправлять нельзя.</div></div></div>
<div class='foot'>Порядок заполнения справки КНД 1151158, п. 3: справка оформляется на каждого обучаемого</div>
""")

# 4. Чек за абонемент
КАРТИНКИ["04_чек_за_абонемент"] = страница("""
<h1>Чек за абонемент</h1><div class='sub'>Абонемент купили заранее — это предоплата, а не «просто оплата»</div><div class='bar'></div>
<div class='row'>
 <div class='card b' style='flex:1'><div class='flex'><span class='num'>1</span><div><b class='t'>Оплатили абонемент</b><div class='txt'>Признак на чеке:<br><b>ПРЕДОПЛАТА 100%</b><br>Оплатили часть — <b>ПРЕДОПЛАТА</b></div></div></div></div>
 <div class='arrow'>➜</div>
 <div class='card b' style='flex:1'><div class='flex'><span class='num'>2</span><div><b class='t'>Провели занятия</b><div class='txt'>Зачёт аванса:<br><b>ПОЛНЫЙ РАСЧЕТ</b></div></div></div></div>
</div>
<div class='row' style='margin-top:18px'>
 <div class='card g' style='flex:1'><div class='flex'><span class='ic'>🙂</span><div><b class='t'>ФИО родителя не нужно</b><div class='txt'>Покупатель в чеке обязателен только между организациями и ИП.</div></div></div></div>
 <div class='card o' style='flex:1'><div class='flex'><span class='ic'>📱</span><div><b class='t'>QR и СБП — тоже чек</b><div class='txt'>Перевод по QR-коду — расчёт электронным средством платежа. Чек на бумаге или на телефон.</div></div></div></div>
</div>
<div class='foot'>Приказ ФНС России от 14.09.2020 № ЕД-7-20/662@, признак способа расчёта (тег 1214)</div>
""")

# 5. Возврат при отказе
КАРТИНКИ["05_возврат_при_отказе"] = страница("""
<h1>Ребёнок бросил: сколько вернуть</h1><div class='sub'>Абонемент на 8 занятий, сходил на 3, потом решил стать блогером</div><div class='bar'></div>
<div class='row'>
 <div class='card b' style='flex:1;text-align:center'><div class='txt'>Оплачено</div><div class='big'>8 000 ₽</div><div class='txt'>8 занятий по 1 000</div></div>
 <div class='arrow'>−</div>
 <div class='card b' style='flex:1;text-align:center'><div class='txt'>Проведено</div><div class='big'>3 000 ₽</div><div class='txt'>3 занятия</div></div>
 <div class='arrow'>−</div>
 <div class='card b' style='flex:1;text-align:center'><div class='txt'>Фактические расходы</div><div class='big'>?</div><div class='txt'>если они есть и подтверждены</div></div>
</div>
<div class='row' style='margin-top:18px'>
 <div class='card g' style='flex:1'><b class='t'>Можно удержать</b><div class='txt'>Проведённые занятия и фактически понесённые расходы.</div></div>
 <div class='card r' style='flex:1'><b class='t'>Нельзя удержать</b><div class='txt'><span class='strike'>«Штраф за отказ»</span>, <span class='strike'>«абонемент сгорает»</span>, <span class='strike'>«так написано в правилах клуба»</span>.</div></div>
</div>
<div class='card o' style='margin-top:18px'><div class='flex'><span class='ic'>🤒</span><div class='txt'><b>Пропуск по болезни</b> закон не решает: перенос, заморозка или возврат — это ваш договор. Запишите заранее, чтобы не договариваться с каждой мамой отдельно.</div></div></div>
<div class='foot'>Закон «О защите прав потребителей», ст. 32 · ГК РФ, ст. 782 — для кружков без лицензии</div>
""")

for имя, html in КАРТИНКИ.items():
    путь_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), имя + ".html")
    with open(путь_html, "w", encoding="utf-8") as ф:
        ф.write(html)
    png = os.path.join(ПАПКА, имя + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1024,640",
                    "--screenshot=" + png, "file:///" + путь_html.replace("\\", "/")],
                   capture_output=True, timeout=60)
    #обрезаем пустой низ: окно Chrome выше содержимого
    from PIL import Image, ImageChops
    картинка = Image.open(png).convert("RGB")
    фон = Image.new("RGB", картинка.size, картинка.getpixel((5, картинка.height - 2)))
    низ = ImageChops.difference(картинка, фон).getbbox()[3]
    картинка.crop((0, 0, картинка.width, min(картинка.height, низ + 28))).save(png)
    print(имя, картинка.width, min(картинка.height, низ + 28))
