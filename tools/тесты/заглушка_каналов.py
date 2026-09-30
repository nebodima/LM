"""Заглушка сервисов для тестов на 127.0.0.1: сообщения (Telegram Bot API, SMS.ru, SMSC.ru, Green-API, Wazzup) и банки
оплаты по QR через СБП (Точка — Open API СБП, Т-Банк — интернет-эквайринг Init/GetQr/GetState/Cancel).

Продукт в песочнице сеанса ходит по HTTP только на эту машину (УЗ_ПровайдерыСообщений.ВыполнитьHTTP), поэтому
тесты ставят в настройки каналов адрес заглушки (http://127.0.0.1:<порт>/<префикс>) и видят каждый запрос: путь,
параметры, тело. Наружу ничего не уходит.

    python tools\\тесты\\заглушка_каналов.py [--порт=0]   — печатает «ПОРТ <n>» и работает до завершения процесса

Управление (для тестов):
    GET  /__запросы            — все принятые запросы JSON-массивом: {"метод", "путь", "параметры", "тело"}
    POST /__сброс              — забыть запросы, снять сбои, очистить очередь обновлений Telegram
    POST /__сбой   {"префикс": "/sms", "код": 503}   — все запросы с путём от префикса отвечают этим кодом
    POST /__обновления [ {...update...}, ... ]        — очередь getUpdates Telegram (отдаётся с учётом offset)
    answerCallbackQuery — {"ok": true} (ответ на нажатие inline-кнопки)
Особые адресаты: чат Telegram «400» — 400 «chat not found»; телефон 79000000099 — SMS.ru отказ по номеру.

Банки (этап 2.3, оплата по QR):
    Точка: POST …/sbp/v1.0/qr-code/merchant/<merchantId>/<счёт>/<БИК> (Bearer обязателен) → Data: qrcId, payload,
           image.content (PNG); GET …/sbp/v1.0/qr-codes/<qrcId>/payment-status → paymentList[0].status (NotStarted…)
    Т-Банк: POST …/v2/Init, /v2/GetQr (PAYLOAD — ссылка, IMAGE — SVG), /v2/GetState, /v2/Cancel; подпись Token
           проверяется, если задан пароль терминала (/__банк {"пароль": …}) — неверная: Success=false, ErrorCode 204
    POST /__оплата {"ид": "<qrcId или PaymentId>", "статус": "Accepted" | "CONFIRMED" | …} — статус платежа в банке
    GET  /__платежи — выставленные QR: {ид: {"статус", "сумма", "банк"}}
"""
import base64
import hashlib
import json
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

СОСТОЯНИЕ = {"запросы": [], "сбои": {}, "обновления": [], "платежи": {}, "пароль": ""}
# картинка QR Точки — настоящий PNG 1×1 (форма показывает его картинкой), SVG Т-Банка — настоящий SVG
PNG = base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360f8cf00000301010018dd8db00000000049454e44ae426082")).decode("ascii")
SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">'
       '<rect width="10" height="10" fill="#000"/></svg>')


def токен_тбанк(поля, пароль):
    """Подпись Т-Банка: корневые скалярные поля без Token + Password, по имени, значения подряд, SHA-256 hex."""
    значения = {к: в for к, в in поля.items() if к != "Token" and not isinstance(в, (dict, list))}
    значения["Password"] = пароль
    строка = "".join(("true" if в is True else "false" if в is False else str(в)) for _, в in sorted(значения.items()))
    return hashlib.sha256(строка.encode("utf-8")).hexdigest()
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
        if путь.endswith("/answerCallbackQuery") and "/bot" in путь:
            return self.ответ(200, {"ok": True, "result": True})
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
        if "/sbp/v1.0/" in путь:
            return self.точка(метод, путь, тело or {})
        if "/v2/" in путь:
            return self.тбанк(путь, тело or {})
        return self.ответ(404, {"ok": False, "description": "нет такого метода в заглушке"})

    def точка(self, метод, путь, тело):
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            return self.ответ(401, {"code": "401", "message": "Unauthorized"})
        if метод == "POST" and "/qr-code/merchant/" in путь:
            данные = тело.get("Data") or {}
            with ЗАМОК:
                ид = "AD%030d" % (len(СОСТОЯНИЕ["платежи"]) + 1)
                СОСТОЯНИЕ["платежи"][ид] = {"статус": "NotStarted", "сумма": данные.get("amount"), "банк": "Точка"}
            ссылка = "https://qr.nspk.ru/%s?type=02&bank=100000000284&sum=%s&cur=RUB&crc=AB12" % (
                ид, данные.get("amount"))
            return self.ответ(200, {"Data": {"qrcId": ид, "payload": ссылка,
                                             "image": {"width": 300, "height": 300, "mediaType": "image/png",
                                                       "content": PNG}}})
        if метод == "GET" and путь.endswith("/payment-status"):
            ид = путь.split("/qr-codes/", 1)[1].split("/", 1)[0]
            with ЗАМОК:
                платеж = СОСТОЯНИЕ["платежи"].get(ид)
            if платеж is None:
                return self.ответ(404, {"code": "404", "message": "QR-код не найден",
                                        "Errors": [{"errorCode": "NotFound", "message": "QR-код не найден"}]})
            return self.ответ(200, {"Data": {"paymentList": [{"qrcId": ид, "code": "RQ00000", "message": "ok",
                                                              "status": платеж["статус"],
                                                              "trxId": "A%s" % ид[-8:]}]}})
        return self.ответ(404, {"code": "404", "message": "нет такого метода в заглушке"})

    def тбанк(self, путь, тело):
        with ЗАМОК:
            пароль = СОСТОЯНИЕ["пароль"]
        if пароль and тело.get("Token") != токен_тбанк(тело, пароль):
            return self.ответ(200, {"Success": False, "ErrorCode": "204", "Message": "Неверный токен",
                                    "Details": "Проверьте пароль терминала"})
        ид = str(тело.get("PaymentId", ""))
        if путь.endswith("/v2/Init"):
            with ЗАМОК:
                ид = str(7000000 + len(СОСТОЯНИЕ["платежи"]) + 1)
                СОСТОЯНИЕ["платежи"][ид] = {"статус": "NEW", "сумма": тело.get("Amount"), "банк": "ТБанк",
                                            "заказ": тело.get("OrderId"), "срок": тело.get("RedirectDueDate")}
            return self.ответ(200, {"Success": True, "ErrorCode": "0", "TerminalKey": тело.get("TerminalKey"),
                                    "Status": "NEW", "PaymentId": ид, "OrderId": тело.get("OrderId"),
                                    "Amount": тело.get("Amount"), "PaymentURL": "https://pay.tbank.ru/stub"})
        with ЗАМОК:
            платеж = СОСТОЯНИЕ["платежи"].get(ид)
        if платеж is None:
            return self.ответ(200, {"Success": False, "ErrorCode": "7", "Message": "Платёж не найден", "Details": ид})
        if путь.endswith("/v2/GetQr"):
            if тело.get("DataType") == "IMAGE":
                return self.ответ(200, {"Success": True, "ErrorCode": "0", "PaymentId": int(ид), "Data": SVG})
            return self.ответ(200, {"Success": True, "ErrorCode": "0", "PaymentId": int(ид),
                                    "Data": "https://qr.nspk.ru/BD%s?type=02&sum=%s" % (ид, платеж["сумма"])})
        if путь.endswith("/v2/GetState"):
            return self.ответ(200, {"Success": True, "ErrorCode": "0", "Status": платеж["статус"], "PaymentId": ид,
                                    "Amount": платеж["сумма"]})
        if путь.endswith("/v2/Cancel"):
            with ЗАМОК:
                платеж["статус"] = "CANCELED"
            return self.ответ(200, {"Success": True, "ErrorCode": "0", "Status": "CANCELED", "PaymentId": ид})
        return self.ответ(404, {"Success": False, "ErrorCode": "404", "Message": "нет такого метода в заглушке"})

    def управление(self, путь, тело):
        with ЗАМОК:
            if путь == "/__запросы":
                return self.ответ(200, СОСТОЯНИЕ["запросы"])
            if путь == "/__платежи":
                return self.ответ(200, СОСТОЯНИЕ["платежи"])
            if путь == "/__сброс":
                СОСТОЯНИЕ.update({"запросы": [], "сбои": {}, "обновления": [], "платежи": {}, "пароль": ""})
            elif путь == "/__оплата":
                if тело.get("ид") in СОСТОЯНИЕ["платежи"]:
                    СОСТОЯНИЕ["платежи"][тело["ид"]]["статус"] = тело.get("статус", "")
            elif путь == "/__банк":
                СОСТОЯНИЕ["пароль"] = тело.get("пароль", "")
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
