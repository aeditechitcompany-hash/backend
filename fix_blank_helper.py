from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

text = path.read_text(encoding="utf-8")

start_marker = "def restore_blank_marker(question_number, text):"
end_marker = "\ndef extract_question_number(text):"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit(
        "ERROR: restore_blank_marker() was not found. No file was changed."
    )

new_function = '''def restore_blank_marker(question_number, text):
    """
    Restore the visual blank position for questions where the
    PDF text layer does not contain an explicit blank marker.
    """

    if not text:
        return text

    if question_number == 11:
        marker = "\\uB530\\uB73B\\uD55C"
        text = re.sub(
            marker + r"\\s+\\uC637\\uC744\\s+\\uAC00\\uB294\\uAC83\\uC774\\uC88B\\uACA0\\uC2B5\\uB2C8\\uB2E4\\.",
            "\\uB530\\uB73B\\uD55C \\uC637\\uC744 [BLANK] \\uAC00\\uB294\\uAC83\\uC774\\uC88B\\uACA0\\uC2B5\\uB2C8\\uB2E4.",
            text,
        )

    if question_number == 12:
        text = re.sub(
            r"\\uC790\\uC2E0\\uC758\\s+\\uB9CC\\uB9D0\\uD558\\uAE30\\uBCF4\\uB2E4",
            "\\uC790\\uC2E0\\uC758 [BLANK] \\uB9CC\\uB9D0\\uD558\\uAE30\\uBCF4\\uB2E4",
            text,
        )

    if question_number == 13:
        text = re.sub(
            r"\\uAE30\\uACC4\\uC758\\uC0C1\\uD0DC\\uB97C\\uBC18\\uB4DC\\uC2DC\\s+\\uC791\\uC5C5\\uD574\\uC57C\\uD569\\uB2C8\\uB2E4\\.",
            "\\uAE30\\uACC4\\uC758\\uC0C1\\uD0DC\\uB97C\\uBC18\\uB4DC\\uC2DC [BLANK] \\uC791\\uC5C5\\uD574\\uC57C\\uD569\\uB2C8\\uB2E4.",
            text,
        )

    return text
'''

text = text[:start] + new_function + text[end:]

path.write_text(text, encoding="utf-8")

print("Updated restore_blank_marker() using Unicode-safe patterns.")
