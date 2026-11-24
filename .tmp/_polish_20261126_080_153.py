# -*- coding: utf-8 -*-
"""润色落盘脚本：第一卷（out_ind/v1）chunk080 / chunk152 / chunk153。

规则：定位唯一子串 -> 替换 -> 断言命中数 1；读写 newline='' 保持 CRLF 与空行结构；
备份 final.txt.bak_20261125（已存在则不覆盖）。
"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BAK = 'final.txt.bak_20261125'

CHANGES = {
    'chunk080': [
        # ① 读不通：分号后「去钓鳟鱼，在维沃纳河上划船」无谓语挂靠，悬空
        ('要是能成为盖尔芒特公爵夫人的朋友，那该多快活；去钓鳟鱼，在维沃纳河上划船；',
         '成为盖尔芒特公爵夫人的朋友，去钓鳟鱼，在维沃纳河上划船，那该是多大的快乐；'),
    ],
    'chunk152': [
        # ⑥ 硬伤：tant que cela ne m'a été dénoncé que par d'autres（「只是别人揭发的时候」）被读成「之前」
        ('——在别人向我揭发之前，我对你的恨一直那么强烈。',
         '——在这事还只是由别人向我揭发的时候，我恨你恨得那么厉害。'),
        # ① 读不通：「看着你坚持」悬空（me soutenir＝一口咬定）
        ('可是，你让我怎么还能接着爱你呢——我看着你坚持，看着你对一件我知道是假的事赌咒发誓。',
         '可是，你让我怎么还能接着爱你呢——我看着你一口咬定，看着你对一件我知道是假的事赌咒发誓。'),
        # ① 读不通：「也很少把坏事想得这么远」缺主语
        ('不只是因为在他最疑心的时刻，也很少把坏事想得这么远，',
         '不只是因为他在最疑心的时刻也极少把坏事想得这么远，'),
        # ③/④ 法语括注式破折号插在主谓之间，「它」指代不明
        ('也不带有那种特有的残忍——它跟他以往所经历的一切都那么不同，就像一个头一回染上的病。',
         '也不带有那种特有的残忍，那种残忍跟他以往经历的一切都那么不同，就像一种头一回染上的病。'),
        # ① 读不通：「他想让她亲口说的……那种可怕的事」先读成「他想让她……」
        ('他想让她亲口说的“两三次”那种可怕的事，再也不能重演。',
         '他要让那桩她亲口说过“两三次”的可怕的事，再也不能重演。'),
        # ① 读不通：「就打那时起起了念头」两个「起」相撞
        ('就打那时起起了念头，', '就从那时起生了念头，'),
        # ⑥ 硬伤：修补「受损坏的组织」搭配冗余
        ('像受伤器官的细胞立刻动手修补受损坏的组织，',
         '像受伤器官的细胞立刻动手修补受损的组织，'),
        # ① 读不通：「就在他伸手按胸……的工夫。」句子未完成
        ('可这些念头都只持续了一秒钟，就在他伸手按胸、重新喘上气、勉强一笑以掩饰痛苦的工夫。',
         '可这些念头都只持续了一秒钟，不过是他伸手按胸、重新喘上气、勉强一笑以掩饰痛苦的工夫。'),
    ],
    'chunk153': [
        # ⑥ 硬伤：je n'y avais jamais repensé＝此后从未再想过；「早就不再去想」把 jamais 读成「早就」
        ('我早就不再去想它，倒好像你非要把这些念头重新塞给我似的。',
         '我从此再没去想过它，倒好像你非要把这些念头重新塞给我似的。'),
        # ① 读不通：「以致斯万喘着气，一切都看得分明」后半句缺谓语挂靠
        ('以致斯万喘着气，一切都看得分明：奥黛特打哈欠，那块小石头。',
         '以致斯万喘着气，把一切都看得清清楚楚：奥黛特打起哈欠，那块小石头。'),
        # ⑦ 体例：破折号插入语后接引语，不应再加冒号
        ('天哪！：“瞎扯！”', '天哪！“瞎扯！”'),
    ],
}


def main():
    for chunk, pairs in CHANGES.items():
        d = os.path.join(BASE, chunk)
        fp = os.path.join(d, 'final.txt')
        bp = os.path.join(d, BAK)
        if not os.path.exists(bp):
            shutil.copyfile(fp, bp)
        with open(fp, encoding='utf-8', newline='') as f:
            text = f.read()
        before = text
        applied = 0
        for old, new in pairs:
            assert old in text, f'{chunk}: 未找到 {old[:30]}'
            assert text.count(old) == 1, f'{chunk}: 命中数 {text.count(old)}: {old[:30]}'
            text = text.replace(old, new)
            applied += 1
        if text != before:
            with open(fp, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
        norm_b = before.replace('\r\n', '\n')
        norm_a = text.replace('\r\n', '\n')
        han_b = sum(1 for c in before if '\u4e00' <= c <= '\u9fff')
        han_a = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        print(f'{chunk}: 改动 {applied} 条 | 行数 {norm_b.count(chr(10)) + 1} -> {norm_a.count(chr(10)) + 1}'
              f' | 段数 {len([x for x in norm_b.split(chr(10)) if x.strip()])} -> '
              f'{len([x for x in norm_a.split(chr(10)) if x.strip()])}'
              f' | 汉字 {han_b} -> {han_a} | CRLF {before.count(chr(13) + chr(10))}/{text.count(chr(13) + chr(10))}')


main()
ast.parse(open(__file__, encoding='utf-8').read())