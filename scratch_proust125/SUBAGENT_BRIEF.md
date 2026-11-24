# 子代理作业单：普鲁斯特第一卷 chunk 逐段润色（2026-11-25 轮）

## 你的范围
只改分配给自己的 chunk（见任务说明里给你的两行范围），其他 chunk 一个字节都不许碰。

## 必读
1. `E:/Translate/POLISH_BRIEF_2026-11-25.md`（总准则，特别是「二、润色准则」七类与「三、红线」）
2. 你自己那批的中文校样：`E:/Translate/scratch_proust125/<你的批次名>_a.txt`、`_b.txt`
   （格式：`@@@ chunkNNN` 一行，下面每段一行，行首 `¶N`；`¶N` 就是该 chunk 的第 N 段）
3. 需要核疑点时读法文原文：`E:/Translate/work_proust/chunks/v1/chunks.json`
   key 是 chunk 号字符串（如 `"61"`），value 是法文段数组，下标 N-1 对应 `¶N`。
   用法示例（务必设 PYTHONIOENCODING=utf-8，否则控制台 GBK 报错）：
   ```
   cd E:/Translate && PYTHONIOENCODING=utf-8 python -c "
   import json,io; d=json.load(io.open('work_proust/chunks/v1/chunks.json',encoding='utf-8'))
   print(d['85'][0])"
   ```
   只核疑点，不要逐句对读，不要把原文贴进汇报。

## 落盘铁律
- 目标文件：`E:/Translate/work_proust/out_ind/v1/chunkNNN/final.txt`，**CRLF** 换行，
  每段一行、段与段之间一个空行。读写必须 `io.open(..., newline='')`，改完 CRLF 计数不许变。
- 只允许「定位唯一子串 → 替换 → 断命中数」：
  `assert old in text and text.count(old) == 1`。禁止整文件重写、禁止用正则批量替换。
- 改前备份：脚本里 `shutil.copy2(path, path + '.bak_20261125')`，已存在就不覆盖。
- 脚本命名：`E:/Translate/polish_proust_ind_<你的批次名>_20261125.py`；
  以 `E:/Translate/polish_proust_ind_p5_20261125.py` 为模板照抄结构（EDITS 列表 + main + 末尾
  `ast.parse(open(__file__, encoding='utf-8').read())` + `main()`）。
- 落盘后跑校验：`cd E:/Translate && PYTHONIOENCODING=utf-8 python scratch_proust125/check_proust_ind.py <起始> <结束>`
  该脚本已自动比对 `.bak_20261125` 的段数/CRLF/引号/ASCII 引号/⟦⟧/段末标点。
  注意它的输出有几类**已知假阳性，不算问题**：段末是「：」（引出下一段）、诗句分行段、`第二部 斯万之恋`这类
  分部标题、`antes`这类作者有意保留的法文音节。除此之外报出来的都要处理掉。

## 只改这七类（其余不动，尤其不要重译、不要加词解释、不要合并/拆分段落）
1. 读不通（语法断裂、主谓/动宾失配、悬空修饰语、缺主语的流水句、逗号连缀成句）
2. 「的」字定语三层以上把中心语压没
3. 外语句法直搬（关系从句后置「……的，他……」、双重「被」、`not…but…`机械对举、冠词式「这个／一个」滥用）
4. 代词指代不明（一段里两个「他／她」指不同人）
5. 专名／术语在同一册内不一致（**注意：本轮专名已合流，不得反改**。你只在发现「同一个名字在本册出现两种
   写法」时才归一，取多数；法文人名地名若有明显误译可改，但要在汇报里点明依据）
6. 硬伤（词义误读、否定/数量反转、时态读反、成语误用、量词错、错别字）
7. 体例（段末标点、引号一律“”、省略号「……」、破折号「——」、数字与西文前后不加空格）

**不动**：作者刻意的短句、排比、重复、口语腔、诗句分行、说话人标签体例、分部标题文字、`⟦i⟧…⟦/i⟧` 标记。

## 分寸
- 保守。一批（24 个 chunk，约 140 段）改 **10～25 条**为宜；宁少勿滥，但也不能一句不改。
- 每条都要能说出属于上面哪一类；纯风格偏好、可改可不改的一律不改。
- 长句不许拆（本册最重要的形式特征）。

## 汇报（最后一条消息里给我）
```
批次: p6  范围: chunk085-108
段数: 改前 == 改后 == N
改动: X 条 —— ①读不通 a ②的字堆叠 b ③外语句法 c ④指代 d ⑤专名 e ⑥硬伤 f ⑦体例 g
典型 3-6 条：旧句 → 新句（各附一句理由，含 chunk 号）
自检: check 脚本输出（除已知假阳性外无 BAD）
另记（不改，只报）：值得进批评稿的问题 2-4 条
```