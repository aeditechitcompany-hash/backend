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


for item in result:

    print("\n" + "=" * 80)

    print(
        f"QUESTION {item['question_number']} "
        f"({item['section']})"
    )

    print(f"PAGE: {item['page_number']}")

    print(
        f"QUESTION TEXT: "
        f"{item['question_text']}"
    )

    print(
        f"OPTIONS: "
        f"{item['options']}"
    )

    # --------------------------------------------------------
    # IMAGES
    # --------------------------------------------------------

    images = item.get("images", [])

    print(
        f"IMAGE COUNT: "
        f"{len(images)}"
    )

    if images:

        for image in images:

            print(
                "  IMAGE: "
                f"page={image.get('page_number')} | "
                f"image={image.get('image_index')} | "
                f"xref={image.get('xref')} | "
                f"path={image.get('path')}"
            )

    else:

        print("  IMAGE: None")

    # --------------------------------------------------------
    # OPTION IMAGES
    # --------------------------------------------------------

    option_images = item.get(
        "option_images",
        {}
    )

    print(
        f"OPTION IMAGE COUNT: "
        f"{len(option_images)}"
    )

    if option_images:

        for option_number, image in option_images.items():

            print(
                f"  OPTION {option_number}: "
                f"page={image.get('page_number')} | "
                f"image={image.get('image_index')} | "
                f"xref={image.get('xref')} | "
                f"path={image.get('path')}"
            )

    else:

        print("  OPTION IMAGES: None")

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    audio = item.get(
        "audio",
        {},
    )

    print(
        f"AUDIO: "
        f"{audio}"
    )

    # --------------------------------------------------------
    # REVIEW
    # --------------------------------------------------------

    print(
        f"NEEDS REVIEW: "
        f"{item['needs_review']}"
    )