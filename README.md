# ai-evaluation-practice

一个围绕 **AI 评测工程能力建设** 的 28 天实践项目，覆盖数据标注、评测指标、自动化流水线、接口服务化、异步任务和 LLM 评测实验。

## 项目概览

### 目标
- 构建从数据到评测报告的完整工程链路。
- 形成可复用的脚本、接口、异步任务与文档资产。
- 支撑 AI 系统评测中的质量分析、指标验证与稳定性验证。

### 核心功能亮点
- **Week1**：标注数据一致性检查 + 可视化分析。
- **Week2**：ROUGE/BLEU/Accuracy/Win Rate 指标实现、验证、模块化与批处理。
- **Week3**：FastAPI 文件上传与批量评测接口，Celery 异步任务与自动报告生成。
- **Week4**：LLM-as-a-Judge 自动评分、对抗输入测试、仿真评测与端到端流程演练。

### 技术栈
- Python 3.11+
- Pandas / Matplotlib / Seaborn
- FastAPI / Uvicorn
- Celery / Redis
- OpenAI Python SDK

---

## 快速上手

### 1) 环境准备
```bash
# 建议使用 uv
uv sync
```

### 2) 启动 API 服务
```bash
uvicorn main:app --reload
```

### 3) 启动异步 Worker（需本地 Redis）
```bash
celery -A tasks worker --loglevel=info
```

### 4) 运行示例脚本
```bash
# 指标验证
python scripts/day10_metric_validation.py

# 指标报告生成
python scripts/day12_metrics_report.py

# LLM 自动评分（离线 mock）
python scripts/day23_llm_judge_experiment.py --mock
```

### 5) 示例输入/输出
- 输入：CSV 标注或评测数据（通过 API 上传或脚本加载）。
- 输出：
  - JSON 指标结果（API 返回）；
  - `outputs/` 下的日常实验产物；
  - `reports/` 下的 CSV/Excel/图表报告。

---

## 目录结构

```text
根目录/
├── docs/                 # 计划、迭代、周总结、协作规范
├── scripts/              # dayX 实践脚本与工具函数
├── data/                 # 标注数据与样例
├── outputs/              # 每日迭代输出
├── reports/              # 评测报告与图表
├── main.py               # FastAPI 入口
├── tasks.py              # Celery 异步任务
├── celery_app.py         # Celery 配置
└── pyproject.toml        # 依赖与 Python 版本
```

---

## 核心模块说明

### scripts/ 模块（按 dayX）
- `day3~day6`：标注数据一致性、可视化、流水线整合、Pandas/NumPy 练习。
- `day9~day13`：文本评测指标实现、校验、封装、报告生成与批处理。
- `day23~day26`：LLM 自动评分、对抗测试、仿真评测、端到端集成。
- `utils.py`：实体/BIO 标签提取与可视化通用函数。

### docs/ 模块
- `practice_plan.md`：28 天练习计划总表。
- `iterations/iter_XXX.md`：每日迭代记录（001~028）。
- `weekly_summaries/weekly_XX_summary.md`：每周总结（01~04）。
- `CLAUDE.md`：协作与工程规范。

### outputs/ & reports/
- `outputs/`：日常实验产出、阶段文档、仿真结果。
- `reports/`：结构化报告（CSV/Excel）与图表（PNG）。

---

## 文件与产出说明

### 每天迭代输出
- 迭代文档位置：`docs/iterations/iter_001.md` ~ `iter_028.md`
- 周总结位置：`docs/weekly_summaries/weekly_01_summary.md` ~ `weekly_04_summary.md`

### 关键数据格式
- 文本指标：`reference`, `candidate`
- 分类指标：`y_true`, `y_pred`
- 胜率指标：`wins`, `losses`, `ties`
- LLM 评分：`accuracy`, `completeness`, `logic`, `readability`, `overall_score`, `rationale`

---

## 贡献指南

- 先阅读：`docs/CLAUDE.md`
- 提交流程建议：
  1. 新建分支并实现变更；
  2. 运行相关脚本/检查；
  3. 更新对应 `iter_XXX.md` 或周总结；
  4. 提交 PR 并附上关键输出说明。

---

## 联系与参考

- 联系方式：请在团队协作平台或代码托管平台 Issue/Discussion 中沟通。
- 参考文档：
  - `docs/practice_plan.md`
  - `docs/project_spec.md`
  - `docs/iterations/`
  - `docs/weekly_summaries/`
