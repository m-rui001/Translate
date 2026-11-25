# 润色日志 2026-11-26 — cent_d（单篇）

篇目：`cent_d`（源章 XVII–XXII，`_cent_d_paras.json` 138 段含篇名；`cent_d_zh.json` 132 段）
脚本：`_polish_20261126_cent_d.py`（`python _polish_20261126_cent_d.py`，`--dry` 可空跑）
备份：`cent_d_zh.json.bak_20261126_cent_d`（本轮动工前快照，56 499 B）；
　　　既有 `cent_d_zh.json.bak_20261126`（56559 B，上一轮动工前）与 `*.bak_20261125` 未覆盖、未改动。
对齐工具：`_align_cd_20261126.py cent_d 0 132`（按核定 offset 分段表导出逐段对照）。

## 〇、对齐（offset = 6 ≠ 1，须写明）

`paras_tool.py show cent_d` 报 `src=138 zh=132 offset=6`，但**全文并非同一 offset**：
译稿没有把原文中独占一段的章号行译出（既有体例，未增段补译），offset 由 1 阶跃到 6。
阶梯点（zh 索引）与丢掉的源段：

| zh 起点 | 此前 offset | 此后 offset | 被丢的源段 |
|---|---|---|---|
| zh[0] | — | 1 | `src[0]`「XVII」（篇名／章号） |
| zh[17] | 1 | 2 | `src[18]`「XVIII」 |
| zh[42] | 2 | 3 | `src[44]`「XIX」 |
| zh[62] | 3 | 4 | `src[65]`「XX」 |
| zh[82] | 4 | 5 | `src[86]`「XXI」 |
| zh[93] | 5 | 6 | `src[98]`「XXII」 |

分段核数：17 + 25 + 20 + 20 + 11 + 39 = 132 段，与 `zh` 长度一致；**无合并、无拆分、无增删段**。
注意：`paras_tool.py show` 的配对按全局 offset=6 打印，**自 zh[0] 起即错位**，本次逐段对读一律用
`_align_cd_20261126.py` 的分段表；下文所有「EN」均摘自核定配对。

## 一、自检

| 篇 | 段数（改前＝改后） | 汉字（改后） | 改动条数 | 换行符 |
|---|---|---|---|---|
| cent_d | 132 ＝ 132 | 16 487 | 12 | CRLF（133 行，与备份一致，末尾无换行） |

脚本内跑、全部通过：

- JSON 可解析；`len(zh) == len(bak) == 132`，段序未动；无空段 ✓
- 无 ASCII 直引号 `"` 与单引号 `'`；`「」`（成对）／`『』`（成对）✓；无 `⟦⟧` ✓
- 无 `。。`／`，，`／`；；`／`：：`／`、、`／`——。`，无「；——」「：——」叠加 ✓
- 无「汉字＋空格＋小写英文＋空格＋汉字」残留英文 ✓
- 段末标点齐全（`zh[55]`、`zh[124]` 为 `＊　＊　＊` 分隔行，按原样式不带标点，豁免）✓
- 元素内 `\n` 计数：改前 0、改后 0（本篇无诗行；分隔行用全角星与空格，非换行）✓
- 落盘风格：`indent=1`、CRLF、末尾无换行，与备份逐字节同制式 ✓；`ast.parse` ✓
- 与备份逐段比对：仅 `[0, 19, 22, 46, 52, 61, 62, 75, 78, 93, 102, 104]` 12 段有变化，其余 120 段逐字未动 ✓

改动分类小计：①读不通 10　②「的」字堆叠 0　③外语句法 0　④指代 1　⑤专名 0　⑥硬伤 1　⑦体例 0。

## 二、改动清单

1. **⑥** zh[0]「他为这个想法举出的若干理由，施塔尔都讲了；」
   → 「他为这个想法举出的若干理由，奥马利讲了一些；」
   理由：原文 `he gave` 的 `he` 是奥马利（上一章末他掏出笔记簿、凭记忆背诵费希纳），不是施塔尔；
   主语错人属硬伤，且使全段叙述者关系错乱。
   EN: *Some of Fechner's reasons for thinking the Earth a being superior in the scale to ourselves, he gave…*
2. **①** zh[19]「把望远镜朝东转，搜寻希腊的第一眼」
   → 「把望远镜朝东转，盼着第一眼望见希腊」
   理由：「搜寻……第一眼」动宾失配，读者会读成「搜寻希腊的那只第一眼」。
   EN: *the tourists turned their glasses eastwards, searching for a first sight of Greece.*
3. **①** zh[22]「再加上手势、面部表情和——沉默的转释，他的完整意思仍避开了精确的界定」
   → 「还要靠手势、面部表情，以及——沉默——来转释，他的完整意思仍避开了精确的界定」
   理由：「和——沉默的转释」把破折号插入语与后置定语挤成一团，主句被截断。
   EN: *interpreted too by gesture, facial expression, and--silence, his full meaning evaded precise definition.*
4. **①** zh[46]「这条伸向星辰、风与大地的那片更宽广意识的边缘」
   → 「这条向星辰、风与大地伸展出去的更宽广意识的边缘」
   理由：一句里「这条……那片」两个指示词争同一中心语，定语链断裂。
   EN: *this fringe of wider consciousness, stretching to the stars and winds and earth.*
5. **①** zh[52]「无树的峰与肩、陡然的崖壁、山顶与山脊，全都清一色地玫瑰红，活生生的」
   → 「……全都泛着精致的玫瑰红，活生生的」
   理由：「清一色」谓其一律无别，与原文 `exquisitely`（精致、各自可辨）相反；且作状语不成搭配。
   EN: *treeless peaks and shoulders, abrupt precipices, summits and ridges all exquisitely rosy and alive.*
6. **④** zh[61]「带着一种仍含不安的宽慰，他看着他那蹒跚的身影消失在楼梯下面。」
   → 「……他看着施塔尔那蹒跚的身影消失在楼梯下面。」
   理由：一句里两个「他」分指奥马利与施塔尔（`his shambling figure`），读者必错认成他自己。
   EN: *he watched his shambling figure disappear down the stairway. He was alone.*
7. **①** zh[62]「他都必须全副用心」
   → 「他都必须倾注全副心力」
   理由：「全副用心」不成词（「全副」只与精神／武装／精力类名词搭配）。
   EN: *To everything that a man does he must give his undivided attention…*
8. **①** zh[75]「仿佛她那胸上所有森林之上，长长的甜风都去低语他的名字」
   → 「仿佛她胸上所有森林之间，长长的甜风都在低语他的名字」
   理由：「胸上……之上」两个方位短语叠置，句子悬空；`across the forests` 是「穿林而过」。
   EN: *as though across all the forests on her breast the long sweet winds went whispering his name.*
9. **①** zh[78]「两岸的岸线都离得很近」
   → 「两边的岸线都离得很近」
   理由：「岸……岸线」同词重复；此处是海峡两岸，不必再点「岸」。
   EN: *The line of the shore lay close on either side.*
10. **①** zh[93]「接下来的事，他讲得激情而半带混乱。」
    → 「接下来的事，他讲得激昂而半带混乱。」
    理由：「讲得激情」以名词充补语，不成搭配（`relates with passion`）。
    EN: *What followed he relates with passion, half confused.*
11. **①** zh[102]「这桩事的一角从彼外渗了过来」
    → 「这桩事的一角从更远处渗了过来」
    理由：「彼外」是照 `from beyond` 生造，汉语不成词。
    EN: *A broken piece of the occurrence filtered through from beyond…*
12. **①** zh[104]「随一股声的风胀起，把那一片片天空、海与星辰都吸着同来」
    → 「随一股声流胀起，把整片整片的天空、海与星辰都一同吸了过来」
    理由：「一股声的风」名词夹名词、不可读；「吸着同来」语序颠倒（`sucked … with it`）。
    EN: *swelling with a draught of sound that sucked whole spaces of sky and sea and stars with it.*

## 三、未改判定（读过、读得通或不属七类，一律不动）

- **章号段不译**（`src` 的 XVII–XXII 六段）：既有体例，未补译，未增删段；offset 来源见第〇节。
- **星号分隔行** `＊　　　＊　　　＊`（zh[55]、zh[124]）：全角星与全角空格原样保留，不加句末标点。
- **题铭两段** zh[42]「独处即无知。」、zh[43]「——乔赛亚·罗伊斯。」：署名行以句号收，与 `cent_c`
  的题铭体例（署名行豁免段末标点作「——作者。」）略异但篇内自洽，不动。
- **作者节律的短句／复沓**：zh[10]「众神——！」、zh[100]「构想上庞大，距离、范围、伸展上庞大！」、
  zh[105]「在汽船引擎的脉搏与颤动之上，在海的涌动与汩汩之上」、zh[92]「但绝不是半颗心出了窍！」——
  均为原文排比／惊叹的对应，未动。
- **「卜到／卜出」**（zh[53]、zh[70]、zh[79]、zh[102]、zh[101] 等）译 `divine`：篇内自洽，
  且比「猜出」更贴神秘语域，不改（与 `cent_c` 分章用词差异，非同一专名）。
- **口语直译**：zh[121]「使整件事都对了」、zh[34]「大剂量地服用他」、zh[68]「道成肉身的折中」、
  zh[91]「那位加拿大的推销员」——读得通，保留。
- **zh[29]「他猜度会被接受的短句」**（`which he divined would be acceptable`）：略拗口但可解，
  且与全篇「卜／猜度」用词体系相合，未改。
- **zh[98]「他们那绷紧人格的敏感边缘」**：紧接下文有破折号释语，能读通，未改。
- **zh[50]「他们会为了逃跑而做出某种努力」**（`in some effort to escape`）：语序略有挪移，
  但语义未反转，属可接受范围，未改。
- **zh[72]「它只描述了一个形与轮廓的一部分」**（`describing but partially a form and outline`）：
  「部分地描述」被译成「描述了……的一部分」，义近而未反，未改。
- **zh[63]「它只描述」一段以外的诺瓦利斯引文**：长句照原文句序，属引文体例，不动。
- **专名**：施塔尔／奥马利／喀戎（Chiron）／忒诺斯岛／马塔潘角／许墨托斯山／皮利翁／
  布尔根费尔德船长——篇内各只一种写法，未发现同篇异写；`haunted` 已于上一轮归一为「闹鬼」。
- **感叹与破折号**：「——」全篇统一为双连字符形式，无半角叠加，未见需改处。