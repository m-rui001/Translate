# 润色日志 — bm_b（2026-11-26）

- 译稿：`work_batch_20261124/bm_b_zh.json`　原文：`work_batch_20261124/_bm_b_paras.json`
- 备份：`bm_b_zh.json.bak_20261126`（`.bak_20261125` 未动）
- 脚本：`_polish_20261126_bm_b.py`（定位唯一子串→替换→断言；结尾 `ast.parse` 自查）
- 对齐：`paras_tool.py show bm_b` 报 `src=184 zh=184 offset=0` —— 本册源文件 `[0]` 即正文首段（无篇名行），
  故 `zh[i] ↔ src[i]`（不是 README 默认的 `src[i+1]`）。逐段核对 184 对，无错位、无跨段错配。

## 一、自检

| 篇 | 段数（改前/改后） | 汉字（改前→改后） | 改动数 | 换行符 |
|---|---|---|---|---|
| bm_b | 184 / 184 | 13730 → 13742 | 16 | LF（`indent=1`，末尾单换行，原样写回） |

脚本内断言全部通过：

- JSON 可解析；数组长度 184 == 备份 184；段序未动；无空段 ✓
- 无 ASCII 直引号 `"` `'` ✓　无 `。。／，，／、、／；；／！！／？？` ✓
- 无「汉字＋空格＋小写英文＋空格＋汉字」残留英文 ✓　无 `⟦⟧` ✓
- `「」`／`『』` 全篇成对（含本次 2 处标签调整）✓
- 段末标点：仅 19、39、175、183 段以「：」收，为引出下段引语的常规体例，非缺标点 ✓

## 二、改动清单（16 条）

类别统计：①读不通 4　②的字堆叠 1　③外语句法 3　④指代不明 1　⑤专名 0　⑥硬伤 5　⑦体例 2

### ① 读不通（4）

1. **[76]** 旧：「他只盖了一条床单，盖着那高大、温暖、柔韧的身体。」
   新：「他只拿一条床单盖住那高大、温暖、柔韧的身体。」
   理由：一句里两个「盖」，后半句谓语重复且悬空。
   原文：*he covered his big, warm, lithe body with a single sheet only.*
2. **[152]** 旧：「根本不可能睡过。」→ 新：「根本不可能睡过觉。」
   理由：「睡过」缺宾语，孤零零像口语省略。
   原文：*He was active all through the darkness and cannot have slept at all.*
3. **[161]** 旧：「可在那种时候，这样一些纸片藏在箱底，样子又怪，而且……」
   新：「可这样一些纸片，样子又怪，又偏在那种时候藏在箱底，而且……」
   理由：时间状语顶了话题位，句子读来断裂；按「转折＋评断＋时间」重排。
   原文：*but they were queer-looking papers to have at such a time, hidden away, too, at the bottom of the trunk*
4. **[5]** 旧：「必定有价值，甚至可能具有启发，直至令人恍然。」
   新：「必定有价值，甚至可能极有启发，乃至近于启示。」
   理由：「具有启发」缺宾语，「直至令人恍然」把 *to the point of revelation* 译死了。
   原文：*must be of value, and might be even illuminating to the point of revelation.*

### ②「的」字定语堆叠（1）

5. **[24]** 旧：「仿佛要追寻这突然新生的、明亮、迅捷、高效——几乎像是某种以一贯计划与体系建造起来的巨大力量——的意识；」
   新：「仿佛要追寻这突然生出的一种意识：明亮、迅捷、高效，几乎像是某种以一贯计划与体系建造起来的巨大力量；」
   理由：中心语「意识」被破折号插语推到句末，读者须回读；中心语提前，破折号改冒号。
   原文：*to trace this sudden new consciousness of bright, quick, rapid competence--almost as of some immense power building with consistent scheme and system*

### ③ 外语句法直搬（3）

6. **[36]** 旧：「另一个则是那台死机器非个人的、准确的胜任。」
   新：「另一个则是那台死机器非个人的、精准的效能。」
   理由：*competence* 名词直搬成「胜任」不成话。
   原文：*the impersonal, accurate, competence of the dead machinery.*
7. **[52]** 旧：「大概是父母，但被梅森刺激、任由其不受约束地生长。」
   新：「大概是父母，不过梅森又加以刺激，任其不受约束地生长。」
   理由：被动式硬搬使一句里主语两变（被刺激者 / 任由者）。
   原文：*the parents probably, but stimulated and allowed unchecked growth by Mason.*
8. **[122]** 旧：「菲利里敏捷地表示赞赏。」→ 新：「菲利里当即表示赞赏。」
   理由：*with quick appreciation* 的 quick 是「立刻」，非「敏捷地」。
   原文：*said Fillery, with quick appreciation.*

### ④ 代词指代不明（1）

9. **[161]** 旧：「这更增加了那官员的兴趣，他告诉那人，那是星象和天气图。」
   新：「这更增加了那官员的兴趣，莱斯特便说，那是星象和天气图。」
   理由：前句主语已是「那官员」，此「他」实指莱斯特，一名两人易混。
   原文：*LeVallon, whose sudden excitement increased the official's interest, told him that they were star-and-weather maps.*

### ⑥ 硬伤（5）

10. **[3]** 旧：「他还需要女人的一双巧手。」→ 新：「他还需要女人的一份体贴。」
    理由：*a woman's touch*＝女人的细腻体贴，非「一双巧手」（词义误读）。
    原文：*He'll need a woman's touch as well.*
11. **[17]** 旧：「梅森的水彩速写」→ 新：「梅森的水彩写生」
    理由：*water-colour sketch*＝水彩写生／画稿；「速写」是另一画种，与水彩不搭。
    原文：*Mason's water-colour sketch had caught something, at least, of their innocence and question*
12. **[50]** 旧：「他现在比我们三天前出发时还不累」
    新：「他现在反倒比三天前我们出发时还不觉得累」
    理由：「比……还不累」否定套比较读不顺，且易读反。
    原文：*He's less tired now than when we started three days ago*
13. **[80]** 旧：「划下严厉的界限」→ 新：「划下严格的界限」
    理由：*drastic limits* 是界限的严格，不是态度的严厉。
    原文：*To the powers of the subconscious self he set drastic limits*
14. **[115]** 旧：「我一点也不觉得挖苦。」→ 新：「我一点也不觉得自己在挖苦。」
    理由：*I feel far from cynical*＝我并不觉得自己在挖苦（回应上句「别挖苦，保罗」）；原译成了「不觉得被挖苦」。
    原文：*"I feel far from cynical."*

### ⑦ 体例（2）

15. **[179]** 旧：「……他开口说：『我父亲也有，』他带着钦佩说，『一架大望远镜。……』」
    新：「……他开口说：『我父亲也有，』」他带着钦佩地说，「『一架大望远镜。……』」
    理由：说话人标签裹在引号内；按本篇 1、7 段既定体例改为「收引号—标签—开引号」。
    原文：*He spoke: 'My father, too,' he said with admiration, 'had a big telescope. Monsieur is an astronomer.'*
16. **[180]** 旧：「『是最伟大的之一，』我赶紧补了一句；『这些图对法国有无穷的价值。』」
    新：「『是最伟大的之一，』」我赶紧补了一句，「『这些图对法国有无穷的价值。』」
    理由：同上，说话人标签（我赶紧补了一句）不应裹在引号内。
    原文：*'One of the greatest,' I added quickly; 'these charts are of infinite value to France.'*

## 三、未改判定

- **[20]**「他把那个『菲』音拖得相当长」：原文 *making the "F" sound rather long*。以「菲」代 F 音可接受，且与 75 段「菲利里」的念法呼应，保留。
- **[23]**「力量使用不当，使他连那几件轻包裹都拿不了」：读得通，只是不漂亮，不动。
- **[35]**「这几句话用那安静、低沉的声音说出来……，年长的那位便朝德文汉姆那边走去」：主语切换属汉语顺承（话在耳中响，人已走开），不是悬空修饰语，保留。
- **[37]**「他仿佛经历了一次精神上辉煌的增强」：*a brilliant intensification of spirit* 直译略硬，但句子读通，且合本篇临床笔记的抽象腔，保留。
- **[95]**「是一个正常人的优秀标本」：*a fine specimen*，出诸精神科医生之口，「标本」是刻意语域，保留。
- **[7]**「乔治爵士新近受了封」：受封为现成词，读得通，保留。
- **[122]**「可那另一位呢——？」：破折号表话被截断，属作者体例，保留。
- **[147]**「『你不是菲利里』，或者『带我去见菲利里。我需要他。』」：引号外逗号与本篇其余各段一致，不改。
- **[150]**「『梅森·菲利里，梅森·菲利里，』他会这么说」：引号里的是被引述者的习惯描述，不是外层说话人的标签，与 179/180 性质不同，保留。
- **短句问答段（41–67 多段，如「癔症？」「毫无迹象。」「健康？」）**：作者刻意的电报式短句，一律不动。
- **[19][39][175][183]** 段末冒号：引出下段引语，合规，不改。
- **专名核对（⑤ 无改动）**：菲利里（Fillery，全篇 30+ 处，与用户定案 canon 一致）／德文汉姆（Paul）／莱斯特（LeVallon）／
  娜扬＝伊莱达·基尔科夫（Nayan＝Iraida）／格里森夫人（安吉拉）／乔治爵士／梅森／罗宾斯护士／希思科特／
  卡赫季／汝拉／纳沙泰尔／伯尔尼／查令十字／里昂车站／「N. H.」（原文形保留）；篇内自洽，未做归并。
- 数字：一九一四年、九月二十二日、一千英尺、一英里、每三十人——全篇汉字数字，前后无空格，符合体例。