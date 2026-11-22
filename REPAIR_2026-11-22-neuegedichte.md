# 《新诗集》（neuegedichte）修订报告（2026-11-22）

里尔克《新诗集》，德语原文 18 章 / 74 首，中文 18,462 字。
本轮把报告里的两条意见逐句回原文核验，改动分三处：**组装器（`build_pub.py` + `build_all.py`）、
译稿（`out/*/final.txt`）、新增数据文件 `work_pub/neuegedichte/verse_roles.json`**。

验收（对 `out/` 实跑）：

| 检查 | 结果 |
| --- | --- |
| `python -X utf8 pipeline_build/build_pub.py neuegedichte` | `18 ch 18,462 汉字 toc=20 err=0` |
| `verify_epub.py` | **70 epub，0 errors**（含本书 `toc=20/ncx=20`，版权页 1 段） |
| `typo_check.py` / `clean_check.py` | 本书**未上榜**（两个脚本共报 5 + 3 处，全部为其它书此前已记录的既有项） |
| 回归：用改后的 `build_pub` 试建同批 7 本（`stundenbuch`/`jedermann`/`torundtod`/`mondaytuesday`/`betrachtung`/`urteil`/`verwandlung`） | 7 本全 0 err，**全部 XHTML/OPF/NCX 与 shipped EPUB 逐字节相同**（只有 `style.css` 多两行未用的规则） |

**本轮改动的文件**

| 文件 | 性质 |
| --- | --- |
| `pipeline_build/build_pub.py` | 组装器：`verse_lines` 括号保护、`GROUP_NUM`、`verse_roles`/`verse_block`、`carry_tail`、`collect` 返回 `types`（仅 verse 分支） |
| `pipeline_build/build_all.py` | `VERSE_KINDS` + `p.verse-title` / `p.verse-sub` 两条 CSS（`p.verse` 未动） |
| `work_pub/neuegedichte/verse_roles.json` | 新增：按章列出的中文诗题 75 条 / 地名行 15 条 |
| `work_pub/neuegedichte/out/{c001,c009,c011,c012,c013/c00,c013/c01,c015}/…/final.txt` | 15 条逐句重写 + 删书名页五行 |
| `out/新诗集（坟头草译）.epub` | 重建 |
| `MEMORY.md` | 追加本轮条目 |
| `scratch/_bak/neuegedichte_pre_20261122/` | 改前成品留档 |

---

## 一、标题粘连：根因与修法

### 1.1 核实结果：报告中「每一首诗的标题都焊在正文第一句上」——**部分成立，但根因不是译文**

先说事实：

1. **`src` 里没有 `type=head` 的诗题。** 17 个 `head` 块全是源文的组序号 `I / II / III`
   （`titles_pub.py` 已把它们编成「第N首」，见 `MEMORY.md`）。真正的诗题在 `src` 里是
   **全大写的普通 `p` 块**：`DER PANTHER`、`IN EINEM FREMDEN PARK`、`BORGHESE`、`QUAI DU ROSAIRE`、
   `BRÜGGE`、`ORPHEUS. EURYDIKE. HERMES`……共约 90 条（含副题/地名行）。
2. **译稿没有把题和正文粘成一段。** `final.txt` 里题、副题、正文都是分开的段落。报告举的
   「一人情：…」也不是同段：`一` 是译者单独成段的组序号，下一段才是 `人情：…`，两者在页上
   紧贴（同一处排版粘连）。全书 `final.txt` 里没有一处「题＋首句」同段的焊接。
3. 粘的是**页面**：`build_pub` 对所有行一律发 `types=["p"]`，`chapter_xhtml` 于是把诗题印成
   `<p>`——和正文那些诗行**同一个类、同一个缩进（2em）、同一段两端对齐**。读者眼里（以及任何
   纯文本抽取 / TTS / 无段距的阅读器里）它就是第一句的一部分：

   > `诗人你离开我，你这时辰。` 　＝ 标题「诗人」＋ 首行「你离开我，你这时辰。」
   > `在一座陌生的园林里博尔盖比庄园是两条路。` ＝ 题＋副题（BORGHESE）＋首句
   > `玫瑰码头布鲁日街巷有一种轻缓的步伐` ＝ 题 QUAI DU ROSAIRE ＋ 地名 BRÜGGE ＋ 首句
   > `广场弗尔讷`、`塔弗尔讷的圣尼古拉塔地之内部` 同理

   即报告举的三句是**同一处根因**：**组装器没有「诗题」这个概念**。
4. `title_zh`（第N首）确实印成了 `<h1>`，但**没有印成 `<h2>`**——`sub` 为空，`chapter_xhtml`
   的 `<h2>` 分支不触发，EPUB 里一本书题名只出现一次（`<title>` 不渲染）。这一条是误报。

### 1.2 改在组装器里（`pipeline_build/build_pub.py`（+114/−9 行）；`pipeline_build/build_all.py`（+10/−1 行））

只对 `VERSE`（`{"neuegedichte"}`）分支生效，其它书走原路径。

| 位置 | 改动 |
| --- | --- |
| `build_pub.py` 新增 `BRACKETS` + 重写 `verse_lines()` | 分行时不切断成对括号/引号内：`（…从前这里曾有什么？）` 不再被拆成两行、把孤零零的 `）` 甩到下一行；`（哪里有一个头脑…享用它们？）` 同。括号不平衡的段落退回旧行为。 |
| 新增 `GROUP_NUM` | 丢掉章首的源文组序号行（`一`/`第二`/`三`/`壹`/`第二部`/`II`…）。它们此前靠 `drop_repeated_head` 的 Levenshtein ≤3 侥幸被删（`一` vs `第1首` 恰好 3），`二`、`一`、`一`（c015/c016/c012）则漏网印在正文里。 |
| 新增 `verse_roles()` + `verse_block()` | 按 `verse_roles.json` 把每章的诗题/地名行标成 `verse-title` / `verse-sub`，**整行输出、不参与句末切分**（原来 `俄耳甫斯。欧律狄刻。赫尔墨斯` 会被切成三行）；其余行标 `verse`。 |
| 新增 `TITLE_KINDS` + `carry_tail()` | **把章末悬空的诗题搬到下一章开头。** 见 §1.3。 |
| `collect()` | `types` 由 `["p"]*n` 改为按块返回；`if book in PLAY` → `elif`；`drop_repeated_head` 提到分行之前（只影响 verse 书）。 |
| `build_all.py` 新增 `VERSE_KINDS` | `para_html` 的 class 判定由「`verse` 才有 class」改为「`verse`/`verse-title`/`verse-sub` 都有自己的 class」。其余 kind 行为不变。 |
| `build_all.py` STYLE 增 2 条 | `p.verse-title{…margin-top:2.2em;font-weight:bold}`（题）与 `p.verse-sub{…italic;.92em;#555}`（地名行）。**`p.verse` 原样未动**，所以用 `verse_indices` 的另一本诗体书（时祷书等）排版不受影响。 |

新增数据文件 `work_pub/neuegedichte/verse_roles.json`：按章、按出现顺序列出译者的中文诗题
（title 75 条 / sub 15 条，覆盖 9 个有诗题的章），纯文本匹配，**不改译文、不冻结正文**——`final.txt` 仍是唯一文本来源。

### 1.3 顺带发现并修掉的真缺陷：章末悬空的诗题

分块器几乎每次都在「诗题」和「它的正文」之间切开。修前每章末尾都挂着一个没有诗的题：

| 章 | 章末悬空 | 它真正属于的章 |
| --- | --- | --- |
| c001 | 阿比萨格 | c002（`她躺着…`） |
| c003 | 大卫在扫罗面前歌唱 | c004 |
| c006 | 门廊 | c007 |
| c009 | 囚徒 | c010 |
| c011 | 尖端 | c012 |
| c013 | 贝居安会院 ＋ 圣伊丽莎白贝居安会院。布鲁日 | c014 |
| c015 | 海岛 ＋ 北海 | c016 |

读者看到的是一页末尾孤零零一个「尖端」，翻页后一首无题诗——报告里「尖端」被判为「无法解析」，
正是这个。现由 `carry_tail()` 统一上移（**改在生成链，不动 `final.txt`**；若最后一章仍以题结尾，
`collect()` 末尾会把它放回，不丢字）。

### 1.4 影响范围

- 只有 `VERSE` 集合（当前仅 `neuegedichte`）走新分支；`PLAY` 与普通散文书逻辑未变。
- `build_all.STYLE` / `VERSE_KINDS` 是共享的，但新增的两条 CSS 只被 `verse-title`/`verse-sub`
  引用，而这两种 kind 只由 `verse_block()` 产出。用改后的 `build_pub` 试建同批 7 本
  （含另一本诗体书 `时祷书`、两个剧本、`观察`/`判决`/`变形记`）：7 本全 0 err，所有
  XHTML/OPF/NCX 与 shipped EPUB **逐字节相同**。
- 全库 `verify_epub.py`：**70 epub，0 errors**（改前同为 70/0）。

---

## 二、逐句重写对照表

德语原文取自 `work_pub/neuegedichte/src/*.json`。原则：只补足中文的句子成分／语序，
保留原意象、原分行、原歧义，不添解释性文字。

| # | 原文（src） | 旧译 | 新译 | 判据 |
| --- | --- | --- | --- | --- |
| 1 | `Es wäre gut viel nachzudenken, um von so Verlornem etwas auszusagen` | 多想一些是好的，为了说出一点那失落了的东西 | 多想一些原是好的，为的是能说出一点那失落之物 | 中文失衡：`是好的，为了……` 无谓语承接；`wäre gut` 是虚拟（「原是好的」）。另「童年」本身是题，不再与首句连读 |
| 2 | `da lebten wir, wie Menschliches, das Ihre und wurden bis zum Rande voll Figur` | 那时我们活着，像属于人的东西，属于它们的，直到边缘都充满了形象 | 那时我们活着，像一样属于人的东西，是它们的所有，直到边缘都充满了形象 | 中文失衡：`像属于人的东西，属于它们的` 两个「属于」叠在无谓语结构里。德语 `das Ihre`（它们的那些／它们的所有）本身歧义，此处取「属于它们所有」，只补系词 |
| 3 | `in welchen nun zu dauern uns verwirrt` | 在其中继续存在如今使我们困惑 | 如今要在其中继续存在下去，却使我们困惑 | 中文失衡：逐字搬德语语序（`in welchen … uns verwirrt`），主语/谓语全丢；「位于其中继续存在」读不成句 |
| 4 | `ist deine Seligkeit in diesem Ding, zu welcher hin, wie zwischen Stamm und Rinde, dein großes Fühlen, kleinverwandelt, ging?` | 你的至福就在这件东西里吗？你浩大的情感，如同夹在树干与树皮之间，细小地转化着，正是朝着它而去吗？ | 你的至福是否就在这件东西里——你那浩大的情感，像夹在树干与树皮之间，变得细小，正是朝它而去？ | 中文失衡：德文是**一个**问句（`ist … ?`），旧译断成两句、第二个「吗」把关系从句变成第二个提问。改回单问句 |
| 5 | `Menschlichkeit: Namen schwankender Besitze, noch unbestätigter Bestand von Glück` | **一**人情：摇摆不定的所有物之名，尚未证实的一份幸福 | 人情：摇摆不定的所有物之名，尚未证实的一份幸福 | `一人情`＝源文组序号 `I`（译者作「一」）＋「人情」，**不是缺字**；「一」是 `GROUP_NUM` 该删的行。见 §3 |
| 6 | `Erdinneres.` | 地之内部。 | 大地内部。 | `Erde`＝大地，`-inneres`＝内部。「地之内部」不成词（报告猜「衍字」，实为 `Erde` 的「地」，但连写不通，故补成「大地」） |
| 7 | `Die Böschung Schauender umschließt die Schiene` | 观看者的**人坡**围住那道轨槽 | 观看者排成的斜坡围住那道轨槽 | `人坡` 是为 `Böschung Schauender` 生造的词，中文无此说法 |
| 8 | `Sein Blick ist vom Vorübergehn der Stäbe so müd geworden, daß er nichts mehr hält` | 他的目光被**走过来的栅栏**磨得那样疲倦，什么也抓不住了 | 他的目光被往复经过的栏杆磨得那样疲倦，再也抓不住什么了 | 误译兼失衡：`Vorübergehn der Stäbe` 是「栏杆的往复经过」，不是「走过来的栅栏」 |
| 9 | `Gib seinen leichten Händen nichts zu halten aus deinem Lastenden` | 不要给你的轻手任何东西去握住，从你沉重的一切里。 | 不要让他那双轻捷的手，从你沉重的一切里握住任何东西。 | 中文失衡：状语「从你沉重的一切里」按德语语序甩在句末，「给你的轻手…去握住」主语错位（`seinen`＝他的） |
| 10 | `aus eines Traumes Ausgeburten` | 从一场梦的**产孽**中 | 从一场梦的**产儿**中 | `产孽` 非词；`Ausgeburten`＝产物／产儿 |
| 11 | `zu kühl für Lorbeer sind noch seine Schläfe` | 他的太阳穴对月桂还太凉 | 他的太阳穴对月桂**来说**还太凉 | 缺「来说」，比较结构不完整 |
| 12 | `LETZTER ABEND / (AUS DEM BESITZE FRAU NONNAS)` | （诺娜修女旧藏）印在已是斜体的副题位上 | 诺娜修女旧藏 | 副题现在自带 `verse-sub` 样式，原文括号＋排版括号叠成「（（…））」 |
| 13 | `IN EINEM FREMDEN PARK / BORGHESE`；`QUAI DU ROSAIRE / BRÜGGE`；`DER TURM / TOUR ST.-NICOLAS, FURNES`；`DER PLATZ / FURNES` | 题、地名行都印成正文 `<p>`，于是 `在一座陌生的园林里博尔盖比庄园是两条路。`／`广场弗尔讷`／`塔弗尔讷的圣尼古拉塔地之内部`／`玫瑰码头布鲁日街巷…` | 题 → `verse-title`（粗体、上方留白），地名行 → `verse-sub`（斜体、小一号），正文 → `verse`（不缩进、独立成行） | 见 §1；译文一字未改 |
| 14 | `ORPHEUS. EURYDIKE. HERMES` | 被 `verse_lines` 按 `。` 切成三行（`俄耳甫斯` / `欧律狄刻` / `赫尔墨斯`） | 整行一个题：`俄耳甫斯。欧律狄刻。赫尔墨斯` | 标题不参与句末切分 |
| 15 | 章末悬空题（尖端／阿比萨格／门廊／囚徒／大卫在扫罗面前歌唱／贝居安会院＋地名／海岛＋北海） | 悬在上一章页脚 | 移到它所命名的诗的前面 | 见 §1.3 |

另：`c001` 卷首的**书名页五行**（`新诗集` / `莱纳·玛利亚·里尔克` / `莱比锡` /
`岛社出版` / `一九二〇`）已删——它们与 `title.xhtml`、`copyright.xhtml` 完全重复，
留在正文里就是五行假诗行。题献 `卡尔与伊丽莎白·冯·德·海特谨志友谊` 保留。
`titles_pub.py` 未动。

---

## 三、「一人情」与两处地名的定案

| 报告疑问 | 核实 | 处理 |
| --- | --- | --- |
| 「一人情」是「一／人情」粘连还是缺字？ | 源文 `Menschlichkeit: Namen schwankender Besitze…`；`一` 是译者给组序号 `I` 的译法（同书另有 `第二`、`壹`、`三`、`第二部` 四种写法），在 `final.txt` 里**是独立一段**，只是印在同一页紧贴着下一段，读成「一人情」。**不是缺字** | 组装器 `GROUP_NUM` 删掉序号行；正文作「人情：…」。**不加字** |
| 「广场弗尔讷」 | 源文 `DER PLATZ` ＋ `FURNES`，是「诗题 ＋ 地名」两行；中文 `广场` `弗尔讷` 本就是两段 | 标成 `verse-title` ＋ `verse-sub`，不再是紧贴的一行 |
| 「塔弗尔讷的圣尼古拉塔**地之内部**」 | 源文 `DER TURM` ＋ `TOUR ST.-NICOLAS, FURNES` ＋ `Erdinneres.`——三行三段。「地之内部」不是衍字，是 `Erdinneres` 的直译，但中文不成词 | 题/地名分标；`地之内部` → `大地内部` |

---

## 四、「原文即歧义／不改」清单

逐条读过原文后**判定不该动**的：

1. `da lebten wir, wie Menschliches, das Ihre`（第 2 条）——`das Ihre` 在德语里可读作「它们的
   所有物」也可读作「属于它们的那一份」，里尔克有意留白。**只补系词，不消解歧义**；不写成
   「像一件属于人的东西，属于它们所有」这类断定式。
2. `Menschlichkeit … ist das unmenschlich` 的谐音（人情／不近人情）——中文用了「不近人情」，
   与 `unmenschlich` 的双关恰好对上。虽然 `Menschlichkeit` 也可作「人性」，但**改了就丢掉双关**，
   保留「人情」。
3. `DIE SPITZE`（尖端）＝ 花边／蕾丝花边的「尖」——全诗双关 `Spitze`（尖端／花边），
   且与全书首篇的「花边之路」（`Bahn vergilbter Spitze`）呼应。中文只能取「尖端」一义，
   **这是不可译的双关，不是错译**，标题保留。
4. `BÉGUINAGE SAINTE-ELISABETH. BRÜGGE` → `圣伊丽莎白贝居安会院。布鲁日`：句中的「。」是
   原文的句点，保留（副题样式已与正文区分）。
5. `Ersatz kann keiner für ihn sein` 一段（阿尔刻斯提斯）里 `⟦i⟧就是⟦/i⟧` 的斜体、
   `玫瑰杯` 一段的多处 `⟦i⟧` 强调：都是译者对原文强调的标注，**保留**。
6. `在厅堂里`「戴着雅博领」（`Jabot` 音译）、`大理石车`「分给七匹拉车的马」（`An sieben Pferde
   verteilt`）、`复活`「只还等着埃里希和乌尔丽克·多罗特娅」——读得通，是译者的取词，未改。
7. `夏雨之前`「叫人想到一个哲罗姆」（`Hieronymus`）、`塔纳格拉`「一小块烧过的泥土」等
   短促句——里尔克原文亦然，**不是中文失衡**，未改。
8. 报告点名的好译 **`离别`／`死亡的体验`／`蓝色的绣球` 一个字未动**——已按段比对确认
   （改前成品留档 `scratch/_bak/neuegedichte_pre_20261122/`，三首诗各 5／11／5 段全部
   与改后逐字符相同）。`豹` 只改了第 1 行（§二 第 8 条），`童年`／`诗人` 见上表。

---

## 五、遗留（未改，供下一轮决定）

1. **目录仍是 18 条「第N首」。** 源文的 `I/II/III` 在每个诗组内重复计数，`titles_pub.py`
   按正文章序编成第N首（见 `MEMORY.md` 2026-10-26）。真正的诗题现在在正文里已经是
   独立的标题行，但 nav 仍是章级 18 条；本书末尾自带译者译好的 `目录`（74 首，c018），
   读者可由它索引。要做诗级 nav，得让每首诗单独成页，属另行设计。
2. **`目录` 页的译名与正文小有出入**（`少女的哀诉`/`少女的哀怨`、`阿比萨格`/`亚比煞`、
   `佛`/`佛陀`、`玫瑰码头`/`玫瑰经码头（布吕赫）` 等）。前者是正文译名，后者是译者给
   原书 `INHALT` 页的译法，两处各自内部一致。统一属改写译名，本轮不动。
3. 扫描源文全大写块时 `L'ANGE DU MÉRIDIEN`（法文题，`É` 不在扫描字符集里）未被自动命中，
   靠人工核出，已在 `verse_roles.json` 中标为 `正午的天使`（副题 `夏特尔` ← `CHARTRES`）。

---

## 六、改动可核对性

改前 EPUB 留档：`scratch/_bak/neuegedichte_pre_20261122/`（改前 `out/` 解包）。把改前、改后
每页正文按段落取集合做差，**差异恰好是上表的改动，没有第三种**：

* 消失的段：4 行组序号（`一`×3、`二`）；4 行书名页（`莱纳·玛利亚·里尔克`/`莱比锡`/
  `岛社出版`/`一九二〇`；`新诗集` 一行本来就被 `drop_repeated_head` 当「与标题近似」删掉了）；
  被改写/合并的 12 段（第 2 条把「你这久已逝去…」和「你浩大的情感…」并回一个问句，
  2 处括号收口、2 处题名不再被 `。` 切断）。
* 新增的段：与上表逐条对应。
