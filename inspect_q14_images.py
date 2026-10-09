import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from mcq.services.pdf_question_images import build_question_image_map

PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"
OUTPUT = r"D:\nibangsh_app\backend\temp_pdf_images"

question_images = build_question_image_map(PDF, OUTPUT)

print("\n" + "=" * 80)
print("Q14 IMAGE CHECK")
print("=" * 80)

for question_number in [10, 11, 12, 13, 14]:
    images = question_images.get(question_number, [])

    print(f"\nQUESTION {question_number}")
    print(f"IMAGE COUNT: {len(images)}")

    for image in images:
        print(
            f"  PAGE {image['page_number']} | "
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
