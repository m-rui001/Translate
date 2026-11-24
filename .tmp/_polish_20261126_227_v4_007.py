# -*- coding: utf-8 -*-
"""逐段润色落盘脚本：v3/chunk227、v3/chunk229、v4/chunk002、v4/chunk005、v4/chunk007。
只做「定位唯一子串 → 替换 → 断言命中数 == 1」，不重写整文件，保持原换行符与空行结构。
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'out')
BAK = 'final.txt.bak_20261125'

# chunk -> [(类别, 旧串, 新串, 备注)]
EDITS = {
    'v3/chunk227': [
        ('①',
         '这么一场危机之后还活着。',
         '经历这么一场危机还能活着。',
         '「après une crise pareille」缺谓语的残句'),
        ('①',
         '总不能什么都一下子要求。',
         '总不能一下子什么都要求。',
         '「on ne peut pas tout demander à la fois」语序拗口'),
        ('③',
         '这并不妨碍没人来打听我的消息，像打听我亲爱的阿马尼安那样。',
         '可即便如此，也没人来打听我的消息，不像打听我亲爱的阿马尼安那样。',
         '「Cela n\'empêche que」直搬成「并不妨碍没人」造成双重否定误读'),
        ('⑥',
         '我吩咐过把斯万先生寄来的那个包着的东西拿上来的呀。',
         '我吩咐过把斯万先生寄来的那张包着的照片拿上来的呀。',
         '漏译 photographie，只剩「包着的东西」'),
        ('④',
         '那人还僭用了本该属于我们的布拉班特的名号',
         '比利时国王还僭用了本该属于我们的布拉班特名号',
         '「那人」紧邻吉尔贝，读者会错认为吉尔贝'),
        ('⑥',
         '在她本国所有团队里都考第一',
         '在她本国各个团里都考第一',
         'régiments 是军队的「团」，非「团队」'),
        ('①⑦',
         '我们已经在整个欧洲九个世纪都居首位了',
         '我们已经在整个欧洲居首位九百年了',
         '「九个世纪」作状语位置错置，读数拗口；数字宜作「九百年」'),
    ],
    'v3/chunk229': [
        ('⑤',
         '可这家伙是个粗胚，',
         '可这家伙是个粗坯，',
         '「粗坯」全库 4:1，此处为异体「粗胚」'),
    ],
    'v4/chunk002': [
        ('⑥',
         '而后者则像被钉在原地，像一株植物那样扎下了根',
         '而后者则突然在德·夏尔吕先生面前像被钉在原地，像一株植物那样扎下了根',
         '漏译 subitement 与 devant M. de Charlus，「面对面」的对峙关系落空'),
        ('③',
         '而德·夏尔吕先生，这仅仅是个比喻',
         '而德·夏尔吕先生——这仅仅是个比喻',
         '括注起始破折号缺失，主语被吞进括注'),
        ('③',
         '——多年来他只趁着絮比安不在的钟点',
         '——多年来只趁着絮比安不在的钟点',
         '主语「德·夏尔吕先生」已提到括注之外，「他」字多余'),
        ('①',
         '——德·夏尔吕先生每次看絮比安，总要让自己的目光伴随着一句话',
         '——所以德·夏尔吕先生每次看絮比安，总要让自己的目光伴随着一句话',
         '「但想必是因为……」三个原因并列后接正句，缺关联词，因果链断裂'),
    ],
    'v4/chunk005': [
        ('⑤',
         '乌利塞斯本人起初也认不出雅典娜。',
         '尤利西斯本人起初也认不出雅典娜。',
         'Ulysse 全库作「尤利西斯」3 次，此处「乌利塞斯」为孤例'),
    ],
    'v4/chunk007': [
        ('⑥',
         '却打算迅速把这些风度装点起来',
         '却打算迅速给自己装点上',
         'orner 的宾语是 corps（自身），非「风度」'),
        ('①',
         '错过与那些他们在其他方面却效仿其谈吐、思想、衣着、发型的人',
         '错过与那些人相聚，而他们在其他方面却效仿这些人的谈吐、思想、衣着、发型',
         '「错过与……的人」悬空，宾语缺失'),
    ],
}


def stats(txt):
    norm = txt.replace('\r\n', '\n')
    paras = [x for x in norm.split('\n') if x.strip()]
    cjk = sum(1 for ch in txt if '\u4e00' <= ch <= '\u9fff')
    return len(paras), cjk, ('CRLF' if '\r\n' in txt else 'LF')


def main():
    total = 0
    for chunk, edits in EDITS.items():
        path = os.path.join(OUT, chunk.replace('/', os.sep), 'final.txt')
        bak = path + '.' + BAK.split('.', 1)[1] if False else os.path.join(
            os.path.dirname(path), BAK)
        if not os.path.exists(bak):
            print('!! 缺备份，跳过：', chunk)
            sys.exit(1)
        with open(path, encoding='utf-8', newline='') as f:
            text = f.read()
        p0, c0, nl = stats(text)
        n = 0
        for cat, old, new, why in edits:
            assert old in text, (chunk, old)
            assert text.count(old) == 1, (chunk, old, text.count(old))
            text = text.replace(old, new, 1)
            n += 1
            print(f'  [{cat}] {why}')
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        p1, c1, nl1 = stats(text)
        assert p0 == p1, (chunk, p0, p1)
        assert nl == nl1, (chunk, nl, nl1)
        total += n
        print(f'{chunk}: 改动 {n} 条；段数 {p0}->{p1} 不变；汉字 {c0}->{c1}；{nl}')
    print('--- 合计改动', total, '条')

    ast.parse(open(__file__, encoding='utf-8').read())
    print('语法自查 OK')


if __name__ == '__main__':
    main()