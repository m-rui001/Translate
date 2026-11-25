# 润色日志 2026-11-26 — cent_c / cent_d

篇目：`cent_c`（源章 XII–XVI，`_cent_c_paras.json` 160 段，含篇名）
　　　`cent_d`（源章 XVII–XXII，`_cent_d_paras.json` 138 段，含篇名）
脚本：`_polish_20261126_cent_cd.py`（`python _polish_20261126_cent_cd.py cent_c|cent_d`）
备份：`cent_c_zh.json.bak_20261126`、`cent_d_zh.json.bak_20261126`（此前 `*.bak_20261125` 未动）
对齐工具：另建 `_align_cd_20261126.py`（按本次核定的人工 offset 分段表导出对照）。

## 〇、对齐（offset ≠ 1，两篇都有，须写明）

`paras_tool.py show` 报 `cent_c offset=5`、`cent_d offset=6`，**都不是 1**。原因是译稿没有把
原文中独占一段的章号行译出（也未把星号分隔行外的任何东西合并），只丢了章号段：

- `cent_c`：`src[14]`「XIII」、`src[51]`「XIV」、`src[100]`「XV」、`src[110]`「XVI」被丢，
  连同篇名段 `src[0]`「XII」，共 5 段 → offset 由 1 阶跃到 2/3/4/5。阶梯点（zh 索引）：
  `13→2, 49→3, 97→4, 106→5`。其余逐段一一对应，无任何合并或拆分。
- `cent_d`：篇名/章号「XVII」「XVIII」「XIX」「XX」「XXI」「XXII」六段被丢 → offset
  1→2→3→4→5→6。阶梯点：`17→2, 42→3, 62→4, 82→5, 93→6`。
- 两篇的诗行段（`cent_c` zh[3]、zh[4]、zh[101]，`cent_d` 无诗段）与「＊　＊　＊」行段
  （`cent_d` zh[55]、zh[124]）均一一对应，段数与备份一致。
- 结论：**段数差全部来自章号段不译，属既有体例，未增删段、未改段序。**

## 一、自检

| 篇 | 段数（改前＝改后） | 汉字（改后） | 改动条数 | 换行符 |
|---|---|---|---|---|
| cent_c | 155 ＝ 155 | 15 809 | 18 | CRLF（156 行，与原文件一致） |
| cent_d | 132 ＝ 132 | 16 476 | 39 | CRLF（133 行，与原文件一致） |

两篇共同自查（脚本内跑，全部通过）：

- JSON 可解析，`len(zh) == len(bak)`，段序未动；无空段 ✓
- 无 ASCII 直引号 `"` / 单引号 `'`；「」『』成对 ✓
- 无 `。。`／`，，`／`；；`／`：：`／`、、`；已清除全部「；——」「：——」组合（cent_c 2 处、cent_d 2 处）✓
- 无「汉字＋空格＋小写英文＋空格＋汉字」残留 ✓
- 段末标点齐全（`cent_d` zh[55]、zh[124] 为 `＊　＊　＊` 分隔行，按原样式不带标点）✓
- `indent=1` + CRLF + 末尾无换行，与备份逐字节风格一致；`ast.parse` ✓

改动分类小计：①读不通 34　②的-定语堆叠 6　③外语句法／被动硬搬 5　④指代 4　⑤专名 1
　⑥硬伤 8　⑦体例 4（同一处可兼两类，按主类计一次；逐条已在脚本里标出类别）。

## 二、改动清单（cent_c）

1. ① zh[11]「这把这三人一概包括进去的手势有一种奇特的威严」
   → 「这个手势把三个人一概包括进去，有一种奇特的威严」
   理由：`这`＋`把`连排，读成两个「把」，主谓断裂。
   EN: *The gesture including the three of them was of singular authority.*
2. ① zh[12]「随之躺下的还有什么巨大而壮丽的东西」
   → 「随之躺下的，还有一种巨大而壮丽的东西」
   理由：「还有」被误读为并列连词，实为「随他躺下的还有／什么」；加逗断开。
   EN: *And something that was enormous and magnificent lay back with him.*
3. ⑦ zh[13]「便自此开始；——倘若未来的身体与未来的生命只是虚言」
   → 「便自此开始。倘若未来的身体与未来的生命只是虚言」
   理由：分号后紧跟破折号不合汉文体例；改句号，与下文「否则……；然而……」的三段式相配。
   EN: *Here begin the wonders of clairvoyance …;--pure fables, if the future body …*
4. ⑥ zh[18]「攀上了一座摆向浩大过去的钟摆」→「攀上了一个摆向浩大过去的钟摆」
   理由：量词误用（钟摆不以「座」计）。
   EN: *He had climbed upon a pendulum that swung into an immense past.*
5. ①② zh[24]「因为终于仿佛有一些更炽烈的生命的形相在那里忙碌操作」
   → 「因为到后来仿佛有一些属于更炽烈生命的形相，在那里忙碌操作」
   理由：「终于＋仿佛」相抵；「更炽烈的生命的形相」三层「的」。
   EN: *For it seemed at length that forms of some intenser life, busily operating …*
6. ① zh[29]「他整个存在都凝在这唯一的渴慕里，从它里面迸发出来——在它身后推动着」
   → 「……凝在这唯一的渴慕里，透过这喊声往外挤——在它背后推着它」
   理由：两个「它」所指不明，「在它身后推动着」缺宾语。
   EN: *his whole being, condensed in the single yearning, pressed through it--drove behind it.*
7. ① zh[30]「又是那张施塔尔的脸，最不受欢迎、最不可解地，忽然闪到他面前来阻碍、来打断」
   → 「施塔尔的脸又忽然闪到他面前来阻碍、来打断，最不受欢迎，也最不可解」
   理由：状语插在主谓之间，句子被割成三截；恢复正常语序。
   EN: *Again, most unwelcome and unexplained, the face of Stahl flashed suddenly before him to hinder and interrupt.*
8. ① zh[32]「被带过高空，出了他自己」→「被带过高空，脱离了他自身」
   理由：「出了他自己」不成话。
   EN: *borne through high space out of himself.*
9. ① zh[36]「萨提尔的奇异光辉的形相」→「萨提尔那些奇异而光辉的形相」
   理由：`strange radiant` 是两个并置形容词，被译成偏正叠加（「奇异光辉的」），中心语被压。
   EN: *strange radiant forms of gods and heroes, nymphs, fauns and satyrs.*
10. ① zh[62]「我比你也许所能了解的更站在你这一边」→「……更靠你这一边」
    理由：「更站在你这一边」不成搭配。
    EN: *I am more with you than perhaps you understand.*
11. ⑥ zh[65]「奥马利屡屡游出了自己的深度」→「奥马利屡屡游到超出自己深浅的地方」
    理由：`plunged over his depth` 是「冒进到力所不及处」，原译方向读反。
    EN: *O'Malley plunged repeatedly over his depth.*
12. ⑦ zh[111]「『天体』；——载着它们的那个『世界』的庞大」
    → 「『天体』；载着它们的那个『世界』的庞大」
    理由：分号与破折号叠加，删破折号。
    EN: *…a "heavenly body" of dead, inert matter; the bulk of the "world" …*
13. ④ zh[122]「以为到了成就的顶点——他嘲笑这个。」
    → 「以为到了成就的顶点——这种人正是他所嘲笑的。」
    理由：「这个」指代不明（指人还是指整幅景象）；且原句主语倒置难解。
    EN: *A little two-legged man … strutting on its tiny brain as the apex of attainment he ridicules.*
14. ④ zh[130]「而它日后将化作最细的尘埃落回它身上」
    → 「而那颗流星日后将化作最细的尘埃，落回她身上」
    理由：一句里两个「它」分指流星与地球，读者必错认。
    EN: *…whereon we perched and chattered, and upon which later it would fall in finest dust.*
15. ⑥ zh[131]「弯屈身体」→「弯曲身体」（错别字）。
16. ⑥ zh[135]「正如我们自己是大的一部分」→「正如我们自己也是大地的一部分」
    理由：脱「地」字，成了「大的一部分」。
    EN: *just as we are ourselves a part of the earth.*
17. ① zh[139]「——一切的、各自小小的意识。」→「——各自分离的小小意识——一切。」
    理由：原文是「……一切民族……昆虫——一切」，译稿断了语序并留下孤立的「、」。
    EN: *--the separate little consciousnesses of all the cities … insects--everything.*
18. ⑥ zh[145]「更知道与她们伟大母亲的一种更亲的关系」
    → 「更知道与他们的伟大母亲有一种更亲的关系」
    理由：「她们」指大地母亲，却写成复数女性代词，与「他们（这些人）」混。
    EN: *who know a more intimate relationship with their great Mother than the rest.*

## 三、改动清单（cent_d）

1. ① zh[20]「忙忙的汽船」→「忙碌的汽船」（「忙忙的」不成词）。
   EN: *the busy steamer.*
2. ③ zh[21]「终于正被带向它的彻底复原」→「终于被引向彻底的复原」
   理由：「正被……被」双被动且「终于＋正」相抵；被动式硬搬。
   EN: *was being led at last toward its complete recapture.*
3. ⑦ zh[23]「……是这样的：——」→「……是这样的：」（冒号后不再接破折号）。
   EN: *…was this:--*
4. ② zh[24]「类似于今日先进的心理学家现在设想为可能的那种我们自身人格的投射」
   → 「类似于今日先进的心理学家视为可能的那种人格投射」
   理由：「现在/今日」重复，四个「的」连缀，中心语「投射」被压没。
   EN: *similar to those projections of our own personality which the advanced psychologists of today now envisage as possible.*
5. ② zh[24]「再者，他那人格中可以这样进入这座由其主观构造出的天堂的那一部分，正是施塔尔所说的……」
   → 「再者，他的人格中有一部分可以这样进入这座由它主观构造出的天堂；那正是施塔尔所说的……」
   理由：五个「的」串成的长定语，主语「那一部分」直到句末才落地；拆成两小句。
   EN: *Further, that the portion of his personality which could thus enter this heaven of its own subjective construction, was that detachable portion Stahl had spoken of…*
6. ④ zh[26]「抗拒仍在他们的能力之内」→「抗拒仍在他的能力之内」
   理由：单数 `his`，译成「他们」；同段前文只有一个「他」。
   EN: *To resist was still within his power.*
7. ① zh[31]「奥马利那点占卜的本领，把那人大我的种种精神特征看出了形貌」
   → 「……把那渐渐胀大的自我所具有的精神特征看成了形貌」
   理由：「看出了形貌」搭配不当，「大我」无着落（原文 `dilating Self`）。
   EN: *O'Malley's divining faculty visualized the spiritual traits of the man's dilating Self.*
8. ③ zh[33]「而那同样的变化也在他自己身上被感觉到了——也许凭感应的地方，并不亚于凭直接的刺激。」
   → 「那同样的变化，他也在自己身上感觉到了——也许是凭感应，并不亚于凭直接的刺激。」
   理由：`made itself felt` 被硬搬成「被感觉到了」；「凭感应的地方」不成话。
   EN: *And, by reflection perhaps as much as by direct stimulation, the same change made itself felt in himself.*
9. ① zh[35]「那皮货商虽然未必是他自以为的那种意思，却实在讨人喜欢——像孩子一样招人」
   → 「那皮货商却实在讨人喜欢——虽然未必是在他自以为的那种意义上——像孩子一样招人」
   理由：「未必是他自以为的那种意思」句法悬空，`Though hardly in the sense he intended` 实为插入语。
   EN: *Though hardly in the sense he intended, the fur-merchant was entirely delightful--engaging as a child.*
10. ⑤ zh[41]「那片有灵萦绕的陆地」→「那片闹鬼的陆地」
    理由：同书 `haunted` 的 canon 是「闹鬼」（cent_c zh[21]、zh[79]、zh[102] 三处，且 cent_c
    zh[21] 与本处所指同为希腊），此处独用「有灵萦绕」，归一。
    EN: *And the ship, meanwhile, drew ever nearer to the haunted land.*
11. ① zh[48]「与动物、鸟、昆虫的生命一样，全都与自然亲密贴近，他开始把……」
    → 「他和动物、鸟、昆虫的生命一样，都与自然亲密贴近；他开始把……」
    理由：`In common with…` 被译成悬空状语，前半句无主语。
    EN: *In common with animal, bird, and insect life, all intimately close to Nature, he began to feel…*
12. ① zh[49]「他感到自己存在的『生命冲力』——柏格森的说法——上受到一次巨大的、推动的一击。」
    → 「他感到自己存在中那柏格森所称的『生命冲力』受到一次巨大而带推力的一击。」
    理由：「——柏格森的说法——上」把「上」字挤成孤悬成分，句子断裂。
    EN: *He experienced an immense, driving push upon what Bergson has called the elan vital of his being.*
13. ① zh[53]「忙忙地上岸」→「忙着上岸」（同上，不成词）。
14. ①③ zh[61]「被那些奇特而光辉的唤起之力召出——即便在最迟钝的头脑里，『希腊』也能把这些力量唤醒——他们暂时逃脱了。」
    → 「那些奇特而光辉的唤起之力——即便在最迟钝的头脑里，『希腊』也能把它们唤醒——把他们召了出去，于是他们暂时逃脱了。」
    理由：长被动式前置分词短语照搬，主语「他们」吊在末尾。
    EN: *Summoned forth by those strange and radiant evocative forces that even in the dullest minds "Greece" stirs into life, they had temporarily escaped.*
15. ① zh[62]「否则就得以他的自我来付」→「否则就得赔上他的自我」
    理由：「以……来付」不成搭配（`or his Ego` 是诺瓦利斯式的突兀省略）。
    EN: *he must give his undivided attention or his Ego.*
16. ① zh[66]「因它红柳的花而微微泛红」→「因它的红柳花而微微泛红」
    理由：一句里「红」字三见，「红柳的花」拗口。
    EN: *blushing faintly with their scarlet tamarisk blossoms.*
17. ① zh[68]「这些忙忙来去的小小『外在之物』」→「这些来去匆匆的小小『外在之物』」。
    EN: *…going to and fro so busily.*
18. ①③ zh[69]「以一种像冷热那样极少地方性的、巨大的感觉压到他身上来」
    → 「以一种像冷热那样不限于一处的、巨大的感觉压到他身上来」
    理由：`as little local as heat or cold` 被逐字硬译成「极少地方性的」。
    EN: *with a kind of massive sensation as little local as heat or cold.*
19. ① zh[69]「就是他的部分人格与其余部分的那种解脱，正是施塔尔警告过的。」
    → 「就是他的一部分人格与其余部分解脱开来——正是施塔尔警告过的那件事。」
    理由：「的那种解脱，正是……」把判断句切成两截，末句无主语。
    EN: *was that disentanglement of a part of his personality from the rest against which Stahl had warned him.*
20. ② zh[73]「海与空的诸力在那里以它们巨大而不变的双手的伸展握着他」
    → 「海与空的力量在那里以那巨大而不变的双手把他握住」
    理由：三个「的」串成「以……的……的伸展握着他」，中心语沉底。
    EN: *where the powers of sea and air held him in the stretch of their gigantic, changeless hands.*
21. ① zh[74]「而那些梦见纪念它的人」→「而那些梦想着追忆它的人」
    理由：「梦见纪念」两个动词硬叠（`dreamed of its remembrance`）。
22. ① zh[75]「近乎劝他的嘴唇再一次去够那伟大母亲的乳房」
    → 「仿佛在催他的嘴唇再一次凑向那伟大母亲的乳房」
    理由：「劝……嘴唇」主谓失配。
    EN: *urging his very lips, as it were, once more to the mighty Mother's breasts.*
23. ① zh[76]「曾经这样是他的同伴」→「曾经是他的同伴」（「曾经这样是」不成话）。
    EN: *once his comrades thus.*
24. ⑦ zh[79]「……然后俯身到他头部的高度，说话了：——」→「……说话了：」。
    EN: *then, stooping to the level of his head, he spoke:--*
25. ①⑥ zh[81]「朝那些紧贴汽船航线、镶着航程的尖峰移动」
    → 「朝那些紧贴着汽船航线的层层尖峰移动」
    理由：`fringed the steamer's course` 是「给航线镶边／紧挨着航线」，译成「镶着航程」义反。
    EN: *toward the line of peaked hills that fringed the steamer's course so close.*
26. ① zh[84]「虽然是披着力量之美」→「虽然是一种披着力量的美」
    理由：「披着力量」的是「美」，原译把「力量」变成被披之物。
    EN: *they reported beauty, though a beauty cloaked in power.*
27. ⑥ zh[89]「它带着一道火星涌上来」→「它带着一股火涌上来」
    理由：`a rush of fire` 是「一股火」，「一道火星」把量缩小成一点。
    EN: *It came with a rush of fire.*
28. ② zh[94]「而正是这点纤巧如发丝的喜悦的触碰——带着一种至高而全然单纯的清白的魔力——使……」
    → 「而正是这点如发丝般纤巧的喜悦触碰——它的魔力是一种至高而全然单纯的纯真——使……」
    理由：三个「的」连缀；「单纯的清白」语义打架，`innocence` 此处作「纯真」。
    EN: *And it was this delicate, hair-like touch of delight, magical with a supreme and utterly simple innocence…*
29. ⑥ zh[101]「穿越他们潜意识意识的诸领域」→「穿越他们阈下意识的诸领域」
    理由：「潜意识意识」同词重复，`subliminal consciousness` 是「阈下意识」。
    EN: *Through regions of their subliminal consciousness…*
30. ① zh[102]「因为在这里，对这个……爱尔兰人，来了一次尖锐而即时的启示：」
    → 「因为在这里，这个……爱尔兰人，得了一次尖锐而即时的启示：」
    理由：「对……来了一次启示」主语悬空（英语 `came the revelation` 的照搬）。
    EN: *For here, to this wild-hearted Irishman …, came the sharp and instant revelation…*
31. ① zh[102]「这桩事有一块碎处从彼方渗了过来」→「这桩事的一角从彼外渗了过来」
    理由：「一块碎处从彼方」重复「块／处／方」，且「渗」的主语被写成了「碎处」。
    EN: *A broken piece of the occurrence filtered through from beyond…*
32. ① zh[105]「那传过来的只是它主体量的一记回声」→「那传过来的只是它主体的一缕回声」
    理由：「主体量」生造，「一记回声」量词不合。
    EN: *but an echo of its main volume had come through.*
33. ① zh[107]「更深地沉进夜色，也更高处，朝北飘进……」
    → 「更深地沉进夜色，位置也更高些，朝北飘进岸线之外更远的山谷与幽壑。」
    理由：「也更高处」缺谓语。
    EN: *sunk more deeply into the night, higher up, too, floating away northwards…*
34. ④ zh[108]「因为那远方声音的美与壮丽绞出了他的心，把他放开了。」
    → 「……把他的心都绞紧了，又把它放开。」
    理由：「他」被写成了被放开的人，原文放开的是那颗心（`wrung his very heart and set it free`）。
35. ① zh[117]「那穿过空气的行程仿佛又像抽出一缕烟般从他身上抽出某一部分」
    → 「那穿过空气的行程仿佛又从他身上抽出一部分来，如一缕烟」
    理由：「仿佛」「像」重复，两个「抽出」夹一个「抽出一缕烟」。
    EN: *it was as if the passage through the air drew out a part of him again like smoke.*
36. ③ zh[118]「把他有效地撞回了自己里面」→「把他结结实实地撞回了他自己里面」
    理由：`effectually` 硬译为「有效地」（此处是「着实、干脆」义）。
    EN: *came upon him with a crash that brought him back effectually again into himself.*
37. ① zh[128]「帆布下面那个安静、年轻的轮廓，从头到尾贯穿这场漫长的哑剧，躺在后面阴影渐渐浓重的榻上。」
    → 「帆布下面那个安静的、年轻的轮廓，躺在后面阴影渐渐浓重的榻上，贯穿了这整场漫长的哑剧。」
    理由：这是名词短语列项（舱房一幕的几笔），「贯穿」插在中间把轮廓与「躺在」隔断。
    EN: *the still, young outline underneath the canvas all through the long pantomime, lying upon a couch at the back where the shadows gathered thickly.*
38. ① zh[130]「指向西北阿卡迪亚的岸线在地平线下所在的地方」
    → 「指向西北阿卡迪亚岸线隐没于地平线之下的方向」
    理由：「……在地平线下所在的地方」是 `lay below the horizon` 的逐字硬搬。
39. ② zh[130]「他抬起双臂，朝那渐渐明亮的天空做了一次巨大的欢迎的挥扫」
    → 「他把双臂大大挥开，朝那渐渐明亮的天空表示欢迎」
    理由：三个「的」堆成「一次巨大的欢迎的挥扫」，「挥扫」亦非词。
    EN: *raised his arms with a huge sweep of welcome to the brightening sky.*

## 四、未改判定（读得通、或属「不动」范围，一律不改）

- **章号段不译**（`src` 的 XII…XXII）：既有体例，未增段补译；只在汇报里写明 offset 来源。
- **星号分隔行** `＊　　　＊　　　＊`（cent_d zh[55]、zh[124]）：保留原有全角星与全角空格，不加句末标点。
- **诗行**（cent_c zh[3]、zh[4]、zh[101]）：分行与 `\n` 原样保留；zh[101] 末行 `望向我？」` 的
  引号是译者给引诗加的框，篇内一致，不动。zh[3] 首行末用全角逗号、次行用句号，与原文逗号断行
  相当，不动。
- **刻意的短句／复沓**：cent_c zh[34]「它极其奇怪地——流着。」（*It most curiously--flowed.*）、
  zh[40]「几乎——他知道自己已被拉了回来。」、cent_c zh[69]「大地是活的，是一个活的存在」、
  cent_d zh[10]「众神——！」、zh[100]「构想上庞大，距离、范围、伸展上庞大！」——均为作者
  节律，未动。
- **「卜到／卜出」**（cent_d zh[31] 等 7 处）译 `divine`：篇内自洽，且比「猜出」更贴原文的神秘
  语域，未动（cent_c 一章未用此词，属译者分章用词差异，非同一专名，不强行归一）。
- **「忙忙」以外的口语译法**：cent_d zh[121]「使整件事都对了」、zh[31]「他变大了」、zh[52]
  「清一色地玫瑰红」——口语腔与原文的直白相当，读得通，不改。
- **「Ｎ射线」**（cent_c zh[60]）：全角字母，与中文行文齐整，无半角空格问题，不动。
- **「亚美尼亚教士」「那位教士」**：`priest` 按本批准则作「教士」，已合；未改。
- **「许多萨克雷和吉卜林」**（cent_d zh[34]，原文是走音的 `"a much of T'ackeray and Keeplin"`）：
  走音梗若照搬需造谐音，属重译范畴，不动，仅记于此。
- **「有灵萦绕」以外的 `haunted`**：cent_c zh[21]、zh[79]、zh[102]「闹鬼」，cent_d zh[41]
  已归一为「闹鬼」，其余不动。
- **「辫／鞭」一类异体**：两篇均未见异体混用。