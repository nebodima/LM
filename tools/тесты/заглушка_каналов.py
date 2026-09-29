"""Заглушка сервисов сообщений для тестов: Telegram Bot API, SMS.ru, SMSC.ru, Green-API, Wazzup — на 127.0.0.1.

Продукт в песочнице сеанса ходит по HTTP только на эту машину (УЗ_ПровайдерыСообщений.ВыполнитьHTTP), поэтому
тесты ставят в настройки каналов адрес заглушки (http://127.0.0.1:<порт>/<префикс>) и видят каждый запрос: путь,
параметры, тело. Наружу ничего не уходит.

    python tools\\тесты\\заглушка_каналов.py [--порт=0]   — печатает «ПОРТ <n>» и работает до завершения процесса

Управление (для тестов):
    GET  /__запросы            — все принятые запросы JSON-массивом: {"метод", "путь", "параметры", "тело"}
    POST /__сброс              — забыть запросы, снять сбои, очистить очередь обновлений Telegram
    POST /__сбой   {"префикс": "/sms", "код": 503}   — все запросы с путём от префикса отвечают этим кодом
    POST /__обновления [ {...update...}, ... ]        — очередь getUpdates Telegram (отдаётся с учётом offset)
Особые адресаты: чат Telegram «400» — 400 «chat not found»; телефон 79000000099 — SMS.ru отказ по номеру.
"""
import json
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

СОСТОЯНИЕ = {"запросы": [], "сбои": {}, "обновления": []}
ЗАМОК = threading.Lock()


def разобрать_тело(заголовки, сырое):
    текст = сырое.decode("utf-8", errors="replace")
    вид = заголовки.get("Content-Type", "")
    if "json" in вид:
        try:
            return json.loads(текст or "null")
        except ValueError:
            return текст
    if "x-www-form-urlencoded" in вид:
        return {к: в[0] for к, в in urllib.parse.parse_qs(текст, keep_blank_values=True).items()}
    return текст


class Обработчик(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def ответ(self, код, данные):
        тело = json.dumps(данные, ensure_ascii=False).encode("utf-8")
        self.send_response(код)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(тело)))
        self.end_headers()
        self.wfile.write(тело)

    def do_GET(self):
        self.обработать("GET")

    def do_POST(self):
        self.обработать("POST")

    def обработать(self, метод):
        адрес = urllib.parse.urlsplit(self.path)
        путь = urllib.parse.unquote(адрес.path)
        параметры = {к: в[0] for к, в in urllib.parse.parse_qs(адрес.query, keep_blank_values=True).items()}
        длина = int(self.headers.get("Content-Length") or 0)
        тело = разобрать_тело(self.headers, self.rfile.read(длина) if длина else b"")
        if путь.startswith("/__"):
            return self.управление(путь, тело)
        with ЗАМОК:
            СОСТОЯНИЕ["запросы"].append({"метод": метод, "путь": путь, "параметры": параметры, "тело": тело,
                                         "авторизация": self.headers.get("Authorization", "").encode("latin-1").decode("utf-8", "replace")})
            сбой = next((к for п, к in СОСТОЯНИЕ["сбои"].items() if путь.startswith(п)), None)
        if сбой:
            return self.ответ(сбой, {"ok": False, "description": "сбой заглушки", "status": "ERROR",
                                     "error": "сбой заглушки", "error_code": 9})
        if "/getUpdates" in путь:
            смещение = int(параметры.get("offset", "0") or 0)
            with ЗАМОК:
                итог = [о for о in СОСТОЯНИЕ["обновления"] if о.get("update_id", 0) >= смещение]
            return self.ответ(200, {"ok": True, "result": итог})
        if путь.endswith("/sendMessage") and "/bot" in путь:
            if str((тело or {}).get("chat_id")) == "400":
                return self.ответ(400, {"ok": False, "error_code": 400, "description": "Bad Request: chat not found"})
            return self.ответ(200, {"ok": True, "result": {"message_id": len(СОСТОЯНИЕ["запросы"])}})
        if путь.endswith("/sms/send"):
            номер = (тело or {}).get("to", "")
            если_отказ = номер == "79000000099"
            return self.ответ(200, {"status": "OK", "status_code": 100, "sms": {номер: (
                {"status": "ERROR", "status_code": 202, "status_text": "Неправильно указан номер"} if если_отказ
                else {"status": "OK", "status_code": 100, "sms_id": "000-1"})}, "balance": 100.0})
        if путь.endswith("/sys/send.php"):
            return self.ответ(200, {"id": 1, "cnt": 1})
        if "/sendMessage/" in путь and "/waInstance" in путь:
            return self.ответ(200, {"idMessage": "3EB0C767D097B7C7C030"})
        if путь.endswith("/v3/message"):
            return self.ответ(201, {"messageId": "wz-1", "chatId": (тело or {}).get("chatId", "")})
        return self.ответ(404, {"ok": False, "description": "нет такого метода в заглушке"})

    def управление(self, путь, тело):
        with ЗАМОК:
            if путь == "/__запросы":
                return self.ответ(200, СОСТОЯНИЕ["запросы"])
            if путь == "/__сброс":
                СОСТОЯНИЕ.update({"запросы": [], "сбои": {}, "обновления": []})
            elif путь == "/__сбой":
                if тело.get("код"):
                    СОСТОЯНИЕ["сбои"][тело["префикс"]] = int(тело["код"])
                else:
                    СОСТОЯНИЕ["сбои"].pop(тело["префикс"], None)
            elif путь == "/__обновления":
                СОСТОЯНИЕ["обновления"] = list(тело or [])
        return self.ответ(200, {"ok": True})


def запустить(порт=0):
    """Заглушка в потоке этого процесса → (сервер, порт). Остановить: сервер.shutdown()."""
    сервер = ThreadingHTTPServer(("127.0.0.1", порт), Обработчик)
    threading.Thread(target=сервер.serve_forever, daemon=True).start()
    return сервер, сервер.server_address[1]


if __name__ == "__main__":
    порт = 0
    for арг in sys.argv[1:]:
        if арг.startswith("--порт="):
            порт = int(арг.split("=", 1)[1])
    сервер = ThreadingHTTPServer(("127.0.0.1", порт), Обработчик)
    print("ПОРТ %d" % сервер.server_address[1], flush=True)
    сервер.serve_forever()
