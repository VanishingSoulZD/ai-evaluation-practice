# Iteration 013 - Day 13: 自动化脚本练习（批量处理数据）

## 目标

- 熟悉 Python 脚本批量处理能力
- 能够批量计算指标并生成报告
- 实现 Day 11/12 指标计算和报告流程的自动化

## 背景

在前两天的练习中，我们完成了：

1. Day 11：模块化封装 `TextMetrics`，可以计算 ROUGE/BLEU/Accuracy/Win Rate 等指标
2. Day 12：将指标生成 CSV 表格和 PNG 图表报告

在 Day 13 中，我们需要把这些功能扩展为自动化批量处理脚本，以便处理多批样本数据，提高工作效率和复用性。

---

## 任务拆解

### 任务 1：准备多批数据

- **背景**：批量处理需要先有多批输入数据。
- **任务要求**：
  1. 构造多批文本数据，每批包含多个样本，样本字段包括：
     - reference 文本
     - candidate 文本
     - y_true 与 y_pred（分类任务）
     - wins, losses, ties（胜率计算）
  2. 支持从 JSON 或 CSV 文件加载多批样本数据（可选）
- **实现步骤**：
  - 创建示例数据列表或读取文件
  - 检查每个样本字段完整性
- **验收标准**：
  - 数据可迭代，样本字段完整
  - 支持至少 3 批，每批 2-3 个样本

---

### 任务 2：批量运行指标计算

- **背景**：使用 Day 11 `TextMetrics` 对每批数据进行指标计算
- **任务要求**：
  1. 对每批样本循环调用 `TextMetrics.compute_all()`
  2. 将结果保存为列表或字典形式，便于后续生成报告
- **实现步骤**：
  - 定义 `process_batch(batch: list[dict]) -> list[dict]` 函数
  - 在函数中对每个样本实例化 `TextMetrics` 并调用 `compute_all()`
- **验收标准**：
  - 输出每批指标列表
  - 输出与输入样本数量一致

---

### 任务 3：生成报告（CSV + PNG）

- **背景**：使用 Day 12 的报告生成逻辑，输出批量指标报告
- **任务要求**：
  1. 对每批结果生成 CSV 文件，例如 `batch_{i}_metrics.csv`
  2. 对每批结果生成 PNG 图表，例如 `batch_{i}_metrics.png`
  3. 统一列顺序与 Day 12 保持一致
- **实现步骤**：
  - 调用 `day12_metrics_report.build_metrics_report(metrics_batch, output_csv, output_png)`
  - 支持批量循环生成
- **验收标准**：
  - 每批都生成对应 CSV 和 PNG
  - CSV 与 PNG 内容正确、列顺序稳定

---

### 任务 4：整合自动化脚本

- **背景**：将多批处理流程整合为可直接运行的 Python 脚本
- **任务要求**：
  1. 支持命令行参数指定输入数据目录和输出报告目录
  2. 自动处理所有批数据，并生成对应报告
- **实现步骤**：
  - 使用 `argparse` 或 `click` 获取输入输出路径
  - 遍历每批数据文件
  - 对每批调用指标计算和报告生成函数
  - 打印处理进度和结果路径
- **验收标准**：
  - 脚本可直接运行完成多批处理
  - 输出目录包含所有 CSV 和 PNG 文件
  - 无未处理异常

---

## 输出与验收

- CSV 文件：每批数据生成 `batch_{i}_metrics.csv`，列顺序与 Day 12 一致
- PNG 文件：每批数据生成 `batch_{i}_metrics.png`，图表清晰可读
- Python 脚本：`day13_batch_process.py`，可直接运行处理多批数据

---

## 参考资料

- Day 11 文档：`docs/iterations/iter_011.md`
- Day 12 文档：`docs/iterations/iter_012.md`
- Pandas 文档：[https://pandas.pydata.org/](https://pandas.pydata.org/)
- Matplotlib 文档：[https://matplotlib.org/stable/contents.html](https://matplotlib.org/stable/contents.html)
- argparse 文档：[https://docs.python.org/3/library/argparse.html](https://docs.python.org/3/library/argparse.html)

---

## 附加说明

- 保证函数和脚本接口清晰，可复用
- 支持空样本和异常数据处理
- 生成报告文件名可根据批次自动命名
- 可以作为 Day 11/12 模块的批量调用示例
