import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django
django.setup()

from mcq.services.pdf_parser import extract_pdf_pages


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

pages = extract_pdf_pages(PDF)

for page in pages:

    print("\n" + "=" * 90)
    print(f"PAGE {page['page_number']}")
    print(
        f"SIZE: {page['width']} x {page['height']}"
    )

    print("\nIMAGES:")

    if not page["images"]:
        print("  NO IMAGES")
        continue

    for image in page["images"]:

        print(
            f"  image_index={image['image_index']} "
            f"xref={image['xref']} "
            f"x0={image['x0']:.2f} "
            f"y0={image['y0']:.2f} "
            f"x1={image['x1']:.2f} "
            f"y1={image['y1']:.2f} "
            f"width={image['width']:.2f} "
            f"height={image['height']:.2f}"
        )