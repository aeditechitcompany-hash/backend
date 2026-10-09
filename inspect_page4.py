import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django
django.setup()

from mcq.services.mcq_importer import extract_pdf_data


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

pages = extract_pdf_data(PDF)

page = pages[3]

print("\n" + "=" * 100)
print("PAGE 4")
print("=" * 100)

for block in page["text_blocks"]:
    print(
        f"y0={block['y0']:.2f} | "
        f"y1={block['y1']:.2f} | "
        f"x={block['x0']:.2f} | "
        f"{block['text']}"
    )