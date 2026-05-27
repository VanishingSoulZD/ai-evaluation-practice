# Day 36 — Kappa Analysis Report (MVP)

## 1) Executive Summary

- **overall Cohen’s Kappa**: 当前数据尚未生成/不可用（`reports/day36_kappa_report.csv` 缺失）。
- **raw agreement**: 当前数据尚未生成/不可用（同上）。
- **当前一致性状态**: 目前只能给出结构化诊断框架，无法对一致性水平作数值判定。
- **是否适合进入下一阶段（benchmark/judge）**: **暂不建议**直接进入；需先补齐 Day36 结果文件并完成以下解释层检查。

> 结论（当前版本）：本报告提供“解释 Kappa”的分析框架与行动计划；待 CSV 产出后可在同结构内快速补全数值结论。

---

## 2) How to Read Kappa（如何解读）

- **Kappa ≠ raw agreement**。
  - raw agreement 只看“两个标注员表面一致了多少”。
  - Kappa 还会扣除“随机情况下本来也可能一致”的部分。
- **“超过随机的一致性”** 的意思是：
  - 如果某些标签特别常见，即使标注质量一般，也可能出现较高的 raw agreement。
  - Kappa 用来衡量“真正由稳定判断带来的额外一致性”，而不是类别分布造成的假象。

在本项目中，应避免“只看一致率就判断数据可用”的误判。

---

## 3) Overall Agreement

### 当前可用性

- `reports/day36_kappa_report.csv`: **当前数据尚未生成/不可用**。
- 因此以下关键指标暂无：
  - overall kappa
  - raw agreement
  - sample_count

### 指标解释层（待数值补齐后使用）

- **This metric means...**
  - overall kappa 代表全局“超越随机的一致性”。
  - raw agreement 代表全局“表面一致率”。
- **In our data it implies...**
  - 若 raw agreement 高但 kappa 一般：大概率存在标签分布偏斜或边界定义不清。
  - 若二者都低：优先排查 guideline 细则与标签边界冲突。

---

## 4) Task-level Analysis

### 当前可用性

- 目标数据源（通常位于 `reports/day36_kappa_report.csv` 中的 task-level 行）当前不可用。

### 分析框架（待补值）

应按 task_type 输出并解释：

| task_type | kappa | sample_count | interpretation |
|---|---:|---:|---|
| TBD | TBD | TBD | 最稳定/最不稳定及原因 |

### 必须回答的问题（不是只贴表）

1. 哪些 task 最稳定（高 kappa 且样本量足够）？
2. 哪些 task 最不稳定（低 kappa 且反复出现同类分歧）？
3. **为什么低**：
   - 规则边界不清？
   - 标签语义重叠？
   - 样本上下文缺失或天然歧义？

---

## 5) Label-level Analysis

### 当前可用性

- `reports/day36_label_disagreement_report.csv`: **当前数据尚未生成/不可用**。

### 分析框架（待补值）

建议输出（按 disagreement_rate 降序）：

| label | disagree_count | disagreement_rate | support_ratio | interpretation |
|---|---:|---:|---:|---|
| TBD | TBD | TBD | TBD | 高频冲突/小样本谨慎解释 |

### 解释重点

- **高频标签**：优先看它们的分歧是否集中在固定边界。
- **小样本标签**：即使 disagreement_rate 很高，也需标注“统计不稳定，避免过度解读”。
- **易混淆标签对**：若 A/B 互相替代频繁，优先怀疑 label boundary 设计问题。

---

## 6) Root-cause Diagnosis（核心）

> 本节用于明确区分问题来源，避免把所有问题归因为“标注员不行”。

### A. Guideline 问题

- **现象**：同类样本在边界场景下反复分歧；标注说明无法唯一决策。
- **为何会拉低 Kappa**：同一证据被不同规则理解，导致系统性不一致。
- **推荐动作**：
  1. 把高分歧 case 写进 guideline 的“正反例”与“优先级规则”。
  2. 增加“冲突决策顺序”（先判 X，再判 Y）。
  3. 小批量复标验证修订前后差异。

### B. Label Boundary 问题

- **现象**：两个标签长期互相替代，且并非偶发。
- **为何会拉低 Kappa**：标签语义重叠导致决策面不互斥。
- **推荐动作**：
  1. 重写标签定义为“必要条件 + 排除条件”。
  2. 对高混淆标签对增加“最小区分特征”清单。
  3. 必要时合并标签或拆分为更可判定层级。

### C. Sample Ambiguity 问题

- **现象**：分歧集中在少量上下文缺失/表述含混样本。
- **为何会拉低 Kappa**：样本信息不足，合理分歧变多。
- **推荐动作**：
  1. 标记 ambiguity 样本并从主评估集隔离。
  2. 为样本补上下文字段（若流程允许）。
  3. 维护 hard-case 列表，单独跟踪其一致性。

---

## 7) Risk Assessment

1. **小样本风险**：某 task/label 样本过少时，kappa 与分歧率波动大。
2. **标签不平衡风险**：可能出现“raw agreement 看起来高，但 kappa 不高”。
3. **boundary case 风险**：边界样本比例高会持续拖低一致性上限。
4. **解释偏差风险**：若不做 root-cause 分层，容易把 guideline/label 问题误判为 annotator 问题。

---

## 8) Action Plan

| priority | issue | recommendation |
|---|---|---|
| P0 | Day36 结果 CSV 缺失，无法形成数值结论 | 先生成/补齐 `reports/day36_kappa_report.csv` 与 `reports/day36_label_disagreement_report.csv`，并按本模板补全数值段落。 |
| P0 | 无法定位最危险 task/label | 产出 task-level 排名与 label-level 分歧 Top 列表，逐条写明“为什么低”。 |
| P1 | guideline 边界不清导致重复分歧 | 在 guideline 中新增高分歧反例与决策顺序，随后做小批复标验证。 |
| P1 | label 语义重叠 | 对高混淆标签对重写定义（必要/排除条件），必要时合并或分层。 |
| P2 | ambiguity 样本污染主评估结论 | 建立 hard-case 子集并单独报告，不与主集平均值混写。 |

---

## 9) Conclusion

- **当前数据可靠性判断**：由于 Day36 核心 CSV 当前不可用，现阶段仅能给出解释框架，不能给出可靠的数值结论。
- **是否适合进入 benchmark/judge**：**暂不适合**直接进入；应先补齐并验证 Kappa 结果。
- **下一轮重点优化方向**：
  1. 先补数据：完成 overall/task/label 数值闭环；
  2. 再做解释：按 guideline / label / sample 三类给出证据化归因；
  3. 再定门槛：基于实际分布设定下一轮一致性目标。

建议下一轮目标（待拿到当前基线后最终确认）：
- overall kappa：提升到“中等及以上一致性”区间并稳定；
- 最危险 task：针对最低 kappa task 做专项修订，目标是显著高于本轮基线。

---

## 报告完整性自检

- [x] Markdown 可正常阅读
- [x] 非纯数字 dump（包含解释层）
- [x] guideline / label / sample 已明确区分
- [x] recommendation 为可执行动作
- [x] 未修改无关文件
