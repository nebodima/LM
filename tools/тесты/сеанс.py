"""Общее для COM-тестов УЗ_ext: подключение к своей базе, проверки, замер, уборка.

    from сеанс import Тест
    т = Тест("печать")            # --база=C:\\1c_bases\\UZ_UNF_C (по умолчанию УНФ стенда)
    т.проверить(условие, "что проверяли", подробности)
    т.убрать(лямбда)              # уборка в обратном порядке — и при падении теста
    sys.exit(т.итог())

Один COM-сеанс на тест. Бюджет — 10 с на сценарий без подключения (подключение к файловой
базе само по себе ~6 с, его время печатается отдельно).
"""
import os
import os
import sys
import time
import traceback

БЮДЖЕТ_СЕК = 10


class Тест:
    def __init__(self, имя):
        import win32com.client
        sys.stdout.reconfigure(encoding="utf-8")
        self.имя = имя
        self.база = r"C:\1c_bases\UZ_UNF"
        for а in sys.argv[1:]:
            if а.startswith("--база="):
                self.база = а.split("=", 1)[1]
        self.ошибок = 0
        self.проверок = 0
        self.уборка = []
        н = time.time()
        self.c = win32com.client.Dispatch("V83.COMConnector").Connect(
            'File="%s";Usr="Администратор";' % self.база)
        self.подключение = time.time() - н
        self.начало = time.time()
        print("== тест %s: база %s, подключение %.1f с" % (имя, self.база, self.подключение))

    def проверить(self, условие, что, подробности=""):
        self.проверок += 1
        if условие:
            print("  ок    %s" % что)
        else:
            self.ошибок += 1
            print("  ОШИБКА %s %s" % (что, подробности))
        return условие

    def убрать(self, действие, что=""):
        self.уборка.append((действие, что))

    def выполнить(self, сценарий):
        try:
            сценарий(self)
        except Exception as е:
            self.ошибок += 1
            # traceback.format_exc спотыкается о кириллицу в строке с «^^^» — печатаем кадры сами
            кадры = "".join("    %s:%d %s\n" % (os.path.basename(к.filename), к.lineno, к.line)
                            for к in traceback.extract_tb(е.__traceback__))
            print("  ОШИБКА сценарий упал: %s\n%s" % (str(е)[:500], кадры))
        finally:
            for действие, что in reversed(self.уборка):
                try:
                    действие()
                except Exception as е:
                    self.ошибок += 1
                    print("  ОШИБКА уборки %s: %s" % (что, е))

    def итог(self):
        сек = time.time() - self.начало
        метка = "  ПРЕДУПРЕЖДЕНИЕ: бюджет %d с превышен" % БЮДЖЕТ_СЕК if сек > БЮДЖЕТ_СЕК else ""
        print("== %s: проверок %d, ошибок %d, сценарий %.1f с (+ подключение %.1f с)%s"
              % (self.имя, self.проверок, self.ошибок, сек, self.подключение, метка))
        return 1 if self.ошибок else 0

    # ── помощники ──
    def массив(self, *значения):
        м = self.c.NewObject("Массив")
        for з in значения:
            м.Добавить(з)
        return м

    def удалить_объект(self, ссылка):
        о = ссылка.ПолучитьОбъект()
        if о is not None:
            о.Удалить()

    def найти_текст(self, тд, текст):
        """Есть ли текст в табличном документе (НайтиТекст ищет по частичному совпадению)."""
        return тд.НайтиТекст(текст) is not None

    def выбрать(self, текст, **параметры):
        з = self.c.NewObject("Запрос")
        з.Текст = текст
        for к, в in параметры.items():
            з.УстановитьПараметр(к, в)
        return з.Выполнить().Выгрузить()
