# Day 10 指标验证与优化记录

## 验证范围
- ROUGE-1 / ROUGE-2 / ROUGE-L
- BLEU-1 / BLEU-2
- Accuracy
- Win Rate（half tie / no tie credit）

## 样本数据
- Reference: `the cat is on the mat`
- Candidate: `the cat sat on the mat`
- `y_true = [1, 0, 1, 1, 0, 0, 1, 0]`
- `y_pred = [1, 1, 1, 1, 0, 0, 0, 0]`
- `wins=6, losses=3, ties=1`

## 手算目标
- ROUGE-1 = `5/6`
- ROUGE-2 = `3/5`
- ROUGE-L = `5/6`
- BLEU-1 = `5/6`
- BLEU-2 = `sqrt(5/6 * 3/5)`
- Accuracy = `6/8`
- WinRate(half tie) = `(6 + 0.5)/10`
- WinRate(no tie credit) = `6/10`

## 验证结果
使用 `scripts/day10_metric_validation.py` 运行后，所有主样本指标 `delta=0`（浮点误差阈值 `1e-12` 下全通过）。

## 边界与异常输入检查
- 空字符串 / 空列表输入返回 `0.0`，无崩溃。
- `n<=0` 的 ROUGE / BLEU 输入抛出 `ValueError`。
- `len(y_true) != len(y_pred)` 抛出 `ValueError`。
- 对 `win_rate` 增加非负校验：当 `wins/losses/ties` 任意为负数时抛出 `ValueError`。

## 结论
Day 9 指标函数在目标小样本上的计算与手算完全一致；边界输入和输入合法性检查已补强，可用于后续批量评测与迭代。
