# 润色日志 — bm_c / bm_d（2026-11-26）

《光明的使者》（The Bright Messenger）第 3 片、第 4 片，`work_batch_20261124/`。
脚本 `_polish_20261126_bm_cd.py`；备份 `<key>_zh.json.bak_20261126`（改前）。

## 〇、对齐说明（与 README §二 的偏差）

`paras_tool.py show` 报 **offset = 0**，非 README 所说的 1：
`_bm_c_paras.json` = 170 段、`bm_c_zh.json` = 170 段；`_bm_d_paras.json` = 186、`bm_d_zh.json` = 186。
两个源文件**不含篇名项**（`src[0]` 即正文第一段「Fillery, I tell you--really I love the fellow…」/「Yes, keep it down a bit…」），
故 `src[i] ↔ zh[i]` 一一对应，无一处分段错位。未增删任何段。

## 一、自检

| 篇 | 段数（改前=改后） | 汉字（改后） | 改动数 | 换行符 | 备份 |
|---|---|---|---|---|---|
| bm_c | 170 = 170 | 14174 | 28 条（27 段；[135] 两处） | LF | bm_c_zh.json.bak_20261126 |
| bm_d | 186 = 186 | 13007 | 20 条（20 段） | LF | bm_d_zh.json.bak_20261126 |

分类：bm_c — ①读不通 13 ③外语句法 6 ⑤专名 1 ⑥硬伤 8；bm_d — ①读不通 5 ②「的」堆叠 2 ③外语句法 4 ⑤专名 3 ⑥硬伤 6。

机械自检（两篇同跑，全部通过）：

| 项 | bm_c | bm_d |
|---|---|---|
| JSON 可解析、长度=备份 | ✓ 170 | ✓ 186 |
| 空段 | 0 | 0 |
| ASCII 直引号 `"` / 撇号 `'` | 0 / 0 | 0 / 0 |
| 「」配对（段内亦闭合） | 175/175 | 216/216 |
| 『』配对（段内亦闭合） | 23/23 | 6/6 |
| 重复标点（。。，，、；；：：！！？？） | 0 | 0 |
| 汉字＋空格＋小写英文＋空格＋汉字 | 0 | 0 |
| 汉字接半角标点 | 0 | 0 |
| `⟦⟧` 残留 | 0 | 0 |
| 段末标点（含星号行豁免） | 0 异常 | 0 异常 |
| `\n` 分行（诗行）未动 | ✓ | ✓ |
| 落盘可复现（从备份重跑＝现文件，逐字节） | ✓ | ✓ |

复现测试：把备份盖回后重跑脚本，两篇输出与现文件**逐字节相同**（含 `}\n]\n` 收尾），`ast.parse` 自查通过。

## 二、改动清单

### bm_c（28 条 / 27 段）

| 段 | 类 | 旧句 → 新句 | 理由 | 英文原文 |
|---|---|---|---|---|
| 2 | ③ | 落在两人之间的沉默，是德文汉姆先打破的。→ 沉默落在两人之间，德文汉姆先打破了它。 | 关系从句后置＋「是……的」判断句硬搬，主语悬空 | Devonham was the first to break the silence that had fallen between them. |
| 4 | ① | 本无意挑战，手套却已经掷下了。→ 他本无意挑战，可手套已经掷下了。 | 缺主语；「本无意挑战」悬空 | No challenge was intended, yet the glove was flung. |
| 18 | ① | 同样的意义无形地拖着尾迹，穿过空气。→ 同一重意义无形地拖在它后面，横过空中。 | 「拖着尾迹」主语不明、动宾失配 | the same freight of meaning trailing behind it invisibly across the air. |
| 19 | ① | 看上去却叫人难受地像个巡场员 → 看上去却偏偏活像个巡场员，叫人看了难受 | 「难受地像……」状语位置不合汉语 | looked painfully like a shopwalker. |
| 30 | ① | 最精纯的本事，你自己刚才说的，你最好的本事。→ 最精纯的本事——用你自己的话说，你最好的本事。 | 插入语被直搬成并列，句子断裂 | your finest skill, your very best, as you said yourself just now. |
| 36 | ⑥ | 思想家们在屋顶上大声疾呼 → 思想家们到处大声疾呼 | cry on the housetops 是「到处宣称」，非字面爬屋顶 | The thinkers were crying on the housetops that progress was a myth… |
| 44 | ⑤ | 压制「N. H.」，使『莱斯特』成为永久。→ 压制「N. H.」，让「莱斯特」成为永久状态。 | 同句两个术语一「」一『』，体例不一；「成为永久」缺中心语 | the suppression of "N. H." and the making permanent of "LeVallon." |
| 49 | ① | 某处高山的令人振奋。→ 还有某处远山顶上的那股令人振奋。 | 「的」后无中心语，句子没落地 | the exhilaration of some distant mountain-top. |
| 50 | ① | 那张奇异而野性的脸上，皮肤上带着幸福与安宁 → 那张奇异而野性的脸上带着幸福与安宁 | 「上……上」重复，主谓被切断 | The strange, wild face wore happiness and peace upon its skin… |
| 57 | ① | 那些书上，讲浅近物理、博物学和天文学的书。→ 书上，那些书讲浅近物理、博物学与天文学。 | 同位语挂在「上」后，宾语重复不成句 | over the books … , books on simple physics, natural history and astronomy. |
| 65 | ① | 「我是双的。」→「我觉得自己是双重的。」 | doubled 直译为「双的」，判断句读不通 | I feel"—he used an odd word—"doubled." |
| 67 | ③ | 眼里露出一种努力让思绪跟去别处的神情 → 眼里透出一种神情，仿佛正努力随思绪跟到别处去 | 英语动词性定语硬塞进「的」字结构 | his eyes betraying an effort to follow thought elsewhere. |
| 70 | ⑥ | 莱斯特是一条手臂、一肢体、一根触须 → 莱斯特是一条手臂、一条肢体、一根触须 | 量词脱落 | LeVallon was an arm, a limb, a feeler… |
| 72 | ⑥ | 他儿时的疑问又刺耳地穿过空气 → 他儿时的疑问又猛地穿过空气 | crashing＝轰然撞出，非「刺耳」 | His childish question went crashing through the air. |
| 74 | ① | 一座花开满谷、日光与风的高加索山谷 → 一座开满花、有日光与风的高加索山谷 | 「花开满谷」与「日光与风」并列不通 | a flowering Caucasian vale of sun and wind. |
| 75 | ③ | 东方的文学与传说把各种元素都住满了有意识的生命 → ……让各种元素里都住满了有意识的生命 | peopled the elements with 的施受关系读反 | peopled the elements with conscious life. |
| 76 | ③ | 它们那被更庞大的意识所居的巨型『身体』，充满了空旷的太空 → 它们那些住着更庞大意识的巨型『身体』，栖居在空旷的太空中 | 被动硬搬（「被……所居」）＋ people 误读为「充满」 | whose gigantic "bodies," inhabited by immenser consciousness, people empty space. |
| 78 | ③ | 「这星球年轻而美丽的无知，所产生的……观念啊！」→「这星球在年轻美好的蒙昧时代所产生的……观念啊！」 | 抽象名词主语＋「的」字定语直搬，句子没了主语 | Delightful, picturesque conceptions of the planet's young, fair ignorance! |
| 94 | ③ | 他们应该被听见。→ 别人该听得见他们才是。 | ought to be heard 被动硬搬 | They ought to be heard. |
| 97 | ① | ……这是回答。→ ……他这样答道。 | 「这是回答」为 was the reply 的死译，无人称 | "…," was the reply. |
| 104 | ⑥ | 「莱斯特才是真正真实的自我。→「莱斯特才是真正的自我。 | 「真正真实」叠义 | "LeVallon is the real true self. |
| 135 | ⑥ | 是他们所说的『二十二号』→ 按他们的说法，是二十二岁 | 22 是年龄（下段「二十二岁以前」可证），非编号 | The body I'm in and using is 22, as they call it… |
| 135 | ① | 我这具身体，身体自己嫌它累赘 → 我这具身体嫌这些东西累赘 | 「身体」重复作主语，句子绕住 | my body, which it irks, is covered with wool and cloth and stuff… |
| 136 | ⑥ | 二十二号以前的事 → 二十二岁以前的事 | 同上，年龄误作编号 | Before 22 I remember nothing… |
| 137 | ⑥ | 他们把它叫作护士和修女。→ 他们管它叫护士和护士长。 | 医院里的 sister＝护士长，作「修女」误读 | They called it nurse and sister. |
| 139 | ⑥ | 我情愿地向它呼气 → 我甘愿地向它呼气 | 「情愿地」不成状语 | I breathed upon it willingly. |
| 144 | ① | 却并不是优雅而邀约的那种 → 却没有半分优雅，也不是在邀我 | yet not with grace and invitation 直搬成「那种」，指代落空 | The figure seemed to spit at me, yet not with grace and invitation. |
| 159 | ① | 带着相当愉快的脸盯着看 → 带着相当愉快的神色盯着我看 | 「愉快的脸」搭配不成立 | staring with quite pleasant faces. |

### bm_d（20 条）

| 段 | 类 | 旧句 → 新句 | 理由 | 英文原文 |
|---|---|---|---|---|
| 4 | ③ | 他的手是活的，至少；尽管在我手里…… → 他的手是活的，至少是这样；尽管握在我手里…… | at any rate 的插入语被硬塞在「至少」后，句子断气 | His hand was alive, at any rate, although within my own it felt rather like a dying branch… |
| 12 | ① | 因为这名字触到我一种失落了伙伴的感觉，而我是想要这伙伴的 → 因为这名字让我触到一种失去同伴的感觉，而这同伴是我想要的 | 「触到我一种……的感觉」动宾套叠 | the name touched me with a sense of lost companionship I wanted. |
| 14 | ⑥ | 我往后一沉，闷气的枕头托着我 → 我往后一沉，靠在闷热不透气的枕头上 | stuffy 是「不通风」，非「闷气（生闷气）」 | I sank back comforted upon the stuffy pillows… |
| 18 | ① | 我真正的记忆覆盖整个行星，这点小事要记新鲜，不算什么。→ 在我真正的记忆覆盖整个行星的时候，这点小事要记清，算不得什么。 | when 从句被删，两个分句失去逻辑关系 | It was a small detail to keep fresh when my real memory covered the whole planet. |
| 47 | ⑤ | 「那些秀丽的？」→「那些秀丽者？」 | 本篇术语是「秀丽者」（8 处），此处走失 | "The comely ones?" |
| 51 | ⑤ | 只有秀丽的人们，以及…… → 只有那些秀丽者，以及…… | 同上，术语归一 | Only the Comely Ones … made me want to sing. |
| 56 | ⑤ | 「那秀丽的人们呢？」→「那秀丽者呢？」 | 同上 | "And the Comely Ones?" |
| 67 | ① | 我又看见她那银大理石子般的小牙。→ 我又看见她那银大理石似的小牙。 | 「银大理石子般」多一层「子」，比喻读不通 | her small teeth of silvery marble. |
| 70 | ② | 我的朋友，那懂事的一位，我那位已死的伟大朋友梅森的同伴，也出了房间。→ 我的朋友也出了房间；他是那位懂事的人，是我那已死的伟大朋友梅森的同伴。 | 四层「的」＋连续同位语把中心语压没 | My friend, the understanding one, companion of my big friend, Mason, who was dead, also had left the room. |
| 82 | ⑥ | 这遗忘，确实是撞得我头晕的一道界限 → 这遗忘确实是我一再撞上去的一道界限 | the limits against which I bang myself，「头晕」为增字 | one of the limits against which I bang myself. |
| 85 | ③ | 后者虽然巨大华美，自有其种 → 后者虽是同类中的巨大华美者 | splendid of their kind 的 of 结构直搬 | though huge and splendid of their kind. |
| 115 | ① | 虽然他靠着我们工作的成果，凡维持他、制约他的一切都是。→ 虽然凡维持他、制约他的一切，他都得益于我们的工作。 | 后半句悬空，谓语缺失 | although he benefited by our work in all that sustained and conditioned him. |
| 116 | ⑥ | 把我的手握得更牢、更宽 → 把我的手握得更牢、更宽厚 | broader grip 指握法宽厚，非「更宽」 | He took a firmer, broader grip of my hand… |
| 138 | ③ | 从一个她刚在恰恰正好的时刻离开的伦敦大城的某一点——那时刻算准了让她稍后与他自己的路径相交。→ 从一个伦敦大城中的某一点——她离开的时刻恰好算准了，让她稍后与他的路线相交。 | 两层关系从句嵌套直搬，读者要倒着解 | from a point in great London town which she had left just at the precise moment which would time her crossing his own path later. |
| 159 | ② | 使她觉察到她秘密的力量，她对付男人时那力量的中央源头。→ 使他觉察到她隐秘的力量，那力量在她对付男人时自有中心的源头。 | 连续「的」字同位语＋代词「她」指代滑动 | he was aware of her secret power, her central source of strength in dealing with men. |
| 161 | ① | 而这又在那块幕上闪出那奇异明亮的身影 → 而这山谷又在他脑中的幕布上闪出那个奇异明亮的身影 | 「这」指代不明（山谷？话？），画面无着落 | and this, again, flashed upon the screen the strange bright figure… |
| 165 | ⑥ | 苍白的阳光照在她身旁的脸上，使它发亮 → 苍白的阳光照着他身旁她的脸，使它发亮 | her face beside him 的主客关系读反 | The pale sunlight caught her face beside him and made it shine. |
| 167 | ③ | 她的眼睛像星星一样淡入某个非人间的春天的远处 → 她的眼睛像星星一样，消隐在某个非人间的春天的远处 | faded into 误用电影术语「淡入」，方向相反 | her eyes faded like stars into the distance of some unearthly spring. |
| 170 | ⑥ | 他嘴边的脸一时间变得严峻。→ 他脸上一时变得严峻，嘴也绷紧了。 | grew stern … about the mouth 的 about 误读成「嘴边的脸」 | His face grew stern a moment about the mouth. |
| 182 | ⑥ | 这简单的提议背后，藏着这些不同的动机、情绪和保留的线头。→ ……缠着这些各不相同的动机、情绪与保留。 | 「藏着……线头」喻体错杂，qualification 作「保留」 | Behind the simple proposal lay these various threads of motive, emotion and qualification. |

## 三、未改判定（读得通但不漂亮，一律不动）

**bm_c**

- [1]「随即把这口气掩了下去」——smothering it 的直译，可通，保留。
- [5]「「这是个，」他平静地说，「既可悲又令人振奋的病例。」——断句照原文，说话人标签体例不动。
- [14]「那段记忆其实就只压在表层之下」——lies just beneath the surface only 语义偏松，可读，不改。
- [33] 叙述段用『』标机构名与『病例』：本篇体例是「对白『』作嵌套、叙述中术语用『』」（[14]『半在』、[24]『特殊能力』、[76]『身体』、[118]『法则』、[130]『游走的视觉』同），自洽；「N. H.」在叙述中作「」是 bm_g/bm_h/bm_j 的既有判例，两制并存留待全稿合并统一。
- [40]「＊　＊　＊　＊　＊」星号行（全角间隔）保留。
- [55] 长定语「一个身怀巨大能量却懒于动用的印象」——原文即一长句，读得通，不改。
- [72]「交出了它的死者」——gave up its dead 的圣经典故直译，保留。
- [101]「没有任何一个……显不出来的东西」——双重否定照原文，不改。
- [155]–[159] 看守口语（ain't / Lunies / Guv'nor）作「是不是／疯子／老板」，口语腔刻意，不动。
- [166]「一号」首见即定名，与 [168] 一致，不回改为「最先开口的那个」。
- [169] 两处「要是你不介意」系原文 if you don't object / if you don't mind 的复沓，保留。

专名核对（bm_c）：菲利里 44 / 德文汉姆 28 / 莱斯特 29 / 梅森 6，全篇一致，与 bm_a…bm_n 及用户现定「菲利里」相符；「N. H.」保留原文形。

**bm_d**

- [22]「人家叫他菲利里医生。」独立成句照原文同位语，属「N. H.」第一人称异质叙述腔，保留。
- [25]「「你当然是的。」」略含糊（Of course, you do），可通，不改。
- [35]「「那是小孩子的，」」与 [36]「「孩子气的，」」呼应，保留。
- [62][106][108][110][115][117] 外层「」为菲利里诵读、内层『』为纸上文字，嵌套无误，未动；引文段末「」』」闭合方式保留。
- [126] 叙述中术语作「莱斯特」「病例」（「」），与全篇一致。
- [158][160][178] the Firm 作「这一行／合伙人」：本片三处自洽，bm_j 作「事务所」，属跨片用词，留待全稿合并统一。
- [133] 长句照原文，可读，不改。
- [147] 萨克岛（Sark）、[167] 圣邓斯坦（St. Dunstan's）为通行译名，保留。

专名核对（bm_d）：菲利里 18 / 德文汉姆 7 / 莱斯特 9 / 梅森 5；「秀丽者」经本次归一后 11 处，余「秀丽的身影」「所有人都秀丽」为形容词用法，不属术语。