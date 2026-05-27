# Day 33：Label Studio 最小安装与启动说明

## 1. Label Studio 简介（简短）

Label Studio 是一个通用的数据标注工具，支持文本、图像、音频等多种任务类型。对本项目来说，先用它完成“安装 → 启动 → 登录 → 创建项目”的最小闭环即可，不涉及生产部署。

---

## 2. 使用 `uv` 的安装方式

> 前提：你本机已安装 `uv`（可用 `uv --version` 验证）。

在项目根目录执行：

```bash
# 进入仓库根目录
cd /workspace/ai-evaluation-practice

# 创建并使用本地虚拟环境（目录名为 .venv）
uv venv

# 在虚拟环境中安装 Label Studio
uv pip install label-studio
```

可选验证：

```bash
uv run label-studio --version
```

---

## 3. 启动命令

在项目根目录执行：

```bash
cd /workspace/ai-evaluation-practice
uv run label-studio start
```

如果你希望显式指定监听端口（例如 8080）：

```bash
cd /workspace/ai-evaluation-practice
uv run label-studio start --port 8080
```

---

## 4. 默认访问地址

服务启动后，默认在浏览器访问：

- `http://localhost:8080`

如果你通过 `--port` 指定了其他端口，请把地址中的 `8080` 替换为对应端口。

---

## 5. 首次创建账号流程

首次打开页面时，按界面引导完成初始化：

1. 进入 `http://localhost:8080`；
2. 点击 **Sign up**（或初始化注册入口）；
3. 输入邮箱、用户名和密码；
4. 提交后自动登录（或跳转登录页后再登录）；
5. 登录成功后可创建第一个标注项目。

> 说明：首次创建的账号通常就是当前本地实例的管理员账号。

---

## 6. 如何停止服务

在运行 `uv run label-studio start` 的终端窗口中：

- 按 `Ctrl + C` 即可停止服务。

如果是后台运行（不推荐本次最小流程使用），可通过进程管理方式结束对应进程。

---

## 7. 常见启动问题（至少 2 个）

### 问题 1：`uv: command not found`

**现象**：终端提示找不到 `uv`。  
**原因**：本机尚未安装 `uv`，或 PATH 未生效。  
**处理**：先安装 `uv` 并重新打开终端，再执行 `uv --version` 验证。

### 问题 2：端口被占用（例如 `Address already in use`）

**现象**：启动时报端口冲突。  
**原因**：`8080` 已被其他程序占用。  
**处理**：改用其他端口启动，例如：

```bash
uv run label-studio start --port 8081
```

然后访问 `http://localhost:8081`。

### 问题 3：依赖安装失败或网络超时

**现象**：`uv pip install label-studio` 失败。  
**原因**：网络不稳定，或 Python/构建环境异常。  
**处理**：

1. 先检查 Python 版本与 `uv` 是否可用；
2. 重新执行安装命令；
3. 必要时切换到网络更稳定的环境后重试。

---

## 8. 最小可复制命令清单

```bash
cd /workspace/ai-evaluation-practice
uv venv
uv pip install label-studio
uv run label-studio --version
uv run label-studio start
```

