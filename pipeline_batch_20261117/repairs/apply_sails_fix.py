"""Replay the source-checked sail treatment correction without changing other prose."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'work_pub/darkness/out/c002/c00/final.txt'
BACKUP = ROOT / 'scratch/audit_20261117/backup/work_pub/darkness/out/c002/c00/final.txt'
OLD = '晒成棕黄的帆'
NEW = '鞣成棕褐色的帆'

def main():
    text = SOURCE.read_text(encoding='utf-8')
    if text.count(NEW) == 1 and OLD not in text:
        print('Already applied.')
        return
    assert text.count(OLD) == 1
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    if not BACKUP.exists():
        shutil.copy2(SOURCE, BACKUP)
    SOURCE.write_text(text.replace(OLD, NEW), encoding='utf-8')
    print('Applied one sail treatment correction.')

if __name__ == '__main__':
    main()
