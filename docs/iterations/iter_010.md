# Iteration 010 - Day 10：指标验证与优化

## 任务背景 / 目的

在前几天的练习中，我们完成了 ROUGE、BLEU、Accuracy、Win Rate 等指标的手工计算与 Python 函数实现（Day 8/Day 9）。  
本次任务旨在验证这些函数的正确性，发现潜在错误并进行优化，确保在小样本测试下，函数输出与手算结果完全一致。

---

## 解决的问题

- 检查指标函数实现的正确性
- 确保手算与函数计算一致
- 修正潜在 bug 或边界情况
- 为后续批量测试和自动化评测做好基础

---

## 参考资料

- Day 8 手工计算记录（`docs/iterations/iter_008.md`）
- Day 9 Python 实现（`scripts/day9_text_metrics.py`）
- Python 官方文档（`collections.Counter`、`math` 模块）
- NLTK / rouge-score 官方文档（可选，用于交叉验证）

---

## 任务要求

1. 使用 Day 9 的指标函数（ROUGE-1/2/L, BLEU-1/2, Accuracy, Win Rate）
2. 准备与 Day 8 手算例子相同的小样本数据
3. 验证函数输出与手算结果一致
4. 修复发现的错误或不一致
5. 记录调试过程及结论，确保函数计算结果 100% 正确

---

## 实现步骤

1. **准备测试数据**
   - 文本生成示例：
     - Reference：`the cat is on the mat`
     - Candidate：`the cat sat on the mat`
   - 分类示例：
     - y_true = [1, 0, 1, 1, 0, 0, 1, 0]
     - y_pred = [1, 1, 1, 1, 0, 0, 0, 0]
   - 对战示例：
     - wins = 6, losses = 3, ties = 1

2. **函数调用与结果比对**
   - 调用 `rouge_n()`, `rouge_l()`, `bleu()`, `accuracy()`, `win_rate()` 计算指标
   - 对比 Day 8 手工计算结果：
     - ROUGE-1 = 5/6
     - ROUGE-2 = 3/5
     - ROUGE-L = 5/6
     - BLEU-1 = 5/6
     - BLEU-2 = √(5/6 \* 3/5)
     - Accuracy = 6/8
     - WinRate(half tie) = (6 + 0.5)/10
     - WinRate(no tie credit) = 6/10

3. **调试与优化**
   - 检查函数在空字符串、短序列、n-gram 边界情况下的行为
   - 修复任何不一致或异常情况
   - 添加异常处理或输入验证（如 `max_n >= 1`, `len(y_true) == len(y_pred)`）

4. **可选交叉验证**
   - 使用 NLTK / rouge-score 库验证 Python 函数计算结果
   - 比较结果差异，确认自实现函数符合标准

5. **文档记录**
   - 记录手算 vs 函数输出对比表
   - 总结调试发现的问题及解决方法
   - 提供可复用的测试脚本模板

---

## 验收标准

1. 所有指标函数在小样本上计算结果与手算完全一致
2. 边界情况（空字符串、短文本、空列表等）处理正确
3. 函数无异常报错，输入验证完善
4. 调试过程和结论记录完整，可复用于后续迭代
5. 可选：交叉验证库输出与自实现函数一致（结果差异在可接受范围内）

---

## 输出成果

- Python 测试脚本（如 `scripts/day10_metric_validation.py`）
- 测试数据表 / 对比表
- 修正后的 Day 9 指标函数（如有优化）
- 文档总结，记录函数验证与优化过程
