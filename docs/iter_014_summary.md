# Day 14: Week 2 总结（精简版）

## 任务目标
- 巩固 Week 2 成果
- 汇总前 7 天的脚本和输出
- 形成可复用的文档说明和参考脚本

## 总结内容

### 1. Day 11 - 文本指标计算
- **脚本**: `scripts/day11_text_metrics.py`
- **功能**: 计算文本生成的多种指标，包括 ROUGE、BLEU、Accuracy、Win Rate 等。
- **使用说明**:
  ```python
  from scripts.day11_text_metrics import TextMetrics

  metrics = TextMetrics(
      reference="参考文本",
      candidate="生成文本",
      y_true=[...],
      y_pred=[...],
      wins=...,
      losses=...,
      ties=...
  ).compute_all()
  print(metrics)
  ```

### 2. Day 12 - 单样本指标报告生成
- **脚本**: `scripts/day12_metrics_report.py`
- **功能**:
  - 将 Day 11 输出的指标生成 CSV 报告
  - 绘制清晰图表（单样本或多样本）
- **使用说明**:
  ```python
  from scripts.day12_metrics_report import build_metrics_report

  df, csv_path, png_path = build_metrics_report(metrics_list)
  print(f"CSV: {csv_path}, PNG: {png_path}")
  ```

### 3. Day 13 - 批量处理
- **脚本**: `scripts/day13_batch_process.py`
- **功能**:
  - 支持批量数据（JSON/CSV）
  - 对每个 batch 自动计算指标并生成报告
  - 记录异常样本日志
- **使用说明**:
  ```bash
  python scripts/day13_batch_process.py --input-dir path/to/batches --output-dir reports/day13_batch
  ```

### 4. Day 14 - 本周总结
- 整理了 Day 11-13 的核心脚本
- 编写可复用文档说明
- 核心产出：
  - 文档：`docs/iter_014_summary.md`
  - 可直接引用脚本：
    - `scripts/day11_text_metrics.py`
    - `scripts/day12_metrics_report.py`
    - `scripts/day13_batch_process.py`

---

> 注意：精简版本不包含示例数据或预生成报告文件，仅保留总结文档与核心脚本引用，便于 Week 2 复盘与 Week 3 扩展。
