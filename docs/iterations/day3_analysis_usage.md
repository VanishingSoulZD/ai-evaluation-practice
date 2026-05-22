# Day 3 一致性分析脚本使用说明

脚本路径：`scripts/day3_consistency_analysis.py`

## 运行方式

```bash
python scripts/day3_consistency_analysis.py <输入文件路径> --output-dir reports
```

- 输入支持：`.csv`、`.xlsx/.xls`（Excel 读取需要安装 `openpyxl`）。
- 默认识别列：`ID`、`任务类型`、`原始文本`、`标注结果`。
- 可通过参数覆盖列名：`--id-col --task-col --text-col --label-col`。

## 输出内容

脚本会在输出目录生成 `<文件名>_analysis_csv/`，包含：

- `summary.csv`：总样本数、缺失单元格数、重复样本数、NER/BIO 异常数
- `missing_stats.csv`：按列缺失统计（数量、比例）
- `duplicate_stats.csv`：重复 ID / 重复文本统计（数量、比例）
- `sentiment_distribution.csv`：`POS/NEG/NEU` 标签分布
- `ner_inconsistency.csv`：同文本不同实体标注异常样本
- `bio_issues.csv`：BIO 序列不合法样本及原因
- `anomaly_list.csv`：重复/缺失异常清单（含异常原因）

若环境已安装 `openpyxl`，同时会生成 Excel 汇总：`<文件名>_analysis_report.xlsx`。
