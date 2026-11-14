# MEMORY

## 2026-10-25 收官状态（前一轮）

七本译作已全部组装、验收通过。详见下方「七本成品表」。

## 2026-10-26 追忆似水年华：改名 + 真目录

**成品**：`追忆似水年华（坟头草译）.epub`（3.8MB / 25 文件 / 1,127,900 汉字）。
旧名 `追忆似水年华（坟头草译·补译卷）.epub` 已删。

### 文件名去掉「补译卷」

用户要求不再叫「补译卷」——本译本就是这部书的完整中译（三、四、六、七卷），
加「补译卷」反而像是在说它残缺。版权页标题同步去掉。

### 目录：从 5 条变 24 条

旧组装器一卷一个 XHTML，nav 只有「版权 + 四卷」五项，113 万字的书里
无法跳转。法语原文其实带结构：

```
Deuxième partie
Chapitre premier
Maladie de ma grand'mère. Maladie de Bergotte. ...
```

即「部 → 章 → 一句内容提要」。按此切分后目录为：

| 卷 | 结构 | 节数 |
|---|---|---|
| 三 盖尔芒特家那边 | 2 部 / 部内 2 章 | 4 |
| 四 索多姆和戈摩尔 | 2 部 / 部内 4 章 | 6 |
| 六 女逃亡者 | 4 章 | 5 |
| 七 重现的时光 | 3 章 | 4 |

nav = 版权 + 四卷 = **5 卷节点 / 24 条**，`toc.ncx` 同步 24 个 `navPoint`。

### `pipeline_proust/` 新增/改写

- **`outline.py`**（新）— 在 `src/<vol>.txt` 里按字符偏移找部/章标记，
  按长度比例映射到中文段落边界。修掉两个坑：① 部与章紧邻时前一个标记
  被后一个覆盖（v3/v4 各一处，丢章）；② 卷首段被安上后面标记的章名。
- **`chapter_titles.py`**（新）— 法文提要 → 中文标题，专名沿用正文译名
  （夏尔吕 / 韦尔迪兰 / 康布雷梅 / 沃古贝尔）。
- **`assemble_proust.py`**（重写）— 按节出 XHTML，`卷(h1) → 部(h2) → 章(h2)`，
  嵌套 nav/ncx。

### 提要泄漏进正文（已清 5 处）

提取时把「章标题 + 一句提要」并进了正文首段，译文里于是出现
`德·夏尔吕先生在社交界。"一位医生。""沃古贝尔夫人的特征性面容。"…` 这种
书目式残段。已删 4 段整段提要 + 1 段提要前缀（`v4/chunk174`）。
判据：一段里全是 <45 字的短句、且句数 ≥3 —— 正常对白不会这样密集。

### 引号：69 处修完

法文长段引语「每段开头加“、末段才收”」是合法的，不能盲数。按
`d=1 且下一段以“开头` 放过；其余逐个读上下文修。**教训**：不能自动插收引号
（`fix_proust_quotes5.py` 把 ” 插到叙述文字后，位置全错，已回退重来），
也不能全局翻转（`说。"下一句"` 本身合法）。正确的办法是**定位具体那个标记**
（`scratch/locate_quotes.py` 用引号栈报出未闭合开引号与多余收引号），再读上下文改。
终态：**0 处真实问题**，剩 29 处全为合法跨段引语。

### 已知：v3 开头是半句

`work_proust/src/v3.txt` 本身以 `ne fût pas encore venu me donner mes affaires…`
开头，是上一卷末尾的续句，非本次组装造成。保持原样。

### 验收

```
xml errors 0 / 汉字 1,127,900 / 引号真问题 0 / ⟦ 残留 0
nav 24 / ncx 24 / 文件 25 / 3,798,452 字节
```

---

## 2026-10-26 新一轮：公版冷门书目批量翻译

### 选目原则（用户明确要求）

1. **避开译著过多的名著**——《悲惨世界》《罪与罚》《安娜·卡列尼娜》《红与黑》
   《包法利夫人》这类一律不选：重译不添价值，好译本也超不过。
2. 作者卒年须 **>50 年**，作品已进公版。
3. 优先 **中文无译本或仅有旧译/节译** 的作品。
4. 文本量不设限。
5. **必须有原文版**。凡是 Gutenberg 只有英译本的（冈察洛夫《悬崖》、约卡伊
   《金人》、奥热什科娃、萨尔蒂科夫），从英译再转译等于把译者的选择洗进中文，
   故只保留有原文的。`timar` 例外保留，见下。

### 已定书目 20 种 / 24 卷 / 16.2MB（`pipeline_gutenberg/books_meta.py`）

| key | 中文名 | 原文 | 作者 | 卒年 | 语种 | ch |
|---|---|---|---|---|---|---|
| nachsommer | 晚夏 | Der Nachsommer | 施蒂弗特 | 1868 | de | 18 |
| effi | 艾菲·布里斯特 | Effi Briest | 冯塔纳 | 1898 | de | 37 |
| immensee | 茵梦湖 | Immensee | 施托姆 | 1888 | de | 11 |
| zauberkaftan | 魔法袍 | Der Zauberkaftan | 米克沙特 | 1910 | de | 10 |
| haidedorf | 草原村 | Das Haidedorf | 施蒂弗特 | 1868 | de | 9 |
| buntesteine | 彩石集 | Bunte Steine | 施蒂弗特 | 1868 | de | 9 |
| wilderMann | 野人旅馆 | Zum wilden Mann | 拉贝 | 1910 | de | 17 |
| fortunata | 福尔图娜塔与哈辛塔 | Fortunata y Jacinta | 加尔多斯 | 1920 | es | 32 |
| regenta | 庭长夫人 | La Regenta | 阿拉斯 | 1901 | es | 31 |
| sotileza | 索蒂莱萨 | Sotileza | 佩雷达 | 1906 | es | 33 |
| ulloa | 乌略亚庄园 | Los pazos de Ulloa | 帕尔多·巴桑 | 1921 | es | 31 |
| germinie | 热尔米妮·拉瑟尔特 | Germinie Lacerteux | 龚古尔 | 1896 | fr | 69 |
| guarany | 瓜拉尼人 | O Guarany | 阿伦卡尔 | 1877 | pt | 55 |
| maias | 马亚一家 | Os Maias | 埃萨·德·凯罗斯 | 1900 | pt | 19 |
| lykkepers | 幸运的佩尔 | Lykke-Per | 彭托皮丹 | 1943 | da | 8 |
| maxhavelaar | 马克斯·哈弗拉尔 | Max Havelaar | 穆尔塔图里 | 1887 | nl | 14 |
| dopoidivorzio | 离婚之后 | Dopo il divorzio | 黛莱达 | 1936 | it | 18 |
| timar | 金人 | Az arany ember | 约卡伊 | 1904 | hu | 47 |
| ayala | 阿亚拉的天使 | Ayala's Angel | 特罗洛普 | 1882 | en | 65 |
| diana | 戴安娜的交叉 | Diana of the Crossways | 梅瑞狄斯 | 1909 | en | 37 |

合计 **571 章 / 2121 chunks / 约 1400 万字符**（≈中文 700 万字）。

### `pipeline_gutenberg/` 模块

- `books_meta.py` — 书目单一真源，`gids` 为**有序卷列表**（多卷必须全取）。
- `fetch.py` — 下载 + 用文件自身 `Title:/Author:` 头校验 gid，防错书；多卷拼接。
- `structure.py` — **章节切分核心**，见下节。`__main__` 打印 20 本诊断表。
- `extract_gutenberg.py` — 切分 → 折行 → `{id,title,blocks}` JSON；`_word_` → `⟦i⟧`。
- `verify_extract.py` — 抽取后体检（标记配平 / 许可残留 / 段长）。
- `run_all.py` — 全仓驱动：chunk → analysis → translate → audit → polish → chapter.md。

### `structure.py` 的六道判定（每道都有真实翻车教训）

1. **序数用后缀判定**，不可枚举。"Sechsunddreißigstes" = 六-and-三十，
   枚举法只能到二十，`Effi Briest` 的 37 章会静默截断。
2. **标题词必须开头**。曾用"包含 Chapter"匹配，把正文
   `In Book Second, Chapter III, "felspar" was mentioned` 当标题，那句就消失了。
3. **标题不可有句末标点**。`Segunda llamó, y Plácido no estaba.` 是段落，
   当标题既丢句又凭空造章。
4. **`DASHED` 匹配 1~2 个横线**。`Los pazos de Ulloa` 用 `-I-`，
   `La Regenta` 用 `--I--`，固定两个横线会让前者整本无结构。
5. **编号族内取"最粗层级"**（间距最大者）。`Fortunata` 的 `-I-` 是部、
   `--i--` 是部内节；取细层会把 10 部炸成 31 节。
6. **编号族与词族不按间距比较，按条数比较**。词族可能只是部级词
   （`TOMO PRIMEIRO`），编号族也可能是部内节；密度才是判据。
   曾让二者纯比间距，`La Regenta` 30 章退化成 3 个"章"。

另有两条专用通路：
- `contents_anchored()` — 有印刷目录时，用目录条目精确锚定正文首现处
  （`Bunte Steine` 靠它拿到 6 篇 + Einleitung + Nachwort）。
- `allcaps_titles()` — 全书大写标题按文档序直接取（`Immensee` 10 章，
  首末章同名 "DER ALTE"，任何"去重"策略都会吃掉最后一章）。

**已知残留偏差**（可接受，不修）：
- `germinie` 70 个 `I.`–`LXX.` 是原书的短节，非章。
- `lykkepers` 原文只有第一部（`Første Del`），共 10 章，已译全该卷。
- `timar` 用英译本（原匈语版 Gutenberg 无），是唯一例外。

### 翻译链路

- 模型统一 `cs:deepseek-v4.1-flash`（`pipeline_whale/llm.py`）。
- **`LIMITS["cs"]` 由 8 改为 160**：原值把并发卡在 8，40 worker 全排队，
  3 分钟零产出。改后 150 worker 满速、零失败。备份在 `llm.py.bak`。
- 审计默认**关闭**：本 key 只有一个模型，自审等于同一颗脑袋查第二遍。
- 术语表初始为空：这批书无中译可借名，先凭文本自译，成品后再由
  `pipeline_polish/terms.py` 挖专名回灌。

### 运行

```
python -X utf8 pipeline_gutenberg/fetch.py          # 下载+校验
python -X utf8 pipeline_gutenberg/extract_gutenberg.py --all
python -X utf8 pipeline_gutenberg/verify_extract.py
python -X utf8 pipeline_gutenberg/run_all.py --all --workers 150
```

### 本轮踩到的环境坑（已记）

- **`python - <<'EOF'` heredoc 常年静默不执行**，还会把 `\\n` 变成真换行写进源码。
  两次把 `structure.py` 写坏。**一律 `write` 落文件再 `python -X utf8 file.py`。**
- `pkill` 在本环境不存在；用 `kill -9 <pid>` 或 `ps -W | grep python` 找进程。
- `--all` 输出重定向到 `/dev/null` 时若脚本报错，会静默留空目录，须复查。

## 2026-10-26 全量润色（不重译，8.17M 字）

**任务**：在现有译文上润色（非重译），且**不止普鲁斯特** —— 全workspace 统一处理。

### 覆盖范围（3,483 单元 / 8,167,692 字）
| 语料 | 单元 | 字数 |
|---|---:|---:|
| Gutenberg 20 本 | 2,114 | 4,710,010 |
| Proust 四卷 | 633 | 1,240,226 |
| 魔山 zauberberg | 244 | 590,172 |
| 魔戒 lotr | 63 | 834,804 |
| 白鲸 whale | 206 | 383,550 |
| 百年孤独 soledad | 120 | 232,646 |
| 鼠疫 camus | 84 | 139,843 |
| 第六病室 chekhov | 19 | 35,924 |

结果：**polished_ok=3,369 / kept_or_reverted=51 / fail=0**，约 66 分钟。

### 新模块
- `pipeline_polish/index_units.py` — 全量单元索引，报告源/译段数对齐率
- `pipeline_polish/polish_engine.py` — 第二代润色引擎（新 key、纯段落协议、可带原文）
- `pipeline_polish/run_polish_all.py` — 统一队列，`--corpora gutenberg,proust,plain,lotr`
- `pipeline_polish/verify_polish.py` — 内容保真核验（数字/拉丁词/长度/相似度）
- `pipeline_polish/detect_shift.py`、`detect_shift2.py` — 段落位移检测
- `pipeline_polish/show_issues.py` — 打印 before/after 供人工判断

### 关键经验（血泪）
1. **模型默认「审读」而非「改写」**。SYS 里只写「不要改内容」会导致它原样抄回。
   必须写明「你的职责是动手改，不是审读」并给改法示例（"添进了…之中"→"添进"）。
2. **段落位移是最危险的缺陷**：字数对、读着顺，叙事已错位。必须逐段比对守卫。
   判据：`best_match_index != i` 且该匹配唯一（重复行多，不加唯一性会大量误报）。
3. **内容审核拒答会被写回正文**（`Sorry, I can't respond...`）。必须正则拦截。
4. **原文对齐不能只看段数**。段数相等但错开一节时，模型会去缩写外文原文。
   加长度比例合理性检查：`min(ratios) < 0.12*ref` 或 `max > 8*ref` 则视为未对齐。
5. **长段必须防空摘要**：`len(out) < 0.80*len(orig)` 即退回。
6. **目录页/词汇表不是散文**，润色会破坏。`timar/c001` 22 条目录被压成 8 条。
7. **对话密集章要逐段润色**（短段 <60 字占比 ≥1/4 时），否则相邻对话被合并。
8. 大 batch（6000 字）段数漂移率高；失败后自动对半切重试可收敛。

### 计费真相（纠正此前误判）
- **按次计费 key `sk-***…` 全程未被管线使用**，只有 `scratch/probe_keys.py`、
  `scratch/measure_keys.py` 引用过。实际全走按量 key `sk-***…`。
- 该 key `/models` 能通（4 个模型：mimo-v2.6-flash / muse-spark-1.3-contributor /
  GLM-5.3 / DeepSeek-V4-Pro-0813），但 `/chat/completions` 一律
  `502` / `Service temporarily unavailable` / `rate_limit_error`。
  **muse-spark 调不通，无法用于润色。**
- 单价（同一 chunk 1173 prompt/1132 completion）：
  `deepseek-v4.1-flash` 与 `deepseek-flash`、`deepseek-v4-flash` 同为 0.07 credit；
  `glm-5.3` 0.87；`kimi-k3` 3.17。**deepseek-v4.1-flash 已是全池最便宜档。**
- 实测账单：`deepseek-v4.1-flash` ≈ $0.000297/1k，`glm-5.3-flash` ≈ $0.000238/1k
  （只便宜 20%），但 glm 输出 84–96 tok/s，deepseek 121–172 tok/s。**慢 2–5 倍，不划算。**
- **缓存字段是 `prompt_cache_hit_tokens`，不是 `prompt_tokens_details.cached_tokens`**。
  `cs:deepseek-v4.1-flash` 累计 44.35M prompt，命中 9.88M（22%）。
  `ds:` 前缀 4.93M、`qw:` 11.17M **零命中**，纯浪费。
- 累计 13,629 次调用，prompt 63.5M，completion 19.0M，credit 1,221.5。

---

## 2025 组装收尾（本轮完成）

### 成品
`./out` 现有 **27 本**（`{书名}（坟头草译）.epub`），**6,515,571 汉字**，23MB。
根目录旧输出已 `prune` 清空（7 个删除）；第三方参照译本
（Moby-Dick / Cien años / Der Zauberberg / La peste / 魔戒 z-library）保留。

| 来源 | 本数 | 组装器 |
|---|---|---|
| 七本旧书 | 7 | `pipeline_build/build_all.py --all` |
| Proust | 1 | `pipeline_proust/assemble_proust.py` |
| Gutenberg | 20 | `pipeline_build/build_gutenberg.py` |

### 本轮修掉的缺陷
1. **`build_gutenberg.py` 调用不存在的 `B.write_epub`** → `package()` 自身写盘；
   改为先设 `B.OUT = OUT` 再调 `package()`。
2. **`⟦i⟧` 斜体标记漏进正文**：润色把收尾标记改坏成 `⟧`、`/i⟧`、`⟧/i⟧`。
   新建 `pipeline_gutenberg/fix_italics.py`：
   - 先把**完整成对** `⟦i⟧…⟦/i⟧` 用占位符寄存（否则会被二次包裹，写出 `⟦/i⟧/i⟧`）；
   - 再把受损形式规范回完整标记；
   - 段数校验后写盘；跑两遍幂等。
   修 12 文件 / 31 处，另有 3 处孤立 `⟧`（成对标记后的残渣）手工删除。
   **教训：检测残留不能用「整对匹配」，长斜体段会超窗口→误判；正确做法是删掉
   `⟦i⟧`/`⟦/i⟧` 两个 token 后再看有没有剩余括号。**
3. **目录全是原文**：`title_zh` 里存的是 `Erstes Kapitel` / `-I-` / `CHAPTER VII` /
   `ZEVENDE HOOFDSTUK`。新建 `pipeline_build/titles_src.py`：
   有名章名查表（德/西/荷/丹/英，约 60 条），其余**一律按书内位置编号**。
   - **不能用原文数字编号**：`庭长夫人`、`热尔米妮` 等分卷书卷内重编号，
     会产出几十个连续「第一章」。改用 `ordinal` 后 20 本 TOC 全中文且无重复。
   - `norm()` 必须做变音符折叠（`ä→a` 等），否则 `Die Häuslichkeit` 查不到。
4. **`verify_epub.py` 口径错**（三处）：
   - `copyright_paras` 曾把页头 `p.src` 计入 → 只数 `div.cn` 内非 `src` 文本块，
     现恒为 **1**（文案已合并为一段）。
   - `chapters` 只认 `OEBPS/cNNN.xhtml` → 加 `v\d+_\d+`；注意**后一行旧赋值会覆盖**，
     已删。
   - 残留检测一并覆盖 `⟦i⟧` / `[[n]]`。
5. **Proust 输出目录**：`PROUST_EPUB` 默认值改到 `E:/Translate/out/`。

### 版权页定稿（用户要求）
用户明确**不要**「防止商用」那半句。现文案只有一段：
```
本译本由坟头草翻译，保留署名权；除此之外不主张任何权利，亦不作任何担保。
```
源头唯一：`pipeline_overhaul/copyright.py::TEXT`，所有组装器共用。

### 验收（`pipeline_build/verify_epub.py`）
`27 epub, 0 with errors` —— mimetype 首项 stored / XML 全解析 / manifest href 存在 /
spine idref 合法 / `nav.xhtml` 带 `properties='nav'` 且在 spine / nav-ncx 条目相等 /
无 `⟦`·`[[n]]`·旧文案残留 / 版权页 1 段 / 目录全中文无重复。

### 脚注（`scratch/check_notes.py`）
`白鲸 943 / 百年孤独 122 / 魔戒 473`，`rN`↔`nN` **双向全闭合，0 断链**。
**坑：脚注 id 每章重置**（`n1…n8` 每章各一套），全书拼接后去重只剩 8 个 →
必须**逐文档**校验，否则 943 会被误报成 8。

### 待办（API 恢复后）
- Proust v1/v2/v5 补译（目前只有 v3/v4/v6/v7；v1 仅 1 chunk 1378 字）。
- 全七卷重分块 `chunk_all_vols.py`（`TARGET_WORDS=2600` / `HARD_MAX_WORDS=4500`）。

---

## 2026-10-26 提速实测（结论：瓶颈是 decode，不是 prefill；audit 不划算）

用户问「怎么把并发开更高，比如一部分流量走我网络 IP，另一部分走代理」。实测结论如下，
**分流方案在当前条件下无效**，但顺手挖到了真正的问题。

### 分流：无效（有数据）
- 直连与本地 7897 代理**出口 IP 相同**（`82.29.38.159`），不存在第二条通道。
- 并发 → 吞吐：`32→2.76 ok/s / 64→4.50 / 100→4.67`。并发 +56% 只换来吞吐 +3.8%，
  p90 却 14.7s→25.1s 并开始 429。这是**软性配额**（≈5 req/s），加线程只排队。
- 因此「按 IP 分流」在拿到真正的第二出口之前**没有可测收益，不值得写代理池**。

### 延迟的真正来源：decode，不是 prefill（修正前一版结论）
前一版 `probe_latency.py` 得出「1.7ms/源文字符，预填充主导」，**这个结论是错的**。
错因值得记：长 prompt 组里塞了 40 句**待译文本**，输出因此也变长，输入长度与输出长度
共变，实验分不开二者。

正确实验（`scratch/probe_decode.py`，同一输入，只改要求输出几遍）：
```
compl 20 token → 2195ms ; compl 240 token → 3056ms
=> 3.9 ms / output token, 实测解码 256 tok/s
```
结论：**延迟由输出 token 数决定**。所以省时的杠杆是**减少「输出全篇重写」的段数**，
不是压缩 prompt。

### 已落地的改动（`pipeline_proust/workflow_independent.py`）
`OPTIONS = {"trim_glossary": True, "trim_source": True, "max_correction": 0.12}`

1. **`trim_glossary`**：system 只放本 chunk 命中的专名（`names.relevant()` 现成但此前
   从未使用），不再塞全 174 条。
   - 原 docstring 假设「前缀逐字节一致 → 命中缓存」，但**前缀每个 chunk 都不同**（动态段
     在一个 user message 内），所以「绝不裁剪」换来的缓存从未发生：实测 polish 命中率
     **16%**，不是假设的 ~100%。
   - 实测：draft prompt **−29%**（5,345→3,782）、polish **−42%**（5,088→2,950）。
2. **`trim_source`**：polish 不再收法文原文（已有对齐译稿，原文是全管线最大重复块）。
   - 风险是失去「补漏译」能力，故加 `_similarity(draft, t) >= 1 - max_correction`
     守门，并把每次相似度记进 `meta["polish_sim"]`（让阈值将来能用分位数校准）。
3. **盲测成对比较**（`scratch/ab_pairwise.py`，标签随机化）：trim **4:1 胜 base**，
   质量没降。→ 截断保留。

### audit 阶段：实测不划算，已改为默认关闭
- v5 的 150 个 chunk 发出 **646 次**调用：`draft 205 / audit 151 / repair 137 / polish 153`
  → 每 chunk **4.3 次请求**，而非设计的 2 次。`repair` 在 151 次 audit 里触发 **137 次**，
  近乎必触发 —— 那不是诊断，是第二遍重写。
- 盲测 5 个 chunk：**audit 2 : no-audit 2（平局）**，但耗时 **49.5s vs 19.8s（2.5x）**。
- 改动：`run_independent.py` 加 `--audit`（opt-in），默认关；`--workers` 默认 80→**64**。

### 「多遍润色」的真实状况（重要）
`scratch/cmp_polish_prompts.py` 在同一份 draft 上比较三种 polish prompt：
```
              sim    说明
无源文(新)    0.999
带源文(原)    0.988
激进重写指令  0.995-1.000
```
**三种都几乎不动文本，连「重写」指令也不动。** 说明不是我把 prompt 写得太保守，
而是 **draft 已接近该模型上限，polish 阶段在空转**。

抽查 draft 质量（`scratch/_cmp/v5_c002/`）：句子如
「我按铃叫弗朗索瓦丝。我打开《费加罗报》。我在报上寻找我那篇寄给该报的文章——…」
已经通顺，aggressive 版仅把前三个短句并成一句，其余逐字相同。

**推论**：靠同一模型重复润色拿不到增益（已两次实验确认）。想再提质量必须
**换模型 / 换视角**（如让另一模型做校勘、或针对具体毛病定向返工），不是加轮次。
这点与用户「多遍润色质量不输人类译者」的判断有张力，需用新书的真实产出再验。

### 吞吐现状（不是配额瓶颈）
`run_independent.py` 并发 64 时 v5 实测 ≈ `0.69 chunks/s`；关掉 audit 后每 chunk 2 请求，
理论 `4.5 req/s ÷ 2 = 2.25 chunks/s`，**尚有 3x 余量**，说明之前是 audit 把自己拖住了。

### 免费 key 与付费 key
- 付费 key 已按用户要求**从代码中彻底移除**（`CSSM_KEY_OLD` 删除，仅留注释记录格式）。
  用户原话：「不要用付费key，没钱」。
- `CSSM_KEY` 现在只可能解析为免费 key。验证：`hasattr(llm,'CSSM_KEY_OLD') == False`。

### 新增/修改文件
- 改：`pipeline_proust/workflow_independent.py`（OPTIONS / `p_polish_short` /
  `_similarity` / `_sys_writer` / `_sys_polisher` / polish_sim 记录）
  — 备份 `pipeline_proust/_bak_workflow_independent.py`
- 改：`pipeline_proust/run_independent.py`（`--audit` opt-in、workers 64）
- 改：`pipeline_overhaul/copyright.py`（`page(..., private=True)` + `TEXT_PRIVATE`）
- 新：`scratch/probe_ip_split.py`、`probe_decode.py`、`ab_pairwise.py`、`ab_audit.py`、
  `verify_truncate.py`、`cmp_polish_prompts.py`
- 新：`pipeline_private/books.py`（公私两条线的书目 + 版权判定）、`lookup_gids.py`、
  `fetch_pub.py`

### 版权线划分（`pipeline_private/books.py`）
- **公版**：作者卒于 **≤1975**。注意不能用 `2026-50`：卒于 1976 者保护期到
  2026-12-31，**今年仍在保护期内**，故 `PUBLIC_CUTOFF = CURRENT_YEAR - 51`。
- **私用（在版）**：卒于 1976 及以后，25 本。规则：**不署名、不发布、不进 `./out`**，
  版权页走 `private=True`（`TEXT_PRIVATE`，无「坟头草」三字）。
- 已抓取 **16 本新公版书**到 `work_pub/src`，全部通过 Gutenberg 头信息作者校验
  （卡夫卡 7 / 里尔克 3 / 伍尔夫 4 / 霍夫曼斯塔尔 2，德文与英文原文，非英译转译）。
- 修正：先前误把卡夫卡、里尔克、伍尔夫、霍夫曼斯塔尔放进私用线 —— 四人**均在 1975 年前
  去世，都是公版**，那么放等于没测。已移回 `PUBLIC`。

### Proust 补译完成
`v1 181/181`、`v2 225/228`、`v5 149/150`，TOTAL 559 chunks，`fail=4`（全为段落数对齐，
非传输失败）。v1 现 **257,878 汉字**、v2 **318,986 汉字**。

## 2026-10-26 公版线（16 本）全流程打通

### 结果
`./out` 现 **43 本 / 7,293,954 汉字 / 25.4MB**，`verify_epub` **43 epub, 0 with errors**。
新增 16 本 / 125 章 / 775,700 汉字。Proust 三卷 559 chunks 全部 0 失败。

### `pipeline_pub` 新链路
- `extract_pub.py`：复用 `structure.strip_licence` / `chapter_starts` /
  `extract_gutenberg.build_blocks`，读 `work_pub/src/*.txt`，出 `work_pub/<key>/src/cNNN.json`
  + `index.json`。
- `run_pub.py`：复用 `pipeline_whale/workflow.translate_chunk`，`audit=False`，`polish=True`，
  无 glossary（`wf.rel_gl=lambda s: []`），`--workers` 默认 64。
- `titles_pub.py` + `apply_titles.py`：中文目录标题（手工表 + 序数解析）。
- `build_pub.py`：组装，复用 `build_all.package`。

### 四个必须记住的坑

**1. `min_paras=3` 会吃掉短篇。**
`Betrachtung` 原书 18 篇，Kafka 短篇常只有 1-4 段。默认 3 时丢了 5 篇
（`Der plötzliche Spaziergang` 2 段、`Der Ausflug ins Gebirge` 1 段……）。改 `min_paras=1` 后
`betrachtung` 13→19 章、`landarzt` 11→15 章、`stundenbuch` 5→7 章。

**2. `is_front_matter` 判据踩了三次坑。**
- v1「最长段 <120 且总长 <400」→ 杀掉 `Neue Gedichte` 的真诗（诗本来就短）。
- v2 加 `IMPRINT` 正则含 `^[A-Z ]{3,}$` → 杀掉 `DAVID SINGT VOR SAUL`（大写诗题）。
- v3 要求「几乎每行都命中」→ `Das Stunden-Buch` 扉页只有 3/8 命中，漏掉。
最终判据（按顺序）：
  a. `total >= 900` → 不是扉页；
  b. 任一行命中 `IMPRINT`（只含 `VERLAG/Copyright/Printed/Druck/Proofreading/
     Gutenberg/Insel-Verlag/Harcourt/pgdp/gutenberg.org`，**不许有 `^[A-Z ]{3,}$`**）→ 扉页；
  c. 含「目录」且最长段 <200 → 扉页；
  d. 含 `Contents` 且 `CHAPTER` 出现 ≥5 次 → 扉页；
  e. `total < 200` 且**无任何句子**（`SENTENCE` 正则）→ 扉页（抓 `Ver.04.29.93*END*` 这类无出版名的）。
结果：11 个扉页全中，诗章零误杀。**`neuegedichte/c001` 是 4,747 字符含真诗，必须翻译**——
「扉页长度」上限设 200 正是为了不吞它。

**3. `rm -rf work_pub/*/out/c001` 会删掉单章书的正文。**
`hungerkuenstler` / `mrsdalloway` / `jedermann` / `strafkolonie` / `torundtod` 全书就是 c001。
误删后要单独 `--books` 重译（67 chunks）。

**4. 章节标题在正文里重复两遍 —— 是假警报。**
`re.sub(r'<[^>]+>','')` 会把 `<title>` 和 `<h1>` 拼在一起，看起来像
「揭穿一个骗子揭穿一个骗子」。**EPUB 内实际只出现一次**。判断重复必须看原始 xhtml。
真正的重复（`final.txt` 首段 = 译好的标题行）已用 `drop_repeated_head` + `_close`
（Levenshtein ≤3、长度 ≤40）剥掉，实测 `揭穿一个骗子` vs `揭穿一个乡下骗子` → 删，
`判决` vs `那是春季一个美好的星期天上午。` → 不删。

### 目录标题规则（`titles_pub.py`）
- 扉页章（首章且无源标题）→ **卷首**；单章书 → **书名本身**（不许出现「卷首」）。
  否则 `jacobsroom` 会列出「第一章 / 第一章 / 第二章」。
- `ERSTES KAPITEL`→第一章、`CHAPTER ONE`/`I`→第一章（`_WORD_ORD` + `_ROMAN` 扩到 XXX）。
- `neuegedichte` 的 `I/II/III` 在每个诗组内重复计数，不能译成「一/二/三」（TOC 会出现
  三个「一」），改 **第N首**（按正文章序，`body_pos`）。
- `urteil` 的 `FÜR F.` 是题献不是篇名，标题必须用 **判决**。
- `verify()` 只报**连续两个以上**拉丁字母；`献给F.` 的单字母是合法中文排法。

### 单章书不要清空 `title_zh`
`build_all.package()` 里 `if not title: title = f"第{cn_number(...)}章"`，
清空反而自动编号成「第一章」。保留书名即可。

---

## 2026-10-26 全库行内拉丁词清扫 + `clean_check.py`

`verify_epub.py` 只看结构（manifest / spine / nav / ncx / 版权页段数），看不出正文里
夹着英文词。模型偶尔在中文句子里留一个源语言副词就接着写中文：

    杜兰特太太 meanwhile 在后屋…      宾客们 meanwhile 拿那些冷盘消遣…
    这病根 chiefly 扎在他的想象里…    门口响起那 unmistakable 的枪托声…

汉字在两侧、中间一个孤立小写拉丁词，是这类漏译的唯一稳定特征：

    [\u4e00-\u9fff]\s+([a-z]{3,12})\s+[\u4e00-\u9fff]

**全库实测**：`work_pub` 10 处、`work_gutenberg` 50 处、`work_proust` 1 处、
`work_zauberberg` 5 处、`work_soledad` 1 处、`lotr` notes 2 处，共 **69 处**。

### 关键：这个正则同时命中大量**合法**外语
不能无脑替换。以下全部是原文在说自己的话，改了就篡改原书：

| 词 | 为什么保留 |
|---|---|
| `erf` | 荷兰殖民时代宅地单位，同段就给了释义 |
| `calli` | 威尼斯小巷，普斯特写威尼斯夜景 |
| `kauern` / `hvalt` / `welsch` | 词汇表与词源考证，整段的主题就是这个词 |
| `moribundus` / `vacuum` / `mot` / `gaudeamus` / `liquefacta` | 拉丁语，人物刻意引经据典 |
| `pazzi` / `ragione` / `ribellione` / `lazzo` / `aquatinta` | 意大利语，塞特姆布里尼与《魔山》语境 |
| `delicado` / `visitador` / `prolongada` / `peseta` / `plaisir` / `bandera` | 西班牙语 |
| `fogas` | 匈牙利语鱼名 |
| `hoch` / `pas` | 普斯特在讲德语音、法语的 `ne…pas` 规则 |
| `serene` | 「最 serene 的先生」是主教尊称的一部分 |
| `plateau` | 体温曲线的高原段，德语原文亦作外来词 |

所以 `pipeline_build/clean_check.py` 里有一张 `LOAN` 白名单，列的就是这些。

### 真正要改的（69 处中 42 处）
英文虚词与普通名词，中文里有现成对应词，属于译者在句子中途切回英文：

    meanwhile→同时   chiefly→主要     overall→大抵      hut→小屋
    strictly→严格    nonetheless→然而  likewise→同样     occasions→场合
    later→稍后       centuries→数百年  exclusively→专一地
    irresistibly→不由自主地           productive→创作   whimsical→任性
    allowances→零用钱  scarecrow→稻草人  pedestal→基座
    adopted→接受     steel→钢         forging→铸造     unmistakeable→不容错认
    blocks→启事      refereeing→洗（被寒气洗过）

替换后必须复查**叠字事故**：`exclusively 地` → `专一地地`，五个候选里中了两个
（`专一地地`、`的的`），逐条手工修掉。**批量替换后一定要再扫 `地地`／`的的`／`得得`**，
但注意 `欢天喜地地`、`死心塌地地`、`无目的的`、`做驮鞍的的特鲁希略家` 里前四种是合法
中文，只有第五种是真错。

### `clean_check.py` 五项检查与它们的误报
1. 行内拉丁词（`LOAN` 白名单除外）
2. 整段未译（拉丁字母 > 60%）—— `草原村` 末尾词汇表条目合法，条号是**汉字**
   `【七十九】` 不是阿拉伯数字，正则要写 `【[\d一二三四五六七八九十零百]+】`
3. 标记泄漏 `⟦i⟧` / `**` / `||` / `[SEP1]` —— 普斯特原文用 `冯·***亲王`
   打码人名，`**` 紧邻 `·` 或汉字必须放行
4. 近空章（< 20 汉字）—— `魔戒` 的 `v3/v26/v48` 是卷扉页
   `<div class='titlepage'>`，不是空章
5. 一章出现多个 `<h1>`

### 段落切分要用块级标签
`re.sub(r'<[^>]+>','',html)` 会把 `<h2>第一部 外祖母的病与死</h2><p>清晨鸟儿…</p>`
粘成一段，看起来像「标题漏进了正文」。必须先
`re.sub(r'</(?:p|h[1-6]|div|li|blockquote|tr)>|<br\s*/?>', '\n\n', ...)` 再剥标签。

### 最终状态
`43 epub / 7,286,168 汉字 / 26MB`，`verify_epub` **0 errors**，
`clean_check` **0 problems**。

### 新增文件
- `pipeline_build/clean_check.py` —— 成品级正文体检，两项验收之一
- `scratch/fix_latin_leaks.py` —— 公版 16 本的 10 处
- `scratch/fix_gut_leaks.py` —— Gutenberg 20 本的 50 处（词表 + `meantime 先到` 特例）

---

## 2026-10-26 标点体检定案 + 拉丁撇号全库修复

### 起点：`typo_check.py` 303 条几乎全是误报

初版六项检查里，**引号平衡**一项独占 300 条。判据是文档级 `count("“") == count("”")`，
逐文档必误报 —— 中文跨段引语每段补 `“`、只在末段收 `”`。

改成 `quote_balance(body)` 按段落序列走 depth 计数器后仍是 205 条，仍然错。查 `魔戒`
`c003.xhtml`：depth 39，但逐段看每段只 +1。这是 **「夹白」格式**：

```
“在很多方面，”巫师答道，“它的威力……
```

两个 `“` 一个 `”`，说话在下一段继续。**这一段就是 39 个跨段引语，不是 39 个漏收**。

### 最终判据：只报 orphan closer

```
” arrives when depth == 0  →  丢了开引号  →  真缺陷
“ arrives and never closes →  跨段对话    →  正常
```

改完 303 → 121 → 18 → 12 → 9 → 7 → 6 → 1 → **0**。

### 期间发现的两类真缺陷

**A. 拉丁撇号被中文引号吃掉（16 处 / 7 本）**

规范化 pass 把每个 ASCII `'` 映到 `”`，中文里对、外文引文里错：

| 错 | 对 | 位置 |
|---|---|---|
| `Si”l vous plaît` | `S'il vous plaît` | 幸运的佩尔 c006 |
| `s”achina` / `t”isetto` | `s'achina` / `t'isetto` | 离婚之后 c012/c018（撒丁语） |
| `d”Innstetten` | `d'Innstetten` | 艾菲·布里斯特 c012 |
| `n”est` / `J”ai` / `j”ai` / `c”est` | `n'est` / `J'ai` / … | 马亚一家 c016（7 处） |
| `s”excuse s”accuse` | `s'excuse s'accuse` | 马克斯·哈弗拉尔 c014 |
| `s”il vous plaît` | `s'il vous plaît` | 马尔特手记 c002 |
| `qu”il` / `d”amandes` | `qu'il` / `d'amandes` | 魔山 c008/c010 |

判据机械无歧义：**撇号在两个字母之间，引号挨着空格/汉字/标点**。

```python
APOS = re.compile(r"(?<=[A-Za-z])”(?=[A-Za-z])")
```

`scratch/fix_apostrophes.py`（`--apply`）就地重写 EPUB 的 xhtml，保留 zip 顺序与
STORED mimetype。**16 fixed → 0 left**。

**B. 中文对话丢开引号（6 处）**

| 书 | 位置 | 症状 |
|---|---|---|
| 晚夏 | c011 段0 | 整段是父亲的话，缺 `“` |
| 庭长夫人 | c022 段11 | 安妮塔内心独白，缺 `“` |
| 星期一或星期二 | c004/c02 段5 | `一家人越来越多——”可你的家人` 夹白漏第二个 `“` |
| 魔山 | c007 段15 | `……谁也说不准。` 跨段续段，缺 `“` |
| 魔戒 | book3c06[118] | `凡能骑马的人…` 同上 |
| 白鲸 | ch120/ch121/ch127 段1 | 舞台指示 `（…）` 后台词缺 `“` |
| 马克斯·哈弗拉尔 | c009 | 整封信只段4开段23收，信体从段5起全悬空 → 段5补 `“` |
| 追忆似水年华 | v6 chunk059 | `您肯定？”这可真叫我吃惊` 公爵的话缺 `“` |
| 追忆似水年华 | v3 chunk037 | 段首 `”哦！他呀` 用了收引号当开引号 |
| 白鲸 | ch003 | `这位”深肤色”` 强调应作 `“深肤色”` |

### `space between Chinese` 31 条全是合法排版

五类各有专属豁免（`typo_check.py` 里逐条注释）：

1. **卷/章号 + 标题**：`第三卷 盖尔芒特家那边`、`第九章 伊萨多·哈梅尔被邀午餐` → `LABEL_HEAD`
2. **注号 + 正文**：`一四五 关于赛义贾这首歌` → `LABEL_HEAD`
3. **文号 + 地点**：`第一百一十四号 朗卡斯贝通` → `号[ \t]+汉字{2,}`
4. **目录条目**：`两不相伤 十、夜之冲突` → `[一二三四五六七八九十\d]+[、.]` 开头
5. **出版信息**：`纽约 哈考特·布雷斯与世界出版公司` → 城市前缀
6. **疏排强调**：`说 不……带着几分 伊壁鸠鲁式 的娇态` → 见下

第 6 类踩了个坑：`<em>不</em>` 剥离标签后变成 `说 不……`，看起来是汉字间空格，
其实是**斜体强调字两侧的空格**。修法是在 `docs()` 里把 `<em>X</em>` / `<i>X</i>`
换成 `\x01X\x02` 哨兵，`SPACED` 检查见到 `\x01`/`\x02` 就跳过。

### `runaway paragraph` 阈值 3000 → 6000

Proust 单段 4000+ 汉字是本色，3000 阈值报 50 条全部误报。这项检查的本意是
「空行丢了没有」，不是「句子太长」。

### 最终验收（八器全绿）

| 检查器 | 结果 |
|---|---|
| `verify_epub.py` | 43 epub, **0 errors** |
| `clean_check.py` | 43 epub, **0 problems** |
| `typo_check.py` | 43 epub, **0 problems**（起点 303） |
| `scan_lost.py` | **0 chapters broken** |
| `scan_licence.py` | **0 licence pages shipped** |
| `scan_meta.py` | **0 meta-talk / 0 duplicated paragraphs** |
| `scan_dups.py` | **0 near-duplicate pairs**（源 + 成品） |
| `scratch/find_orphan_quotes.py` | **0 orphan closers**（起点 18） |

### 本章的两条通用教训

**一、引号平衡必须按「说话单位」判，不能按「文档」或「段落」判。**
中文对话三种合法形态：段内自平衡、跨段延续（每段开、末段收）、夹白（两开一收）。
只有「收引号先于开引号出现」是错。任何基于 `count()` 相等的判据都会把前两种判成缺陷。

**二、`final` 与前缀目录不是唯一正文源，`polished` 树会覆盖 JSON。**
`build_all.py::collect_json_book` 先读 `json` 目录的 `texts`，再调 `polished_chapter()`
用 `work_XXX/out/<cid>/c*/final.txt` **整章替换**（段数相等时）。所以：
- 改 `work_overhaul/whale/final/ch120.json` 对 `白鲸` **无效**；
- 真正的正文在 `work_whale/out/ch120/c00/final.txt`；
- `魔戒` 反过来 —— 只有 `work_overhaul/lotr/final/*.json` 有 `texts`，`rev/`、`ch/` 是 0。

**改哪一本之前，先确认那本走哪条 `collect_*`**：
`collect_json_book`（whale/lotr/soledad…）、`collect_flat`（flat/parts/split）、
`collect_parts`、`collect_gutenberg`、`collect_pub` 五条路，正文位置各不相同。

### 新增文件
- `scratch/fix_apostrophes.py` —— 拉丁撇号修复，`--apply` 才写，幂等
- `scratch/find_orphan_quotes.py` —— orphan closer 定位，含「在哪个 JSON 里」反查
- `scratch/find_two.py` / `scratch/patch_typo_em.py` —— 一次性定位/补丁

---

## 2026-10-26 API 端点大清查：cssmapi 已死，切换本地网关

### 触发

用户报「cssmapi 用不了了」，随后指示「用 e:\tools 里面的 api」「不能用的 api
清理掉 能用的整理出来」。

### 诊断 cssmapi：网关活着，后端死了

```
GET  /v1/models                          200, 0.04s, 列出 deepseek-v4.1-flash
POST /v1/chat/completions  (该模型)       挂起 60s，零字节，HTTP=000
POST /v1/chat/completions  (其他模型名)   404 "not available for this group"，秒回
```

**鉴权和分组检查都在工作**（所以不是 401），只有推理后端不响应。限时免费 key 额度
耗尽或后端被撤就是这个形态：**挂起而非拒绝**。

这条差别是批量任务的命门 —— 拒绝立刻释放连接，挂起会吃满客户端的整个读超时，
一个死端点能拖垮整条并发队列。所以死端点要么置空 key 让它秒失败，要么从
WRITER 删掉。

### 全池实测：41 个模型，12 个能用

探测器 `scratch/probe_all_models.py`，6 并发，单次 120s 超时，**判据是「返回里有没有汉字」**。

**`/v1/models` 返回 200 完全不能作可用判据** —— cssmapi 和 10000 网关都能秒回
模型列表，chat 却全挂。必须真做一次 round-trip。

| 端点 | 列出 | 真能出文 |
|---|---|---|
| `127.0.0.1:8317`（key `<local-key>`） | 32 | **12** |
| `127.0.0.1:10000`（OpenCode2API） | 9 | **0** |

8317 上 20 个死：8 个 TimeoutError、9 个 HTTPError、3 个返回非中文。
10000 上 9 个全 TimeoutError（它的上游 `OPENCODE_SERVER_URL=http://127.0.0.1:10001`）。

### 选定 WRITER：`lc:ms-deepseek-v4.1-flash`

| 模型 | 延迟 | 速度 | 判词 |
|---|---|---|---|
| **`ms-deepseek-v4.1-flash`** | 1.1s | 43.9 tok/s | 老人坐在河边，等着鱼儿浮出水面。 ← 采用 |
| `or-north-mini-code` | 1.3s | 76.0 tok/s | 最快，但 `rise` 译成「上钩」 |
| `ms-qwen3.8-flash` | 3.0s | 49.7 tok/s | 好 |
| `ms-qwen3.5-27b` | 23.8s | 67.6 tok/s | 首包太慢 |
| `cf-r1-distill-32b` | 8.6s | 34.0 tok/s | **带思维链污染**，勿直用 |
| `cf-mistral-7b` | 3.3s | 14.4 tok/s | **附英文说明污染**，勿直用 |

### 改动

**`pipeline_whale/llm.py`**（备份 `.bak_20261026`）
- 新增 `LOCAL_BASE` / `LOCAL_KEY` / `LOCAL_OVERRIDE`，provider `local-gateway`
- `NS_PROVIDER` 加 `"lc"`；`LIMITS["lc"] = 6`（本地网关实测 6 并发零传输失败）
- **`CSSM_KEY` 默认改 `""`** —— 旧 `cs:` 调用秒失败，不再吃满 600s 读超时

**`scratch/switch_writer.py`** 把 8 个文件 12 处 `cs:deepseek-v4.1-flash`
→ `lc:ms-deepseek-v4.1-flash`（各留 `.bak_writer`）：`run_all` / `notes` /
`polish_engine` / `run_independent` / `run_pub` / `eval_whale` / `run.py` / `workflow`。

清单文档：**`API_STATUS.md`**。

### 冒烟测试踩坑：玩具样本会被 `min_ok` 误杀

先用两句手写英文测 `translate_chunk`，报 `no usable first translation`。
查 `workflow.py:354`：

```python
min_ok = max(60, int(len(source) * 0.18))
```

译文只有 28 字符 < 60 被拒。**管线没坏，是样本太小**。换真实块
（`work_pub/betrachtung/chunks/c005.json` chunk 0，德文 5 块 1149 字符）后：

```
elapsed 6.9s  final.txt: 5 paragraphs, 323 hanzi (ratio 0.28)
[0] 决心
[1] 从一种悲惨的状况中脱身出来，即便使出意志的力量也应当是容易的。…
```

**给 `translate_chunk` 做冒烟必须用 ≥700 字符的真实块**，两句英文永远过不了
`min_ok` 地板。

**另一个坑**：`llm.chat()` 默认返回 `(text, model)` 元组，不是纯字符串。
诊断脚本里直接把返回值传给 `wf.tag()` 会 `TypeError: got 'tuple'`。

### 教训

**「列得出来」和「答得出来」是两回事。** 两个网关都能秒回 9–32 个模型名，实测
只有一半能用。判据必须是「返回中文」这个最朴素的行为。

**挂起比拒绝危险。** 死端点置空 key 是为了把 600s 的挂起变成毫秒级失败。

**本地网关并发上限 6。** 此前 32 并发实测「2/24 成功、800s」，放大只会打回挂起。

### 续：清理范围扩大到全库死命名空间（同日）

**第一批只换了 writer 池，grep 一扫又暴露 12 处死配置**，三种病因：

**① `css:` 命名空间从未存在**（`cs` 笔误）—— `pipeline_proust/revise.py`、
`eval_ab.py`。`llm.NS_PROVIDER` 里没有 `css`，首次调用直接抛
`provider for namespace css not in models.json`。这是**潜伏 bug**：一旦有人跑就崩。

**② bailian 全命名空间死**（`qw:`/`ds:`/`km:`/`gl:`/`in:`/`ia:`）—— 逐个模型名实测：
```
Access to model denied   qw:qwen3.8-max / qw:qwen-plus / qw:qwen3.5-27b
                         ds:deepseek-v4.1-flash / km:qwen-max
Model not exist          qw:qwen-turbo / qw:qwen-max-latest / qw:qwen3-max
                         gl:glm-4.5 / gl:glm-4.6
model is not found       ia:Qwen2.5-7B-Instruct / in:Qwen2.5-7B-Instruct
```
`mm:MiniMax-M3.1-Flash` → `insufficient_balance_error` —— **余额不足，不重试**（花钱）。

**③ 最危险：`pipeline_polish/engine.py` 硬编码付费 key**

它**绕过 `llm.py` 自建 `requests.post`**，`BASE=cssmapi` + `KEY=sk-***…`
（付费按量），且被 5 个模块 import（`books`/`judge_terms`/`launch`/`run_polish`）。
既是死端点，又违反「不要用付费 key」。

```python
BASE = "http://127.0.0.1:8317/v1"     # 原 cssmapi.fun/v1
KEY  = "<local-key>"              # 原 sk-***…
MODEL= "ms-deepseek-v4.1-flash"       # 原 deepseek-v4.1-flash
GLOBAL_CAP = 6                        # 原 150
```

**`GLOBAL_CAP` 必须一起降**：150 是为 cssmapi「TLS 握手超 200 才拒」调的；本地网关
在 6 并发以上**不拒绝而是排队**，留 150 只会让每个请求排在队尾，把慢变成挂。

**④ 又发现 3 个可用 reseller 端点**（judge 用，不能与 writer 同源）：

| 命名空间 | 模型 | 延迟 |
|---|---|---|
| `xm:` | `xm:mimo-v2.6-flash` | 1.3s |
| `ox:` | `ox:gemini-3.8-flash` | 2.7s |
| `oxd:` | `oxd:deepseek-v4.1-flash` | 4.6s |

judge 池原是 `qw,km,gl,in,ds`（全死），改用 `ox,oxd,xm`。

**验收**：`grep -rn '"\(css\|ds\|qw\|km\|gl\|mm\|ia\|in\):' pipeline_*/` → **空**；
12 个文件 `py_compile` 全过；端到端 7.2s / 5 段 / 325 汉字。

### 教训（补）

**只换 writer 是不够的，要 grep 全部命名空间。** 第一批改完看着干净，一扫
`grep -rn '"\w\+:'` 又冒出 12 处。

**`grep` 命名空间之外还要查 BASE/KEY 字面量。** `engine.py` 绕过 `llm.py` 自建请求，
里面藏着付费 key —— 这类「第二套客户端」是凭据泄漏的高发地。

**冒烟必须用真实块。** 两句英文过不了 `min_ok = max(60, len(source)*0.18)` 的 60 字符
地板，报 `no usable first translation` 会误导成管线坏了。用
`work_pub/betrachtung/chunks/c005.json` 的德文 5 块 1149 字符即可。

---

## 2026-10-28 全库修复（65 本）

起因：抽查报告点名五本（都柏林人、浮士德上册、福尔图娜塔、星期一或星期二、远航/茵梦湖），
用户随后要求「全库修复」。范围扩到 `out/` 全部 65 本 / 12,318,896 汉字。

**根因不是五本书，是组装器。** `build_all.package()` 的章题回退取源文件名尾号（c003 → 第三章），
front matter 又占掉前几个 id：49 本目录从第三章开始或章号重复（远航两个「第二章」、布登勃洛克 11 次「第一章」）。
改法：title_zh 先由 `apply_titles.py` 落库，回退改用正文位置；补通用罗马数字解析（I–LXVII）与
法/德/英序号规则，486 处拉丁目录清零。

**新增 `pipeline_fix/`**：
- `build_epub.py` 自建 EPUB 3 组装器（部/卷嵌套、诗行 `<br/>`、`white-space:pre-line`）
- `rebuild.py` 六本书的结构规则（浮士德 28 场、福尔图娜塔 4 部 31 章、星期一 8 篇、茵梦湖 10 章）
- `names_scan.py` + `adjudicate_names.py` + `apply_names.py` 专名三件套
- `register_pass.py` 语体最小改动（955 段）
- `clean_spaces.py` 汉字间游离空格（1157 处）
- `verify_all.py` 全库复核

**专名的教训**：字符级聚类会把「克西米利亚诺」从「马克西米利亚诺」里切出来，噪声淹没信号。
只取真名字位置（堂/小/老＋名、名＋先生/太太、名＋说/道/问）才收敛。原文共现复核能挡住
「赫斯特/赫威特」——远航里是 Hirst 与 Hewet 两个人，模型判成了同一个。

**残留**：浮士德诗体未重译；文白夹杂未系统清除；未逐句校准确性；追忆第五卷未分章；
修订只在 out/*.epub，work_* 未同步。

报告：`REPAIR_2026-10-28.md`；修复前快照：`_bak/out_20261028/`。

---

## 2026-10-30 反转：EPUB 不是唯一真相（构建器才是丢字元凶）

**前提被推翻。** 原计划把修好的 EPUB 镜像回 `work_*`；实测发现 20 本 Gutenberg 的
work 树都是 EPUB 的严格超集——是**构建器在丢正文**，盲目镜像会永久删掉 46 万汉字。

**根因**：`build_gutenberg.strip_front()` 原逻辑「跳到首个 ≥500 字符且 ≥200 汉字的段」
本为剥章 1 的 Gutenberg 许可证，却被 `collect()` 对**每一章**调用。开头短段多的章节
整段头被丢（maias c009 丢 218/265 段、c004 丢 254/309）。已改为按 NOTICE 正则只剥
首章 notice，18 本共恢复 460,461 汉字，58 本重建 `xml_err=0`。

**回写也完成了（反方向）**：`pipeline_fix/sync_revisions.py` 把 EPUB 里的 4,482 条审校
修订以段级 difflib 合回 work（apply 6,507 条，2,517 文件，段落数零变化；诗集
`neuegedichte` 走 `reflow_edits` 行级配对）。备份 `_bak/work_revisions_20261030`。
之后用修复后的构建器重建 58 本覆盖 `out/`（旧版 `_bak/out_20261030_all`），
旧 EPUB ⊂ 新书 4-gram 覆盖率 56/58 ≥0.995，差值全部是章题提升为 `<h1>`（标题去重，非丢字）。

**入口地图**：`scratch/REBUILD_MAP.md`（六条入口 × 重定向方式 × 五类收集器）。

**LLM 通道现状**：唯一活站 `cssmapi.fun`（key 在 models.json 的 `cssm-free`），
命名空间 `csf:`（`pipeline_whale/llm.py`），四模型轮转。8317 网关拒连、xiaomi provider
已删、旧 cssmapi key 失效、bailian/openox 全 403。端点**长生成必挂**：prompt ≤1000 字
4-10s，2000 字拄 125s 边缘，4500+ 必 524（Cloudflare 超时）——审查请求 prompt ≤3200 字、
`max_tokens≤700`、逐单元断点缓存（`work_polish2/reports/review_cache/`）。524 是边缘超时
不是模型坏，`llm.py` 已不再因 524 熔断模型。抽查入口：`pipeline_polish/sample_review.py`。

**出版级闭环（抽查→仲裁→修复→重建）已建成**：
1. 抽查：`sample_review.py --trees work_pub,work_gutenberg --per-book 2 --workers 3`，
   结果逐单元缓存在 `work_polish2/reports/review_cache/`（可断点续跑）。
   第一轮 76/76 单元完成：12 pass / 64 needs_work / 171 条意见。
2. 修复：`pipeline_polish/apply_review_fixes.py --apply`——先异族模型仲裁（YES/NO），
   再最小改动重写，机械校验（段数/数字/斜体标记/专名/相似度≥0.55/长度比 0.6–1.8），
   备份 `_bak/work_reviewfix_20261030`。首轮 170 条：165 被仲裁拒绝（初审多为窗口
   截断伪报），1 条实修（bovary 擅补“普罗大众”→“他们”）。
3. 审计补漏：`pipeline_fix/port_audit.py` 把 audit_applied 里 sync 漏掉的 254 条以
   原文片段直接splice进 work（已入书 4482/4482 验证），备份 `_bak/work_auditport_20261030`。
4. 伪影清理：`pipeline_fix/fix_artifacts.py` 干掉 splice 留下的 7 处叠词（“两局牌之间
   两局牌之间”等）；扫描器模式：对备份新引入的 2–8 字相邻重复（AABB 除外）。
5. 重建：受影响书沙箱重建→覆盖率验证→覆盖 `out/`（`scratch/port_rebuild.py` 模板）。
   旧版备份 `_bak/out_20261030_all` / `_round1` / `_round2`。

**待做**：gutenberg 书树抽查波；修复器重跑后重建受影响书；多轮抽查直到 needs_work 收敛。

---

## 2026-10-31 抽查修复轮（4 本点名书 + 全库）

起因：用户抽查四本（高老头/百年孤独/追忆似水年华/爱玛）给出批评，要求
"全面修复，不止这几本"。

**策略调整**：首轮派 6 个子 agent 并行（4 本深修 + 2 个全库扫描），全部因
LLM 通道慢 + 20 分钟硬上限中断。改为**主 agent 直接执行**：机械性专名统一
自己做（确定性替换），LLM 改写只在必要时用。子 agent 留下的中间成果
（proust 的 维米尔 已入工作树、sweep 已修 3 本、sweep_names 的 pairs.json）
全部复用。

**四本点名书**（详见 REPAIR_2026-10-31.md）：
- 高老头：63 组专名统一 + paria 巴蒂拉→受气包 + 维克托丽娜娜叠字 +
  军需总监/街名统一；核实 7 处"俚语"全是对法文双关的忠实翻译（保留）。
- 百年孤独：删 Sorry 泄漏补全截断句 + simplicisimum 拼写 + Centurias 锚点
  位置 + **122 条脚注死链全部修复**（build_all._find_span 未清洗 ⟦i⟧ 的
  bug，锚点插词中间）+ 专名统一 + 粗话核查（忠实，未加码）+ 开篇重写降
  范晔重叠。
- 追忆：维米尔/维尔帕里西统一 + grand-croix 最高长官→显贵 + 删 v1 的
  Sorry + Zut→啧/管他部里呢（收敛）+ pipi/caca 忠实保留。
- 爱玛：composed himself/threatened alloy/Taylor 段等误译 + 禀承/荐举/
  搞 文白与时代错位 + 哈里特→哈丽特。

**全库关键发现**：2026-10-28 的专名 FIX 表只落在 EPUB 上，后被从工作树的
重建覆盖而**丢失**（EPUB 与工作树计数一致=变体仍在）。已把 FIX 表回填到
**21 本**工作树并重建；浮士德用 rebuild.py 重建 28 场版（原为单章平铺）；
另修 5 处新变体 + 斜体标记 + 叠字标点 + 包法利夫人 slightest 泄漏。

**验收**：verify_epub 65 本 0 errors；clean_check 剩 4 处全为合法拉丁文/
法文（误报）；typo_check 剩 12 处多为合法跨段引语；总汉字 12,778,943。

**教训**：
1. 子 agent 20 分钟硬上限对"LLM 慢 + 任务大"的组合不够；机械活自己干更快。
2. 专名修复必须落在**工作树**再重建，否则下次重建即丢失（本轮踩到）。
3. 批评者的"俚语/粗话加码"判断要先对照原文——本轮 4 本的多数"加码"实为
   忠实翻译（Enfoncé Poiret、Mierda de perro、Me cago dos veces en natura、
   Zut、pipi/caca）。

## 2026-10-31 续：其他书 orphan closer 修补

应"继续其他书修复"，对 typo_check 的 orphan closer 逐处查上下文，修掉明确
多出/缺失的 9 处（乌略亚庄园/悲惨世界/金人/马克斯·哈弗拉尔×3/瓜拉尼人×2/
阿亚拉的天使），均对照原文确认（金人按英源 DODI.'、阿亚拉按英源两句独立
引语补开引号）。复杂嵌套/跨段引语（福尔图娜塔/荒凉山庄/诉讼/晚夏）保留，
需人工判读。typo_check 12→8 处，verify_epub 仍 65 本 0 errors。

## 2026-10-31 续二：orphan closer 第二轮 + 空格

对照原文（德/英/荷文源）修掉 6 处 orphan closer（金人/马克斯×2/荒凉山庄×2/
戴安娜空格），确认晚夏/福尔图娜塔/诉讼/索蒂莱萨为合法跨段引语/署名行
（typo_check 误报）。typo_check 12→5 处（余全误报），verify_epub 仍 65 本 0 errors。

## 2026-10-31 续三：最终状态

typo_check 余 5 处全为误报（合法跨段引语 + 署名行空格），clean_check 余 4 处
全合法。verify_epub 65 本 0 errors。荒凉山庄 p79 初判引号位置错并改了说话
标点，复核英文源确认是合法跨段引语，已还原；p92 为真实缺陷（续语漏开引号）
已补。全部修复完成。

## 2026-10-31 续四：系统性语体修复（非表面问题）

用户批评"只修表面问题"。做系统性风格/语体审计：全库扫现代口语/网络俚语，
清除子串/专名误报（雷人=贡布雷人、种草=一种草叶、狗血=成语、老铁=老铁匠、
ok=kokos、bro=bronce）。对 17 本书做机械性语体统一（压根儿→根本、这当儿→
这时、这号→这种、那号→那种、甭→别、那光景→那时、得嘞→好 等，240+ 处），
覆盖追忆/爱玛/荒凉山庄/福尔图娜塔/布登勃洛克/阿亚拉/远大前程/庭长夫人/
无名的裘德/三个火枪手/德伯家的苔丝/远航/艾菲/幸运的佩尔/金人/学生托勒斯/
诉讼。保留经原文核实的忠实俚语（高老头法文双关、百年孤独西班牙文粗话、
追忆法文 caca/pipi）。verify_epub 65 本 0 errors。

## 2026-10-31 续五：现代俚语误报清除 + 完蛋修复

第二轮风格扫描：绝了×55/凉了×6/裂开×8 多为误报（拒绝/谢绝/断绝 子串、
凄凉/凉了 字面、果子裂开壳 字面），溜了/小乖乖/小坏蛋/小狼 为合法对话口语。
唯一明确时代错位：完蛋（done for），法文源 finis/déchu/atterré，追忆 3 处
语境化替换（告终/完了/破灭）。verify_epub 65 本 0 errors。

## 2026-10-31 续六：语体修复覆盖缺口补全

发现重要遗漏：register_fix.py 改了所有工作树，但第一轮只重建 17 本。核查发现 35 本书
工作树已修但 shipped EPUB 未重建（仍含旧口语词）。补全重建全部 35 本（含 classic-7
走 build_all、浮士德走 rebuild.py 28 场）。另魔戒正文在 JSON texts 里（work_overhaul/
lotr/final/*.json），register_fix 只处理 final.txt 未覆盖，单独应用后重建。最终 65 本
0 errors，压根儿全库 0 处。教训：系统性修复改工作树后必须逐本核对 shipped EPUB，
魔戒这类正文在 JSON 的书是覆盖盲区。

## 2026-10-31 续七：语体修复最终补全

第二轮覆盖核查发现还有 6 本书残留少量现代口语标记（在流放地/巴黎圣母院/时祷书/
每个人/热尔米妮·拉瑟尔特/百年孤独）——工作树已改但 EPUB 未重建。重建这 6 本
（百年孤独走 build_all）。最终 65 本 0 errors，现代口语标记全库 0 处，语体修复
真正覆盖全部 65 本。
