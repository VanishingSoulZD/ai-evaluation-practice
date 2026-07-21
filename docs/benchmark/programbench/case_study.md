# ProgramBench Case Studies

数据口径：仅使用 ProgramBench 官方任务名、ProgramBench 论文/官网说明，以及 GitHub API/官方仓库可复现脚本可采集字段；当前执行环境无法直连 GitHub API 时，未知字段保留为 `unknown`，不做推断。

## 1. abishekvashok/cmatrix

- **ProgramBench task**: `abishekvashok__cmatrix.5c082c6`
- **Repository**: <https://github.com/abishekvashok/cmatrix>
- **简介**: cmatrix 是一个终端动画程序，复现类似电影 _The Matrix_ 的字符雨效果。
- **代码规模**: `programbench_tasks.csv` 中 `loc=unknown`；脚本未将 GitHub language API 的字节数伪装为 LOC。
- **核心功能**:
  - 终端屏幕控制与刷新。
  - 字符流随机生成、颜色/属性渲染。
  - 命令行参数影响滚动速度、颜色、异步滚动、粗体等显示行为。
- **为什么 ProgramBench 难**:
  - 行为主要是 TTY/terminal side effects，正确性不只是 stdout 文本匹配。
  - curses/terminfo、ANSI 控制序列、窗口尺寸和刷新时序会影响可观察输出。
  - Agent 只能看到二进制与文档，需要从黑盒行为中恢复选项组合、默认参数和边界情况。

## 2. FFmpeg/FFmpeg

- **ProgramBench task**: `ffmpeg__ffmpeg.360a402`
- **Repository**: <https://github.com/FFmpeg/FFmpeg>
- **简介**: FFmpeg 是多媒体处理工具链，覆盖音视频转码、封装/解封装、过滤、探测与流处理等场景。
- **代码规模**: `programbench_tasks.csv` 中 `loc=unknown`；源仓库非常大，但本项目不在离线环境中编造精确 LOC。
- **核心功能**:
  - `ffmpeg` 命令处理音视频输入、转码、过滤并输出到多种容器/编码格式。
  - `ffprobe`/相关组件提供媒体信息探测。
  - 大量 codec、format、filter、protocol 组合构成复杂行为面。
- **为什么 ProgramBench 难**:
  - 行为面极大：CLI 参数解析、容器格式、编解码器、时间戳、metadata、错误处理都可能被测试覆盖。
  - 需要复现二进制的外部行为，而不是实现一个小函数；架构、模块边界和兼容性全部由 Agent 自主决定。
  - 即使测试是有限行为测试，FFmpeg 的输入空间和格式组合也使“几乎正确”的实现很容易在边界样例失败。
