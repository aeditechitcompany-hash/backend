import re
from pathlib import Path

from mcq.services.pdf_question_images import build_question_image_map

import pymupdf

from .audio_import import build_audio_map


# ============================================================
# OPTION LABELS
# ============================================================

OPTION_LABELS = {
    "①": 1,
    "➀": 1,
    "②": 2,
    "➁": 2,
    "③": 3,
    "➂": 3,
    "④": 4,
    "➃": 4,
}


QUESTION_PATTERN = re.compile(
    r"^\s*(\d{1,3})\s*[\.\)]?\s*(.*)$"
)


GROUP_PATTERN = re.compile(
    r"^\s*\[\s*(\d+)\s*[~\-]\s*(\d+)\s*\]"
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def restore_blank_marker(question_number, text):
    """
    Restore the visual blank position for questions where the
    PDF text layer does not contain an explicit blank marker.
    """

    if not text:
        return text

    if question_number == 11:
        marker = "\uB530\uB73B\uD55C"
        text = re.sub(
            marker + r"\s+\uC637\uC744\s+\uAC00\uB294\uAC83\uC774\uC88B\uACA0\uC2B5\uB2C8\uB2E4\.",
            "\uB530\uB73B\uD55C \uC637\uC744 [BLANK] \uAC00\uB294\uAC83\uC774\uC88B\uACA0\uC2B5\uB2C8\uB2E4.",
            text,
        )

    if question_number == 12:
        text = re.sub(
            r"\uC790\uC2E0\uC758\s+\uB9CC\uB9D0\uD558\uAE30\uBCF4\uB2E4",
            "\uC790\uC2E0\uC758 [BLANK] \uB9CC\uB9D0\uD558\uAE30\uBCF4\uB2E4",
            text,
        )

    if question_number == 13:
        text = re.sub(
            r"\uAE30\uACC4\uC758\uC0C1\uD0DC\uB97C\uBC18\uB4DC\uC2DC\s+\uC791\uC5C5\uD574\uC57C\uD569\uB2C8\uB2E4\.",
            "\uAE30\uACC4\uC758\uC0C1\uD0DC\uB97C\uBC18\uB4DC\uC2DC [BLANK] \uC791\uC5C5\uD574\uC57C\uD569\uB2C8\uB2E4.",
            text,
        )

    return text

def extract_question_number(text):
    """
    Detect:

        1.
        2.
        10.
        11
        15.
    """

    text = clean_text(text)

    match = QUESTION_PATTERN.match(text)

    if not match:
        return None

    return int(match.group(1))


def remove_question_number(text):
    text = clean_text(text)

    match = QUESTION_PATTERN.match(text)

    if not match:
        return text

    return clean_text(match.group(2))


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_data(pdf_path):
    """
    Extract text blocks and images with coordinates.

    This function does NOT create database records.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    pages = []

    try:

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            blocks = []

            for block in page.get_text("blocks"):

                if len(block) < 5:
                    continue

                x0, y0, x1, y1, text = block[:5]

                text = clean_text(text)

                if not text:
                    continue

                blocks.append(
                    {
                        "x0": float(x0),
                        "y0": float(y0),
                        "x1": float(x1),
                        "y1": float(y1),
                        "text": text,
                    }
                )

            blocks.sort(
                key=lambda item: (
                    round(item["y0"], 2),
                    round(item["x0"], 2),
                )
            )

            images = []

            seen_xrefs = set()

            for image_index, image in enumerate(
                page.get_images(full=True),
                start=1,
            ):

                xref = image[0]

                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                rects = page.get_image_rects(xref)

                for rect in rects:

                    images.append(
                        {
                            "image_index": image_index,
                            "xref": xref,
                            "x0": float(rect.x0),
                            "y0": float(rect.y0),
                            "x1": float(rect.x1),
                            "y1": float(rect.y1),
                            "width": float(rect.width),
                            "height": float(rect.height),
                        }
                    )

            images.sort(
                key=lambda item: (
                    round(item["y0"], 2),
                    round(item["x0"], 2),
                )
            )

            pages.append(
                {
                    "page_number": page_number,
                    "width": float(page.rect.width),
                    "height": float(page.rect.height),
                    "text_blocks": blocks,
                    "images": images,
                }
            )

    finally:
        document.close()

    return pages


# ============================================================
# OPTION PARSING
# ============================================================

def split_options(text):
    """
    Extract options from text containing circled-number labels.

    Supports:
        ①text
        ②text
        ③text
        ④text

    and:
        ➀text
        ➁text
        ➂text
        ➃text

    Options may appear on the same line.
    """

    if not text:
        return {}

    pattern = re.compile(
        r"(?:^|\s)"
        r"([①➀②➁③➂④➃])"
    )

    matches = list(pattern.finditer(text))

    if not matches:
        return {}

    options = {}

    label_map = {
        "①": 1,
        "➀": 1,
        "②": 2,
        "➁": 2,
        "③": 3,
        "➂": 3,
        "④": 4,
        "➃": 4,
    }

    for index, match in enumerate(matches):

        label = match.group(1)

        option_number = label_map[label]

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        option_text = text[start:end].strip()

        if option_text:
            options[option_number] = option_text

    return options
def is_option_block(text):
    """
    True when the block contains one or more
    circled option labels.
    """

    return bool(
        re.search(
            r"[①➀②➁③➂④➃]",
            text,
        )
    )


# ============================================================
# PAGE / QUESTION BOUNDARIES
# ============================================================

def get_question_ranges(page_number):
    """
    Exact question boundaries for this PDF.

    These boundaries are based on the actual PDF
    coordinates we inspected.
    """

    ranges = {

        # ----------------------------------------------------
        # PAGE 1
        # ----------------------------------------------------

        1: [
            (1, 0, 180),
            (2, 180, 330),
            (3, 330, 470),
            (4, 470, 900),
        ],

        # ----------------------------------------------------
        # PAGE 2
        # ----------------------------------------------------

        2: [
            (5, 0, 213),
            (6, 213, 340),
            (7, 340, 500),
            (8, 500, 900),
        ],

        # ----------------------------------------------------
        # PAGE 3
        # ----------------------------------------------------

        3: [
            (9, 0, 102),
            (10, 102, 357),
            (11, 357, 477),
            (12, 477, 599),
            (13, 599, 721),
            (14, 721, 900),
        ],

        # ----------------------------------------------------
        # PAGE 4
        # ----------------------------------------------------

        4: [
            (15, 126, 248),
            (16, 248, 466),
            (17, 466, 713),
        ],

        # ----------------------------------------------------
        # PAGE 5
        # ----------------------------------------------------

        5: [
            (18, 0, 138),
            (19, 138, 228),
            (20, 228, 462),
            (21, 462, 510),
            (22, 510, 534),
            (23, 534, 677),
            (24, 677, 900),
        ],

        # ----------------------------------------------------
        # PAGE 6
        # ----------------------------------------------------

        6: [
            (25, 0, 357),
            (26, 357, 563),
            (27, 563, 717),
            (28, 717, 900),
        ],

        # ----------------------------------------------------
        # PAGE 7
        # ----------------------------------------------------

        7: [
            (28, 0, 205),
            (29, 205, 286),
            (30, 286, 335),
            (31, 335, 384),
            (32, 384, 432),
            (33, 432, 481),
            (34, 481, 600),
            (35, 600, 900),
        ],

        # ----------------------------------------------------
        # PAGE 8
        # ----------------------------------------------------

        8: [
            (36, 0, 143),
            (37, 143, 351),
            (38, 351, 445),
            (39, 445, 522),
            (40, 522, 717),
        ],
    }

    return ranges.get(page_number, [])


# ============================================================
# QUESTION CONTENT
# ============================================================

def extract_question_content(page, question_number):
    page_number = page["page_number"]

    # ============================================================
    # SPECIAL CASE: QUESTION 14 CONTINUES FROM PAGE 3 TO PAGE 4
    # ============================================================
    #
    # Page 3 contains only:
    #     14.
    #
    # The actual Q14 text and options are at the top of page 4,
    # immediately before question 15.
    #
    # We deliberately keep this special case here instead of
    # changing the general question-page mapping.
    #
    if question_number == 14:
        if page_number == 3:
            # Page 3 contains only the Q14 number.
            for block in page["text_blocks"]:
                text = clean_text(block["text"])

                if extract_question_number(text) == 14:
                    return {
                        "question_text": "",
                        "options": {},
                    }

            return {
                "question_text": "",
                "options": {},
            }

        if page_number == 4:
            selected_blocks = []

            for block in page["text_blocks"]:
                y0 = block["y0"]
                y1 = block["y1"]

                # Q14 occupies the top portion of page 4.
                # Stop before question 15.
                if y1 <= 0:
                    continue

                if y0 >= 126.85:
                    continue

                selected_blocks.append(block)

            selected_blocks.sort(
                key=lambda item: (
                    round(item["y0"], 2),
                    round(item["x0"], 2),
                )
            )

            question_parts = []
            options = {}
            last_option_number = None

            for block in selected_blocks:
                text = clean_text(block["text"])

                if not text:
                    continue

                # Ignore any question number.
                number = extract_question_number(text)

                if number is not None:
                    if number == 14:
                        remainder = clean_text(
                            remove_question_number(text)
                        )

                        if remainder:
                            question_parts.append(remainder)

                    continue

                # Ignore section/group headings.
                if GROUP_PATTERN.match(text):
                    continue

                if text in {"듣기", "끝났어요"}:
                    continue

                # Parse blocks containing circled options.
                if is_option_block(text):
                    parsed = split_options(text)

                    for option_number, option_text in parsed.items():
                        options[option_number] = option_text
                        last_option_number = option_number

                    continue

                if re.search(r"[①➀②➁③➂④➃]", text):
                    parsed = split_options(text)

                    if parsed:
                        for option_number, option_text in parsed.items():
                            options[option_number] = option_text
                            last_option_number = option_number

                        continue

                # Ignore separator-only blocks.
                if re.fullmatch(
                    r"[\s/|①➀②➁③➂④➃]+",
                    text,
                ):
                    continue

                # Continuation of an option.
                if last_option_number is not None:
                    options[last_option_number] = clean_text(
                        options[last_option_number]
                        + " "
                        + text
                    )
                    continue

                question_parts.append(text)

            question_text = clean_text(
                " ".join(question_parts)
            )

            question_text = restore_blank_marker(
                question_number,
                question_text,
            )

            return {
                "question_text": question_text,
                "options": dict(sorted(options.items())),
            }

        # Q14 has no content on any other page.
        return {
            "question_text": "",
            "options": {},
        }

    # ============================================================
    # NORMAL SINGLE-PAGE QUESTIONS
    # ============================================================

    ranges = get_question_ranges(page_number)

    question_range = None

    for number, y_start, y_end in ranges:
        if number == question_number:
            question_range = (y_start, y_end)
            break

    if question_range is None:
        return {
            "question_text": "",
            "options": {},
        }

    y_start, y_end = question_range

    selected_blocks = []

    for block in page["text_blocks"]:
        y0 = block["y0"]
        y1 = block["y1"]

        if y1 <= y_start:
            continue

        if y0 >= y_end:
            continue

        selected_blocks.append(block)

    selected_blocks.sort(
        key=lambda item: (
            round(item["y0"], 2),
            round(item["x0"], 2),
        )
    )

    question_parts = []
    options = {}
    last_option_number = None

    for block in selected_blocks:
        text = clean_text(block["text"])

        if not text:
            continue

        # Page 1 contains a header above Q1.
        if (
            page_number == 1
            and question_number == 1
            and block["y1"] <= 175.66
        ):
            continue

        if GROUP_PATTERN.match(text):
            continue

        if text in {"듣기", "끝났어요"}:
            continue

        number = extract_question_number(text)

        if number is not None:
            if number != question_number:
                continue

            remainder = clean_text(
                remove_question_number(text)
            )

            if not remainder:
                continue

            if re.search(
                r"[\u2460\u2780\u2461\u2781\u2462\u2782\u2463\u2783]",
                remainder,
            ):
                option_match = re.search(
                    r"[\u2460\u2780\u2461\u2781\u2462\u2782\u2463\u2783]",
                    remainder,
                )

                if option_match:
                    before_options = clean_text(
                        remainder[:option_match.start()]
                    )

                    if before_options:
                        question_parts.append(before_options)

                parsed = split_options(remainder)

                for option_number, option_text in parsed.items():
                    options[option_number] = option_text
                    last_option_number = option_number

                continue

            question_parts.append(remainder)
            last_option_number = None

            continue

        if is_option_block(text):
            option_match = re.search(
                r"[\u2460\u2780\u2461\u2781\u2462\u2782\u2463\u2783]",
                text,
            )

            if option_match:
                before_options = clean_text(
                    text[:option_match.start()]
                )

                if before_options:
                    question_parts.append(before_options)

            parsed = split_options(text)

            for option_number, option_text in parsed.items():
                options[option_number] = option_text
                last_option_number = option_number

            continue

        if re.search(
            r"[①➀②➁③➂④➃]",
            text,
        ):
            parsed = split_options(text)

            if parsed:
                for option_number, option_text in parsed.items():
                    options[option_number] = option_text
                    last_option_number = option_number

                continue

        if re.fullmatch(
            r"[\s/|①➀②➁③➂④➃]+",
            text,
        ):
            continue

        if last_option_number is not None:
            options[last_option_number] = clean_text(
                options[last_option_number]
                + " "
                + text
            )
            continue

        if text.startswith("[") and "]" in text:
            continue

        question_parts.append(text)

    question_text = clean_text(
        " ".join(question_parts)
    )

    question_text = restore_blank_marker(
        question_number,
        question_text,
    )

    return {
        "question_text": question_text,
        "options": dict(sorted(options.items())),
    }
# ============================================================
# IMAGE ASSIGNMENT
# ============================================================

def image_matches_region(
    image,
    y_start,
    y_end,
):
    """
    Image overlaps a vertical question region.
    """

    image_y0 = image["y0"]
    image_y1 = image["y1"]

    return (
        image_y1 > y_start
        and image_y0 < y_end
    )


def assign_images_to_question(
    page,
    question_number,
):
    """
    Preserve the known image layout of this PDF.
    """

    page_number = page["page_number"]

    images = page["images"]

    result = []

    # ========================================================
    # PAGE 5
    # ========================================================

    if page_number == 5:

        # Q21-Q24 use the image area at the bottom.
        if question_number in {
            21,
            22,
            23,
            24,
        }:

            for image in images:

                if image["y0"] >= 550:

                    result.append(image)

            return result

    # ========================================================
    # PAGE 6
    # ========================================================

    if page_number == 6:

        if question_number == 25:

            for image in images:

                if image["y0"] <= 160:

                    result.append(image)

            return result

        if question_number == 26:

            for image in images:

                if (
                    image["y0"] >= 160
                    and image["y1"] <= 360
                ):
                    result.append(image)

            return result

        if question_number == 27:

            for image in images:

                if (
                    image["y0"] >= 400
                    and image["y1"] <= 560
                ):
                    result.append(image)

            return result

        if question_number == 28:

            for image in images:

                if image["y0"] >= 560:

                    result.append(image)

            return result

    # ========================================================
    # PAGE 7
    # ========================================================

    if page_number == 7:

        # Q28 continues at top of page 7.
        if question_number == 28:

            for image in images:

                if image["y1"] <= 205:

                    result.append(image)

            return result

        # Q35-Q36 image area.
        if question_number in {
            35,
            36,
        }:

            for image in images:

                if image["y0"] >= 600:

                    result.append(image)

            return result

        # Q29-Q33 have no embedded images in this PDF.
        return []

    # ========================================================
    # PAGE 8
    # ========================================================

    if page_number == 8:

        # Q36 uses four images at the top.
        if question_number == 36:

            for image in images:

                if image["y1"] <= 150:

                    result.append(image)

            return result

        # Q37 uses the large image below.
        if question_number == 37:

            for image in images:

                if image["y0"] >= 150:

                    result.append(image)

            return result

    return []


# ============================================================
# SECTION
# ============================================================

def get_section(
    question_number,
    listening_start=21,
    listening_end=40,
):
    if (
        listening_start
        <= question_number
        <= listening_end
    ):
        return "listening"

    return "reading"


# ============================================================
# QUESTION NUMBER DISCOVERY
# ============================================================

def discover_questions(pages):
    """
    Discover question numbers from explicit numbered
    blocks.

    This supplements the fixed boundaries above.
    """

    discovered = {}

    for page in pages:

        page_number = page["page_number"]

        for block in page["text_blocks"]:

            text = clean_text(
                block["text"]
            )

            number = extract_question_number(
                text
            )

            if number is None:
                continue

            if number < 1 or number > 100:
                continue

            discovered[number] = page_number

    return discovered


# ============================================================
# AUDIO
# ============================================================

def build_audio_for_questions(
    audio_filenames,
):
    if not audio_filenames:
        return {}

    return build_audio_map(
        audio_filenames
    )


# ============================================================
# MAIN IMPORT PARSER
# ============================================================

def parse_import(
    pdf_path,
    listening_start=21,
    listening_end=40,
    audio_filenames=None,
):
    """
    Parse a PDF into MCQ import records.

    IMPORTANT:

    This function DOES NOT create database records.

    It only returns structured Python dictionaries.
    """

    pages = extract_pdf_data(
        pdf_path
    )

    # --------------------------------------------------------
    # All question numbers for this PDF.
    #
    # The supplied PDF contains Q1-Q40.
    # --------------------------------------------------------

    question_numbers = list(
        range(1, 41)
    )

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    audio_map = build_audio_for_questions(
        audio_filenames
    )

        # --------------------------------------------------------
    # Question image mapping
    # --------------------------------------------------------

    question_image_map = build_question_image_map(
        pdf_path,
        r"D:\nibangsh_app\backend\temp_pdf_images",
    )

    # --------------------------------------------------------
    # Page lookup
    # --------------------------------------------------------

    page_lookup = {
        page["page_number"]: page
        for page in pages
    }

    # --------------------------------------------------------
    # Known page mapping
    # --------------------------------------------------------

    question_page_map = {

        # Reading
        1: 1,
        2: 1,
        3: 1,
        4: 1,

        5: 2,
        6: 2,
        7: 2,
        8: 2,

        9: 3,
        10: 3,
        11: 3,
        12: 3,
        13: 3,
        14: 3,

        15: 4,
        16: 4,
        17: 4,

        18: 5,
        19: 5,
        20: 5,

        # Listening
        21: 5,
        22: 5,
        23: 5,
        24: 5,

        25: 6,
        26: 6,
        27: 6,
        28: 7,

        29: 7,
        30: 7,
        31: 7,
        32: 7,
        33: 7,
        34: 7,
        35: 7,

        36: 8,
        37: 8,
        38: 8,
        39: 8,
        40: 8,
    }

    results = []

    for question_number in question_numbers:

        page_number = question_page_map.get(
            question_number
        )

        page = page_lookup.get(
            page_number
        )

        if page is None:

            results.append(
                {
                    "question_number": question_number,
                    "section": get_section(
                        question_number,
                        listening_start,
                        listening_end,
                    ),
                    "page_number": page_number,
                    "question_text": "",
                    "options": {},
                    "images": [],
                    "audio": audio_map.get(
                        question_number,
                        {},
                    ),
                    "needs_review": True,
                }
            )

            continue

                # ----------------------------------------------------
        # Extract question content
        # ----------------------------------------------------
        #
        # Q14 starts on page 3 but its actual text/options
        # continue onto the top of page 4.
        #
        # Keep Q14's official page mapping as page 3, but
        # extract its content from page 4.
        #

        if question_number == 14:
            content_page = page_lookup.get(4)

            if content_page is not None:
                content = extract_question_content(
                    content_page,
                    question_number,
                )
            else:
                content = {
                    "question_text": "",
                    "options": {},
                }

        else:
            content = extract_question_content(
                page,
                question_number,
            )

        images = question_image_map.get(
            question_number,
            [],
        )

        # ----------------------------------------------------
        # Option images
        # ----------------------------------------------------
        #
        # Q25 has exactly four images, and they are the
        # four answer choices:
        #
        # image 1 -> option 1
        # image 2 -> option 2
        # image 3 -> option 3
        # image 4 -> option 4
        #
        # Keep this separate from the general question image
        # list. Do not modify the image mapping itself.
        #

        option_images = {}

        if question_number in {23, 25, 35, 36}:
            sorted_option_images = sorted(
                images,
                key=lambda image: image.get("x0", 0),
            )

            for option_number, image in enumerate(
                sorted_option_images,
                start=1,
            ):
                option_images[option_number] = image
        
        audio = audio_map.get(
            question_number,
            {},
        )

        # ----------------------------------------------------
        # Review rules
        # ----------------------------------------------------

        needs_review = False

        # No question text AND no options AND no images.
        if not (
            content["question_text"]
            or content["options"]
            or images
        ):
            needs_review = True

        # Text questions without options should be reviewed.
        if (
            content["question_text"]
            and not content["options"]
            and not images
        ):
            needs_review = True

        # Listening image questions are valid if images exist.
        if (
            get_section(
                question_number,
                listening_start,
                listening_end,
            )
            == "listening"
            and images
        ):
            needs_review = False

        # ----------------------------------------------------
        # Special known image/audio questions
        # ----------------------------------------------------

        if question_number in {
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            35,
            36,
            37,
        }:

            # Some of these questions depend on visual/audio
            # material and may legitimately have no text options.
            #
            # Q29-Q33 have no embedded images in this PDF,
            # so keep them marked for review.
            if question_number in {
                29,
                30,
                31,
                32,
                33,
            }:
                needs_review = True

        results.append(
            {
                "question_number": question_number,

                "section": get_section(
                    question_number,
                    listening_start,
                    listening_end,
                ),

                "page_number": page_number,

                "question_text": content[
                    "question_text"
                ],

                "options": content[
                    "options"
                ],

                "images": images,
                "option_images": option_images,
                "audio": audio,

                "needs_review": needs_review,
            }
        )

    return results

