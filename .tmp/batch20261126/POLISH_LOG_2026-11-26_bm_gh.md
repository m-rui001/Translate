# 润色日志 · bm_g / bm_h（2026-11-26）

稿目：`work_batch_20261124/bm_g_zh.json`、`bm_h_zh.json`（The Bright Messenger 穿插章节）
脚本：`work_batch_20261124/_polish_20261126_bm_gh.py`
备份：`bm_g_zh.json.bak_20261126`、`bm_h_zh.json.bak_20261126`
对读：`paras_tool.py show bm_g|bm_h`，两篇均 `offset = len(src) - len(zh) = 0`（篇名不在 `src[0]`，
`zh[i] ↔ src[i]` 逐段对应，段数差 0，无跨段错位）。

## 自检

| 篇 | 段数（改前=改后） | 汉字 | 改动条数 | 改动段数 | 换行符 |
|---|---|---|---|---|---|
| bm_g | 131 = 131 | 14536 | 57 | 41 | LF |
| bm_h | 193 = 193 | 13936 | 41 | 34 | LF |

（bm_h 41 处 = 30 条逐句改动 + 专名归一 10 处（计 1 条）+ 酒名体例 1 处 + 二遍微调 1 处；
bm_g 57 处 = 53 条 + 二遍微调 4 处。）

- JSON 可解析、长度与备份一致、无空段 —— ✓
- 无 ASCII 直引号（本批用「」；篇内用『』作引中之引） —— ✓
- 无 `。。`／`，，`／`、、` 重复标点 —— ✓
- 无「汉字＋空格＋小写英文＋空格＋汉字」残留英文；`N. H.`（原文的姓名缩写记号）与引文保留 —— ✓
- 数组长度、元素顺序、元素内 `\n`（诗行）一律未动；indent=1、LF、文末 `\n` 与原文件一致 —— ✓

改动分布（处）：
- bm_g：① 25　② 4　③ 7　④ 3　⑤ 0　⑥ 17　⑦ 1　＝ 57
- bm_h：① 16　② 2　③ 2　④ 0　⑤ 11（专名归一 10 + 术语 1）　⑥ 9　⑦ 1　＝ 41

## 改动清单 · bm_g

**① 读不通（25）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 9 | 他的结论只有一个结果，他同助手公开得够坦率 → 他的结论里只有一点，他相当坦率地同助手讲了 | 主谓失配，「一个结果……公开得够坦率」不成句。*Only one result of his conclusions he shared openly enough with his assistant* |
| 18 | 那高大的青年挺立在他身旁，姿态安稳 → 那青年高大、挺直、沉着地立在他身旁 | 破折号里的同位语被切成三段短句。*tall, erect and poised beside him* |
| 30 | 我会很看重帮助——一种宗教气质的看法 → 我倒很看重这份帮助——一个宗教气质的人的看法 | 「看重帮助」缺定语，「一种……看法」悬空。*I should value the help--the view of a religious temperament* |
| 47 | 「不会毫无意义地用，」 → 「不是随口说的，」 | 承接上句「不会用这种字眼」，原文是打断对方的辩解。*"Without meaning," the other caught him up at once* |
| 59 | 这太令人错位了 → 这太叫人错乱了 | 「令人错位」不成词。*It was so dislocating* |
| 65 | 菲利里这才知道他也在门框里看见了那姑娘 → 菲利里这才明白，他也看见了门框里那姑娘的身影 | 「在门框里看见」把 framed 读成方位。*he, too, had seen the girl framed in the doorway* |
| 71 | 「记住，潜意识并不能解释一切，」话来了。 → ……话传了过来。 | 「话来了」是 came the words 的硬搬。*came the words* |
| 72 | 总会放进最狂野的不满、探寻和质疑的泛滥 → 最狂野的不满、探寻与质疑便泛滥而入 | 「放进……的泛滥」动宾失配。*always lets in extravagance of wildest dissatisfaction, search and question* |
| 75 | 积累得极其巨大的知识 → 闻所未闻、庞大无比的积累知识 | 「积累得极其巨大」的「得」误用。*an immense accumulated knowledge* |
| 81 | 「……还有别的类型的生命——」他说得鼓励。 → 他鼓励地说。 | 「说得鼓励」不成句。*He spoke encouragingly* |
| 84 | 它是空白的、易受的、准备好的 → 它是空白的、易于感受的、准备好的 | 「易受的」是 receptive 的硬搬。*blank, receptive, ready* |
| 91 | 这一群人的意思是容易读出的 → 这一群人的意味，一眼就看得出来 | 「意思是容易读出的」主谓失配。*The meaning of the group was easily read* |
| 94 | 曾感到自己的心被她投入其中的……情感所打动 → 也曾感到自己的心被她倾注其中的……所打动 | 长句中途丢主语，前半句无谓语中心。*had felt his heart stirred by the true simple feeling she put into it* |
| 94 | 把它提出时空的已知沟渠 → 把它从时空的已知沟渠中提了出来 | 缺介词「从」。*lifting it out of the known ditch of space and time* |
| 94 | 他听着那甜美，这话打在…… → 他听着那甜美的歌声，这话正打在…… | 「听着那甜美」宾语缺失。*as he listened to the sweetness* |
| 101 | 清楚得就像读着最白纸页上的黑字 → 清楚得就像在雪白的纸上读着黑字 | 「最白纸页」缺「的」，且定语杂乱。*a page of whitest paper* |
| 103 | 他毫无颤动地迎住它们 → 他一动不动地迎住那目光 | 「毫无颤动地迎住」不成词。*He met them without a quiver* |
| 103 | 他又抓住了她那温柔的、探询的疑问 → 他接住了她那温柔探询的疑问 | 「抓住……疑问」动宾失配，「的」字堆叠（本条含二遍微调：删去多余的「又」）。*he caught again her tender, searching question* |
| 106 | 她惯于承受较小男人们较小股的倾慕 → 她惯于承受小男人们小股的倾慕 | 「较小男人们」不成话。*smaller jets of admiration from smaller men* |
| 107 | 萦绕着他的预言，以实质充实着他的希望与恐惧的，是一个突出的确断 → ……为他的希望与恐惧充实了实质的，是一个格外分明的确定 | 定语与谓语挤在一句里，读来断裂。*stood one outstanding certainty* |
| 111 | 所以无法接到他的目光 → 所以无法与他的目光相接 | 「接到目光」不成词。*not possible to catch his eye* |
| 116 | 然而足以使他警觉。 → 然而这已足以使他警觉。 | 无主语的残句（原文省略，中文须补）。*Yet enough to set him on the alert* |
| 124 | 正在菲利里山谷幻象的这一刻 → 就在菲利里沉入山谷幻象的这一刻 | 「正在……这一刻」句式悬空。*At which second precisely in Fillery's valley-vision* |
| 129 | 他们一边满足饥饿，外面的雨一边以稳定浸透的声音倾泻 → 他们一边填肚子，外面的雨一边下个不停，发出湿透一切的沉稳声响 | 「满足饥饿」「以稳定浸透的声音」皆非中文。*while they satisfied their hunger, the rain outside poured down with a steady drenching sound* |
| 107＊ | 突出的确断 → 格外分明的确定 | 「确断」生僻，与全篇语域不合。二遍微调 |

**② 「的」字定语堆叠（4）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 81 | 那平静背后半掩着的固执观念的确信 → 那平静底下半掩着的、对一个固定念头的笃信 | 两个「的」叠在中心语前，语义被压没。*the half-concealed conviction of an idee fixe behind the calmness* |
| 101 | 对菲利里那能占卜的心来说 → 对菲利里那颗能占卜的心来说 | 「那……那」相撞，指代与定语混淆。*to Fillery's divining heart* |
| 104 | 跃向了她自己的、神圣的、创造性的太阳 → 跃向那属于她自己的、神圣而创造性的太阳 | 三个「的」并列，节奏塌陷。*leaped towards its own divine, creative sun* |
| 125 | 足以扰乱哪怕最平衡的心智的平衡 → 足以叫哪怕最沉稳的心智也失去平衡 | 「心智的平衡」两个「的」相撞。*upset the equilibrium of even the most balanced mind* |

**③ 外语句法直搬（7）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 40 | 他站得很近——近得可怕——与自然 → 他离自然很近——近得可怕 | 介词短语被搬到句末（is close to Nature）。*he stands close--terribly close--to Nature* |
| 57 | 他知道这片刻的混乱，当那呼喊沿着风飞逝而去的时候 → 当那呼喊沿风飞逝而去时，他才明白…… | 英语后置时间从句照搬；中文从句须前置。*as the cry fled down the wind* |
| 97 | 在这甜美歌声的波浪上形成，由……情感塑造，被……所激发，这两个人创造了…… → 在这甜美歌声的波浪上，凭一种……情感，又被……所激发，这两个人共同造出…… | 三个分词短语照搬成悬空定语，句子没有落脚点。*formed on the waves…, shaped by feeling…, inspired by emotions…* |
| 101 | 那闪过的欢乐与同情的无线信息，被他截收了 → 他也截收了那道闪过的、传着欢乐与同情的无线信息 | 被动式硬搬。*the wireless message of joy and sympathy that flashed he intercepted* |
| 102 | 他极其迅捷的心智，一边观看，一边倾泻下浓缩形式的记忆、反思、判断 → 他一边观看，一边有……记忆、反思与判断源源不断地流过他那极其迅捷的心智 | 「Through his mind poured…」主语照搬，中文主语错位。*Through his extremely rapid mind, as he watched, poured memories…* |
| 105 | 没有嫉妒被搅起 → 他心中没有一丝嫉妒搅起 | 被动硬搬。*No jealousy stirred* |
| 102＊ | ……流过他那极其迅捷的心智，却冷静、稳定，尽管…… → ……；这一切进行得冷静、稳定，尽管…… | 二遍微调：状语无处安放，补出主语。*yet calmly, steadily, though against a background of deep and troubled emotion* |

**④ 代词指代不明（3）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 65 | 「正如你自己也属于别处，」忽然又有人用……低语补上一句 → ……那声音忽然又用……低语补上一句 | 「又有人」把同一说话人读成第三个人。*"As you yourself do, too," was added in a thrilling whisper suddenly* |
| 111 | 他的上司惊讶地发现 → 菲利里倒惊讶地发现 | 前句的「他」是菲利里，「他的上司」指同一人，读者会错认。*his chief surprised* |
| 111 | ——他又完全忘了他在近旁——正……盯着他 → ——他早又忘了此人就在近旁——正……盯着自己 | 一句里三个「他」分指两人。*he had again completely forgotten his proximity* |

**⑥ 硬伤（17）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 7 | 这三人合起来，是懂事的一代 → 这三个人加在一起，在各自那一代人中算得上明白人 | "wise in their generation" 被读成「懂事的一代」。*were wise in their generation* |
| 15 | 以及在同一个姑娘结识之后 → 以及在结识一位姑娘之后 | "the introduction to a girl" 误作「同一个姑娘」。*by the introduction to a girl* |
| 15 | 高出她的女性同类一头一肩 → 远远高出于她的女性同类之上 | "head and shoulders above" 成语直搬。*rose head and shoulders… beyond her feminine kind* |
| 24 | 主教自然宁可让「科林斯神父」的位子空着 → 主教自然宁可要「科林斯神父」腾出来的那间空屋子 | "preferred the room of… to his company" 的双关（空屋／人）被读成「位子」。*The Bishop, naturally, preferred the room of "Father" Collins to his company* |
| 52 | 她似乎被欢喜魔住了 → 她仿佛被欢喜施了魔法 | 「魔住」不成词。*She seemed spellbound with delight* |
| 55 | 他自己也被魔住了一会儿 → 他自己也一时被施了魔法 | 同上。*He stood spellbound himself a moment* |
| 73 | 我们这神话般的旧世界在平衡中发抖 → 我们这神话般的旧世界正悬于一线，摇摇欲坠 | "trembles in the balance" 在危局中，非「在平衡中」。*Our fabulous old world trembles in the balance* |
| 73 | 到处空空荡荡，失去了亲人 → 到处空空荡荡、孤苦无依 | "bereft" 无宾语，擅加「亲人」。*empty and bereft* |
| 96 | 其字面程度，恰如人的灵魂利用熟悉的肉体来显现自己 → 其真切程度，恰如人的灵魂借熟悉的肉体来显现自己 | "as literally as" 是「实实在在、不打折扣」，非「字面」。*as literally as a human spirit uses the familiar physical body* |
| 96 | 去迎接它们所称呼的那位新找到的伴侣 → 去迎接它们所呼唤的那位新找到的伴侣 | "addressed" 是歌声「呼唤」，非「称呼」。*the newly-found companion they addressed* |
| 100 | 几乎就在他眼前裂成花与果 → 几乎就在他眼前绽成花朵与果实 | "breaking into flower and fruit" 误作「裂」。*breaking almost into flower and fruit* |
| 114 | 而菲利里的惊讶，只有一点能与之相比：那张严峻的脸竟柔和得…… → 使菲利里惊讶不亚于此的，是那张严峻的脸竟柔和得…… | "was only equalled by" 比较关系被读成程度比较。*Fillery's astonishment was only equalled by the fact that…* |
| 120 | 他是在娜扬被那青年扛到钢琴边的那几秒里看见这些的 → 他看到这些，只用了娜扬在钢琴边被那青年甩上肩头的那几秒钟 | "swung over the shoulders beside the piano" 地点与动作错位。*Nayan was swung over the youth's shoulders beside the piano* |
| 121 | 即便人类这个物种为他所知也未必 → 甚至人类这个物种于他是否熟悉也成问题 | "even if the species were familiar to him at all" 句意读拧。*even if the species were familiar to him at all* |
| 121 | 他居住在莱斯特的躯架里 → 他居住在莱斯特的躯壳里 | 「躯架」错字。*He inhabited LeVallon's frame* |
| 122 | 这在美味的风与阳光中闪入他心头 → 这在甘美的风与阳光中闪入他心头 | "delicious wind" 误作「美味」。*in the delicious wind and sunshine* |
| 65 | 菲利里这才知道他也在门框里看见了那姑娘 → 菲利里这才明白，他也看见了门框里那姑娘的身影 | 「在门框里看见」把 framed 读成方位。*he, too, had seen the girl framed in the doorway* |

**⑦ 体例（1）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 89 | 不过他心与智的反应却有重要性 → 不过他的心与智的反应却有其重要性 | 缺「其」，与全篇体例不一。*The reactions of his heart and mind, however, have importance* |

## 改动清单 · bm_h

**⑤ 专名归一（2 项，10 处）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 全篇 10 处 | 柯林斯神父 → 科林斯神父 | 同一册（The Bright Messenger）中 bm_g 用「科林斯」23 处、本篇「柯林斯」10 处；按「出现最多者为 canon」归一。*Father Collins* |
| 71 | 投射出自己的『双重身』 → 投射出自己的二重身 | *double* 的通行译法，与社内术语（提婆、元素存在、灵测）体例一致。*project his double consciously* |

**① 读不通（17）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 6 | 水与火彼此相灭 → 水与火彼此相克 | 「相灭」不成词；下文即言「互相仇视的元素」。*Water and fire mutually destroy each other* |
| 26 | 他整个姿态都竖起了累积的挑战与异议 → 他整个人的神气都竖起了刺，满是积攒已久的挑衅与不服 | 「竖起了累积的挑战」不成话。*His whole manner bristled with accumulated challenge and disagreement* |
| 33 | 仍站在他的上司上方 → 仍旧站在上司跟前 | "standing over" 是「立在身旁／当面」，非「上方」。*still standing over his Chief* |
| 39 | 针对人类的『情结』——作为人类 → 针对人类本身的『情结』 | "as such" 被切成独立的尾巴。*against humanity--as such* |
| 42 | ……他除了是……的结果，或者……——除此之外，他还能是什么？ → 他不是……的结果，就是从……学来的（……），或者……——除此之外，你怎么能认为他还有别的可能？ | 双重否定被拆成并列项，句尾悬空。*how can you think it possible, then--that he is other than the result of…* |
| 44 | 我们怎么，」他问道，……「怎么敢——怎么断定——因为我们并非全然无知 → 我们怎么敢——」他问道，……「怎么断定——毕竟我们并非全然无知 | 「我们怎么……怎么敢」重复卡壳。*How shall we venture--how decide--for we are not wholly ignorant, you and I* |
| 53 | 却一个字也没有来 → 却一个字也没等到 | 「一个字没有来」主语与谓语错配。*but no word came* |
| 83 | 一见钟情，或者就这件事说，一见生恨 → 一见钟情，或者就此而言一见生恨 | 「就这件事说」夹在并列项里读不通。*Love at first sight, or hate, for that matter, is always memory* |
| 86 | 「无论如何，我们知道的有一件事，」 → 「无论如何，有一件事我们是知道的，」 | 语序颠倒。*One thing we know, at any rate* |
| 105 | 他停下来，找不着自己了 → 他停下来，找不回自己的话头 | "unable to find himself" 是接不上话，非「找不着自己」。*unable to find himself, his confusion obvious* |
| 146 | 谈话继续下去，一边走一边加速 → 谈话继续下去，越说越有劲 | "gathering impetus as it went" 直搬成走路。*gathering impetus as it went* |
| 150 | 操练那古老被遗忘的魔法 → 操练那古老而被遗忘的魔法 | 缺连词。*practised the old forgotten magic* |
| 150 | 你瞧，那里那巨大的风和热是神性的载体 → 你瞧，在那里，巨大的风和热就是神性的载体 | 「那里那」两个指代词相撞。*were vehicles of deity, you see--there* |
| 172 | 大家普遍有种松了口气的感觉 → 四下里不约而同地像吸了口气 | "a general sense of drawing breath" 是吸气／屏息，非松口气。*There was a general sense of drawing breath as he appeared* |
| 183 | 仿佛置身于那本该属于他的失落的讲坛 → 仿佛又站上了那个本该属于他、如今已经失掉的讲坛 | 定语堆叠致指代不清。*as though he were in the lost pulpit that was his right* |
| 44＊ | 「我们怎么，」他问道…… | 二遍微调，见上（同段） |
| 1（⑥）| 某种内心的热忱漫透了他整个身心 → 浸透了他整个身心 | 「漫透」错字。*some inner enthusiasm pervaded his whole being* |

**② 「的」字定语堆叠（2）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 45 | 那尊敬的、亲爱的友谊的旧纽带 → 那条以敬重和亲爱相连的旧日友谊纽带 | 三个「的」并列，中心语被压没。*the old tie of respectful and affectionate friendship* |
| 146 | 人人似乎都感到一个他们的知识无法解释、任何尘世的解释也无法满足的人格暗示 → 人人似乎都感到某种人格的暗示，那是他们的知识无法解释、任何尘世的解释也无法交代的 | 长定语里三个「的」，「人格暗示」被埋。*the hint of a personality their knowledge could not explain, nor any earthly explanation satisfy* |

**③ 外语句法直搬（3）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 180 | 「一个希腊神，如果我见过的话，」 → 「我要是见过希腊神，那就是他，」 | 条件从句后置直搬。*A Greek God, if ever I saw one* |
| 190 | 总之，人人都找到了舌头，如果说是秘书波维领着这场骚动的话 → 总之，人人都开口了，尽管这场骚动是秘书波维带的头 | 后置让步从句硬搬，句尾悬空。*All found their tongues, at any rate, if Povey, as Secretary, led the turmoil* |
| 146（⑥）| 划下了一道无法解读的符 → 划下一道无法辨认的象形符号 | "hieroglyph" 是象形符号。*scored an undecipherable hieroglyph* |

**⑥ 硬伤（10）**

| 段 | 旧 → 新 | 理由 / 原文 |
|---|---|---|
| 20 | 我在那白色貂皮、裸露的手臂和珠宝把他围住的一瞬看见了他的脸 → 有那么一瞬，我看见他的脸夹在白色貂皮、赤裸的手臂和珠宝中间 | "a moment among…" 被读成「被围住的一瞬」。*I saw his face a moment among the white ermine, the bare arms and jewels that enveloped him* |
| 31 | 等着被这族类所知最好的知识治好 → 等着被人类所知最好的知识治好 | "the race" 本篇统一作「人类」，此处作「这族类」口径不一。*healed by the best knowledge known to the race* |
| 70 | 另一个口袋里装着精神照片 → 装着几帧灵异照片 | "spirit photographs" 是显灵照片，非「精神照片」。*spirit photographs* |
| 71 | 眼睛里有种奇特的强度 → 眼神里有种奇特的炽烈 | "eyes of strange intensity" 误作「强度」。*eyes of strange intensity* |
| 90 | 越过横在两者之间那道定命的鸿沟 → 那道固定不移的鸿沟 | "the gulf fixed"（路加福音语）非「定命」。*the gulf fixed between the two* |
| 146 | 也许每一个人的意识都被催快了 → 被催得更敏锐了 | "quickened" 误作「催快」。*Her consciousness knew an abrupt intensification.（The consciousness in each one, perhaps, had been quickened.）* |
| 167 | 这否定的消息所产生的效果，远不如……惊人兴趣 → 这句否定的话没引起什么反应；真正叫人吃惊的，是……激起的兴趣 | "was as nothing compared to" 比较项错位（效果 vs 兴趣）。*The effect of this negative information was as nothing compared to the startling interest…* |
| 173（⑦）| 再来一杯 moulin a vent → 再来一杯『风车磨坊』 | 西文酒名未译，属体例；此处非引文亦非人名地名。*Bring another moulin a vent and a clean glass* |

## 未改判定（读得通、或有疑但不改）

1. **[15] 伊莱达·基尔科夫**：本篇他处皆作「娜扬」，但此处原文即 *Iraida Khilkoff*，属原作的另一写法（本名／教名），改之即等于改原文，故保留并在日志记明。
2. **[7] 「是懂事的一代」以外的「三人合起来」**：句式口语，未动。
3. **[17] 「他看着金色的蜜蜂吮吸那野杜鹃的蜜——连本地人也不敢去抢，除非甘冒那种危险的、令人亢奋的欢欣」**：`not…without` 的语义（抢蜜须冒危险的欢愉）译得基本对，只是「冒……欢欣」搭配略生硬；属风格边界，不动。
4. **[19] 「他心里的那个东西狂野地与心智对抗」**：*The heart in him played wild against the mind* 用了「那个东西」避复，略失「心／心智」的对举，但读得通，不动。
5. **[37] 引号内「你当然注意到了——你——那些女人的眼睛？」**：原文的自我更正式停顿，保留。
6. **[52] 「仿佛生命被狂喜的、辉煌的、强烈的惊讶暂时攫住了」**：三个「的」并列但均为修饰同一中心语，且是原文三重形容词的复沓，属作者风格，不动。
7. **[58][69][113] 诗行用「／」分行、`\n` 保留**：诗句段末行不带标点，按说明保留。
8. **[59] 「她上楼去为父亲的客人梳妆准备了」**：*make herself ready* 的压缩译法，口语可通。
9. **[90] 「他的镜片工艺完美」**：*his glasses of consummate workmanship* 略硬，但仍通，不动。
10. **[94] 「曲子是她自己作的」**：*the music was her own*（可能是「她自己的曲子」而非作曲），两种读法都通，不擅改。
11. **[103] 「然后又以迅速变化的焦点，一闪之间转向他自己的」**：「他自己的」指菲利里的眼睛，上下文可辨，未改。
12. **[105] 「那必须由他奇特天性的全部力量加在她身上的东西」**：定语冗长但有原文依据（*must bring to bear upon her*），未拆。
13. **[119] 「他看见「N. H.」在一片明亮的翡翠草地上……」整段**：长句多、复沓多，属原文气势，除「躯架」外未动。
14. **[131] 「时机也是选定的，地点也是——」**：破折号后的长插入语是原文修辞（*The moment, too, was chosen, the place as well*），保留。
15. **[147] 分隔行「＊　＊　＊　＊　＊」**：原文 `* * * * *`，体例保留，段末无标点属正常。
16. **[161] 「「哦，那场实验，对，唔——我知道的就是，」」**：口语断续，原文即 *Oh, the experiment, yes, well*，保留。
17. **[171] 「在讨论别的信仰……的口令」**：*shibboleth* 作「口令」可通（通行译法之一），未改。
18. **[174] 「街上又湿又冷」**：*raw and bitter* 略弱于原文的「阴冷刺骨」，但不动。
19. **[178] 「这次半属教会的来访把局面弄复杂了」**：*This semi-clerical visit complicated* 的略译，可通。
20. **[24] bm_g「主教自然宁可要「科林斯神父」腾出来的那间空屋子，也不愿与他为伴」**：改后保留了 *room* 的双关；此处不再作更深处理（原文的英式谐趣无法完全移植）。