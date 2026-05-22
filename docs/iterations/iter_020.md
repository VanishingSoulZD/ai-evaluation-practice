# Iteration 020 – Day 20: 接口+异步综合练习

## 目标

整合 Week2 的指标计算模块与 Week3 的异步任务系统，实现从 CSV 上传到异步计算再到报告生成的完整流程。

## 背景/目的

在前几天的练习中，我们分别实现了：

- CSV 文件上传接口（Day 16）
- 批量指标计算接口（Day 17）
- 异步任务处理（Day 18）
- 异步报告生成（Day 19）

Day 20 目标是将这些模块组合成一个完整的端到端流程，实现自动化处理和报告输出。

## 解决问题

- 将同步和异步模块结合，形成可复用、可调用的端到端流程
- 保证文件上传、异步计算、报告生成、状态查询流程顺畅
- 处理可能的异常和任务失败，确保系统健壮性

## 参考资料

- FastAPI 官方文档: https://fastapi.tiangolo.com/
- Celery 官方文档: https://docs.celeryq.dev/
- pandas 文档: https://pandas.pydata.org/docs/
- matplotlib & seaborn 文档
- 前几天迭代文档: iter_016.md ~ iter_019.md

## 任务要求

1. 编写整合 API 接口：
   - 上传 CSV → 异步计算指标 → 异步生成报告
2. 提供任务状态查询接口：
   - 可查看异步计算和报告生成进度
   - 可返回最终报告文件路径（CSV +图表）
3. 测试整个流程：
   - 上传 CSV 文件
   - 调用异步任务
   - 等待完成后获取报告
4. 输出报告：
   - CSV 指标文件
   - 图表文件（可视化指标分布）

## 实现步骤

1. **环境与依赖**
   - 确保 `fastapi`, `uvicorn`, `pandas`, `celery`, `redis`, `matplotlib`, `seaborn` 已安装
   - 创建上传目录和报告目录（`UPLOAD_DIR`, `REPORT_DIR`）

2. **整合 API 编写**
   - 在 `main.py` 中新增 `/process-csv-async` POST 接口
   - 上传 CSV 文件后生成唯一文件名并保存
   - 调用 Celery 任务 `compute_metrics_and_report` 处理文件
   - 返回任务 ID 给客户端

3. **任务状态查询**
   - 新增 `/process-tasks/{task_id}` GET 接口
   - 使用 `compute_metrics_and_report.AsyncResult(task_id)` 查询任务状态
   - 返回 JSON，包含：
     - task_id
     - status
     - 成功时的 report 路径（CSV + 图表）
     - 失败时的错误信息

4. **异步任务封装**
   - 任务文件 `tasks.py` 已有 `compute_metrics_and_report`
   - 确保任务可以接收文件路径，返回 `{ "csv": path, "chart": path }`
   - 异常捕获返回错误信息

5. **测试流程**
   - 上传示例 CSV
   - 调用 `/process-csv-async`
   - 使用 `/process-tasks/{task_id}` 查询任务状态
   - 确认 CSV 指标文件和图表文件生成
   - 验证结果正确性

6. **文档和注释**
   - 接口、任务、函数注释必须详细
   - 所有路径、文件名生成策略明确，避免冲突
   - 确保异步任务失败不会阻塞服务

## 验收标准

- 上传 CSV 成功返回任务 ID
- 异步计算指标任务完成，生成 CSV + 图表文件
- 查询任务状态接口返回正确状态和文件路径
- 整个流程自动化，无人工干预即可完成
- 异常处理完善，任何错误都能被捕获并返回
