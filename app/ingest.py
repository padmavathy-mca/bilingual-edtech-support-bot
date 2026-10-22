"""Module 1: turn approved help articles into searchable chunks."""
import json, pathlib, re


def chunk_markdown(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    lang = "ta" if path.name.startswith("ta_") else "en"
    title = text.splitlines()[0].lstrip("# ").strip()
    chunks = []
    for i, section in enumerate(re.split(r"\n(?=## )", text)):
        section = section.strip()
        if not section.startswith("## "):      # skip the title-only part
            continue
        chunks.append({"id": f"{path.stem}-{i}", "text": f"{title}\n{section}",
                       "source": path.name, "lang": lang})
    return chunks


def build(docs_dir="data/help_docs", out="data/chunks.json"):
    chunks = []
    for f in sorted(pathlib.Path(docs_dir).glob("*.md")):
        chunks += chunk_markdown(f)
    pathlib.Path(out).write_text(json.dumps(chunks, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
    return chunks


if __name__ == "__main__":
    print(f"Saved {len(build())} chunks")
