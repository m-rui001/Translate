"""Build the three complete tales; no API calls, no paid services."""
from pathlib import Path
import hashlib
import html
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work_batch_20261117'
TITLE = '风与雾：邓萨尼短篇三则（选译）'
OUT = ROOT / 'out' / f'{TITLE}（坟头草译）.epub'

def xhtml(title, body):
    return ("<?xml version='1.0' encoding='utf-8'?>"
            "<html xmlns='http://www.w3.org/1999/xhtml' lang='zh-CN'>"
            f'<head><title>{html.escape(title)}</title><style>body{{font-family:serif;line-height:1.85;margin:5%;}}p{{text-indent:2em;margin:0 0 .7em;}}h1{{text-align:center;font-size:1.5em;}}.cn{{font-size:.9em;}}</style></head><body>{body}</body></html>')

def main():
    global WORK, TITLE, OUT
    second = '--second' in sys.argv
    egerton = '--egerton' in sys.argv
    data_file = 'translations.json'
    uid = 'urn:translate:dunsany-three-20261117'
    if second:
        WORK = ROOT / 'work_batch_20261117_second'
        TITLE = '无歌之国：邓萨尼短篇七则（选译）'
        OUT = ROOT / 'out' / f'{TITLE}（坟头草译）.epub'
        data_file = 'second_translations.json'
        uid = 'urn:translate:dunsany-seven-20261117'
    if egerton:
        WORK = ROOT / 'work_batch_20261117_egerton'
        TITLE = '一部失落的杰作'
        OUT = ROOT / 'out' / f'{TITLE}（坟头草译）.epub'
        data_file = 'egerton_translations.json'
        uid = 'urn:translate:egerton-lost-masterpiece-20261117'
    WORK.mkdir(parents=True, exist_ok=True)
    books = json.loads(Path(__file__).with_name(data_file).read_text(encoding='utf-8'))
    files = {}
    stats = []
    for i, b in enumerate(books, 1):
        src, zh = b['source'], b['translation']
        assert len(src) == len(zh) and all(src) and all(zh)
        assert not any(re.search(r'[A-Za-z]{4,}|⟦|Sorry|抱歉', p) for p in zh)
        assert all(p[-1] in '。！”？：—…' for p in zh)
        for lang, paras in [('en', src), ('zh', zh)]:
            (WORK / f"{b['key']}.{lang}.txt").write_text('\n\n'.join(paras)+'\n', encoding='utf-8')
        (WORK / f"{b['key']}.md").write_text('# '+b['title_zh']+'\n\n'+'\n\n'.join(zh)+'\n',encoding='utf-8')
        body = '<h1>'+b['title_zh']+'</h1>'+''.join('<p>'+html.escape(p)+'</p>' for p in zh)
        files[f'OEBPS/c{i:03}.xhtml'] = xhtml(b['title_zh'],body)
        stats.append({'key':b['key'],'paragraphs':len(src),'source_words':len(re.findall(r"\b[\w'-]+\b",' '.join(src))), 'han':len(re.findall(r'[\u4e00-\u9fff]',''.join(zh))), 'source_sha256':hashlib.sha256('\n\n'.join(src).encode()).hexdigest()})
    note = (f'本册仅收{len(books)}篇独立短篇的完整译文，并非《五十一则故事》全译。'
            '作者：邓萨尼勋爵（1878—1957）。原作1915年出版；英文原文据Project Gutenberg第7838号，'
            'https://www.gutenberg.org/cache/epub/7838/pg7838.html。中文由本项目本轮独立翻译并校订。'
            '原文为公版文本；已有中文译介，本译文未据既有中文译本转译。')
    if second:
        note = (f'本册仅收{len(books)}篇独立短篇的完整译文，并非《五十一则故事》全译。'
                '作者：邓萨尼勋爵（1878—1957）。原作1915年出版；英文据Victorian Web所载Gutenberg文本，'
                '并对照Wikisource所载1915年纽约版。原文为公版文本。中文由本项目直接据英文翻译并逐段校订。'
                '本轮未检出这些单篇的明确中文译本条目，不据此断言不存在译本。'
                '原文网页：'+'；'.join(b['url'] for b in books))
    if egerton:
        note = ('作者：乔治·埃格顿（George Egerton，1859—1945）。'
                '本篇完整译自《黄皮书》第一卷（1894年4月）第189—196页，副题为“一种城市心情，1893年8月”。'
                '英文据Yellow Nineties 2.0数字转录，并对照其原刊扫描校正识别错误。'
                '原作属公版文本，中文由本项目直接据英文翻译、逐段校订。'
                '本轮未检出明确中文单篇译本记录，不据此断言不存在译本。'
                '原文：https://1890s.ca/YBV1_egerton_masterpiece/。')
    files['OEBPS/copyright.xhtml'] = xhtml('版本说明',"<h1>版本说明</h1><div class='cn'>"+note+'</div>')
    entries = [('copyright.xhtml','版本说明')]+[(f'c{i:03}.xhtml',b['title_zh']) for i,b in enumerate(books,1)]
    links = ''.join(f"<li><a href='{n}'>{t}</a></li>" for n,t in entries)
    files['OEBPS/nav.xhtml'] = xhtml('目录',"<nav xmlns:epub='http://www.idpf.org/2007/ops' epub:type='toc'><h1>目录</h1><ol>"+links+'</ol></nav>')
    points = ''.join(f"<navPoint id='n{i}' playOrder='{i}'><navLabel><text>{t}</text></navLabel><content src='{n}'/></navPoint>" for i,(n,t) in enumerate(entries,1))
    files['OEBPS/toc.ncx'] = "<?xml version='1.0'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/' version='2005-1'><head><meta name='dtb:uid' content='urn:translate:dunsany-three-20261117'/></head><docTitle><text>"+TITLE+'</text></docTitle><navMap>'+points+'</navMap></ncx>'
    manifest = "<item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/><item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>"
    manifest += ''.join(f"<item id='b{i}' href='{n}' media-type='application/xhtml+xml'/>" for i,(n,t) in enumerate(entries))
    spine = "<itemref idref='nav'/>"+''.join(f"<itemref idref='b{i}'/>" for i in range(len(entries)))
    files['OEBPS/content.opf'] = "<?xml version='1.0'?><package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='uid'><metadata xmlns:dc='http://purl.org/dc/elements/1.1/'><dc:identifier id='uid'>urn:translate:dunsany-three-20261117</dc:identifier><dc:title>"+TITLE+"</dc:title><dc:creator>邓萨尼勋爵</dc:creator><dc:language>zh-CN</dc:language><meta property='dcterms:modified'>2026-11-17T00:00:00Z</meta></metadata><manifest>"+manifest+"</manifest><spine toc='ncx'>"+spine+'</spine></package>'
    files['META-INF/container.xml'] = "<?xml version='1.0'?><container xmlns='urn:oasis:names:tc:opendocument:xmlns:container' version='1.0'><rootfiles><rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/></rootfiles></container>"
    files = {name: text.replace('urn:translate:dunsany-three-20261117', uid) for name, text in files.items()}
    if egerton:
        files['OEBPS/content.opf'] = files['OEBPS/content.opf'].replace('<dc:creator>邓萨尼勋爵</dc:creator>', '<dc:creator>乔治·埃格顿</dc:creator>')
    for doc in files.values(): ET.fromstring(doc)
    with zipfile.ZipFile(OUT,'w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        for n,t in files.items(): z.writestr(n,t.encode('utf-8'),compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(OUT) as z:
        for i,b in enumerate(books,1):
            doc=ET.fromstring(z.read(f'OEBPS/c{i:03}.xhtml'))
            actual=[p.text for p in doc.findall('.//{http://www.w3.org/1999/xhtml}p')]
            assert actual == b['translation'], 'EPUB text differs from reviewed text'
    sys.path.insert(0,str(ROOT))
    from pipeline_build.verify_epub import check
    validation=check(str(OUT))
    assert not validation['errors'], validation
    result={'epub':str(OUT),'works':stats,'validation':validation,'method':'Direct translation by the current Codex agent, then source-aligned self-review; no external LLM API used.'}
    (WORK/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
