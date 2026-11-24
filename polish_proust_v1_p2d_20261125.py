# -*- coding: utf-8 -*-
"""《追忆似水年华》第一卷 chunk026-030 通读润色 p2d（2026-11-25 轮）

只做「定位唯一子串 -> 替换 -> 断言命中数」的改法，不整文件重写。
行数/段数不变；已有 .bak_20261125 的不覆写。
"""
import io
import os
import shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'work_proust', 'out_ind', 'v1')

# (chunk, old, new, 类别, 理由)
EDITS = [
    # ---- chunk027 ----
    ('chunk027', '这使她喜爱自然和天才的作品，并相信它们富有裨益的影响——只要人的手没有像姑祖母的园丁那样把自然弄小。',
     '这使她喜爱自然——只要人的手没有像姑祖母的园丁那样把它弄小——并相信自然和天才的作品富有裨益的影响。', '①',
     '原文 «qui lui faisait aimer et croire riches d’une influence bienfaisante, la nature, quand la main de l’homme ne l’avait pas… rapetissée, et les œuvres de génie»：限定条件只管「自然」，原译挪到句末，读来像是连「天才的作品」也一并管住，且「只要……」悬空'),
    # ---- chunk028 ----
    ('chunk028', '人要是从那两个台阶下通往河边的好看花园里望过去',
     '人要是站在那顺着几级石阶下到河边的好看花园里望过去', '⑥',
     '«quand on la regarde du beau jardin qui descend des perrons vers la rivière»：perrons 是「几级石阶」，不是「两个台阶」；「从那……台阶下……望过去」句法也不通'),
    # ---- chunk029 ----
    ('chunk029', '成天下来，不是去做日课', '整天从那儿下来，不是去做日课', '⑥',
     '«d’où elle descendait tout le temps soit aux offices»：tout le temps 是「整天」，descendait 是「从那儿（租的屋子）下来」；原译把两者搅成「成天下来」，动作丢失'),
    ('chunk029', '就是日课外头念一小段祈祷', '就是日课之外念一小段祈祷', '①',
     '«en dehors des offices» 是「日课之外」；「日课外头」不成话'),
    ('chunk029', '她在一件黑呢斗篷上头戴一顶白色的小软帽', '她黑呢斗篷上头戴一顶白色的小软帽', '③',
     '«Elle portait au-dessus d’une mante de drap noir un petit béguin blanc»：介词与冠词照搬，「在一件……上头戴一顶」叠床架屋'),
    ('chunk029', '就像昨天萨泽拉夫人还跟我说的那样', '就像昨天萨泽兰夫人还跟我说的那样', '⑥',
     '«comme me disait hier encore Mme Sazerin»：厄拉莉把 Sazerat 说成 Sazerin，这正是下文那条括号笑话的引子，译作「萨泽拉」把笑话抹平了'),
    ('chunk029', '就是萨泽拉夫人名叫萨泽拉夫人', '就是萨泽拉夫人名叫萨泽兰夫人', '⑥',
     '«était que Mme Sazerat s’appelait Mme Sazerin»：同字重复成废话，笑话全失；改出「萨泽兰」才有反证可言'),
    # ---- chunk030 ----
    ('chunk030', '那是园子的一小角，一扇边门朝圣灵街开着，从那里未经打理的泥土上，靠着两级台阶，像一座独立的建筑似的，凸出着房屋的后厨房。',
     '就在园子的一小角里，一扇边门朝圣灵街开着；这片未经打理的泥土上，后厨房被两级台阶垫高，像一座独立的建筑似的，凸出在房屋之外。', '①',
     '«sur le banc sans dossier ombragé d’un lilas, dans ce petit coin du jardin qui s’ouvrait par une porte de service… et de la terre peu soignée duquel s’élevait par deux degrés, en saillie de la maison… l’arrière-cuisine»：「那是园子的一小角」把长凳说成了角落；「从那里……凸出着后厨房」主语倒装且悬空'),
    ('chunk030', '把它田里的第一批果实献给它', '把他们田里的第一批果实献给它', '④',
     '«pour lui dédier les prémices de leurs champs»：田是商贩们的；「它田里」把「他们」误作「它」，指代错人'),
]

def main():
    touched = {}
    for chunk, old, new, kind, why in EDITS:
        path = os.path.join(BASE, chunk, 'final.txt')
        text = io.open(path, encoding='utf-8', newline='').read()
        assert old in text and text.count(old) == 1, (chunk, old)
        bak = path + '.bak_20261125'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        raw = io.open(path, encoding='utf-8', newline='').read()
        assert len(raw.splitlines()) == len(raw.replace(old, new).splitlines()), chunk
        io.open(path, 'w', encoding='utf-8', newline='').write(raw.replace(old, new))
        touched.setdefault(chunk, []).append((kind, why))
    for chunk in sorted(touched):
        print(chunk, len(touched[chunk]))

if __name__ == '__main__':
    main()
    import ast
    ast.parse(io.open(__file__, encoding='utf-8').read())