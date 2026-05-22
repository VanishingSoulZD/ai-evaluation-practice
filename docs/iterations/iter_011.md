# Day 11 模块化封装

## 目标

- 学习 Python 模块化设计与面向对象编程（OOP）基本方法。
- 将 Day 9 / Day 10 的指标计算函数封装成可复用的类和模块。
- 提供清晰、统一的接口，便于后续批量评测或项目复用。

## 背景

Day 9 和 Day 10 的指标函数已经实现并验证过，可计算 ROUGE、BLEU、Accuracy、WinRate，并支持边界和异常输入检测。本次迭代目标是将这些函数组织成模块化类，使接口标准化、代码可读性增强、易于扩展。

## 任务拆解

### 1. 设计类结构

- **类名**：`TextMetrics` 或 `ClassificationMetrics`，可按功能拆分。
- **输入**：
  - 文本指标：reference 和 candidate 文本
  - 分类指标：y_true 和 y_pred 列表
  - 比赛指标：wins, losses, ties
- **方法**：
  - `compute_rouge(n: int) -> float`
  - `compute_rouge_l() -> float`
  - `compute_bleu(max_n: int) -> float`
  - `compute_accuracy() -> float`
  - `compute_win_rate(half_tie: bool = True) -> float`
  - `compute_all() -> dict[str, float]`（一次性计算所有指标）
- **输出**：
  - 指标值，统一返回 `dict[str, float]`，键为指标名，值为指标结果。
- **可选功能**：
  - 支持可选的外部库验证（NLTK / rouge-score）
  - 可处理空输入、异常参数

### 2. 编写类与模块化接口

- 将 Day 9 的函数改写为类方法或静态方法。
- 保留原函数可直接调用或通过类方法调用。
- 每个方法增加详细 docstring，说明输入、输出、异常抛出情况。
- 编写 `__init__` 方法统一接收输入数据。
- 提供 `compute_all()` 方法便于一次性输出所有指标。

### 3. 测试模块化类

- 准备小样本数据（可使用 Day 10 样本）。
- 调用类方法计算各指标。
- 对比手算目标，保证 `delta=0`。
- 测试边界输入与异常输入：
  - 空文本 / 空列表
  - n <= 0 的 ROUGE/ BLEU
  - len(y_true) != len(y_pred)
  - win_rate 中负数输入

### 4. 输出与验收

- 模块化类正确封装，接口清晰，易于调用：

```python
metrics = TextMetrics(reference="the cat is on the mat", candidate="the cat sat on the mat",
                      y_true=[1,0,1,1,0,0,1,0], y_pred=[1,1,1,1,0,0,0,0],
                      wins=6, losses=3, ties=1)
all_results = metrics.compute_all()
```

- 计算结果与手算目标一致。
- 异常输入和边界情况处理正确，不崩溃。
- docstring 和注释完整，类方法可复用。

## 参考资料

- Python 官方 OOP 教程: [https://docs.python.org/3/tutorial/classes.html](https://docs.python.org/3/tutorial/classes.html)
- Day 9 / Day 10 指标函数与验证脚本
- NLTK 文档（可选）: [https://www.nltk.org/](https://www.nltk.org/)
- rouge-score 库文档（可选）: [https://pypi.org/project/rouge-score/](https://pypi.org/project/rouge-score/)

## 验收标准

1. 指标计算函数成功封装成类和方法。
2. `compute_all()` 输出所有指标，与 Day 10 手算结果完全一致。
3. 边界输入和异常输入安全处理。
4. 类接口文档齐全，方法注释清楚。
5. 模块化代码可复用，便于后续扩展和批量计算。
