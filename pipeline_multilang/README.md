# pipeline_multilang · 分段随机多语种

把一份文本按段切开，每段随机分配**一种语种**（池内 170 种语言、30 个文字系统，默认不重复），
逐段翻译后装配成「每段前一行语种标记」的成品，并出一份段号 / 语种 / 抽检结果对照表。

与主流水线的区别：主流水线是「全部译成中文」，这里是「每段译成不同的随机语言」，
用于多语种排版测试、字体回退检查、语种识别器评测等场景。

## 用法

```bash
# 1. 切段 + 分配语种（不需要联网、不需要密钥）
python -X utf8 pipeline_multilang/multilang.py prepare 文本.txt -o work/ml --seed 7

# 2. 逐段翻译（OpenAI 兼容网关）
export FREEAI_BASE=http://127.0.0.1:8317
export FREEAI_KEY=sk-local
export MULTILANG_MODEL=<网关里的模型名>
python -X utf8 pipeline_multilang/multilang.py translate -o work/ml --workers 4

# 3. 装配成品 + 对照表
python -X utf8 pipeline_multilang/multilang.py assemble -o work/ml --title "书名"

# 4. 抽检（缺段 / 占位 / 文字系统错配 / 长度异常 / 疑似拒译）
python -X utf8 pipeline_multilang/multilang.py verify -o work/ml --strict
```

产物：`work/ml/segments.json`（唯一真源，可手改译文）、`cache.json`（按
sha1(语种+原文+模型) 缓存）、`manifest.md`（人工翻译清单）、
`out/<标题>.multi.txt`、`out/INDEX.md`。

## 行为约定

- **围栏代码块整块保留**，不拆不译（``` 与 ~~~ 都识别）。
- **标题行、`---` 分隔线、纯 HTML 标签行**按原样跳过（`--keep-headings` 可改为参与翻译）。
- 空行分段；`--min-chars N` 把短于此长度的正文段并入相邻段。
- 语种分配用 `--seed` 固定，可复现；段数超过池容量时重洗第二轮并给出 warning。
- 缩池：`--only ja,ko,th` 或 `--exclude-script Hani,Latn`（想强制非拉丁文字时用后者）。
- 译文缺失不静默通过：`assemble` 默认报错，`verify` 逐条列出。

## 抽检口径

`verify` 会检查五项：译文为空、译文与原文相同（>40 字符）、目标文字系统字符占比 <50%、
长文译文长度 <25% 原文、开头出现「抱歉 / 无法 / 作为……模型」一类措辞。
文字系统覆盖率见 `out/INDEX.md` 最后一列；以拉丁字母为目标的语种（Latn）无法靠此区分，
需另做识别器比对。

## 已知限制

- 语种池里少数语种在网关侧模型能力较弱（如 Cans 音节文字、Tfng、Cher、部分 Cyrl 小语种），
  译文可能夹带拉丁转写或大量保留原文；`verify` 只报警不纠正。
- 表格按整块处理，逐行翻译可能破坏列宽对齐，宽表建议先转列表。
- `translate` 失败会在 `segments.json` 里写 `error` 字段，重跑只补缺段。