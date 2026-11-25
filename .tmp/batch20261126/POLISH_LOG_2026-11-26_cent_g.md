# POLISH LOG — cent_g（2026-11-26）

## 一、对齐说明（offset ≠ 1）

`paras_tool.py show cent_g` 报 `src=156 zh=150 offset=6`。**该自动对齐不可用**：
原文里夹着 6 段未译的章号小标题（`src` 索引 0 `XXXI`、8 `XXXII`、37 `XXXIII`、
62 `XXXIV`、80 `XXXV`、103 `XXXVI`），工具按 `src[i+6]↔zh[i]` 硬对齐，结果把
zh[0]（「那是春天——潘的笛声」）接到了 src[6]（`In front his big leader...`），全篇错位。

实际对齐为：**`zh[i]` ↔ 剔掉上述 6 个章号段之后的 `src[i]`**，即
`zh[0]`↔`src[1]`、`zh[7]`↔`src[9]`、`zh[8]`↔`src[10]`（引诗署名行）……末尾
`zh[149]`↔`src[155]`。按此逐段人工核对了 150 段，**无一处分段差异**；段数差 6 全部来自
那 6 个章号段，未增删任何段。

## 二、自检

| 篇 | 段数（改前→改后） | 汉字 | 改动数 | 换行符 |
|---|---|---|---|---|
| cent_g | 150 → 150 | 16658 | 30 条／28 段 | CRLF（indent=2，照原样） |

- JSON 可解析 ✓　段数与备份一致（150）✓　无空段 ✓
- 无 ASCII 直引号 `"` ✓　无 `。。`／`，，` 类重复标点 ✓　无残留英文 ✓
- 每段 `\n` 数（诗行分行）与改前逐一相同 ✓　无 `⟦⟧` ✓
- 备份：`cent_g_zh.json.bak_20261126`（本轮开工时已存在，未覆盖）
- `python work_batch_20261124/check_batch.py cent_g` → `checked 1, with problems 0, paras 150, han 16658`

改动分类：①读不通 13　②「的」字堆叠 6　③外语句法 1　④指代 3　⑤专名 0　⑥硬伤 7　⑦体例 0

## 三、改动清单

| # | 段 | 类 | 旧 | 新 | 理由 |
|---|---|---|---|---|---|
| 1 | zh[6] | ① | 他四周摊着这整片开满花的、巨大而安静的高加索的存在，在闲暇里啜饮阳光。 | 他四周摊着这整片开满花的高加索存在，巨大而安静，正闲暇地啜饮着阳光。 | 「drinking in the sunshine at its leisure」的悬空分词被搬成无主语的尾缀，补出主语「它／正…啜饮着」。原文：*About him lay this whole spread being of the flowered Caucasus, huge and quiet, drinking in the sunshine at its leisure.* |
| 2 | zh[12] | ① | 他没法满足，因为他不能满足。 | 他没有回答，因为他答不上来。 | 「satisfy / could not」同一动词照搬两遍，中文成同义反复；拆为「回答／答不上来」。原文：*he did not satisfy, because he could not.* |
| 3 | zh[29] | ① | 因锐利的欢乐而沉醉，微弱下去 | 因锐利的欢乐而沉醉，渐渐低微下去 | 「faint with…」是声音的谓语，原译两个谓语并列且「微弱下去」无所属。原文：*his voice fell, like music that makes giddy the dim brain, faint with intoxication of keen joy.* |
| 4 | zh[33] | ① | 以某种精神的方式，我活了起来，看清了 | 在某种精神的方式上，我心中豁然一亮，看清了 | 「quickened to the view」误作「我活了起来」；主语是「我」的领悟，补出。原文：*In some spiritual way I quickened to the view that…* |
| 5 | zh[39] | ① | 它们是——不真的； | 它们是——假的； | 「untrue」形容词直搬，「不真的」不成话。原文：*they were--untrue* |
| 6 | zh[45] | ① | 它注满一间又一间室， | 它注满一间又一间屋子， | 「chamber after chamber」逐字作「室」，单字不成词。原文：*Filling chamber after chamber* |
| 7 | zh[46] | ① | 大地的种种性质也同样，如此轻易地，都装在他自己之内。 | 大地的种种性质同样也在他自己之内，如此轻易地就容纳下了。 | 「so easily contained」的独立分词被搬成插入状语，句子失主谓；改回正常语序。原文：*The qualities of all the Earth lay too, so easily contained, within himself.* |
| 8 | zh[54] | ① | 某种类似的、上涌的欢喜也在我胸中半破开来 | 某种相似的欢喜也在我胸中涌起，隐隐要破裂开来 | 「half breaking in my breast」直搬成「半破开来」，动作不成立。原文：*some similar rising joy half breaking in my breast* |
| 9 | zh[54] | ① | 「这总算点什么——」 | 「这总算一点什么——」 | 「总算点什么」口语卡顿，缺量词。原文：*“That's something--”* |
| 10 | zh[66] | ① | 在它们巨人的美里永恒。 | 在它们那巨人的美中长存不朽。 | 「eternal in their giant beauty」省略系词被搬来，中文得补谓语。原文：*eternal in their giant beauty* |
| 11 | zh[92] | ① | 接着又一声吼，一个既巨大又单纯的手势，他似乎立起来 | 接着又一声吼，又做一个既巨大又单纯的手势，他似乎立起来 | 「and a gesture that…」并列名词照搬，中文缺谓语，成悬空短语。原文：*Then, with another roar, and a gesture that was somehow both huge and simple, he seemed to rise and paw the air.* |
| 12 | zh[112] | ① | 视觉毕竟只是一种不完整的认知形式——一样他已经留在身后的东西——留在别处了。 | 视觉毕竟只是一种不完整的认知形式——一样他早已丢在身后、丢在别处的东西。 | 「left behind--elsewhere」两处「留」撞车，第二处悬空。原文：*a thing he had left behind--elsewhere.* |
| 13 | zh[136] | ① | 骄傲、强健而悲剧。 | 骄傲、强健而悲怆。 | 「tragic」名词化直搬，中文不能以「悲剧」作谓语形容词。原文：*proud, strong, and tragic.* |
| 14 | zh[28] | ② | 我没法假装有超过一种模糊的同情的理解。 | 我没法假装自己懂得更多，至多只是一种模糊而同情的领会。 | 「模糊的同情的理解」三个「的」压住中心语，且「有超过一种」是 *more than a* 的硬搬。原文：*I could not pretend more than a vague sympathetic understanding* |
| 15 | zh[30] | ② | 它徒然搏动着，抵着文明铺下的伦敦砖石路面的窒息重压 | 它徒然搏动着，顶着文明铺下的伦敦砖石路面那令人窒息的重压 | 「文明铺下的／伦敦砖石路面的／窒息重压」三「的」连缀，拆成动宾＋「那…的重压」。原文：*beating in vain against the suffocating weight of London's bricks and pavements laid by civilization* |
| 16 | zh[61] | ② | 空气因一片流动的色调的雾而变得灿烂。 | 空气透过一片流动变幻的色雾，变得灿烂。 | 「流动的色调的雾」三「的」套叠，且「色调的雾」非汉语搭配。原文：*The air turned radiant through a mist of running tints.* |
| 17 | zh[101] | ② | 它以惊人的活力和深厚的信念之丰盈从他唇间倾出。 | 它带着惊人的活力与丰盈深厚的信念，从他唇间倾出。 | 「深厚的信念之丰盈」名词串不可读，改「丰盈深厚的信念」。原文：*With an astonishing vitality and a wealth of deep conviction it all poured from his lips.* |
| 18 | zh[114] | ② | 一阵风一般的力量的吼声充满了天空 | 一片挟着风一般巨力的吼声充满了天空 | 「风一般的力量的吼声」三「的」连缀。原文：*A roar of windy power filled the sky* |
| 19 | zh[133] | ② | 无论他是否记得这些从已被抛在身后的外在世界来的、结巴却意味深长的话，它们所影射的真理升起来，把他接住了 | 这些言语说得结巴，却意味深长，来自已被抛在身后的外在世界。无论他是否记得，它们所影射的真理都升起来，把他接住了 | 「从…来的、结巴却意味深长的」三「的」把「话」压到最后；断为两句。原文：*Whether or not he remembered these stammering yet pregnant words from the outer world now left behind, the truth they shadowed forth rose up and took him* |
| 20 | zh[22] | ③ | 「不算坏的一个词，」他笑了；「当然，就其所及而言，也不算错的一个。 | 「这词不算坏，」他笑了；「当然，就它所能及的而言，也算不上错。 | 「Not a bad word」「not a wrong one」冠词式语序硬搬，中文「一个」后无中心语。原文：*“Not a bad word,” he laughed; “certainly, as far as it goes, not a wrong one.”* |
| 21 | zh[69] | ④ | 与几个只比他略低的峰一起 | 与几座只比它略低的峰一起 | 「others but slightly lower than himself」的 himself 指卡兹别克峰，原译「他」把读者引向人物；且山峰量词用「座」。原文：*the pyramid of Kasbek, with others but slightly lower than himself, stared down upon them* |
| 22 | zh[93] | ④ | ——对方脚下的声音已经融进那另一种更广大的踏地声里 | ——那蹄声已经融进另一种更广大的踏地声里 | 同句前文已用「对方」指那身形，此处再出现两个指代易与「他」混。原文：*the sound of his feet already merged in that other, vaster tramping* |
| 23 | zh[143] | ④ | 它们那双大褐眼总欢喜地寻找他的眼睛。 | 它们那两双大褐眼总欢喜地寻找他的眼睛。 | 两头兽共四眼，「那双」量词错，且与主语「它们」相抵。原文：*Their big brown eyes continually sought his own with pleasure.* |
| 24 | zh[44] | ⑥ | 把它们的假象当作完整的化身摆在生命的边缘，而其实它们只是背后那些永恒原型的不完整的、象征性的表现 | 看它们在生命的边缘冒充完整的化身，其实只是背后那些永恒原型的局部而象征性的表现 | *masquerading* 的主语是「这些力」，原译成了「现代生活把假象当作化身」，动作方向反了；兼收「不完整的、象征性的」的「的」字。原文：*dealt only with these forces when they had emerged, masquerading at the outer rim of life as complete embodiments, whereas actually they are but partial and symbolical expressions of their eternal prototypes behind.* |
| 25 | zh[52] | ⑥ | 还是年年月月、分分秒秒？—— | 还是几年与几分钟？—— | *or was it years and minutes?* 是对「日日夜夜」的悖论式反照，原译「年年月月、分分秒秒」把两词各自叠成词组，悖论消失。原文：*--or was it years and minutes?--* |
| 26 | zh[66] | ⑥ | 从未完全收回。 | 从未被完全收回。 | *never quite withdrawn* 是「（被她）收回」的被动，原译成主动，主语误落到「最早的诸族」身上。原文：*the earliest races half divined and worshipped, and never quite withdrawn.* |
| 27 | zh[70] | ⑥ | 用她那银灰色的建筑群 | 用她那银色的建筑群 | *silvery* 是「银色／银白」，「银灰」是另一种色阶。原文：*building with her masses of silvery architecture a barrier that rose to heaven.* |
| 28 | zh[78] | ⑥ | 却不许你的父被看见—— | 却不许你的父看见—— | *Forbidden thy Father to see* 是「你的父被禁止去看（你）」，原译加了「被」把方向翻成「被看见」。原文：*Forbidden thy Father to see, Who is older and greater than thou* |
| 29 | zh[98] | ⑥ | 「在这里我们只是憔悴萎缩， | 「在这里我们只是登顶又衰微， | *peak and dwindle* 是「到顶又衰微」的升降对举，原译把 peak 读成「憔悴」。原文：*Here we but peak and dwindle* |
| 30 | zh[104] | ⑥ | 因为这些会限制、囚禁、贬小 | 因为这些会限制、囚禁、贬低 | *belittle* 无「贬小」一词。原文：*For these confine, imprison, and belittle* |

## 四、未改判定（读得通／改了会伤文气）

1. **zh[8] zh[36] zh[60] zh[79] zh[100] 引诗署名行**：`——F. W. H. 迈尔斯《宇宙观》。`／`——E. B. 勃朗宁。` 等，行末均带句号，全篇自洽；有原诗题者补题名（《宇宙观》《五月颂》），无题者只署名，与原书一致，不动。
2. **zh[50] zh[108] zh[111] zh[117] zh[122] zh[128] zh[134] zh[140] zh[147] 分节星号**：作 `＊　＊　＊　＊　＊`（全角星＋表意空格），十处一律，属体例既定，不动。
3. **zh[4] zh[35] zh[76]–[78] zh[98]–[99] 引诗分行**：`\n` 断行与原文行数对应，末行不带标点者按原诗断行保留；只动了 zh[98] 首行的词义硬伤（见清单 #30 前一条），未改行数。
4. **zh[20]「某个伟大的引导性念头」、zh[29]「破旧的灰衣服」、zh[64]「这丰盈的、驱策着的生命」一类**：字面直但读得通，属译者朴拙一路，不动。
5. **zh[44]「他算是半路遇见了那些事物，在它们前往外在物质世界…的路上」**：长句，但 *met things halfway, en route for…* 的迂回结构已译清，断句会伤这册的绵密腔，不动。
6. **zh[83]「那些丛簇在草皮上掠过得太快，不像是这样」**：`for that` 的指代偏虚（指「被风撒遍山坡」），但上下文可复，改则须重写整句，判为可读，不动。
7. **zh[95]「甲板上那父母奇异的散发」**：原文 *the parent's curious emanations* 单数所属，所指（父／母）在此篇内无硬证，不擅改，留待统一校订。
8. **zh[125]「看见自己与大地共享」**：*sharing the Earth* 的宾语省略，中文明说会添字，判为可读，不动。
9. **zh[80]「尽管他说，「睡眠」既意味着意识的丧失…」**：说话人标签夹在句中，但全篇仅此一处如此行文，不属成体系的体例问题，未动（若全册统一校订，可并入⑦处理）。
10. **zh[128]–[149] 各段**：长句多、意象密，多处「的」字成串但未到压没中心语的地步（如 zh[148]「带着几乎不可能的美，纤细如百合」），按「读得通但不漂亮一律不改」保留。