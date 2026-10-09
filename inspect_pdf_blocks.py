import pymupdf


PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

doc = pymupdf.open(PDF)

try:
    for page_number in [3, 4]:

        page = doc[page_number - 1]

        print("\n" + "=" * 100)
        print(f"PAGE {page_number}")
        print("=" * 100)

        blocks = page.get_text("blocks")

        for block in blocks:

            if len(block) < 5:
                continue

            x0, y0, x1, y1, text = block[:5]

            text = text.replace("\n", " ").strip()

            if not text:
                continue

            print(
                f"y={y0:8.2f} | "
                f"x={x0:8.2f} | "
                f"x1={x1:8.2f} | "
                f"y1={y1:8.2f} | "
                f"{text}"
            )

finally:
    doc.close()