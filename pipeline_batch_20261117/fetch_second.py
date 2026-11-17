"""Fetch a bounded, serial batch of complete original-language tales."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work_batch_20261117_second'
CATALOG = [
    (7, 'raft_builders', 'The Raft-Builders', '造筏人'),
    (12, 'prayer_of_flowers', 'The Prayer of the Flower', '花的祈祷'),
    (13, 'time_and_tradesman', 'Time and the Tradesman', '时间与商人'),
    (14, 'little_city', 'The Little City', '小城'),
    (15, 'unpasturable_fields', 'The Unpasturable Fields', '不可放牧的原野'),
    (17, 'songless_country', 'The Songless Country', '无歌之国'),
    (18, 'latest_thing', 'The Latest Thing', '最新的东西'),
]

class BodyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.done = False
        self.current = None
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('id') == 'main':
            self.active = True
        if self.active and tag == 'hr':
            self.done = True
        if self.active and not self.done and tag == 'p' and not attrs.get('class'):
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            text = re.sub(r'\s+', ' ', ''.join(self.current)).strip()
            if text:
                self.paragraphs.append(text)
            self.current = None

def main():
    WORK.joinpath('sources').mkdir(parents=True, exist_ok=True)
    items = []
    for number, key, title, zh in CATALOG:
        url = f'https://www.victorianweb.org/authors/dunsany/51tales/{number}.html'
        path = WORK / 'sources' / f'{key}.html'
        if not path.exists():
            response = requests.get(url, timeout=40)
            response.raise_for_status()
            assert '<div id="main">' in response.content.decode('utf-8')
            path.write_bytes(response.content)
        parser = BodyParser()
        parser.feed(path.read_text(encoding='utf-8'))
        assert parser.done and parser.paragraphs, key
        items.append({'key': key, 'title_src': title, 'title_zh': zh,
                      'url': url, 'source': parser.paragraphs,
                      'html_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        print(key, len(parser.paragraphs), 'paragraphs')
    WORK.joinpath('extracted.json').write_text(json.dumps(items, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
