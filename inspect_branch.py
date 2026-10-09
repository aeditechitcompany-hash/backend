from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

text = path.read_text(encoding="utf-8")

start = text.find("if number is not None:")
end = text.find("if is_option_block(text):", start)

print(repr(text[start:end]))
