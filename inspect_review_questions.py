import pymupdf

PDF = r"D:\nibangsh_app\backend\Full set 1 F.pdf"

doc = pymupdf.open(PDF)

checks = {
    5: (677, 900),       # Q24
    7: (205, 481),       # Q29-Q33
}

for page_number, (y_start, y_end) in checks.items():

    page = doc[page_number - 1]

    print()
    print("=" * 100)
    print(f"PAGE {page_number}")
    print(f"Y RANGE: {y_start} -> {y_end}")
    print("=" * 100)

    blocks = page.get_text("blocks")

    for block in blocks:
        x0, y0, x1, y1, text = block[:5]

        if y1 <= y_start or y0 >= y_end:
            continue

        text = text.replace("\n", " ")

        print(
            f"y={y0:.2f} -> {y1:.2f} | "
            f"x={x0:.2f} -> {x1:.2f} | "
            f"{text}"
        )

doc.close()
