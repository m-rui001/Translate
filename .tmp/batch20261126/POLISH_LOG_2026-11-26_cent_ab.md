# POLISH_LOG 2026-11-26 — cent_a / cent_b（黑木《半人马》The Centaur 分片）

脚本：`work_batch_20261124/_polish_20261126_cent_ab.py`（改前备份 `*.bak_20261126`；
落盘方式一律「定位唯一子串 → 替换 → 断言命中数 1」；`json` 原 indent=1、CRLF 未动；
脚本尾 `ast.parse` 自查通过）

## 自检

| 篇 | 源段 | 译段 | 汉字 | 改动数 | 换行符 |
|---|---|---|---|---|---|
| cent_a | 156 | 151（不变） | 16366 | 16 | CRLF |
| cent_b | 226 | 220（不变） | 17514 | 12 | CRLF |

体检（脚本内跑，两篇均 OK）：JSON 可解析 ✓ 长度与备份一致 ✓ 无空段 ✓
无 ASCII 直引号 `"` ✓ 无 `。。`／`，，` 类重复标点 ✓ 无「汉字＋空格＋小写英文＋空格＋汉字」残留 ✓
`「」`／`『』` 全配对 ✓ `⟦⟧` 无 ✓

## 对齐说明（offset 非 1）

`paras_tool show` 报 cent_a `offset=5`、cent_b `offset=6`。原因不是分段错乱，而是**章序行**
（I / II / … / XI）在源文里单独成段、译稿未收（篇名亦不入 `_zh.json`）。
去章序行后两篇逐段严格一一对应：a 为 `zh[i] ↔ src[去行后第 i 项]`（`zh[0]`=src[1] 詹姆斯题铭，
`zh[150]`=src[155] 末段）；b 同理（`zh[0]`=src[1] 诺瓦利斯题铭，`zh[219]`=src[225] 末段）。
未为对齐增删任何段。

## 改动清单

### cent_a（16 条：①4 ③3 ⑤2 ⑥7）

| # | 类 | 旧句 → 新句 | 理由 | 英文原文 |
|---|---|---|---|---|
| 1 | ⑥ | 他那体格并不像**大人物**常有的情形那样把人压得透不过气 → 并不像**大个子**… | big people 是体格大的人，非「要人」 | *The size of his body did not smother, as so often is the case with big people* |
| 2 | ⑥ | 就是一个从庸众中站出来引人注目的**个性** → **个体** | 「一个……个性」量词／范畴错配 | *an individuality that invites consideration from the ruck of commonplace men* |
| 3 | ① | **血管里**有一种对荒野的贪求 → **他血管里**… | 缺主语，前句主语是「他」，此处悬空 | *An insatiable longing for the wilderness was in his blood* |
| 4 | ⑥ | 仔细地系着一块**骨牌**标签 → **骨制**的标签 | bone label 是骨制标签，骨牌是 domino | *carefully ticketed with a bone label* |
| 5 | ⑥ | 不过是**一条**枯骨的谷 → **一片**枯骨的**谷地** | valley 不用「条」 | *was a valley of dry bones* |
| 6 | ③ | **这条线索，他这样称呼它，**把他自己心智的挣扎结晶得… → **这条他所谓的线索，**… | `This clue, as he called it,` 插入语硬搬，读者以为另有「线索」 | *This clue, as he called it, crystallized so neatly…* |
| 7 | ③ | **信件颇不规则** → **信件时断时续** | irregular correspondence 指通信断续，非信件不合规格 | *months of somewhat irregular correspondence* |
| 8 | ① | **我，爱他，也听他讲，**却从未完全领会… → **我虽然爱他、也听他讲，**… | 关系从句 `I, who loved him and listened` 悬空同位语 | *I, who loved him and listened, yet never quite apprehended…* |
| 9 | ① | **活的思想，那个！** → **活生生的思想，正是这个！** | `Living idea, that!` 残句直搬，中文不成话 | *Living idea, that!* |
| 10 | ① | **他舌头上就有着一句**关于他们的话 → **话就到了他舌尖上**——一句… | 直搬 on the tip of his tongue，中文无此说法 | *it was on the tip of his tongue to make a remark about them* |
| 11 | ⑥ | 我在看**对面半桌子**那两个人 → **对面桌子中段**的那两个人 | half-way down the table opposite 是「对方那侧桌腰」 | *those two half-way down the table opposite* |
| 12 | ③ | 更像是**本质的不能言说在挣扎着发出一种对它是生疏的、不合适的语言** → **本质上的不能言语，挣扎着要挤出一句对它生疏而不合的语言** | 抽象名词主语（inarticulateness）＋「发出语言」动宾不搭 | *like essential inarticulateness struggling into an utterance foreign to it--unsuited* |
| 13 | ⑥ | 把话一字一字凿出来，**真费着力** → **真费着力气** | 「费着力」不成词 | *quarrying out the words with real labor* |
| 14 | ⑤ | 往**驾驶台**去了／让我上**驾驶台**跟你抽支烟 → 两处改**舰桥** | 全册 bridge 作「舰桥」4 次、「驾驶台」2 次；此处为少数派，归一 | *toward the bridge* / *come up sometimes for a smoke with you on the bridge* |
| 15 | ⑥ | **这些贪求代表着灵魂的掳获物，而他必须禁绝自己。** → …而他必须**克制自己不去取用**。 | 禁绝（杜绝某事）不能带「自己」 | *that loot of the soul which he must deny himself* |

### cent_b（12 条：①8 ②1 ⑥3）

| # | 类 | 旧句 → 新句 | 理由 | 英文原文 |
|---|---|---|---|---|
| 1 | ⑥ | **那堆**伪普世文化的闷气 → **那股**… | smother 是弥散的闷气，不用「堆」 | *smother of sham universal culture* |
| 2 | ① | 风与海的**流**先是经由他到达我 → 风与海的**气流**… | currents 无中心语，「流」单字不成名词 | *the currents of wind and sea reached me through him first* |
| 3 | ② | 他是**那深深埋在我自身之中的东西的**极端例子 → 他是**我自身深处那件东西的**极端例子 | 三个「的」串起，中心语被压没 | *he was a supreme case of what lay so deeply in myself* |
| 4 | ① | 虽然它们在**形体界定上**躲开他 → 在**形体上总是**躲开他 | `in terms of physical definition` 状语硬搬 | *though they evaded him in terms of physical definition* |
| 5 | ① | 证实了**他做了件鲁莽事的感觉** → 证实了**他觉得自己做了件鲁莽事** | 定语套定语，中心语（感觉）失主 | *confirmed the sense that he had done a rash thing* |
| 6 | ⑥ | 虽然它们**好歹**让我们的相识熟成了友谊 → **竟如此好心地**… | kindly 是承它的好意，非「勉强、好歹」 | *though they have so kindly ripened our acquaintance into friendship* |
| 7 | ③ | 并且**使他被置于人类之中而绝对孤立** → 并且**使他在人类当中绝对孤立** | 被动式硬搬（placed … thus absolutely alone） | *and placed him in the midst of humanity thus absolutely alone* |
| 8 | ① | 施塔尔平静地讲着，**他是如何被……逼到某种这样的信念的。** → …**他如何被……逼到了这样一种信念。** | 「是……的」框架套长状语，句子散架 | *Stahl was telling calmly how he had been driven to some such belief by the facts…* |
| 9 | ① | **他不再被关押、戴镣在一个渺小人格的监牢里。** → 他不再**被关锁、被戴上镣铐，囚在**一个渺小人格的**牢**里。 | caged and manacled within… 动宾错位 | *He was no longer caged and manacled within the prison of a puny individuality* |
| 10 | ① | 奥马利**在当晚自觉得不可少的独处里** → **在那晚他觉得不可或缺的独处里** | 定语断裂（in the solitude that he found necessary that evening） | *In the solitude that O'Malley found necessary that evening* |
| 11 | ① | **他爱抚弄着它。** → **他满怀爱意地反复玩味它。** | 「爱抚弄」歧义（爱／抚弄），played lovingly with it | *He played lovingly with it.* |
| 12 | ⑥ | **「撑住！」**他听见耳语 → **「站住！」** | `Hold up!` 此处是「停住、别动」，非「撑住」 | *"Hold up!" he heard whispered* |

## 未改判定（读得通或近于重译，一律不动）

### cent_a
- zh[6]「我也把与那人的这番经历看得非同寻常地难忘」：与「难忘的历险」字面重复，但原文 memorable 亦复现（篇名式回指），属作者复沓，不改。
- zh[20]「他便走到独处中去，把它唤回脚边」：calling it to heel 是驯犬语，译文保留此意象，可解，不改。
- zh[21]/[23]「一句话，他是个……的人」句序依原文 `A man he was, in a word`，通，不改。
- zh[43]「为何人们会在他身上引起一种死寂」：`produced in him a state of death` 略生硬，然可读，改动近于重译，不改。
- zh[108]「升起一个预言式的、巨大的姿势」「某种巨大的、泅泳的美之情绪」：`gesture` 作「姿势」、`giant swimming mood` 本即朦胧，保留原译的模糊。
- zh[58]/[78]/[113] 段末以「：」收：系引语起段（下段整段为引语），依原分段，非体例失。
- 题铭体例：`——威廉·詹姆斯《多元的宇宙》。`／`——同上。`／`——惠特曼。`／`——梭罗。`／`——亨利·柏格森。`／`——诺瓦利斯《花粉》。` 全篇一致，篇名不入 `_zh.json`，不改。
- 「希腊诸岛」2 次、「皮货商」6 次、「施塔尔」11 次：篇内一致，且与 cent_d 多数派同，不改。
- 诗行段（59–61，奥肖内西颂歌）保留 `\n` 分行与段末标点，未动。

### cent_b
- zh[13]「『试着，』我说，因为我一直怕它冒出来太多」：说话者在引语内自引其语（原文 `'Tried to,' I said`），属原文体例，不改。
- zh[70]「若不径直采用费希纳那个概念的原文」：`the very letter of Fechner's conception` 之 letter 作「字面／原文」，可通，不改。
- zh[96]「『unheimlich』」保留德文原词：术语保留体例（同本册 `Urmenschen` 作「原人」），不改。
- zh[149]「不是你我惯于用这个词所指的那种人」：双重否定链依原文，通，不改。
- zh[156]「脱开中央的、覆盖性的身体而运作」：`the central covering body` 艰涩但可解，改动即重译，不改。
- zh[160]「『星光体』」、zh[190]「宁芙」：通译／音译，篇内仅一见，不改。
- zh[147]「——古谚。」（OLD SAYING）：署名行体例，段末标点齐全，不改。
- 章序行 VI–XI 不入译稿：与 cent_a 同例，勿补。
- 对白引号「」、术语『』、双引号层级全篇自洽，未换制。

## 遗留（供合并期统一，本册未动）

- 全册 bridge：cent_a 已归一为「舰桥」，cent_d/cent_h/cent_i 亦作「舰桥」；合并期可复查是否仍有「驾驶台」残迹。
- `Urmenschen` 作「原人」、`Cosmic Being` 作「宇宙生命体」、`astral` 作「星光体」，cent_b 内一致；cent_c 起若另立译名，合并期统一。