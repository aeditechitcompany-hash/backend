import os
import sys

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from mcq.services.pdf_parser import extract_pdf_pages


# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

pages = extract_pdf_pages(PDF)


for page in pages:

    print("\n")
    print("=" * 100)
    print(f"PAGE {page['page_number']}")
    print("=" * 100)

    for block in page["text_blocks"]:

        print(
            f"Y={block['y0']:7.2f} "
            f"X={block['x0']:7.2f} "
            f"TEXT={block['text']}"
        )