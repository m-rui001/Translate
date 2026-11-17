"""Exact, replayable corrections checked against source chapter JSONs."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'scratch' / 'validation_20261117'
plans = {
    'work_pub/twocities/out/c015/c00/final.txt': [
        ('“真的”这词就够糟的了，”', '“‘真的’这词就够糟的了，”'),
    ],
    'work_gutenberg/regenta/out/c004/c00/final.txt': [
        ('“”她干净', '“她干净'),
        ('“可奥布杜利娅又添一句：——”除了', '可奥布杜利娅又添一句：——“除了'),
        ('“——”可惜呀——“奥布杜利娅收尾道，心里并不觉得可惜——”', '——“可惜呀——”奥布杜利娅收尾道，心里并不觉得可惜，“'),
        ('“”啊！她得承认', '“啊！她得承认'),
        ('“奥布杜利娅真心叹赏', '奥布杜利娅真心叹赏'),
        ('“安娜十分小心地', '安娜十分小心地'),
        ('“她掀开床。', '她掀开床。'),
        ('“——“总告解！”', '——“总告解！”'),
        ('“她想起自己', '她想起自己'),
        ('“也许她更大的罪，正是从这不幸里生出来的。”', '也许她更大的罪，正是从这不幸里生出来的。'),
    ],
}

changes = []
for rel, edits in plans.items():
    p = ROOT / rel
    old = p.read_text(encoding='utf-8')
    new = old
    for before, after in edits:
        assert new.count(before) == 1, (rel, before, new.count(before))
        new = new.replace(before, after)
    backup = HERE / 'backup' / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(p, backup)
    p.write_text(new, encoding='utf-8')
    changes.append({'file': rel, 'replacements': edits})
HERE.joinpath('quote_edits.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
print('corrected', len(changes), 'files; exact matches asserted')
