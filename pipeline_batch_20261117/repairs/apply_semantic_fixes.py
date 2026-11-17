"""Replay source-checked corrections; retain exact before-images."""
from pathlib import Path
import shutil, json

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'scratch' / 'audit_20261117'
FIXES = {
 'work_gutenberg/immensee/out/c002/c00/final.txt': [
  ('晚霞的芬芳', '夕阳的薄霭', 'Abendsonnenduft: visual evening haze, not a fragrance'),
  ('这里幽静而隐秘', '这里温馨而幽静', 'heimlich und still: homely/cozy and quiet in this room'),
 ],
 'work_gutenberg/immensee/out/c003/c00/final.txt': [
  ('他自己的年纪是她的一倍', '他自己的年纪是她的两倍', 'er selbst war doppelt so alt: twice her age'),
 ],
}

def main():
    prepared = []
    for rel, fixes in FIXES.items():
        p = ROOT / rel
        text = p.read_text(encoding='utf-8')
        for old, new, reason in fixes:
            if old not in text and text.count(new) == 1:
                continue
            assert text.count(old) == 1, (rel, old, text.count(old))
            text = text.replace(old, new)
        prepared.append((p, rel, text))
    for p, rel, text in prepared:
        backup = HERE / 'backup' / rel
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, backup)
        p.write_text(text, encoding='utf-8')
    (HERE / 'fixes.json').write_text(json.dumps(FIXES, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Verified and applied 3 source-checked corrections in 2 units.')

if __name__ == '__main__':
    main()
