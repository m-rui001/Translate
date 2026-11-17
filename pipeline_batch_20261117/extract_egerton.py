"""Recover the story, excluding page headers/catchwords and joining page breaks."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work_batch_20261117_egerton'

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    archive = ROOT / 'pipeline_batch_20261117/sources_egerton/masterpiece.html'
    raw = archive.read_text(encoding='utf-8')
    start = raw.index('<p><p>I REGRET')
    end = raw.index('regret it !', start) + len('regret it !')
    body = raw[start:end]
    body = re.sub(r'<p align="center">.*?</p>', '', body, flags=re.S)
    body = re.sub(r'<div align="(?:left|center)">.*?</div>', '', body, flags=re.S)
    body = re.sub(r'([A-Za-z])-\s*<br>\s*([a-z])', r'\1\2', body)
    body = body.replace('</p>', '\n\n')
    body = html.unescape(re.sub(r'<[^>]*>', ' ', body))
    paras = [re.sub(r'\s+', ' ', p).strip() for p in body.split('\n\n') if p.strip()]
    joined = []
    continuations = ('because all the while', 'a thin-toned violin', 'of the pavement', 'that is to bring')
    for p in paras:
        if p.startswith(continuations):
            assert joined
            joined[-1] += ' ' + p
        else:
            joined.append(p)
    assert joined[0].startswith('I REGRET') and joined[-1].endswith('regret it !')
    result = {'key': 'lost_masterpiece', 'title_src': 'A Lost Masterpiece',
              'title_zh': '一部失落的杰作', 'subtitle_src': 'A City Mood, Aug. ’93',
              'author': 'George Egerton', 'source_url': 'https://1890s.ca/YBV1_egerton_masterpiece/',
              'source': joined, 'html_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
    (WORK / 'source.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (WORK / 'source_numbered.txt').write_text('\n\n'.join(f'{i}: {p}' for i,p in enumerate(joined)), encoding='utf-8')
    print(len(joined), 'paragraphs extracted; page continuations joined')

if __name__ == '__main__':
    main()
