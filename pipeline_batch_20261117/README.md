# 2026-11-17 翻译与审校交付

本目录保存3批、11篇完整短篇的原文和中文，以及修复4本历史成品的定点脚本。选译集不代表原书全译。原文来源、译介检索限制和校读方法见 `SELECTION_AND_QA.md`、`SECOND_BATCH_QA.md`、`EGERTON_QA.md`。

## 从检出的仓库重建

在仓库根目录使用 Python 3.13：

```powershell
python pipeline_batch_20261117/build.py
python pipeline_batch_20261117/build.py --second
python pipeline_batch_20261117/build.py --egerton
python pipeline_batch_20261117/verify_delivery.py
python pipeline_build/verify_epub.py
```

以上命令无需网络、API或历史工作目录。三份 `*translations.json` 是构建真源，生成文件写入被忽略的 `work_batch_*/` 与 `out/`。

要从已存档HTML和中文编辑源重新生成对齐JSON：

```powershell
python pipeline_batch_20261117/prepare_second.py
python pipeline_batch_20261117/extract_egerton.py
python pipeline_batch_20261117/prepare_egerton.py
```

`fetch_second.py` 是可选的在线重新采集工具，需要 `requests`。其他交付构建不需要它发起网络请求。

## 历史修复

`repairs/` 的三份脚本记录4处词义/数量修复和11处引号修复。它们需要本机历史 `work_pub/`、`work_gutenberg/`，因此不承诺在只有Git文件的检出中重建历史作品；仓库已包含修复后的4本EPUB。执行前会断言精确匹配，并在 `scratch/` 保留备份。审计细节见仓库根目录两份2026-11-17报告。

`verify_delivery.py --with-local-backups` 还会对《黑暗的心》修复前备份逐XHTML比较，确认只有帆布术语发生改变。默认检查只验证可随Git获得的交付，不依赖本地备份。

## 保留与排除

保留原译对照、来源HTML、原刊8页PDF、审校记录、确定性脚本及精简验证结果。不纳入缓存、API凭据、临时探测响应、历史工作树或修前备份。中断时尚未采集成功的法语候选不属于本次交付。
