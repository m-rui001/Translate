# POLISH LOG — dn_a（2026-11-26）

篇目：`dn_a`（两篇连排，共 123 段；`src=123 / zh=123，offset = 0`，逐段一一对齐，无语段错位）
脚本：`work_batch_20261124/_polish_20261126_dn_a.py`
备份：`work_batch_20261124/dn_a_zh.json.bak_20261126`

## 自检

| 篇 | 段数 | 汉字 | 改动条数 | 涉及段 | 换行符 |
|---|---|---|---|---|---|
| dn_a | 123（改前 = 改后） | 15089 | 33 条 | 26 段 | LF（原文件即 LF，`newline=''` 读写，indent=1、`ensure_ascii=False` 照原样） |

`python work_batch_20261124/check_batch.py dn_a` → **checked 1, with problems 0, paras 123, han 15089**

自检项：JSON 可解析 ✓／长度 = 备份 123 ✓／无空段 ✓／无 ASCII 直引号 ✓／无 `。。`、`，，` 类重复标点 ✓／无「汉字＋空格＋小写英文＋空格＋汉字」残留 ✓／无 `⟦⟧` ✓／引号全用「」✓／分段星号行（[7][43][56]）格式未动 ✓

改动分类（一条可兼两类，故合计 35 > 33）：
① 读不通 17　② 「的」字堆叠 1　③ 外语句法 5　④ 指代 0　⑤ 专名 3　⑥ 硬伤 9　⑦ 体例 1

## 改动清单

| 段 | 类 | 旧句 → 新句 | 理由 | 英文原文 |
|---|---|---|---|---|
| 1 | ① | 「——不像这些年间每回追忆时，岁月都给那感觉添上一层可悲的减损。」→「——不是带着这些年间每一回追忆时岁月给它添上的那层可悲的减损。」 | 「不像＋主语从句」读成了比较，原意是「不带那种减损」，须补出谓语 | not with that tragic lessening the interval had brought to each repetition of its memory |
| 6 | ⑥ | 「可声音不济了」→「可嗓子不听使唤了」 | 「不济」指本事差，不能状声音；her voice failed 是气力接不上 | but her voice failed |
| 12 | ⑤① | 「……记起来，那是在白色小花园门那边、不许人进出的牧师宅花园里。」→「……记起来——那些日子是在那扇白色小花园门外、不许人进的教区长宅花园里过的。」 | ①rectory 与 [22]「教区长」并称，此作「牧师宅」不统一；②「，那是在……」悬空修饰 | remembered passionately each detail of the far-off courtship days in the forbidden rectory garden |
| 15 | ① | 「他此来已不再是他自己所认为的、一桩体面的尽责之举；」→「他此来已不再是为了他自己也许会认作体面尽责之举的那桩事；」 | 主语「他此来」与表语「一桩……之举」类别不合 | No longer was he bound upon what he deemed, perhaps, an act of honourable duty |
| 20 | ③ | 「他有意识时并不觉得它们」→「他并不曾自觉地意识到它们」 | Consciously 是「自觉地」，原译读成时间状语 | Consciously, he was not aware of them |
| 20 | ① | 「他心不在焉地认出了它们，可以说；并不分析追究。」→「他可以说是心不在焉地认出了它们；并不去分析、追究。」 | as it were 修饰「认出」；原译把插入语甩在分号前，句子断气 | He recognised them absentmindedly, as it were |
| 20 | ① | 「……表现为轻微的迟疑或失算，把自己泄露出来。」→「……借着在一两件无关紧要的举动上的轻微迟疑或失算，把自己泄露出来。」 | 两个谓语（表现为／泄露）并列，后者悬空 | betrayed itself by a slight hesitancy or miscalculation |
| 20 | ⑥ | 「只因短短的半个钟头」→「只差短短的半个钟头」 | by a brief half-hour 是差半小时，非「因为」 | by a brief half-hour, was just--too late |
| 21 | ① | 「也正因为这份急，他才有那些轻微的失算，或许。」→「也正因为这份急，或许，他才有那些轻微的失算。」 | possibly 为插入语，照搬句末，中文读着断句 | And, due to this hurry, possibly, were the slight miscalculations |
| 22 | ⑥ | 「还要给他添上年岁的模样」→「还要给他添上几岁年纪」 | add to the appearance of the years＝显老，原译不成话 | add to the appearance of the years he bore |
| 23 | ⑥ | 「然后一路唱着、兴冲冲地顺着弯曲的小径出发了」→「然后兴冲冲、急匆匆地顺着弯曲的小径出发了」 | gaily and impetuously 无「唱」；唱是下一句的事，此处增译且与下文重复 | set out gaily and impetuously along the winding lane |
| 26 | ⑤ | 「「往牧师宅」」→「「往教区长宅」」 | rectory 归一 | "To the Rectory." |
| 26 | ① | 「每一个细小之处都满满装着亲爱联想的货。」→「每一个细小之处都满载着亲昵的联想。」 | cargo 直搬成「货」，不成话 | each little detail brimmed with its cargo of fond association |
| 29 | ⑤ | 「看见了牧师宅的烟囱」→「看见了教区长宅的烟囱」 | rectory 归一（同 [12][26]） | the chimneys of the rectory |
| 30 | ① | 「这静、这沉寂，满在他四周。」→「这静、这沉寂，遍布他的四周。」 | 「满在……四周」缺搭配 | This stillness, silence, was all about him. |
| 31 | ⑥③ | 「气急败坏、力竭一般扑在他眼前与她的眼睛之间那道……障碍上」→「上气不接下气、力气用尽，扑在隔开他双眼与她双眼的那道……障碍上」 | ①breathless and exhausted 是喘不上气、力尽，「气急败坏」是恼怒；②「他眼前与她的眼睛之间」两截不对称 | flung himself, breathless and exhausted, against the trivial barrier that stood between his eyes and--hers |
| 33 | ① | 「他推那不肯让开的一层。」→「他推那不肯让开的表面。」 | surface 译作「一层」，量词与所指皆错 | he pushed against the unyielding surface |
| 38 | ⑥ | 「他的声音怪异地不济；里面没有力气。」→「他的声音怪异地提不起来；里面没有力气。」 | 同 [6] | His voice failed oddly |
| 41 | ① | 「……那扇白色小花园门那不肯让开的一层。」→「……那扇白色小花园门不肯让开的表面。」 | 两个「那」连排，且「一层」误 | hammered and beat against the unyielding barrier |
| 53 | ①⑦ | 「「你这样下去，一辈子也嫁不出去……，」她说，「要是你脸上老挂着那副兔子的神情。」→「「你要是脸上老挂着那副兔子的神情，一辈子也嫁不出去……，」她说，「现在到咱们家来住的那类体面年轻人……」 | 条件从句被劈到后半句并以句号收尾，成了半截话；条件前置，说话人标签体例不动 | "You'll never marry at all, child…," she said, "if you go about with that rabbit expression on your face. |
| 57 | ① | 「他们对待用人，」→「他们对待用人的方式，」 | 并列项中唯此一项无谓语无中心语 | their treatment of the servants |
| 57 | ⑥ | 「也按这一伙人的风气行事，趁着她最后一场放荡——」→「……纵情于她最后一场放荡——」 | expected over her final fling 的 over 是「在……之际」，译作「趁着」读反 | behaving as the tone of the clique expected over her final fling |
| 58 | ③ | 「他们已经进了容易说话的距离。」→「他们已经近得能说话了。」 | within easy speaking range 的 range 硬搬 | They were within easy speaking range. |
| 64 | ③ | 「「就跟她们恰恰是另一路一样确凿！」」→「「正如她们恰恰是相反的一路，同样确凿无疑！」」 | as surely as… 比较框架直搬，中文看不出「同样确凿」 | "as surely as they are just the other thing!" |
| 93 | ① | 「把他唤回那仿佛是当下的东西」→「把他唤回那仿佛是当下的境地」 | 「唤回……东西」搭配不成 | recalled him at length to what seemed the present |
| 97 | ① | 「那种除自己以外谁都瞧不起，」→「那种除自己以外谁都瞧不起的傲慢，」 | 名词短语并列缺中心语 | the contempt of all others but themselves |
| 97 | ② | 「那种被当作欢快的、没趣味的头脑的胡闹」→「那种出自没趣味头脑、却被当作欢快的胡闹」 | 三个「的」把中心语压没 | the horseplay of tasteless minds that passed for gaiety |
| 102 | ① | 「花园躺在黑白里，满得溢出来的美，被……月光穿过」→「花园躺在黑白里，美得满溢出来，被……月光穿过」 | 「满得溢出来的美」为悬空同位语，接不上后文主语链 | In black and white the garden lay, brimmed full with beauty |
| 104 | ① | 「于是失掉了度量所记事物的标准」→「于是他失掉了衡量所记事物的标准」 | so that 从句缺主语，与前句断链；standard 是「标准」而非「度量……的标准」 | so that he lost the standard of remembered things |
| 104 | ⑥ | 「跳过那些辛苦培植出来供人玩笑的花坛」→「跳过那些费尽人工修剪出来、含着嘲弄意味的花坛」 | shaped in mockery 是「以嘲弄（自然）的手法制成」，「供人玩笑」误读 | the flower-beds, so laboriously shaped in mockery |
| 106 | ⑥ | 「他们手拉手一同跑过干净的夏月。」→「……跑过干净的夏日月光。」 | moonlight 漏成「夏月」，与「六月黄昏」自相矛盾 | through the clean summer moonlight |
| 119 | ③ | 「他的眼睛把主宰放在她的眼睛上。」→「他的目光压住她的目光，俨然是主宰。」 | put mastery on 逐字搬，中文不成句 | His eyes put mastery on her own. |
| 121 | ① | 「崇拜的静穆偷上了她小小的脸」→「崇拜的静穆悄悄爬上了她小小的脸」 | 「偷上了」不成词 | the hush of worship stole upon her little face |

## 未改判定（读得通、或属作者本色，一律不动）

1. **[0] 法语题词**「Je suis la premiere au rendez-vous. Je vous attends.」保留原文，只统一引号为「」。属题词原文，译为中文即等于重译＋越体例。
2. **[8]**「他们把五年定为分离的可能的期限」——两个「的」但中心语清楚，未到堆叠，不改。
3. **[9]**「穷得只剩鞋底……那鞋底虽已换过……补了又补」——on his uppers 的双关被中文顺势铺开，虽与字面（鞋面）有出入，但全段譬喻自洽，改则伤戏。
4. **[10]**「他性格里就有这种漂亮、愚蠢、自私的执拗」——fine/stupid/selfish 三词并列，作者反讽所在，不修饰。
5. **[12]**「没有一个单一、清晰的定盘星」——「定盘星」为口语化喻，虽僻而达意，保留。
6. **[15]**「；她并没有褪色，倒是他自己决定了『我必须忘掉她』」——英文以 that 从句接在 said "No" 之后；中文改成分号并列后意思仍清楚，且更符合汉语节奏，不改。
7. **[18]**「那时她的名字、她的信、她在他心里的影像找上他时，即便不算冷淡，至少也没有热烈的回应」——「即便不算冷淡」承前省略主语「他」，读得通，不改。
8. **[22]**「他也没想到自己戴着眼镜……还要给他添上几岁年纪」——只改了这一处搭配，其余「他不想。」一类短句为作者刻意断句，不动。
9. **[25][28]**「还有一种——奇怪地——无可避免的东西」「羞怯的、试探的前行」——破折号插入语与短句节奏是 de la Mare 的语感，保留。
10. **[48]**「大多数讲理的人活着只为记得它」——直译略拗，但对应 live only to remember，改则须重铸全句，判定保留。
11. **[49]**「一想到黎明里的山谷……他的脚也会觉得孤单」——英文本身奇警（made his feet lonely），中文照应得住，保留。
12. **[57]**「夫妻不一同请。」「他觉得不自在，格格不入。」——刻意的短句列举，不动。
13. **[76]**「甚至一并忘了父亲的姓和他自己的姓」——name 译「姓」略窄，然与「古老英国世家」相合，不改。
14. **[84][86]**「「在那林的心里，我住。」」「「在林的心里——我住……」」——诗句分行、语序倒装为作者原样（In the heart of that wood dwell I），保留。
15. **[94]**「他的手势把他关于这一位要说的话都作完了」——略绕但达意，不改。
16. **[99]**「几座烟囱正好镶在基座边上」——edged the pedestal precisely 的取象，改成「描出基座的边」须重铸，保留。
17. **[112]**「嘘！呼！嗡！」——Whisht! Whew! Whir! 拟声，保留。
18. **[118]**「在它的奇怪里梦想着天真与纯洁」——dreamed innocence and purity 的抽象主语句虽属③范畴，但此处是作者抒情的高点，改写会削掉其恍惚感，判定保留。
19. 全篇「他／她」在同一段内指代清楚，无④类问题；「希伯／伊丽莎白—埃尔斯佩思／赫迈厄妮夫人」三名前后一致，未动。
20. 分段星号行 [7][43][56]（`＊　＊　＊　＊　＊`）与原文 `* * * * *` 对应，全角星号＋全角空格体例统一，不动。