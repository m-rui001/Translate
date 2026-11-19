"""Package the reviewed Chinese Markdown using the shared EPUB builder."""

from pathlib import Path
import sys
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline_build import build_all
from pipeline_build.verify_epub import check


def main():
    sources = Path(__file__).with_name("sources_schwob")
    items = []
    for key in ("train_081", "le_fort", "conte_des_oeufs"):
        text = (sources / f"{key}.zh.md").read_text(encoding="utf-8")
        heading, _, *paragraphs = text.split("\n---\n", 1)[0].strip().split("\n\n")
        paragraphs = ["⁂" if paragraph == "***" else paragraph for paragraph in paragraphs]
        items.append({
            "id": key, "title_zh": heading.removeprefix("# "), "title_en": "",
            "texts": paragraphs, "types": ["p"] * len(paragraphs), "notes": [],
        })

    build_all.OUT = str(ROOT / "out")
    result = build_all.package({
        "title": "081次列车：施沃布短篇三则",
        "sub": "Le Train 081 · Le Fort · Le Conte des œufs",
        "author": "马塞尔·施沃布",
        "src": "Marcel Schwob",
        "uid": "urn:translate:schwob-three-tales",
        "note": "译自 Cœur double，巴黎 Ollendorff 版（1891），第 31–46、139–147 页。",
    }, items, "chapters")

    validation = check(result["path"])
    if validation["errors"]:
        raise ValueError(validation)
    with ZipFile(result["path"]) as epub:
        for index, item in enumerate(items, 1):
            chapter = ElementTree.fromstring(epub.read(f"OEBPS/c{index:03d}.xhtml"))
            actual = [node.text for node in chapter.findall(".//{http://www.w3.org/1999/xhtml}p")]
            if actual != item["texts"]:
                raise ValueError(f"EPUB text differs from Markdown: {item['id']}")
    print(result)


if __name__ == "__main__":
    main()
