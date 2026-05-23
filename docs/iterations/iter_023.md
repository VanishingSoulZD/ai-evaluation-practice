# Iteration 023 - Day 23

## Week 4：前沿方法 + 综合演练

### Day 23 - LLM评分实验

**背景 / 目的**  
在 Day 22 中，我们理解了 LLM-as-a-Judge（LaaJ）的概念和标准流程。Day 23 的目标是将理论落地，通过小规模实验验证 LLM 对文本的自动评分能力，掌握调用 GPT API 进行评分、收集和分析结果的完整流程。

**解决问题**

- 验证 LLM 对文本进行多维度评分的可行性
- 掌握 GPT API 的调用方式及结果解析
- 输出可分析的评分表格，为后续大规模实验打基础

**参考资料**

- OpenAI GPT API 文档：[OpenAI API](https://platform.openai.com/docs/api-reference)
- Day 22 LaaJ 流程文档：`docs/iterations/iter_022.md`
- Python requests / OpenAI SDK 使用示例
- 小规模文本样例集（可从 MT-Bench 或自定义样本中选取）

**任务要求**

1. 准备小规模文本样本集（至少 5-10 条样例）
2. 调用 GPT 模型对样例文本进行评分
3. 解析 GPT 返回结果，提取维度分数及总体评分
4. 保存评分结果到结构化表格（CSV / Excel / JSON）
5. 对评分结果进行简单分析（如均分、方差、异常值等）

**实现步骤**

1. **准备实验样本**
   - 收集 5-10 条示例文本，可以是问答、摘要、对话等
   - 为每条文本准备参考答案（可选，用于对比评分）

2. **调用 GPT API 进行评分**
   - 选择合适模型（如 GPT-4、GPT-3.5-turbo）
   - 构造评分 prompt，例如：

     ```
     请根据以下维度对回答进行评分（1-10）：
     1) 准确性 2) 完整性 3) 逻辑性 4) 可读性

     问题：{question}
     参考答案：{reference}
     被测答案：{prediction}

     请以 JSON 格式返回结果：
     {
       "accuracy": int,
       "completeness": int,
       "logic": int,
       "readability": int,
       "overall_score": float,
       "rationale": "..."
     }
     ```

   - 调用 API 获取评分结果

3. **解析和保存结果**
   - 将 GPT 返回 JSON 解析为 Python 字典
   - 保存至 CSV/Excel，字段包括 sample_id、维度分数、总体分数、评语

4. **简单分析**
   - 统计均分、方差
   - 检查评分分布，发现异常或极端分值
   - 输出可视化表格或简单报告

**验收标准**

- 所有示例文本均获得 GPT 评分结果
- 输出的评分表格格式正确，字段齐全
- 能分析评分结果并得出初步结论，例如均分、方差、异常案例
- 可用文档或口头方式复现实验流程
