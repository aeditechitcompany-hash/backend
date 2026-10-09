import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django
django.setup()

from mcq.services.pdf_images import (
    extract_pdf_images,
)


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

OUTPUT = r"D:\nibangsh_app\backend\temp_pdf_images"


images = extract_pdf_images(
    PDF,
    OUTPUT,
)


print("\n" + "=" * 80)
print("EXTRACTED IMAGES")
print("=" * 80)

for image in images:

    print(
        f"PAGE {image['page_number']} | "
        f"image={image['image_index']} | "
        f"xref={image['xref']} | "
        f"("
        f"{image['x0']:.1f}, "
        f"{image['y0']:.1f}"
        f") -> "
        f"("
        f"{image['x1']:.1f}, "
        f"{image['y1']:.1f}"
        f") | "
        f"{image['path']}"
    )


print("\nTOTAL:", len(images))
print("OUTPUT:", OUTPUT)