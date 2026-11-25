# POLISH_LOG — cent_h（2026-11-26）

润色对象：`work_batch_20261124/cent_h_zh.json`
源文：`work_batch_20261124/_cent_h_paras.json`（154 段，`src[0]` 为篇名「XXXVII」）
脚本：`work_batch_20261124/_polish_20261126_cent_h.py`
备份：`work_batch_20261124/cent_h_zh.json.bak_20261126`（与改前逐字一致；旧备份 `.bak_20261125` 未覆盖）

## 一、自检

| 篇 | 段数 | 汉字 | 改动数 | 换行符 |
|---|---|---|---|---|
| cent_h | 148（源 154） | 14414 | 27 条 / 21 段 | CRLF |

- `python work_batch_20261124/check_batch.py cent_h` → `checked 1, with problems 0, paras 148, han 14414`
- 脚本自检：JSON 可解析；数组长度 148 = 备份 148；无空段；无 ASCII 直引号；无 `。。／，，／、、／！！／？？`；无「汉字＋空格＋小写英文」残留；无 `⟦⟧`；`ast.parse` 通过；落盘 indent=1、CRLF 照原样。

### 对齐（offset = 6 ≠ 1，须按内容校准）

`paras_tool.py show cent_h` 打印的 `offset = 6` 直线对齐**整体错位**（它把 `zh[0]` 对到 `src[6]` 的星号行）。实际情形：

- `src[0]`「XXXVII」为篇名，不进 `_zh.json`；
- 五个章节标题 `src[23]=XXXVIII`、`src[37]=XXXIX`、`src[66]=XL`、`src[110]=XLI`、`src[133]=XLII` 未译入 `_zh.json`（共 6 段差，正好等于 offset 6）；
- 其余 148 段严格逐段对应：`zh[i] ↔ src[i + 1 + (i 之前跳过的标题数)]`。六个星号分隔段一一对齐（`zh[5]/[10]/[16]/[18]/[45]/[138]` ↔ `src[6]/[11]/[17]/[19]/[48]/[144]`），可作校准锚点。

未增删段、未补译标题、未改篇名。

## 二、改动清单（旧句 → 新句；理由；英文原文）

### ① 读不通（12 条）

1. `zh[7]`（src[8]）「她的意识曾镶触了他自己意识的边缘」→「她的意识曾触到他意识的边缘」
   「镶触」非汉语词，全篇三处一致误用（另见 3、10），读者卡在此处；三处同步改通。
   原：*her consciousness had fringed his own--had bruised it.*
2. `zh[17]`（src[18]）「这一切都是那伟大大地生命的流」→「那伟大的大地生命的流」
   缺一顿，「伟大大地」被读成「伟大／大大地」，中心语被截断。
   原：*were currents of the great Earth Life*
3. `zh[20]`（src[21]）「那时他镶触到一个更伟大存在的领域的边缘」→「那时他触及了一个更伟大存在的领域的边缘」
   同 1，动词生造，宾语又挂在长定语后面，句子失衡。
   原：*He then fringed a region of yet greater being*
4. `zh[23]`（src[28]）「他最后这样说，那是叙述将近结束时我大着胆子在这里那里提了个问题。」→「他最后这样说——那时叙述将近结束，我大着胆子东一句西一句地问。」
   原译后半是悬空的判断句（「那是……」无所指），主谓断裂。
   原：*as he said at last when I ventured a question here and there toward the end of the recital.*
5. `zh[29]`（src[34]）「站在一个认得的小村附近」→「站在他认得的一个小村附近」
   「一个认得的小村」缺施事，定语错位。
   原：*near the tumbled-down stone huts of a hamlet that he recognized*
6. `zh[73]`（src[78]）「几乎像某段凄惨的牢狱生活的细节，痛苦、困顿与争斗，是把它们全绑在一起的调子。」→「几乎像是某段凄惨牢狱生活的细节；痛苦、困顿与争斗，就是把它们全绑在一起的调子。」
   三个名词性成分并列却无谓语，成残句；补「就是」、改为分号分层。
   原：*Details of some sad prison life, it almost seemed, pain and distress and strife the note that bound them all together.*
7. `zh[98]`（src[103]）「因为它把他那激情整个儿地宣告完整了」→「因为它把他那份激情整个儿地说尽了」
   *told … all complete* 字面硬凑，「宣告完整」汉语不成话。
   原：*because it told his Passion all complete*
8. `zh[109]`（src[114]）「「再往东去了吧，我猜？」一天下午，轮船停在布尔萨外，正装上一小批额外货物——核桃木原木；那工程师这样说。」→「……正额外装上一小批核桃木原木；那工程师这样说。」
   叙述语被一个破折号插入成分劈成两截，「额外货物——核桃木原木」是同语重复。
   原：*as the steamer lay off Broussa, taking on a little extra cargo of walnut logs.*
9. `zh[134]`（src[140]）「她的意识又一次擦伤、镶触了他自己意识的边缘」→「她的意识又一次触及并擦伤了他意识的边缘」
   同 1、3；顿号连两个近义动词亦不通。
   原：*Her consciousness again had bruised and fringed his own.*
10. `zh[139]`（src[145]）「在那人的抚慰的宁静面前慢慢退去」→「在对方那抚慰的宁静面前慢慢退去」
    「那人的抚慰的宁静」两「的」叠压，「那人」在同段两个男性之间指代含混（兼④）。
    原：*Slowly O'Malley's pain and restlessness gave way before the other's soothing quiet.*
11. `zh[144]`（src[150]）「向这另一个人敞开了心，让他灵魂的闸门大大敞开」→「……，任凭灵魂的闸门大大敞开」
    「让」把敞开动作推给受话者，主体错位；*let the floodgates … swing wide* 是「任由」。
    原：*he opened his heart to this other and let the floodgates of his soul swing wide.*

### ② 「的」字定语堆叠（3 条）

12. `zh[12]`（src[13]）「令人目盲的美的局部瞬间」→「令人目盲之美的局部瞬间」
    一句开头连四个「的」；以「之」断开一处，保住「局部」与「美」两层修饰。
    原：*these partial moments of blinding beauty*
13. `zh[47]`（src[52]）「肉体奢华与浅薄机巧的、看来琐屑的活动」→「肉体奢华与浅薄机巧之种种看来琐屑的活动」
    三个「的」夹一个顿号，中心语「活动」被压没。
    原：*the paltry activities of an age of machinery, physical luxury, and superficial contrivances*
14. `zh[126]`（src[131]）「这难道不是比文明借以产生另外那些类型的、那套相对晚近才发展出来的理性方式，具有更大的精神意义与价值？」→「文明靠一套相对晚近才发展出来的理性方式产生了另外那些类型；比起这套方式，这种天性难道不具有更大的精神意义与价值？」
    原句套了四层「的」，以「比……的、那套……的……方式」作长定语，比较项与中心语分不清。
    原：*was it not of greater spiritual significance and value than the mode of comparatively recently-developed reason by which Civilization had produced these other types?*
15. `zh[137]`（src[143]）「那与大地同行时自由的、奔流般的通道的欢乐」→「那与大地同行时自由奔涌的通道之乐」
    三「的」连缀，中心语「欢乐」被压到最末。
    原：*the joy of that free, torrential passage with the Earth*

### ③ 外语句法直搬（2 条）

16. `zh[81]`（src[86]）「「死亡的打击，」回答轻轻地说出。」→「「死亡的打击，」那回答轻轻地说了出来。」
    英语被动 *was the answer, gently spoken* 硬搬成汉语被动＋无主句；改主动。
    原：*"The shock of death," was the answer, gently spoken.*
17. `zh[112]`（src[117]）「听说在山那一类里，那是个了不起的东西。」→「听说论山，那可是一样了不起的东西。」
    *in the mountain line* 逐词硬搬，汉语不这么说。
    原：*I'm told they're a wonderful thing in the mountain line.*

### ④ 代词指代不明（1 条）

18. `zh[126]`（src[131]）「可归根到底，……比起这套方式，它难道不具有更大的精神意义与价值？」→「……这种天性难道不具有……」
    同段有「他们／它（天性）／这套方式」三方，「它」离先行词过远（先有「它需要训练、指引、净化」），改用名词点明。
    原：*was it not of greater spiritual significance and value …?*（it = that deeper and more elemental nature）

### ⑥ 硬伤（词义误读，8 条）

19. `zh[47]`（src[52]）「更甚于此——一种深沉而痛切的失落之感」→「更进一层，是一种深沉而痛切的失落之感」
    *more--* 是「更甚者／更进一层」，原译读成「比这更厉害」，转折关系反了。
    原：*brought him a sense of pain that was acute and trenchant, more--a deep and poignant sense of loss.*
20. `zh[7]`（src[8]）「在那素朴之可爱的刹那」→「在那素朴之美的刹那」
    *loveliness* 在此篇一律指「美」，「可爱」在汉语里是 cute，词义走偏，且与同段下文「美」自相矛盾。
    原：*In that instant of a simple loveliness*
21. `zh[15]`（src[16]）「世人所认识的可爱，是背后那大地灵魂的一番启示？」→「世人所认识的美，……」
    同上。
    原：*Was loveliness, as men know it, a revelation of the Earth-Soul behind?*
22. `zh[15]`（src[16]）「无一例外都是她之可爱的通道」→「都是她之美的通道」
    同上，并与同段「赤裸形体之美」统一（兼⑤）。
    原：*For one and all were channels for her loveliness.*
23. `zh[19]`（src[24]）「一种眩目而至高的可爱」→「一种眩目而至上的美」
    同上。
    原：*a dazzling and supreme loveliness*
24. `zh[12]`（src[13]）「奇妙、可爱与激情」→「奇妙、美与激情」
    同上，*wonder, loveliness, and passion*。
25. `zh[70]`（src[75]）「可它外在的可爱上蒙着灰」→「可它外在的美上蒙着灰」
    同上，*dust upon its outer loveliness*。
26. `zh[137]`（src[143]）「对那具小小空置的肉身躯壳作过调查」→「对那具空置的小小肉身作过查验」
    *inquest* 是对遗体的查验，译「调查」丢掉“验尸／查验”义（上文正是施塔尔对尸体作检查）。
    原：*they held the inquest on the little empty tenement of flesh*

### ⑦ 体例（1 条）

27. `zh[103]`（src[108]）「「——又有几个愿意跟从——更少的人敢。」」→「「……又有几个愿意跟从——敢的人就更少了。」」
    说话人标签插在引语中间后，后半引语以破折号起头（原文即 *--how few …*），汉语体例上以省略号接续更顺；「更少的人敢」是倒装硬搬，改顺。
    原：*"… And even of those who hear," he shrugged his shoulders as he led him away toward the sea,--"how few will care to follow--how fewer still will dare."*

## 三、未改判定

- `zh[1]` 题铭署名行「——理查德·杰弗里斯《我心灵的故事》。」源文只有 `--RICHARD JEFFERIES`；补书名与本册题铭惯例一致（pf 各片同式），保留，不删。
- `zh[52]`「现代廉价货色式生活的噩梦」（*the nightmare of modern cheap-jack life*）：生硬但可通，改则牵动全句节奏，未改。
- `zh[108]`「肤色黝黑，眼睛野，衣衫褴褛」：*dark-skinned, wild-eyed, ragged* 的紧凑并置，属作者短句节奏，未改。
- `zh[88]`「第弗利斯」（Tiflis）：旧译，全篇仅一见，不改作「第比利斯」，以免与同册他处不一致（留待全稿统一）。
- 引语内的「『离去』『回家』『智识』」：均在「」之内，属嵌套，用『』正确，未改。
- `zh[35]`「看来，这转换的异常突兀并没有使他茫然失措。」等 *it seems* 插入语的位置：可通，未改。
- `zh[105]`「他压着气息低低补了一句」、`zh[118]`「说话的是世界上最时髦的国家」：略涩而未越「读得通」的线，未改。
- `zh[43]` 起连续短句（「他抓住了那异象飞逝的尾端。他知道自己看见过什么东西。可就在那一刻，仅此而已。」）：作者刻意的短句复沓，未合并。
- 章节标题 XXXVIII–XLII 与篇名 XXXVII：按体例不进 `_zh.json`，未补。
- 星号分隔段六处（`＊　＊　＊　＊　＊`）：照旧，未动。
- 段末标点：148 段全部以 `。！？…」` 收（题铭署名行另有「。」），无需补。