
from pathlib import Path
import zipfile

from django.core.files import File
from django.db import transaction

from mcq.models import (
    MCQImport,
    ImportedQuestion,
    ImportedOption,
)
from mcq.services.mcq_importer import parse_import


BACKEND_ROOT = Path(__file__).resolve().parents[2]

QUESTION_AUDIO_DIR = (
    BACKEND_ROOT
    / "media"
    / "mcq"
    / "questions"
    / "audio"
)

OPTION_AUDIO_DIR = (
    BACKEND_ROOT
    / "media"
    / "mcq"
    / "options"
    / "audio"
)


def _prepare_set24_audio(import_job):
    """
    Extract only the expected Set24 MP3 files into a
    job-specific folder. The original ZIP is unchanged.
    """

    if not import_job.audio_zip:
        raise ValueError("Set24 audio ZIP is not attached.")

    zip_path = Path(import_job.audio_zip.path)

    if not zip_path.exists():
        raise FileNotFoundError(
            f"Audio ZIP not found: {zip_path}"
        )

    audio_root = (
        BACKEND_ROOT
        / "media"
        / "mcq"
        / "imports"
        / f"set24_audio_job_{import_job.pk}"
    )
    audio_root.mkdir(parents=True, exist_ok=True)

    required = {}

    # Questions 21–28 have question-level audio.
    for number in range(21, 29):
        required[number] = (f"{number}.mp3", {})

    # Questions 29–34 have question and four option audio files.
    for number in range(29, 35):
        required[number] = (
            f"{number}Q.mp3",
            {
                i: f"{number}-{i}.mp3"
                for i in range(1, 5)
            },
        )

    # These questions have question-level audio only.
    for number in (35, 36, 38, 39, 40):
        required[number] = (f"{number}.mp3", {})

    # Question 37 has question and four option audio files.
    required[37] = (
        "37Q.mp3",
        {
            i: f"37-{i}.mp3"
            for i in range(1, 5)
        },
    )

    expected = {
        filename
        for question_file, option_files in required.values()
        for filename in [
            question_file,
            *option_files.values(),
        ]
    }

    with zipfile.ZipFile(zip_path, "r") as archive:
        members = {}

        for name in archive.namelist():
            archive_path = Path(name)

            if (
                archive_path.suffix.lower() == ".mp3"
                and archive_path.parent.name.lower() == "ubt24"
            ):
                members[archive_path.name] = name

        missing = sorted(expected - members.keys())

        if missing:
            raise ValueError(
                "Missing Set24 audio files: "
                + ", ".join(missing)
            )

        paths = {}

        for filename in sorted(expected):
            destination = audio_root / filename

            destination.write_bytes(
                archive.read(members[filename])
            )

            paths[filename] = str(destination.resolve())

    return {
        number: {
            "question": paths[question_file],
            "options": {
                option_number: paths[filename]
                for option_number, filename
                in option_files.items()
            },
        }
        for number, (question_file, option_files)
        in required.items()
    }


def _get_audio_path(question_number, option_number=None):
    """
    Resolve an existing audio file from the shared audio
    directories. This helper is retained for compatibility.
    """

    if option_number is None:
        directory = QUESTION_AUDIO_DIR
        filename = f"{question_number}.mp3"
    else:
        directory = OPTION_AUDIO_DIR
        filename = f"{question_number}-{option_number}.mp3"

    path = directory / filename

    if path.exists():
        return path

    return None


def _attach_file(model_instance, field_name, file_path):
    """
    Attach a local file to a Django FileField.
    The model field's configured storage handles the saved file.
    """

    if not file_path:
        return

    file_path = Path(file_path)

    if not file_path.is_file():
        return

    with file_path.open("rb") as file_handle:
        getattr(model_instance, field_name).save(
            file_path.name,
            File(file_handle),
            save=False,
        )


def _question_has_content(question_text, images, audio):
    return bool(question_text or images or audio)


def _option_has_content(text, image, audio):
    return bool(text or image or audio)


def _create_imported_question(import_job, record):
    """Create one ImportedQuestion from one parser record."""

    question = ImportedQuestion(
        import_job=import_job,
        question_number=record["question_number"],
        section=record["section"],
        question_text=record["question_text"],
        correct_answer="",
        needs_review=True,
    )

    images = record.get("images") or []

    # Assign a question image only when it is not an
    # option-image question.
    if images and not record.get("option_images"):
        first_image = images[0]
        image_path = Path(first_image["path"])

        if image_path.is_file():
            _attach_file(
                question,
                "question_image",
                image_path,
            )

    # Set24 provides absolute paths. Set1 can continue to
    # provide filenames relative to QUESTION_AUDIO_DIR.
    audio_info = record.get("audio") or {}
    question_audio_filename = audio_info.get("question")

    if question_audio_filename:
        audio_path = Path(question_audio_filename)

        if not audio_path.is_absolute():
            audio_path = QUESTION_AUDIO_DIR / audio_path

        if audio_path.is_file():
            _attach_file(
                question,
                "question_audio",
                audio_path,
            )

    question.save()

    return question


def _create_imported_options(question, record):
    """
    Create ImportedOption records for text, image, and audio
    options. Audio-only options are also included.
    """

    options = record.get("options") or {}
    option_images = record.get("option_images") or {}

    audio_info = record.get("audio") or {}
    option_audio = audio_info.get("options") or {}

    # Include options found in any of the three sources.
    all_option_numbers = set(options.keys())
    all_option_numbers.update(option_images.keys())
    all_option_numbers.update(option_audio.keys())

    created_options = []

    for option_number in sorted(all_option_numbers):
        text = options.get(option_number, "")
        image = option_images.get(option_number)

        option = ImportedOption(
            imported_question=question,
            order=option_number,
            text=text,
            is_correct=False,
            needs_review=True,
        )

        has_image = False

        if image:
            image_path = Path(image["path"])

            if image_path.is_file():
                _attach_file(
                    option,
                    "image",
                    image_path,
                )
                has_image = True

        has_audio = False
        audio_filename = option_audio.get(option_number)

        if audio_filename:
            # Set24 provides absolute paths. Set1 can continue
            # to provide filenames relative to OPTION_AUDIO_DIR.
            audio_path = Path(audio_filename)

            if not audio_path.is_absolute():
                audio_path = OPTION_AUDIO_DIR / audio_path

            if audio_path.is_file():
                _attach_file(
                    option,
                    "audio",
                    audio_path,
                )
                has_audio = True

        if not _option_has_content(
            text,
            has_image,
            has_audio,
        ):
            option.needs_review = True

        option.save()
        created_options.append(option)

    return created_options


@transaction.atomic
def stage_import(import_job, audio_filenames=None):
    """
    Parse an MCQ PDF and create staging records only.

    Existing staging records for this job are replaced.
    This function does not create live Question or Option records.
    """

    if not isinstance(import_job, MCQImport):
        raise TypeError(
            "import_job must be an MCQImport instance."
        )

    import_job.status = "processing"
    import_job.error_message = ""
    import_job.save(
        update_fields=["status", "error_message"]
    )

    try:
        pdf_path = Path(import_job.pdf.path)

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        is_set24 = (
            import_job.name.strip().lower() == "set24"
            or Path(import_job.pdf.name).name.lower()
            == "full_set_24.pdf"
        )

        if is_set24:
            # Set24 has its own parser and ZIP audio mapping.
            from mcq.services.set24_importer import (
                parse_set24_import,
            )

            records = parse_set24_import(
                str(pdf_path),
                listening_start=(
                    import_job.listening_start
                    if import_job.listening_start is not None
                    else 21
                ),
                listening_end=(
                    import_job.listening_end
                    if import_job.listening_end is not None
                    else 40
                ),
            )

            set24_audio = _prepare_set24_audio(import_job)

            for record in records:
                record["audio"] = set24_audio.get(
                    record["question_number"],
                    {
                        "question": None,
                        "options": {},
                    },
                )

        else:
            # Preserve the existing parser path for Set1 and
            # all other non-Set24 imports.
            if audio_filenames is None:
                audio_filenames = []

                if QUESTION_AUDIO_DIR.exists():
                    audio_filenames.extend(
                        path.name
                        for path in QUESTION_AUDIO_DIR.iterdir()
                        if path.is_file()
                    )

                if OPTION_AUDIO_DIR.exists():
                    audio_filenames.extend(
                        path.name
                        for path in OPTION_AUDIO_DIR.iterdir()
                        if path.is_file()
                    )

            records = parse_import(
                str(pdf_path),
                listening_start=(
                    import_job.listening_start
                    if import_job.listening_start is not None
                    else 21
                ),
                listening_end=(
                    import_job.listening_end
                    if import_job.listening_end is not None
                    else 40
                ),
                audio_filenames=audio_filenames,
            )

        # Replace existing staging data only after parsing and
        # audio preparation have completed successfully.
        import_job.questions.all().delete()

        created_questions = []

        for record in records:
            question = _create_imported_question(
                import_job,
                record,
            )

            _create_imported_options(
                question,
                record,
            )

            created_questions.append(question)

        import_job.status = "review"
        import_job.save(update_fields=["status"])

        return created_questions

    except Exception as exc:
        import_job.status = "failed"
        import_job.error_message = str(exc)
        import_job.save(
            update_fields=[
                "status",
                "error_message",
            ]
        )
        raise
