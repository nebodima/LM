"""Снимки веб-клиента «Учёта занятий» для карточки Инфостарта и видео — без окна (headless Chrome).

    python tools\\демо\\снимки.py                  весь набор → docs\\публикация\\снимки\\NN_название.png
    python tools\\демо\\снимки.py урок календарь   только эти кадры (ключи — из КАДРЫ ниже)
    python tools\\демо\\снимки.py --разведка e1cib/list/Документ.УЗ_Урок   открыть ссылку, снять кадр в TEMP
                                                   и напечатать id видимых элементов формы
    python tools\\демо\\снимки.py справка_вычет договор --видео   кадры на стенде видео (tools\\видео\\стенд.py
                                                   --старт: UZ_VIDEO, http://127.0.0.1:8111/uzv/) — там
                                                   справка об оплате обучения и договор (этап 2.1, часть 2)

Стенд: база C:\\1c_bases\\UZ_DEMO (демо-данные — tools\\демо\\наполнить.py), своя публикация
http://127.0.0.1:8100/uz/ (C:\\1c_bases\\веб\\httpd_DEMO.conf; запуск
C:\\1c_bases\\web_uz\\bin\\httpd_uz.exe -f C:\\1c_bases\\веб\\httpd_DEMO.conf). Вход — пользователем из default.vrd.

Управление — протоколом отладки Chrome (Page/Input/Runtime по вебсокету), как в
PUTEVYE_LISTY\\tools\\scripts\\снимки_справки.py. Элементы — по id веб-клиента (formN_Имя), не по точкам.
Каждый кадр — свежая загрузка клиента по навигационной ссылке (смена якоря роутер не будит).
Формы документов и справочников сначала открываются другим объектом (прогрев): первое открытие формы
в сеансе раскладывает подписи без общей вертикали.
"""
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

import websocket

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "тесты"))
from сеанс import настроить_вывод  # noqa: E402

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
СНИМКИ = os.path.join(КОРЕНЬ, "docs", "публикация", "снимки")
СТЕНД = "http://127.0.0.1:8100/uz/ru_RU/"
БАЗА = r"C:\1c_bases\UZ_DEMO"
ШИРИНА, ВЫСОТА = 1280, 768
АНОНС = (1200, 900)
ХРОМ = next((п for п in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") if os.path.isfile(п)), None)
ОКНА_ОШИБОК = ("Не удалось перейти по навигационной ссылке", "непредвиденная ошибка", "Ошибка при вызове",
               "Неверный формат навигационной ссылки", "Поле объекта не обнаружено", "Ошибка выполнения")


def свободный_порт():
    for порт in range(9500, 9600):
        с = socket.socket()
        try:
            с.bind(("127.0.0.1", порт))
            return порт
        except OSError:
            continue
        finally:
            с.close()
    raise RuntimeError("свободного порта для отладки не нашлось")


class Браузер:
    def __init__(self, ширина=ШИРИНА, высота=ВЫСОТА):
        if ХРОМ is None:
            raise RuntimeError("Chrome не найден")
        self.порт = свободный_порт()
        self.профиль = os.path.join(os.environ.get("TEMP", "."), "chrome-уз-демо-%d" % self.порт)
        self.процесс = subprocess.Popen([
            ХРОМ, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", "--remote-debugging-port=%d" % self.порт, "--remote-allow-origins=*",
            "--user-data-dir=%s" % self.профиль, "--window-size=%d,%d" % (ширина, высота),
            "--force-device-scale-factor=1", "--lang=ru-RU"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.счётчик = 0
        self.ws = self._подключиться()
        self._команда("Page.enable")
        self._команда("Runtime.enable")
        self.размер(ширина, высота)

    def _цели(self):
        return json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % self.порт, timeout=2).read())

    def _подключиться(self, адрес=None):
        for _ in range(80):
            try:
                if адрес is None:
                    страницы = [ц for ц in self._цели() if ц.get("type") == "page"]
                    if not страницы:
                        raise RuntimeError("нет страниц")
                    адрес = страницы[0]["webSocketDebuggerUrl"]
                return websocket.create_connection(адрес, timeout=180)
            except Exception:
                time.sleep(0.5)
        raise RuntimeError("браузер молчит на порту %d" % self.порт)

    def _команда(self, метод, ws=None, **параметры):
        ws = ws or self.ws
        self.счётчик += 1
        ws.send(json.dumps({"id": self.счётчик, "method": метод, "params": параметры}))
        моя = self.счётчик
        while True:
            ответ = json.loads(ws.recv())
            if ответ.get("method") == "Page.javascriptDialogOpening":
                # «Покинуть сайт?» веб-клиента при уходе со страницы — соглашаемся (данные не меняем)
                self.счётчик += 1
                ws.send(json.dumps({"id": self.счётчик, "method": "Page.handleJavaScriptDialog",
                                    "params": {"accept": True}}))
                continue
            if ответ.get("id") == моя:
                if "error" in ответ:
                    raise RuntimeError("%s: %s" % (метод, ответ["error"]))
                return ответ.get("result", {})

    def размер(self, ширина, высота):
        self._команда("Emulation.setDeviceMetricsOverride", width=ширина, height=высота, deviceScaleFactor=1,
                      mobile=False)
        self.ширина, self.высота = ширина, высота

    def js(self, выражение, ws=None):
        ответ = self._команда("Runtime.evaluate", ws=ws, expression=выражение, returnByValue=True)
        return ответ.get("result", {}).get("value")

    def открыть(self, ссылка="", ждать=25):
        """Свежая загрузка клиента; ждём, пока пропадёт заставка и появится хоть одна форма."""
        адрес = СТЕНД + ("#" + ссылка if ссылка else "")
        self._команда("Page.navigate", url="about:blank")
        time.sleep(0.5)
        self._команда("Page.navigate", url=адрес)
        срок = time.time() + ждать + 40
        time.sleep(8)
        while time.time() < срок:
            if self.js("document.querySelectorAll('[id$=\"_$scrl\"], .themesCell, [id^=\"themesCell\"]').length") :
                break
            time.sleep(1)
        time.sleep(4)
        self.закрыть_окна_платформы()

    def закрыть_окна_платформы(self):
        """Окно «Информационная база перемещена» — кнопкой «Это копия информационной базы»; всплывающие
        оповещения («Оповещений: 4») — их крестиком: иначе они закрывают правый нижний угол формы."""
        if self.клик_по_тексту("Это копия информационной базы", ждать=4) == "ок":
            print("   (закрыто окно «база перемещена»)")
        self.закрыть_оповещения()

    def закрыть_оповещения(self):
        for _ in range(5):
            м = self.js("""(function(){var к=document.querySelectorAll('#notificationArea .notificationClose');
                for(var i=0;i<к.length;i++){var r=к[i].getBoundingClientRect(); if(r.width>0) return [r.left+12,r.top+12];}
                return null;})()""")
            if not м:
                return
            self.клик(м[0], м[1], ждать=1)

    def ждать(self, сек):
        time.sleep(сек)

    def клик(self, x, y, ждать=2, двойной=False):
        for тип in ("mouseMoved", "mousePressed", "mouseReleased"):
            self._команда("Input.dispatchMouseEvent", type=тип, x=x, y=y, button="left", clickCount=1)
        if двойной:
            for тип in ("mousePressed", "mouseReleased"):
                self._команда("Input.dispatchMouseEvent", type=тип, x=x, y=y, button="left", clickCount=2)
        time.sleep(ждать)

    def место(self, ид):
        return self.js("""(function(){var p=document.getElementById(%s); if(!p) return null;
            var r=p.getBoundingClientRect(); if(r.width<1) return null; return [r.left,r.top,r.width,r.height];})()"""
                       % json.dumps(ид, ensure_ascii=False))

    def клик_элемент(self, ид, ждать=3, двойной=False):
        м = self.место(ид)
        if not м:
            return "нет"
        self.клик(м[0] + min(12, м[2] / 2), м[1] + min(10, м[3] / 2), ждать, двойной)
        return "ок"

    def найти_текст(self, текст, область=""):
        """[x, y] самого глубокого видимого элемента с таким текстом (пробелы нормализуются)."""
        return self.js("""(function(){
            var все=document.querySelectorAll(%s), найден=null, нужно=%s;
            for (var i=0;i<все.length;i++){ var p=все[i];
              var т=(p.textContent||'').replace(/[\\s\\u00a0]+/g,' ').trim();
              var r=p.getBoundingClientRect();
              if (т===нужно && r.width>0 && r.height>0 && r.top>=0 && r.top<innerHeight) найден=p;}
            if(!найден) return null; var r=найден.getBoundingClientRect();
            return [r.left+Math.min(10,r.width/2), r.top+Math.min(8,r.height/2)];})()"""
                       % (json.dumps((область + " " if область else "") + "div,span,a,td,button", ensure_ascii=False),
                          json.dumps(текст, ensure_ascii=False)))

    def клик_по_тексту(self, текст, ждать=3, двойной=False):
        м = self.найти_текст(текст)
        if not м:
            return "нет"
        self.клик(м[0], м[1], ждать, двойной)
        return "ок"

    def клавиша(self, ключ, код, ждать=1, модификаторы=0, текст=None):
        for тип in ("keyDown", "keyUp"):
            п = dict(type=тип, key=ключ, code=ключ, windowsVirtualKeyCode=код, nativeVirtualKeyCode=код,
                     modifiers=модификаторы)
            if текст and тип == "keyDown":
                п["text"] = текст
            self._команда("Input.dispatchKeyEvent", **п)
        time.sleep(ждать)

    def ввести(self, текст, ждать=1):
        self._команда("Input.insertText", text=текст)
        time.sleep(ждать)

    def выбрать_в_поле(self, текст):
        """Поле ссылочного типа: ввести начало наименования и выбрать строку из выпадающего списка подбора
        (Tab после набора оставляет в поле просто текст, и поле очищается)."""
        # посимвольно: подбор по вводу веб-клиент запускает по событиям клавиатуры, Input.insertText его не будит
        for символ in текст:
            self._команда("Input.dispatchKeyEvent", type="keyDown", key=символ, text=символ, unmodifiedText=символ)
            self._команда("Input.dispatchKeyEvent", type="keyUp", key=символ)
            time.sleep(0.05)
        time.sleep(3)
        self.клавиша("ArrowDown", 40, ждать=1)
        self.клавиша("Enter", 13, ждать=5, текст="\r")

    def номер_формы(self):
        n = self.js(r"""(function(){var n=-1; document.querySelectorAll('[id^="form"]').forEach(function(e){
            var m=e.id.match(/^form(\d+)_/); if(!m) return; var r=e.getBoundingClientRect();
            if(r.width<10||r.height<10) return; if(+m[1]>n) n=+m[1];}); return n;})()""")
        return 0 if n is None or n < 0 else n

    def ид_формы(self, n):
        return self.js(r"""(function(){var итог=[]; document.querySelectorAll('[id^="form%d_"]').forEach(function(e){
            var r=e.getBoundingClientRect(); if(r.width>0&&r.height>0) итог.push(e.id);}); return итог;})()""" % n) or []

    def окно_ошибки(self):
        return self.js("""(function(){var найдено=[], фразы=%s;
            function обойти(д){try{var т=д.documentElement?д.documentElement.textContent:'';
              фразы.forEach(function(ф){if(т.indexOf(ф)>=0&&найдено.indexOf(ф)<0)найдено.push(ф);});
              д.querySelectorAll('iframe').forEach(function(р){try{обойти(р.contentDocument);}catch(е){}});}catch(е){}}
            обойти(document); return найдено.join(' | ');})()""" % json.dumps(list(ОКНА_ОШИБОК), ensure_ascii=False)) or ""

    def снять(self, путь, ws=None):
        итог = self._команда("Page.captureScreenshot", ws=ws, format="png", captureBeyondViewport=False)
        with open(путь, "wb") as ф:
            ф.write(base64.b64decode(итог["data"]))
        return путь

    def закрыть(self):
        try:
            self._команда("Page.navigate", url="about:blank")   # веб-клиент закрывает свой сеанс при уходе со страницы
            time.sleep(2)
            self.ws.close()
        except Exception:
            pass
        self.процесс.terminate()
        try:
            self.процесс.wait(timeout=10)
        except Exception:
            self.процесс.kill()


def ссылки():
    """Навигационные ссылки демо-объектов: ссылки строятся по тем же постоянным идентификаторам, что
    в наполнить.py (uuid5 от ключа), навигационную ссылку отдаёт сама 1С (байты id в ней переставлены)."""
    import uuid
    import win32com.client
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from наполнить import НАЧАЛО, ПРОСТРАНСТВО, СЕГОДНЯ
    c = win32com.client.Dispatch("V83.COMConnector").Connect('File="%s";Usr="Администратор";' % БАЗА)

    def ссылка(менеджер, вид, ключ):
        ид = uuid.uuid5(ПРОСТРАНСТВО, "%s/%s" % (вид, ключ))
        return менеджер.ПолучитьСсылку(c.NewObject("УникальныйИдентификатор", str(ид)))

    def нав(с):
        return c.String(c.ПолучитьНавигационнуюСсылку(с))

    def урок(группа, сдвиг_недель, день_недели, час, минута):
        """Урок группы: день недели (0 — пн) прошлой недели (сдвиг 1) или позапрошлой (2)."""
        import datetime
        пн = СЕГОДНЯ - datetime.timedelta(days=СЕГОДНЯ.weekday() + 7 * сдвиг_недель)
        д = пн + datetime.timedelta(days=день_недели)
        return нав(ссылка(c.Документы.УЗ_Урок, "УЗ_Урок", "%s/%s%02d%02d" % (группа, д.strftime("%Y%m%d"), час, минута)))

    итог = {
        "урок": урок("вокал_дети", 1, 3, 18, 30),
        "урок_прогрев": урок("гитара1", 1, 1, 17, 0),
        "абонемент": нав(ссылка(c.Справочники.УЗ_Абонемент, "УЗ_Абонемент", "у9/вокал_дети/2")),
        "абонемент_прогрев": нав(ссылка(c.Справочники.УЗ_Абонемент, "УЗ_Абонемент", "у3/вокал_дети/1")),
        "расчет": нав(ссылка(c.Документы.УЗ_РасчетЗарплаты, "УЗ_РасчетЗарплаты", "вокал/" + НАЧАЛО.strftime("%Y%m"))),
        "расчет_прогрев": нав(ссылка(c.Документы.УЗ_РасчетЗарплаты, "УЗ_РасчетЗарплаты", "гитара/" + НАЧАЛО.strftime("%Y%m"))),
        "ученик": c.String(ссылка(c.Справочники.УЗ_ФизЛица, "УЗ_ФизЛица", "ученик/у2")),
    }
    # ПКО: последняя оплата абонемента и предыдущая — для прогрева формы
    з = c.NewObject("Запрос")
    з.Текст = """ВЫБРАТЬ ПЕРВЫЕ 2 П.Ссылка КАК Ссылка ИЗ Документ.УЗ_ПриходДенег КАК П
        ГДЕ П.Проведен И НЕ П.Абонемент = ЗНАЧЕНИЕ(Справочник.УЗ_Абонемент.ПустаяСсылка)
        УПОРЯДОЧИТЬ ПО П.Дата УБЫВ"""
    в = з.Выполнить().Выбрать()
    в.Следующий()
    итог["пко"] = нав(в.Ссылка)
    в.Следующий()
    итог["пко_прогрев"] = нав(в.Ссылка)
    # справка на вычет и договор (этап 2.1, часть 2): первые в базе — на стенде видео их заводят руками/скриптом
    for ключ, вид in (("справка_вычет", "УЗ_СправкаОбОплатеОбучения"), ("договор", "УЗ_ДоговорОбучения")):
        з.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1 Д.Ссылка КАК Ссылка ИЗ Документ.%s КАК Д УПОРЯДОЧИТЬ ПО Д.Дата" % вид
        в = з.Выполнить().Выбрать()
        итог[ключ] = нав(в.Ссылка) if в.Следующий() else ""
    з.Текст = "ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Число ИЗ Документ.УЗ_Урок КАК У ГДЕ НЕ У.Проведен"
    в = з.Выполнить().Выбрать()
    в.Следующий()
    итог["уроков_плана"] = int(в.Число)
    return итог


def к_справка_вычет(б, сс):
    """Справка об оплате обучения (КНД 1151158): «Печать справки» → бланк налоговой по знакоместам."""
    б.открыть(сс["справка_вычет"])
    n = б.номер_формы()
    for попытка in range(3):   # форма после загрузки клиента иногда ещё не принимает нажатий — повтор
        if б.клик_элемент("form%d_ФормаПечатьСправки" % n, ждать=3) == "нет":   # кнопка «Печать справки» формы
            б.клик_по_тексту("Печать справки", ждать=3)
        try:
            ждать_текст(б, "Справка об оплате образовательных услуг", секунд=8)   # заголовок формы печати
            break
        except RuntimeError:
            if попытка == 2:
                raise
    б.закрыть_оповещения()


def к_договор(б, сс):
    """Договор обучения: «Печать» → договор об оказании платных образовательных услуг."""
    б.открыть(сс["договор"])
    n = б.номер_формы()
    открыть_печать(б, n, "Договор об оказании платных образовательных услуг")
    ждать_текст(б, "Договор обучения")   # заголовок формы печати
    б.закрыть_оповещения()


def открыть_печать(б, n, команда):
    """«Печать» → команда. Подменю — по id (formN_ПодменюПечать), нет — по надписи «Печать»; пункт — по надписи."""
    for попытка in range(3):
        if б.клик_элемент("form%d_ПодменюПечать" % n, ждать=2) == "нет":
            б.клик_по_тексту("Печать", ждать=2)
        if б.клик_по_тексту(команда, ждать=3) != "нет":
            return
    raise RuntimeError("не открылась команда печати «%s»" % команда)


def ждать_текст(б, текст, секунд=20, точно=True):
    """Печатная форма открывается в отдельной форме не сразу — кадр только после её текста на экране."""
    срок = time.time() + секунд
    while time.time() < срок:
        if б.найти_текст(текст) if точно else б.js("document.body.innerText.indexOf(%s) >= 0" % json.dumps(текст)):
            time.sleep(1.5)
            return
        time.sleep(0.5)
    raise RuntimeError("не дождался «%s»" % текст)


def разведка(ссылка):
    б = Браузер()
    try:
        if ссылка in ("урок", "абонемент", "расчет", "пко"):
            ссылка = ссылки()[ссылка]
            print("ссылка:", ссылка)
        б.открыть(ссылка)
        n = б.номер_формы()
        print("форма N =", n)
        print(" ".join(б.ид_формы(n)))
        путь = б.снять(os.path.join(os.environ.get("TEMP", "."), "уз_разведка.png"))
        print("кадр:", путь, "ошибка:", б.окно_ошибки())
    finally:
        б.закрыть()


# ── кадры ──
# каждая функция готовит экран и возвращает None (снимаем основную вкладку) или адрес вебсокета другой вкладки
# (справка F1 открывается отдельным окном браузера)

def к_раздел(б, сс):
    б.открыть("")
    # панель разделов длиннее окна: раздел прокручиваем в видимую часть, потом щёлкаем
    б.js("""(function(){var все=document.querySelectorAll('[id^="themesCell_theme_"]');
        for(var i=0;i<все.length;i++) if((все[i].textContent||'').trim()==='Учёт занятий'){все[i].scrollIntoView({block:'end'});return 1;}
        return 0;})()""")
    б.ждать(1)
    б.клик_по_тексту("Учёт занятий", ждать=6)
    б.закрыть_оповещения()


def к_журнал(б, сс):
    б.открыть("e1cib/list/Документ.УЗ_Урок")
    n = б.номер_формы()
    # первая строка списка — самый поздний урок плана; вниз на число уроков плана + 2 — прошедший урок с явками
    м = б.js(r"""(function(){var все=document.querySelectorAll('#form%d_Список div.gridBoxText, #form%d_Список div');
        for(var i=0;i<все.length;i++){var т=(все[i].textContent||'').trim(); var r=все[i].getBoundingClientRect();
          if(/^\d\d\.\d\d\.\d\d \d\d:\d\d$/.test(т) && r.width>0) return [r.left+10, r.top+8];} return null;})()""" % (n, n))
    if м:
        # список — по возрастанию даты, курсор на последнем уроке плана: вверх на число уроков плана + 2
        б.клик(м[0], м[1], ждать=2)
        for _ in range(сс["уроков_плана"] + 2):
            б.клавиша("ArrowUp", 38, ждать=0.4)
        б.ждать(4)
    б.закрыть_оповещения()


def к_урок(б, сс):
    б.открыть(сс["урок_прогрев"])
    б.открыть(сс["урок"])


def к_календарь(б, сс):
    б.открыть("e1cib/app/Обработка.УЗ_Календарь")
    n = б.номер_формы()
    # «Не отображать помещения» форма помнит между сеансами — щёлкаем, только если сетка разбита по помещениям
    if б.найти_текст("Барабанный класс", "#form%d_Планировщик" % n):
        б.клик_элемент("form%d_НеГруппироватьПомещения" % n, ждать=3)
    # часы сетки — с 12:00: утром в студии занятий нет
    б.клик_элемент("form%d_ВремяКалендаряС_i0" % n, ждать=1)
    б.клавиша("a", 65, ждать=0.5, модификаторы=2)
    for символ in "12":
        б._команда("Input.dispatchKeyEvent", type="keyDown", key=символ, text=символ)
        б._команда("Input.dispatchKeyEvent", type="keyUp", key=символ)
    б.клавиша("Tab", 9, ждать=3)
    б.клик_по_тексту("Неделя", ждать=6)
    б.клик_элемент("form%d_РазделительКартинка1" % n, ждать=4)   # спрятать левую панель — сетка шире
    б.закрыть_оповещения()


def к_помощник(б, сс):
    б.открыть("e1cib/list/Документ.УЗ_Урок")
    n = б.номер_формы()
    б.клик_элемент("form%d_ФормаПомощникСозданияУроков" % n, ждать=6)
    m = б.номер_формы()
    б.клик_элемент("form%d_ЗаполнятьИзГруппыОбучения" % m, ждать=2)
    б.клик_элемент("form%d_ГруппаОбучения_i0" % m, ждать=1)
    б.выбрать_в_поле("Гитара: начинающие")
    б.клик_по_тексту("Заполнить след. месяц", ждать=6)
    б.закрыть_оповещения()


def к_панель(б, сс):
    б.открыть("e1cib/app/Обработка.УЗ_ПанельУченика")
    n = б.номер_формы()
    б.клик_элемент("form%d_Ученик_i0" % n, ждать=1)
    б.выбрать_в_поле(сс["ученик"])
    б.клик_элемент("form%d_Обновить" % n, ждать=8)
    # раскрыть уроки первого предмета в нижнем списке
    м = б.js("""(function(){var с=document.getElementById('form%d_СписокУроков'); if(!с) return null;
        var все=с.querySelectorAll('div,span'); for(var i=0;i<все.length;i++){var т=(все[i].textContent||'').trim();
          var r=все[i].getBoundingClientRect(); if(т==='Гитара' && r.width>0) return [r.left+5,r.top+8];} return null;})()""" % n)
    if м:
        б.клик(м[0], м[1], ждать=1)
        б.клавиша("+", 107, ждать=4, текст="+")
        б.клавиша("ArrowDown", 40, ждать=1)
        б.клавиша("+", 107, ждать=4, текст="+")
    б.закрыть_оповещения()


def к_абонемент(б, сс):
    б.открыть(сс["абонемент_прогрев"])
    б.открыть(сс["абонемент"])
    # карточка справочника открывается плавающим окном поверх начальной страницы — разворачиваем (кнопка
    # «Развернуть»; развёрнутое окно платформа помнит, и тогда у кнопки подсказка «Восстановить» — не трогаем)
    б.js("""(function(){var к=document.querySelectorAll('[id$="_cmd_MaximizeButton"]');
        for(var i=к.length-1;i>=0;i--){var r=к[i].getBoundingClientRect(); if(r.width>0 && к[i].getAttribute('title')==='Развернуть'){
          ['mousedown','mouseup','click'].forEach(function(т){к[i].dispatchEvent(new MouseEvent(т,{bubbles:true,clientX:r.left+8,clientY:r.top+8}));});
          return 1;}} return 0;})()""")
    б.ждать(3)


def к_пко(б, сс):
    б.открыть(сс["пко_прогрев"])
    б.открыть(сс["пко"])


def к_расчет(б, сс):
    б.открыть(сс["расчет_прогрев"])
    б.открыть(сс["расчет"])


def отчет(б, ссылка, кнопка):
    б.открыть(ссылка)
    n = б.номер_формы()
    б.клик_элемент("form%d_%s" % (n, кнопка), ждать=12)
    б.закрыть_оповещения()


def к_взаиморасчеты(б, сс):
    отчет(б, "e1cib/app/Отчет.УЗ_Взаиморасчеты", "ФормаСформировать")


def к_аналитика(б, сс):
    отчет(б, "e1cib/app/Отчет.УЗ_АналитикаПоУченикам", "Сформировать")


def к_печать(б, сс):
    б.открыть(сс["пко"])
    n = б.номер_формы()
    б.клик_элемент("form%d_ПодменюПечать" % n, ждать=3)
    if б.клик_по_тексту("Приходный кассовый ордер", ждать=10) != "ок":
        б.клик_по_тексту("Приходный кассовый ордер (КО-1)", ждать=10)
    б.закрыть_оповещения()


def к_справка(б, сс):
    б.открыть(сс["урок"])
    было = {ц["id"] for ц in б._цели()}
    б.клавиша("F1", 112, ждать=10)
    новые = [ц for ц in б._цели() if ц["id"] not in было and ц.get("type") == "page"]
    if not новые:
        return None
    адрес = новые[0]["webSocketDebuggerUrl"]
    ws = б._подключиться(адрес)
    б._команда("Emulation.setDeviceMetricsOverride", ws=ws, width=б.ширина, height=б.высота, deviceScaleFactor=1,
               mobile=False)
    time.sleep(4)
    return ws


КАДРЫ = (
    ("раздел", "01_раздел_учёт_занятий", "Раздел «Учёт занятий» в панели разделов", к_раздел),
    ("журнал", "02_журнал_уроков", "Журнал уроков: ученики, явка и оплата выбранного урока", к_журнал),
    ("урок", "03_урок", "Урок: ученики, явка, оплата, абонементы", к_урок),
    ("календарь", "04_календарь_неделя", "Календарь на неделю", к_календарь),
    ("помощник", "05_помощник_создания_уроков", "Помощник создания уроков группы", к_помощник),
    ("панель", "06_панель_ученика", "Панель ученика", к_панель),
    ("абонемент", "07_абонемент_приостановка", "Абонемент с приостановкой", к_абонемент),
    ("пко", "08_приход_денег", "Приход денег (ПКО) по абонементу", к_пко),
    ("расчет", "09_расчёт_зарплаты", "Расчёт зарплаты педагога", к_расчет),
    ("взаиморасчеты", "10_отчёт_взаиморасчеты", "Отчёт «Взаиморасчеты»", к_взаиморасчеты),
    ("аналитика", "11_отчёт_аналитика_по_ученикам", "Отчёт «Аналитика по ученикам»", к_аналитика),
    ("печать", "12_печать_пко", "Печать приходного кассового ордера", к_печать),
    ("справка", "13_справка_f1_урока", "Справка F1 формы урока", к_справка),
    ("справка_вычет", "15_справка_вычет", "Справка об оплате обучения для налогового вычета (КНД 1151158)",
     к_справка_вычет),
    ("договор", "16_договор", "Договор об оказании платных образовательных услуг", к_договор),
)


def снять_кадр(б, сс, ключ, имя, подпись, функция, пусто):
    print("%-14s %s" % (ключ, подпись), flush=True)
    ws = None
    try:
        ws = функция(б, сс)
    except Exception as е:
        пусто.append("%s (сбой: %s)" % (имя, str(е)[:120]))
        print("   [!] сбой: %s" % str(е)[:200])
    путь = б.снять(os.path.join(СНИМКИ, имя + ".png"), ws=ws)
    ошибка = б.окно_ошибки() if ws is None else ""
    if ws is not None:
        ws.close()
    размер = os.path.getsize(путь) / 1024
    print("   снят %s  %.0f КБ" % (os.path.basename(путь), размер))
    if ошибка:
        пусто.append("%s (окно ошибки: %s)" % (имя, ошибка))
    elif размер < 30:
        пусто.append("%s (почти пустой экран)" % имя)


def анонс(сс, пусто):
    """Анонс Инфостарта: 4:3, не меньше 800×600 — календарь недели в окне 1200×900."""
    б = Браузер(*АНОНС)
    try:
        снять_кадр(б, сс, "анонс", "00_анонс", "Анонс 4:3 (1200×900): календарь на неделю", к_календарь, пусто)
    finally:
        б.закрыть()


def главная(заказ):
    os.makedirs(СНИМКИ, exist_ok=True)
    сс = ссылки()
    пусто = []
    б = Браузер()
    try:
        for ключ, имя, подпись, функция in КАДРЫ:
            if заказ and ключ not in заказ:
                continue
            снять_кадр(б, сс, ключ, имя, подпись, функция, пусто)
    finally:
        б.закрыть()
    if not заказ or "анонс" in заказ:
        анонс(сс, пусто)
    print("-" * 70)
    print("папка: %s" % СНИМКИ)
    if пусто:
        print("проверить глазами:", "; ".join(пусто))
        return 1
    return 0


if __name__ == "__main__":
    настроить_вывод()
    if "--видео" in sys.argv:   # стенд видео: копия демо UZ_VIDEO (tools\\видео\\стенд.py --старт)
        СТЕНД = "http://127.0.0.1:8111/uzv/ru_RU/"
        БАЗА = r"C:\1c_bases\UZ_VIDEO"
    if "--разведка" in sys.argv:
        разведка(sys.argv[sys.argv.index("--разведка") + 1] if len(sys.argv) > sys.argv.index("--разведка") + 1 else "")
    else:
        sys.exit(главная([а for а in sys.argv[1:] if not а.startswith("-")]))
