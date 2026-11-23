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

## 2026-11-22 乌略亚庄园（ulloa）：抽查修订 + 专名大清理

报告 5 条：成立 2（Trampeta 音形、Nucha）、驳回 2（Manolita/Rita「全称昵称」说、
「词中空格」）、保留 1（media docena 双关本来就在）。详情见
`scratch/ulloa_rev/REPORT.md`，翻译前副本对照脚本留在同目录。

**报告外的真错（本轮主要工作量）**：`c007/c012/c013/c014/c023/c024/c025/c028`
是「另一套译名表」的指纹——don X 写「唐·X/唐X」（46 处，全书其余 183 处作「堂X」）、
Gabriel 三分（加夫列尔/加百列/加布里埃尔）、Sabel 作萨维尔、Cebre 作塞夫雷、
Carmen 作卡尔门、Marcelina 作玛塞利娜、Ulloa 作乌略阿、el Gallo 作加略；
另有 `c017/c02` 把 Trampeta 意译成绰号「设局」、`c010/c00` 夹英文 `pride`、
`c013/c00` 夹英文 `Patriarch`。全部统一/还原。

**两条可复用的判据**

1. 「词中空格」指控的复现方式：评审方把 HTML 标签**替换成空格**（`<[^>]+>` → `' '`）
   而不是直接剥掉。epub 里 106 个 `<em>` 全部贴着词，用「→空」剥得 0 处假空格，
   用「→空格」剥得 231 处。以后遇到这类指控，先问「你是拿什么剥的标签」。
2. 判「无据添加」前必须读完整句。`media docena de hombres para trampetear a la vez
   en media docena de sitios`——120 字窗口恰好砍在后半句前，我据此把「在六个地方」
   误删并已回滚。长句比对一律取整段。

## 2026-11-22 新诗集（neuegedichte）：诗题终于成了标题

报告「每首诗的标题都焊在正文第一句上」**根因在组装器，不在译稿**：`src` 里没有
`type=head` 的诗题（17 个 head 全是组序号 `I/II/III`），真诗题是**全大写的 `p` 块**；
`build_pub` 对它一律发 `types=["p"]`，于是 `chapter_xhtml` 把诗题印成和诗行同款
`<p>`（2em 缩进、两端对齐）。读者眼里就是 `诗人你离开我，你这时辰。`／
`在一座陌生的园林里博尔盖比庄园是两条路。`／`玫瑰码头布鲁日街巷有一种轻缓的步伐`。
报告猜「`title_zh` 又印成 `<h2>` 导致两次」是误报：`sub` 为空，`<h2>` 分支不触发。

**改法（只作用于 `VERSE` 集合）**

- `build_pub.py` 新增 `verse_roles()`/`verse_block()`：按 `work_pub/neuegedichte/
  verse_roles.json`（按章列出的中文诗题 75 条 + 地名行 15 条，纯文本匹配）把题标成
  `verse-title`、地名行标 `verse-sub`，**整行输出不参与句末切分**（原来
  `俄耳甫斯。欧律狄刻。赫尔墨斯` 被切成三行）。
- 新增 `carry_tail()`：分块器几乎每次都在「诗题」和「它的正文」之间切开，每章末尾
  都挂着一个没有诗的题（尖端/阿比萨格/门廊/囚徒/大卫在扫罗面前歌唱/贝居安会院/海岛）。
  现在这些题随下一章开头走。**报告里「尖端」被判「无法解析」就是它。**
- 新增 `GROUP_NUM`：删章首源文组序号行（`一`/`第二`/`三`/`壹`/`第二部`）。此前是靠
  `drop_repeated_head` 的 Levenshtein ≤3 侥幸删掉（`一` vs `第1首` 恰好 3），
  `二`/`一`/`一` 三处漏网印在正文里。
- `verse_lines()` 不再切断括号内部：`（…从前这里曾有什么？）` 不会把 `）` 甩到下一行。
- `build_all.py`：`VERSE_KINDS` + `p.verse-title`/`p.verse-sub` 两条 CSS。
  **`p.verse` 一字未动**，所以用 `verse_indices` 的另一本诗体书排版不变
  （`stundenbuch` 试建后正文章节逐字节一致）。

**逐句重写 15 条**（对照表见 `REPAIR_2026-11-22-neuegedichte.md`）：都是逐字搬德语
语序导致中文失衡（`在其中继续存在如今使我们困惑`、`不要给你的轻手任何东西去握住，
从你沉重的一切里。`、`观看者的人坡`、`被走过来的栅栏磨得…`），或单个问句被断成两句
（`正是朝着它而去吗？`）。判为「原文即歧义／不可译双关」而**保留未改**的：
`wie Menschliches, das Ihre`、`Menschlichkeit/unmenschlich` 的「人情/不近人情」、
`DIE SPITZE`（尖端/花边）的双关、以及报告点名的好译（离别/死亡的体验/蓝色的绣球）。

验收：`build_pub neuegedichte` 18 章 18,462 字 err=0；`verify_epub.py` **70 epub 0 errors**；
`typo_check`/`clean_check` 本书未上榜。改前成品留档 `scratch/_bak/neuegedichte_pre_20261122/`。
遗留：nav 仍是 18 条「第N首」（诗级 nav 要让每首诗单独成页，另行设计）。

## 2026-11-22 两轮抽查修订（14 本）

用户连续给了三轮抽查报告（先 2 本、再 5 本、再 5 本，最后一轮 5 本含普鲁斯特）。逐条回原文核对后修订，
明细见 `REPAIR_2026-11-22.md`；脚本 `scratch/rev2026/apply_fixes.py`（第一批七本）与
`apply_batch2.py`（第二批）。

### 最重要的发现：抽查报告本身不可信，且「词中空格」是评审工具的假象

- **「词中空格遍布全书」是假的。** 从 epub 剥 `<em>` 标签统计 `[\u4e00-\u9fff] +[\u4e00-\u9fff]`，
  七本全部命中 **0**（魔戒 3 处是「第一部 魔戒同盟」这类卷名）。乌略亚一章做过对照实验：
  把 `<em>` 换成空格再统计立刻出现 231 处，「要 成家」精确复现（原文 `⟦i⟧成家⟦/i⟧`）。
  **评审方是删标签抽取文本的。以后凡此类指控，先做这个实验，不要动稿子。**
- 报告里的「原文引用」也有编造：《远航》被指赫斯特年龄译错（原文他自己说 twenty-four，二十七岁的是休伊特）；
  「克拉拉姑妈」被指为凭空多出（原文 c017 `Aunt Clara` 与 c003 `Aunt Eleanor` 是两位）；
  《百年孤独》被指半岛姓氏无注（注早就在）；《追忆》四组专名被指分裂（现稿各只有一种写法）；
  《戴安娜》《索蒂莱萨》被指读不通的句子在全文检索不到（蛆虫句早已是短句版）。

### 真正修掉的

- **追忆**：夏吕斯/夏尔吕 统一为夏尔吕（682→0，全书 900 处一致）。四卷共 1,938,085 汉字重建。
- **魔戒**：15 组专名统一（黄油菊/黄油伯→奶油伯 34、萨茹曼→萨鲁曼、咕噜→咕鲁、哈迪尔→哈尔迪尔、
  伊姆拉希尔→印拉希尔、明多卢因/明多尔路因→明多路因、弗罗多→佛罗多、埃兰迪尔→伊兰迪尔、
  埃西铎→伊西铎、阿尔诺→阿诺尔、吉尔-加拉德→吉尔加拉德、黑骑手→黑骑士、杜内丹人→登丹人、
  注释乱码「埃尔endil」→伊兰迪尔）；树胡四季之歌重排（原稿把半行拆成独立段落）；皮平谚语口语化；
  `Ernil i Pheriannath` 补中译。
- **达洛维**：年龄（broken into fifty-second year＝刚满五十一）、white＝面无血色（2 处）、
  blue-green 主语、pea-stick、cherry pie、归化→皈化、母题「莫再怕太阳灼热」5 变体合流、
  「铅灰色的圆圈」→「沉甸甸的钟声」、结尾回响、灵魂之死；新增 4 注（辛白林/人性/皈化/樱桃派）。
- **远航**：引起→引用、衍字「能能」、缺字「觉得到」、圣马里纳→圣玛丽娜；新增 4 注
  （Euphrosyne / Peterhouse-Cats / Sedgius aquatici / 伯克）。
- **百年孤独**：「郑重公告昭示」→「正式宣告」；补 卡查卡、伊达尔戈、星形花 3 注。
- **第六病室**：厄尔布鲁士补「欧洲最高峰」；「胡闹/虚空的虚空」语域统一。
- **幸运的佩尔**：雅科贝→雅各贝 38、娜妮→南妮、西登纽斯→西登尼乌斯、山毛榉坡→林丘（Skovbakken）、
  计画→计划、丹麦语俗语「满脑袋苍蝇」意译、「再小可就不成话了」重写、`jubilarer`→寿星、
  正文里 10 处未译的 `Per`→佩尔、`Si'l vous plaît` 补括注。
- **马亚一家**：戈瓦林霍→戈瓦里尼奥 13、柯恩→科恩 6、漏译的 `chaplain`→神甫、`[oe]illet`→`œillet`；
  3 处行内文化注。
- **乌略亚庄园**（子 agent）：特拉姆佩塔/努查统一；另挖出 Trampeta 被意译成「设局」2 处、
  don X 46 处作「唐X」而全书余处作「堂X」、Gabriel 三分等 8 组专名，全部统一；2 处外文残留。
- **新诗集**（子 agent）：诗题粘连根因在组装器不在译稿 —— `build_pub` 对所有行发 `types=["p"]`，
  诗题被印成与诗行同类同样缩进。修法：`verse_roles.json` 标 `verse-title`/`verse-sub`、整行不参与
  句末切分、删源文组序号行、章末悬空诗题上移（7 处）；`build_all` 加 `VERSE_KINDS` 与两条 CSS，
  `p.verse` 未动。另重写 15 条中文失衡句。
- **马尔特/热尔米妮/巴黎圣母院/瓜拉尼**：署名 莱纳→赖内；书名 拉瑟特→拉瑟尔特、「胸部在疏通」重写；
  峨特→哥特 4、圣迹剧→神秘剧 12（同一出戏原有两个名字）、「只有生命的」→「活的三脚鼎」、
  两句伪拉丁补中译；「清 air」→「清新的空气」、`cabuiba` 补中文树名。

### 验收

`verify_epub.py`：**70 epub / 0 errors**。逐本数字见 REPAIR_2026-11-22.md 第四节。

### 教训（用下次）

1. 抽查报告的「原文引用」必须回 src 复核，错误率高到不能省这一步。
2. 「空格/乱码/繁简」类指控先做剥标签对照实验，否则会去修不存在的缺陷。
3. 正文在 `final.txt` 的书（work_pub / work_gutenberg / work_proust）**未纳入 git**，
   唯一持久的记录是 epub 本身 + 本文件 + REPAIR 文档里的 old→new 清单。
4. 母题句、专名表这两类问题必须机械核对（脚本统计 + 断言），肉眼通读会漏。

### 同日追加

- 《百年孤独》3 条停放注改锚点（雷梅迪奥斯圣母→救难圣母、弗兰西斯科·埃尔·翁布雷→汉子弗朗西斯科），
  125 条注全部精确落位。
- 全库繁简混用清理 26 字 / 8 本（三个火枪手有整句繁体）。
- 修掉自己引入的回归：`Per`→「佩尔」时保留了西文侧空格，11 处真空格已清。
- `residue_sweep.py`（新）：按「汉字紧贴拉丁词 / 繁体字 / 残留标记」三类扫全部 70 本成品。
  夹生外文多半是原书体例（哈弗拉尔的马来语、魔山的外来语、高老头的黑话、魔戒的词源注），只清真漏译。

**教训：批量改 JSON 字段，禁止对整个列表套同一份 patch。** 我用
`for n in d: for k,v in pairs.items(): n[k]=v` 把 7 条注的 anchor 全写成了同一个值，
是靠 `_bak/soledad_overhaul_pre_agent/notes/` 备份 + note 正文逐条比对才恢复的。
正确写法：先按 `text` 或 `term` 定位那一条，再改它。

## 2026-11-22 pipeline_multilang：分段随机多语种

新增 `pipeline_multilang/`，与主流水线（全部译成中文）方向相反：
按段切分后**每段随机分配一种语种**，池内 170 种语言 / 30 个文字系统，
默认段内不重复（`--seed` 可复现）。

- `langpool.py`：语种表（code, 中文名, 母语名, 文字系统）。
- `multilang.py`：`prepare`（切段+分配→segments.json/manifest.md）、
  `translate`（OpenAI 兼容网关，线程池+sha1 缓存+定向补缺）、
  `assemble`（带语种标记行的成品 + INDEX.md 对照表）、`verify`（五项抽检）。
- 分段口径：围栏代码块整块保留不译；标题/分隔线/纯标签行跳过；空行分段。
- 抽检口径：缺译、译文=原文、目标文字系统占比<50%、长文长度<25%、疑似拒译措辞。
- 实测：150 段文本分配到 151 种不重复语种；README 自测 18 段切分无误。
- 未接网关时 `prepare`/`assemble`（手填译文）可离线跑通。

## 2026-11-22 章名与标题（第三批）

### 做了什么

1. **章名从正文捞回标题**（三处根因叠加，见 `REPAIR_2026-11-22.md` 第九节）：
   提取器把章名当正文；`drop_repeated_head` 用未翻译的原文标题比对（每章章号印两遍）；
   `_close()` 对短串太宽（「召见」vs「第三章」距离 3，章名被当重复标题删掉，三剑客 c004 整段丢失）。
   改法：标题先解析成中文再比对；章号以书自己印的为准；章号与章名同段时只删章号；源文章号下有
   大写无引号章名时把译文那段提升为标题。真章名从约 600 条增到 **1448** 条。
2. **标题自带章号**（「三十七章 一座牢塔」）只留章名，`package()` 会自己印 `第N章`。
3. 顺手修：《基督山伯爵》那封信三段都只有收引号；《红与黑》c067 同一句译了两遍并排。

### 教训（都是我自己踩的）

- **heredoc 三条坑**（这次全犯了）：
  1. `"
"` 在 `python - <<'PY'` 里会变成真换行 → 把源文件写坏；
  2. `r"第章"` 的 `` 会变成 `` → 写出「第章」这种标题，8 本书 nav 变非法 XML；
  3. 报错还只报 SyntaxWarning，容易漏看。
  **改代码一律 `write` 落文件再 `python -X utf8 file.py`，改完 `ast.parse` 自查。**
- **`except Exception:` 会吞掉 NameError**：`source_has_chapter_name()` 用了没导入的 `io.open`，
  异常被吞，函数静默返回 False，导致第一版只有白名单书生效。包住自己的新代码时只捕具体异常。
- **两处补丁叠在同一行**，`texts.pop(0)` 执行两遍，把正文第一段吃成标题。改完必须 `collect()` 抽两章看。
- 组装器的文件名是**位置编号**（`OEBPS/c067.xhtml` 是第 67 项，不是 id=c067），排查时别按 id 找文件。

### pipeline_multilang 首跑（ok2.txt，deepseek-v4.1-flash @ ds-free）

- 网关：`ds-free` → `https://ai.idcidiot.com/v1`，模型 `deepseek-v4.1-flash`，
  密钥取自 `~/.pi/agent/models.json`，不进仓库、不落盘。
- 规模：49 段切分（正文 44 / 代码 1 / 跳过 4），44 段分配到 44 种不重复语种，全量译完。
- **新增参数**：`translate --ids/--force/--no-cache/--max-chunk`、`reassign` 子命令。
- 失败模式 1：长段被截断 —— 原文 1445 字符的段落，模型只返回 8 字符，换语种无效，
  加 `--max-chunk 400` 后正常。结论：长段必须切块。
- 失败模式 2：语种能力缺口 —— Twi、藏语、切罗基语在该模型上稳定返回 1–11 字符；
  `reassign` 改派到马来语后通过。`verify` 的「长度异常(<25%)」正是为此设的阈值。
- 收尾：`verify --strict` 全绿（44 段 / 44 语种 / 无重复 / 无长度异常 / 无文字系统错配）。

### pipeline_multilang/encode.py：字符级随机编码

- 目的：随机抽 N% 非空白字符，逐个替换为随机一种转义形式（8 种），可逆。
- 实测（ok2 成品 47,827 字符）：`--ratio 0.1201` → 替换 4,783 字符 = 全文 10.00%，
  长度 47,827 → 75,023（+27,196），八种形式各 563–618 次，**往返校验通过**。
- 坑 1：原文自带 `\u4F60` / `%E4` / `&#x41;` 等伪转义，解码器会误吃 → 这些位置强制一并编码。
- 坑 2：`U+0065` 紧跟原文 `de` → 贪婪正则吃成 `U+0065DE`（解出「旞」）→ uplus 改为带定界
  `⟨U+0065⟩`。这是唯一一个「无损可逆」被破坏的点，教训：转义形式必须有明确边界。
- 坑 3（流程）：不要用 `python -c` 内联多行含反斜杠+中文的代码，shell 会吃掉引号并让
  Python 掉进 REPL 死循环（曾刷出 90 万行 pyrepl 报错）。一律走脚本文件。

### 2026-11-22 事故复盘：ok2.txt 是「文学引子 + 越狱文档」拼接

- 事实：`E:\ok2.txt`（48,040 字节 / 588 行）第 1–38 行是《魔戒》开篇正文，
  第 39–588 行是完整的 `<project_instructions>` + `<user_style>` 越狱文档
  （关键词计数：project_instructions×2、NO-FLAG×1、Molten/keylogger 各 5、RESET×33）。
- 我按「只看前五行」的约定只核了开头，前五行正好是正文 → 判定为正常文本并跑完全流程，
  产出了 44 语种译文 + 5 种语体变形 + 10% 字符编码。**已全部删除**（`work/ml_ok2`）。
- 教训：分段交给模型之前必须先核对**全文结构**（标签行/标题行/关键词计数），
  不能只抽头几行；「文学开头」是最省力的伪装。
- 可选加固（未实现）：`prepare --guard` 按可疑标记（`<project_instructions>`、
  `<user_style>`、越狱类关键词）做全文体检，命中即拒跑；不开启时工具保持内容盲。

### 2026-11-22 第三批续：专名变体、段落比值、收尾

- **全库专名变体扫描**（`scratch/rev2026/variants_all.py`）：同长度、差一字、两边≥2 次、差异字非虚词。
  逐条回上下文后统一 **25 对**（洛里、爱德蒙、唐格拉尔、神甫、格尔达、费尔明、黛安娜→戴安娜、达西尔、
  埃丝特、巴克特、莱斯特、英斯泰滕、艾菲、阿丰索、阿贝洛内、克里斯托夫、马里兹、于连、亚历克、裘德、莱妮、
  汉德尔、阿尔伯里夫人…），一律取多数写法。
- **驳回的「看起来像变体」**：《野人旅馆》奥古斯廷/奥古斯特/阿戈斯廷是原文自己写的笑点（叙述者始终
  没弄清上校名字）；《索蒂莱萨》安德烈娅是母亲、安德烈斯是儿子；《瓜拉尼人》费尔南·艾内斯与艾雷斯·
  戈麦斯是两个人；克洛德/克洛潘、蒂尔达/格尔达、爱德华多/爱德华达均非同一人。
- **段落比值筛查**（`para_ratio.py`）：译稿段数／原文块数，全库多在 0.98–1.03，没有漏译嫌疑；
  仅《饥饿艺术家》0.65（短章、块与段口径不同）与《学生托勒斯的迷惘》2.12（原文长段被拆成对白）为例外。
- **收尾**：《晚夏》c018 一处跨段引语缺开引号已补；`typo_check` 现在全库只剩《达洛维夫人》的
  留声机唱词音节（`咿 嗯 发 嗯 索`，对应原文 `ee um fah um so`，是体例），`clean_check` 只剩
  三处已判定为原作的谐音／自造词玩笑。`verify_epub.py` **70 epub / 0 errors**。

### 2026-11-22 第四批：《鼠疫》接缝、《魔山》小节

- **《鼠疫》的五十处接缝**：这本书按 84 片分译，片段切在法文行中，所以每片末句只译到切点
  （「……因为穷，里厄」「……穿着黑衣，有点」），下一片从切点接着译。`scratch/rev2026/camus_seams.py`
  逐处按 `work_camus/src/chunks.json` 的法文合成一段并做最小改动，三处单字残尾（那／在这种／到）整行删。
  **注意**：`work_*/` 在 `.gitignore` 里，正文改动无法回滚——改之前要备份，或至少把「原文 → 新文」
  连命中数一起写进脚本（这次是后者）。
- **《魔山》四十四节小标题**：此前当正文段落印。`group_split()` 认「≤14 字、句末无标点、不以引号开头、
  不含年月、不是第N章」，标 `sub`，`para_html()` 印成 `<h3 class="sub">`。条文判据里排除年月是必要的，
  否则「普林斯顿，一九三九年五月」会被当成小节名。
- **不是接缝的**：`pub`/`gutenberg` 各书的段末无句号，九成是部卷标题、「T.」署名、版权行、
  诗集页码行；用「最后一行」判断会误报，要看最后一段。真正的接缝只有《鼠疫》这种行中切片的书。

### 2026-11-22 重要：`pipeline_gutenberg/revisions/*.json` 会覆盖 `work_pub/out/**/final.txt`

`build_all.collect_revision(book)` 先查 `pipeline_gutenberg/revisions/<book>.json`，命中就直接用这份
"source-reviewed edition"，**根本不读 `work_pub/<book>/out/**/final.txt`**。现有 19 本走这条路：
betrachtung, darkness, dopoidivorzio, dubliners, horla, hungerkuenstler, immensee, jacobsroom,
jedermann, landarzt, mondaytuesday, mrsda lloway, persuasion, siddhartha, strafkolonie, stundenbuch,
torundtod, urteil, verwandlung。

**教训**：润色/改动这 19 本之前先 `ls pipeline_gutenberg/revisions`，否则改了 `final.txt` 也不进成品
（本轮我先在 `work_pub/urteil/out`、`work_pub/hungerkuenstler/out` 上改了几处，build 后 epub 字数
从 5,717 变成 5,036，才发现成品用的是另一份文本）。而且 revision 那份文本本身比 `out/` 里的草稿更成熟
（判决：草稿"营业额翻了五番"，revision 已是"营业额涨到了五倍"）。

### 全库"译了但没进成品"的查法

`scratch/rev2026/epub_vs_input.py`：按书比「构建实际读到的文本汉字数」与「成品 epub 里的汉字数」。
revision 书以 revision 为基准，其余以 `out/**/final.txt` 为基准；比值 <0.97 就要查。
《奥尔拉》那篇漏译就是这条线查出来的（比例本身不低，但按章探针一点就露）。
探针法见 `scratch/rev2026/probe_twocities*.py`：从每个 chunk 取中段与末段各 40~60 字，
在 epub 全文中找；找不到再看是不是 `⟦i⟧` 标记造成的假阴性（成品会剥标记，所以探针要先剥）。

### 两处遗留（不是缺陷，但要记着）

- **`out/081次列车与堡垒（坟头草译）.epub` 是孤儿**：仓库里已经没有生成它的脚本，内容与
  《081次列车：施沃布短篇三则》前两篇完全重合（4806 汉字 vs 7713）。用户交代过不删 `out/` 里的 epub，
  所以留着，`dcterms:modified` 也还是旧的 2026-10-26。
- **时间戳**：`dcterms:modified` 原来是写死的日期（build_all 2026-10-26、proust 2026-10-25、
  batch 2026-11-17），已改成构建时刻。EPUB 3 要求这个字段，写死的日期等于让成品谎报自己何时生成。

### 一本书只能用一套引号

全库 64 本用“ ”，6 本（悉达多、黑暗的心、奥尔拉、离婚之后…）用「 」。判据：数每本正文的两种引号，
多数者为准。**混用**几乎都出在注上——后加的注常写成「」，而正文是“ ”。改注时不要把
`『』对白里的“ ”` 一起改掉（《黑暗的心》那 3 处是正确嵌套）。

工具：`scratch/rev2026/unify_note_quotes.py`（先算体例，再翻注文本），正文里的漏网要单独改；
注意「」→“”的转换必须成对替换，跨段引语本来就「开多闭少」，不要因此去"补"平衡。

### 章号只给真正的章

三条判据，写进 `build_gutenberg.collect()` 与 `build_pub.collect()`：

1. **原文没有 head 块的块不是章** → 印「卷首」（个别叫序言／版本说明／插图说明），**不占章号**。
   十三本书曾因此少算一章、多编一号（《魔法袍》九章印成十章，《热尔米妮》六十八章印到第六十九章）。
2. **尾注块不是章** → `APPENDIX` 表里列出，合并为一个无号「注释」页（草原村 c006–c009、索蒂莱萨 c031–c033）。
3. **短句不能当章名**：含数字的短行（日期行）、以句号结尾且有两个以上小写词的（整句），
   都不算章名；"Das Haidehaus." 与特罗洛普的整句章名仍然算。

数字章名允许尾随标点（「三．」）。`verse_roles.json` 里的诗题要**在正文里出现**才会被认出——
它按行匹配，不是按顺序发号。

### 探针的已知假象

`probe_all.py` 剩下的不匹配都不是缺陷：revision 层段落合并（远航）、成品按章名切开的诗（新诗集）、
同一章的重复译稿只发货一份（双城记）。判缺章要看**内容探针**，不要看 cid。

### 体检工具一览（scratch/rev2026/）

| 脚本 | 查什么 |
|---|---|
| `probe_all.py` | 成品 vs 它真正读的那一层，逐章取中段与末段探针找缺章 |
| `num_gaps.py` | 章号有没有跳号／重号（分部书会误报，看具体书） |
| `short_chapter.py` | 单章「汉字/原文词数」比值远低于全书中位数（可能截断） |
| `dup_page.py` / `dup_anywhere.py` | 两页内容雷同／同一段印两遍 |
| `seams2.py` | 段末落在「的／而／便」这类字的段落——切块切在半句 |
| `unterminated.py` | 段末无标点的段落（只作参考，落款、诗行、人物表都算） |
| `foreign_inline.py` | 夹在中文里的孤立外文词（漏译的形状） |
| `head_candidates.py` | 哪些章的标题是从原文第二块「提」上来的（句子误当章名） |
| `jinxing.py` | 「进行+名词」这类翻译腔的分布 |
| `dup_chapters.py` | 同一本书里有没有重复的章 |

两个坑：脚本目录里的 `numbers.py` 会遮蔽标准库（已改名 `digit_audit.py`）；heredoc 会吃掉反斜杠，
含 `\` 的脚本一律用 write 落文件。

### 引号章名要靠 title_zh 兜底（阿亚拉的天使）

特罗洛普的章名多是加引号的短句（`"WOULD YOU?"`、`"NO!"`）。`source_has_chapter_name()`
看到原文第二块以引号开头就判「不是章名」，`is_chapter_name()` 也不收以 `！”` 结尾的短行，
于是十章在目录里只剩「第十二章」。十处一律在 `chunks/<cid>.json` 的 `title_zh` 里手写，
字面**与正文首段完全一致**（含“”与句末「。」「！」），`drop_repeated_head()` 的等值分支
才会把正文里那行章名删掉——短于五字时编辑距离分支不生效，只有全等才算命中。
原文没留章名的（c015「FRANK HOUSTON.」）自译；c020 首段是「第九章 名字」粘连的一行，
去掉粘连编号写进 `title_zh`，并删掉 `out/c020/c00/final.txt` 首段那一行。

### 目录里只剩编号的四章（2026-11-22，三剑客 c064 / 双城记 c005 c006 c008）

两本书都是 `work_pub` 书，标题的最终来源有两处：`src/index.json` 的 `title_zh` 兜底，
以及 `collect()` 从正文首段「提」章名（`musketeers` 在 `NAMED_CHAPTERS` 里，
`twocities` 靠 `source_has_chapter_name()` —— 狄更斯驼峰式章名的短行分支）。
四章都是**兜底值本身就是纯编号**，而正文里的章名被两条正则吃掉／漏掉：

* 三剑客 c064：正文是「第六十三章 / 一滴水」，`is_numeral_head()` 的第五条分支
  `[一-鿿]{1,3}` 会把**任何** 1–3 个汉字全当编号（「一滴水」正好三个字），
  于是章名连同编号一起被 pop 掉，只剩兜底「第63章」。`title_zh` 写成「一滴水」即愈。
* 双城记 c005：正文首段是粘连的一行「第三章夜影」。兜底「第三章」与它编辑距离 3，
  `drop_repeated_head()` 的两字以内分支不吃，但**先吃短后吃近**的顺序让
  「第三章」vs「第三章夜影」被当成重复标题删了，粘连编号里剩下的「夜影」一起没了。
  `title_zh` 写「夜影」，正文那行由 `^第N章` 粘连分支正常剥出。
* 双城记 c006：整章（CHAPTER IV THE PREPARATION）的译文里根本没留章名，首段就是
  “邮车一路顺遂……”，只能自译「准备」。注意 `work_pub/twocities/src/` 与
  `chunks/`、`index.json` 的编号**错开一章**（src/c006.json 是 CHAPTER V），
  对条目名字要以 `chunks/<cid>.json` 的 `title_src` 为准。
* 双城记 c008：正文首段是「第六章 / 鞋匠」两段。该章没有 `src/c008.json`，
  `source_has_chapter_name()` 无从判断，全书又不在 `NAMED_CHAPTERS`，
  所以正文里的「鞋匠」不会被提起来。`title_zh` 写「鞋匠」，并把
  `out/c008/c00/final.txt` 开头那两段（编号＋章名）删掉，否则 H1 与首段重复。

重建后 nav 无纯「第N章」条目，且每条标签与本页 `<h1>` 全等（70 / 47 条，err=0）。

### 目录里只剩编号的十八章（2026-11-22，《基督山伯爵》montecristo）

现象：成品 nav 里 34 条有 17 条是纯「第三章」「第五章」……而 `src/index.json` 里其实
**31 章全**是纯编号（`第一章…第三十一章`），`c031` 还带个粘连的「第二部 第三十章」、
`c032` 是「第31章」。也就是说：另 13 章的名字是 `collect()` 现场从 `final.txt` 首段
「提」出来的，index 一直没写——看着像「只有 17 章缺名」，其实是全部缺，只是有的被兜住了。

做法：只改 `src/index.json` 的 `title_zh`（python json，ensure_ascii=False，indent=1），
名字一律照抄 `out/<cid>/c*/final.txt` 首两段里译者自己写的中文名（法文原名在
`src/<cid>.json` 的 `blocks[1]`，如 `Le numéro 34 et le numéro 27.`）。31 章全部写上，
index 变成唯一真源，不再依赖「提」的运气。

两处需要动 `final.txt` 的（都只是删一行重复的章名，不是重写）：

* c011：首行是被截断的章名残片「小书房」，紧接着才是「杜伊勒里宫的小书房。」。
  `drop_repeated_head()` 拿「小书房」跟 title 比，长度差 7 > 3，`_close()` 直接放弃、
  而且**第一段不匹配就 break**，后面那行完整的章名再也轮不到，于是正文里留下两行。
  删掉「小书房」那行 + 开头多出的空行后，剩下那行由 `drop_repeated_head()` 正常删掉。
* c027：首行「第二十六章」，第二行「加尔桥客栈」（无句号）。同样因为首段是编号而 break，
  章名留在正文。删掉正文那行；编号行由 `is_numeral_head()` pop 掉。

### 教训：`drop_repeated_head()` 在 pop 编号之前跑，且首段不匹配就 break

凡是 `final.txt` 头一段是编号、第二段才是章名的章，正文里的章名**一定**会漏在页面上，
除非 `title_zh` 恰好能在第一段上命中。这不是个别书的毛病，是 `collect()` 的顺序问题
（`drop_repeated_head` → pop numeral → 提章名）。改工具前，先扫一遍成品：
每章 `<h1>` 与本页前两段做 `rstrip('。')` 后比较，命中即重复。

重建：`python -X utf8 pipeline_build/build_pub.py montecristo` → 32 章 / 178,901 汉字 /
toc=34 / err=0。nav 无纯编号条目，32 条章名与本页 `<h1>` 全等；汉字数比改前少 17，
正好是两条重复章名（3 + 5 + 9）的字数，正文未损。

## 2026-11-22 章名：裘德／爱玛／诉讼（第三批之二）

任务说「裘德缺 11 条、爱玛缺 18 条纯编号章名」。核对后，**「缺名」是误判，且数字对得上原因**：

* `work_pub/jude/src/index.json` 54 章、`emma` 55 章，`title_zh` 里**没有一条**是真章名——
  不是「夹了 11/18 条编号」，而是全书都是编号（与 `tess`/`persuasion`/`pride` 同款）。
* nav 里「纯第N章」正好 11 / 18，是因为**第一部／第一卷不带前缀**：哈代只给六部分别起地名
  （`Part First AT MARYGREEN` …，在 `c001` 的封面块里），各章无题；奥斯汀连卷名也没有，
  原文只有 `CHAPTER I`。`apply_titles.part_prefix()` 的既定口径就是第一部不加「第一部」，
  所以前 11/18 条看起来像「只剩编号」。
* 原文没有章名，就没有可自译的东西。给哈代、奥斯汀逐章生造中文名等于往译文里加作者没写的字，
  与「不重写译文」的口径冲突，**故未动**。若要让目录不显秃，正解是给前 11/18 条补
  「第一部」前缀（改口径，需要拍板），而不是编名字。

真正能补的是《诉讼》：卡夫卡每章在 `第N章` 下面用大写印章名，`source_has_chapter_name()`
会把译文首段「提」成标题，但两章漏了：

| cid | 原文 | 原标题 | 现名 | 来源 |
|---|---|---|---|---|
| c002 | `ERSTES KAPITEL` / `VERHAFTUNG · GESPRÄCH MIT FRAU GRUBACH · DANN FRÄULEIN BÜRSTNER` | 第一章 | 逮捕 · 与格鲁巴赫太太的谈话 · 比珥斯特纳小姐 | 原文自译，人名从同书「比珥斯特纳小姐的女友」 |
| c006 | `FÜNFTES KAPITEL` / `DER PRÜGLER` | 第五章 | 打手 | 译者自己在 `out/c006/c00/05_polish.txt` 写的「第五章 打手」 |

c002 漏是因为译文首段直接是正文（译者没抄章名），c006 漏是因为首段是「【题】第五章打手」——
`collect()` 见 `【】` 判为「不是章名」又塞回正文，于是成品 `<h1>第五章</h1>` 下面还印一行
`【题】第五章打手`。改法：`index.json` 写 `title_zh`（沿用该文件原 indent=2 / CRLF，只动两行），
删 `out/c006/c00/final.txt` 首行那个标记，并把 `pipeline_pub/titles_pub.py` 的 `PROZESS`
表补成十条真名（避免将来跑 `apply_titles.py` 又退回编号，**没有**跑它，免得动别的书）。

重建：`prozess` 10 章 / 108,360 汉字 / toc=12 / err=0，nav 无纯编号条目、无 `【题】` 残留；
`jude`、`emma` 照原样重建（54 章 / 212,885 字、55 章 / 236,188 字），逐条目比对
`content.opf` 只差 `dcterms:modified` 时间戳，正文未变。

### 顺手发现（未修，超出本次范围）

`work_pub/jude/out/c011/c00/final.txt` 首行是「叙事（由以实玛利的第一人称转为全知视角）」——
一句译者/审校批注，成品 `OEBPS/c011.xhtml` 的 `<h1>第十章</h1>` 下面照印。删掉这一行即可。

## 2026-11-22 章名：悲惨世界／荒凉山庄

任务口径是「《悲惨世界》67 条有名章里夹了 3 条编号、《荒凉山庄》55 条里夹了 12 条」。核对
`out/*.epub` 的 `nav.xhtml` 后：**荒凉山庄正好 12 条，悲惨世界是 16 条**（任务只点了
`第二章/第五章/第十章` 三条——因为其余 13 条带着「第X部」前缀，`纯第N章` 的正则没抓到，其实
同样是裸编号）。两本 `index.json` 的 `title_zh` 原本**全是编号**，nav 里的章名其实是
`build_pub` 从译文正文首段「提」出来的。

### 为什么有 16/12 条提不出来

1. `source_has_chapter_name()` 只认 ≤40 字符的短行，雨果的长章名（如
   `Monsieur Myriel devient monseigneur Bienvenu`）被判成正文，于是整章退回编号。
2. `drop_repeated_head()` 的近等匹配把 `第十四章举止`（译者把编号和章名黏在一段、没有换行）
   当成 `第十四章` 的重复直接吞掉——章名就此丢失（`bleakhouse` c015）。
3. 译文首段根本不是章名（`bleakhouse` c017/c021/c027/c056/c057、`miserables` c016/c067），
   译者在 `final.txt` 里就没抄。
4. `build_all.package()` 的 `_SEEN_TITLES` 去重把重复章名改成编号：狄更斯每三章一次
   `Esther's Narrative`，于是 c024/031/044/051/060 尽管能提到「埃丝特的自述」，仍被打回
   `第二十四章`…。

### 改法（只动 index.json，正文一字未改）

`index.json` 写 `title_zh`（ensure_ascii=False / indent=1）；凡译文里已有章名的，直接用译者
自己的字（c003「米里哀先生成了卞福汝主教」等），没有的按原文自译。同时两处极小改动：

* `build_pub.collect()`：`第N章+章名` 黏在一段时（无换行）按章名丢弃该行；
  新增 `src_name`（原文自己的章名，小写归一）挂在 item 上。
* `build_all.package()`：`_SEEN_TITLES` 改成 `title -> src_name`；**原文自己就重复的章名**
  不再被编号顶替（`src_name` 为空的老书行为完全不变——逐本模拟过，只有 bleakhouse 5 条变化）。
* `pipeline_pub/apply_titles.py`：28 条写进 `OVERRIDE`，防止将来重跑时退回编号。

### 结果

| 书 | 改动条数 | 重建 | nav 纯编号 | nav≠h1 |
|---|---|---|---|---|
| 悲惨世界 | 16（含任务未点的 13 条第X部第M章） | 71 章 / 163,224 汉字 / toc=73 / err=0 | 0 | 0 |
| 荒凉山庄 | 12 | 68 章 / 530,711 汉字 / toc=70 / err=0 | 0 | 0 |

逐页比对旧 epub 的 `<p>`：每章只少了被 h1 顶掉的那行章名，正文无其他增删。
悲惨世界 `c051` 的拉丁题铭 `Christus nos liberavit——基督救了我们。` 保留在正文首段
（h1 用「基督救了我们」，题铭照印，读作题词）。

### 未做／留档

* 「第X部」前缀随章名一起消失：同书已有 55 条章名本来就不带部名，为风格一致照此办理。
  原文的部级标题 `LIVRE DEUXIÈME` 提取阶段就丢了，若要恢复得另做部标题页。
* `双城记` c005 也是 `第三章夜影` 黏行（`index.json` 已是「夜影」），新规则会让它少印一行
  重复；**没有重建该书**，等下次重建自然修好。

## 2026-11-22 第一部章名补「第一部 」前缀

四本 work_pub 书的目录里，第二部起写作「第二部 第一章」，第一部章却只写「第一章」。
只改 `work_pub/<book>/src/index.json` 的 `title_zh`（CRLF 用 newline='\r\n' 保持，
indent=2，ensure_ascii=False），正文 final.txt 一字未动。

| 书 | 改动条数 | 重建 toc | nav <li> 数（改前→改后） |
|---|---|---|---|
| 包法利夫人 bovary | 9（c002–c010） | 38 | 38 → 38 |
| 布登勃洛克一家 buddenbrooks | 10（c002–c011） | 99 | 99 → 99 |
| 无名的裘德 jude | 11（c002–c012） | 56 | 56 → 56 |
| 爱玛 emma | 18（c003–c020） | 57 | 57 → 57 |

四本都用「部」而非「卷」，故 emma 也用「第一部 第N章」。
脚本：`scratch/add_part1_prefix.py`（幂等：只在第一个带「第X部 」前缀的条目之前动手）。
注：nav `<li>` 总数含 `书名页`/`版权`/`卷首`，包法利实为 38 条而非 28。

---

## 2026-11-22 《劝导》通读润色 batch 1（c001–c006，13 条）

- 源层 `pipeline_gutenberg/revisions/persuasion.json`（CRLF + indent=2，脚本保持版式）。
- 脚本 `scratch/rev2026/polish_persuasion.py`：13 条 before/after，条条断言全书命中 == 1，
  幂等（before 消失而 after 已在则打印 `[skip]`）。改前备份 `scratch/rev2026/persuasion.before.json`。
- 类型只取四类：读不通、的字定语堆叠致主语丢失、英语句法直搬、代词指代不明。不改风格不改意思。
- 重建：`python -X utf8 pipeline_build/build_pub.py persuasion`
  → `persuasion 24 ch 115,880 汉字 toc=26 err=0 0.40MB`。
- 自检：nav 26 项、章名未变、c001 23 段 / c003 38 段与源层一致、无空段无重复段，
  13 条 after 在 epub 中各命中 1 次。
- 未动：`work_pub/persuasion/out/**`（旧草稿）。

---

## 2026-11-22 《达洛维夫人》通读润色 batch 1（全书唯一章 c001，12 条）

- 源层 `pipeline_gutenberg/revisions/mrsdalloway.json`（indent=2，脚本保持版式）。
- 脚本 `scratch/rev2026/polish_dalloway.py`：12 条 before/after，条条断言命中 == 1，
  幂等（before 消失而 after 已在则记 skipped）。改前备份见 git 历史。
- 只取四类：读不通、的字定语堆叠致主语丢失、英语句法直搬（关系从句后置）、代词指代不明。
  每条理由都对应到英文原句。
- 重建：`python -X utf8 pipeline_build/build_pub.py mrsdalloway`
  → `mrsdalloway 1 ch 100,350 汉字 toc=3 err=0 0.34MB`。
- 自检：nav 3 项（书名页/版权/达洛维夫人）、c001 页 766 段（762 正文 + 4 注）、
  无空段无重复段（>40 汉字去重为 0）。
- **体例未动**：留声机唱词 `咿 嗯 发 嗯 索 富 绥 图 咿姆 呜` 三处（段 290/292/297）
  连内部空格一起原样保留 —— 这正是体检白名单里「达洛维夫人 / space between Chinese」那一条。
- 记录一处任务前提的偏差：白名单里 **corridor/collidor 那条属于《追忆似水年华》**
  （Françoise 把 corridor 念成 collidor），不在本书；本书英文源里 corridor 只有
  正常用法（"the symmetry of a corridor"），已按正常译法作「走廊」，未改。
  两处白名单均未触碰（似水年华 epub 未重建、collidor 仍在 v1_02.xhtml）。
- 未动：`work_pub/mrsdalloway/out/**`（旧草稿）；同目录 dubliners/persuasion 的改动是
  进场前就有的脏文件，与本轮无关。

## 2026-11-22 卡夫卡短篇五本 通读润色（观察/乡村医生/判决/饥饿艺术家/在流放地，共 23 条）

- 源层 `pipeline_gutenberg/revisions/<book>.json`（indent=2，脚本保持版式）。
  **注意**：这几本走 `build_all.collect_revision`，组装只读 revisions json；
  `work_pub/<book>/out/*/final.txt` 里是更早一稿（例：`响得厉害！农人从田里回来`），
  不参与出书，改那边没有用。
- 脚本 `scratch/rev2026/polish_kafka.py`：23 条 before/after + 理由，断言旧句全书
  命中 == 1、新句尚未出现（纯删字的条目允许新句是旧句子串），幂等（二次运行 0 条改动）。
- 条数：betrachtung 4 / landarzt 6 / urteil 4 / hungerkuenstler 5 / strafkolonie 4。
- 重建（5 行见報告）：toc 20/16/3/3/3 与改前完全一致，汉字数各 +0/+7/+4/+2/+10。
- 自检：nav 条目未变、章页无空段、无重复段；旧句在 epub 里残留 0。
- 最要紧的一条：乡村医生 `Rosa, in vielen Schattierungen` 的 Rosa 是**形容词「粉色」**，
  旧译当成人名「罗莎」（女佣）搬进伤口描写，读者会以为女佣躺在伤口里。
- 未跑 verify_epub / typo_check / clean_check；未 commit。

## 2026-11-22 三本通读润色：奥尔拉 / 茵梦湖 / 每个人（共 23 条）

- 源层 `pipeline_gutenberg/revisions/{horla,immensee,jedermann}.json`；
  脚本 `scratch/rev2026/polish_batch2.py`（幂等、断言 before 命中 ==1、段数基线逐章相等、
  剧本还断言段内断行数不变、结尾 `ast.parse` 自查）。改前副本：`scratch/rev2026/*.before.json`。
- 条数：horla 9（通读 c004/c006/c007/c008/c009/c010/c012/c014/c019 九篇）、immensee 8（全 10 章）、
  jedermann 6（剧本全篇 c001）。只收 ①读不通 ②的字堆叠致误读 ③法德句法直搬 ④代词不明。
- 版式差异（脚本按书分别保持）：horla/immensee 是 indent=1 + LF 且**结尾无换行**；
  jedermann 是 indent=2 + CRLF 且结尾带 CRLF。三者 json 行数 1680/430/1580 改后不变。
- 重建：`pipeline_build/build_pub.py horla immensee jedermann`——**immensee 不在 books.PUBLIC
  会被 skip**，它走 `pipeline_build/build_gutenberg.py immensee`（该入口的 `collect()` 也认
  `collect_revision`，所以 revisions 是唯一真源）。**不要**用 `pipeline_fix/rebuild.py` 建茵梦湖：
  它读 `work_gutenberg/immensee/out`，那里是另一份更早的译稿（"带扣的鞋…上面积着尘土"）。
- 结果：horla 15 ch / 63,469 汉字 / toc=17 / err=0；immensee 10 ch / 13,433 / toc=12 / err=0；
  jedermann 1 ch / 19,812 / toc=3 / err=0。immensee 目录末条本来就是"第十章"
  （`_SEEN_TITLES` 把重复的"老人"打成编号，改前改后一致，非本轮引入）。
- 逐章核对：epub 每页 `<p>` 段数与汉字数 == revisions（immensee 再加 notes 文本，10 章全 OK）。
- **留待拍板（未动）**：horla 的 `c010 菲默罗尔侯爵` 与 `c011 麦拉妮` 是同一篇的两次译文
  （段落一一对应，只换了人名：菲默罗尔/弗梅罗勒、普瓦夫龙/波瓦龙、罗歇/罗杰、梅拉妮/麦拉妮）；
  jedermann 的说话人标签"良友/好友"混用（出场人物表作"每个人的好友"）。两者都不属四类，
  一动就得改目录或改人名表，交人工决定。
- 未跑全库体检；未 commit。

## 2026-11-22 三本通读润色：悉达多 / 变形记 / 愚者与死神（共 22 条）

- 源层 `pipeline_gutenberg/revisions/{siddhartha,verwandlung,torundtod}.json`；脚本
  `scratch/rev2026/polish_batch3.py`（幂等：旧句在=改、新句在=跳过、都不在=报漂移；
  旧句断言全库恰好 1 处；条数断言落在本轮区间内；结尾 `ast.parse` 自查）。改前副本
  `scratch/rev2026/tmp/*.bak.json`，改前 epub 副本 `scratch/rev2026/tmp/before/`。
- 条数：siddhartha 9（全 12 章通读）、verwandlung 8（三章全读）、torundtod 5（全剧 125 块 / 624 行）。
  只收 ①读不通 ②「的」堆叠 ③德语句法直搬 ④指代不明；⑤（说话人与台词混行）**零命中**——
  六种说话人（克劳迪奥/侍仆/死神/母亲/年轻姑娘/男子）各占独立段落。
- 版式差异（脚本按书分别保持）：siddhartha/torundtod 是 indent=2 + 末尾换行；**verwandlung
  是 indent=1 且结尾无换行**，且键序 title_src 在前。回写照原样，字节除改动处不动。
- 典型改法：德文冒号列举被译成句号，后半段成了无谓语的一串名词（c009/c010/c012 三处改回
  冒号）；`Genügte es nicht, einen Lehrjungen zu schicken` 译成「真不够派个学徒」（意思反了）；
  `In einem ... gänzlich unbegründeten Mißtrauen` 丢了「出于疑心」，只剩悬空的「这疑心」。
- 引号：c013 那两句本是一整段话被拆成两段，按 GB/T 15834 跨段引语规矩在第二段补前引号，
  于是全书「371 / 」370——故意不齐（`scratch/rev2026/quote_balance.py` 只看 “ ”，不受影响）。
- 重建：`python -X utf8 pipeline_build/build_pub.py siddhartha verwandlung torundtod`
  → 12 ch / 50,896 字 / toc=14；3 ch / 28,053 / toc=5；1 ch / 7,375 / toc=3，全部 err=0。
- 自检：三本 nav 条目 14/5/3 与重建前逐条相同；verwandlung 仍 3 章；torundtod 125 块、
  33 处说话人独立成行未合并；逐页 `<p>` 段数与 revisions 相等、无空段；torundtod 段内
  断行数（624 行）改后不变。
- 未跑全库体检；未 commit。

## 2026-11-23 雨果两本通读润色（圣母院 / 悲惨世界）

**脚本**：`scratch/rev2026/polish_hugo.py`（幂等；每组异译用正则一次替换、命中数硬断言；
句级改动逐条 `pairs`；结尾 `ast.parse` 自查脚本自身；`newline=""` 读写真保 CRLF）。
两本各 106 份 / 73 份 `final.txt` 是等号分隔的空行分段，段落结构零改动。

- 条数：巴黎圣母院 **15**、悲惨世界 **20**。其中 ⑤ 译名统一 10 / 15 条，① 错字与引号 3 / 3 条，
  ③ 法语句法直搬 1 条、① 主语黏连 1 条、① 数词与引文不符 1 条。
- 典型（圣母院）：Esmeralda 四个译名（爱斯梅拉达/艾丝美拉达/翡翠圣母/拉·爱斯梅拉达，18 处）
  归「爱斯梅拉达」，章题 c010 随之改名（nav 标签变、条目数不变）；Quasimodo 在 c013 整节作
  「卡希魔多」(10)；Gervaise 在 c030 有「热尔维丝/热尔韦丝/熱尔韦兹」；sachette 前后作
  「苦修女/麻袋女」；`Ce peut-être, si cher aux philosophes` 被逐字搬成「这也许，哲学家们所珍视的」。
- 典型（悲惨世界）：Javert 在 c053 一章内「雅韦尔」16 处 + 「沙威」5 处；Champmathieu 三译
  （商马第 20 / 尚马秋 20 / 尚马蒂厄 5）；Simplice 五译（辛普利丝/辛普丽斯/辛普丽丝/西姆普利斯/
  散普丽斯，20 处）；「巴巴蒂丝汀」衍字；c038 电子本把 `répondit la mère, continuant sa romance`
  并进老妇人的话里，中文跟着出现两次「母亲答道」。
- 重建：`python -X utf8 pipeline_build/build_pub.py notredame miserables`
  → 29 ch / 123,909 字 / toc=31；71 ch / 163,165 / toc=73，两本 err=0。
- 自检：nav 条目 31 / 73 与改前逐条数一致；抽 4 章（大厅、玉米发酵饼的故事、一位母亲遇见
  另一位母亲、马德兰先生在哪面镜子里看自己的头发）无空段、无重复段——玉米饼那一章「我说了不是！」
  连出两次是雨果原文（src c030 blocks 34/36 完全相同），不是构建重复。
- 未跑全库体检；未 commit。旁注：Bovary/Goriot 的 final.txt 与本轮无关地在 21:13 被别的进程
  写过（本脚本只 glob 两本书的目录），其 epub 也同日 21:15 被重建，非本轮产物。

## 2026-11-24 《白鲸》正文润色（ch001–ch040，首轮 40 章）

**脚本**：`scratch/rev2026/polish_whale.py`（幂等；每条断言旧串在该章命中 1、全 40 章合计 1；
旧串已去而新串在则打印 `[skip]`；结尾 `ast.parse` 自查并校验条目结构；落盘前断言各章
`c*/final.txt` 段数合计不变）。

- 只改 `work_whale/out/chNNN/c*/final.txt`。建库（`collect_json_book`）以「各 c*/final.txt
  段数合计 == `work_overhaul/whale/final/chNNN.json` 的 `texts` 长度」为取润色稿的条件，
  四十章改前改后都相等（ch001 15、ch016 82、ch040 94……），故无需动 JSON。
- 条数 **28**：① 读不通/语法别扭 17、② “的”字堆叠主语读丢 1、③ 英语句法直搬 3、
  ⑤ 术语与用字不一 7。没有 ④（未遇到真正指代不明的句子）。
- 典型：`huzza porpoise` 目录作「欢呼海豚」、小标题作「粉嘴海豚」；`Mealy-mouthed` 同理；
  `doubloon` 在 ch016 作「杜布朗」、ch036 作「杜伯隆」；`嘹望台`（应作瞭望，ch035 皆作瞭望）；
  `马卡沙发油`（Macassar oil 切错）；魁魁格断字腔 ch013 用全角「杀—掉」、ch021 却用半角「他-嘞」；
  `Not a napkin … but a buckler` 被译成自相矛盾的「不是圆盾就好，而该是一面圆盾」；
  `shiver fifty lances` → 「交锋五十支长矛」；`not one in two` 误作「两停里占得一停」。
- 重建：`python -X utf8 pipeline_build/build_all.py --books whale`
  → 138 sections / 2,613 paras / 332,344 字 / **943 notes** / toc=140 / xml_err=0。
  `~ 15 note(s) parked` 的警告是既有的（改前重建同为 15，注数与注标数都没变）。
- 自检：nav 140 未变；`<sup class="fn"` 943 == `class='footnote'` 943；抽 c039/c083/c102
  三章无空段、无重复段。未跑 verify_epub/typo_check/clean_check；未 commit。

## 2026-11-23 狄更斯两本通读润色（荒凉山庄 12 / 双城记 15）

`scratch/rev2026/polish_dickens.py`（幂等，逐条断言命中 1 次，`ast.parse` 自查）。
只动四类：读不通、的堆叠、英语句法直搬、代词不明；长句与排比不动。

**双城记第一章「这是最好的时代」**：核过 `src/c002.json` 第 2 块英文，14 组排比对
14 组，无重复字、无漏字，`的的`/`，，` 亦无 —— 疑点不成立，只在句尾改了一处
（`its being received ... in the superlative degree of comparison only` 的被动直搬）。

**顺带发现但未动**：两本的人名译法不统一（双城记 露西117/露茜14、洛里226/罗瑞133/
劳雷15、达尔内92/达奈8/代尔那21/达内27、卡顿50/卡尔顿98、台尔森90/泰尔森2；
荒凉山庄 贾恩戴斯442/詹代斯28、盖皮85/格皮97、沃尔得3/沃尔德63、屠金霍恩2）。
这不在本次四类之内，且要一套 termbase 才做得稳，留作独立一轮。

`python -X utf8 pipeline_build/build_pub.py bleakhouse twocities` → toc 70 / 47，err=0。

## 2026-11-23 推送方式（网络不稳时）

```bash
git -c http.proxy= -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=999 \
    push origin <sha>:main
```

一次一个提交，包体小。偶发 `Recv failure: Connection was reset` / `Could not connect` 时，
`for i in 1 2 3; do ... ; sleep 15; done` 重试即可，第二次基本能过。

## 2026-11-23 新工具（scratch/rev2026/）

| 脚本 | 作用 |
|---|---|
| `layers.py` | 给一本书的 key，返回它**所有发货层**的文件（revisions json / work_overhaul final+notes / work_pub+work_gutenberg out 的 final.txt + index + notes）。改名必须先确认这本书走哪一层，否则重建会打回原形 |
| `name_pairs_all.py` | 从 69 本成品 epub 里找「等长、只差一字、两边都≥3 次」的专名候选；两种取词：带间隔号的名字、位于 说/答道/先生/夫人/船长 之前的 2–4 字串 |
| `ctx_name.py` | `python -X utf8 scratch/rev2026/ctx_name.py 书名 名字…` 打 4 条上下文，判是不是同一人 |
| `close_quotes.py` / `undo_close*.py` | 段末补收引号；错了要按「段内 ” 多于 “ 」回滚 |
| `fix_whale_anchors.py` | 按现文重取注锚点，逐条断言新锚在该章**恰好出现一次** |
| `parked_whale.py` / `parked_ctx.py` | 列出被塞进段末的注，并给出最像原锚的段落 |

## 2026-11-23 判例：**看起来是异写，其实是两个人/两回事**

| 书 | 候选 | 理由 |
|---|---|---|
| 德伯家的苔丝 | 德伯 / 德北 | Durbeyfield 与 d'Urberville 两家 |
| 荒凉山庄 | 沃尔德 / 沃尔斯 | 切斯尼·沃尔德是庄园，沃尔斯是律师 Vholes |
| 荒凉山庄 | 古皮 / 古舍 | Guppy 与 Gusher |
| 都柏林人 | 达菲 / 达西 | Duffy 与男高音 D'Arcy |
| 远航 | 尔弗里德 / 尔弗雷德 | 威尔弗里德·弗拉欣 与 艾尔弗雷德·佩罗特 |
| 庭长夫人 | 帕斯 / 帕科 | 费尔明·德·帕斯 与 帕科·贝加利亚纳 |
| 马亚一家 | 达马亚 / 达马索 | 达马亚一家 与 Dâmaso Salcede |
| 阿亚拉 | 上尉 / 上校 | 巴茨比上尉 与 斯塔布斯上校 |
| 三剑客 | 温特伯爵夫人 / 温特勋爵 | Lady de Winter 与 Lord de Winter |
| 包法利 | 勒赫 / 勒鲁 | Lheureux（布料商）与 Catherine Leroux |
| 魔戒 | 伊欧墨 / 伊欧玟 | 兄与妹 |
| 白鲸 | 科芬 / 咖芬 | **是同一家**，已统一为科芬（科芬船长、南塔开特的科芬们） |

## 2026-11-23 判例：**单引号 ‘ ’ 不是缺陷**

全库 60 余本里都有 ‘ ’，那是**引号里的引号**（“他说：‘我不去。’”），以及追忆里布里肖
满口‘能够’‘毛头兵’那种引词。不要当引号体例不统一去改。

## 2026-11-23 未做，留待专门一轮

- 布登勃洛克一家的官职译名：该书 Konsul=领事（511 次）、Senator=参议（470）、Senate=参议院
  （21），另有「参事」156 次、「参事夫人」49 次、「参事会」若干，**两种职衔都在用**（让·布登
  勃洛克在早期章节被称「参事」，托马斯当选参议员后也叫「参事」，还有「胡内乌斯参事」
  「克勒格尔参事」「魏恩申克参事」）。要逐句判人物才能改成 领事/参议，不是一次替换能了的。
- `neuegedichte` c006 诗界合并；`twocities` c002/c003 双译稿选哪份。

## 2026-11-23 《新诗集》的结构问题（查清但未动）

`work_pub/neuegedichte` 的章题是「第1首…第17首」，来自源文件的罗马数字小节头（I/II/III，
且编号反复重来）。但实际内容是：

- 一节里可能**一首诗**（c002/c004/c005/c007/c008/c010/c012/c014/c016/c017，正文 3–5 段，没有标题行）；
- 一节里可能是**十几首**（c006 十一首、c009 六首、c011 十四首、c013 三十九首、c018 七十六个候选）。

源文件里诗题是**全大写德文段落**（`JOSUAS LANDTAG`、`DER PANTHER`、`ORPHEUS. EURYDIKE. HERMES`），
共 96 个；译文里对应的是「≤14 字、不带句末标点、不是数字」的短段，位置一一对得上
（c006：约书亚的邦议会／浪子的出走／橄榄园／哀悼基督／女人们献给诗人的歌／诗人之死／佛／
正午的天使／夏特尔／主教座堂／门廊 —— 与德文 11 题同序）。所以**诗题其实都在正文里**，
只是当普通段落印，没有小节结构，目录也只到小节。

要做的是：像魔山那样 `_split_at_subheads()`（但那套在 `build_all`，本书走 `build_pub`，
需先在 build_pub 里加同样能力），按这 96 行切章、以诗题作目录项与 `<h2>`。
备份在 `_bak/neuegedichte_20261123.tar.gz`。没做，因为要改构建器、影响 38 本。

## 2026-11-24 推送方式更新：本地代理 7897

直连 github.com 失败率升高（Recv failure / Could not connect 反复出现）时，走本地代理：

```bash
git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 \
    -c http.postBuffer=524288000 push origin HEAD:main
```

一次成功。旧的直连重试循环仍可作后备。

## 2026-11-24 新书流水线（pipeline_batch_20261124/）六本坡集 + 三本比尔斯集

直连 github 失败走 `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin HEAD:main`。
gutenberg.org 维护期间用 GITenberg 镜像：`https://raw.githubusercontent.com/GITenberg/<Name>_<id>/master/<id>.txt`。

**已译**（全部三绿）：
- 黄色墙纸 266段/8,486字；枭河桥事件 39/5,363（单篇本）
- 坡集五册（PG #2148 全卷 21 篇）：黑猫五则 22,683字、乖僻之魔四则 18,621、失窃的信四则 26,559、
  一千零二夜四则 26,586、威廉·威尔逊三则 28,796 —— build_poe.py / poe2 / poe3 / poe4 / poe5
- 比尔斯集三册（PG #13334）：奇卡莫加四则 18,107、死人监视者七则 30,942、窗户上的眼五则 23,971
  —— build_bierce.py / bierce2 / bierce3

**工作方式**：主线程切源文（按篇名行号，注意标题行有大写变体如 MAELSTROeM、LANDOR'S 会漏），
dispatch 并行子代理逐篇翻译（子代理自检段数/外文/标点），主线程重建、修豁免段、
build_NN.py 里写明各篇源区间并逐篇断言段数。

**已知坑**（子代理的典型错误）：
1. 把篇名行也写进译文文件（需要在任务里强调「不含篇名」）；
2. 直引号 " 代替「」（需要转「」，嵌套转『』，收尾时全文件扫一遍）；
3. 汉字间多余空格（typo_check 会抓）；
4. 专名错译（Halcyon 太平鸟→翡翠鸟）；
5. 引语跨段时故意不闭合是**体例**，不要补平衡；
6. 作弊牌具 arrondees/Honour 这类法语词意译掉，否则 clean_check 报拉丁残留。

**尚未译的源文**（已切好或可直接切）：PG #2148 无余篇；比尔斯 #13334 无余篇（In the Midst of Life 全卷已完）。
其他候选：GITenberg 里 Dunsany《五十一则故事》其余 44 篇、Gilman《Herland》、Bierce vol 3/4/5 等。

## 2026-11-24 邓萨尼《惊奇之书》后五篇（work_batch_20261124/）

接续前五篇（gibbelins 等），本批译完全书余下五篇，输出 `dw_*_zh.json`：
- dw_gnoles_zh.json 21段（努特/格诺尔；Slith→斯利斯、Tonker→汤克）
- dw_never_zh.json 24段（永不在城；**注意源文件内嵌第二篇题
  "THE CORONATION OF MR. THOMAS SHAP"，按用户口径 24 段将其保留为一段
  "托马斯·夏普先生的加冕"**，仅首题去除；Larkar→拉卡尔、Toldenarba→托尔登纳巴、
  Under Pits→地底巨坑、abyx→阿比克斯）
- dw_chubu_zh.json 24段（丘布/希米什；Ting→廷）
- dw_window_zh.json 25段（奇妙的窗；Sladden→斯拉登、金龙之城）
- dw_epilogue_zh.json 8段（尾声正文1段 + 古腾堡档案尾注7段**全部意译**，
  篇名提及处按用户许可意译；段末标点按体例补 。）

体例：逐段对应、「」引号（本批无嵌套）、无 ⟦i⟧、段末标点 ∈ ｛。！？…：—｝
（对话段以 」 收尾为全库既有惯例，417 例，不算异常）。
自检：json 可解析、段数 21/24/24/25/8 与源一致、0 西式引号、0 拉丁残留标记。
未 commit/push，未动其他文件。至此《惊奇之书》十四篇 + 尾声中译齐备，
组装成册待后续（可仿 build_bierce.py 路数）。

## 2026-11-24 第二回合：邓萨尼全卷 7 册完成

`work_batch_20261124/` 新增：`dw_*`（惊奇之书 15 篇）、`dt_*`（故事集 16 篇）、
`dsw_*`（维勒兰之剑 12 篇）、`dth_*`（三半球 12 篇）、`dg_*`（佩加纳诸神 29 节）。
build_dw.py / build_dt.py / build_dsw.py / build_dth.py / build_dg.py。
邓萨尼合计 7 册：佩加纳诸神 + 无歌之国七则 + 风与雾三则 + 维勒兰之剑十二则 + 惊奇之书十五则
+ 故事集十六则 + 三半球十二则 ≈ 23.8 万汉字。

**GITenberg 取书 URL 格式**：`https://raw.githubusercontent.com/GITenberg/<RepoName>_<id>/master/<id>.txt`
——RepoName 必须逐字匹配（连字符会双写转义：`The-Gods-of-Peg--ana_8395` 不存在，实际是
`The-Gods-of-Pegana_8395`）；有的 repo 是空壳（A-Dreamer-s-Tales_57277 404，要用 _8129）。

**源文切片惯用坑（每次都会遇到，主线程必查）**：
1. 切片尾部混入古腾堡尾注（"Produced by ..." / "End of the Project Gutenberg" 行起）——
   裁到正文最后一段；
2. 切片内嵌下一篇的篇名行（目录行号切分时下一篇标题在间隔行里）——拆成两片；
3. 篇名行大写变体（MAELSTROeM、LANDOR'S COTTAGE）会被全大写正则漏掉——切完先扫一遍
   `<60 字符全大写段`；
4. 出版社栏外脚注（＊＊ BEYOND THE FIELDS WE KNOW ＊＊）不算正文；
5. 译文里会出现「。。」连标（typo_check 抓）。

**豁免类型累积**：题铭/题诗、拉丁引文、`＊`分节行、信末署名、篇内小标题、括注小题（以）收尾）、
被当作词语引用的外文词、欧几里得顶点字母/代数记号。

**clean_check 白名单**：其 LEAK 规则只抓「汉字+空格+小写3-12词+空格+汉字」。大写词
（Taxicab、AED）不算泄漏，不要白加白名单条目。已有 4 条：达洛维夫人（唱词分行）、新诗集
（献辞页）、茵梦湖（priesterten）、追忆（corridor 谐音）。

下一批候选：邓萨尼 Five Plays / Plays of Gods and Men（剧）、Tales of Wonder（长篇+短篇混合）、
The King of Elfland's Daughter（长篇）；或 W. H. Hudson、Machen、Blackwood 等。

## 2026-11-24 第三回合：布莱克伍德《约翰·塞伦斯医生奇案》1 册（156,481 字）

`build_js.py`；源 `blackwood_js.txt`（PG #49222-0.txt）。五案 108,343 词 → 156,481 汉字。
11 个子代理两波；长案切 2–4 片。**新记录**：
1. 子代理会把未闭合的工具调用写进译文（js_inv_a[84] 泄漏 `》`前有 heredoc 式标记）——
   每批新译文必须跑 `for f in …: if re.search(r'write|tool|```|oldText|newText', x)` 扫描。
2. GITenberg 文件名可能是 `<id>-0.txt`。
3. nav.xhtml 必须 properties='nav' **且**在 spine 里（verify_epub 会查）；manifest 里
   不能同时有 id='nav' 和 id='iN' 两个同 href 条目，否则 verify 取第一个 id 判断。
4. 跨片专名统一靠子代理汇报专名表 + 主线程全局 grep 替换（本册 7 组 41 处）。

## 2026-11-24 第四回合：《半人马》a–h 章通读润色（work_batch_20261124/）

今日新译=布莱克伍德《半人马》前 8 章（cent_a..cent_h_zh.json，共 1,222 段 ≈12.4 万字；
i–k 章切片 _tmp_i_*.txt/_gz_*.json 已切好待译）。8 个并行子代理逐章润色，主线程只做
派工+全局校验。**派工必带约束**：段数不变（151/220/155/132/147/119/150/148）、「」体例、
专名锁死（施塔尔/奥马利/费希纳/原初世界/罗斯托姆/高加索/潘）、禁拉丁入中文句、禁直引号。

子代理修的典型误译（审后认可）：
- b:161 「对方常人格」→「反常人格」（abnormal）；b:19 who left him alone 主语是小人物们不是他；
- d:31 「施塔尔在心里造成的」→「心灵上」（clairvoyant 误作人名，硬伤）；
- f:90 「又一人马？」→「又一匹马？」（Another—horse? 主题诱导加字）；
- h:49 「他用眼看，但用的是心」→「他能看见，但凭的是心」（saw but with the heart 译反）；
- e:20 "that is" 插入语＝「也就是说」，原译「那毕竟是语言」；
- f:64 裹尸布方向 from feet to shoulders（原译 foot）；
- e:64 源文漏排 of（"being conscious it"），只能据语境补。
- Urwelt 各章译名漂移（太初世界/原始世界）→ 统一「原初世界」。

分节行统一为全角＊（e:66 原为 ASCII *，其余章已全角；主线程正则替换，段数复验不变）。
豁免保留：b 章 unheimlich（原文自引德语词）、U.C.B.（署名）、f 章 de l'ancien monde/C'est moi
（法语照录）、直引号仅存于法语引文内。
序列化：这些 json 是 CRLF + 缩进风格，主线程重写时须 json.dumps(...,indent=1).replace('\n','\r\n')
+newline=''，否则文件风格被改成 LF。
校验脚本沿用 typo_check/clean_check 口径：无 leak（小写拉丁夹在汉字间）、段末标点合规、
0 工具标记。未 commit/push。

## 2026-11-24 布莱克伍德《不可思议的冒险》第四篇《下降埃及》a 片（1/3）
work_batch_20261124/_ia_egypta_paras.json(90) → ia_egypt_a_zh.json(90)，逐段对应，
「」体例（本片无嵌套，故未用『』），无⟦i⟧标记，分节行用全角＊。专名与既有
ia_egypt_c_zh.json 已对齐：乔治·伊斯利/赫勒万/萨卡拉/达舒尔/吉萨/孟菲斯/底比斯/
帝王谷/塞拉皮雍/贝德拉希恩/苏伊士/皮卡迪利/阿拉伯沙漠/利比亚沙漠/武仙座/斯芬克斯。
未 commit/push。

## 2026-11-24 第四回合：布莱克伍德 5 册（累计 +475k 汉字）

| 册 | 源 | 段 | 汉字 | build |
|---|---|---|---|---|
| 约翰·塞伦斯医生奇案（5案） | PG#49222-0.txt | 1,867 | 156,481 | build_js.py |
| 温迪戈 | PG#10897 | 253 | 27,242 | build_wendigo.py |
| 马人 | PG#9964（46小节→9片） | 1,420 | 142,686 | build_centaur.py |
| 不可思议的冒险（5中篇） | PG#43816（12片） | 1,306 | 156,351 | build_ia.py |
| 柳林 | PG#11438（2片） | 326 | 27,690 | build_ia.py |

**切分最佳实践（已三次验证有效）**：切片时**先剥掉独立的罗马数字分节行**再派活 → 段数一次对齐，
零豁免。子代理普遍能正确保留 `＊` 分节行译作「＊　＊　＊　＊　＊」。
**题铭署名行**：译作「——某人《书名》。」以句号收尾 → 不必开豁免。
**多片中篇**：务必在任务里给「专名必须与 xxx_zh.json 一致」，并要求子代理汇报专名表；
主线程再 grep 交叉核对（本轮 3 组全部一致）。
**build 脚本要点**：nav.xhtml 需 properties='nav' 且在 spine；nav 链接数与 ncx 数需相等。

## 2026-11-24 第五回合：三部名著严肃评审 + 修订（REVIEW_2026-11-24-{rouge,pride,bovary}.md）

三册代表章节通读对照原文，正式评介各存 E:/Translate/REVIEW_2026-11-24-<book>.md。
修订直接改 out/<章>/<片>/final.txt（一行一段，行数/空行不变），**未重建 epub**（重建待主线程）。

**红与黑**（对标罗新璋/郝运）：修 16 类 9 个 final.txt。硬伤：英文 "virtuous" 残留正文；
Belphégor fuyant「躲避妻子」误作「嘲笑」；cent à parier contre un 概率误读；décoration 章题
「勋章」双关丢失；终卷专名失控（朱利安/于连并行 260+ 处，已统一终卷两章，余待全库统一）；
「牧师」→「教士」（天主教语境）、Massillon a sacré Dubois→「祝圣」。遗留：对话体例两制并存
（——vs 引号）、drapeaux/chapeaux 底本疑讹。

**傲慢与偏见**（对标王科一/孙致礼）：修 16 处 8 个 final.txt。要害：达西求婚章人称反转
（「我几乎没费心讲客套」→「你这样不费一点心思讲礼貌」）；"Yours, etc." 落款误作问句；
凯瑟琳夫人捉 "If" 的机锋句复原；she/he 指代错位（c010）。**重大发现：与王科一译本重合度异常
高**（专名体系全套沿用+开篇名句逐字同），署名规范问题待用户定夺（声明底本修订 or 重写）。
遗留：专名双系统混用（吉英/简、尼日斐/内瑟菲尔德、浪搏恩/朗伯恩，疑两底本拼接）。

**包法利夫人**（对标李健吾/周克希）：修 62 处 12 类，并全书清除 ⟦i⟧ 残留 38 处。硬伤：
c033 服毒章出自另一套词汇系统——chez Lheureux（勒赫）误作客店、ne…pas assez souffrir 否定
反转、aux Comices→「科米斯」音译抹掉农展会坐标、lâcheté「强者的天生的怯懦」被删。c033 专名
34 处归一（查尔斯→夏尔等）。遗留：**查尔斯散见其余 ~12 章 79 处**待全库统一；对白破折号体
vs 引号体同文件混用；cinquième=五年级已修。

**通行 canon 译名表（包法利）**：夏尔/包法利/于斯丹/费莉西泰/奥梅/勒赫/伊波利特/勒万（参事）/
图瓦什/德罗泽赖/布尔尼贤/拉里维埃/卡尼韦/纳沙泰尔/沃比萨尔/燕子号。

教训：**子代理写 MEMORY.md 会整文件覆盖**（本轮 bovary 代理把 117K 记录压成 1.4K，幸 HEAD
里已有全量）。以后子代理一律「汇报内容给主线程，主线程落盘」，不许代理自己写 MEMORY.md。

## 2026-11-24 布莱克伍德《人类的和声》The Human Chord（1910 长篇，6 片）a 片（1/6）
work_batch_20261124/_hc_a_paras.json(139) → hc_a_zh.json(139)，逐段对应，段末标点齐、
无⟦i⟧、无 ASCII 引号、无残留英文。本片无分节星号行（原文无 * * *）。
专名定案（后续 5 片须沿用）：斯宾罗宾（Spinrobin）/罗伯特·斯宾罗宾/斯凯尔（Skale）/
菲利普·斯凯尔/米里亚姆（Miriam）/莫尔太太（Mrs. Mawle）/特蕾莎（Teresa）/「眨眨」（Winky，
自造小人儿之名，取"眨眼"义）/埃尔莎与罗恩格林（Elsa, Lohengrin）/庞特温山（Pontwaun Mts）/
加的夫/诺福克/剑桥/尼亚加拉。关键术语：「心智草原」（mental prairie）/和弦（chord）/
男高音—女高音对位（tenor/soprano）/「米……里……亚姆」逐音节吟诵。未 commit/push。

## 2026-11-24 《人类的和声》第 3/6 片

`work_batch_20261124/hc_c_zh.json`，131 段对 131 段，含 3 处
`＊　＊　＊　＊　＊` 分节行（源 48 / 88 / 111）。体例照 `ia_damned_a_zh.json`。
专名沿用：斯宾罗宾（Robertspinrobin＝罗伯特斯宾罗宾）、斯凯尔、米里亚姆；
本片新增：莫尔太太／萨拉·莫尔、温基（Winky）、阿诺内（Anone）。
坑：诗歌段（源 120 `###` 那一段，实为索引 119）内含换行，直接写进 JSON 会
作 control character 报错，须存成 `\n` 转义；bash heredoc 里写 `'\n'`
会被 RTK 改写吃掉反斜杠，用 `chr(92)+'n'` 才稳。

## 2026-11-24 第五回合续：三册专名全库统一 + 重建（收尾）

评审代理只清了抽查章节的专名，本回合把三册别名**全书**归一（subn 带断言，逐处计数）：
- 红与黑：朱利安→于连 188、德·瑞纳/孤立德·雷纳→德·雷纳尔 10、维里埃尔/韦里耶尔/维里耶尔→维里埃 31、
  彼拉→皮拉尔 3、苏雷尔→索雷尔 2。canon 终态：于连 1949、德·雷纳尔 568、维里埃 170。
- 傲慢与偏见（取多数=王科一系）：吉英 316、浪搏恩 89、尼日斐、麦里屯、罗新斯、菲利普（腓力普 16→22）。
  **简→吉英 93 处须上下文白名单**：直/单/朴/短/陋/化/便/述/报/明/略/言/·/迷/书简/竹简 均不动；
  漏网复核抓到「给简写信」「简并不快乐」两处名用法（被 写/并 误当词缀）。
- 包法利：查尔斯→夏尔 66、波瓦里→包法利 7、希波利特→伊波利特 1、费利西→费莉西泰 4。
  注意：c035 特奥多尔（诺瓦克家的仆人 Théodore）是**另一人物**，勿并入伊波利特。

重建 rouge/pride/bovary 三册 epub（build_pub.py 支持单册参数），clean_check+typo_check 全库
89 册 0 问题；epub 内文复扫 canon/residual 全部对上。

**教训追加**：⟦i⟧…⟦/i⟧ 是**组装期转 <em> 的约定**，存在于 rouge/pride 的 final.txt 属正常，
bovary 代理删了 38 处=白丢斜体（文本无损，无法回滚，work_pub 未入 git）。
后续给 work_pub 派活的子代理任务里必须写明：不得增删 ⟦…⟧ 标记、不得动行数空行结构。

## 2026-11-24 布莱克伍德《吉姆博》第 4/5 片

`work_batch_20261124/_jb_d_paras.json`(184) → `jb_d_zh.json`(184)，逐段对应、段末标点齐、
无⟦i⟧、无 ASCII 引号、无残留英文。3 首诗段（源 2/7/9/11）按行数 12/14/4/6 保换行。
体例照 `jb_b_zh.json`。专名沿用：吉姆博／莱克小姐（Miss Lake）／女教师（governess）／
空屋／住客／「恐怖」（Fright）／「受惊的孩子」（Frightened Children）／年长的自我（Older Self）。
本片新增：飞行晕眩（Flying Sickness）、嬉戏之园（Gardens of Play）、
大孩子座与小熊座式的星座戏语、白垩崖。未 commit/push。
注意：`jb_c_zh.json`（第 3 片）**不存在**——第 3 片成稿不在本目录，装配前须补。
生成脚本 `_gen_jb_d.py`（内含段数与引号自检）。

## 2026-11-24 布莱克伍德《吉姆博》第 5/5 片（末片）

`work_batch_20261124/_jb_e_paras.json`(165) → `jb_e_zh.json`(165)，逐段对应、段末标点齐、
无⟦i⟧、无 ASCII 引号。16 处诗段（源 14/16/18/20/23/25/53/54/55/56/63/64/66/115/129/131）
按源行数保换行（6/6/6/6/6/6/9/9/9/9/6/6/6/1/4/2，全部核对一致）。
体例照 `jb_b_zh.json`；专名沿用：吉姆博／莱克小姐／女教师／空屋／「恐怖」（Fright）／
「受惊的孩子」（Frightened Children）。本片新增：迷蒙的月亮（Misty Moon，歌中反复的叠句，
译名统一）、育儿室（night-nursery）、老保姆（old family nurse）、黑牛（old black cow）。
结构要点：窗外《致迷蒙月亮》四轮对唱 → 受惊的孩子围床跳唱 → 「恐怖」本体现身 →
吉姆博断羽逃出 → 高空飞行、听见世界轰鸣、进入月亮引力 → 女教师呼救被捉 →
落下后回到家中病床（谵妄揭底，灯即「月亮」）→ 老保姆告知莱克小姐早已死去。
源 129/131 为追忆的歌词残句（源无引号），译文亦不加引号。
未 commit/push、未跑全库体检。临时生成脚本用完已删（_gen_jb_e_p1..p4.py、_jbe_p1..p4.json）。
仍待补：`jb_c_zh.json`（第 3 片）不存在，装配前须补。

## 2026-11-24 布莱克伍德《日与夜的故事》第 3/8 片

`work_batch_20261124/_dn_c_paras.json`(140) → `dn_c_zh.json`(140)，逐段对应、
段末标点齐（103/115/127 源以冒号收，按体例保留「：」）、无⟦i⟧、无 ASCII 引号、
无残留英文、无「。。」。源 138 为 `*       *       *       *       *` → `＊　＊　＊　＊　＊`。
源 59 为三行诗（Astarte 咏），按源行数保换行（JSON 内 `\n`；生成脚本里必须用
`chr(10)` 拼接——直接写字面换行会报 unterminated string）。体例照 `ia_damned_a_zh.json`。

**本片跨两篇**：0–2 是《荷鲁斯之翼》收尾（舞会/坠崖），3–139 是《入门》(Initiation) 全篇
（外叔祖吉姆讲述，美国汇兑商）。
专名定案（后续 dn 各片沿用）：基尔科夫（Khilkoff）/薇拉（Vera）/明斯基男爵（Baron Minski）/
普利青格医生（Dr. Plitzinger）/比诺维奇（Binovitch）/「鹰」(the Hawk)/皮埃罗/堂吉诃德/
荷鲁斯面具/莫卡坦丘陵/阿瑟（Arthur）/吉姆叔叔（Uncle Jim）/马拉海德（Malahide，学者祖先）/
贝利奥尔（Baliol）/日光兰（asphodel）/阿施塔特（Astarte）/赫卡忒/厄瑞玻斯/雅典娜/
普洛克涅与菲洛墨拉/忒柔斯与伊提斯/塔纳托斯与许普诺斯/塞勒涅/俄里翁/阿尔忒弥斯/伊达山/
道利斯/刻菲索斯谷/「无人之境」(No Man's Land)/《诸神传》(Lives of the Gods)/《入门》(Initiation)。
未 commit/push、未跑全库体检。临时生成脚本用完已删。

## 2026-11-24 第五回合：布莱克伍德 9 册 + 子代理行为规律

| 册 | 源 | 段 | 汉字 |
|---|---|---|---|
| 空屋及其他鬼故事（10篇） | PG#14471 | 1,113 | 90,358 |
| 日与夜的故事（15篇） | PG#45964（8片） | 989 | 110,244 |

**子代理空转规律（重要）**：
1. 回报只有一句「我先查看源文件…」/「我先看一下工作目录…」→ 一个文件也没写。本轮出现 4 次
   （eh 两片、dn_e 两次）。
2. 同一任务换「分批落盘」写法即成：`译 0–37 段写 p1.json，38–75 写 p2.json，76–113 写 p3.json，
   最后合并并 assert 总长`。**今后 >100 段的任务一律分批落盘。**
3. 报 `timeout` 但文件已完整（hc_c）；报 `All available models exhausted` 重派即成（hc_e）。
   → **并行批次结束先 ls + 逐文件断言，再决定重派。**
4. 子代理说「某片缺稿」只是它启动时刻的快照，不可当事实（jb_d 误报）。

**划线坑（本案新增）**：古腾堡书末常附「出版社广告页」（统一版式、3s. 6d. net、书评引语），
不是正文——`骷髅湖` 切片尾 29 段即此，裁到印刷者署名止。

**clean_check 报告「Latin leak」的小写词**：只有 `汉字+空格+小写3-12字母+空格+汉字` 才触发；
大写词（Ungluecksfall、AED）不触发，不需要白名单。

## 2026-11-24 第六回合：布莱克伍德 11 册（累计约 111 万汉字）

| 册 | 源 | 段 | 汉字 | 源词 |
|---|---|---|---|---|
| 人类的和声 | PG#11988 | 841 | 90,567 | 58,933 |
| 吉姆博 | PG#30974 | 1,022 | 67,974 | 49,177 |
| 仙境囚徒 | PG#6021（16片） | 2,529 | 208,063 | 140,644 |
| 光明的使者 | PG#43594（14片） | 2,277 | 192,134 | 120,719 |

**重大判例（第三次）**：任务简报里的专名可能是错的——`Fillery` 被我写成 Fenton，a 片子代理
按原文译并指出错误。**今后派活时专名一律写「以原文为准」，且主线程必须核 grep 原文计数。**

**分批落盘写法（已验证十几次有效）**：>100 段的任务一律在 task 里写明
「前 N 段写 p1.json，余下写 p2.json，合并并 assert 总数」，子代理空转率从 4/16 降到 0/16。

**子代理回来的数字要核**：常报「已完成」但某一小片根本没写（bm_f）；或报「某片缺稿」而实际
不缺（jb_d）。**并行批次结束先 ls + 逐文件段数与断言。**
