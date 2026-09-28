"""Окна процессов 1С: убрать за экран (владелец работает за этим ПК) и снять снимок окна без вывода на экран.

Окно не сворачивается, а уводится за левый край: свёрнутое окно платформа не рисует, и снимок был бы пустым;
за экраном оно рисуется как обычно, PrintWindow (PW_RENDERFULLCONTENT) снимает его содержимое.
"""
import ctypes
import ctypes.wintypes as wt
import threading
import time

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
ЗА_ЭКРАН_X = -6000
SWP_NOSIZE, SWP_NOZORDER, SWP_NOACTIVATE = 0x0001, 0x0004, 0x0010
PW_RENDERFULLCONTENT = 2
# координаты окон — в физических пикселях (экран владельца 200 %): иначе снимок обрезан на половине
try:
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    pass

ПеречислитьОкна = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def окна_процессов(пиды, видимые=True):
    """Окна верхнего уровня процессов (hwnd, pid, заголовок)."""
    итог = []

    def обход(hwnd, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in пиды and (not видимые or user32.IsWindowVisible(hwnd)):
            длина = user32.GetWindowTextLengthW(hwnd)
            буфер = ctypes.create_unicode_buffer(длина + 1)
            user32.GetWindowTextW(hwnd, буфер, длина + 1)
            итог.append((hwnd, pid.value, буфер.value))
        return True
    user32.EnumWindows(ПеречислитьОкна(обход), 0)
    return итог


def прямоугольник(hwnd):
    п = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(п))
    return п.left, п.top, п.right, п.bottom


class Сторож(threading.Thread):
    """Каждые 50 мс уводит за экран новые окна процессов (заставка, основное окно, вопросы). Выключен (--видно) —
    окна остаются на месте."""

    def __init__(self, убирать=True):
        super().__init__(daemon=True)
        self.пиды = set()
        self.убирать = убирать
        self.стоп = threading.Event()

    def run(self):
        while not self.стоп.is_set():
            if self.убирать and self.пиды:
                for hwnd, _, _ in окна_процессов(set(self.пиды)):
                    л, в, п, н = прямоугольник(hwnd)
                    if л > ЗА_ЭКРАН_X + 3000:
                        user32.SetWindowPos(hwnd, 0, ЗА_ЭКРАН_X, max(в, 0), 0, 0,
                                            SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
            time.sleep(0.05)


def снимок(пиды, путь):
    """PNG самого большого видимого окна процессов (основное окно клиента; модальное окно рисуется поверх него
    отдельным окном — его тоже снимаем рядом, если есть). Возвращает список сохранённых файлов."""
    from PIL import Image
    окна = []
    for hwnd, _, заголовок in окна_процессов(set(пиды)):
        л, в, п, н = прямоугольник(hwnd)
        if п - л > 50 and н - в > 50:
            окна.append(((п - л) * (н - в), hwnd, п - л, н - в))
    окна.sort(reverse=True)
    файлы = []
    for номер, (_, hwnd, ш, в) in enumerate(окна[:3]):
        hdc = user32.GetWindowDC(hwnd)
        mem = gdi32.CreateCompatibleDC(hdc)
        bmp = gdi32.CreateCompatibleBitmap(hdc, ш, в)
        gdi32.SelectObject(mem, bmp)
        user32.PrintWindow(hwnd, mem, PW_RENDERFULLCONTENT)

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                        ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                        ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                        ("biClrImportant", wt.DWORD)]
        заголовок = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), ш, -в, 1, 32, 0, 0, 0, 0, 0, 0)
        буфер = ctypes.create_string_buffer(ш * в * 4)
        gdi32.GetDIBits(mem, bmp, 0, в, буфер, ctypes.byref(заголовок), 0)
        картинка = Image.frombuffer("RGB", (ш, в), буфер, "raw", "BGRX", 0, 1)
        файл = путь if номер == 0 else путь.replace(".png", "_%d.png" % номер)
        картинка.save(файл)
        файлы.append(файл)
        gdi32.DeleteObject(bmp)
        gdi32.DeleteDC(mem)
        user32.ReleaseDC(hwnd, hdc)
    return файлы
