# Day39 METEOR 机制解释报告（MVP）

## 背景与目标

在前序迭代中，BLEU 与 ROUGE-L 已经能够衡量生成文本与参考文本的重合程度，但它们都高度依赖 **surface overlap（表层字词重合）**。这会导致一个常见问题：

- 当候选答案进行了合理改写（同义替换、词形变化、句式变化）时；
- 模型输出在人类看来“意思接近”；
- 指标却可能因为字面不一致给出偏低分。

本报告目标不是再做“分数流水账”，而是解释：

1. 为什么 BLEU / ROUGE-L 容易低估改写；
2. 为什么 METEOR 在一些场景更宽松；
3. 为什么 METEOR 与人工判断更接近；
4. 为什么它仍然不是 semantic understanding（语义理解）指标。

---

## 实验设置与样本设计

本轮实验已基于 `scripts/day39_meteor_eval.py` 的固定样本集与统一流程完成，结果保存于 `outputs/day39_meteor_scores.csv`。

### 样本分组（experiment_type）

- `exact_match`：控制组，候选与参考基本一致；
- `stemming_effect`：测试词形变化（如时态/词性变化）；
- `synonym_match`：测试同义改写；
- `surface_mismatch`：语义接近但表层词汇与短语差异较大；
- `order_or_noise`：测试词序扰动与冗余噪声。

### 使用指标

- **METEOR**：结合 precision/recall，并支持 exact/stem/synonym 匹配；
- **BLEU**：以 n-gram precision 为主，偏好字面连续重合；
- **ROUGE-L**：以最长公共子序列（LCS）为核心，反映 sequence overlap。

这三者恰好构成“严格表层匹配 → 相对灵活匹配”的观察轴。

---

## 核心结果与现象分析（按机制，不按样本流水）

### 现象 1：控制组验证了评测链路稳定

`exact_1 / exact_2` 中，三个指标都处于高分区间。

- **现象**：字面一致时，三者都能稳定识别“正确匹配”；
- **机制**：此时不需要同义词或词干扩展，纯表层重合已足够；
- **指标含义**：后续差异可归因于“改写处理能力”，而非实现异常。

### 现象 2：词形变化场景下，METEOR 明显更稳

以 `stem_3` 为代表（analyze/analyzed 类变化）：

- **现象**：BLEU 对形态变化更敏感，分数明显回落；METEOR 保持高位；
- **机制**：METEOR 的 stem match 将词形变化映射到共同词干，减少“表面不一致”惩罚；
- **指标含义**：在“内容基本不变、只改词形”的生成中，METEOR更接近人类“本质没变”的判断。

### 现象 3：同义替换场景中，METEOR 比 BLEU 更能保留“语义接近性”

以 `syn_1 / syn_2` 为代表（boy→child, difficult→hard 等）：

- **现象**：BLEU 因 n-gram 精确匹配缺失而显著下降；METEOR 相对更高；
- **机制**：METEOR 的 synonym matching（由 WordNet 词汇关系支持）可识别部分同义映射；
- **指标含义**：当表达发生词汇级改写但核心意思仍接近时，METEOR更能反映人工判断中的“可接受改写”。

### 现象 4：表层大幅改写时，METEOR 也会显著降分

以 `surface_1 / surface_2` 为代表：

- **现象**：三项指标都下降，METEOR虽然通常高于BLEU，但并不“自动高分”；
- **机制**：METEOR本质仍依赖 lexical matching，词汇桥接不足时无法完整恢复深层语义等价；
- **指标含义**：METEOR 的“宽松”是有限宽松，不是语义推理能力。

### 现象 5：词序扰动与噪声会暴露“非语义性”边界

`order_1` 与 `noise_1` 对边界最有解释力：

- **现象**：即便词汇重合较多，词序异常或冗余噪声仍会影响各指标；
- **机制**：METEOR并非只做词袋计数，它包含对匹配片段组织方式的惩罚；
- **指标含义**：它比BLEU更灵活，但仍不能真正理解“句子是否逻辑自然、推理成立”。

---

## METEOR 行为机制分析

METEOR 可理解为“三层匹配 + 平衡式评分 + 结构惩罚”：

1. **Exact match**：先吃到与 BLEU/ROUGE 共通的字面重合信息；
2. **Stem match**：把词形变化拉回同一词干空间，降低形态噪声；
3. **Synonym match**：把部分同义表达纳入可匹配集合；
4. **Precision/Recall 平衡**：不像 BLEU 那样主要偏 precision；
5. **片段化惩罚**：避免“关键词堆砌”在无序情况下获得不合理高分。

因此它在改写场景通常比 BLEU 更稳：

- BLEU 看的是“短语是否原样重现”；
- METEOR 更关注“是否能对齐到近似语义单元”。

但这种“近似语义单元”仍主要建立在词汇资源与词形归一化之上，不等于真正语义建模。

---

## 与 BLEU / ROUGE-L 的对比分析

### BLEU：precision 导向，强依赖精确 n-gram

- 优点：对模板化、字面一致任务有判别力；
- 局限：对同义替换、语序重写、轻度改写敏感，容易低估可接受答案。

### ROUGE-L：sequence overlap 导向

- 优点：比纯 n-gram 更能容忍局部变化；
- 局限：本质仍是表层序列对齐，难覆盖词汇替换带来的语义等价。

### METEOR：更 flexible 的 lexical matching

- 优点：在 stemming/synonym 场景更接近人工“意思差不多即可”的评价习惯；
- 局限：词汇层增强并不等于语义层理解，面对深层语义与推理仍会失效。

**综合判断**：
在本轮样本分布里，METEOR 对改写更加友好，通常比 BLEU / ROUGE-L 更接近人工直觉；但它仍属于“增强版词汇匹配”，不是 semantic evaluation。

---

## 风险与局限

本节必须作为报告的“防误读”部分：

1. **METEOR 不是 semantic understanding**：它提升的是词汇匹配弹性，不是语义推理能力；
2. **仍依赖 lexical matching**：深层改写、隐含因果、跨句推断可能被低估或误判；
3. **WordNet 覆盖有限**：同义词资源对领域术语、新词、上下文义项覆盖不完整；
4. **无法评估 factual correctness**：即使分数高，也可能事实错误；
5. **无法评估 reasoning correctness / logical consistency**：推理链错误、逻辑矛盾不一定被惩罚到位。

因此，METEOR 适合作为“比 BLEU/ROUGE 更灵活的传统过渡指标”，不适合作为单一最终质量标准。

---

## 结论与下一步

### 核心结论

A. 在 `stemming_effect` 与 `synonym_match` 场景下，METEOR 通常比 BLEU / ROUGE-L 更接近人工判断。  
B. METEOR 的优势来自更灵活的匹配机制（stem + synonym + P/R 平衡），而非深层语义理解。  
C. 它仍无法可靠判断 factuality、reasoning、logical consistency。

### 下一步建议

为弥补传统 lexical metrics 的边界，下一阶段应引入 embedding-based metrics：

- 例如 **BERTScore**（基于上下文向量相似度）；
- 将其与 METEOR 组合使用，形成“词汇层 + 语义层”的双视角评估；
- 在报告中继续沿用“现象 → 机制 → 指标含义”的解释框架，避免重新回到分数流水账。

---

## 报告完整性自检（Task 4）

- [x] Markdown 章节结构完整；
- [x] 已覆盖重点 case：`exact_1/exact_2`, `stem_3`, `syn_1/syn_2`, `surface_1/surface_2`, `order_1`, `noise_1`；
- [x] 明确解释 stem matching 与 synonym matching；
- [x] 明确写出 WordNet limitation；
- [x] 结论引出 embedding metrics 与 BERTScore；
- [x] 以机制解释为主，非分数流水账。
