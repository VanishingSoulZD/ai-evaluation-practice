# Day42：自动指标与 LLM Judge 评测矩阵

## 1. 背景与结论先行
在文本生成评测里，BLEU/ROUGE/METEOR/BERTScore 与 LLM Judge 常被混用，但它们衡量的是不同层面的“相似”或“好”。如果不区分目标，评测会产生系统性偏差。三个必须明确的原则是：

- **overlap ≠ quality**：词面重叠高，不代表答案真的更好。
- **semantic similarity ≠ factual correctness**：语义相近不代表事实正确。
- **judge ≠ ground truth**：评审模型意见有价值，但不是客观真值。

---

## 2. 核心对比表（Metric / Judge Matrix）

| 方法 | 核心思想 | 典型适用任务 | 主要优势 | 主要局限 | 常见 failure modes | 推荐使用场景 |
|---|---|---|---|---|---|---|
| **BLEU** | 基于 n-gram 精确率与 brevity penalty，衡量候选与参考的词面重叠 | 机器翻译、模板化生成 | 简单、快速、可复现、历史可比性强 | 对同义改写不友好；句级稳定性差；与人评相关性受任务影响 | 高 BLEU 但语义生硬；关键词堆砌；对自由表达低分 | 需要与历史结果对齐的 MT/受控生成基线；不宜单独用于开放生成 |
| **ROUGE** | 主要看召回（如 ROUGE-N、ROUGE-L），衡量参考内容被覆盖程度 | 摘要、长文本压缩 | 对“信息覆盖”直观；摘要场景常用 | 偏词面；对表达多样性鲁棒性有限 | 抄参考片段得高分；遗漏关键事实但仍有可观分数 | 摘要初筛、ablation 快速比较；需搭配事实性指标 |
| **METEOR** | 结合 unigram 对齐、词干/同义匹配与惩罚项 | 翻译、改写 | 比 BLEU 更关注召回与语义近邻；句级相关性通常更好 | 资源依赖（词形/同义词）；跨域迁移表现不稳定 | 词汇层“近义”命中但语用不当；句法错误被低敏感处理 | 中小规模翻译/改写实验，作为 BLEU 的补充 |
| **BERTScore** | 用上下文嵌入比较 token 语义相似度（P/R/F1） | 改写、摘要、开放式生成 | 对同义表达更鲁棒；语义层相关性通常优于纯重叠指标 | 对事实错误不敏感；受底层编码器与语言域影响 | 语义“像”但事实反；幻觉细节未被惩罚 | 语义质量评估、改写与创意生成比较；必须加事实校验 |
| **LLM Judge（单点评分）** | 让评审模型按 rubric 对回答打分或分类 | 开放问答、对话、推理输出 | 能评估连贯性、帮助性、风格、步骤质量等高阶维度 | 成本高、方差高、提示敏感、模型偏好显著 | leniency/harshness bias；位置偏置；提示泄漏；“会写但不真”得高分 | 需要多维主观质量判断时；建议多次采样+盲评模板 |
| **LLM Judge（Pairwise）** | 两个候选直接比较优劣（A/B）而非绝对分数 | 模型迭代、策略对比、在线实验前离线筛选 | 对标尺漂移更稳；更贴近“选择哪个更好”决策 | 仍受评审偏置影响；并列难处理；传递性不总成立 | position bias（先后顺序影响）；verbosity bias（更长更占优） | 版本对比、prompt 对比、回归测试中的优选环节 |

---

## 3. 方法演进：从 overlap 到 semantic，再到 judge

可把评测演进理解为三层：

1. **Overlap 层（BLEU/ROUGE/METEOR）**：
   关注“写得像不像参考答案”。优点是稳定、便宜、快；缺点是容易把“像”误当“好”。

2. **Semantic 层（BERTScore 等）**：
   关注“语义近不近”。解决了大量同义改写问题，但无法天然保证事实与逻辑正确。

3. **Judge 层（LLM-as-a-Judge）**：
   关注“整体是否更好”，可结合任务 rubric 判断帮助性、可读性、推理步骤质量。代价是主观性和偏置更强。

**实践上不应单点押注**：
- 只看 overlap，会错杀高质量改写；
- 只看 semantic，会放过“语义像但事实错”；
- 只看 judge，会把评审偏好误当客观标准。

---

## 4. overlap vs semantic vs judge：如何组合

推荐采用“**三层证据链**”思路：

- **第 1 层（Overlap）**：做快速回归报警（是否明显退化）。
- **第 2 层（Semantic）**：看表达多样性下是否保持语义等价。
- **第 3 层（Judge）**：按业务 rubric 评估可用性与用户感知质量。

一个简化组合示例：
- 摘要任务：`ROUGE-L + BERTScore + factuality/judge`；
- 开放问答：`BERTScore(可选) + pairwise judge + 事实核查`；
- 推理任务：`judge(步骤与结论分开) + 程序化校验(若可行)`。

---

## 5. Pairwise Judge：为什么常比绝对打分更实用

在模型迭代里，业务问题通常不是“这条答案是 7.8 还是 8.1”，而是“**A 和 B 选哪个上线**”。Pairwise 更贴近该决策，优点包括：

- 降低评审标尺漂移（不同批次打分口径变化）。
- 对小幅质量差异更敏感。
- 更容易做显著性统计（win-rate / tie-rate）。

但要控制设计偏差：
- 随机化展示顺序（缓解 position bias）。
- 控制长度提示（缓解 verbosity bias）。
- 盲化模型身份与系统提示。

---

## 6. Judge Bias：常见偏置与缓解策略

常见偏置：
- **Position bias**：先看/后看影响选择。
- **Verbosity bias**：更长更像“认真回答”。
- **Style bias**：措辞华丽但信息空洞仍高分。
- **Self-preference bias**：评审模型偏好与自己风格相近的输出。
- **Prompt sensitivity**：评分随 rubric 文字微调而波动。

缓解策略：
- 固定并版本化 rubric；
- 同题多次评审、取多数或平均；
- A/B 顺序随机；
- 引入人类抽检集做锚点；
- 将“事实正确”拆成独立维度或外部校验。

---

## 7. 任务推荐矩阵（QA / Summarization / Paraphrase / Open-ended / Reasoning）

| 任务 | 首选评测组合 | 不建议单独使用 | 关键补充 |
|---|---|---|---|
| **QA（事实问答）** | Pairwise Judge（正确性 rubric）+ 事实核查 +（可选）BERTScore | 仅 BLEU/ROUGE | 必须显式检查证据一致性与拒答策略 |
| **Summarization** | ROUGE-L + BERTScore + Judge（覆盖/忠实/简洁） | 仅 ROUGE | 增加 factual consistency 检查，防摘要幻觉 |
| **Paraphrase** | BERTScore + METEOR + Judge（保真与流畅） | 仅 BLEU | 加语义保真约束，避免“改写成改义” |
| **Open-ended Generation** | Pairwise Judge + rubric 多维评分（有用性/安全/风格） | 任何单一重叠指标 | 加安全与事实抽检；看用户偏好指标 |
| **Reasoning** | Judge（步骤正确性+结论正确性分离）+ 可执行/可验证测试 | 仅语义相似度指标 | 尽量使用程序化判定或单元测试做外部真值 |

---

## 8. 落地建议（Day42 可执行版）

1. 先定义任务目标：你要优化的是“参考贴合度”、 “语义保真”、还是“用户可用性”。
2. 每个任务至少使用两类指标（例如 overlap + judge，或 semantic + factual）。
3. 涉及事实与推理的任务，必须引入 judge 之外的外部校验。
4. 做版本对比优先 pairwise judge，并记录 win/tie/loss 与样本案例。
5. 将本页三条红线写入评测规范：
   - overlap ≠ quality
   - semantic similarity ≠ factual correctness
   - judge ≠ ground truth

以上矩阵的核心目的不是“选出唯一最好指标”，而是建立一个**分层、互补、可解释**的评测体系。
