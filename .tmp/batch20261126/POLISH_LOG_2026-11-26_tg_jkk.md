# 润色日志 —— tg_jest / tg_kai / tg_king（2026-11-26）

依据：`POLISH_BRIEF_2026-11-25.md` + `work_batch_20261124/SUBTASK_README_2026-11-26.md`
脚本：`work_batch_20261124/_polish_20261126_tg_jkk.py`（定位唯一子串 → 断言命中 → 替换；结尾 `ast.parse` 自查）
备份：`tg_jest_zh.json.bak_20261126`、`tg_kai_zh.json.bak_20261126`、`tg_king_zh.json.bak_20261126`

## 对齐说明

三篇的 `_paras.json` **不含篇名元素**，`src[0]` 即是正文首段，故 `offset = 0`，
`zh[i] ↔ src[i]`，逐段一一对应，无错位、无分段差异。段数 2 / 51 / 23，改前 == 改后。

## 自检

| 篇 | 段数 | 汉字 | 改动数 | 换行符 | JSON indent |
|---|---|---|---|---|---|
| tg_jest | 2 (2) | 391 | 2 | LF | 1 |
| tg_kai | 51 (51) | 2364 | 10 | LF | 0 |
| tg_king | 23 (23) | 922 | 2 | CRLF | 1 |

- 段数不变 ✓ 无空段 ✓ 引号成对（「」）✓ 无 ASCII 直引号 ✓ 无重复标点 ✓ 无 `⟦⟧` ✓
- `python work_batch_20261124/check_batch.py tg_jest tg_kai tg_king` →
  `checked 3, with problems 0, paras 76, han 3677`
- 合计改动 **14 条**：①读不通 7 ②的字堆叠 1（与①合并计）③外语句法 1 ④指代 1 ⑤专名 0 ⑥硬伤 3 ⑦体例 0

## 改动清单

### tg_jest

**[0] ⑥ 否定反转＋②的字堆叠**
旧：`放进对别家君王所不贪的疆土的贪欲`
新：`放进对疆土的贪欲，比别家君王更甚`
原文：*lust for territories beyond the lust of other kings*
理由：`beyond the lust of other kings` 是「超出别家君王所贪求」，旧译「所不贪」把比较读成了否定；顺手解掉三层「的」串成的长定语。

**[1] ④ 指代不明**
旧：`他们的怒气渐渐消散，把眼睛转开了`
新：`他们的怒气渐渐消散，诸神把眼睛转开了`
原文：*Their anger died away and They averted Their eyes.*
理由：`They` 是诸神；旧译紧接「怒气」，读者会把「把眼睛转开」挂到君王魂灵身上。

### tg_kai

**[3] ① 读不通**
旧：`于是各级魔法师都聚到伊劳恩来，直到第七级，那些曾在「独居的哈纳扎」朝上施过咒的；`
新：`于是各级魔法师——直到第七级——都聚到伊劳恩来，他们都是曾在「独居的哈纳扎」朝上施过咒的；`
原文：*the wise men of all the degrees of magic, even to the seventh, who had made spells before Khanazar the Lone*
理由：`even to the seventh` 是插说，旧译顺排成「直到第七级，那些……的」，插说悬空、后半句无谓语。

**[19] ⑥ 词义**
旧：`派出骑手去告诫平原上的居民`
新：`派出骑手去告知平原上的居民`
原文：*sent out horsemen to warn the dwellers of the plains*
理由：此处 warn 只是「预先通报」，非训诫。

**[21] ① 读不通（关系从句倒装致主谓反）**
旧：`哈纳扎王和他跟随西拉恩的两支军队前行`
新：`哈纳扎王和他那两支跟随西拉恩的军队一路前行`
原文：*went Khanazar the King, and his two armies who followed Syrahn*
理由：旧译读成「他跟随西拉恩的军队」，跟随的方向反了。

**[21] ⑥ 词义**
旧：`张起紫底金边的帐篷`
新：`张起紫色镶金边的帐篷`
原文：*the purple tent with golden border*
理由：`with golden border` 是镶金边；「紫底」另造了一层原文没有的意思。

**[23] ① 读不通**
旧：`「那边看我的礼物。`
新：`「看那边，那是我的礼物。`
原文：*"Yonder behold my gifts."*
理由：`yonder` 是指示方位，旧译「那边看」动词悬空。

**[31] ① 读不通（定语倒挂成句末悬空成分）**
旧：`还我一粒粘在那个时辰上的尘土，就在你洞中那一堆里的。`
新：`还我一粒粘在那个时辰上的尘土——那尘土就在你洞中那一堆里。`
原文：*one grain of dust that clings to that hour in the heap that lies within thy cave*
理由：第二个定语从句被搬到句末成了「……的。」残句，缺主谓。

**[39] ① 读不通＋②的字堆叠**
旧：`琴弦上像沾着尘土似的，粘着几个从被遗忘的时辰里来的秒，和过去的日子里的一些小事。`
新：`琴弦上像沾了尘土，粘着几个零碎的秒——那是从被遗忘的时辰里来的——还有些过去日子里的小事。`
原文：*to its strings have clung like dust some seconds out of the forgotten hours and little happenings of the days that were*
理由：「从被遗忘的时辰里来的秒」四个「的」串死，且「的秒」不成词。

**[40] ① 读不通（语序颠倒）**
旧：`琴师见哈纳扎看他并不恼怒，`
新：`琴师见哈纳扎并不恼怒地看着他，`
原文：*when the harper saw that Khanazar looked not angrily upon him*
理由：旧译词序把「看他」与「不恼怒」并置，读成「看他、并不恼怒」两个谓语。

**[47] ① 读不通**
旧：`你就去守着我的大明天；`
新：`你就去守着我的伟大的明天；`
原文：*thou shalt stand sentinel over my great to-morrow*
理由：「大明天」与「明朝」同形，易误读；改「伟大的明天」。

**[49] ① 读不通（与前段口径统一）**
旧：`「我愿守着你的大明天；`
新：`「我愿守着你的伟大的明天；`
原文：*I will stand sentinel over thy great to-morrow*
理由：同上，两处对白须一致。

### tg_king

**[1] ⑥ 词义**
旧：`又把云披在身上，摆出最神异的姿态`
新：`又把云披在身上，摆出他们最神圣的气度`
原文：*put upon Them Their divinest air*
理由：`divinest air` 是「最神圣的气度」；「神异」偏「灵异」，「姿态」偏体态，皆失。

**[6] ③ 被动式硬搬**
旧：`于是传令官被派往鲁纳扎各城和附近一切土地`
新：`于是国王派传令官前往鲁纳扎各城和附近一切土地`
原文：*And heralds were sent abroad through the cities of Runazar and of all the lands near by*
理由：英语被动无施事，中文「被派往」主语虚悬；按上下文补出施事「国王」。

## 未改判定（读得通但可议，一律不动）

- tg_jest[0]「把那魂灵送进人的田野」——*the fields of men* 的直译，邓萨尼惯用意象，改「人间」反而丢象。
- tg_jest[1]「抛掉了自己的身体」——*cast his body away* 即投海弃身，语气合。
- tg_jest 全篇「较古的诸神」——*the Older gods* 的既定译法，篇内一致。
- tg_kai[0]「从南方一座远方的城堡」——两个「远」是原文 *far castle to the south* 的重复，未到病句。
- tg_kai[9]「最智慧的一位」——略生，但合 *the wisest of them all*，且下文「第七级」已有解释，不重译。
- tg_kai[14]「你是一个人。」——*Thou art a man.* 的短促判断句，属作者刻意短句，保留。
- tg_kai[23]「那……的昨天，那……的昨天，那……的昨天」——复沓，是原文排比，非「的」字病。
- tg_kai[25]「在那积满尘土的被遗忘的日子的堆里」——两层「的」，节奏尚可，未达三层红线。
- tg_kai[44]「只留下一个，点着一支蜡烛」——*save one that stayed and kept one taper burning*，可通。
- tg_king[16]「就不再是一件存在过或曾经存在过的东西了」——*no longer a thing that was or had ever been*，绕而准，属原文的绕。
- 专名：哈纳扎／独居的哈纳扎／阿维隆／伊劳恩／阿格多拉／西拉恩／齐曼霍／鲁纳扎／阿尔塔扎／佩加纳／蒙格／凯——三篇内写法统一，未见异写，⑤ 类 0 条。
- 引号：三篇一律「」，说话人标签体例照旧（「……」他说，「……」），⑦ 类 0 条。