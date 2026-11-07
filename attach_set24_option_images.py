from pathlib import Path
from django.core.files import File
from django.db import transaction
from mcq.models import MCQImport, ImportedOption

job = MCQImport.objects.get(pk=2)
if job.name != "Set24" or job.status != "review":
    raise RuntimeError(f"Unexpected job: {job.name}, status={job.status}")

questions = [24, 25, 26, 27, 28, 35, 36]
image_dir = Path("temp_set24_final_options")

# Validate all files and option counts before changing anything.
for number in questions:
    question = job.questions.get(question_number=number)
    count = question.options.count()
    if count not in (0, 4):
        raise RuntimeError(f"Q{number} has {count} options, not 0 or 4.")
    for index in range(1, 5):
        path = image_dir / f"Q{number}_option_{index}.jpg"
        if not path.is_file():
            raise FileNotFoundError(path)

with transaction.atomic():
    for number in questions:
        question = job.questions.get(question_number=number)
        options = list(question.options.order_by("order"))

        if not options:
            for index in range(1, 5):
                ImportedOption.objects.create(
                    imported_question=question,
                    order=index,
                    text="",
                    is_correct=False,
                    needs_review=True,
                )
            options = list(question.options.order_by("order"))

        for index, option in enumerate(options, start=1):
            path = image_dir / f"Q{number}_option_{index}.jpg"
            with path.open("rb") as image_file:
                option.image.save(path.name, File(image_file), save=False)
            option.needs_review = True
            option.is_correct = False
            option.save()

        question.needs_review = True
        question.save(update_fields=["needs_review"])

print("Staging image update completed.")
for number in questions:
    question = job.questions.get(question_number=number)
    print(
        f"Q{number}:",
        [
            (o.order, bool(o.image), o.is_correct, o.needs_review)
            for o in question.options.order_by("order")
        ],
    )
