from pathlib import Path

from mcq.services.pdf_images import extract_pdf_images


def _image_record(image):
    return {
        "page_number": image["page_number"],
        "image_index": image["image_index"],
        "xref": image["xref"],
        "path": image["path"],
        "x0": image["x0"],
        "y0": image["y0"],
        "x1": image["x1"],
        "y1": image["y1"],
    }


def build_question_image_map(pdf_path, output_dir):
    """
    Map PDF images to MCQ question numbers.

    Mapping is based on the actual coordinates of the images
    in Full set 1 F.pdf.
    """

    images = extract_pdf_images(pdf_path, output_dir)

    by_page = {}

    for image in images:
        by_page.setdefault(image["page_number"], []).append(image)

    for page_images in by_page.values():
        page_images.sort(
            key=lambda image: (
                round(image["y0"], 1),
                round(image["x0"], 1),
            )
        )

    question_images = {}

    def add_question(question_number, images_for_question):
        question_images[question_number] = [
            _image_record(image)
            for image in images_for_question
        ]

    # ============================================================
    # PAGE 1
    # ============================================================

    page1 = by_page.get(1, [])

    if len(page1) >= 4:
        add_question(1, page1[0:1])
        add_question(2, page1[1:2])
        add_question(3, page1[2:3])
        add_question(4, page1[3:4])

    # ============================================================
    # PAGE 2
    # ============================================================

    page2 = by_page.get(2, [])

    if len(page2) >= 1:
        add_question(7, page2[0:1])

    # ============================================================
    # PAGE 3
    # ============================================================

    page3 = by_page.get(3, [])

    if len(page3) >= 1:
        add_question(10, page3[0:1])

    # ============================================================
    # PAGE 5
    # ============================================================

    page5 = by_page.get(5, [])

    # Q20 has the large picture beside "가락"
    if len(page5) >= 1:
        add_question(20, page5[0:1])

    # Q23 has the four picture choices.
    #
    # The PDF contains several embedded image resources because
    # some visual choices are composed of multiple resources.
    # Keep all resources here for later image-group processing.
    if len(page5) >= 2:
        add_question(23, page5[1:])

    # ============================================================
    # PAGE 6
    # ============================================================

    page6 = by_page.get(6, [])

    # Page 6 contains:
    #
    #   top four images       -> Q25 choices
    #   middle image          -> Q26
    #   lower image           -> Q27
    #   bottom image          -> Q28
    #
    # We use Y coordinates rather than image index because the
    # PDF resource order is not the visual order.

    q25_images = [
        image
        for image in page6
        if image["y0"] < 160
    ]

    q26_images = [
        image
        for image in page6
        if 160 <= image["y0"] < 360
    ]

    q27_images = [
        image
        for image in page6
        if 360 <= image["y0"] < 570
    ]

    q28_images = [
        image
        for image in page6
        if image["y0"] >= 570
    ]

    if q25_images:
        add_question(25, q25_images)

    if q26_images:
        add_question(26, q26_images)

    if q27_images:
        add_question(27, q27_images)

    if q28_images:
        add_question(28, q28_images)

    # ============================================================
    # PAGE 7
    # ============================================================

    page7 = by_page.get(7, [])

    # Q28 is the first image on page 7.
    # It belongs to Q28 because Q28 starts at y=29 and its
    # four visual choices are around y=165.
    #
    # Q29-Q33 do NOT have separate embedded images in the
    # extraction list. Their choices are represented by image
    # content positioned around y=262, 311, 360, 408, 457.
    #
    # Therefore we record their image-region coordinates rather
    # than incorrectly assigning the single top image to all
    # five questions.

    page7_top = [
        image
        for image in page7
        if image["y0"] < 200
    ]

    if page7_top:
        add_question(28, page7_top)

    # Q35-Q36 share the four image choices at the bottom.
    q35_36_images = [
        image
        for image in page7
        if image["y0"] >= 600
    ]

    if q35_36_images:
        add_question(35, q35_36_images)
        add_question(36, q35_36_images)

    # ============================================================
    # PAGE 8
    # ============================================================

    page8 = by_page.get(8, [])

    # Q36 has four image choices at the top.
    q36_images = [
        image
        for image in page8
        if image["y0"] < 150
    ]

    if q36_images:
        add_question(36, q36_images)

    # Q37 has the large image below it.
    q37_images = [
        image
        for image in page8
        if image["y0"] >= 150
    ]

    if q37_images:
        add_question(37, q37_images)

    return question_images