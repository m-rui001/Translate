"""Translation brief for the independent Proust version (all seven volumes).

Two principles, in this order:

1. **The result has to read well.** "Fidelity" is not a defence for a sentence no
   Chinese reader can follow. Where a faithfully long Chinese sentence reads
   smoothly, keep it; where it does not, restructure or divide it. Zhou Kexi
   himself divides Proust's sentences when Chinese requires it — that is ordinary
   craft, not concession. What must never happen is losing the *movement* of the
   thought: the qualifications, the second thoughts, the aside, the delayed verb.
   Sentence count is not sacred; the order of the ideas is.

2. **Register follows context, not a rule.** Proust moves within a page from
   salon comedy to a deathbed, from a child's bedtime to a meditation on memory.
   The brief therefore gives no global tone. It tells the writer to read the
   passage, decide what it is doing, and match it — comedy paced to its punchline,
   grief allowed to slow down, society dialogue carrying its own posturing.

Nothing here is calibrated against an existing Chinese translation. Names come
from `names_proust.py`; the reviewer checks meaning, not style.
"""

STYLE = """
【项目】把马塞尔·普鲁斯特《追忆似水年华》全七卷法文原文译成中文。
这是一部独立完整的译本，不与任何既有中译本衔接，也不模仿任何既有中译本的文风。

【最高准则：整体效果】
译文的成败不看某一句是否"忠实"到字面，而看整段读下来，中文读者是否读懂了、
读进去了、并且感受到了原文的力量。所有具体规定都要服从这一条。

一、句子怎么断，由中文决定
1. 原文的长句，中文能不能一口气读完？
   - 能，就保留长句。普鲁斯特的思绪常常是一口气下来的，断了反而走味。
   - 不能，就断开、重排、拆成两句——**这是正当的译法，不是偷懒**。
     判断标准是读者：一个受过教育的中国读者，读一遍能否抓住主干，
     读两遍能否感到层次。做不到就改，不要用"保留原句结构"当借口。
2. 无论断不断句，必须保住的是**思绪的次序和层次**：
   让步、保留、转念、补充、举例、自我修正——这些必须都在，顺序不能乱。
   可以把一个长句拆成三个中文短句，但不能把三层意思压成一层。
3. 避免两种相反的毛病：
   - 拆得太碎：原文一个完整的思绪被切成一串等长短句，读起来像电报。
   - 黏得太死：为保留从句而堆出"的"字套"的"字、主语悬空、
     读到句末已经忘了开头是什么。这种长句是失败，不是忠实。
4. 中文的句子靠动词走。如果一个句子里全是名词和"的"，没有动作，
   就重写它——把名词还原成动作。
5. 不用"对于……来说""关于……的问题""由于……的原因""进行……的处理"
   这类欧化套壳；不滥用"被"字；不把主语一路省略到读者迷路。

二、语气：看这一段在做什么
不要用同一种腔调译全书。动笔前先判断这一段是什么：
1. **童年与家庭**（贡布雷、母亲的吻、外祖母）——温软，慢，
   细节密，允许一点孩子的执拗和委屈。
2. **社交界**（盖尔芒特府、韦尔迪兰家的沙龙）——机锋藏在礼节里。
   贵族的刻薄是客客气气地让人下不来台，译出来要让人读着发凉或发笑；
   布尔乔亚的附庸风雅要显得笨拙可笑，不要替他们遮丑。
3. **爱情与嫉妒**（阿尔贝蒂娜）——偏执、反复、自我折磨。
   句子可以绕，因为他的心思就在绕；但绕的必须是痛，不是语法。
4. **病与死**（外祖母之死）——收住。这时候不要修辞，越平越重。
5. **沉思**（记忆、时间、艺术、音乐）——允许句子长、抽象、层层推进，
   但每一层都要落地，不能变成一串空洞的大词。
6. **讽刺与幽默**——一定要译出笑点。原文在开玩笑的地方，
   译文读起来不好笑，就是没译对。
段落之间语气会切换，跟着它切换。

三、用词
1. 现代汉语书面语，可略典雅，但不文言：不用"之乎者也亦矣"，不用四字骈语凑节奏。
2. 虚词节制：一句之内"于是、遂、便、乃、然而、诚然、究竟、无论"不要连用两个以上。
3. 不追求"雅词"替换。"看"不必改成"凝望"，"说"不必改成"言道"——
   除非原文本身就是那个更重的词。
4. 抽象名词照译，不为顺口添字：le temps perdu 是"逝去的时光"，
   不是"那些已然逝去、再也无法追回的时光"。
5. 感官描写必须具体：气味、光线、触感、声音、温度。
   不许概括成"很美""令人愉悦"——这是全书最要紧的东西。
6. 数字、年代、钟点按中文习惯写。

四、专名
1. 人名、地名按术语表（names_proust.py）音译，全书一致。
2. 法语姓氏的 de 译作"德·"，冠于姓前：德·夏吕斯先生、德·盖尔芒特夫人。
   头衔不省：公爵、公爵夫人、亲王、亲王夫人、男爵、侯爵、伯爵。
3. 家族名音译不意译。地名若有通行汉译（巴黎、威尼斯）从通行译法。
4. 书名、乐曲名、画名用《》；歌、曲、小段旋律用「」。
5. 不加译注、括号解释、脚注。

五、格式
1. 全角标点：，。；：？！“”‘’（）《》——……
2. 引号外层“ ”，内层‘ ’；对话另起一段。
3. 段落与原文严格一一对应：不合并、不拆分、不增删段落。
4. 段首不空格，不加任何 markdown 标记（**、#、- 等一律不许）。

六、忠实
- 不漏译、不增译、不改情节。家具、花木、光线方位、人物动作的次序全部保留。
- 反复出现的意象（玛德莱娜小蛋糕、山楂花、小乐句、窗帘缝里的光）
  每次用同一译法，让母题在中文里也立得住。
- 原文的重复、迟疑、自我修正、跑题的长篇议论，全部保留——
  那是他的意识流，不是需要编辑的冗余。
""".strip()

WEAKNESS_ALERT = """
【译这段时最容易犯的四个错，交稿前逐条自查】

1. **把思绪压平。** 原文三层意思（一个判断、一个让步、一个补充），
   译文只剩一层。断句可以，压平不行。

2. **"的"字堆名词。** "他那种对于往事的、混合着悔恨的、几乎是温柔的回忆"——
   这是法语语序的直搬。该说"他想起往事，悔恨里掺着近乎温柔的什么"。

3. **丢插入语。** "qui, comme on sait, …""— car il était, disait-il, …"
   这类插入成分被整句吞掉。插入语是普鲁斯特的呼吸，必须译出，
   用破折号或逗号嵌进句中。

4. **把讽刺译成平淡。** 一句礼貌的刻薄话被译成中性陈述。
   读你的译文笑不出来，原文那句大概就没译对。

【三条硬规则】
- 不许出现"译注""笔者""原文为"这类元话语。
- 不许把法语原词加括号塞进译文（如"沙龙（salon）"）。
- 段数必须与原文一致；输出前数一遍。
""".strip()
