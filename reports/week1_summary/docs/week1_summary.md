# Week 1 回顾与总结（Day 1–Day 6）

## 1. 本周目标与完成情况

| Day | 学习目标 | 完成情况 |
|---|---|---|
| Day1 | 熟悉标注任务场景、标注规范与样本结构 | 已完成，形成任务背景与标注规范理解 |
| Day2 | 产出结构化标注数据（CSV / Excel） | 已完成，产出 `day2_annotation_practice.csv/.xlsx` |
| Day3 | 实现一致性与异常分析（缺失、重复、BIO、NER 一致性） | 已完成，产出多张分析表 |
| Day4 | 可视化标注结果分布 | 脚本完成；当前环境依赖缺失，图表未在本次归档中重跑 |
| Day5 | 打通“标注→分析→可视化”流水线 | 脚本完成；当前环境依赖缺失，图表未在本次归档中重跑 |
| Day6 | Python / Pandas / NumPy 综合练习 | 脚本完成；当前环境依赖缺失，结果未在本次归档中重跑 |

---

## 2. 核心知识点与心得

### Python 基础
- 函数封装与参数化（输入路径、输出目录、列名可配置）
- 通过 `argparse` 实现可复用命令行脚本
- 通过 `Path` 统一文件路径管理，增强跨平台能力

### Pandas 数据分析
- 表格读取：CSV / Excel 双格式支持
- 常见分析：缺失值统计、重复样本识别、分组聚合、分布统计
- 宽表与长表变换（explode、groupby、merge）

### NumPy 向量化思维
- 数组切片、广播运算、掩码过滤
- 汇总统计（sum/mean/min/max）与标准化

### 标注质量分析
- 情感标签分布（POS/NEG/NEU）
- 实体标签统计（PER/ORG/LOC/TIME）
- BIO 序列合法性校验
- 同文本多版本标注一致性检查（NER inconsistency）

---

## 3. 脚本说明（按功能分类）

### A. 标注处理
- `scripts/generate_day2_annotation_files.py`
  - 输入：内置样例/配置
  - 输出：Day2 标注练习数据（CSV / Excel）

### B. 数据分析
- `scripts/day3_consistency_analysis.py`
  - 输入：标注数据 CSV / Excel
  - 输出：summary、missing、duplicate、sentiment、BIO、异常样本等 CSV；可选 Excel

### C. 可视化
- `scripts/day4_visualization.py`
  - 输入：标注数据 CSV / Excel
  - 输出：情感柱状图、实体柱状图、BIO 热力图，以及统计 CSV/Excel

- `scripts/day5_annotation_analysis_pipeline.py`
  - 输入：标注数据 CSV / Excel
  - 输出：自动补标日志、统计表、分布图，形成端到端流程

### D. Python 综合练习
- `scripts/day6_python_pandas_numpy_practice.py`
  - 输入：历史标注表（CSV / Excel）
  - 输出：清洗数据、任务统计、标签分布、NumPy 摘要 JSON

---

## 4. 图表展示与解读

> 本次环境因依赖下载受限，未重跑 Day4/Day5 图表。已有图表脚本可直接复用，推荐在本地或可联网环境执行：

```bash
uv run python scripts/day4_visualization.py day2_annotation_practice.csv --output-dir reports/week1_summary/charts/day4 --excel
uv run python scripts/day5_annotation_analysis_pipeline.py day2_annotation_practice.csv --output-dir reports/week1_summary/charts/day5 --excel
```

图表解读建议：
- 若 NEG 比例偏高，优先回看负向样本是否存在标签误配。
- 若实体分布极不均衡，补充长尾实体样本提升泛化。
- 若 BIO 热力图中 `I-*` 明显异常，需重点复核序列连续性。

---

## 5. 可复用代码示例

```python
# 统一输出目录模式
from pathlib import Path

out = Path("reports/week1_summary/analysis_tables/day3")
out.mkdir(parents=True, exist_ok=True)
```

```python
# 情感标签计数模式
labels = df["标注结果"].fillna("").astype(str).str.upper()
counts = {lb: labels.str.contains(rf"\\b{lb}\\b").sum() for lb in ["POS", "NEG", "NEU"]}
```

---

## 6. Week1 闭环与下周建议

### 本周闭环结果
- 已完成 Day1–Day6 的脚本、数据与分析结果归档。
- 目录结构按“数据/分析表/图表/脚本/文档”拆分，便于检索。
- Week1 总结文档可直接复用为后续周报模板。

### 下周建议（Week2）
1. 增加标注一致性评估指标（如 Cohen’s Kappa）。
2. 为 Day4/5 图表增加英文标题与自动保存元数据。
3. 将 Day3–6 脚本串成单入口 `run_week_pipeline.py`。
4. 增加最小测试集（pytest）验证输出字段完整性。
