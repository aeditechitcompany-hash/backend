from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

text = path.read_text(encoding="utf-8")

old = '''def extract_question_number(text):
'''

new = '''def restore_blank_marker(question_number, text):
    """
    Restore the visual blank position for questions where the
    PDF text layer does not contain an explicit blank marker.

    This is specific to the current PDF.
    """

    if not text:
        return text

    if question_number == 11:
        text = text.replace(
            "??????????????.",
            "?????[BLANK]?????????.",
        )

    if question_number == 12:
        text = text.replace(
            "?????????",
            "???[BLANK]??????",
        )

    if question_number == 13:
        text = text.replace(
            "????????????????.",
            "?????????[BLANK]???????.",
        )

    return text


def extract_question_number(text):
'''

if old not in text:
    raise SystemExit(
        "ERROR: Could not find the expected insertion point. "
        "No file was changed."
    )

path.write_text(
    text.replace(old, new, 1),
    encoding="utf-8",
)

print("Added restore_blank_marker().")
