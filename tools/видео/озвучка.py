"""Озвучка видеоинструкции «Учёт занятий 2.0» — ElevenLabs, по фрагменту на сцену.

    python tools\\видео\\озвучка.py              основной и короткий ролики: чего не хватает или что изменилось
    python tools\\видео\\озвучка.py --заново     переозвучить всё

Текст — только из docs\\публикация\\сценарий_видео.md (цитаты `>` под заголовками `## N. …` с `**Сцена:** \\`имя\\``);
раздел «# Основной ролик» → ролик «основной», «# Короткий ролик» → «короткий». Голос и модель — как в роликах
«Путевых листов» (PUTEVYE_LISTY\\tools\\scripts\\озвучка_видео.py): Eric, eleven_multilingual_v2, те же настройки.
Готовый фрагмент не переозвучивается, пока его текст не изменился (сверка по расклад.json) — символы тарифа.
Ключ — %USERPROFILE%\\.elevenlabs_token или ELEVENLABS_API_KEY; в репозиторий и в вывод не попадает.
Итог — ВЫХОД\\озвучка-<ролик>\\NN_<сцена>.mp3 и расклад.json (имя, сцена, подпись, текст, секунд).
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "тесты"))
from сеанс import настроить_вывод  # noqa: E402

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
СЦЕНАРИЙ = os.path.join(КОРЕНЬ, "docs", "публикация", "сценарий_видео.md")
ВЫХОД = r"C:\1c_bases\видео\работа"          # звук и кадры — вне репозитория (объём)
ГОЛОС = "Eric"
МОДЕЛЬ = "eleven_multilingual_v2"
НАСТРОЙКИ = {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}


def ffmpeg():
    путь = r"C:\ffmpeg\bin\ffmpeg.exe"
    if os.path.isfile(путь):
        return путь
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def длительность(файл):
    итог = subprocess.run([ffmpeg(), "-i", файл, "-f", "null", "-"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    м = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", итог.stderr or "")
    if not м:
        return 0.0
    ч, мин, с = м[-1]
    return int(ч) * 3600 + int(мин) * 60 + float(с)


def реплики():
    """{'основной': [...], 'короткий': [...]}: имя, сцена, подпись, текст."""
    текст = io.open(СЦЕНАРИЙ, encoding="utf-8").read()
    итог = {}
    for часть in re.split(r"(?m)^# ", текст)[1:]:
        ролик = "основной" if часть.startswith("Основной") else "короткий" if часть.startswith("Короткий") else None
        if not ролик:
            continue
        список = []
        for кусок in re.split(r"(?m)^## ", часть)[1:]:
            строки = кусок.splitlines()
            м = re.match(r"^(К?\d+)\.\s*(.+?)\s*$", строки[0])
            if not м:
                continue
            сцена = next((re.search(r"`([^`]+)`", с).group(1) for с in строки if с.startswith("**Сцена:**")), "")
            реплика = " ".join(с[2:].strip() for с in строки if с.startswith("> "))
            if реплика:
                номер = м.group(1)
                список.append({"имя": "%s_%s" % (номер.zfill(2) if номер.isdigit() else номер, сцена),
                               "сцена": сцена, "подпись": м.group(2), "текст": реплика})
        итог[ролик] = список
    return итог


def ключ():
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"].strip()
    путь = os.path.join(os.path.expanduser("~"), ".elevenlabs_token")
    if not os.path.exists(путь):
        sys.exit("нет ключа ElevenLabs: %USERPROFILE%\\.elevenlabs_token")
    return io.open(путь, encoding="ascii").read().strip()


def голос(ключ_api):
    запрос = urllib.request.Request("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": ключ_api})
    for г in json.loads(urllib.request.urlopen(запрос, timeout=30).read()).get("voices", []):
        if г["name"].split(" - ")[0].strip().lower() == ГОЛОС.lower():
            return г["voice_id"]
    sys.exit("голос %s в каталоге ElevenLabs не найден" % ГОЛОС)


def синтез(текст, ид, ключ_api, путь):
    тело = json.dumps({"text": текст, "model_id": МОДЕЛЬ, "voice_settings": НАСТРОЙКИ}).encode("utf-8")
    запрос = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/%s" % ид, data=тело,
                                    headers={"xi-api-key": ключ_api, "Content-Type": "application/json",
                                             "Accept": "audio/mpeg"})
    with open(путь, "wb") as ф:
        ф.write(urllib.request.urlopen(запрос, timeout=180).read())


def главная():
    заново = "--заново" in sys.argv
    ид = ключ_api = None
    for ролик, список in реплики().items():
        папка = os.path.join(ВЫХОД, "озвучка-" + ролик)
        os.makedirs(папка, exist_ok=True)
        файл_расклада = os.path.join(папка, "расклад.json")
        было = {}
        if os.path.exists(файл_расклада):
            было = {р["имя"]: р["текст"] for р in json.load(io.open(файл_расклада, encoding="utf-8"))}
        всего, новых, знаков = 0.0, 0, 0
        for р in список:
            путь = os.path.join(папка, р["имя"] + ".mp3")
            if заново or not os.path.exists(путь) or было.get(р["имя"]) != р["текст"]:
                if ид is None:
                    ключ_api = ключ()
                    ид = голос(ключ_api)
                синтез(р["текст"], ид, ключ_api, путь)
                новых += 1
                знаков += len(р["текст"])
            р["секунд"] = round(длительность(путь), 2)
            всего += р["секунд"]
            print("  %-8s %-20s %5.1f с  %s" % (ролик, р["имя"], р["секунд"], р["подпись"]))
        with io.open(файл_расклада, "w", encoding="utf-8") as ф:
            json.dump(список, ф, ensure_ascii=False, indent=1)
        print("%s: реплик %d, озвучено заново %d (%d знаков), речь %d:%02d" % (
            ролик, len(список), новых, знаков, int(всего) // 60, int(всего) % 60))
    return 0


if __name__ == "__main__":
    настроить_вывод()
    sys.exit(главная())
