import pymupdf

PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

document = pymupdf.open(PDF)

print("=" * 100)
print("PAGES 5-8 TEXT BLOCKS")
print("=" * 100)

for page in document[4:8]:
    print()
    print("=" * 100)
    print(f"PAGE {page.number + 1}")
    print("=" * 100)

    blocks = page.get_text("blocks")

    for block in blocks:
        if len(block) < 5:
            continue

        x0, y0, x1, y1, text = block[:5]

        text = text.strip()

        if not text:
            continue

        text = text.replace("\n", " / ")

        print(
            f"y={y0:7.2f} | "
            f"x={x0:7.2f} | "
            f"x1={x1:7.2f} | "
            f"y1={y1:7.2f} | "
            f"{text}"
        )

document.close()