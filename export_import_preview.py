import os
import sys
import json

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


OUTPUT = r"D:\nibangsh_app\backend\mcq_import_preview.json"


with open(
    OUTPUT,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        result,
        file,
        ensure_ascii=False,
        indent=2,
    )


print()
print("=" * 80)
print("IMPORT PREVIEW CREATED")
print("=" * 80)
print()
print(f"Questions: {len(result)}")
print(f"Output:    {OUTPUT}")
print()


review_questions = [
    item["question_number"]
    for item in result
    if item.get("needs_review")
]


print(
    "Questions needing review:",
    review_questions,
)


print()
print("Image summary:")


for item in result:

    images = item.get("images", [])
    option_images = item.get("option_images", {})
    audio = item.get("audio", {})

    if images or option_images or audio:

        print(
            f"Q{item['question_number']}: "
            f"images={len(images)}, "
            f"option_images={len(option_images)}, "
            f"audio={audio}"
        )


print()
print("=" * 80)
print("DONE")
print("=" * 80)