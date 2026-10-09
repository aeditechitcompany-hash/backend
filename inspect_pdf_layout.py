import pymupdf
from pathlib import Path

pdf_path = Path(r"D:\nibangsh_app\backend\Full set 1 F.pdf")

doc = pymupdf.open(pdf_path)

for page_index in range(4, 8):  # pages 5-8
    page = doc[page_index]

    print("\n" + "=" * 100)
    print(f"PAGE {page_index + 1}")
    print("=" * 100)

    blocks = page.get_text("blocks")

    # Sort by vertical position, then horizontal position
    blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))

    for i, block in enumerate(blocks):
        x0, y0, x1, y1, text = block[:5]

        text = " ".join(text.split())

        if text:
            print(
                f"\nBLOCK {i}"
                f"\n  X: {x0:.1f} -> {x1:.1f}"
                f"\n  Y: {y0:.1f} -> {y1:.1f}"
                f"\n  TEXT: {text}"
            )

    print("\nPAGE SIZE:", page.rect.width, "x", page.rect.height)

doc.close()