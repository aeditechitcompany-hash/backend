import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from mcq.services.mcq_importer import parse_import


sys.stdout.reconfigure(encoding="utf-8")


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

AUDIO_FILES = [
    "21.mp3",
    "25-1.mp3",
]


result = parse_import(
    PDF,
    listening_start=21,
    listening_end=40,
    audio_filenames=AUDIO_FILES,
)


QUESTIONS = {23, 25, 35, 36}


for item in result:

    question_number = item["question_number"]

    if question_number not in QUESTIONS:
        continue

    print("\n" + "=" * 80)
    print(f"QUESTION {question_number}")
    print("=" * 80)

    option_images = item.get("option_images", {})

    if not option_images:
        print("NO OPTION IMAGES")
        continue

    for option_number, image in option_images.items():

        print(
            f"OPTION {option_number}: "
            f"{image.get('path')}"
        )