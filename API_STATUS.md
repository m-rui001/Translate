# API 端点状态清单

实测时间 **2026-10-26**。判据只有一个：**发一条英译中请求，看它是否返回中文**。
列在 `/v1/models` 里不算能用 —— 网关会枚举它接的任何上游，哪怕上游已经死了。

探测脚本：`scratch/probe_all_models.py`（41 个模型，6 并发，单次 120s 超时）。

---

## ✅ 可用：本地网关 `127.0.0.1:8317`

- **key**：`<local-key>`
- **base**：`http://127.0.0.1:8317/v1`
- **前缀**：`lc:`（`pipeline_whale/llm.py` 已接入）
- 32 个模型列出，**12 个真能出文**。

### 推荐（按译文质量 + 速度）

| 模型 | 延迟 | 速度 | 译文 |
|---|---|---|---|
| **`ms-deepseek-v4.1-flash`** | 1.1s | 43.9 tok/s | 老人坐在河边，等着鱼儿浮出水面。 ← **当前 WRITER** |
| `ms-qwen3.8-flash` | 3.0s | 49.7 tok/s | 老人坐在河边，等鱼上钩。 |
| `or-north-mini-code` | 1.3s | **76.0 tok/s**（最快） | 老人坐在河边，静静地等待着鱼儿上钩。 |
| `ms-qwen3.5-27b` | 23.8s（首包慢） | 67.6 tok/s | 老人坐在河边，等待着鱼儿浮起。 |
| `or-nemotron-3-ultra` | 1.9s | 29.4 tok/s | 老人坐在河边，等待鱼儿浮出水面。 |
| `cf-llama4-scout` | 0.7s | 20.7 tok/s | 老人坐在河边，等待着鱼儿浮出水面。 |
| `ms-nex-n2.5-mini` | 0.7s | 17.3 tok/s | 老人坐在河边，等着鱼儿浮上来。 |

### 可用但有输出污染（勿直接用作 WRITER）

| 模型 | 问题 |
|---|---|
| `cf-r1-distill-32b` | 带思维链前缀 `{'\n好，用户让我把一句英文翻译成中文…` |
| `cf-mistral-7b` | 译文后附英文说明 `(Note: This is a simple and direct translation…)` |

### 能用但慢/弱

`cf-llama3.1-70b`（12.2 tok/s）、`ms-mistral-large`（7.9 tok/s）、
`cf-llama3.2-3b`（`鱼上水` 生硬）、`ms-mistral-large`（`鱼上钩` 增译了 `hook` 义）。

---

## ✅ 可用：reseller 端点（`llm.py` 的 `ox`/`oxd`/`xm`）

这些走 `models.json` 里的凭据，不是本地网关。单独探测时三者都能出文：

| 命名空间 | 模型 | 延迟 | 译文 |
|---|---|---|---|
| `xm:` | `xm:mimo-v2.6-flash` | **1.3s** | 老人坐在河边。 |
| `ox:` | `ox:gemini-3.8-flash` | 2.7s | 老人坐在河边。 |
| `oxd:` | `oxd:deepseek-v4.1-flash` | 4.6s | 老人坐在河边。 |

**用途**：作 fallback 与**评判模型**（judge 不能与 writer 同源，否则盲测失效）。
主写手仍是本地网关 `lc:` —— 更快且不耗信用。

---

## ❌ 已死

### `cssmapi.fun`（原主力 `cs:` 前缀）

- `/v1/models` **200，0.04s**，仍列出 `deepseek-v4.1-flash`
- `/chat/completions` **挂起 60s，零字节返回**
- 其他模型名 → 404 `not available for this group`（秒回）
- **症状**：网关与分组鉴权都活着（key 未吊销），**上游推理后端不响应** ——
  请求被挂起而非拒绝。限时免费 key 额度耗尽/后端撤走就是这个样子。
- **处置**：`llm.py` 中 `CSSM_KEY` 置空，旧 `cs:` 调用现在秒失败，
  不再占用 600s 读超时。

### `127.0.0.1:10000`（OpenCode2API 网关）

- key `sk-***`
- `/v1/models` 正常列出 9 个 `opencode/*-free` 模型
- **9/9 chat 全部超时**，无一可用
- 配置文件 `E:\tools\OpenCode2API-main\config.json`，上游 `OPENCODE_SERVER_URL=http://127.0.0.1:10001`

### `8317` 网关上 20/32 个模型

| 症状 | 模型 |
|---|---|
| **TimeoutError** | `nemotron-3.5-lightning`、`nemotron-3-ultra`、`big-pickle`、`glm-5.3-flash`、`deepseek-v4.1-flash`、`nemotron-3.5-vl`、`mimo-v2.6-flash`、`beam` |
| **HTTPError**（402/429/404） | `sf-kimi-k2.7-code`、`or-xing4.0-29b`、`or-gemma-4-31b`、`sf-deepseek-v3.2`、`sf-deepseek-v4-pro`、`sf-glm-5.2`、`sf-qwen3-coder`、`or-inkling`、`sf-qwen3-8b` |
| **返回非中文** | `or-nemotron-3.5-vl`、`ms-glm-5.2`、`or-nemotron-3.5-lightning` |

### bailian 全命名空间（`qw:`/`ds:`/`km:`/`gl:`/`in:`）

逐个模型名实测，**无一可用**：

| 结果 | 模型名 |
|---|---|
| `Access to model denied` | `qw:qwen3.8-max`、`qw:qwen-plus`、`qw:qwen3.5-27b`、`ds:deepseek-v4.1-flash`、`km:qwen-max` |
| `Model not exist` | `qw:qwen-turbo`、`qw:qwen-max-latest`、`qw:qwen3-max`、`gl:glm-4.5`、`gl:glm-4.6` |
| `model is not found` | `ia:Qwen2.5-7B-Instruct`、`in:Qwen2.5-7B-Instruct` |

### `mm:` MiniMax —— 余额不足

`insufficient_balance_error`。**不重试**（花钱的事不做）。

### 已彻底停用（按指示，不再测试）

- **付费按量 key** `sk-***…` —— 已从代码删除
- **按次计费 key** `sk-***…` —— 从未进入管线

---

## 管线改动

### 第一批：writer 池（8 文件 12 处）

`scratch/switch_writer.py` 把 `cs:deepseek-v4.1-flash`
→ `lc:ms-deepseek-v4.1-flash`：

```
pipeline_gutenberg/run_all.py      pipeline_pub/run_pub.py
pipeline_overhaul/notes.py         pipeline_whale/eval_whale.py
pipeline_polish/polish_engine.py   pipeline_whale/run.py
pipeline_proust/run_independent.py pipeline_whale/workflow.py
```

### 第二批：`pipeline_polish/engine.py`（付费 key 移除）

这是**最严重的一处** —— 它绕过 `llm.py`，自己 `requests.post` 直连 cssmapi，
并硬编码了一个 **`sk-efab…` 付费按量 key**，且被 5 个模块 import
（`books`/`judge_terms`/`launch`/`run_polish`）。

| 项 | 改前 | 改后 |
|---|---|---|
| `BASE` | `https://cssmapi.fun/v1`（已死） | `http://127.0.0.1:8317/v1` |
| `KEY` | `sk-***…`（付费） | `<local-key>` |
| `MODEL` | `deepseek-v4.1-flash` | `ms-deepseek-v4.1-flash` |
| `GLOBAL_CAP` | **150** | **6** |

`GLOBAL_CAP` 必须一起降。150 是为 cssmapi 的 TLS 握手上限调的；本地网关在 6 并发
以上不拒绝而是**排队**，留 150 只会让每个请求排在队尾，把慢变挂。

### 第三批：bailian / 笔误死配置（12 文件）

`scratch/fix_dead_models.py` + `fix_dead_models2.py`：

| 文件 | 原 | 因 |
|---|---|---|
| `pipeline_proust/revise.py` | `css:deepseek-v4.1-flash` | **命名空间 `css` 从未存在**（`cs` 笔误），首调即崩 |
| `pipeline_proust/eval_ab.py` | `default="css:…"` | 同上 |
| `pipeline_new/run_new.py` | WRITER/AUDITOR/POLISHER/ANALYST 全 bailian | bailian 全拒 |
| `pipeline_overhaul/terms.py` | `ds:…` | bailian |
| `pipeline_overhaul/verify.py` | `ds:…` | bailian |
| `pipeline_overhaul/revise.py` | `qw:…, ds:…` | bailian |
| `pipeline_proust/revise3.py` | `qw:…` | bailian |
| `pipeline_new/eval_new.py` | judges `qw,km,ds` | bailian |
| `pipeline_whale/eval_whale.py` | judges `qw,km,gl,in,ds` | bailian |

judge 池改用 `ox:`/`oxd:`/`xm:` —— **judge 不能与 writer 同源**，否则盲测失效。

**验收**：`grep -rn '"\(css\|ds\|qw\|km\|gl\|mm\|ia\|in\):' pipeline_*/` → **空**；
12 个文件 `py_compile` 全过。

### 端到端验证

```
elapsed 7.2s  cached=False
5 paragraphs from 5 blocks, 325 hanzi (ratio 0.28)
first line: '决心'
```

真实块 `work_pub/betrachtung/chunks/c005.json` chunk 0（德文 5 块 1149 字符）。

### `llm.py` 其他改动

- 新增 `LOCAL_BASE` / `LOCAL_KEY` / `LOCAL_OVERRIDE`，provider 名 `local-gateway`
- `NS_PROVIDER` 加 `"lc": "local-gateway"`；`LIMITS` 加 `"lc": 6`
- `CSSM_KEY` 默认 `""`，旧 `cs:` 调用快速失败
- 备份：`pipeline_whale/llm.py.bak_20261026`、`engine.py.bak_20261026`、各管线 `.bak_writer`

---

## 经验

**`/v1/models` 返回 200 不能作为可用判据。** cssmapi 和 10000 网关都能秒回模型列表，
但 chat 全部挂死。必须做一次真实 round-trip 并检查返回是否是中文。

**挂起和拒绝是两种故障，处置不同。** 挂起（零字节、无 HTTP 状态）会耗尽客户端的
整个读超时，批量任务里一个挂死的端点能拖垮整条并发队列；拒绝（4xx）会立刻释放。
所以死端点要么置空 key 让它秒失败，要么从 WRITER 里删掉。

**本地网关并发上限 6。** `probe` 阶段 6 并发下 12/12 成功；此前 32 并发实测
「2/24 成功、800s」，放大并发只会把它打回挂起。

**硬编码付费 key 是最危险的残留。** `engine.py` 绕过 `llm.py` 自建请求，
里面藏着一个 `sk-efab…` 付费 key，且被 5 个模块 import。**grep 命名空间只是第一步，
还要查 BASE/KEY 字面量** —— 付费端点即使还活着，也不能用。

**`mm:` 报余额不足时不要重试。** 那不是故障，是没钱；重试只会扣费。

**冒烟测试必须用 ≥700 字符的真实块。** `workflow.translate_chunk` 的
`min_ok = max(60, len(source) * 0.18)` 有 60 字符地板，两句英文永远过不了。
**另一个坑**：`llm.chat()` 默认返回 `(text, model)` 元组，不是纯字符串。
