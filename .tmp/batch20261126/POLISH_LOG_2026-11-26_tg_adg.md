# POLISH_LOG 2026-11-26 — tg_dawn / tg_dreams / tg_honour（邓萨尼三篇）

稿源：`work_batch_20261124/{tg_dawn,tg_dreams,tg_honour}_zh.json`
原文：`_tg_dawn_paras.json` / `_tg_dreams_paras.json` / `_tg_honour_paras.json`
对齐：三篇 `offset = len(src) - len(zh) = 0`（源自段首即正文，无「篇名行」，也**无未译章号行**；
`src[0]` 非篇名而是正文「When the worlds and All began…」「I」「Of the great wars…」）。
逐段核验起始语气与语义，`zh[i] ↔ src[i]` 一一对应，无错位。段数、段序、`\n` 均未动。
脚本：`work_batch_20261124/_polish_20261126_tg_adg.py`（备份 `<key>_zh.json.bak_20261126`）

## 自检

| 篇 | 段数 | 汉字 | 改动数 | 换行符 |
|---|---|---|---|---|
| tg_dawn | 19（改前 19） | 3241 | 12 | LF |
| tg_dreams | 22（改前 22） | 1307 | 12 | LF |
| tg_honour | 15（改前 15） | 1501 | 16 | CRLF |

`check_batch.py tg_dawn tg_dreams tg_honour` → checked 3, with problems 1, paras 56, han 6049
唯一告警：`tg_dreams[0]`「一」、`tg_dreams[18]`「二」NO-END-PUNCT —— 源文为裸罗马数字节题
（`I` / `II`），承 tg_journey_a 体例作汉字数字单行、不加句末标点，属豁免项，非缺陷。
脚本内另跑：JSON 可解析 ✓ 长度与备份一致 ✓ 无空段 ✓ 无 ASCII 直引号 ✓ 无重复标点 ✓
无汉字夹小写英文 ✓ 无首尾/连续空白 ✓ `ast.parse` ✓

## 改动清单

### tg_dawn（12 条：①4 ③1 ⑥7）

1. ⑥量词　`她玩着那只金球` → `她玩着那个金球`（[0]；球论「个」不论「只」；同篇 [2][3]「一只金球」一并归一）
   原：*Their child, who played with the golden ball.*
2. ①　`他们从白了岁月的眉毛底下看着那开端` → `他们从被年岁染白的眉毛底下看着那开端`（[0]；「白了岁月的眉毛」语序倒错，主语被吃掉）
   原：*They saw the Beginning from under eyebrows hoar with years.*
3. ⑥量词　`找到黎明之子所哭的那只金球` → `…那个金球`（[2]）
   原：*at last they found the golden ball for which the Dawnchild wept.*
4. ④指代　`翁博罗多姆紧跟在他脚后` → `翁博罗多姆紧跟在猎犬脚后`（[2]；前句主语是猎犬「雷」，紧跟句主语换人，「他」易误指翁博罗多姆自己）
   原：*and fast at his heels followed Umborodom.*
5. ⑥量词　`他们之间夹带着一只金球` → `…一个金球`（[3]）
   原：*that carried away between them a golden ball.*
6. ①　`也不想她所有的父亲诸神` → `也不想她的父亲们——诸神`（[5]；「所有的父亲诸神」定语与同位语糊成一团，读不出「她的众父即诸神」）
   原：*nor of all her fathers the gods.*
7. ⑥漏译　`可一只野鸭在山间飞回家时…` → `可芦苇丛里的一只野鸭在山间飞回家时…`（[6]；原文 in some reeds 未译，野鸭的位置是「谁最后看见」的关键）
   原：*but a wild duck in some reeds had seen it last as she came home across the hills.*
8. ①　`可唉！它哗啦一声落进大海` → `可是，唉！它哗啦一声落进大海`（[8]；「可唉」不成词）
   原：*But alas! it fell with a splash into the great sea.*
9. ⑥词义　`她小心地望着它落下` → `她仔细地望着它落下`（[8]；carefully 是「仔细」，非「小心／谨慎」）
   原：*and carefully she watched it as it fell.*
10. ①⑥　`从佩加纳门槛上最后一级玉髓台阶上大力跃下` → `从佩加纳门槛的最后一级玉髓台阶上奋力跃下`（[11]；一句两个「上」介词叠加；mightily 是「奋力」不是「大力」）
    原：*mightily dived from the last chalcedony step out of Pegana's threshold.*
11. ③　`把湖变成在银子里闪光的蓝宝石` → `把湖泊变成在银光中闪亮的蓝宝石`（[12]；amongst silver 直搬成「在银子里」，中文不成话）
    原：*their lakes to sapphires gleaming amongst silver.*
12. ⑥　`这些事连诸神也看不清。` → `这些事连诸神也无从得知。`（[18]；全篇结句，hidden from the gods 是「瞒过诸神」，不是视力问题）
    原：*These things be hidden even from the gods.*

### tg_dreams（12 条：①5 ②2 ③4 ④1 ⑥3，有互见）

1. ⑥　`那时我赞美诸神，献上祭祀` → `…献上祭品`（[1]；offer sacrifice＝献祭／献祭品，「祭祀」指仪式本身）
   原：*then did I praise the gods and offer sacrifice.*
2. ①　`从最后一处记得的角落扫去` → `从最后一处还留在记忆里的角落扫去`（[1]；「最后一处记得的角落」缺谓语，读不通）
   原：*tore up the dust and even the spider's web from the last remembered nook.*
3. ②③　`四下还躺着巨大的头骨形状，像很久以前被驱赶的奴隶大军为暴虐的君王建造的白色大理石宫殿穹顶。` → `四下还躺着巨大头骨的形状，像白色大理石的宫殿穹顶——那是很久以前被驱赶的奴隶大军为暴虐君王建造的。`（[7]；四个「的」把中心语「穹顶」压没，且英语比较结构整个照搬）
   原：*here and there lay the enormous shapes of skulls like the white marble domes of palaces built for tyrannous kings a long while since by armies of driven slaves.*
4. ⑥　`曾经撕下我少年时花园里的花` → `曾经摘下我少年时花园里的花`（[10]；花不能「撕」，tore 此处是「摘」）
   原：*tore once the flowers in gardens of my youth.*
5. ①③④　`他们造了悔恨，他的毛皮灰得像…；造了痛苦，他有滚烫的手和迟迟不去的脚；…造了愤怒，有夏日蜻蜓急飞的迅疾，生着燃烧的眼睛。` → `他们造了悔恨，毛皮灰得像…；造了痛苦，一双手滚烫，一双脚迟迟不去；…造了愤怒，飞得像夏日的蜻蜓一样急，眼里烧着火。`（[14]；with／having 分词短语逐句照搬成「他有…」，且「他」先后指悔恨与痛苦，读者必错认）
   原：*They made Remorse with his fur grey like a rainy evening in the autumn, with many rending claws, and Pain with his hot hands and lingering feet, … and Anger with the swift flight of the dragonfly in summer having burning eyes.*
6. ①　`那些弯弧而美丽的骨头`→`那些弯曲而美丽的骨头`（[16]；「弯弧而」不成词）
   原：*I looked long at those curved and beautiful bones.*
7. ④　`它们再也伤害不了它们所造的万界中最小的生灵。我久久想着它们做过的恶，也想着它们做过的好。` → `它们再也伤害不了自己亲手所造的万界中最小的生灵。我久久想着诸神做过的恶，也想着他们做过的好。`（[16]；同段「它们」兼指骨头与诸神，与下句「他们那双大手」相撞）
   原：*that were no longer able to hurt the smallest creature in all the worlds that they had made. And I thought long of the evil that they had done, and also of the good.*
8. ⑥　`只为给一个孩子摘一朵报春花` → `只为造一朵报春花，好让孩子去摘`（[16]；to make a primrose for a child to pick，造花的是神的手，摘花的是孩子，原译把施事换了）
   原：*Their great hands coming red and wet from battles to make a primrose for a child to pick.*
9. ①　`同一个春日里一道忽然的阳光将再催开同一朵水仙` → `同一个春日里，一道突如其来的阳光将再催开同一朵水仙`（[21]；「一道忽然的阳光」定语悬空）
   原：*a sudden glare of sunlight on the same spring day shall bring the same daffodil to bloom once more.*
10. ③　`其间落下的十亿年也不会被惋惜` → `而夹在中间落下的十亿年，也不会有人惋惜`（[21]；not regretted shall be the billion years 的无主被动硬搬）
    原：*and not regretted shall be the billion years that fell between.*
11. ③　`同样那些旧面孔将再被看见` → `那些同样的旧面孔都将重新出现`（[21]；shall be seen again 被动硬搬）
    原：*And the same old faces shall be seen again.*
12. ①　`而你和我将在夏天一个午后、太阳正当天顶与海面之间的正中间时，在我们从前常会面的花园里再会。` → `而你和我将在夏天的一个午后，在我们从前常会面的那座花园里再会——那时太阳正悬在天顶与海面之间。`（[21]；状语连缀错位，「正当中……的正中间」又重复一次，句子读断）
    原：*And you and I shall in a garden meet again upon an afternoon in summer when the sun stands midway between his zenith and the sea, where we met oft before.*

### tg_honour（16 条：①8 ②3 ③4 ⑥3，有互见）

1. ⑥成语　`百无聊赖的太平把那些岛笼罩` → `倦怠的太平把那些岛笼罩`（[0]；「百无聊赖」写人「闲得发慌」，listless peace 是「倦怠／没精打采的太平」）
   原：*and listless peace obscured those isles in the days before the olden time.*
2. ①　`把名字大字写在史书里` → `把名字大大地写进史书里`（[0]；writ large 直搬，「大字写」不合中文搭配）
   原：*and leave their names writ large in histories.*
3. ①③　`可它们却也肯答应人在黄昏时于灶边随口送上去的闲散祷告——那是人耕田回来的时候。` → `可它们也肯应一声闲散的祷告——黄昏时分，人耕田回来，在灶边随口念上那么几句。`（[1]；when 从句被搬成悬空的「那是…的时候」，与前面时间状语重复脱节）
   原：*but yet are apt to answer idle prayer flung up at evening near the hearth, when a man returneth from the ploughing of the fields.*
4. ②　`人喃喃的祷告都升到不理人的云里去了` → `人喃喃念出的祷告都升到不理人的云里去了`（[4]；「喃喃的祷告」定语歧义，像是祷告本身在喃喃）
   原：*The prayers that a man mutters … go up unheeded to the heedless clouds.*
5. ⑥　`说：『岛上有百姓，叫作三岛，…』` → `说：『有百姓住在叫作三岛的群岛里，…』`（[4]；There be men in the Isles called Three，被叫作「三岛」的是群岛，原译把「百姓」当了主语）
   原：*'There be men in the Isles called Three, or sometimes named by sailors the Prosperous Isles…'*
6. ⑥　`他们下面有许多小小的军队` → `他们下面是一支支小人的军队`（[6]；armies of little men 是「小人的军队」，不是「小小的军队」）
   原：*And below them there were armies of little men.*
7. ①　`在诸神脚边彼此厮杀，为诸神的荣耀互相残杀，为诸神之名的光荣。` → `在诸神脚边为诸神的荣耀彼此厮杀，为诸神之名的光荣互相残杀。`（[6]；末一分句「为诸神之名的光荣」无谓语，悬空）
   原：*they fought against each other and slew one another for the honour of the gods, and for the glory of the name of the gods.*
8. ③⑥　`谷中他们亲手辛苦筑起的城，也为诸神的荣耀被烧掉了；他们在为诸神的荣耀而死的地方死去，诸神俯视着微笑。` → `谷中他们亲手辛苦筑起的城，他们也放火烧了，为的是诸神的荣耀；就在那里，他们为诸神的荣耀而死。诸神俯视着微笑。`（[6]；原文是主动「他们烧城」，被动硬搬丢了施事，语义反转成「城被烧」；后半 where 从句照搬成「在…的地方死去」）
   原：*their cities that they had builded with the toil of their hands, they burned for the honour of the gods, where they died for the honour of the gods, and the gods looked down and smiled.*
9. ①　`而人始终在死。` → `而人一直在死。`（[6]；all the while men died，「始终在死」不成句）
   原：*and all the while men died.*
10. ①③　`随后他们回去，仍旧在丰饶群岛牧羊，自从看见诸神怎样对待人以后，对牛也温和了些。` → `随后他们回去，仍旧在丰饶群岛放牧；自从看见诸神怎样对待人，他们对自家的牛也温和了些。`（[11]；since 从句被后置成悬空状语，主谓被拆散）
    原：*and were kinder to their cattle after they had seen how that the gods used men.*
11. ①　`三岛本来还算好` → `三岛本可安然无事`（[12]；it had been well for the Islands Three 是「本可无事」，「还算好」意思走散）
    原：*Still it had been well for the Islands Three had not certain men … sought also to see the gods themselves.*
12. ②③　`看见那些在不吉利的日子找神的人的满帆白影。` → `看见一片饱满的白帆——那是些在不吉利的日子出门寻神的人。`（[12]；三个「的」压住中心语，且 the full white sails of those that… 的关系从句硬搬成前置定语）
    原：*They saw where ocean meets with sky the full white sails of those that sought the gods upon an evil day.*
13. ③　`派了六个人到有人告诉过他们的那座山去` → `派了六个人到那座听人说起过的山去`（[12]；the mountain whereof they had been told 的无主被动照搬，「有人告诉过他们」既生硬又添了一个说话人）
    原：*and sent six of their number to the mountain whereof they had been told.*
14. ②①　`只看见烧掉的城升起的烟，和立在天空里代替了应允祷告的秃鹫。` → `只看见焚毁的城中升起的烟，和天空里盘旋的秃鹫——那本该是应允了的祷告。`（[12]；vultures … instead of answered prayer 的定语套叠把意思拧成一个「代替祷告的秃鹫」，反而不可解）
    原：*but only the smoke that went upward from burned cities, and vultures that stood in the sky instead of answered prayer.*
15. ①　`三个岛，诸神各以不同的衣饰形貌现身` → `三个岛，诸神在每一座都以不同的衣饰形貌现身`（[12]；前半截「三个岛」悬空，无介词无谓语）
    原：*And to every isle of the three the gods showed themselves in different garb and guise.*
16. ①　`他们穿着兽一样的毛` → `他们披着野兽般的毛`（[14]；be clothed in hair 直搬，「穿毛」不合搭配）
    原：*gods that were clothed in hair like beasts.*

## 未改判定（读得通或属作者笔法，一律不动）

- **tg_dawn**：`chalcedony, onyx, chalcedony, onyx`（玉髓、缟玛瑙…）的复沓是原文刻意的节奏，[1]/[13] 原样保留；「于是…于是…于是」的连词复沓同属邓萨尼圣经体腔调，不改。
  「诸神」「他们」大写神称按原文大小写区分，未改小写。
  [13]`地震便跳起来，把他睡在两崖之间的洞穴甩开`——`the Earthquake` 作神名直译「地震」，承原文拟人，保留（未改作「地动之神」之类）。
  [12]`找不到什么镶红宝石、银子或蓝宝石的匣子`：原文列举本就近于荒诞（rubies, silver or sapphires），照直保留，只把「湖」改「湖泊」以免与上句「把湖变成」重复过紧。
  [6]`蝙蝠答了，却没人听见`（And though the bat answered none heard）语义含混是原文省略所致，不加解释。
- **tg_dreams**：通篇第一人称诅咒＋圣经体排比（`当诸神…那时我…`）为作者腔调，全部保留。
  [7]`像陨落的月亮一样巨大的肋骨`「白白竖起」：`stood up white` 的「白白」略显生硬，但合于本篇枯骨的白，且不致误读，不改。
  [16]`这样死寂、这样白、这样静` 三顿复沓保留。
  [20]`剩下的只是虚无`（what remained was nothing）：意译为「虚无」与篇末「诸神仍旧活着」相映，读得通，不改。
  [0]`一`、[18]`二` 为节题，源文裸罗马数字，按体例不加句末标点（check_batch 告警即此二处，豁免）。
- **tg_honour**：`为诸神的荣耀…为诸神之名的光荣` 的复沓是原作修辞（末段「为诸神的荣耀打仗」再呼应），保留。
  [1]`这些水手说的东西在我们之外`（things beyond）：`beyond` 在此近于「超出我们之上／之外」，译文取「之外」虽稍平，仍可解，按「读得通不改」放过。
  [2]`那些在三岛中可能比我们更显得高大的`：以「的」字结构收尾作名词，是本篇对白的口语腔，未动。
  [14]`额上生着爪子`（claws upon their foreheads）：意象怪异是原文所有，不修饰。