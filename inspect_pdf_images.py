import pymupdf
from pathlib import Path

pdf_path = Path(r"D:\nibangsh_app\backend\Full set 1 F.pdf")

doc = pymupdf.open(pdf_path)

for page_index in range(4, 8):
    page = doc[page_index]

    images = page.get_images(full=True)

    print("\n" + "=" * 80)
    print(f"PAGE {page_index + 1}")
    print(f"NUMBER OF IMAGES: {len(images)}")
    print("=" * 80)

    for i, img in enumerate(images):
        xref = img[0]

        try:
            rects = page.get_image_rects(xref)
        except Exception:
            rects = []

        print(f"\nImage {i + 1}")
        print(f"  XREF: {xref}")
        print(f"  Rectangles: {rects}")

doc.close()