import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

import pymupdf


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"


document = pymupdf.open(PDF)

try:

    for page_number in [5]:

        page = document[page_number - 1]

        print("\n" + "=" * 80)
        print(f"PAGE {page_number}")
        print("=" * 80)

        blocks = page.get_text("blocks")

        blocks = sorted(
            blocks,
            key=lambda block: (
                round(block[1], 2),
                round(block[0], 2),
            ),
        )

        for index, block in enumerate(blocks):

            if len(block) < 5:
                continue

            x0, y0, x1, y1, text = block[:5]

            print(
                f"\nBLOCK {index}"
            )

            print(
                f"x0={x0:.2f} "
                f"y0={y0:.2f} "
                f"x1={x1:.2f} "
                f"y1={y1:.2f}"
            )

            print(
                f"TEXT: {text!r}"
            )

finally:

    document.close()