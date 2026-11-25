# POLISH LOG — hc_a（2026-11-26）

## 0. 对齐说明

`paras_tool.py show hc_a` 报 `src=139 zh=139 offset=0`。

本篇 `_hc_a_paras.json` **首项即正文**（无篇名行），故 offset=0，`zh[i]` 直对 `src[i]`，非 README 所述 offset=1 的常规情形。逐段核对无错位，未增删段。

## 1. 自检

| 篇 | 段数（改前） | 段数（改后） | 汉字 | 改动数 | 换行符 |
|---|---|---|---|---|---|
| hc_a | 139 | 139 | 17269 | 38 条（涉 35 段） | CRLF |

- 备份：`hc_a_zh.json.bak_20261126`（新建，未覆盖既有备份）
- 脚本：`_polish_20261126_hc_a.py`（结尾 `ast.parse` 自查通过）
- 自检项：JSON 可解析 ✓／数组长度与备份一致 139 ✓／无空段 ✓／无 ASCII 直引号 `"` ✓／无 `。。`「，，」类重复标点 ✓／无 `；——`「：——」错配 ✓／引号成对 ✓／无 `⟦⟧` ✓／无「汉字＋空格＋小写英文＋空格＋汉字」残留 ✓
- `check_batch.py hc_a`：`checked 1, with problems 0, paras 139, han 15015`
- 分类合计：①12 ②7 ③6 ④2 ⑥7 ⑦4

## 2. 改动清单

### ① 读不通（12）

1. **段8**
   - 旧：「因为她无论怎样解释，都说不动她相信一个叫「眨眨」的人会是和气温柔的」
   - 新：「因为她无论怎样解释，都劝不动她去相信：一个叫「眨眨」的人会是和气温柔的」
   - 理由：「说不动她相信」是动补结构硬带小句宾语，谓语塌了；改为「劝不动她去相信」＋冒号引出小句。
   - 原文：*for no amount of explanation could persuade her that a person named Winky could be nice and gentle*

2. **段11**
   - 旧：「而埃尔莎对罗恩格林那番过早的放肆，这个故事总能触动他的敬畏之心。」
   - 新：「而埃尔莎对罗恩格林那番过早的放肆的故事，总能触动他的敬畏之心。」
   - 理由：原句把主语提出来又用「这个故事」复指，成了悬空话题＋双主语；合为一个名词短语。
   - 原文：*and the story of that premature audacity of Elsa with Lohengrin never failed to touch his sense of awe*

3. **段49**
   - 旧：「身后门关上的响声，就是最后一片静水也过去了——那片水面上原本还可能靠岸。」
   - 新：「身后门关上的响声，就是最后一片静水也流过去了——在那片水面上，原本还可能靠得了岸。」
   - 理由：「就是……也过去了」缺主谓衔接；补「流」字立住谓语，破折号后补介词与句末落点。
   - 原文：*The noise of the door closing behind him was the passing of the last bit of quiet water across which a landing to the bank might still have been possible.*

4. **段51**
   - 旧：「这在活人脸上极少见到，即便有，也只是在少数把一生过到最高境地的人死后、死亡温柔地留在他们五官上的那副安息面具背后，隐隐暗示过。」
   - 新：「这在活人脸上极少见到；即便有，也只是隐约的暗示——在少数把一生过得最为高贵的人脸上，死亡温柔地留下那副安息的假面，表情就藏在它背后。」
   - 理由：原句「在……死后、死亡温柔地留在……的那副面具背后，隐隐暗示过」三层套叠，主谓跨了四十余字全散；拆成判断句＋破折号说明。
   - 原文：*rarely, if ever, seen upon a human face alive, and only here and there suggested behind that mask of repose which death leaves so tenderly upon the features of those few who have lived their lives to noblest advantage.*

5. **段58**
   - 旧：「这又给他那些害他懵懂的谜样条目添了一条。」
   - 新：「这又给那些叫他懵懂的怪事添了一条。」
   - 理由：「害他懵懂的谜样条目」定语倒装生硬，且「给他……添了一条」双宾读不通；理顺。
   - 原文：*he merely noted that it added one more to the puzzling items that caused his bewilderment*

6. **段68**
   - 旧：「极其精致地颤栗了他。」
   - 新：「极其精妙地使他浑身颤栗。」
   - 理由：`thrilled him` 被硬搬成「颤栗了他」，中文「颤栗」不及物；改使动。
   - 原文：*a melodious, haunting phrase of music that thrilled him exquisitely*

7. **段75**
   - 旧：「然而带着一种伟大而天然的骄傲而强健。」
   - 新：「然而带着一种伟大而天然的骄傲，强健有力。」
   - 理由：「骄傲而强健」把名词与形容词用「而」并列，句子收不住；断开。
   - 原文：*perfectly simple, yet strong with a great and natural pride*

8. **段77**
   - 旧：「她毫无羞怯的痕迹地说」
   - 新：「她毫无羞怯之色地说」
   - 理由：「毫无羞怯的痕迹」带「地」作状语不成立；换「毫无羞怯之色」。
   - 原文：*she said, without a trace of shyness*

9. **段87**
   - 旧：「桌对面忽然响起一个柔和低低的声音」
   - 新：「桌对面忽然响起一个柔和低沉的声音」
   - 理由：「柔和低低」叠词误粘，缺并列标记。
   - 原文：*suddenly sounded soft and low across the table*

10. **段101**
    - 旧：「在他们那里，这光是从一副或多或少的、被磨损、有阅历的皮肉之衣里冲出来的。」
    - 新：「在他们那里，这光是穿过一副多少有些蒙尘、被磨损而有阅历的皮肉之衣冲出来的。」
    - 理由：「或多或少的、被磨损、有阅历的」三层定语以顿号与「的」交替堆叠，中心语被压没；改动词句「穿过……冲出来」。
    - 原文：*In their case it had forged its way through the more or less defiling garment of a worn and experienced flesh.*

11. **段116**
    - 旧：「斯宾罗宾急急地、带着一阵扑动地翘起腿。」
    - 新：「斯宾罗宾急急地翘起腿，带着一阵扑动。」
    - 理由：两个「地」状语相撞，后一状语无处安放；移到句末作补述。
    - 原文：*Spinrobin crossed his legs with a fluttering motion, hastily.*

12. **段126**
    - 旧：「「那灵呢？」」
    - 新：「「那么灵呢？」」
    - 理由：`And spirits?` 是承接上一个问句的追问，单用「那」不成话。
    - 原文：*"And spirits?"*

### ② 「的」字定语堆叠（7）

1. **段20**
   - 旧：「只因他喜欢那语言里那些神祇与天使的、漂亮而高亢的名字。」
   - 新：「只因他喜欢那语言里神祇与天使那些漂亮而高亢的名字。」
   - 理由：三个「的」＋顿号把「名字」压到最后；去掉一层所属定语。
   - 原文：*because he liked the fine, high-sounding names of deities and angels to be found in that language*

2. **段22**（其一）
   - 旧：「他想象着一位被某种奇异癖好所占的梦想家式的牧师，」
   - 新：「他想象着一位梦想家式的牧师，给某种奇异的癖好占着，」
   - 理由：「被……所占的……式的」双重长定语；拆成主句＋后置谓语。
   - 原文：*He imagined some dreamer-priest possessed by a singular hobby*

3. **段22**（其二）
   - 旧：「在他心里拨响了自他童年相信名字、相信名字之意义的日子以来再没振动过的弦。」
   - 新：「在他心里拨响了久已不响的弦——自他童年相信名字、相信名字之意义的日子以来，那些弦就再没振动过。」
   - 理由：四十字定语压在「弦」上；先立中心语，再用破折号补时间状语。
   - 原文：*set chords trembling in him that had not vibrated since the days of his boyhood's belief in names and the significance of names*

4. **段44**
   - 旧：「盘叠的山间所居的寂静落到他们脚步四周」
   - 新：「盘叠的山峦间那种常驻的寂静落到他们脚步四周」
   - 理由：`the silence that dwells in the folded hills` 的关系从句直搬成「所居的」；改为「那种常驻的」。
   - 原文：*the silence that dwells in the folded hills fell about their steps*

5. **段60**
   - 旧：「效果是叫他目盲的、完全的占有。」
   - 新：「效果是一种炫目而完全的占有。」
   - 理由：「叫他目盲的、完全的」两「的」并列且第一层不成定语（`blinding` 被误读作「叫他目盲」）。
   - 原文：*with the effect of a blinding and complete possession*

6. **段63**
   - 旧：「他觉察到自己小小的灵的内殿里有什么荣耀的新东西在幸福地振动。」
   - 新：「他觉察到自己小小灵魂的内殿里有什么荣耀的新东西在幸福地振动。」
   - 理由：三个「的」串成「小小的／灵的／内殿」；「灵」并回「灵魂」，减一层。
   - 原文：*He was aware of some glorious new thing in the penetralia of his little spirit, vibrating with happiness.*

7. **段66**
   - 旧：「而那种唯恐「米——」竟是「米兰达」「桃金娘」或别的什么可怕东西的一部分的恐惧，立刻过去了。」
   - 新：「而那种恐惧——唯恐「米——」竟是「米兰达」「默特尔」或别的什么可怕名字的一部分——立刻过去了。」
   - 理由：近五十字的定语压在「恐惧」上，读者到句末才知主语；先出「那种恐惧」，内容用破折号插入。
   - 原文：*the feeling of dread that "Mir--" might prove to be part of "Miranda," "Myrtle," or some other enormity, passed instantly.*
   - 附：同句「桃金娘」为 `Myrtle`（女子名）误按植物名译，改为通行译名「默特尔」；该点属⑥硬伤，与②合并在本条整改。

### ③ 外语句法直搬（6）

1. **段12**
   - 旧：「彼此之必需，如同同一和弦里的两个音……」
   - 新：「彼此互为必需，如同同一和弦里的两个音……」
   - 理由：`as necessary to one another` 的名词化直搬，「彼此之必需」不成谓语。
   - 原文：*as necessary to one another as two notes in the same chord*

2. **段14**
   - 旧：「从他较近的意识里扫走了」
   - 新：「从他意识较近的地方扫走了」
   - 理由：`from his nearer consciousness` 的「较近的＋名词」直接照抄，中文这个搭配不通。
   - 原文：*which education and conflict with a prosaic age had swept away from his nearer consciousness*

3. **段21**
   - 旧：「以至于视之为无足轻重，与灵性知识相比——尤其当……」
   - 新：「以至于与灵性知识相比，视之为无足轻重——尤其当……」
   - 理由：`consider it of small account compared to spiritual knowledge` 的比较状语被悬在句末，无所附丽；前置。
   - 原文：*so far indifferent to worldly success as to consider it of small account compared to spiritual knowledge*

4. **段32**
   - 旧：「而且很快，这些无名的品质就开始显形」
   - 新：「很快，这些无名的品质就开始显形」
   - 理由：段首 `And very soon` 的 `And` 机械照搬，段首「而且」无上文可承（上一段已收尾）。
   - 原文：*And very soon it was that these nameless qualities began to assert themselves*

5. **段54**
   - 旧：「向管家的介绍打断了他的思绪；」
   - 新：「管家过来同他相见，打断了他的思绪；」
   - 理由：`An introduction to the housekeeper interrupted…` 抽象名词主语照搬；改为人物动作句。
   - 原文：*An introduction to the housekeeper interrupted his reflections*

6. **段74**
   - 旧：「秘书为此更加对他生出好感，即使不为别的理由。」
   - 新：「秘书为此更加对他生出好感，哪怕不为别的，只为这一点。」
   - 理由：`if on no other` 的省略式对举硬搬成「即使不为别的理由」，读者不知所云。
   - 原文：*the secretary warmed to him on that account more than ever, if on no other*

### ④ 代词指代不明（2）

1. **段24**
   - 旧：「而当他把票交给站长、自报是菲利普·斯凯尔先生时，一个巨大人影沿月台大步走来——没戴帽子……——他更是惊讶。」
   - 新：「而当他在站长面前交票时，一个巨大人影沿着月台大步走来——没戴帽子，穿着灯笼裤，一大把飘动的灰胡子，自报是菲利普·斯凯尔先生——他更是惊讶。」
   - 理由：原译把 `announced himself as Mr. Philip Skale` 的主语误系于「他」（斯宾罗宾），读成秘书自称是斯凯尔；自报者实为来迎的巨人，须移到巨人的定语串里。
   - 原文：*but he was surprised to find only a rickety little cart … and still more surprised when a huge figure of a man, hatless, dressed in knickerbockers, and with a large, floating grey beard, strode down the platform as he gave up his ticket to the station-master and announced himself as Mr. Philip Skale.*

2. **段42**
   - 旧：「他引起的那种模糊敬畏，大概只是使之更强。」
   - 新：「他引起的那种模糊敬畏，大概只会使它更强。」
   - 理由：「之」与「它」并用且「之」指代含糊（吸引力？敬畏？）；统一为「它」并加「会」立住推断语气。
   - 原文：*that vague awe he roused probably only increased it*

### ⑥ 硬伤（7）

1. **段47**
   - 旧：「直到按时走出环绕的树林」
   - 新：「直到终于走出环绕的树林」
   - 理由：`in due course` 被读成「按时」（守时刻），实为「到时候、终于」。
   - 原文：*till in due course they emerged from the encircling woods*

2. **段49**
   - 旧：「一场大奇遇的贪欲正把他往前拉」
   - 新：「一场大奇遇的渴望正把他往前拉」
   - 理由：`the lust of a great adventure` 此处 `lust` 是「渴慕、热望」，非贬义「贪欲」。
   - 原文：*the lust of a great adventure drawing him forward*

3. **段53**
   - 旧：「那是很好的头骨，配上那管主导性的鼻子和蓬乱纠结的须发」
   - 新：「那是很好的头颅，配上那管气势逼人的鼻子和蓬乱纠结的须发」
   - 理由：`a fine head` 是「一颗好头颅」，非解剖学的「头骨」；`dominating nose` 是「逼人的鼻子」，非「主导性的」。
   - 原文：*It was a fine head with that dominating nose and the shaggy tangle of hair and beard*

4. **段59**
   - 旧：「有什么迷人、极其美味的东西侵入了他的生命之流」
   - 新：「有什么迷人、极其美妙的东西侵入了他的生命之流」
   - 理由：`utterly delicious` 在此为通感性的「极其美妙」，译「美味」落到味觉，词义窄化。
   - 原文：*he became suddenly conscious that something attractive and utterly delicious had invaded the stream of his being*

5. **段75**
   - 旧：「一个身不由己出身低微的姑娘」
   - 新：「一个出身低微的姑娘」
   - 理由：`perforce of humble origin` 的 `perforce` 是「必然、不由她选」，与「身不由己」叠用后语义打架，且两「的」挤在一处。
   - 原文：*a girl who was perforce of humble origin*

6. **段86**
   - 旧：「他觉察到她是有目的地说话」
   - 新：「他觉察到她说话是有用意的」
   - 理由：`talking with a purpose` 被读成「有目的地」（目的地），是典型同形误读。
   - 原文：*He became aware that she was talking with a purpose*

7. **段93**
   - 旧：「奇妙……精致……美味。」
   - 新：「奇妙……精致……甘美。」
   - 理由：同段59，`delicious` 为通感赞叹；「甘美」保留感官性而不落味觉实指。
   - 原文：*It was wonderful … exquisite … delicious.*

（⑥共 7 条：段47、49、53、59、75、86、93。段66 的「桃金娘→默特尔」属人名误译，已并入上面②第 7 条一并整改。）

### ⑦ 体例（4）

1. **段18**
   - 旧：「作饵的那则广告是这样写的：——」
   - 新：「作饵的那则广告是这样写的：」
   - 理由：冒号与破折号连用，全册无此例；引文由冒号引出即可。
   - 原文：*The advertisement that formed the bait read as follows:--*

2. **段39**
   - 旧：「它就躺在它们嘴里，」秘书的目光往深处看去」
   - 新：「它就躺在它们嘴里。」秘书的目光往深处看去」
   - 理由：引号内句末用逗号，后接的却是叙述句而非说话人标签，读成「秘书的目光说」；改为句号断开。
   - 原文：*"How the mountains positively eat it up. It lies in their very jaws," and the secretary's eyes, traveling into the depths, made out…*

3. **段52**
   - 旧：「纳闷：是什么产生了它；——是否有一天，那也会是他的。」
   - 新：「纳闷：究竟是什么产生了它，是否有一天那也会是他的。」
   - 理由：分号＋破折号连用（「；——」），且句子未终；改为逗号并列的两个疑问小句。
   - 原文：*He wondered with a rush of sudden joy what produced it;--whether it might perhaps one day be his too.*

4. **段55**
   - 旧：「她左臂是」——他迟疑了极短的一瞬——「萎缩的。」
   - 新：「她左臂是——」他迟疑了极短的一瞬，「萎缩的。」
   - 理由：破折号被切成两截分置引号内外，句子在引号中断开无处收；改为引号内带破折号表示中断，迟疑语落在引号外。
   - 原文：*Her left arm is"--he hesitated for a fraction of a second--"withered."*

## 3. 未改判定

- **「牧师」保留**：`priest / clergyman / curate` 全篇一律作「牧师」／「助理牧师」（[22][26][27][36][48][55][64][82][100][110][112] 等十余处），本册 canon 已立，按「以出现最多者为 canon」不动；未按通则改「教士」。
- **「莫尔太太」的敬称**：原文 `"Mrs." Mawle`（引号标出 courtesy-title，暗示她并非真姓太太），译文以「莫尔太太」＋括注「显然是敬称」处理，通篇一致，保留。
- **「以 M 开头」等西文前后空格**：batch 内 `cent_b`、`pf_d`、`pf_o`、`willows_a` 等篇同为「汉字＋空格＋单字母」体例，本篇 3 处与全批一致，不改。
- **段9「比头一个还能蹦，蹦两倍」**：`twice as hoppy as the first` 的直译复沓，虽欠圆熟但读得通，属不改范围（读得通但不漂亮）。
- **段31「他觉得自己一脚踩空，落进了全然陌生的深水」**：`out of his depth` 的意译，意思对，保留。
- **段37「某种原素之力」**：`Elemental force`，「原素」为旧译常用词，非错字，保留。
- **段3「从十点到凌晨四点——直到他悄悄爬回育儿室自己那个角落——」**：以破折号插入 `when` 从句，是合理的中文处理，未改。
- **段27「四肢干净笔直」**（`clean, straight limbs`）、**段23「无政府主义者的领带」**（`anarchist tie`）：直译而可解，属作者刻意笔法的移植，保留。
- **篇名**：`_hc_a_paras.json` 无篇名项（首项即正文），`_zh.json` 亦不含篇名，未补。
- **诗行／`\n`**：本篇无分行段，所有元素内无 `\n`，未动。