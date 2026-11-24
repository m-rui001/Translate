# -*- coding: utf-8 -*-
"""v6 chunk051 / chunk053 / chunk056 / chunk057 逐段润色（2026-11-26）。
只做「定位唯一子串 → 替换 → count 断言」，不整文件重写；每 chunk 改完立即落盘。
"""
import os, shutil, ast

BASE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    "chunk051": [
        # ⑤ 地名 canon：Bois = 布洛涅林苑（v3/v7 均作「布洛涅林苑」，「林苑」全库仅此 1 处且易误读）
        ("正是我在林苑里跟踪过的那三个少女",
         "正是我在布洛涅林苑里跟踪过的那三个少女",
         "⑤", "au Bois 卷内另作「布洛涅林苑」6 处，单用「林苑」读者无法定位"),
        # ① 生造复合词
        ("我便跟上了这三个新见的少女",
         "我便跟上了这三个新遇见的少女",
         "①", "ces trois nouvelles jeunes filles，「新见」不成词"),
        # ⑤ 术语归一：maison de passe 卷内作「妓院」（chunk018、chunk033）
        ("他在一家窑子里遇见过她",
         "他在一家妓院里遇见过她",
         "⑤", "maison de passe 同卷另作「妓院」2 处，「窑子」为少数派且语体不合"),
        # ① 形容词当名词，句子缺中心语
        ("谁在一生中没有经历过若干这类模模糊糊、却又美妙动人的不确定呢？",
         "谁在一生中没有经历过若干这类模模糊糊、却又美妙动人的犹疑呢？",
         "①", "de ces incertitudes… délicieuses，「不确定」不能作名词中心语"),
        # ① 指代绕成「那个人……的那一位」
        ("恰恰正是你盼着她就是那个人的那一位呢？",
         "恰恰正是你盼着就是她的那一位呢？",
         "①", "celle que vous souhaitiez qu'elle fût，「盼着她就是那个人的那一位」套两层指代"),
        # ③ 法文破折号括注割断主句（je songeais surtout … que la concierge allait m'apprendre que…）
        ("这回忆给我带来一阵尖锐而短暂的痛楚；门房去找他妻子的当口，我想的主要是——想着德·埃波舍维尔小姐，"
         "而且就像在那些等待的片刻里，一个名字、一条信息，不知为什么被你安在了一张脸上，一时间它空了出来，"
         "飘浮着，只要它附到一张新脸上，就能反过来让它原先所标明的那张脸变得陌生、无辜、不可捉摸——"
         "女门房也许会告诉我，德·埃波舍维尔小姐反倒是那两个褐发少女中的一个。",
         "这回忆给我带来一阵尖锐而短暂的痛楚；门房去找他妻子的当口，我想的主要是：女门房也许会告诉我，"
         "德·埃波舍维尔小姐反倒是那两个褐发少女中的一个。我一面想着德·埃波舍维尔小姐，情形就像在那些等待的片刻里"
         "——一个名字、一条信息，不知为什么被你安在了一张脸上，一时间它空了出来，飘浮着，只要它附到一张新脸上，"
         "就能反过来让它原先所标明的那张脸变得陌生、无辜、不可捉摸。",
         "③", "「我想的主要是——（插入语）——女门房也许会告诉我」把主谓用破折号劈开，是法文 pensant à… que… 的直搬"),
        # ① 缺中心语 + ⑤ 术语
        ("偏偏不是那个出入窑子的，若说这一切纯属偶然",
         "偏偏不是那个出入妓院的人，若说这一切纯属偶然",
         "①", "celle qui allait dans les maisons de passe，「那个出入窑子的」后无中心语，读成半句"),
    ],
    "chunk053": [
        # ③ 括注（devant lequel il faudrait se retirer immédiatement）被搬成破折号插在分句中间
        ("哪怕一个意想不到的障碍——本来应当立刻退开的——使它变得危险。",
         "哪怕这时冒出一个意想不到的障碍，本该立刻退开，却使这个动作变得危险。",
         "③", "关系从句被搬成破折号插语，插在「障碍」与「使它变得危险」之间"),
        # ① 并列失衡，「一份又是万份」不成话
        ("这是奇迹般的、可增殖的面包，同时是一份又是万份，对每个人都是同一份，却不可计数地同时进入所有人家。",
         "这是奇迹般的、可以增殖的面包，是同一份，又是上万份，对每个人都一样，却不可计数地同时进入所有人家。",
         "①", "qui est à la fois un et dix mille，「同时是一份又是万份」自相抵消"),
        # ⑥ 量词：报纸论「份」不论「本」
        ("不是这份报纸的某一本，而是这一万本里的随便哪一本",
         "不是这份报纸的某一份，而是这一万份里的随便哪一份",
         "⑥", "un certain exemplaire / l'un quelconque des dix mille，量词误用「本」"),
        # ⑥ 词义误读：compte trop lentement exprès ＝ 故意把数数得很慢，非「算账」
        ("就像一个故意把账算得很慢的等候者",
         "就像一个故意数得很慢的等待者",
         "⑥", "compte trop lentement exprès，「把账算得很慢」误读为算账"),
        # ⑥ 双重否定硬搬，读成肯定
        ("我没法相信每个人睁开眼睛不会直接看见我看见的形象",
         "我无法想象每个人睁开眼睛时，竟看不见我所看见的那些形象",
         "⑥", "je ne peux pas croire que… ne verra pas… 法文双重否定照搬，中文读反"),
        # ①③ 被动硬搬 + ④「它」指代不明（指文章而非怀疑）
        ("并由此压过我对自己那份怀疑，而我已经不需要再去摧毁它了。",
         "并由此压服了我对自己的那份怀疑，而我已经不必再去摧毁这篇文章了。",
         "④", "s'imposait à ma propre défiance… le détruire：被动照搬，且「它」紧邻「怀疑」易误指"),
        # ④ 引文里「它们」无先行语
        ("“它们的美的最大部分，存在于读者的心灵之中。”",
         "“这类句子的美，最大部分存在于读者的心灵之中。”",
         "④", "la plus grande partie de leur beauté：leur 指上文的「句子」，中文「它们」跳空"),
        # ⑥ 量词：肢体论「条」
        ("人们便只拥有她一个残缺的肢体",
         "人们便只拥有她一条残缺的肢体",
         "⑥", "un membre mutilé，量词误用「一个」"),
        # ① 动宾错搭 + ⑥ 动词
        ("若不是他认为该把它塞满自己的专栏，好让这一击传得更远，这想法也许永远不会从他身上出来",
         "若不是他觉得该拿它去塞满自己的专栏文章，好让这一击传得更远，这想法也许永远不会从他身上冒出来",
         "①", "en bourrer son feuilleton，「把它塞满自己的专栏」动宾倒错"),
        # ③ 「要不是……的话」吊在句末（法文 si… ne 后置）
        ("晚上，穿灰裤子的诺阿耶公爵用马车带她出去时，会告诉她社交界是怎么想的，要不是德·埃尔布维尔夫人的一句话已经让他知道了的话。",
         "晚上，穿灰裤子的诺阿耶公爵用马车带她出去时，要不是德·埃尔布维尔夫人的一句话已经让他知道了，就会告诉她社交界是怎么想的。",
         "③", "si un mot de Mme d'Herbouville ne le lui avait déjà appris 的条件从句被照搬到句末"),
        # ① 缺谓语动词，「使我充满的力量」读不通
        ("这道曙光使我充满的力量和胜利的欢乐",
         "这道曙光使我心中充满更大的力量和胜利的欢乐",
         "①", "qui me remplissait de plus de force et de joie triomphante，「使我充满的力量」主语谓语黏连"),
    ],
    "chunk056": [
        # ①④ 「责备恋人」歧义（blâment chez les amoureux）＋从句吊尾
        ("还可以加上一种幸运的自信：不喜欢某人的人，正是凭着这种自信，置身于他们责备恋人的那些事情之外，"
         "而恋人的爱情又恰好解释了那些事情。",
         "还可以加上一种幸运的自信：不喜欢某人的人，正是凭着这种自信，对恋人们身上那些他们自己也要责备、"
         "而爱情恰好能为之开脱的事，一概置身事外。",
         "①", "se tiennent à l'écart de ce qu'ils blâment chez les amoureux，「责备恋人」读成责备自己的恋人"),
        # ① 同位语错位：「态度，即那句 Suave mari magno」
        ("这就是斯万本人早就不再爱奥黛特、也不再看重那个小圈子以后，就韦尔迪兰一家向我建议的态度，即那句“Suave mari magno”。",
         "这就是斯万本人早就不再爱奥黛特、也不再看重那个小圈子以后，对我谈起韦尔迪兰一家时向我建议的那句“Suave mari magno”。",
         "①", "C'est le Suave mari magno que Swann… me conseillait，「态度，即那句」把同位语接错"),
        # ③ 括注被搬成破折号插在主谓之间（de ce propos… l'étonnement du lecteur）
        ("我听了这番话——比起我期待的那番话，它是多么轻浮——所产生的惊讶，正像一位读者在《费加罗报》惯常的位置寻找日俄战争的最新消息，"
         "却偏偏看到给莫特马尔小姐送结婚礼物者的名单",
         "这番话比起我期待的那番话是多么轻浮；我听了，惊讶得就像一位读者在《费加罗报》惯常的位置寻找日俄战争的最新消息，"
         "却偏偏看到给莫特马尔小姐送结婚礼物者的名单",
         "③", "si frivole auprès de celui que j'attendais 是插入语，被搬成破折号割断主谓"),
        # ② 被动硬搬 + 「的」字堆叠
        ("而这种好奇不再被她自己抵抗斯万的要求的欲望遮蔽。",
         "而这种好奇，也不再被她那股要抵抗斯万之要求的欲望所遮掩了。",
         "②", "que ne venait plus lui masquer le désir de résister à la prétention de Swann：被动照搬 + 三层「的」"),
        # ⑦ 「这样或那样的」冗余「的」
        ("因他们的这样或那样的行为惹她恼怒而中断",
         "因他们这样那样的行为惹她恼怒而中断",
         "⑦", "tels ou tels de leurs actes，「这样或那样的」中「的」多余"),
        # ② 「替她多少有些自尊心」不成话
        ("所有爱她并替她多少有些自尊心的人",
         "所有爱她、也为她顾些体面的人",
         "②", "avaient un peu d'amour-propre pour elle，「替她有些自尊心」主语错位"),
        # ① 两个「对」相撞
        ("才可能对公爵夫人对她态度的转变感到高兴。",
         "才会为公爵夫人对她态度的转变而高兴。",
         "①", "「对……对……」两个介词连缀，读来打结"),
    ],
    "chunk057": [
        # ① 两个「端详着自己」连用，读者不知谁看谁
        ("蓝色的眼睛端详着自己，端详着自己依然金黄的头发",
         "蓝色的眼睛端详着自己，也端详着自己依然金黄的头发",
         "①", "se regardaient eux-mêmes et regardaient ses cheveux，并列关系被读成重复"),
        # ① 应答语不成话
        ("“您完全有理，”公爵答道",
         "“您说得完全有理，”公爵答道",
         "①", "Vous aviez parfaitement raison，答语缺谓语"),
        # ② 「这做女儿的悲伤」定语悬空
        ("仿佛以此表明她懂得这做女儿的悲伤",
         "仿佛以此表明她懂得做女儿的这份悲伤",
         "②", "le chagrin de la fille，「这做女儿的悲伤」缺中心语"),
        # ⑥ 词义误读：renseignements 是中性的「情况」，非「底细」
        ("向这姑娘提供关于他的底细",
         "向这姑娘提供一些关于他的情形",
         "⑥", "des renseignements sur lui，「底细」带贬义，与原意不合"),
        # ① 生硬对译
        ("出于炫耀谦逊与恪求准确",
         "出于卖弄谦逊和讲究精确",
         "①", "par ostentation de modestie et scrupule d'exactitude，「炫耀谦逊」不成搭配"),
        # ① 「断难狠心」叠床
        ("当时断难狠心放你走",
         "那时便狠不下心放你走",
         "①", "ne pouvant alors se résoudre à vous laisser partir，「断难狠心」两重否定叠在一起"),
        # ⑥ 词义：profondeur de sa sensibilité 是「感情的全部深度」
        ("本是极愿向她吐露自己内心全部的敏锐与柔情的",
         "本是极愿向她袒露自己感情的全部深度的",
         "⑥", "lui dévoiler toute la profondeur de sa sensibilité，「敏锐与柔情」是擅加分拆"),
        # ⑥ 词义误读：précisément ≠ 恰巧
        ("不知是恰巧认为情势不容许这般感情流露",
         "不知是他恰恰认为情势不容许这般感情流露",
         "⑥", "soit qu'il pensât précisément que…，précisément 为「恰恰」，非「恰巧」"),
    ],
}


def han(t):
    return sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")


def main():
    total = 0
    for name in ["chunk051", "chunk053", "chunk056", "chunk057"]:
        d = os.path.join(BASE, name)
        fp = os.path.join(d, "final.txt")
        bak = fp + ".bak_20261125"
        if not os.path.exists(bak):
            shutil.copy2(fp, bak)
        else:
            print("backup exists, skip cp:", bak)
        with open(fp, encoding="utf-8", newline="") as f:
            text = f.read()
        nl = "\r\n" if "\r\n" in text else "\n"
        lines_before = len(text.split(nl))
        han_before = han(text)
        n = 0
        for old, new, cls, why in EDITS[name]:
            assert "\r\n" not in old and "\r\n" not in new
            if old not in text:                      # 已改过，重跑时跳过
                assert new in text, (name, old[:30])
                continue
            assert text.count(old) == 1, (name, old[:30], text.count(old))
            text = text.replace(old, new)
            n += 1
        with open(fp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        total += n
        print("%s: 改动 %d 条 | 行数 %d→%d | 汉字 %d→%d | 换行 %s"
              % (name, n, lines_before, len(text.split(nl)), han_before, han(text),
                 "CRLF" if nl == "\r\n" else "LF"))
    print("总改动条数:", total)


main()
ast.parse(open(__file__, encoding="utf-8").read())