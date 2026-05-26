# ai-evaluation-practice-plan

### **Week 1：数据标注与数据分析基础**

| 日    | 背景/目的                  | 解决问题               | 参考资料                                   | 任务要求                                  | 实现步骤                                                      | 验收                                 |
| ----- | -------------------------- | ---------------------- | ------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------- | ------------------------------------ |
| Day 1 | 熟悉数据标注基本概念和规范 | 了解标注规则、标签边界 | 开源文本数据集（SQuAD、GLUE）、NLP标注教程 | 理解标注任务类型，做10条示例标注          | 1. 阅读标注规则<br>2. 手工标注10条示例<br>3. 标注说明写成文档 | 文档中清楚记录标注规则及边界         |
| Day 2 | 数据标注实践               | 掌握标注操作和审核流程 | SQuAD/CoQA/自己模拟数据                    | 完成50条文本标注                          | 1. 准备50条样本<br>2. 标注并校对<br>3. 记录易错标签           | 标注准确率≥90%，能识别边界问题       |
| Day 3 | 数据一致性检查             | 学会统计标注质量       | Pandas基础教程、Python数据分析             | 编写Python脚本统计一致率、重复值、缺失值  | 1. 导入CSV/Excel<br>2. 统计重复/缺失<br>3. 计算一致率         | 输出报告表格，展示统计结果           |
| Day 4 | 数据分布可视化             | 了解数据结构、分布     | Matplotlib/Seaborn官方教程                 | 绘制直方图、条形图、热力图                | 1. 导入标注数据<br>2. 可视化标签分布<br>3. 保存图表           | 图表清晰反映数据分布，可用于汇报     |
| Day 5 | 小型综合练习               | 将标注+分析结合        | SQuAD/自制小数据集                         | 做50条标注 → 统计一致率 → 输出分布图      | 1. 标注数据<br>2. Python统计<br>3. 绘图                       | 能完整输出“标注→分析→可视化”流程结果 |
| Day 6 | Python基础复习与优化       | 为后续指标计算打基础   | Pandas/NumPy教程                           | 掌握数据操作函数（groupby、merge、apply） | 1. 复习基础函数<br>2. 练习小数据处理                          | 能用函数处理数据并生成结果           |
| Day 7 | 回顾与总结                 | 巩固Week1知识          | 前6天产出                                  | 写周总结文档，整理脚本、图表              | 1. 总结学习收获<br>2. 整理脚本/文档                           | 周总结文档完整，脚本可复用           |

---

### **Week 2：评测指标与自动化脚本**

| 日     | 背景/目的        | 解决问题                      | 参考资料                          | 任务要求                       | 实现步骤                                                | 验收                         |
| ------ | ---------------- | ----------------------------- | --------------------------------- | ------------------------------ | ------------------------------------------------------- | ---------------------------- |
| Day 8  | 文本评测指标理解 | 理解ROUGE、BLEU、准确率、胜率 | NLP教材、官方论文、Python实现例子 | 学习指标公式和计算方法         | 1. 阅读指标原理<br>2. 手算小例子                        | 能解释指标含义并完成手算示例 |
| Day 9  | Python实现指标   | 实现指标计算函数              | Python + NLTK/rouge库             | 写ROUGE/BLEU函数               | 1. 导入小样本数据<br>2. 编写函数计算指标<br>3. 输出结果 | 输出正确结果，符合手算例子   |
| Day 10 | 指标验证与优化   | 检查指标函数正确性            | Python                            | 用小样本验证函数，调试错误     | 1. 准备测试数据<br>2. 比对手算结果<br>3. 修正错误       | 函数计算结果100%正确         |
| Day 11 | 模块化封装       | 练习模块化设计                | Python OOP教程                    | 封装指标计算类/函数            | 1. 定义类：输入数据→计算指标→返回结果<br>2. 写注释      | 模块化代码可复用，接口清晰   |
| Day 12 | 报告生成初步     | 输出CSV/表格报告              | Pandas/Matplotlib                 | 将指标结果生成表格+图表        | 1. 计算指标<br>2. 输出CSV<br>3. 绘图保存                | 生成完整报告，图表清晰       |
| Day 13 | 自动化脚本练习   | 批量处理数据                  | Python                            | 写脚本处理多批数据             | 1. 准备多批数据<br>2. 批量运行指标计算<br>3. 生成报告   | 能批量计算并输出报告         |
| Day 14 | 周总结           | 巩固Week2成果                 | 前7天产出                         | 整理模块化脚本、示例数据、报告 | 1. 汇总脚本<br>2. 写文档说明                            | 文档+脚本可直接复用          |

---

### **Week 3：平台接口与异步任务**

| 日     | 背景/目的         | 解决问题      | 参考资料            | 任务要求                        | 实现步骤                                               | 验收                       |
| ------ | ----------------- | ------------- | ------------------- | ------------------------------- | ------------------------------------------------------ | -------------------------- |
| Day 15 | FastAPI入门       | 构建简单接口  | FastAPI官方教程     | 写上传数据→返回结果API          | 1. 安装FastAPI<br>2. 写最简单接口<br>3. 测试返回JSON   | 接口可访问，能返回示例数据 |
| Day 16 | 文件上传接口      | 支持CSV上传   | FastAPI             | 写文件上传并保存                | 1. 写POST接口<br>2. 保存上传文件<br>3. 返回确认信息    | 上传CSV成功并保存          |
| Day 17 | 批量指标计算API   | 接口调用脚本  | Week2模块化指标代码 | 接收上传CSV，批量计算指标       | 1. 导入CSV<br>2. 调用指标计算类<br>3. 返回JSON/表格    | JSON输出指标正确           |
| Day 18 | 异步任务入门      | 处理大数据集  | Celery/RQ教程       | 写异步任务处理批量指标          | 1. 配置Celery/RQ<br>2. 封装任务函数<br>3. 调用异步任务 | 批量任务异步完成，结果正确 |
| Day 19 | 异步任务与报告    | 自动生成报告  | Python              | 异步完成指标计算 → 输出CSV/图表 | 1. 异步调用指标函数<br>2. 生成报告<br>3. 保存文件      | 报告生成自动化完成         |
| Day 20 | 接口+异步综合练习 | 流程集成      | Week2+Week3成果     | 上传CSV → 异步计算 → 返回报告   | 1. 写整合API<br>2. 测试流程<br>3. 输出报告             | 流程运行正确，自动化       |
| Day 21 | 周总结            | 巩固Week3成果 | 前7天产出           | 文档+代码整理                   | 1. 汇总脚本<br>2. 写使用说明                           | 文档完整，接口可直接使用   |

---

### **Week 4：前沿方法 + 综合演练**

| 日     | 背景/目的              | 解决问题       | 参考资料                 | 任务要求                          | 实现步骤                                          | 验收                     |
| ------ | ---------------------- | -------------- | ------------------------ | --------------------------------- | ------------------------------------------------- | ------------------------ |
| Day 22 | LLM-as-a-Judge概念理解 | 理解评测新范式 | OpenCompass/MT-Bench论文 | 读文档，写总结                    | 1. 阅读框架文档<br>2. 理解评分流程                | 能口头/文档解释流程      |
| Day 23 | LLM评分实验            | 小规模验证     | GPT-API                  | 输入示例文本 → GPT评分 → 输出分析 | 1. 调用模型<br>2. 获取评分<br>3. 保存结果         | 输出评分表格正确         |
| Day 24 | 对抗性测试实验         | 模拟异常输入   | NLP对抗性测试文献        | 设计5个对抗性输入                 | 1. 准备输入<br>2. 模型预测<br>3. 记录指标变化     | 输出结果体现对抗影响     |
| Day 25 | 仿真环境评估           | 模拟用户交互   | 对话生成文献             | 设计简单模拟对话                  | 1. 准备输入数据<br>2. 模拟交互<br>3. 记录指标     | 输出对话指标表格         |
| Day 26 | 综合流程练习           | 标注→指标→报告 | Week1~Week4              | 模拟完整流程                      | 1. 标注小数据集<br>2. 批量计算指标<br>3. 生成报告 | 生成完整报告，流程可复用 |
| Day 27 | 跨团队沟通模拟         | 输出分析结论   | 自己产出报告             | 写简短汇报文档                    | 1. 撰写文档<br>2. 总结数据问题与建议              | 文档清晰可读，可用作汇报 |
| Day 28 | 总结与整理             | 全面复盘       | 全部成果                 | 整理代码/报告/文档                | 1. 汇总所有脚本<br>2. 输出周报式总结              | 所有脚本可复用，文档完整 |

# Practice Plan（Day 29 ~ Day 42）

> 本文档是 `ai-evaluation-practice` 项目的第 29 天到第 42 天实操计划，承接前 28 天的已有迭代。
> 这一阶段的目标不是“看懂概念”，而是把一条**可复用、可复核、可落地**的 NLP/LLM 评测链路跑通：
>
> 1. 选定主流数据集和任务；
> 2. 完成标注规范、标注工具配置、双人标注与一致性分析；
> 3. 用主流指标库完成自动评测；
> 4. 接入 LLM-as-a-judge 的评测思路；
> 5. 输出一个有实际参考价值的小型评测项目。

---

## 一、这一轮的最终目标

这一轮不要做“玩具式演示”，而是做一个**真实可复用的小型评测项目**。建议最终项目定位为：

> **面向文本生成与问答场景的评测基线项目**
>
> 包含：
>
> - 主流公开数据集样本抽取与组织；
> - 标注规范与人工标注流程；
> - 一致性指标（Cohen’s Kappa）；
> - 自动指标（BLEU / ROUGE / METEOR / BERTScore）；
> - LLM judge 评测入口（OpenCompass / MT-Bench / FastChat 思路）；
> - 结果报表与图表输出。

### 适合的实际意义

这个项目不是为了“做一个最强 benchmark”，而是为了练出一套以后做真实项目时可直接复用的方法：

- 新任务来了，知道如何定义样本、标签和标准；
- 多人协作时，知道如何控制一致性；
- 生成任务来了，知道传统指标和 judge 指标怎么配合；
- 最后能产出一份结构清晰、可解释的评测报告。

---

## 二、资源使用原则

### 1）外部资源只看必要部分

本轮会提供外部资源网址，但不要求你从头到尾自己摸索。每个资源只看与当前任务直接相关的部分。

### 2）任务与数据集由计划指定

不再让你自己临时选“文本分类 / 问答抽取 / 对话回答”之一，而是按任务链路来做：

- **SQuAD**：问答抽取 / 阅读理解；
- **CoQA**：多轮对话问答；
- **GLUE**：通用语言理解中的分类/判断任务；
- **生成指标任务**：摘要/改写/问答生成；
- **judge 任务**：对开放式回答进行偏好或分数评估。

### 3）工具使用要求

- 标注工具：优先使用 **Label Studio** 和 **doccano**。
- 指标实现：优先使用主流库，而不是手写“仅供演示”的版本。
- 项目输出：每一天都要落到脚本、数据、报告或图表文件。

### 4）推荐仓库结构约定

建议在当前仓库内延续已有命名方式：

- `scripts/day29_*.py` ~ `scripts/day42_*.py`
- `data/day29_*` ~ `data/day42_*`
- `outputs/day29_*` ~ `outputs/day42_*`
- `reports/day29_*` ~ `reports/day42_*`
- `docs/iterations/iter_029.md` ~ `docs/iterations/iter_042.md`

---

## 三、外部资源入口

以下资源在本轮会用到，先记住网址，不要求一次性全部看完：

### 数据集

- SQuAD: [https://rajpurkar.github.io/SQuAD-explorer/](https://rajpurkar.github.io/SQuAD-explorer/)
- GLUE: [https://gluebenchmark.com/](https://gluebenchmark.com/)
- CoQA: [https://stanfordnlp.github.io/coqa/](https://stanfordnlp.github.io/coqa/)

### 标注工具

- Label Studio: [https://labelstud.io/](https://labelstud.io/)
- Label Studio 文档: [https://labelstud.io/guide/](https://labelstud.io/guide/)
- doccano: [https://doccano.github.io/doccano/](https://doccano.github.io/doccano/)
- doccano tutorial: [https://doccano.github.io/doccano/tutorial/](https://doccano.github.io/doccano/tutorial/)
- doccano install: [https://doccano.github.io/doccano/install_and_upgrade_doccano/](https://doccano.github.io/doccano/install_and_upgrade_doccano/)

### 一致性与评测

- Cohen’s Kappa 说明（可参考综述/教程，后续迭代文档中会展开）
- OpenCompass: [https://opencompass.org.cn/](https://opencompass.org.cn/)
- OpenCompass 文档（LLM judge 相关）: [https://doc.opencompass.org.cn/advanced_guides/llm_judge.html](https://doc.opencompass.org.cn/advanced_guides/llm_judge.html)
- MT-Bench 论文: [https://arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)
- FastChat: [https://github.com/lm-sys/fastchat](https://github.com/lm-sys/fastchat)
- Chatbot Arena: [https://lmarena.ai/](https://lmarena.ai/)

### 自动指标

- BLEU 论文: [https://aclanthology.org/P02-1040/](https://aclanthology.org/P02-1040/)
- ROUGE 论文: [https://aclanthology.org/W04-1013/](https://aclanthology.org/W04-1013/)
- METEOR 论文: [https://aclanthology.org/W05-0909/](https://aclanthology.org/W05-0909/)
- BERTScore: [https://github.com/Tiiiger/bert_score](https://github.com/Tiiiger/bert_score)

### 可视化与实验

- Matplotlib: [https://matplotlib.org/](https://matplotlib.org/)
- Seaborn: [https://seaborn.pydata.org/](https://seaborn.pydata.org/)
- Kaggle: [https://www.kaggle.com/](https://www.kaggle.com/)

---

# Day 29 ~ Day 42

---

## Day 29：确定本轮项目主题与任务边界

### 目标

把本轮实操的“评测对象”定下来，避免后面边做边改。

### 任务

1. 选定本轮主线为：**文本生成 + 问答评测**。
2. 明确两个子任务：
   - 子任务 A：SQuAD / CoQA 风格的问答评测；
   - 子任务 B：生成任务的自动指标评测（BLEU / ROUGE / METEOR / BERTScore）。

3. 定义最终交付物：
   - 一个主数据集样本集；
   - 一份标注规范；
   - 一份双人标注一致性分析；
   - 一套自动指标脚本；
   - 一份 judge 评测说明；
   - 一份完整报告。

### 你要产出的文件

- `docs/iterations/iter_029.md`
- `docs/practice_plan.md`（本文件后续可继续更新）
- `data/day29_project_scope.md`

### 这一日要确认的判断

- 这个项目不是单纯做分类，而是做**可落地的生成式评测链路**。
- 如果后面要给真实项目服务，这条链路既能用于问答，也能扩展到摘要、改写和对话。

---

## Day 30：理解 SQuAD、CoQA、GLUE 的样本结构

### 目标

把主流数据集的输入输出结构搞清楚。

### 任务

1. 浏览 SQuAD、CoQA、GLUE 的官方页面，只看三件事：
   - 数据长什么样；
   - 标签长什么样；
   - 适合评测什么能力。

2. 提取少量样本到本地，建立统一目录。
3. 做一个小型对比文档，比较三者的任务形式：
   - SQuAD：单轮阅读理解 / span answer；
   - CoQA：多轮上下文相关问答；
   - GLUE：通用语言理解任务集合。

### 建议的数据组织方式

```
data/day30_raw/
  squad/
  coqa/
  glue/
```

### 你要产出的文件

- `docs/iterations/iter_030.md`
- `data/day30_raw/README.md`
- `data/day30_task_comparison.md`

### 这一日要得到的结论

- SQuAD 更适合练“答案是否命中证据 span”；
- CoQA 更适合练“上下文依赖与多轮对话”；
- GLUE 更适合练“通用语言理解的分类/匹配判断”。

---

## Day 31：从主流数据集中抽取本轮样本

### 目标

不要自己造样本，直接从主流数据集中抽取。

### 任务

1. 从 SQuAD / CoQA / GLUE 中抽取一小批适合评测的样本。
2. 设计统一样本格式，至少包含：
   - `sample_id`
   - `source_dataset`
   - `input`
   - `reference`
   - `task_type`
   - `difficulty_tag`

3. 把样本拆分成：
   - 标注样本；
   - 开发样本；
   - 检查样本。

### 样本组织原则

- 优先保留主流数据集原始语义，不重新编造任务；
- 如果是生成任务，保留参考答案；
- 如果是问答任务，保留上下文、问题、参考答案；
- 如果是分类任务，保留输入和标签定义。

### 你要产出的文件

- `data/day31_samples.jsonl`
- `data/day31_samples.csv`
- `data/day31_sampling_notes.md`

### 本日要求

- 样本规模不要大，但一定要“结构正确”。
- 后续所有标注、指标、judge 都复用这批样本。

---

## Day 32：写一份可执行的标注规范

### 目标

让别人拿到你的规范就能标，不会凭感觉乱标。

### 任务

1. 编写一份标注规范，必须包含：
   - 任务定义；
   - 标签定义；
   - 正例；
   - 反例；
   - 边界样例；
   - 冲突处理规则；
   - 统一裁决规则。

2. 标注规范要按任务分模块写，不要写成一篇空泛说明。
3. 把本轮项目要做的任务全部纳入规范，而不是只写一个任务。

### 推荐覆盖的任务

- 阅读理解 / 问答抽取；
- 多轮问答；
- 文本生成质量判断；
- 简单分类或匹配判断（如 GLUE 中可复用的一类任务）。

### 你要产出的文件

- `data/day32_labeling_guideline.md`
- `data/day32_labeling_examples.md`

### 验收标准

- 规范是否能指导别人独立标注；
- 歧义样本是否有明确处理方法；
- 是否包含“必须一致”的裁决规则。

---

## Day 33：配置 Label Studio，跑通第一个项目

### 目标

完整学会 Label Studio 的最小闭环。

### 任务

1. 安装并启动 Label Studio。
2. 创建一个文本标注项目。
3. 导入第 31 天的样本。
4. 根据第 32 天的标注规范配置标注界面。
5. 做第一轮人工标注。
6. 导出结果，确认格式可用。

### 你在网站上要做的操作

- 新建 project；
- 选择文本相关的标注模板；
- 导入 JSON/CSV；
- 调整标签按钮、输入框和说明文字；
- 完成标注后导出结果。

### 你要产出的文件

- `outputs/day33_label_studio_export.*`
- `docs/iterations/iter_033.md`
- `data/day33_label_studio_setup.md`

### 这一日的关键能力

- 你要知道 Label Studio 适合做什么类型的任务；
- 你要知道它如何从“样本”变成“可标注项目”；
- 你要知道怎么把标注结果导出来给后续脚本使用。

---

## Day 34：配置 doccano，跑通第二个项目

### 目标

完整学会 doccano 的最小闭环，并理解它和 Label Studio 的差异。

### 任务

1. 安装并启动 doccano。
2. 创建一个新的文本标注项目。
3. 导入第 31 天的样本或它的子集。
4. 用 doccano 完成一轮标注。
5. 导出结果。
6. 对比 Label Studio 与 doccano 的差异。

### 你在网站上要做的操作

- 创建 project；
- 设置项目类型；
- 导入数据；
- 开始标注；
- 导出数据；
- 如有需要，检查 REST API 入口。

### 你要产出的文件

- `outputs/day34_doccano_export.*`
- `docs/iterations/iter_034.md`
- `data/day34_doccano_compare.md`

### 本日重点

- doccano 更适合哪类 NLP 标注；
- Label Studio 更适合哪类可定制标注；
- 两者的导出格式如何进入后续分析脚本。

---

## Day 35：做双人标注与分歧分析

### 目标

通过双人标注识别规范中的问题。

### 任务

1. 同一批样本用两份标注结果进行对照。
2. 找出所有分歧样本。
3. 对分歧进行分类：
   - 标签歧义；
   - 规则理解偏差；
   - 样本本身信息不足；
   - 边界样本。

4. 写出返工策略。

### 你要产出的文件

- `reports/day35_disagreement_analysis.csv`
- `reports/day35_disagreement_summary.md`
- `docs/iterations/iter_035.md`

### 本日要求

- 不只是列出分歧，要解释分歧为什么产生；
- 要把分歧反馈回标注规范，而不是只做统计。

---

## Day 36：计算 Cohen’s Kappa 并解释结果

### 目标

把“主观感觉不一致”变成“可量化的一致性分数”。

### 任务

1. 用第 35 天的双人标注结果计算 Cohen’s Kappa。
2. 解释分数含义，而不是只报数字。
3. 按标签或子任务分别计算，观察哪些任务最不稳定。

### 你需要理解的点

- Kappa 衡量的是“超过随机一致的部分”；
- 分数越高，说明标注越稳定；
- 如果分数偏低，通常不是“模型差”，而是“规范不清”或“样本歧义高”。

### 你要产出的文件

- `reports/day36_kappa_report.csv`
- `reports/day36_kappa_report.md`
- `docs/iterations/iter_036.md`

### 提升方向

- 重新写标签定义；
- 增加边界样本；
- 拆分过于含糊的标签；
- 让两位标注者先做小样本对齐。

---

## Day 37：实现 BLEU，并解释它能衡量什么

### 目标

把自动指标的“第一层”打通。

### 任务

1. 用主流库实现 BLEU。
2. 对一组生成样本计算 BLEU。
3. 观察字面重合和语序变化对分数的影响。

### 你需要理解的点

- BLEU 衡量的是 n-gram 重合程度；
- 它更偏向“精确率”；
- 适合翻译、模板式生成、表述较固定的任务；
- 对同义改写不够友好。

### 分数解读

- 分数很低：通常说明字面重合少、改写幅度大、生成偏离参考；
- 分数中等：说明部分关键短语命中；
- 分数较高：通常说明与参考表达接近，但不等于语义一定更好。

### 你要产出的文件

- `scripts/day37_bleu_eval.py`
- `outputs/day37_bleu_scores.csv`
- `docs/iterations/iter_037.md`

---

## Day 38：实现 ROUGE，并解释它能衡量什么

### 目标

理解摘要和覆盖类任务为什么常用 ROUGE。

### 任务

1. 用主流库实现 ROUGE-1 / ROUGE-2 / ROUGE-L。
2. 在同一批样本上与 BLEU 对照。
3. 观察召回型指标与精确率型指标的差异。

### 你需要理解的点

- ROUGE 更关注参考内容是否被覆盖；
- 适合摘要、问答生成、长文本概括；
- ROUGE-L 常用于衡量序列层面的最长公共子序列覆盖。

### 分数解读

- ROUGE 低：说明参考中的关键信息没有被覆盖；
- ROUGE 高：说明主要信息点被包含，但不代表表达一定自然；
- 如果 ROUGE 高但人工觉得差，可能是内容堆砌或冗余。

### 你要产出的文件

- `scripts/day38_rouge_eval.py`
- `outputs/day38_rouge_scores.csv`
- `docs/iterations/iter_038.md`

---

## Day 39：实现 METEOR，并理解它和前两个指标的差异

### 目标

补足一个更接近人工判断的传统指标。

### 任务

1. 用主流库实现 METEOR。
2. 和 BLEU / ROUGE 在同一批样本上比较。
3. 写出你对三者适用范围的判断。

### 你需要理解的点

- METEOR 比较强调词形变化、词匹配灵活性和与人工判断的一致性；
- 它通常比 BLEU 更宽松；
- 适合“表述不完全固定”的生成任务。

### 你要产出的文件

- `scripts/day39_meteor_eval.py`
- `outputs/day39_meteor_scores.csv`
- `docs/iterations/iter_039.md`

---

## Day 40：实现 BERTScore，并理解语义级评测

### 目标

从字面匹配迈向语义相似。

### 任务

1. 跑通 BERTScore。
2. 构造几组“字面差异大但语义接近”的句子。
3. 对比 BERTScore 与 BLEU / ROUGE / METEOR。

### 你需要理解的点

- BERTScore 利用上下文嵌入做语义比较；
- 对同义改写更友好；
- 对事实正确性不一定天然可靠，仍需要结合人工判断或 reference。

### 你要产出的文件

- `scripts/day40_bertscore_eval.py`
- `outputs/day40_bertscore_scores.csv`
- `docs/iterations/iter_040.md`

---

## Day 41：理解 OpenCompass 的 LLM judge 思路

### 目标

把“模型当裁判”的评测方式接起来。

### 任务

1. 阅读 OpenCompass 的 LLM judge 文档。
2. 阅读 MT-Bench 论文，理解为什么开放式回答不能只靠 n-gram 指标。
3. 阅读 FastChat 与 Chatbot Arena 的基本思路。
4. 写出一份 judge 评测说明。

### 你需要理解的论文精华

#### MT-Bench / Chatbot Arena

这篇工作的核心观点是：

- 对开放式对话，传统自动指标不够用；
- 可以让更强的 LLM 作为裁判；
- 需要注意 position bias、verbosity bias、self-enhancement bias 等偏差；
- pairwise 偏好比较通常比绝对打分更稳定。

#### OpenCompass judge

OpenCompass 提供了可复用的 LLM judge 组件，适合把你的评测任务组织成统一的评测格式。

#### FastChat / Chatbot Arena

FastChat 是一个支持训练、服务、评测聊天模型的平台；Chatbot Arena 则是匿名随机对战和人类投票的偏好评测形式。

### 你要产出的文件

- `docs/day41_llm_judge_notes.md`
- `docs/iterations/iter_041.md`

---

## Day 42：完成本轮最终小项目与总结报告

### 目标

把前 13 天的成果收束成一个完整项目。

### 项目交付要求

最终项目必须包含以下内容：

1. **数据层**
   - 来自 SQuAD / CoQA / GLUE 的真实样本；
   - 统一的样本格式；
   - 清晰的数据划分和来源说明。

2. **标注层**
   - 标注规范；
   - Label Studio 或 doccano 的配置与导出；
   - 双人标注结果；
   - 一致性分析。

3. **指标层**
   - BLEU / ROUGE / METEOR / BERTScore 中至少两项完整实现；
   - 指标结果表；
   - 指标解释与适用范围说明。

4. **judge 层**
   - LLM judge 的设计说明；
   - OpenCompass / MT-Bench / FastChat 参考关系说明；
   - 至少一个简单的 judge 评审示例。

5. **报告层**
   - 图表；
   - 结论；
   - 局限性；
   - 后续可扩展方向。

### 你要产出的文件

- `reports/day42_final_report.md`
- `reports/day42_final_report.xlsx`（如需要）
- `outputs/day42_final_metrics.*`
- `docs/iterations/iter_042.md`

### 最终总结要回答的问题

- 这条评测链路解决了什么问题？
- 哪些地方适合自动化，哪些地方必须人工？
- 哪些指标适合哪些任务？
- judge 评测什么时候比传统指标更合适？
- 这个项目以后能不能继续扩展成更完整的 AI 评测框架？

---

# 四、建议的执行节奏

如果你后面要按迭代文档持续写，每一天建议固定输出以下内容：

1. 本日目标；
2. 使用的外部资源网址；
3. 关键知识点摘要；
4. 操作步骤；
5. 实验结果；
6. 问题与修正；
7. 当日结论；
8. 下一个迭代建议。

---

# 五、这一轮结束时你应该具备的能力

完成 Day 29 ~ Day 42 后，你应该能独立做这些事：

- 从主流公开数据集中抽取并组织评测样本；
- 写出可执行的标注规范；
- 在 Label Studio / doccano 中完成标注闭环；
- 用 Cohen’s Kappa 做一致性分析；
- 用 BLEU / ROUGE / METEOR / BERTScore 做自动评测；
- 理解并组织 LLM judge 评测；
- 输出一份结构完整、可复用、可解释的评测报告。

---

# 六、后续迭代约定

从本文件开始，后续所有实践计划与迭代文档统一从 **Day 29** 顺延编号，不再沿用前 28 天的编号方式。
