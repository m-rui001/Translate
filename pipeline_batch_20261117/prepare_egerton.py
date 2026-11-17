from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / 'work_batch_20261117_egerton'

def main():
    book = json.loads((WORK / 'source.json').read_text(encoding='utf-8'))
    book['translation'] = json.loads((HERE / 'egerton_zh.json').read_text(encoding='utf-8'))
    assert len(book['translation']) == len(book['source']) == 50
    book['source_normalizations'] = [
        {'paragraph': 6, 'old': 'enjoy ment', 'new': 'enjoyment', 'reason': 'join line-broken word'},
        {'paragraph': 33, 'old': 'bring mt kudos', 'new': 'bring me kudos', 'reason': 'checked printed page 195'},
        {'paragraph': 36, 'old': 'umbrella waning', 'new': 'umbrella waving', 'reason': 'checked printed page 195'},
        {'paragraph': 38, 'old': 'her r’s s', 'new': 'her r’s', 'reason': 'checked printed page 195; extra HTML italic suffix'},
    ]
    book['source_normalized'] = list(book['source'])
    for edit in book['source_normalizations']:
        p = edit['paragraph']
        assert book['source_normalized'][p].count(edit['old']) == 1
        book['source_normalized'][p] = book['source_normalized'][p].replace(edit['old'], edit['new'])
    (HERE / 'egerton_translations.json').write_text(json.dumps([book], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (WORK / 'translations.json').write_text(json.dumps([book], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('50 source and translation paragraphs; raw transcription preserved; 4 normalizations recorded.')

if __name__ == '__main__':
    main()
