"""Build the reader's canonical novel and data from chapter files."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
TITLE = "핑크의 통화"
SUBTITLE = "마주 보면 사라지는 말"

chapter_files = [ROOT / f"ch{number:02d}.md" for number in range(1, 6)]
chapter_texts = [path.read_text(encoding="utf-8").strip() for path in chapter_files]
chapters = []
for index, chapter_text in enumerate(chapter_texts, start=1):
    heading, _, body = chapter_text.partition("\n")
    match = re.fullmatch(r"## (제\d+장)\. (.+)", heading)
    if not match:
        raise ValueError(f"Invalid chapter heading: {heading}")
    paragraphs = [line.strip() for line in body.splitlines() if line.strip()]
    if not paragraphs:
        raise ValueError(f"Empty chapter: {heading}")
    chapters.append({
        "id": index,
        "fullTitle": heading.removeprefix("## "),
        "number": match.group(1),
        "subtitle": match.group(2),
        "paragraphs": paragraphs,
    })

novel = "\n\n".join(chapter_texts) + "\n"
(ROOT / "novel.md").write_text(novel, encoding="utf-8")
epilogue = (ROOT / "epilogue.md").read_text(encoding="utf-8").strip()
afterword = [line.strip() for line in epilogue.splitlines()[1:] if line.strip()]
data = {
    "title": TITLE,
    "chapterCount": len(chapters),
    "totalParagraphs": sum(len(chapter["paragraphs"]) for chapter in chapters),
    "chapters": chapters,
    "afterword": afterword,
}
(ROOT / "novel-data.js").write_text(
    "window.NOVEL_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";",
    encoding="utf-8",
)
(ROOT / f"{TITLE}.md").write_text(
    f"# {TITLE}\n\n### {SUBTITLE}\n\n{novel}\n{epilogue}\n",
    encoding="utf-8",
)
print(f"Built {len(chapters)} chapters, {data['totalParagraphs']} paragraphs")
