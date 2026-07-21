# mini-SWE-agent Evaluation Pipeline for ProgramBench

数据来源：ProgramBench 官网/论文说明与 `SWE-agent/mini-swe-agent` 官方仓库说明。ProgramBench extended leaderboard 明确标注结果使用 `mini-SWE-agent`、200 tasks，并给出更新时间；mini-SWE-agent README 描述其 minimal agent、bash-only tool use、linear history、`subprocess.run` action execution，以及 Docker/Podman 等环境支持。

## Agent loop

1. 输入任务 prompt：ProgramBench 给 agent 一个已编译 reference program 与文档，要求从零实现源码和构建脚本。
2. 模型生成下一步 shell action。
3. mini-SWE-agent 执行动作并把输出追加到线性消息历史。
4. 循环：模型读取历史、继续编辑/构建/自测，直到达到步数/预算/提交条件。
5. 产物通常是候选源码与 build script，然后交给 ProgramBench evaluator。

## Docker environment

- ProgramBench 论文说明任务构造与评测在 Docker container 中运行。
- 对正式任务 worker，环境不提供互联网；这避免直接下载原项目或搜索答案。
- mini-SWE-agent 官方 README 说明它支持 local、docker/podman、singularity/apptainer 等环境；在 sandbox 中执行 action 可替换为 `docker exec` 风格。

## Tool usage

- mini-SWE-agent 的核心设计是只给 agent bash，不依赖复杂 tool-calling interface。
- 文件查看、编辑、编译、运行测试、调试都通过 shell 命令完成。
- 每个 action 独立执行；历史是线性的，便于复盘轨迹与成本统计。

## Test execution

1. ProgramBench 对候选解运行隐藏 behavioral tests。
2. 测试比较候选 executable 与 gold executable 的外部可观察行为，例如 stdout/stderr、exit code、文件系统副作用等。
3. leaderboard 的主要统计包括 fully resolved、almost resolved（官网说明为通过 ≥95% behavioral tests 的实例）和平均 API cost。
4. 官方文档提醒部分不确定或有缺陷的 tests/branches 会被忽略；复现应使用 `programbench eval` 或同等官方评分逻辑。
