import re
from pathlib import Path


AUDIO_PATTERN = re.compile(
    r"^(\d+)(?:-(\d+))?\.mp3$",
    re.IGNORECASE,
)


def identify_audio(filename):
    """
    Recognizes:

        21.mp3
        21-1.mp3
        21-2.mp3
        21-3.mp3
        21-4.mp3
    """

    filename = Path(filename).name.strip()

    match = AUDIO_PATTERN.fullmatch(filename)

    if not match:
        return None

    question_number = int(match.group(1))
    option_number = match.group(2)

    return {
        "question_number": question_number,
        "option_number": (
            int(option_number)
            if option_number is not None
            else None
        ),
        "filename": filename,
    }


def build_audio_map(filenames):
    """
    Converts audio filenames into:

    {
        21: {
            "question": "21.mp3",
            "options": {
                1: "21-1.mp3",
                2: "21-2.mp3",
                3: "21-3.mp3",
                4: "21-4.mp3",
            }
        }
    }
    """

    audio_map = {}

    for filename in filenames:

        parsed = identify_audio(filename)

        if not parsed:
            continue

        question_number = parsed["question_number"]
        option_number = parsed["option_number"]

        if question_number not in audio_map:
            audio_map[question_number] = {
                "question": None,
                "options": {},
            }

        if option_number is None:
            audio_map[question_number]["question"] = filename
        else:
            audio_map[question_number]["options"][
                option_number
            ] = filename

    return audio_map