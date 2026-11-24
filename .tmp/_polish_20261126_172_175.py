# -*- coding: utf-8 -*-
"""逐段润色 chunk172-175（卷1 / out_ind/v1）。定位唯一子串替换，不整文件重写。"""
import ast
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "172": [
        # ① 三个并列主语被"它"切断，末项独吞谓语；补"这三样"收拢
        ("我的心灵一想起她，单凭自身的运作就充满的那份魅力",
         "我的心灵一想起她、单凭自身的运作便充满的那份魅力"),
        ("那种精神习惯的内在拘束，早已开始",
         "那种精神习惯的内在拘束：这三样早已开始"),
        # ③ au milieu de mes larmes 直搬
        ("我的泪水中间形成一个微笑", "在我的泪水中形成一个微笑"),
        # ⑤ 专名统一（全库以"狄奥多西"为多数形）
        ("看泰奥多兹国王驾到", "看狄奥多西国王驾到"),
    ],
    "173": [
        # ① 省略谓语的比较句悬空，补"一样"收口
        ("就像当年斯万之于奥黛特之美中的审美品格。",
         "就像当年斯万之于奥黛特之美中的审美品格一样。"),
        # ① "大火漆印"被读成"大火"+"漆印"，且缺动词
        ("纸封用几枚白色大火漆印封着，系着一束淡紫的缎带，是她给我带来的。",
         "纸封上盖着几枚大大的白色火漆封印，系着一束淡紫的缎带，是她给我带来的。"),
        # ③ ne commençant pas par décider 直搬
        ("也不从断定我被爱开始", "也不先断定我是被爱的"),
        # ① 悬空"想必"
        ("若是她想必不会在那儿", "若是她不会在那儿"),
        # ① "重新一样爱我"缺比较基准
        ("才会重新一样爱我", "才会重新像从前一样爱我"),
        # ① "单凭……而定"悬空在句末，移作前置状语
        ("仿佛她真能随她的意、随我的意，改变对我的感情来讨我欢喜，单凭她说出口的话，看我表现好坏而定。",
         "仿佛她真能只凭说出口的话、凭我表现好坏，随她的意、随我的意改变对我的感情来讨我欢喜。"),
        # ③ 关系从句后置（"……的东西，是我们的愿望奈何不得的"）
        ("然而在这些举动的脉络里自有一种明明白白的东西，是我们的愿望奈何不得的，明天她会怎样做，我们该去问这种明白，而不是问自己的愿望。",
         "然而在这些举动的脉络里自有一种我们的愿望奈何不得的明白；明天她会怎样做，我们该去问这种明白，而不是问自己的愿望。"),
        # ④ Mademoiselle 指的就是institutrice，作"小姐"易误认
        ("跟小姐去买东西", "跟女教师去买东西"),
    ],
    "174": [
        # ⑤ institutrice 本卷 canon 为"女教师"
        ("吉尔贝特很喜欢她的家庭女教师", "吉尔贝特很喜欢她的女教师"),
        # ③ à l'égard de 直搬成"之于"
        ("就像某些失语症患者之于最常用的词那样，是一个新词",
         "就跟某些失语症患者看最常用的词一样，是一个新词"),
        # ⑥ innocent 与下句"罪孽深重"对照，作"清白"
        ("一面又不再显得无辜", "一面又不再显得清白"),
        # ④ 复数"事实"用单数"它"回指
        ("它们重复着既成的事实，却改变不了它", "它们重复着既成的事，却改变不了它"),
        # ① 条件从句与主句咬合不清
        ("真要像我一直以为的那样，她确实认识斯万夫人，那她准是个不折不扣的疯子。",
         "她若真的认识斯万夫人，那她必定像我历来所想的那样，是个不折不扣的疯子。"),
    ],
    "175": [
        # ⑤ institutrice 统一
        ("她从家庭教师那里听来的", "她从女教师那里听来的"),
        # ⑥ rayon des Trois Quartiers = 百货店柜台，误作"灯光"；① 破折号插在主谓之间
        ("可是母亲似乎并不觉得，在“三街区”那片灯光里，她出现在斯万面前——在他看见她的那一刻，她在他眼里是一个确定的人，与他共有一些回忆，正是这些回忆促使他走近她、向她行礼——这有什么特别的趣味。",
         "可是母亲似乎并不觉得，她出现在“三街区”百货店那个柜台前这件事有什么特别的趣味——在他看见她的那一刻，她在他眼里是一个确定的人，与他共有一些回忆，正是这些回忆促使他走近她、向她行礼。"),
        # ① 连用两个"在"
        ("当我在香榭丽舍在他面前爱得发抖时", "当我在香榭丽舍当着他的面爱得发抖时"),
        # ③ 破折号括注把主句的谓语隔断，改为顺句
        ("原因是，要在吉尔贝特周围的一切里察觉出一种未知的品质——它在感情世界里，就好比红外线在颜色世界里——我的父母缺少这份额外的、一时的感觉能力，而爱情把它给了我。",
         "原因是，要在吉尔贝特周围的一切里察觉出一种未知的品质，它在感情世界里，就好比红外线在颜色世界里，而我的父母缺少这份额外的、一时的感觉能力，爱情却把它给了我。"),
        # ⑥ noble retombée 的"下垂"被副词化
        ("在它们细布窗帘高贵地下垂之间", "在它们细布窗帘那高贵的下垂之间"),
    ],
}

stats = {}
for cid, edits in EDITS.items():
    d = os.path.join(BASE, "chunk" + cid)
    path = os.path.join(d, "final.txt")
    bak = path + ".bak_20261125"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    before_lines = text.count("\n")
    before_cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    for old, new in edits:
        assert old in text, (cid, old)
        assert text.count(old) == 1, (cid, old)
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    with open(path, encoding="utf-8", newline="") as f:
        t2 = f.read()
    after_lines = t2.count("\n")
    after_cjk = sum(1 for ch in t2 if "\u4e00" <= ch <= "\u9fff")
    assert before_lines == after_lines, (cid, before_lines, after_lines)
    stats[cid] = (len(edits), before_lines, after_lines, before_cjk, after_cjk,
                  "CRLF" if "\r\n" in t2 else "LF")
    print("chunk%s: 改动 %d 条  行数 %d→%d  汉字 %d→%d  换行 %s"
          % (cid, len(edits), before_lines, after_lines, before_cjk, after_cjk,
             "CRLF" if "\r\n" in t2 else "LF"))
    # 结构自检
    paras = t2.replace("\r\n", "\n").split("\n")
    assert all(p != "" for i, p in enumerate(paras) if i % 2 == 0), cid
    assert all(p == "" for i, p in enumerate(paras) if i % 2 == 1), cid
    assert t2.count("“") == t2.count("”"), cid
    assert "⟦" not in t2 and "⟧" not in t2, cid

print("总改动:", sum(v[0] for v in stats.values()))
ast.parse(open(__file__, encoding="utf-8").read())
print("ast 自查 OK")