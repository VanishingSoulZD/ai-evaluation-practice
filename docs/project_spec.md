# 项目规格说明（project_spec）

## 1. 项目概览

### 1.1 目标与背景
`ai-evaluation-practice` 是一个以 **28 天渐进式工程实践** 为主线的项目，目标是系统展示 AI 评测工程中的关键能力：
- 数据标注与质量分析；
- 指标设计与实现（ROUGE/BLEU/Accuracy/Win Rate）；
- 批处理与报告自动化；
- API 服务化与异步任务化；
- LLM-as-a-Judge、对抗测试与端到端仿真评测。

整体练习计划定义在 `docs/practice_plan.md`，并通过每日迭代文档和周总结文档持续沉淀实现过程与结果。

### 1.2 核心功能概览
- **标注与数据分析链路（Week1）**：从手工标注到一致性检查、可视化与流程集成。
- **文本评测指标链路（Week2）**：从公式理解到 Python 实现、验证、封装、批量化。
- **接口与异步执行链路（Week3）**：基于 FastAPI + Celery + Redis 的上传、批量评测、异步任务与报告。
- **前沿方法与综合演练（Week4）**：LLM 自动评分、对抗输入评估、仿真评测与端到端流程复盘。

---

## 2. 项目结构

## 2.1 根目录说明

| 路径 | 说明 |
|---|---|
| `docs/` | 计划文档、迭代记录、周总结、协作规范 |
| `scripts/` | Day 级别脚本与通用工具函数 |
| `data/` | 标注原始样例与练习数据 |
| `outputs/` | 每日脚本输出与实验产物 |
| `reports/` | 报告文件（CSV/Excel/图表等） |
| `main.py` | FastAPI 服务入口 |
| `tasks.py` | Celery 异步任务定义 |
| `celery_app.py` | Celery 实例与 broker/backend 配置 |
| `pyproject.toml` | Python 依赖与版本要求 |

### 2.2 目录细分
- `docs/practice_plan.md`：28 天任务规划。
- `docs/iterations/iter_XXX.md`：按迭代编号记录设计、实现与结果。
- `docs/weekly_summaries/weekly_XX_summary.md`：每周阶段性总结。
- `docs/CLAUDE.md`：协作与实现规范（含注释、依赖、工程流程要求）。
- `scripts/dayX_*.py`：按天拆分的能力训练脚本。
- `scripts/utils.py`：可视化与标签提取通用函数。
- `outputs/day25|day26|day27`：第 25~27 天示例输出目录。

### 2.3 文件命名与功能概述
- 迭代文档命名：`iter_001.md` ~ `iter_028.md`。
- 周总结命名：`weekly_01_summary.md` ~ `weekly_04_summary.md`。
- 日脚本命名：`day{N}_*.py`（如 `day23_llm_judge_experiment.py`）。
- 报告输出：`report_<uuid>.csv`、`chart_<uuid>.png` 等。

---

## 3. 功能模块与技术流程

### 3.1 模块划分
1. **数据处理与标注分析模块**
   - 典型脚本：`day3_consistency_analysis.py`、`day4_visualization.py`、`day5_annotation_analysis_pipeline.py`、`utils.py`。
   - 输入：CSV/XLSX/Markdown 标注数据。
   - 输出：一致性统计、分布图、分析结果文件。

2. **评测指标实现模块**
   - 典型脚本：`day9_text_metrics.py`、`day10_metric_validation.py`、`day11_text_metrics.py`。
   - 输入：参考文本、候选文本、分类标签、胜负统计。
   - 输出：ROUGE/BLEU/Accuracy/Win Rate 指标值与校验结果。

3. **报告与批处理模块**
   - 典型脚本：`day12_metrics_report.py`、`day13_batch_process.py`。
   - 输入：指标记录（单条/批量 JSON、DataFrame）。
   - 输出：CSV 报告、图表 PNG、批处理日志。

4. **服务化与异步执行模块**
   - 典型组件：`main.py`、`tasks.py`、`celery_app.py`。
   - 输入：上传 CSV、API 调用参数。
   - 输出：实时 JSON 响应、异步任务状态、自动报告文件。

5. **LLM 与仿真评测模块**
   - 典型脚本：`day23_llm_judge_experiment.py`、`day24_adversarial_test.py`、`day25_simulation_eval.py`、`day26_end_to_end_pipeline.py`。
   - 输入：问题-答案样本、对抗输入、仿真对话配置。
   - 输出：评分结果、异常样本分析、端到端评测报告。

### 3.2 依赖关系与流程

```text
data/ 标注数据
   │
   ├─> Week1 脚本（一致性/可视化）
   │        └─> outputs/ + reports/
   │
   ├─> Week2 指标脚本（day9~day13）
   │        └─> 指标结果 + 报告文件
   │
   ├─> Week3 API 上传（main.py）
   │        └─> Celery 异步任务（tasks.py）
   │               └─> reports/report_*.csv + chart_*.png
   │
   └─> Week4 LLM/Judge/对抗/仿真脚本
            └─> outputs/day25~day27 与迭代文档
```

---

## 4. 28 天练习计划映射

> 说明：项目中存在完整的 `iter_001~iter_028` 与 `weekly_01~04` 文档体系。下表按练习计划目标给出“计划目标 → 当前实现载体”映射。

| Day | 计划目标（practice_plan） | 主要实现/脚本 | 迭代文档 | 周总结 | 主要输出 |
|---|---|---|---|---|---|
| 1 | 标注规范与样例 | 数据标注文档与样例数据 | `iter_001.md` | `weekly_01_summary.md` | `data/data_day01_annotation.md` |
| 2 | 50 条标注实践 | 标注文件生成与分析准备 | `iter_002.md` | `weekly_01_summary.md` | `data_day02_annotation.*`, `reports/day2_*` |
| 3 | 一致性检查 | `day3_consistency_analysis.py` | `iter_003.md` | `weekly_01_summary.md` | 一致性分析结果 |
| 4 | 数据分布可视化 | `day4_visualization.py`, `utils.py` | `iter_004.md` | `weekly_01_summary.md` | 分布图（hist/bar/heatmap） |
| 5 | 标注+分析综合 | `day5_annotation_analysis_pipeline.py` | `iter_005.md` | `weekly_01_summary.md` | 流程化输出文件 |
| 6 | Pandas/NumPy 练习 | `day6_python_pandas_numpy_practice.py` | `iter_006.md` | `weekly_01_summary.md` | 数据处理练习结果 |
| 7 | Week1 总结 | 文档整理 | `iter_007.md` | `weekly_01_summary.md` | 周总结文档 |
| 8 | 指标理解 | 理论记录 `day8_record.md` | `iter_008.md` | `weekly_02_summary.md` | 指标学习记录 |
| 9 | 指标函数实现 | `day9_text_metrics.py` | `iter_009.md` | `weekly_02_summary.md` | 指标计算结果 |
| 10 | 指标验证优化 | `day10_metric_validation.py` | `iter_010.md` | `weekly_02_summary.md` | 校验日志/报告 |
| 11 | 模块化封装 | `day11_text_metrics.py` | `iter_011.md` | `weekly_02_summary.md` | 可复用类接口 |
| 12 | 报告生成 | `day12_metrics_report.py` | `iter_012.md` | `weekly_02_summary.md` | CSV + PNG |
| 13 | 批量自动化 | `day13_batch_process.py` | `iter_013.md` | `weekly_02_summary.md` | 批处理报告 |
| 14 | Week2 总结 | 文档与脚本整理 | `iter_014.md` | `weekly_02_summary.md` | 周总结文档 |
| 15 | FastAPI 入门 | `main.py` 基础接口 | `iter_015.md` | `weekly_03_summary.md` | API 返回 JSON |
| 16 | 文件上传接口 | `/upload-file` | `iter_016.md` | `weekly_03_summary.md` | 上传确认信息 |
| 17 | 批量指标 API | `/batch-metrics` | `iter_017.md` | `weekly_03_summary.md` | 批量 metrics JSON |
| 18 | 异步任务入门 | `/batch-metrics-async`, Celery | `iter_018.md` | `weekly_03_summary.md` | task_id 与状态查询 |
| 19 | 异步任务+报告 | `compute_metrics_and_report` | `iter_019.md` | `weekly_03_summary.md` | `report_*.csv`, `chart_*.png` |
| 20 | 接口+异步整合 | `main.py`+`tasks.py` 集成 | `iter_020.md` | `weekly_03_summary.md` | 端到端异步流程输出 |
| 21 | Week3 总结 | 文档沉淀 | `iter_021.md` | `weekly_03_summary.md` | 周总结文档 |
| 22 | LLM-as-a-Judge 理解 | 方法学习与文档 | `iter_022.md` | `weekly_04_summary.md` | 说明文档（含 `outputs/iter_022_v2.md`） |
| 23 | GPT 自动评分实验 | `day23_llm_judge_experiment.py` | `iter_023.md` | `weekly_04_summary.md` | 评分结果与统计 |
| 24 | 对抗测试 | `day24_adversarial_test.py` | `iter_024.md` | `weekly_04_summary.md` | 对抗输入结果文件 |
| 25 | 仿真环境评估 | `day25_simulation_eval.py` | `iter_025.md` | `weekly_04_summary.md` | `outputs/day25` |
| 26 | 综合流程练习 | `day26_end_to_end_pipeline.py` | `iter_026.md` | `weekly_04_summary.md` | `outputs/day26` |
| 27 | 输出分析结论 | 汇报文档与结果整理 | `iter_027.md` | `weekly_04_summary.md` | `outputs/day27` |
| 28 | 全量复盘整理 | 代码/文档归档 | `iter_028.md` | `weekly_04_summary.md` | 最终总结沉淀 |

---

## 5. 数据与输出规范

### 5.1 `data/` 文件说明
- `data_day01_annotation.md`：Day1 标注规则与样例。
- `data_day02_annotation.csv/.xlsx/.md`：Day2 标注实践数据，多格式便于脚本与人工复核。

### 5.2 `outputs/` 文件说明
- 存放日常迭代产出，通常包含：
  - LLM 评测结果；
  - 仿真评测记录；
  - 每日复盘文档。
- 示例：`outputs/day25`, `outputs/day26`, `outputs/day27`, `outputs/iter_022_v2.md`。

### 5.3 `reports/` 文件说明
- 存放结构化分析报告与可视化图表。
- 典型格式：CSV、Excel、PNG。
- 示例：`day2_annotation_practice_analysis_report.xlsx`、`iter_010_validation.md`。

### 5.4 关键数据格式字段
- 文本评测样本常见字段：`reference`, `candidate`。
- 分类评测字段：`y_true`, `y_pred`。
- 对战统计字段：`wins`, `losses`, `ties`。
- LLM 评分字段：`accuracy`, `completeness`, `logic`, `readability`, `overall_score`, `rationale`。

---

## 6. 使用指南

### 6.1 推荐运行顺序
1. Week1：day3 → day4 → day5 → day6
2. Week2：day9 → day10 → day11 → day12 → day13
3. Week3：启动 FastAPI + Celery，再执行上传与异步接口联调
4. Week4：day23 → day24 → day25 → day26

### 6.2 主要依赖
- Python：`>=3.11`
- 依赖定义：`pyproject.toml`
- 关键库：`pandas`, `fastapi`, `uvicorn`, `celery`, `redis`, `matplotlib`, `seaborn`, `openai`

### 6.3 示例命令
```bash
# 安装依赖
uv sync

# Week2 指标验证
python scripts/day10_metric_validation.py

# 生成指标报告
python scripts/day12_metrics_report.py

# 批处理
python scripts/day13_batch_process.py

# 启动 API
uvicorn main:app --reload

# 启动 Celery Worker（需 Redis）
celery -A tasks worker --loglevel=info

# Day23：离线 mock
python scripts/day23_llm_judge_experiment.py --mock
```

### 6.4 注意事项
- 异步任务依赖 Redis，请先确保 broker/backend 可连通。
- LLM 实验如需真实调用 OpenAI，需设置 `OPENAI_API_KEY`。
- 建议按周顺序执行脚本，确保输入输出依赖完整。

---

## 7. 附录

### 7.1 CLAUDE.md 规范说明
- 代码/文档协作优先“简单、精准、目标驱动”。
- Python 依赖管理建议使用 `uv`。
- 关键流程需要明确输入输出与注释说明。

### 7.2 参考文档
- `docs/practice_plan.md`
- `docs/iterations/iter_001.md` ~ `iter_028.md`
- `docs/weekly_summaries/weekly_01_summary.md` ~ `weekly_04_summary.md`
- `docs/CLAUDE.md`
