# Day32 标注示例文档（MVP）

> 目的：提供可执行的“轻量示例集”，帮助标注员/复核员按同一口径执行 Day32 主规范。  
> 约束：本文件是示例补充，不新增主标签体系；冲突时以 `data/day32_labeling_guideline.md` 为准。

---

## 1. 使用说明（最小）

- 每个示例仅包含：输入、期望输出、最小理由。
- 主标签保持轻量：
  - QA 类：`SUPPORTED` / `UNSUPPORTED` / `AMBIGUOUS`
- `MULTI_ANSWER`、`AMBIGUOUS_SPAN` 仅作为解释性歧义说明，不作为新增主标签。
- `rule_id` 使用轻量引用（如：`QA-R1`、`DIALOGUE-R2`、`GEN-R1`）。

---

## 2. QA 抽取模块（qa_span）

### QA 规则（轻量）
- `QA-R1`：仅依据 context 可见证据，不使用外部常识。
- `QA-R2`：有直接证据且答案语义一致 -> `SUPPORTED`。
- `QA-R3`：无直接证据或与 context 冲突 -> `UNSUPPORTED`。
- `QA-R4`：答案大方向可判断，但证据边界/题面约束无法唯一 -> `AMBIGUOUS`。

### EX-QA-01（正例）
- sample_id: `squad_train_0003`
- rule_id: `QA-R1, QA-R2`

**Input**
- context: "Beyoncé Giselle Knowles-Carter is an American singer, songwriter, record producer and actress."
- question: "What is the full name of Beyoncé?"
- answer_candidate: "Beyoncé Giselle Knowles-Carter"

**Expected**
- label: `SUPPORTED`
- final_answer: `Beyoncé Giselle Knowles-Carter`
- evidence_span: `Beyoncé Giselle Knowles-Carter`

**Why**
- 候选答案与 context 显式一致，可直接定位。

### EX-QA-02（反例）
- sample_id: `squad_train_0002`
- rule_id: `QA-R3`

**Input**
- context: "The Grotto of Our Lady of Lourdes is one of the most recognizable landmarks on the campus of the University of Notre Dame."
- question: "What is in front of the Notre Dame Main Building?"
- answer_candidate: "the Grotto of Our Lady of Lourdes"

**Expected**
- label: `UNSUPPORTED`
- final_answer: `N/A`
- evidence_span: ``

**Why**
- context 只说该地标“位于校园中”，未直接支持“在 Main Building 前方”。

### EX-QA-03（边界）
- sample_id: `squad_train_0001`
- rule_id: `QA-R4`

**Input**
- context: "Architecturally, the school has a Catholic character. Atop the Main Building's gold dome is a golden statue of the Virgin Mary."
- question: "To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?"
- answer_candidate: "Saint Bernadette Soubirous"

**Expected**
- label: `AMBIGUOUS`
- final_answer: `N/A`
- evidence_span: ``
- ambiguity_note: `样本 reference 给出答案，但当前 context 片段本身不含该事实；是数据截断风险还是真实不可支持，需最小裁决。`

**Why**
- 不可凭外部常识补齐；但 reference 与 context 存在不一致迹象，需要进入歧义处理。

### EX-QA-04（边界：多答案说明）
- sample_id: `squad_train_0005`
- rule_id: `QA-R4`

**Input**
- context: "Solar power is the conversion of energy from sunlight into electricity, either directly using photovoltaics."
- question: "What does solar power convert into electricity?"
- answer_candidate: "sunlight"

**Expected**
- label: `AMBIGUOUS`
- final_answer: `energy from sunlight`
- evidence_span: `energy from sunlight`
- ambiguity_note: `"sunlight" 与 "energy from sunlight" 在该句中可能被不同标注员视为可接受同义粒度。`

**Why**
- 核心语义可支持，但答案粒度与最小 span 边界可能出现分歧。

---

## 3. 对话问答模块（qa_dialogue）

### DIALOGUE 规则（轻量）
- `DIALOGUE-R1`：history 是可用证据的一部分；不得忽略已给历史轮次。
- `DIALOGUE-R2`：若当前问题依赖指代，必须能在 history+context 中回溯实体。
- `DIALOGUE-R3`：仅靠猜测补全对话信息 -> `UNSUPPORTED` 或 `AMBIGUOUS`。

### EX-DIA-01（正例）
- sample_id: `coqa_dev_0002`
- rule_id: `DIALOGUE-R1, DIALOGUE-R2`

**Input**
- context: "The boy went to the park with his dog. ..."
- history: `[{"turn_id":1,"question":"Where did the boy go?","answer":"to the park"}]`
- question: "Who went with him?"
- answer_candidate: "his dog"

**Expected**
- label: `SUPPORTED`
- final_answer: `his dog`
- evidence_span: `with his dog`

**Why**
- 指代 “him” 可在上下文稳定回溯，答案直接可证。

### EX-DIA-02（反例）
- sample_id: `coqa_dev_0004`
- rule_id: `DIALOGUE-R3`

**Input**
- context: "... they sat under a tree because it started to rain."
- history: （同源前序轮次）
- question: "Why did they sit under a tree?"
- answer_candidate: "because they were tired"

**Expected**
- label: `UNSUPPORTED`
- final_answer: `N/A`
- evidence_span: ``

**Why**
- context 已给出明确因果是“下雨”，与候选冲突。

### EX-DIA-03（边界）
- sample_id: `coqa_dev_0005`
- rule_id: `DIALOGUE-R2`

**Input**
- context: "... He threw a red ball, and the dog ran after it."
- history: 包含前 1~4 轮
- question: "Who ran after the ball?"
- answer_candidate: "dog"

**Expected**
- label: `AMBIGUOUS`
- final_answer: `the dog`
- evidence_span: `the dog ran after it`
- ambiguity_note: `答案本身明确，但是否必须保留定冠词（dog vs the dog）在输出规范上可能有轻微分歧。`

**Why**
- 事实支持清楚，但输出文本标准化粒度可能不一致。

---

## 4. 通用分类模块（text_classification / sentence_pair / textual_inference）

### GEN 规则（轻量）
- `GEN-R1`：严格使用样本内 label 语义映射，不跨任务复用口径。
- `GEN-R2`：句对任务先判语义关系，再映射标签值。
- `GEN-R3`：文本不足以确定唯一关系时，标记 `AMBIGUOUS` 并记录分歧点。

### EX-GEN-01（正例：SST2）
- sample_id: `glue_sst2_train_0001`
- rule_id: `GEN-R1`

**Input**
- text: "a charming and often affecting journey."
- label_map: `0=negative, 1=positive`
- answer_candidate: `1`

**Expected**
- label: `SUPPORTED`
- final_answer: `1`
- evidence_span: `charming`, `affecting`

**Why**
- 情感倾向与 `positive` 映射一致。

### EX-GEN-02（反例：MRPC）
- sample_id: `glue_mrpc_train_0002`
- rule_id: `GEN-R2`

**Input**
- sentence1: "He denied all allegations in court."
- sentence2: "He admitted every allegation in court."
- label_map: `0=not_equivalent, 1=equivalent`
- answer_candidate: `1`

**Expected**
- label: `UNSUPPORTED`
- final_answer: `0`
- evidence_span: `denied` vs `admitted`

**Why**
- 关键谓词语义相反，不可判为等价。

### EX-GEN-03（边界：MNLI）
- sample_id: `glue_mnli_train_0003`
- rule_id: `GEN-R3`

**Input**
- premise: "Children are outdoors building a snowman."
- hypothesis: "Kids are outside in winter."
- label_map: `0=entailment, 1=neutral, 2=contradiction`
- answer_candidate: `0`

**Expected**
- label: `AMBIGUOUS`
- final_answer: `1`
- evidence_span: `building a snowman`
- ambiguity_note: `多数口径会给 neutral（文本未显式给出季节），但部分标注员可能据常识倾向 entailment。`

**Why**
- 该例主要用于强调“禁止常识外推”的边界。

---

## 5. 最小裁决说明（仅 MVP）

出现 `AMBIGUOUS` 时，最小记录如下：

- `sample_id`
- `task_type`
- `candidate_labels`
- `evidence_span`
- `ambiguity_note`
- `rule_id`

裁决输出仅需：

- 最终标签
- 一句规则依据
- 是否需要将该例沉淀为后续固定示例（是/否）

