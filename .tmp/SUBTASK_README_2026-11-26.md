# work_pub 分册「逐片」润色说明（2026-11-26 起）

你在给 `work_pub/<book>` 的**一「片」**做逐段通读润色。项目根 `E:/Translate`（Windows；用 `python`，
`python3` 是空壳）。

## 一、先读

1. `E:/Translate/POLISH_BRIEF_2026-11-25.md` —— 作业准则与红线。
2. 本文件。

## 二、一片是什么

- 一片 = `work_pub/<book>/out/<chapter>/<piece>/final.txt`，**一行一段、段间空一行**。
- 德/英文原文 = `work_pub/<book>/chunks/<chapter>.json` 里 `chunks[k]` 这一组，
  k = piece 目录序号（`c07` → 第 7 组）。组内 `type=="p"` 的项就是它对应的段落，**顺序一一对应**。
- 全部用工具看，不要自己写解析：
  ```bash
  python work_pub/piece_tool.py show   <book> <chapter> <piece>   # 德/英原文与中文逐段对照
  python work_pub/piece_tool.py backup <book> <chapter> <piece>   # 建 final.txt.bak_20261126
  ```

## 三、只改这七类（与普鲁斯特那轮同口径）

①读不通（语法断裂、主谓失配、悬空修饰语、缺主语的流水句）
②「的」字定语堆叠（三个以上「的」把中心语压没）
③外语句法直搬（关系从句后置、被动式硬搬、`nicht…sondern` / `not…but` 机械照搬、
  德语框形结构（动词被推到句末）照搬、独立分词短语被搬成让步句）
④代词指代不明（一段里两个「他/她」指不同人；德语 `er/sie/es` 的性数线索在汉语里会丢）
⑤专名/术语/职衔不一致（**以本册出现最多者为 canon**；平票时取通行汉译并说明）
⑥硬伤（词义误读、否定反转、量词错、错别字、成语误用、时态与体读反）
⑦体例（段末标点齐全、引号全册一致、省略号「……」、破折号「——」、数字与西文前后不加空格）

**不动**：作者刻意的长句、排比、复沓、方言、诗句分行、说话人标签体例、章名、脚注锚点、`⟦i⟧`。
不重译、不改情节、不删减、不加解释。读得通但不漂亮的地方一律不改，只在日志里记「未改判定」。

## 四、各册特别提示

- **prozess（卡夫卡《诉讼》，德语）**：卡夫卡的长句是「公文式」的——从句套从句、动词最后落地。
  汉语要保住这个拖沓感，但不许让它断句。常见病是「关系从句后置直搬」与「被动式硬搬」
  （`wurde verhaftet`）。人名统一：约瑟夫·K.／格鲁巴赫太太／布尔斯特纳小姐／弗兰茨／威廉／
  监察官／拉本施泰纳／库利希／卡米纳／毕斯特纳（注意别与「布尔斯特纳」混）。
- **malte（里尔克《马尔特手记》，德语）**：第一人称、现在时、句子极长，感官细节密度高。
  常见病是「的」字堆叠与把 `wie` 从句读成因果。
- **faust（歌德《浮士德》第一部，德语韵文）**：**诗句分行必须保持**（`final.txt` 里一行一行，
  不许并成散文）。诗行可以润字，不可改行数、不可改韵脚位置。角色名用「浮士德／梅菲斯特／
  玛加蕾特」。
- **neuegedichte（里尔克《Neue Gedichte》，德语韵文；**不是**海涅）**：同上，行数不可动；
  里尔克的「物诗」（Dinggedicht）把判断压在一个动作或一个物件的转折上，落点常在末行，
  不许把末行并进上一行。诗题照原文（`FRÜHER APOLLO`／`ERANNA AN SAPPHO`／`ABISAG`）。

## 五、落盘铁律

- 先 `python work_pub/piece_tool.py backup <book> <chapter> <piece>`；已存在备份**不要覆盖**。
- 只允许「定位唯一子串 → 替换 → `assert text.count(old) == 1`」，**不许整文件重写**。
- 读写 `open(..., encoding='utf-8', newline='')`，保持原换行符与空行结构；**段数不变**。
- 脚本放 `work_pub/<book>/_polish_20261126_<chapter>_<piece>.py`，
  结尾 `ast.parse(open(__file__, encoding='utf-8').read())` 自查，并打印改动条数与行数校验。
- 改完跑：
  ```bash
  python work_proust/verify_polish.py work_pub/<book>/out/<chapter>/<piece>
  ```
  该脚本默认找 `final.txt.bak_20261125`；若你的备份是 `bak_20261126`，先
  `cp final.txt.bak_20261126 final.txt.bak_20261125`（仅当后者不存在时）再跑。

## 六、交回什么

1. 已改的 `final.txt` + 备份；
2. 脚本；
3. 日志 `work_pub/<book>/POLISH_LOG_2026-11-26_<chapter>_<piece>.md`：
   「自检」表（片 / 段数改前后 / 行数 / 汉字 / 改动数 / 换行符）＋「改动清单」
   （类别①–⑦ + 旧句 → 新句 + 一句理由 + 德/英原文）＋「未改判定」；
4. 汇报：按 POLISH_BRIEF 第四节格式，附 verify_polish 输出行。

## 七、判例（前几轮踩过的）

- 德语 `nicht…sondern`＝「不是…而是」；`nur`／`erst`／`kaum` 是最常被吞掉的限制词。
- 德语框形结构：句末的动词不能丢，也不能提得太早把状语串断。
- 有「被」不一定真有被动；`wurde` 也可表状态变化。
- 说话人标签塞进引号属⑦：改为「“……，”他说，“……”」。
- 本书对白体：**沿用该书既有体例**（work_pub 多册用「“”」），不要中途换制。