"""Rebuild the icon delivery. Run with python -B; writes only to this directory tree."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, ImageFont
from draw import Canvas, S, T, Y, L
from schedule_money import ICONS as MONEY
from people import ICONS as PEOPLE
from common import ICONS as COMMON

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'_исходники'
ORDER='Урок Календарь Помощник Абонемент Заморозка Ученик Педагог Группа ПанельУченика Оплата Возврат Перемещение НачислениеУченику РасчетЗарплаты Выплата Бонусы Явка КОплате Напомнить Долг Переплата Выбыл Перевод Продлить ПечатьПКО Отчет Настройки Почта ДатаЗапрета Фото'.split()
BY_NAME={row['name']:row for row in MONEY+PEOPLE+COMMON}
ICONS=[BY_NAME['УЗ_И'+name] for name in ORDER]


def font(size,bold=False):
    filename='arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype(str(Path('C:/Windows/Fonts')/filename),size)


def text_center(draw,x,y,text,f,color=S):
    box=draw.textbbox((0,0),text,font=f)
    draw.text((int(x-(box[2]-box[0])/2),y),text,font=f,fill=color)


def make_sheet():
    width=1080; row_h=64; start_y=176
    sheet=Image.new('RGB',(width,start_y+len(ICONS)*row_h+54),'#FFFFFF')
    d=ImageDraw.Draw(sheet)
    d.rectangle((0,0,width,8),fill=T)
    d.text((28,26),'Учёт занятий · иконки интерфейса',font=font(29,True),fill=S)
    d.text((28,69),'30 сюжетов · 2 самостоятельных рисунка · прозрачные PNG',font=font(17),fill=S)
    d.text((28,100),'Размеры ниже — реальные пиксели. Смотрите лист в масштабе 100%.',font=font(15),fill=S)
    name_w=330; swatch_w=350
    for half,bg in enumerate(('#FFFFFF','#F2F4F5')):
        x=name_w+half*swatch_w
        d.rectangle((x,125,x+swatch_w-1,start_y+len(ICONS)*row_h),fill=bg)
        text_center(d,x+swatch_w/2,127,'Белый фон' if half==0 else 'Светло-серый фон',font(14,True))
        for index,label in enumerate(('М 16','М 20','М 32','Б 32','Б 48')):
            text_center(d,x+35+index*70,151,label,font(12))
    for index,row in enumerate(ICONS):
        y=start_y+index*row_h
        d.line((24,y,width-24,y),fill='#E3E8EB',width=1)
        d.text((28,y+10),f'{index+1:02d}  {row["label"]}',font=font(16,True),fill=S)
        d.text((57,y+34),row['name'],font=font(12),fill='#657582')
        for half in range(2):
            for col,(suffix,size) in enumerate(((16,16),(16,20),(16,32),(48,32),(48,48))):
                im=Image.open(ROOT/f'{row["name"]}_{suffix}.png').convert('RGBA')
                im=im.resize((size,size),Image.Resampling.LANCZOS)
                x=name_w+half*swatch_w+35+col*70
                sheet.paste(im,(x-size//2,y+(row_h-size)//2),im)
    d.text((28,sheet.height-36),'М — рисунок для 16 px; Б — рисунок для 32–48 px. Красный используется только у долга.',font=font(14),fill=S)
    sheet.save(ROOT/'_лист.png',optimize=True)
    qa=SOURCE/'проверка'; qa.mkdir(exist_ok=True)
    for part in range(3):
        top=start_y+part*10*row_h
        block=Image.new('RGB',(width,10*row_h+176),'white')
        block.paste(sheet.crop((0,0,width,176)),(0,0))
        block.paste(sheet.crop((0,top,width,top+10*row_h)),(0,176))
        block.save(qa/f'малые_{part+1}.png',optimize=True)
    large=Image.new('RGB',(6*184,5*184+64),'#F2F4F5')
    ld=ImageDraw.Draw(large)
    ld.text((24,18),'Крупные исходники · обзор геометрии',font=font(22,True),fill=S)
    for index,row in enumerate(ICONS):
        x=(index%6)*184; y=64+(index//6)*184
        im=Image.open(ROOT/f'{row["name"]}_48.png').resize((128,128),Image.Resampling.LANCZOS)
        large.paste(im,(x+28,y+5),im)
        text_center(ld,x+92,y+145,row['label'],font(13))
    large.save(qa/'крупные.png',optimize=True)


def make_description():
    lines=[
        '# Иконки интерфейса «Учёт занятий»',
        '',
        'Готово: **30 сюжетов, 60 PNG с прозрачным фоном**. Палитра: бирюзовый `#1E9E8F`, тёмно-сланцевый `#34495E`, жёлтый `#F5B642`, светлый `#E9F5F3`. Красный `#C94E48` используется только для минуса задолженности. Внутри иконок нет текста или цифр.',
        '',
        '- `Имя_16.png` — **64×64**, отдельная упрощённая геометрия для 16 px, также просмотрена в 20 и 32 px.',
        '- `Имя_48.png` — **256×256**, более подробная геометрия для показа в 32–48 px.',
        '- `_лист.png` — все 30 пар на белом `#FFFFFF` и сером `#F2F4F5` фоне: малая в 16, 20, 32 px; большая в 32, 48 px. Просматривать при **100%**.',
        '- `_исходники/svg/` — **60 отдельных SVG**, включая самостоятельный исходник каждой малой иконки. Все исходники лежат внутри разрешённой папки.',
        '',
        'Назначение — кнопки действий, вкладки, колонки состояния и команды навигации/функций. У обычных подписей полей декоративные значки не ставить. У действий с неоднозначной бизнес-семантикой сохранять подпись; у состояния в колонке — всплывающую подсказку.',
        '',
        '| Имя | Что изображено | Где ставить (кнопка/вкладка/колонка/команда) |',
        '|---|---|---|',
    ]
    for row in ICONS:
        lines.append(f'| `{row["name"]}` | {row["description"]} | {row["usage"]} |')
    lines += [
        '',
        '## Где нужна подпись или подсказка',
        '',
        '| Иконка | Ограничение смысла без подписи |',
        '|---|---|',
        '| `УЗ_ИКОплате` | Монета с галочкой может читаться как «уже оплачено». Использовать подпись «К оплате» / «Отметить к оплате». |',
        '| `УЗ_ИПереплата` | Плюс означает положительный остаток, но не различает аванс и переплату. Нужна подсказка с названием состояния. |',
        '| `УЗ_ИВыбыл` | Человек с крестом может читаться как удаление. Подпись «Выбыл» / «Отметить выбытие» обязательна. |',
        '| `УЗ_ИПродлить` | Календарь со стрелкой может означать переход к следующему периоду. Нужна подпись «Продлить расписание». |',
        '| `УЗ_ИПечатьПКО` | В 16 px надёжно видна печать, но вид документа невозможно передать без мелких деталей. Ставить у команды «Печать ПКО». |',
        '| `УЗ_ИПедагог` | Видно человека у доски, но его роль уточняет подпись «Педагог». |',
        '',
        'У «Оплата» стрелка направлена к монете, у «Возврат» — от неё. «Выплата» использует прямоугольную купюру, поэтому не совпадает силуэтом с возвратом. «Абонемент» отличают билетные вырезы, «Бонусы» — карта со звездой. Коробка отличает начисление материалов от положительного денежного остатка.',
        '',
        '## Исходники и проверка',
        '',
        'Фигуры нарисованы геометрически; PNG экспортированы со сглаживанием и RGBA-каналом, без тени и внешней подложки. Светлый цвет используется внутри предметов и для разделения пересекающихся форм. Малые версии нарисованы на сетке 16×16, большие — на отдельной сетке 32×32.',
        '',
        'Повторная сборка из корня проекта (Python + Pillow; вывод только в эту папку):',
        '',
        '```powershell',
        'python -B "docs/макеты-ui/иконки/_исходники/build.py"',
        '```',
        '',
        'Контрольные фрагменты листа в натуральном размере: `_исходники/проверка/малые_1.png`, `малые_2.png`, `малые_3.png`. Обзор крупной геометрии: `_исходники/проверка/крупные.png`. Технические результаты экспорта: `_исходники/проверка/результаты.json`.',
        '',
        'Проверены состав набора, размеры, альфа-канал, поля по краям и отсутствие повторов. Читаемость оценена визуально по уменьшениям PNG. Это проверка макетов, без загрузки в конфигурацию и без проверки рендеринга в живом клиенте 1С.',
        '',
    ]
    (ROOT/'_описание.md').write_text('\n'.join(lines),encoding='utf-8')


def validate():
    rows=[]; hashes=set(); warnings=[]
    for row in ICONS:
        for suffix,size in ((16,64),(48,256)):
            path=ROOT/f'{row["name"]}_{suffix}.png'
            im=Image.open(path)
            assert im.size==(size,size),path.name
            assert im.mode=='RGBA',path.name
            alpha=im.getchannel('A')
            assert alpha.getextrema()==(0,255),path.name
            mask=alpha.point(lambda value:255 if value>24 else 0)
            bbox=mask.getbbox()
            assert bbox is not None,path.name
            assert all(alpha.getpixel(point)==0 for point in ((0,0),(size-1,0),(0,size-1),(size-1,size-1))),path.name
            digest=hashlib.sha256(im.tobytes()).hexdigest()
            assert digest not in hashes,path.name
            hashes.add(digest)
            edge=min(bbox[0],bbox[1],size-bbox[2],size-bbox[3])
            if edge==0:
                warnings.append(path.name+': shape reaches raster edge')
            rows.append(dict(file=path.name,size=size,mode=im.mode,alpha_bbox_gt24=bbox,clear_edge_px=edge,sha256=digest))
    report=dict(icon_names=len(ICONS),png_count=len(rows),svg_count=len(list((SOURCE/'svg').glob('*.svg'))),all_unique=True,warnings=warnings,files=rows)
    (SOURCE/'проверка'/'результаты.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='files'},ensure_ascii=False))


def main():
    assert len(ICONS)==30 and len(BY_NAME)==30
    svg_dir=SOURCE/'svg'; svg_dir.mkdir(exist_ok=True)
    for row in ICONS:
        for key,grid,suffix,pixels in (('small',16,16,64),('large',32,48,256)):
            canvas=Canvas(grid)
            row[key](canvas)
            canvas.save(svg_dir/f'{row["name"]}_{suffix}.svg',ROOT/f'{row["name"]}_{suffix}.png',pixels)
    make_sheet()
    make_description()
    validate()


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
