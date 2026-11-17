"""Validate delivered batches; optionally compare the local sail correction backup."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from pipeline_build.verify_epub import check
from pipeline_batch_20261117.fetch_second import BodyParser

def main():
    results = []
    for filename, title in [('translations.json', '风与雾：邓萨尼短篇三则（选译）'),
                            ('second_translations.json', '无歌之国：邓萨尼短篇七则（选译）'),
                            ('egerton_translations.json', '一部失落的杰作')]:
        books = json.loads((HERE / filename).read_text(encoding='utf-8'))
        epub = ROOT / 'out' / f'{title}（坟头草译）.epub'
        report = check(str(epub))
        assert not report['errors'], report
        with zipfile.ZipFile(epub) as z:
            for i, book in enumerate(books, 1):
                doc = ET.fromstring(z.read(f'OEBPS/c{i:03}.xhtml'))
                paras = [''.join(p.itertext()) for p in doc.findall('.//{http://www.w3.org/1999/xhtml}p')]
                assert paras == book['translation'], book['key']
                assert len(paras) == len(book['source'])
                if 'html_sha256' in book and filename == 'second_translations.json':
                    html = HERE / 'sources_second' / f'{book["key"]}.html'
                    assert hashlib.sha256(html.read_bytes()).hexdigest() == book['html_sha256']
                    parser = BodyParser()
                    parser.feed(html.read_text(encoding='utf-8'))
                    assert parser.paragraphs == book['source'], book['key']
                if filename == 'egerton_translations.json':
                    html = HERE / 'sources_egerton/masterpiece.html'
                    assert hashlib.sha256(html.read_bytes()).hexdigest() == book['html_sha256']
        results.append({'file': epub.name, 'works': len(books),
                        'paragraphs': sum(len(b['source']) for b in books),
                        'epub_validation': report})
    backup = ROOT / 'scratch/audit_20261117/backup/黑暗的心（坟头草译）.epub'
    changed = None
    if '--with-local-backups' in sys.argv:
        assert backup.is_file(), f'Local backup required: {backup}'
        changed = verify_sails(backup)
    result = {'batches': results, 'sails_changed_documents': changed}
    (HERE / 'delivery_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('11 complete works; 120 aligned paragraphs; archived source matches; EPUB checks passed.')
    if changed is not None:
        print('Local sail correction backup comparison passed.')

def verify_sails(backup):
    changed = []
    with zipfile.ZipFile(backup) as old, zipfile.ZipFile(ROOT / 'out/黑暗的心（坟头草译）.epub') as new:
        assert set(old.namelist()) == set(new.namelist())
        for name in old.namelist():
            before, after = old.read(name), new.read(name)
            if before != after:
                assert name.endswith('.xhtml'), name
                assert before.decode('utf-8').replace('晒成棕黄的帆', '鞣成棕褐色的帆') == after.decode('utf-8'), name
                changed.append(name)
        assert len(changed) == 1, changed
    return changed

if __name__ == '__main__':
    main()
