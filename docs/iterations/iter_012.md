# Iteration 012 - Day 12: 指标报告生成初步

## 目标

- 将 Day 10/11 计算的指标结果进行可视化和表格化输出。
- 生成 CSV 文件保存指标，同时生成可直接查看的图表。
- 为后续自动化报告和批量评测打基础。

## 任务类型

- 技能练习：Python 数据处理与可视化
- 核心工具：Pandas、Matplotlib

## 输入输出

| 类型 | 内容                                                              |
| ---- | ----------------------------------------------------------------- |
| 输入 | Day 11 `TextMetrics` 类计算出的指标结果                           |
| 输出 | 1. CSV 文件：指标表格<br>2. 图表文件（PNG）：各指标柱状图或折线图 |

## 任务细节

### 1. 数据准备

- 使用 `TextMetrics.compute_all()` 得到一个 dict：
  ```python
  metrics = TextMetrics(...).compute_all()
  # 示例输出
  # {'rouge_1': 0.8333, 'rouge_2': 0.6, 'rouge_l': 0.8333, 'bleu_1': 0.8333, 'bleu_2': 0.7071, 'accuracy': 0.75, 'win_rate_half_tie': 0.65, 'win_rate_no_tie_credit': 0.6}
  ```

* 可扩展为多条样本记录，形成列表或 DataFrame。

### 2. 表格输出 (CSV)

- 使用 `pandas.DataFrame` 将指标结果转换为表格。
- 将表格保存为 CSV 文件：

  ```python
  import pandas as pd

  df = pd.DataFrame([metrics])  # 单样本，若多样本用列表
  df.to_csv("day12_metrics_report.csv", index=False)
  ```

- CSV 文件列名与指标键名对应。

### 3. 图表生成

- 使用 `matplotlib.pyplot` 绘制柱状图或折线图。
- 示例柱状图：

  ```python
  import matplotlib.pyplot as plt

  plt.figure(figsize=(10, 6))
  plt.bar(df.columns, df.iloc[0])
  plt.ylabel("Score")
  plt.title("Day 12 Metrics Report")
  plt.ylim(0, 1)
  plt.savefig("day12_metrics_report.png")
  plt.close()
  ```

- 可为多样本绘制折线图，x 轴为样本编号，y 轴为指标值。
- 图表保存为 PNG 文件，可嵌入 Markdown/HTML 报告。

### 4. 验证

- 确认 CSV 文件能被 Excel / Pandas 正确读取。
- 确认图表生成无错误，数据正确映射。
- 样本数量不同、部分指标为 0 时，图表显示合理。

### 5. 扩展（可选）

- 添加柱状图颜色区分（ROUGE、BLEU、Accuracy、Win Rate）。
- 绘制多指标折线图，用不同颜色标识指标。
- 自动生成 Markdown 或 HTML 报告模板，将 CSV 和图表嵌入。

## 验收标准

- [ ] 指标结果正确计算，数值与 `TextMetrics.compute_all()` 一致。
- [ ] CSV 文件保存成功，列名与指标键名对应。
- [ ] 图表生成清晰、文件保存成功，指标值正确映射。
- [ ] 可扩展到多样本报告，无报错。

## 参考资料

- [Pandas 官方文档](https://pandas.pydata.org/pandas-docs/stable/)
- [Matplotlib 官方教程](https://matplotlib.org/stable/tutorials/index.html)
- Day 11 `TextMetrics` 类文档

## 迭代任务总结

- 本迭代完成指标的初步报告生成。
- 形成 CSV 与图表，为后续 Day 13/14 自动化报告和批量分析做准备。
