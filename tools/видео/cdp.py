"""Headless Chrome по протоколу отладки — для записи видеоинструкции веб-клиента 1С.

Отличия от tools\\демо\\снимки.py (снимки по одному кадру):
  * окно 1536×864 CSS-пикселей с масштабом 1,25 — кадр ровно 1920×1080, а шрифт 1С крупнее, чем в окне 1920;
  * видимый курсор: в headless-браузере курсора нет, поэтому страница получает свой слой-стрелку, которая плавно
    едет к цели, а нажатие показывается расходящимся кругом. Настоящие события мыши идут в ту же точку;
  * запись — поток кадров Page.startScreencast по ВТОРОМУ вебсокету в отдельном потоке: команды основного
    соединения не глотают кадры, а кадры не ждут ответов команд. Кадр приходит, только когда картинка меняется,
    поэтому у каждого — своё время прихода.

Браузер можно держать запущенным между вызовами (--порт) — разведка форм без новой загрузки клиента.
"""
import base64
import json
import os
import socket
import subprocess
import threading
import time
import urllib.request

import websocket

ХРОМ = next((п for п in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") if os.path.isfile(п)), None)
ШИРИНА, ВЫСОТА, МАСШТАБ = 1536, 864, 1.25          # кадр 1920×1080
ОКНА_ОШИБОК = ("Не удалось перейти по навигационной ссылке", "непредвиденная ошибка", "Ошибка при вызове",
               "Неверный формат навигационной ссылки", "Поле объекта не обнаружено", "Ошибка выполнения",
               "Нарушение прав доступа", "Недостаточно прав")


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


# слой курсора: стрелка + круг нажатия; pointer-events:none — клики проходят в клиент 1С
КУРСОР_JS = r"""(function(){
 if (window.__вк) return 1;
 var с=document.createElement('div'); с.id='__вк_курсор';
 с.style.cssText='position:fixed;left:0;top:0;width:30px;height:30px;z-index:2147483647;pointer-events:none;'+
   'transform:translate(760px,430px);will-change:transform;filter:drop-shadow(1px 2px 2px rgba(0,0,0,.45))';
 с.innerHTML='<svg width="30" height="30" viewBox="0 0 24 24"><path d="M3 2 L3 19 L7.6 14.8 L10.6 21.5 L13.4 20.3 L10.5 13.7 L16.8 13.7 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
 document.documentElement.appendChild(с);
 var st=document.createElement('style');
 st.textContent='@keyframes __вк_волна{0%{transform:translate(-50%,-50%) scale(.3);opacity:.95}100%{transform:translate(-50%,-50%) scale(1.6);opacity:0}}'+
  '.__вк_круг{position:fixed;width:46px;height:46px;border-radius:50%;border:4px solid #ff7a00;background:rgba(255,160,0,.28);'+
  'z-index:2147483646;pointer-events:none;animation:__вк_волна .7s ease-out forwards}';
 document.documentElement.appendChild(st);
 window.__вк={x:760,y:430,
  ехать:function(x,y,мс){var н=performance.now(),x0=this.x,y0=this.y,я=this;
    function шаг(т){var k=Math.min(1,(т-н)/мс); k=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
      var cx=x0+(x-x0)*k, cy=y0+(y-y0)*k; с.style.transform='translate('+cx+'px,'+cy+'px)';
      if(k<1) requestAnimationFrame(шаг); else {я.x=x;я.y=y;}}
    requestAnimationFrame(шаг);},
  нажать:function(){var к=document.createElement('div'); к.className='__вк_круг';
    к.style.left=(this.x+3)+'px'; к.style.top=(this.y+3)+'px'; document.documentElement.appendChild(к);
    setTimeout(function(){к.remove();},800);}};
 return 1;})()"""


class Запись:
    """Поток кадров страницы во втором соединении: [(секунда, путь_jpeg)], время — time.time()."""

    def __init__(self, адрес_ws, папка, качество=88):
        self.адрес, self.папка, self.качество = адрес_ws, папка, качество
        self.кадры = []
        self.идёт = False
        self.поток = None
        os.makedirs(папка, exist_ok=True)

    def начать(self):
        self.ws = websocket.create_connection(self.адрес, timeout=5)
        self.номер = 0
        self.ws.send(json.dumps({"id": 1, "method": "Page.startScreencast",
                                 "params": {"format": "jpeg", "quality": self.качество, "maxWidth": 1920,
                                            "maxHeight": 1080, "everyNthFrame": 1}}))
        self.идёт = True
        self.поток = threading.Thread(target=self._цикл, daemon=True)
        self.поток.start()

    def _цикл(self):
        сч = 10
        while self.идёт:
            try:
                сообщение = self.ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break
            д = json.loads(сообщение)
            if д.get("method") != "Page.screencastFrame":
                continue
            п = д["params"]
            путь = os.path.join(self.папка, "к%06d.jpg" % self.номер)
            with open(путь, "wb") as ф:
                ф.write(base64.b64decode(п["data"]))
            self.кадры.append((time.time(), путь))
            self.номер += 1
            сч += 1
            try:
                self.ws.send(json.dumps({"id": сч, "method": "Page.screencastFrameAck",
                                         "params": {"sessionId": п["sessionId"]}}))
            except Exception:
                break

    def закончить(self):
        self.идёт = False
        try:
            self.ws.send(json.dumps({"id": 2, "method": "Page.stopScreencast"}))
        except Exception:
            pass
        if self.поток:
            self.поток.join(timeout=3)
        try:
            self.ws.close()
        except Exception:
            pass


class Хром:
    def __init__(self, порт=None, запустить=True, профиль=None):
        if порт is None:
            порт = свободный_порт()
        self.порт = порт
        self.процесс = None
        if запустить:
            self.профиль = профиль or os.path.join(os.environ.get("TEMP", "."), "chrome-уз-видео-%d" % порт)
            self.процесс = subprocess.Popen([
                ХРОМ, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                "--no-default-browser-check", "--remote-debugging-port=%d" % порт, "--remote-allow-origins=*",
                "--user-data-dir=%s" % self.профиль, "--window-size=%d,%d" % (ШИРИНА, ВЫСОТА), "--force-device-scale-factor=%s" % МАСШТАБ,
                "--lang=ru-RU",
                "--disable-features=Translate", "--font-render-hinting=none"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=0x00000008 | 0x00000200)
        self.счётчик = 0
        self.ws = self._подключиться()
        self.команда("Page.enable")
        self.команда("Runtime.enable")
        # размер и масштаб — ключами запуска браузера: подмена (Emulation) живёт, пока открыто соединение, и её снятие
        # при переподключении — это «изменение размера окна», на которое веб-клиент 1С отменяет ввод строки таблицы
        if self.js("[innerWidth, innerHeight, devicePixelRatio].join()") != "%d,%d,%s" % (ШИРИНА, ВЫСОТА, МАСШТАБ):
            self.размер()
        self.курсор = tuple(self.js("window.__вк ? [window.__вк.x, window.__вк.y] : null") or (ШИРИНА // 2, ВЫСОТА // 2))

    # ── соединение ──
    def цели(self):
        return json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % self.порт, timeout=2).read())

    def адрес_страницы(self):
        return [ц for ц in self.цели() if ц.get("type") == "page"][0]["webSocketDebuggerUrl"]

    def _подключиться(self):
        for _ in range(80):
            try:
                return websocket.create_connection(self.адрес_страницы(), timeout=180)
            except Exception:
                time.sleep(0.5)
        raise RuntimeError("браузер молчит на порту %d" % self.порт)

    def команда(self, метод, **параметры):
        self.счётчик += 1
        моя = self.счётчик
        self.ws.send(json.dumps({"id": моя, "method": метод, "params": параметры}))
        while True:
            ответ = json.loads(self.ws.recv())
            if ответ.get("method") == "Page.javascriptDialogOpening":
                self.счётчик += 1
                self.ws.send(json.dumps({"id": self.счётчик, "method": "Page.handleJavaScriptDialog",
                                         "params": {"accept": True}}))
                continue
            if ответ.get("id") == моя:
                if "error" in ответ:
                    raise RuntimeError("%s: %s" % (метод, ответ["error"]))
                return ответ.get("result", {})

    def размер(self, ширина=ШИРИНА, высота=ВЫСОТА, масштаб=МАСШТАБ):
        self.команда("Emulation.setDeviceMetricsOverride", width=ширина, height=высота, deviceScaleFactor=масштаб,
                     mobile=False)

    def js(self, выражение):
        о = self.команда("Runtime.evaluate", expression=выражение, returnByValue=True, awaitPromise=True)
        return о.get("result", {}).get("value")

    # ── навигация ──
    def открыть(self, адрес, ждать=60):
        """Загрузка клиента: ждём, пока пропадёт заставка и появится панель разделов или форма."""
        self.команда("Page.navigate", url="about:blank")
        time.sleep(0.5)
        self.команда("Page.navigate", url=адрес)
        срок = time.time() + ждать
        time.sleep(5)
        while time.time() < срок:
            if self.js("document.querySelectorAll('[id^=\"themesCell_theme_\"], [id$=\"_$scrl\"]').length"):
                break
            time.sleep(0.5)
        time.sleep(3)
        self.поставить_курсор()

    def поставить_курсор(self):
        self.js(КУРСОР_JS)
        x, y = self.курсор
        self.js("window.__вк && (window.__вк.x=%d, window.__вк.y=%d, window.__вк.ехать(%d,%d,1))" % (x, y, x, y))

    def закрыть(self):
        try:
            self.команда("Page.navigate", url="about:blank")   # веб-клиент закрывает свой сеанс при уходе
            time.sleep(2)
            self.ws.close()
        except Exception:
            pass
        if self.процесс:
            self.процесс.terminate()
            try:
                self.процесс.wait(timeout=10)
            except Exception:
                self.процесс.kill()

    # ── поиск ──
    def место(self, ид):
        return self.js("""(function(){var p=document.getElementById(%s); if(!p) return null;
            var r=p.getBoundingClientRect(); if(r.width<1||r.height<1) return null; return [r.left,r.top,r.width,r.height];})()"""
                       % json.dumps(ид, ensure_ascii=False))

    def найти_текст(self, текст, область="", точно=True):
        """[x, y, w, h] самого глубокого видимого элемента с таким текстом (пробелы нормализуются)."""
        return self.js("""(function(){
            var все=document.querySelectorAll(%s), найден=null, нужно=%s, точно=%s;
            for (var i=0;i<все.length;i++){ var p=все[i];
              var т=(p.textContent||'').replace(/[\\s\\u00a0]+/g,' ').trim();
              var r=p.getBoundingClientRect();
              var да = точно ? т===нужно : т.indexOf(нужно)>=0 && т.length < нужно.length+200;
              if (p.closest('.tooltip')) continue;   // всплывающая подсказка с тем же текстом — не цель
              if (!(да && r.width>0 && r.height>0 && r.top>=0 && r.bottom<=innerHeight+2 && r.left<innerWidth)) continue;
              // виден на самом деле: в его центре — он сам (или его часть), а не окно поверх и не скрытое меню
              var в=document.elementFromPoint(r.left+Math.min(10,r.width/2), r.top+r.height/2);
              if (в && (в===p || p.contains(в))) найден=p;}
            if(!найден) return null; var r=найден.getBoundingClientRect(); return [r.left,r.top,r.width,r.height];})()"""
                       % (json.dumps((область + " " if область else "") + "div,span,a,td,button,label", ensure_ascii=False),
                          json.dumps(текст, ensure_ascii=False), "true" if точно else "false"))

    def форма(self):
        """Номер активной формы (самый большой N у видимых formN_)."""
        n = self.js(r"""(function(){var n=-1; document.querySelectorAll('[id^="form"]').forEach(function(e){
            var m=e.id.match(/^form(\d+)_/); if(!m) return; var r=e.getBoundingClientRect();
            if(r.width<10||r.height<10) return; if(+m[1]>n) n=+m[1];}); return n;})()""")
        return 0 if n is None or n < 0 else n

    def ид_формы(self, n=None):
        n = self.форма() if n is None else n
        return self.js(r"""(function(){var итог=[]; document.querySelectorAll('[id^="form%d_"]').forEach(function(e){
            var r=e.getBoundingClientRect(); if(r.width>0&&r.height>0) итог.push(e.id);}); return итог;})()""" % n) or []

    def окно_ошибки(self):
        return self.js("""(function(){var т=document.body?document.body.innerText:'', ф=%s, н=[];
            ф.forEach(function(x){if(т.indexOf(x)>=0) н.push(x);}); return н.join(' | ');})()"""
                       % json.dumps(list(ОКНА_ОШИБОК), ensure_ascii=False)) or ""

    def текст(self):
        return self.js("document.body ? document.body.innerText : ''") or ""

    # ── мышь и клавиатура ──
    def ехать(self, x, y, мс=None):
        x0, y0 = self.курсор
        if мс is None:
            расстояние = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
            мс = int(min(1100, max(350, расстояние * 1.1)))
        self.js("window.__вк || %s" % КУРСОР_JS)
        self.js("window.__вк.ехать(%d,%d,%d)" % (x, y, мс))
        self.команда("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
        time.sleep(мс / 1000 + 0.08)
        self.курсор = (x, y)

    def клик_в(self, x, y, ждать=1.0, двойной=False, ехать=True):
        if ехать:
            self.ехать(x, y)
        self.js("window.__вк && window.__вк.нажать()")
        self.команда("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
        self.команда("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
        if двойной:
            self.команда("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=2)
            self.команда("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=2)
        time.sleep(ждать)

    def клик(self, цель, ждать=1.0, двойной=False, сдвиг=None, ждать_цель=15):
        """Цель: 'id:formN_Имя' | 'эл:Имя' (в активной форме) | 'текст:Надпись' | 'часть:Надпись' | (x, y)."""
        м = self.найти(цель, ждать_цель)
        if сдвиг:
            x, y = м[0] + сдвиг[0], м[1] + сдвиг[1]
        else:
            x, y = м[0] + min(14, м[2] / 2), м[1] + м[3] / 2
        self.клик_в(int(x), int(y), ждать, двойной)

    def навести(self, цель, мс=None, сдвиг=None):
        """Курсор к цели (подсказать зрителю, куда смотреть). Нет цели — не повод ронять запись: предупредить."""
        try:
            м = self.найти(цель, ждать=3)
        except RuntimeError as е:
            print("    [навести] %s" % е, flush=True)
            return
        x, y = (м[0] + сдвиг[0], м[1] + сдвиг[1]) if сдвиг else (м[0] + м[2] / 2, м[1] + м[3] / 2)
        self.ехать(int(x), int(y), мс)

    def найти(self, цель, ждать=15):
        if isinstance(цель, (tuple, list)):
            return [цель[0], цель[1], 0, 0]
        вид, значение = цель.split(":", 1)
        срок = time.time() + ждать
        while True:
            if вид == "id":
                м = self.место(значение)
            elif вид == "эл":
                м = self.место("form%d_%s" % (self.форма(), значение))
            elif вид == "вкладка":   # закладка страницы формы — по имени страницы
                м = self.место("thpage_form%d_%s" % (self.форма(), значение))
            elif вид == "текст":
                м = self.найти_текст(значение)
            elif вид == "часть":
                м = self.найти_текст(значение, точно=False)
            elif вид == "css":        # последний видимый элемент по селектору
                м = self.js("""(function(){var в=document.querySelectorAll(%s), н=null;
                    for(var i=0;i<в.length;i++){var r=в[i].getBoundingClientRect(); if(r.width>0&&r.height>0) н=r;}
                    return н?[н.left,н.top,н.width,н.height]:null;})()""" % json.dumps(значение, ensure_ascii=False))
            else:
                raise ValueError(цель)
            if м:
                return м
            if time.time() > срок:
                raise RuntimeError("на экране нет цели «%s»" % цель)
            time.sleep(0.3)

    def ячейка(self, строка, колонка, флажок=False):
        """[x, y, w, h] ячейки таблицы: строка — видимый текст в ней (ФИО ученика), колонка — заголовок. флажок —
        сам квадратик (.checkbox): щелчок по ячейке мимо квадратика отметку не меняет."""
        return self.js("""(function(строка, колонка, флажок){
            function найти(т){var все=document.querySelectorAll('div,span'), н=null;
              for(var i=0;i<все.length;i++){var p=все[i], r=p.getBoundingClientRect();
                if((p.textContent||'').replace(/[\\s\\u00a0]+/g,' ').trim()===т && r.width>0 && r.top>=0 && r.top<innerHeight) н=p;}
              return н;}
            var с=найти(строка), к=найти(колонка); if(!с||!к) return null;
            var кр=к.getBoundingClientRect(), линия=с.closest('.gridLine'); if(!линия) return null;
            var лр=линия.getBoundingClientRect();
            if(флажок){var ф=линия.querySelectorAll('.checkbox');
              for(var i=0;i<ф.length;i++){var r=ф[i].getBoundingClientRect(), ц=r.left+r.width/2;
                if(ц>=кр.left-4 && ц<=кр.right+4) return [r.left,r.top,r.width,r.height];} return null;}
            return [кр.left, лр.top, кр.width, лр.height];})(%s, %s, %s)"""
                       % (json.dumps(строка, ensure_ascii=False), json.dumps(колонка, ensure_ascii=False),
                          "true" if флажок else "false"))

    def отметить(self, строка, колонка, ждать=0.6):
        м = self.ячейка(строка, колонка, флажок=True)
        if not м:
            raise RuntimeError("нет флажка «%s» в строке «%s»" % (колонка, строка))
        self.клик_в(int(м[0] + м[2] / 2), int(м[1] + м[3] / 2), ждать)

    def клавиша(self, ключ, код, ждать=0.3, модификаторы=0, текст=None):
        for тип in ("keyDown", "keyUp"):
            п = dict(type=тип, key=ключ, code=ключ, windowsVirtualKeyCode=код, nativeVirtualKeyCode=код,
                     modifiers=модификаторы)
            if текст and тип == "keyDown":
                п["text"] = текст
            self.команда("Input.dispatchKeyEvent", **п)
        time.sleep(ждать)

    def печатать(self, текст, пауза=0.055):
        """Посимвольно, как человек: подбор по вводу в 1С будят только события клавиатуры."""
        for символ in текст:
            if символ == "\n":
                self.клавиша("Enter", 13, ждать=пауза, текст="\r")
                continue
            self.команда("Input.dispatchKeyEvent", type="keyDown", key=символ, text=символ, unmodifiedText=символ)
            self.команда("Input.dispatchKeyEvent", type="keyUp", key=символ)
            time.sleep(пауза)

    def выделить_всё(self):
        self.клавиша("a", 65, ждать=0.2, модификаторы=2)

    def снять(self, путь):
        о = self.команда("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        with open(путь, "wb") as ф:
            ф.write(base64.b64decode(о["data"]))
        return путь

    def закрыть_оповещения(self):
        for _ in range(6):
            м = self.js("""(function(){var к=document.querySelectorAll('#notificationArea .notificationClose, .notificationClose');
                for(var i=0;i<к.length;i++){var r=к[i].getBoundingClientRect(); if(r.width>0) return [r.left+8,r.top+8];}
                return null;})()""")
            if not м:
                return
            self.команда("Input.dispatchMouseEvent", type="mousePressed", x=м[0], y=м[1], button="left", clickCount=1)
            self.команда("Input.dispatchMouseEvent", type="mouseReleased", x=м[0], y=м[1], button="left", clickCount=1)
            time.sleep(0.6)
