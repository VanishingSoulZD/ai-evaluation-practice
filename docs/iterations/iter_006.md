# Iteration 006 - Day 6

## 任务概述

**任务名称**：Python 基础复习与数据处理优化  
**所属周**：Week 2 - 数据处理与分析能力提升  
**目标**：复习 Python 基础知识，掌握 Pandas/NumPy 核心操作函数，为后续复杂指标计算和数据分析打下基础。

## 背景/目的

- Python 是数据处理和分析的基础工具
- Pandas 和 NumPy 是高效数据操作的核心库
- 掌握数据操作函数可提高数据处理效率，为后续标注分析和统计指标计算做好准备

## 要解决的问题

- 熟悉 Python 基础语法和常用内置函数
- 掌握 Pandas 常用操作：`groupby`、`merge`、`apply`、数据筛选、排序
- 熟悉 NumPy 基本操作：数组创建、切片、运算和聚合
- 提高小数据集处理和分析能力，为后续指标计算提供支撑

## 参考资料

- Python 官方教程（https://docs.python.org/3/tutorial/）
- Pandas 官方教程（https://pandas.pydata.org/docs/getting_started/index.html）
- NumPy 官方教程（https://numpy.org/doc/stable/user/quickstart.html）
- Day 1–5 标注数据和分析脚本作为练习数据集

## 任务要求

- 复习 Python 基础函数及数据结构（列表、字典、集合、字符串操作）
- 掌握 Pandas DataFrame/Series 操作，包括：
  - 数据导入、筛选、排序
  - 分组统计 `groupby`
  - 数据合并 `merge` / `concat`
  - 行/列操作 `apply` / `map` / `applymap`
- 掌握 NumPy 数组操作，包括切片、广播、聚合函数
- 对小数据集进行处理练习，并生成统计结果

## 实现步骤

1. **Python 基础复习**
   - 回顾列表、字典、集合、字符串操作
   - 练习函数定义、条件语句和循环

2. **Pandas 数据处理练习**
   - 导入 Day 5 标注生成的 CSV/Excel 数据
   - 使用 `groupby` 对分类标签、实体标签进行统计
   - 使用 `merge` 合并不同表格或数据集
   - 使用 `apply`/`map` 对列进行批量计算或转换

3. **NumPy 操作练习**
   - 创建数组并进行基本运算
   - 切片、索引和条件筛选
   - 使用聚合函数（sum、mean、max、min 等）处理数据

4. **综合练习**
   - 对 Day 5 数据进行简单指标计算，例如：
     - 每类标签样本数量
     - 重复 ID 或重复文本数量
     - 分类标签和实体标签分布比例
   - 将处理结果输出为 DataFrame 或 CSV

## 验收标准

1. 熟练使用 Python 基础语法及数据结构
2. 能用 Pandas 完成数据导入、筛选、分组统计、合并及 apply 操作
3. 能用 NumPy 完成数组创建、切片、运算和聚合
4. 对小数据集进行完整处理并生成统计结果
5. 脚本或 Notebook 可复现，处理结果与数据一致
