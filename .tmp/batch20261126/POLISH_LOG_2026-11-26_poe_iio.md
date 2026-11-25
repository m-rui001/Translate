# 润色日志 2026-11-26：爱伦·坡三篇（imp / island / owl）

作业依据：`POLISH_BRIEF_2026-11-25.md` + `SUBTASK_README_2026-11-26.md`（offset=1）。
脚本：`work_batch_20261124/_polish_20261126_poe_iio.py`
备份：`imp_zh.json.bak_20261126`、`island_zh.json.bak_20261126`、`owl_zh.json.bak_20261126`（原有 `.bak_20261125` 未动）

对读方式：`PYTHONIOENCODING=utf-8 python work_batch_20261124/paras_tool.py show <key>` 逐段对读；三篇逐篇改完即落盘。

## 一、自检

| 篇 | 段数（改前=改后） | 汉字 | 改动数 | 换行符 / indent | 卷尾换行 |
|---|---|---|---|---|---|
| imp（The Imp of the Perverse） | 16 = 16 | 3833 | 4 | LF，indent=1 | 有 |
| island（The Island of the Fay） | 14 = 14 | 2869 | 9 | CRLF，indent=1 | 无 |
| owl（An Occurrence at Owl Creek Bridge） | 39 = 39 | 5364 | 6 | LF，indent=0 | 无 |

脚本自检：JSON 可解析；段数与备份一致；无空段；无 ASCII 直引号；无 `。。`／`，，` 重复标点；无「汉字＋空格＋小写英文＋空格＋汉字」残留；`⟦⟧` 未动；落盘前另做「原样回写 == 原字节」的格式比对（indent / CRLF / 卷尾换行均未变）。

`check_batch.py imp island owl` 结果：

```
[!!] owl
      owl[7]: NO-END-PUNCT '二'
      owl[18]: NO-END-PUNCT '三'
checked 3, with problems 1, paras 69, han 12066
```

`owl[7]`「二」、`owl[18]`「三」是分节序号（原文 `II` / `III`），不是正文句子，按体例不加句末标点，属预期告警，非缺陷。island/imp 全清。

## 二、对读提示（段序）

- imp、island：`src[0]` 是篇名，`zh[i] ↔ src[i+1]`，与工具一致。
- **owl 例外**：`_owl_paras.json` 里 `src[0]` 就是开篇段（“A man stood upon a railroad bridge…”），**不含篇名**，末尾 `src[39]` 是 Gutenberg 尾注 “End of Project Gutenberg's…”，译稿无对应段。因此 offset 虽显示 1，实际是 `zh[i] ↔ src[i]` 一一对应；照工具的 `zh[i] ↔ src[i+1]` 读会整体错开一段（开篇段与尾行错配）。已按 `zh[i] ↔ src[i]` 校验全文，未增删段。

## 三、改动清单（19 条：①2 ③3 ⑤1 ⑥11 ⑦2）

### imp（4 条）

1. **[7] ⑥ 词义误用**
   - 旧：为了给你**指派**一点东西——至少稍微像个缘由的东西
   - 新：为了给你**举出**一点东西——至少稍微像个缘由的东西
   - 理由：「指派」只用于任务或人员（指派工作／指派代表），不能「指派一点东西」；原文 assign to you something 是「举出／提出」。
   - 原文：that I may assign to you something that shall have at least the faint aspect of a cause for my wearing these fetters

2. **[12] ① 读不通**
   - 旧：我十分、**太十分**明白
   - 新：我十分明白，**太明白了**
   - 理由：「太十分」不成词，副词叠加造成语法断裂；原文是 well, too well understood 的复沓，中文用「明白，太明白了」承接复沓。
   - 原文：for, alas! I well, too well understood that to think, in my situation, was to be lost.

3. **[12] ③ 外语句法直搬**
   - 旧：这时我感到了我**命运的完成**。
   - 新：这时我感到**自己的大限已到**。
   - 理由：consummation of my fate 照字面搬成「命运的完成」，中文不成话；实指命运走到终点、死期已至。
   - 原文：I felt then the consummation of my fate.

4. **[13] ① 读不通**
   - 旧：却带着**显著的加重**和炽热的急促
   - 新：却带着**明显的加重语气**和炽热的急促
   - 理由：「加重」单用作名词悬空（加重什么？）；marked emphasis 是「加重语气」。
   - 原文：but with marked emphasis and passionate hurry

### island（9 条）

5. **[0] ⑦ 体例（段末标点）**
   - 旧：……——塞尔维乌斯
   - 新：……——塞尔维乌斯**。**
   - 理由：题词段末缺句末标点；本批体例（purloined、eleonora 的题词）署名后带句号。
   - 原文：Nullus enim locus sine genio est.--Servius.

6. **[1] ⑥ 增义（加了原文没有的形容）**
   - 旧：仿佛存心讥讽它**那轻快戏谑的**精神
   - 新：仿佛存心讥讽它**本身的**精神
   - 理由：原文只说「仿佛在讥讽这个书名的 spirit（本意）」，「轻快戏谑」是译者添的形容，属增义。
   - 原文：which in all our translations, we have insisted upon calling "Moral Tales," as if in mockery of their spirit

7. **[1] ③ 逻辑读反**
   - 旧：**而它与其他才能所共有的，仅仅是**它会产生一些可以在独处中充分享受的效果。
   - 新：它产生一些可以在独处中充分享受的效果，**这一点也不过与其他才能相同。**
   - 理由：And it is only in common with other talents that it produces effects… 被搬成「与其他才能所共有的仅仅是……」，把「也不过相同」误读成「只有这一点」，与原意相反。
   - 原文：And it is only in common with other talents that it produces effects which may be fully enjoyed in solitude.

8. **[2] ⑦ 语体（口语填充词）**
   - 旧：星辰运行的**那些个**周期
   - 新：星辰运行**所循的那些**周期
   - 理由：「那些个」是口语填充词，与全篇庄重的论说体不合；改后保留原文的指示语气。
   - 原文：The cycles in which the stars move

9. **[2] ③ 外语句法直搬**
   - 旧：这并不**构成反对体积为上帝所关注的一个理由**
   - 新：这并不**足以反驳体积乃是上帝所看重之物**
   - 理由：argument against X being Y 的介词串照搬成「反对……为……的理由」，中文读不通；改为动词句。
   - 原文：Nor is it any argument against bulk being an object with God, that space itself is infinite

10. **[2] ⑤ 术语**
    - 旧：即**神体**旋转
    - 新：即**神格**旋转
    - 理由：Godhead 是「神格／神性本体」，不是「神体」（后者易读作神像、神的身躯）；基督教语境取通行译法。
    - 原文：all revolving around one far-distant centre which is the God-head

11. **[5] ⑦ 冗余**
    - 旧：随即**立刻**看不见了
    - 新：**于是**立刻看不见了
    - 理由：「随即」「立刻」同义叠用；原文只有一个 immediately。
    - 原文：which turned sharply in its course, and was thus immediately lost to sight

12. **[6] ⑥ 词义误读**
    - 旧：静卧在流水的**心口上**
    - 新：静卧在流水的**怀抱里**
    - 理由：bosom 在此是「怀抱、胸腹」，译作「心口」把位置读错，且与「静卧」不搭。
    - 原文：reposed upon the bosom of the stream

13. **[13] ③ 直译不成词**
    - 旧：少了那**弹性的**欢欣
    - 新：少了那**轻快的**欢欣
    - 理由：elastic joy 直搬「弹性的欢欣」不成词；elastic 在此是「轻快、有弹跳感」。
    - 原文：there was more of care and uncertainty and less of elastic joy

### owl（6 条）

14. **[3] ⑥ 生造搭配**
    - 旧：一片漂来荡去的浮木**引住了**他的注意
    - 新：一片漂来荡去的浮木**吸引了**他的注意
    - 理由：「引住」不是词（只有「引住目光」勉强可说），此处应作「吸引」。
    - 原文：A piece of dancing driftwood caught his attention

15. **[8] ⑥ 词义误读**
    - 旧：**天生是个原始的**分离派
    - 新：**天生就是个**分离派
    - 理由：original secessionist 的 original 是「从一开始、骨子里的」，不是「原始的」（野蛮、未开化）。
    - 原文：he was naturally an original secessionist and ardently devoted to the Southern cause

16. **[24] ⑥ 词义误读 / 抽象名词误搬**
    - 旧：**预先给出、又强行带来一片静默**
    - 新：**预示凶兆、又强使兵士们安静下来**
    - 理由：presaging 是「预示（凶兆）」，不是「预先给出」；tranquility in the men 是兵士心里的镇定，不是场面上的「静默」。
    - 原文：with what an even, calm intonation, presaging, and enforcing tranquility in the men

17. **[28] ① 悬空**
    - 旧：这个**被猎的**人从肩上回头看着这一切
    - 新：这个**被追猎的**人从肩上回头看着这一切
    - 理由：「被猎的人」缺及物对象、读来悬空；the hunted man 是「被追猎的人」。
    - 原文：The hunted man saw all this over his shoulder

18. **[34] ① 生造搭配**
    - 旧：靠着**太阳转圆**来定方向
    - 新：靠着**太阳的运转**来定方向
    - 理由：「太阳转圆」是生造搭配；the rounding sun 指太阳的运行（绕行一周）。
    - 原文：laying his course by the rounding sun

19. **[34] ⑥ 错别字**
    - 旧：他先前不知道**自已**住在这样荒僻的地方
    - 新：他先前不知道**自己**住在这样荒僻的地方
    - 理由：「自已」误，应为「自己」。
    - 原文：He had not known that he lived in so wild a region.

## 四、未改判定（读得通或属作者刻意，一律不动）

1. **imp[0][2][3]「根柢」**（×3：根柢的、根柢性）——「根柢」是「根底」的古写，全篇三处一致，配合坡的说理腔，不算异体混用，保留。
2. **imp[3]「它并不比它的独特更难索解」**——It is not more incomprehensible than distinctive 的比较结构保留了原文的对举，中文可解，仅记不改。
3. **imp[0] 长句与原文长句一一对应**（分号、破折号串），未拆句：拆了反而丢坡的推演节奏。
4. **imp[9][10]「我是安稳的」**——两处同译 I am safe，前后自洽，未改（改成「安全的」会与下段「只要我不蠢到去当众招供」的口吻脱节）。
5. **imp 全篇「「」」引号**与 owl/island 一致，未换制。
6. **island[9]「光彩灼灼的花园美色的后宫」**——all one radiant harem of garden beauties 的奇喻原文如此，虽略拗，删改即损其奇，保留。
7. **island[10]「虽然芸香和迷迭香攀满它们的上面和四周」**——although 从句后置，原文亦后置，且中文读得通，不动。
8. **island[12]「哀伤便扭曲了它」**——it 指前句刚出的「姿态」，一段内无第二个候选指代，不算④，保留。
9. **island[7][8] 诗行**（“岸与影在那里交融——／仿佛双双悬在半空”）——分行与 `\n`／破折号原样保留。
10. **owl 篇 「托枪」「不稳的立足处」等引号内的名目**——体例与原文引号对应，保留；`owl[25]` 号令段「全连！……立正！……」的「……」亦照原文的点列保留。
11. **owl[7]「二」、owl[18]「三」**——分节序号，不加句末标点（`check_batch.py` 的 NO-END-PUNCT 属预期告警）。
12. **owl 无「篇名段」**——`src[0]` 即开篇正文，译稿不缺段，未补篇名（README：篇名不进 `_zh.json`）。
13. owl 通篇「枭河桥」写法一致，人名「佩顿·法夸尔」一致，未动（⑤ 无少数派）。