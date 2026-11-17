"""Join complete crawled paragraphs and reviewed Chinese, checking alignment."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / 'work_batch_20261117_second'

def main():
    from fetch_second import BodyParser, CATALOG
    WORK.mkdir(parents=True, exist_ok=True)
    import hashlib
    source = []
    for number, key, title, title_zh in CATALOG:
        path = HERE / 'sources_second' / f'{key}.html'
        parser = BodyParser()
        parser.feed(path.read_text(encoding='utf-8'))
        assert parser.done and parser.paragraphs, key
        source.append({'key': key, 'title_src': title, 'title_zh': title_zh,
                       'url': f'https://www.victorianweb.org/authors/dunsany/51tales/{number}.html',
                       'source': parser.paragraphs,
                       'html_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    translations = json.loads((HERE / 'second_zh.json').read_text(encoding='utf-8'))
    assert {b['key'] for b in source} == set(translations)
    for b in source:
        b['translation'] = translations[b['key']]
        assert len(b['source']) == len(b['translation']), b['key']
    (HERE / 'second_translations.json').write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (WORK / 'translations.json').write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(len(source), 'complete works prepared')

if __name__ == '__main__':
    main()
