# Day42：生成式 AI Evaluation Pipeline 总览

## 0. 文档定位

本文是“架构与方法论总结”，不是操作教程。目标是从系统工程视角说明：我们如何把数据、标注、自动指标、LLM 裁判与报告串成可复用的评测流水线，并解释其局限与扩展方向。

评测方法通常经历三步演进：

- 从词面匹配（BLEU/ROUGE）到语义匹配（METEOR/BERTScore）；
- 从单指标到多指标组合；
- 从离线打分到“自动指标 + LLM Judge + 人审抽检”的治理体系。

---

## 1. Data Layer：评测对象定义

### 1.1 数据集角色

- **SQuAD**：偏抽取式问答，检验定位与精确回答；
- **CoQA**：多轮问答，检验上下文记忆和对话连贯；
- **GLUE**：通用语言理解集合，补足分类/蕴含/匹配能力。

三者组合的意义在于能力覆盖，而不是简单拼盘。

### 1.2 Sample Schema

建议统一最小样本模式：

- `sample_id`（唯一 ID）
- `source_dataset`（SQuAD/CoQA/GLUE）
- `input`（问题/上下文/prompt）
- `reference`（一个或多个参考答案）
- `task_type`（qa/dialogue/classification/generation）
- `meta`（长度、领域、语言、难度、版本）

多轮任务需显式保留历史轮次，避免被错误降级为单轮字符串比较。

### 1.3 Sampling 与 Split

采样建议“分层 + 边界 + 回归”并行：

- 分层：按任务、长度、领域、难度均衡抽样；
- 边界：纳入长上下文、歧义问题、噪声输入；
- 回归：固定一批长期样本用于版本横比。

切分建议至少三层：

- `dev`：调参使用；
- `test-frozen`：冻结对比，避免泄漏；
- `challenge`：对抗与高风险样本。

---

## 2. Annotation Layer：语义真值构建

### 2.1 Guideline

标注规范必须可执行，至少包含：标签定义、判定边界、正反例、冲突优先级、无法判断条件。生成式任务建议把“事实性、相关性、完整性、可读性”分维记录，避免单标签掩盖问题。

### 2.2 Disagreement 处理

推荐流程：双人独立标注 → 分歧仲裁 → 记录分歧类型 → 回写 guideline。分歧本身是难例信号，可反向提升规则质量。

### 2.3 Cohen's Kappa

仅看一致率会失真，Kappa 能校正随机一致。可作为过程健康度指标：

- 低 Kappa：规范或培训需重做；
- 中等 Kappa：可用但要补示例；
- 较高 Kappa：进入稳定期并持续抽检。

### 2.4 工具：Label Studio / doccano

- **Label Studio**：流程可配置能力强，适合复杂 schema；
- **doccano**：部署轻、上手快，适合快速标注。

工具之外，更关键的是导出版本化、审计日志与可复审流程。

---

## 3. Metrics Layer：自动评测信号

- **BLEU**：n-gram 精确率导向，适合保守改写场景；
- **ROUGE**：召回导向，常用于摘要覆盖评估；
- **METEOR**：引入词干/同义词对齐，句级相关性更稳；
- **BERTScore**：基于上下文嵌入，能捕捉语义接近。

但自动指标必须带边界解释：

1. **overlap ≠ quality**（重叠高不代表质量高）；
2. **semantic similarity ≠ factual correctness**（语义相似不代表事实正确）；
3. 自动指标适合筛查与趋势监控，不应单独决定上线。

---

## 4. Judge Layer：LLM 裁判机制

### 4.1 LLM Judge 与 Pairwise

开放式任务中，LLM Judge 可补足传统指标盲区。相较绝对打分，pairwise（A/B）更稳定：更贴近用户偏好，也更易做排序建模与显著性分析。

### 4.2 生态组件位置

- **MT-Bench**：多轮对话评测基准；
- **OpenCompass**：多任务、多模型评测平台；
- **FastChat**：常用于多模型对话与评测流程集成。

它们是能力基建，不是“唯一真理源”。

### 4.3 Judge Bias

需重点防控：位置偏差、文风偏差、模型同源偏差、judge prompt 敏感性。标准做法包括顺序打乱、盲评、多裁判投票、人审抽检与定期重标。

必须明确：**judge ≠ human truth**。LLM 裁判是近似偏好模型，不是人类事实真值的替代。

---

## 5. Reporting Layer：从分数到决策

### 5.1 Metrics Report 结构

一份可落地报告应覆盖：

- 数据范围与版本（dataset/split/schema）；
- 指标总览（BLEU/ROUGE/METEOR/BERTScore）；
- 裁判结果（pairwise 胜率、置信区间）；
- 典型案例（优秀/失败/争议样本）；
- 风险结论（可上线、灰度、阻断）。

### 5.2 Limitations

常见限制：参考答案覆盖不足、跨领域泛化弱、人审成本高、Judge 版本变更导致可比性下降。

### 5.3 Future Work（可扩展性）

- 引入 claim-level 事实核查子流程；
- 增加安全性/可解释性/时效性维度；
- 建立线上反馈与离线评测对齐闭环；
- 推进指标插件化、数据版本治理与审计自动化。

---

## 6. 结论

生成式 AI 评测的本质，不是“找一个最高分指标”，而是建设可追溯、可迭代、可扩展的评测系统：

- Data Layer 决定比较边界；
- Annotation Layer 定义人类标准；
- Metrics Layer 提供规模化信号；
- Judge Layer 处理开放式偏好判断；
- Reporting Layer 将信号转化为工程决策。

只有把这五层联动起来，evaluation pipeline 才能真正服务模型迭代与产品质量治理。 
