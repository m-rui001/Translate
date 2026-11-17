# 新增第二批：无歌之国（2026-11-17）

完成《造筏人》《花的祈祷》《时间与商人》《小城》《不可放牧的原野》《无歌之国》《最新的东西》七篇全文，非整书全译。与第一批三篇无重复。直接根据英文原作翻译，未调用模型 API。

## 来源与实际采集

原作是邓萨尼1915年《五十一则故事》中的英语作品。[Gutenberg书目](https://www.gutenberg.org/ebooks/7838)载作者1878—1957、语言English及美国公版状态。本轮实际以 requests 串行下载 Victorian Web 的7个完整HTML页面，均 HTTP 200；原始HTML、逐段提取结果及SHA256在 `work_batch_20261117_second/sources/` 和 `extracted.json`。可重放采集命令：`python pipeline_batch_20261117/fetch_second.py`。保存的HTML副本另在本目录 `sources_second/`，不依赖被Git忽略的工作目录。

网页正文：[造筏人](https://www.victorianweb.org/authors/dunsany/51tales/7.html)、[花的祈祷](https://www.victorianweb.org/authors/dunsany/51tales/12.html)、[时间与商人](https://www.victorianweb.org/authors/dunsany/51tales/13.html)、[小城](https://www.victorianweb.org/authors/dunsany/51tales/14.html)、[不可放牧的原野](https://www.victorianweb.org/authors/dunsany/51tales/15.html)、[无歌之国](https://www.victorianweb.org/authors/dunsany/51tales/17.html)、[最新的东西](https://www.victorianweb.org/authors/dunsany/51tales/18.html)。

提取只取 `div#main` 中、页尾分隔线前、无模板class的正文段落，排除面包屑、编辑说明、导航及日期。没有把页面编辑者的说明翻进正文。该站模板将原书误称为 The Book of Wonder；书目和逐篇正文已对照 [Wikisource所载1915年版](https://en.wikisource.org/wiki/Fifty-one_Tales)核对，不沿用此模板误题。

所用网络文本与Wikisource的段落划分不同，例如《时间与商人》的首段被网络版拆为两段、《花的祈祷》末句另起一段。按实际采用网页保留分段，未将“与另一版段数不同”视作漏译。

## 译介筛选

2026-11-17 检索：`邓萨尼 "造筏" OR "花的祈祷" OR "时间与商人"`、`邓萨尼 "无歌之国" OR "不可放牧" OR "最新的东西"`、`"Dunsany" "The Little City" 翻译 中文`、`"邓萨尼" "The Latest Thing"`；前序另检索 The Unpasturable Fields 和 The Songless Country 的英语题名加中文。

本轮未检出明确的单篇中文译本条目，因此优先纳入；这不能证明不存在改题、未索引或已出版中译。[HyRead馆藏记录](https://mmh.ebook.hyread.com.tw/bookDetail.jsp?id=8349)将双语题名书目归入“英文书”，不能据双语标题反推其包含中文全译。避开项目已有作品及本次第一批三篇；没有将这些微型寓言冒称为新增七部长篇。

## 逐段校读

七篇43段均按原文核对，保留首尾意象、逻辑关系和数字：

- 《造筏人》：保留写作者—水手—筏—遗忘之海的连贯隐喻；巴比伦、尼尼微、推罗、波斯波利斯及结尾荷马为海伦造筏均完整。hull/bulk的网络异文未直译成无意义的“数量”。
- 《花的祈祷》：两个铁路频率分别为每2分钟1列、每5分钟2列；Midland是英格兰中部，并非虚构城市名；潘从阿卡狄亚逆风回应，未颠倒方向。
- 《时间与商人》：染木、铁链敲打、仿虫孔三种做旧手段完整；变老的是商人本人，末句城市需要时间摧毁的反讽保留。
- 《小城》：11.8为11点08分班次；山谷金烟、天堂城墙碎片、山比文明长久的比较均保留；未删pre-destined。
- 《不可放牧的原野》：wear是磨损时间的脚，不是穿戴；云在群山之上，飞马吃百灵送来的歌，战争发生在众神膝上长袍褶皱里，均未落入现实场景改写。
- 《无歌之国》：aimless是没有实用目的，不是写得混乱；保留现代商业对诗歌的拒绝及末尾受诅咒的结语。
- 《最新的东西》：食秽者、诗人、河流、城市之间关系清楚；世纪在命运之山“融化”引起洪水，未改成具体洪灾解释。

本批为主agent逐段自校，未冒称经过第二名独立审校者。第一批三篇已由另一agent全文独立审读。

## 构建与验证

`python pipeline_batch_20261117/prepare_second.py` 合并采集段落和 `second_zh.json`，生成可追踪版本 `second_translations.json`；`python pipeline_batch_20261117/build.py --second` 生成第二批EPUB。构建核对源译段数、非空、标记残留和段末标点，再从EPUB抽出43个段落逐字比对。只有这些检查通过才输出 `validation.json`。

提交前已将 `prepare_second.py` 调整为直接从本目录归档HTML重新提取，无需先联网采集或已有 `work_batch_*/extracted.json`。已在不含历史工作树与备份的隔离目录实跑完整准备、构建和验证流程。

构建数据直接保存在代码目录，工作目录被Git忽略不会导致译文在检出后消失。第一批同样已将原文和中文对齐JSON移入代码目录作为构建真源。
