from pathlib import Path

from mcq.services.mcq_importer import (
    clean_text,
    extract_pdf_data,
    get_section,
    split_options,
)
from mcq.services.pdf_images import extract_pdf_images


# Set24: question number -> (PDF page, start Y, end Y).
QUESTION_REGIONS = {
    1: (1, 220, 420),
    2: (1, 420, 555),
    3: (1, 555, 760),
    4: (2, 20, 155),
    5: (2, 155, 260),
    6: (2, 260, 410),
    7: (2, 410, 590),
    8: (2, 590, 750),
    9: (3, 50, 180),
    10: (3, 180, 310),
    11: (3, 310, 545),
    12: (3, 545, 760),
    13: (4, 20, 280),
    14: (4, 310, 730),
    15: (5, 20, 340),
    16: (5, 345, 545),
    17: (5, 545, 760),
    18: (6, 20, 235),
    19: (6, 235, 420),
    20: (6, 420, 560),
    21: (6, 605, 670),
    22: (6, 670, 760),
    23: (7, 60, 250),
    24: (7, 250, 460),
    25: (7, 460, 750),
    26: (8, 25, 220),
    27: (8, 220, 415),
    28: (8, 415, 650),
    29: (9, 70, 145),
    30: (9, 145, 215),
    31: (9, 215, 280),
    32: (9, 280, 345),
    33: (9, 345, 400),
    34: (9, 430, 500),
    35: (9, 510, 710),
    36: (10, 20, 230),
    37: (10, 230, 490),
    38: (10, 520, 710),
    39: (11, 90, 290),
    40: (11, 300, 490),
}


QUESTION_INSTRUCTIONS = {
    1: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    2: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    3: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    4: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    5: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    6: "빈칸에 들어갈 가장 알맞은 것을 고르십시오.",
    7: "다음 중 밑줄 친 부분이 맞는 문장을 고르십시오.",
    8: "다음 중 밑줄 친 부분이 맞는 문장을 고르십시오.",
    16: "다음 그림을 보고 맞는 단어나 문장을 고르십시오.",
    17: "다음 그림을 보고 맞는 단어나 문장을 고르십시오.",
    23: "들은 내용과 관계있는 그림을 고르십시오.",
    24: "들은 내용과 관계있는 그림을 고르십시오.",
    25: "들은 내용과 관계있는 그림을 고르십시오.",
    26: "들은 내용과 관계있는 그림을 고르십시오.",
    27: "들은 내용과 관계있는 그림을 고르십시오.",
    28: "들은 내용과 관계있는 그림을 고르십시오.",
    29: "듣고 물음에 알맞은 대답을 고르십시오.",
    30: "듣고 물음에 알맞은 대답을 고르십시오.",
    31: "듣고 물음에 알맞은 대답을 고르십시오.",
    32: "듣고 물음에 알맞은 대답을 고르십시오.",
    33: "듣고 물음에 알맞은 대답을 고르십시오.",
    34: "듣고 이어지는 말로 가장 알맞은 것을 고르십시오.",
    35: "들은 내용과 관계있는 그림을 고르십시오.",
    36: "들은 내용과 관계있는 그림을 고르십시오.",
    37: "들은 내용과 관계있는 그림을 고르십시오.",
}


def _group_instruction(number):
    return QUESTION_INSTRUCTIONS.get(number, "")
def parse_set24_import(
    pdf_path,
    listening_start=21,
    listening_end=40,
    audio_filenames=None,
    image_output_dir=None,
):
    """
    Parse Set24 without writing to the database.

    Images are attached to questions for review. This version
    deliberately does not guess how to split a composite image
    into four separate answer-option images.
    """
    pdf_path = Path(pdf_path)
    pages = extract_pdf_data(pdf_path)

    if len(pages) != 11:
        raise ValueError(
            f"Expected 11 Set24 pages; found {len(pages)}."
        )

    page_lookup = {p["page_number"]: p for p in pages}

    if image_output_dir is None:
        image_output_dir = (
            pdf_path.parent.parent.parent
            / "temp_set24_images"
        )

    image_output_dir = Path(image_output_dir)
    image_output_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = extract_pdf_images(
        pdf_path,
        str(image_output_dir),
    )

    # Attach images by their actual page coordinates.
    images_by_page = {}
    for image in extracted_images:
        images_by_page.setdefault(
            image["page_number"], []
        ).append(image)

    records = []

    for number in range(1, 41):
        page_number, y_start, y_end = QUESTION_REGIONS[number]
        page = page_lookup[page_number]

        question_parts = []
        options = {}

        blocks = sorted(
            (
                block for block in page["text_blocks"]
                if block["y1"] > y_start
                and block["y0"] < y_end
            ),
            key=lambda block: (
                round(block["y0"], 2),
                round(block["x0"], 2),
            ),
        )

        for block in blocks:
            text = clean_text(block["text"])
            if not text:
                continue
            # Q11 graph labels belong to the embedded graph,
            # not to the question's written prompt.
            if number == 11 and 360 <= block["y0"] < 510:
                continue
            # Remove the explicit number for this question.
            prefix = f"{number}."
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
            elif text == f"{number}":
                continue

            parsed = split_options(text)
            if parsed:
                options.update(parsed)
                continue

            # Skip labels without actual option text.
            if text.replace(" ", "") in {
                "①②③④", "➀➁➂➃"
            }:
                continue

            # Ignore section headings and question numbers.
            if text.startswith("[") and "]" in text:
                continue

            question_parts.append(text)

        question_text = clean_text(" ".join(question_parts))

        if not question_text:
            question_text = _group_instruction(number)

        # Only attach images that overlap this question's region.
       
      
        # Only attach images that overlap this question's region.


        question_images = []
        for image in images_by_page.get(page_number, []):
            if not (
                image["y1"] > y_start
                and image["y0"] < y_end
            ):
                continue

            # Ignore the duplicate nested image for Set24 Q27.
            if (
                number == 27
                and page_number == 8
                and image["xref"] == 72
            ):
                continue

            question_images.append({
                "page_number": image["page_number"],
                "image_index": image["image_index"],
                "xref": image["xref"],
                "path": image["path"],
                "x0": image["x0"],
                "y0": image["y0"],
                "x1": image["x1"],
                "y1": image["y1"],
            })

        records.append({
            "question_number": number,
            "section": get_section(
                number, listening_start, listening_end
            ),
            "page_number": page_number,
            "question_text": question_text,
            "options": dict(sorted(options.items())),
            "images": question_images,
            "option_images": {},
            "audio": {},
            "needs_review": True,
        })

    return records
