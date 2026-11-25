# 润色日志 · eh_empty（2026-11-26）

篇：E. F. Benson,《The Empty House》·`work_batch_20261124/eh_empty_zh.json`
原文：`_eh_empty_paras.json`（114 段；**本篇 src 数组不含篇名**，故 offset＝0，`zh[i]` 直接对应 `src[i]`，非说明书的 offset＝1）
落盘脚本：`_polish_20261126_eh_empty.py`　备份：`eh_empty_zh.json.bak_20261126`（未覆盖 20261125 的旧备份）

## 自检

| 项目 | 结果 |
|---|---|
| 段数 | 114（改前＝改后） |
| 汉字 | 8775 → 8791 |
| 改动 | 43 条（①16 ②3 ③5 ⑤3 ⑥14 ⑦2） |
| 换行符 | LF（原文件即 LF，indent=1，照原样写回） |
| `check_batch.py eh_empty` | `checked 1, with problems 0, paras 114, han 8791` |
| 无空段 / 无 ASCII 直引号 / 无重复标点 / 长度不变 | ✓ |

## 改动清单（段号为 0 基，`zh` 数组下标）

### ①读不通（16）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 6 | 谜底就揭开了：暮色中他们沿海滨慢慢走着，她挨近他身边。 | 谜底就揭开了。暮色中两人沿海滨慢慢走着，她挨到他身边来。 | 「when」从句被搬成句尾悬空短语，主句没了落点 | The revelation was made soon after tea, when she sidled close up to him as they paced slowly along the sea-front in the dusk. |
| 10 | 她声音和神气里有种东西 | 她的声音和神气里有种东西 | 缺定语标记，「她声音」易读作并列 | Something in her voice and manner thrilled him. |
| 15 | 可跟你一起去，我会觉得其乐无穷 | 不过跟你在一起，我会觉得其乐无穷 | 一句里两个「可」，转折信号打架 | but with you I should enjoy it immensely |
| 27 | 并不冒充别的什么 | 并不自命不凡 | `had no pretensions to being other than…` 误读为「冒充」 | Shorthouse had no pretensions to being other than a very ordinary young man |
| 30 | 看清了房子侧面那个名字 | 看清了房子侧面标着的街名 | 「名字」在汉语里指人，指物须点明是街名牌 | looked up at the name on the side of the house |
| 54 | 仿佛都隔着面纱似的眼睛看着他们 | 仿佛都用蒙了面纱的眼睛看着他们 | 「隔着面纱似的眼睛」定语错挂 | watching them, as it were, with veiled eyes |
| 61 | 挡着路的，是一个女人的身影。 | 挡着路的，站着一个女人的身影。 | 判断句套悬空定语，画面立不起来；改存现句 | stood the figure of a woman |
| 75 | 近得他嘴唇几乎能碰到。 | 近得他的嘴唇几乎能碰上去。 | 「能碰到」缺宾语，句子断了 | so close to his own that he could almost have touched it with his lips |
| 77 | 肖特豪斯不由得低低叫了一声，在姑妈以全身重量扑上来的一刻真正的、控制不住的恐惧里，他差点失去平衡。 | 肖特豪斯不由得低低叫了一声；有一刻姑妈真个控制不住恐惧，以全身的重量吊在他身上，他差点失去平衡。 | 「在……恐惧里」悬空，主语两次重启 | nearly losing his balance as his aunt clung to him with her whole weight in one moment of real, uncontrollable terror |
| 77 | 幸而她什么也没看见……所以她几乎立刻就恢复了控制 | （删「所以」）她几乎立刻就恢复了控制 | 「幸而…所以」连词叠用，逻辑错挂 | Fortunately, however, she had seen nothing… for her control returned almost at once |
| 79 | 他立刻压下听来的那些……故事 | 他立刻把听来的那些……故事压到脑后 | 「压下故事」搭配不成，`suppressed the memory of` 是「不去想」 | He at once suppressed the memory of stories he had heard |
| 87 | 真正恐惧的可能有了新的可怕含义 | 真正恐惧起来的可能，有了新的可怕含义 | 「恐惧的可能」歧义（可能＝也许） | the possibility of real fear took on a new and terrible meaning |
| 90 | 那些破家具、低顶棚、窄窗子的地方 | 那些破家具、低顶棚、窄窗子的小屋子 | 「的地方」中心语错配，回指不清 | those horrid gloomy little servants' rooms with their bits of broken furniture, low ceilings, and cramped windows |
| 109 | 然后到楼梯平台上的，是一个人的脚步——沉甸甸地走着。 | 然后一个人的脚步走到楼梯平台上——沉甸甸地踏着。 | 主谓在句末才拼上，「是一个人的脚步」作主语不成话 | then out on to the landing came the step—of a single person treading weightily |
| 110 | 随之一声沉闷的撞击，在下面房子深处——门厅的石板地上。 | 随之一声沉闷的撞击，从下面房子深处传来——是门厅的石板地上。 | 破折号后剩一个无谓语的介词短语 | a dull, crashing thud in the depths of the house below—on the stone floor of the hall |

（另：42 段「他们站在一条宽阔的门厅里；左边是……饭厅敞着的门」→「一间……左边是宽敞饭厅洞开的门」，兼②与⑦，计入⑦。）

### ②「的」字堆叠（3）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 44 | 他的声音的回声 | 他话音的回声 | 「的」连环，且「声音的回声」同义 | The echoes of his voice |
| 92 | 把她轮廓分明的脸在白墙前衬得格外分明 | 衬得格外触目 | 一句两「分明」 | threw her strongly-marked face into vivid relief |
| 93 | 因为那种压倒一切的恐惧的可怕印记，明明白白写在…… | 因为压倒一切的恐惧，其可怕的印记明明白白写在…… | 三个「的」把「印记」压没 | the dreadful signature of overmastering fear was written plainly in that utter vacancy of the girlish face |

### ③外语句法直搬（5）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 0 | 散发出一种隐秘而邪恶的念头的气氛 | 散发出一种气息，里头藏着隐秘而邪恶的念头 | `an atmosphere of secret and wicked thoughts` 硬搬成「念头的气氛」 | communicate an atmosphere of secret and wicked thoughts |
| 5 | 就接上了她那种电流般状态的头一波 | 就感到了她那股电流般兴奋的头一波 | `electrical condition` 直译成「电流般状态」 | caught the first wave of her electrical condition |
| 63 | 声音听着像别人的，且只一半受着控制 | 而且只勉强压得住 | `was only half under control` 被动硬搬 | a voice that sounded like someone else's and was only half under control |
| 75 | 那是一张被激情扭动的脸 | 那是一张因激情而抽搐的脸 | `a face working with passion` 无被动义，硬搬成「被…扭动」 | a face working with passion |
| 75 | 可在他看见的时候，那张脸因强烈而带攻击性的情绪而活了起来 | 可在他看见的那一刻，它被强烈而咄咄逼人的情绪激得活了起来 | 「因…而…而…」两「而」连着，句法照搬 | but as he saw it, alive with intense, aggressive emotion |

### ⑤专名／术语一致（3）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 9 | 广场上那栋凶宅 | 广场上那座凶宅 | 全篇「座」为多数（2、3、33 段），「栋」为孤例 | the haunted house in the square |
| 71 | 有人在后厅里正对着他 | 有人在后客厅里正对着他 | 同段上文作「前后客厅」，此处简称跳字 | someone facing him in the back room |
| 82 | 他们走进三楼楼梯口 | 他们走进四楼楼梯口 | 本篇自 33、67 段起按英制计层（first floor＝二楼），故 third floor＝四楼；且 111 段「三段楼梯」正好落到四楼 | a small room on the third floor |

### ⑥硬伤（14）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 4 | 这在镇上简直成了丑闻 | 这在镇上简直不亚于一桩丑闻 | `little less than a scandal`＝不亚于，非「成了」 | was indeed little less than a scandal in the town |
| 33 | 墙上有雨水留下的痕 | 墙上有雨水留下的水痕 | 缺字 | weather streaks in the wall |
| 34 | 被胳膊上那份沉甸甸的重量拖累 | 被胳膊上那份始终不松的重量牵累 | 「沉甸甸的重量」同义反复，且丢掉 `steady` | hampered by the steady weight on his arm |
| 59 | 一股冷湿的气迎面扑来 | 一股冷湿的空气迎面扑来 | 缺字，「一股气」不成词 | a cold, damp air meeting them in the face |
| 60 | 发出一声尖利的叫 | 发出一声尖利的叫声 | 缺字 | uttered a piercing scream |
| 61 | 白得像死 | 白得像死人 | 缺「人」；94 段同改，两处统一 | white as death |
| 68 | 他们往上走了不到十几级 | 他们还没走上十来级 | `not more than a dozen` 被读成「不到十几级」，数目反转 | They had not gone up more than a dozen steps |
| 81 | 衰老的床架 | 朽坏的床架 | `decrepit` 指器物朽坏，不指「衰老」 | decrepit bedsteads |
| 88 | 听清房子里深处 | 听清房子深处 | 多一「里」 | in the depths of the house |
| 93 | 那竟能字字为真 | 那竟会是真的 | 「字字」只用于文字；`literally true` 说的是脸 | that it could be literally true |
| 93 | 而当他觉出她凝注的目光、见她转过脸来看他时 | 而当他觉出自己目光逼人、见她转过脸来看他时 | `feeling his intense gaze` 主语看反：凝注的是他，不是姑妈 | feeling his intense gaze |
| 94 | 虽然脸白得像死 | 虽然脸白得像死人 | 同上，与 61 段统一 | though the face was deathly white |
| 102 | 让那一大杯烈酒见效 | 让那一大剂烈酒见效 | 100 段是「一杯」，`tremendous dose` 指浓度不是容量 | the tremendous dose of spirits |
| 107 | 闯进这空楼午夜般的寂静 | 闯进这空楼里午夜的寂静 | 「午夜般的寂静」反读：寂静是午夜的，不是「像午夜」 | breaking in upon the midnight silence of the empty building |

### ⑦体例（2）

| 段 | 旧 | 新 | 理由 | 原文 |
|---|---|---|---|---|
| 2 | 它既不孤零零的，也不邋遢。 | 它既不孤零零，也不邋遢。 | 状语误加「的」 | It was neither lonely nor unkempt. |
| 42 | 站在一条宽阔的门厅里；左边是一间宽敞饭厅敞着的门 | 站在一间宽阔的门厅里；左边是宽敞饭厅洞开的门 | 「门厅」量词用「间」；两「敞」叠用 | They were standing in a wide hall-way; on their left was the open door of a spacious dining-room |

## 未改判定（读得通但不漂亮，按准则不动）

- **0 段**「不知怎的一眼就把自己为恶的本性宣告出来」——略生硬，但「为恶的本性」对应 `character for evil` 准确，不动。
- **0 段**「他们的存在根本有什么地方不对头：他们是恶的」——连用两个冒号，属作者层层递进的顿挫，保留。
- **1 段**「某座屋顶下犯下的恶行所留的那股气味，在真正动手的人早已故去多年之后，仍叫人生出……」——长句有英语味，但语法完整、气息也对，不动。
- **28 段**「借着那说不清名目的内心过程……积起一份控制力的储备；这过程难以描述」——插入语稍绕，可读，不动。
- **29 段**「他低头瞥了一眼她那斯芬克斯般的面孔，想到在真正的恐惧猛然袭来时这张脸未必会好看」——「未必会好看」比原文直白，但未失义，不动。
- **37 段**「碰到的只是空气」（`met nothing more solid than air`）——未照「再没有比空气更实」的否定式搬，译得通，不动。
- **45 段**「咱们得弄清楚没人藏着」——口语腔成立，不动。
- **59 段**「一间比一间更不招人待见」——口语化但与前句「一间比一间冷」的排比相配，不动。
- **83 段**「他在这里比在房子任何别的地方都更觉得自己不像是自己的主人」——「不像是自己的主人」略滞，但结构无误，不动。
- **100 段**「再不动也不行了」——作者刻意短句，不动。
- **112 段**「它便落在后面／它便赶上来」——`IT` 大写代词保持「它」并前后一致，属作者刻意的非人称，不动。
- 全篇对白一律「」、省略（无）、破折号「——」，段末标点齐全，无一处 ASCII 直引号；诗行无（本篇无分行段），故不涉分行豁免。
- 「肖特豪斯／朱莉娅姑妈／马夫／洗碗间／碗橱」等专名与职衔全篇自洽（「马夫」对应 19 段 `stableman` 与 82 段 `groom`，同指一人，统一作「马夫」）。