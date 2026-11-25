# 润色日志 — poe_cask / valdemar（2026-11-26）

书目：`work_batch_20261124/`（短篇，Poe《一桶阿蒙蒂亚多酒》与《瓦尔德马先生案之真相》）
依据：`POLISH_BRIEF_2026-11-25.md`、`SUBTASK_README_2026-11-26.md`
脚本：`_polish_20261126_poe_1.py`（定位唯一子串 → `assert` 命中一次 → 替换；结尾 `ast.parse` 自查）
对齐：两篇均 `offset = 1`（`zh[i]` ↔ `src[i+1]`），无分段差异。

## 自检

| 篇 | 段数（改前=改后） | 汉字（改前→改后） | 改动数 | 涉及段 | 换行符 | JSON |
|---|---|---|---|---|---|---|
| poe_cask | 89 = 89 | 3221 → 3219 | 8 | 8 | LF（indent=0） | 可解析，无空段 |
| valdemar | 51 = 51 | 5143 → 5119 | 33 | 24 | LF（indent=1） | 可解析，无空段 |

- 无 ASCII 直引号（本批统一「」）；无 `。。`／`，，` 类重复标点；无残留英文；段末标点齐全；
- 全篇 `；——`（英式 `;--` 直搬）已清零；
- `check_batch.py`：两篇均**不在**报错清单内（251 篇里 49 篇有问题，与此两篇无关）。
- 备份：`poe_cask_zh.json.bak_20261126`、`valdemar_zh.json.bak_20261126`（`paras_tool.py backup` 生成，未覆盖既有 `.bak_20261125`）。

## 改动清单 — poe_cask（8 条：① 4、③ 0、⑥ 3、⑦ 1）

| # | 类别 | 旧句 → 新句 | 理由 | 原文 |
|---|---|---|---|---|
| 1 | ① | 「福图纳托加在我身上的伤害，**成千上万**，我都**极**力忍了」→「福图纳托加在我身上的伤害**有千百桩**，我都**尽**力忍了」 | 插入语「成千上万」堵在主谓之间，「伤害，成千上万，我…」读来断裂；`the thousand injuries` 亦不必夸大 | The thousand injuries of Fortunato I had borne as I best could |
| 2 | ① | 「那是**有**狂欢节最疯的时节，一天傍晚…」→「那是狂欢节最疯的时节，一天傍晚…」 | 「那是有的时节」谓语重复，删一字即通 | one evening during the supreme madness of the carnival season |
| 3 | ⑦ | 「我没有约会**；——**走吧。」→「我没有约会**——**走吧。」 | `;--` 直搬成「分号＋破折号」，全篇破折号体例为「——」 | I have no engagement;--come |
| 4 | ⑥ | 「是我看你**染了**重伤风」→「是我看你**患了**重伤风」 | 「伤风」不与「染」搭配（染病/患病） | the severe cold with which I perceive you are afflicted |
| 5 | ① | 「他转向我，**用两只蒙着翳的眼睛看我的眼睛**，那眼里淌着**醉出来的**黏液」→「他转向我，**两只蒙着翳的眼珠直盯着我的眼睛**，眼里淌着**酒醉的**黏液」 | 一句里「眼睛」两见、「的」字串三层；「醉出来的黏液」不成话 | with two filmy orbs that distilled the rheum of intoxication |
| 6 | ① | 「你是**不能少的人**。」→「你是**少不得的人**。」 | 「不能少的人」非中文说法 | You are a man to be missed |
| 7 | ⑥ | 「有一处还堆成个不小的**土丘**」→「…不小的**骨堆**」 | 堆的是骨殖，`a mound of some size` 非土丘（量词／词义误置） | forming at one point a mound of some size |
| 8 | ⑥ | 「福图纳托举起他那支**昏沉**的火把」→「…**黯淡**的火把」 | `dull torch` 是光弱，不是火把「昏沉」（拟人误读） | uplifting his dull torch |

## 改动清单 — valdemar（33 条：① 8、② 2、③ 6、④ 2、⑤ 2、⑥ 9、⑦ 4）

| # | 段 | 类别 | 旧句 → 新句 | 理由 | 原文 |
|---|---|---|---|---|---|
| 1 | 2 | ⑦ | 「疏漏**：——**至今还没有人」→「疏漏**——**至今还没有人」 | 冒号叠破折号 | --no person had as yet been mesmerized in articulo mortis |
| 2 | 3 | ⑥ | 「已宣布他**患了确诊的**痨病」→「已宣布他**已确诊为**痨病」 | 「确诊的痨病」定语误挂；`in a confirmed phthisis` 是说病已确诊 | his physicians had declared him in a confirmed phthisis |
| 3 | 4 | ② | 「属于**那种对其终止于死亡的时日可以精确计算的性质**」→「属于**这样一种性质：可以精确算出它终结于死亡的时日**」 | 三层「的」把中心语「性质」压没 | His disease was of that character which would admit of exact calculation in respect of the epoch of its termination |
| 4 | 4 | ② | 「在医生们宣告**的他的**死期之前」→「在医生们宣告**的**死期之前」 | 「的他的」两「的」相撞 | before the period announced by his physicians |
| 5 | 9 | ① | 「他说话吐字清晰**——不用人帮忙服一些缓和的药——**我进屋时」→「他说话吐字清晰**，不用人帮忙就服了些缓和的药；**我进屋时」 | 破折号里塞进一个与「吐字清晰」无语法关系的动词短语，主语断流 | He spoke with distinctness--took some palliative medicines without aid--and… |
| 6 | 12 | ⑥ | 「在迅速地**衰沉**下去」→「…**衰竭**下去」 | 「衰沉」非词（衰颓／沉衰均不切） | he was evidently sinking fast |
| 7 | 13 | ⑥ | 「**答应了**我的**愿望**」→「**答应了**我的**请求**」 | 搭配：答应请求／满足愿望 | accede to my desire |
| 8 | 15 | ① | 「他**微弱地、却相当可以听见地**答道」→「他**答得很微弱，却相当清楚**」 | 「可以听见地」是 `audibly` 的副词硬造 | He replied feebly, yet quite audibly |
| 9 | 17 | ⑥ | 「呼吸**是鼾声性的**，间隔半分钟一次」→「呼吸**带鼾声**，隔半分钟一次」 | 「鼾声性的」不成词 | his breathing was stertorous, and at intervals of half a minute |
| 10 | 18 | ⑥ | 「几乎**原封不动地**持续了一刻钟」→「几乎**一成不变地**持续」 | 成语误用：「原封不动」只用于物件 | This condition was nearly unaltered for a quarter of an hour |
| 11 | 18 | ⑥ | 「鼾声性的呼吸停止了——也就是说，「鼾声性」不再显露；间隔却没有**减少**」→「带鼾声的呼吸停止了——也就是说，鼾声不再明显；间隔却没有**缩短**」 | 前半不成词；`undiminished` 指间隙未变短，非「减少」 | its stertorousness was no longer apparent; the intervals were undiminished |
| 12 | 18 | ① | 「病人的四肢**是冰一样冷**」→「病人的四肢**冷得像冰一样**」 | 「是…冷」判断句套形容词，谓语失配 | The patient's extremities were of an icy coldness |
| 13 | 19 | ⑥ | 「**十点差五分**，我觉察到催眠影响的…征象」→「**差五分十一点**，…」 | **硬伤**：`five minutes before eleven` 是十点五十五分，译文读成九点五十五，与下文「十点过几分医生来访」自相矛盾 | At five minutes before eleven I perceived unequivocal signs |
| 14 | 19 | ③ | 「直到把那入睡者的四肢**（在先把它们安置成看似舒适的位置之后）**完全僵固化了」→「直到我**先把他四肢摆成看似舒适的姿势，再把它们完全僵住**」 | 英语 `after placing…` 插入语按原序塞进中文主谓之间，动作先后读不出来 | until I had completely stiffened the limbs of the slumberer, after placing them in a seemingly easy position |
| 15 | 19 | ① | 「两臂也差不多**，**安放在床上」→「两臂也差不多**伸直**，安放在床上」 | 「两臂也差不多」缺谓语 | the arms were nearly so |
| 16 | 22 | ③ | 「作了**半心半意的一次尝试**」→「**半心半意地试了一下**」 | 冠词式「一次尝试」＋「半心半意的」定语硬搬 | I made a kind of half effort |
| 17 | 22 | ① | 「非常顺从地**跟随我的手给它的每一个方向**」→「非常顺从地**随着我的手，朝我给它的每一个方向移动**」 | 「跟随…方向」动宾失配，两个「的」串死 | followed every direction I assigned it with mine |
| 18 | 23 | ③ | 「他全身**被一阵极轻微的战栗激动**」→「他全身**起了一阵极轻微的战栗**」 | 被动式硬搬（有「被」不必真有被动）＋「战栗激动」同义相撞 | his whole frame was agitated by a very slight shivering |
| 19 | 23 | ④ | 「嘴唇迟缓地翕动，**从它们之间**发出」→「…**从两唇之间**发出」 | 「它们」指代不明（嘴唇不能作复数代词） | the lips moved sluggishly, and from between them… |
| 20 | 24 | ⑦ | 「「是的**；——**现在睡着了。」→「「是的**——**现在睡着了。」 | `;--` 直搬，统一为「——」 | Yes;--asleep now |
| 21 | 25 | ③ | 「**我在这里**摸了摸他的四肢」→「**这时**我摸了摸他的四肢」 | 英语 `here`（此时）直搬成方位词 | I here felt the limbs |
| 22 | 28 | ① | 「直到福———医生**到来**。他在日出前一点**到来**」→「…**到来**。他在日出前**不久赶到**」 | 一句内「到来」两见，且「日出前一点」易误读 | until the arrival of Dr. F--, who came a little before sunrise |
| 23 | 31 | ⑦ | 「「是的**；——**还睡着——正在死去。」→「「是的**——**还睡着——正在死去。」 | 同上 | Yes;--still asleep--dying |
| 24 | 33 | ① | 「两眼缓缓地**睁开转动**」→「两眼缓缓**睁开**」 | 两个动词硬拼，眉眼动作先后不明 | The eyes rolled themselves slowly open |
| 25 | 33 | ⑥ | 「下颌随着一声听得见的**脱臼般**的声音垂落」→「下颌随着一声**清晰的响动猛然垂落**」 | **硬伤**：`jerk` 是猛然一沉，原文无「脱臼」，属增添与误读 | the lower jaw fell with an audible jerk |
| 26 | 35 | ⑤ | 「从那胀开的、不动的**两颌**之间」→「…**牙关**之间」（同改 46 段「两颌和嘴唇」） | 「两颌」非中文解剖词（颌指单骨）；全篇统一「牙关」 | from the distended and motionless jaws |
| 27 | 37 | ⑦ | 「「是的**；——**不**；——**我一直在睡——」→「「是的**——**不**——**我一直在睡——」 | 同上（两处） | Yes;--no;--I have been sleeping |
| 28 | 38 | ① | 「我们**一言不发地默默**忙着救醒勒———先生」→「我们**默不作声，一心**忙着救醒」 | 「一言不发」与「默默」语义重复，句子拖沓 | we busied ourselves, silently--without the utterance of a word |
| 29 | 40 | ⑥ | 「无非是**确保**他立刻、至少是迅速地**消解**」→「无非是**促成**他立刻、至少是迅速的**死亡**」 | `dissolution` 此处是死亡／解体，「消解」是词义误读；「确保死亡」亦搭配不当 | to insure his instant, or at least his speedy dissolution |
| 30 | 43 | ③ | 「复活的最初迹象**由虹膜的部分下移显示出来**」→「复活的第一个迹象，**是虹膜略微下移**」 | 「由…显示出来」被动直搬，句子无施动者 | The first indication of revival was afforded by a partial descent of the iris |
| 31 | 43 | ③ | 「伴随着**一种黄色的脓浆（从眼睑之下）的大量涌出**」→「还伴随着**大量黄色的脓浆从眼睑底下涌出**」 | 括号插入语按英文语序嵌在名词与中心语之间，中文读不通 | accompanied by the profuse out-flowing of a yellowish ichor (from beneath the lids) |
| 32 | 46 | ⑤ | 「（虽然**两颌**和嘴唇仍同先前一样僵直）」→「（虽然**牙关**和嘴唇…）」 | 见 #26，全篇归一 | although the jaws and lips remained rigid |
| 33 | 48 | ④ | 「但因**意志**全然中止而未能奏效」→「但因**病人的意志**已全然停摆而未能奏效」 | 段内两个「我」，此处「意志」易被读成叙述者的意志 | failing in this through total abeyance of the will |

## 未改判定（读得通、或改了即越界，一律不动）

**poe_cask**
- 「他这个福图纳托有个短处」「我到底是要报仇的」「报了仇而报仇者自己遭了殃」——口语插入与复沓是叙述人腔调，保留。
- 「那是有…」之外，「他过分热络地招呼我」「我见了他那样高兴，握起他的手来简直没个够」——通顺。故 ① 只在第 2 条收一改。
- 「论绘画和宝石…是个充内行的」——`quack` 译「充内行」准确，不改。
- 「我向他鞠了一躬，领着他穿过好几间厅堂」——`bowed him through` 为「鞠躬引路」，译文可通，不重译。
- 「酒在他眼里发亮」「我又停了一停」——短句节奏，保留。
- 「愿他安息！」（`In pace requiescat!`）——拉丁文归化为中文成语式收束，合体例。
- 专名：福图纳托／卢凯西／蒙特雷梭／阿蒙蒂亚多／梅多克／格拉夫／雪利——全篇一致，无需归一。

**valdemar**
- 「我亲爱的皮———」「丁———」「福———」「勒———」「——瓦尔德马——」——原文即以破折号隐去姓名（`P---`、`D----`、`F----`、`L--l`），书信用「———」，与原文形制对应，不改（若改半角连字符，反破坏全篇体例）。
- 「我怕你已经催过眠了」——`I fear you have mesmerized--` 是说话人自我截断，译「催过眠了」保留截断感；改成「施行过催眠」会抹掉这层断句，判为不改。
- 「当我完成这一切时，已过午夜」——`it was fully midnight`，译「已过午夜」略偏，但与下文「凌晨三点」不冲突，属可容忍的模糊，不改。
- 「右肺的上部也部分地、即便不算彻底地骨化了」——`partially, if not thoroughly` 的让步语虽拗，未至读不通，且改动会动到医学判断的分寸，不改。
- 「只说病人已在死亡的痛苦之中」——`in the death agony` 译「死亡的痛苦」直白但不错，不改。
- 「把横向的手法换成了纵向的」——`lateral / downward` 作「横／纵」是中文习惯对举，不改。
- 「我既说过「声音」，也说过「嗓音」」——`sound / voice` 的分辨正是原文要点，保留。
- 「令人憎恶的——可憎的」——`loathsome--of detestable` 的复沓，刻意保留。
- 「他便收回手法」（`retraced my steps`）——取「收回」的具象读法，语境可通，不动。
- 睡行者 / 睡行状态（`sleep-waker / sleep-waking`）——全篇一致，不改。