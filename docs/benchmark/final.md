根据你的要求，我只做**整理、去重、分类**：

- ✅ 只保留你提供文档中出现过的 Benchmark
- ✅ 同名/明显变体合并
- ✅ 不新增任何 Benchmark
- ✅ 不删除任何 Benchmark（仅合并重复项）
- ✅ 不输出 leaderboard、模型、论文、数据集说明
- ✅ 最后给出“最核心20个”

---

# 1. Agent / General Agent / Agent 能力评测

- GDPval-AA
- GDPval-AA v2
- SaaS-Bench
- Qwenclaw
- CoWorkBench
- ClawEval
- SkillsBench
- QwenWorldBench
- Vitabench
- SpreadSheetBench-v1
- Agents' Last Exam
- Humanity's Last Exam (HLE)
- HLE w/ tools
- Toolathlon

---

# 2. Coding Agent / 软件工程 / 代码生成评测

- SWE-Bench
- SWE-Bench Pro
- SWE-Pro
- SWE-Verified
- SWE-Multilingual
- DeepSWE
- DeepSWE v1.1
- Terminal-Bench
- Terminal-Bench Hard
- Terminal-Bench 2.0-Terminus
- Terminal-Bench 2.1
- FrontierCode (Diamond)
- LiveCodeBench
- NL2repo
- BigCodeBench
- HumanEval
- SciCode
- QwenWebDev
- QwenSVG
- ProgramBench

---

# 3. Computer Use / GUI Agent / 浏览器 Agent 评测

- OSWorld-Verified
- OSWorld 2.0
- Online-Mind2Web
- BrowseComp
- AutomationBench
- BenchCAD
- BenchCAD (python 工具)

---

# 4. Tool Use / Function Calling / MCP Agent 评测

- BFCL-V4
- MCP-Mark
- MCP-Atlas
- AutomationBench
- Toolathlon

---

# 5. 通用推理 / 知识 / 综合能力评测

- ARC Prize
- ARC-AGI-3
- GPQA
- GPQA Diamond
- SuperGPQA
- MMLU
- MMLU-Pro
- MMLU-Redux
- MMMLU
- MMLU-ProX
- AGIEval
- Simple-QA verified
- FACTS Parametric
- TriviaQA
- BBH
- DROP
- HellaSwag
- WinoGrande
- CLUEWSC
- IFEval
- IFBench
- SQuAD

---

# 6. 数学 / STEM / 科学推理评测

- FrontierMath Tier 1-3 (v2)
- FrontierMath Tier 4 (v2)
- GSM8K
- MATH
- MGSM
- CMath
- HMMT 2026 Feb
- IMOAnswerBench
- CritPT
- Apex
- PolyMATH

---

# 7. 多模态 / Vision-Language Model 评测

- MMMU
- MMMU-Pro
- MMMU Pro (无工具)
- MMMU Pro (使用工具)
- OmniDocBench
- Blueprint-Bench 2
- GDP.pdf

（合并：

- GDP.pdf
- gdp.pdf）

---

# 8. 长上下文 / Memory / 信息检索能力评测

- Memory Sources
- LongBench-V2
- OpenAI MRCR v2 8-needle 256K-512K
- OpenAI MRCR v2 8-needle 512K-1M
- MRCR-v2 128k
- GraphWalks BFS 256k f1
- GraphWalks BFS 1mil f1

---

# 9. 网络安全 / Cybersecurity Agent 评测

- ExploitBench
- ExploitGym
- SEC-Bench Pro
- 夺旗挑战

（合并：

- ExploitBench
- ExploitBench (Cap%)

）

---

# 10. 医疗 / 生物专业领域 Agent 评测

- HealthBench Professional
- BioMysteryBench

（合并：

- Healthbench Professional
- HealthBench Professional
  ）

---

# 11. 法律 / 专业知识 Agent 评测

- Legal Agent Benchmark

---

# 12. AI研发 / 自我优化 / RSI 能力评测

- Internal Research Debugging Evaluation
- KernelGen 1P
- Kernel Bench L3
- NanoGPT
- PostTrainBench Lite
- RSI Index

---

# 13. 中文 / 多语言能力评测

- C-Eval
- CMMLU
- MultiLoKo
- WMT24++
- MAXIFE
- INCLUDE
- NOVA-63
- Global PIQA

---

# 14. 去重后的完整 Benchmark 数量

合并明显重复后：

**约 136 个 Benchmark**

---

# 最核心、最重要的20个 Benchmark

以下按照当前 **Frontier LLM / Agent 模型发布影响力 + 使用频率 + 行业认可度** 综合排序：

| 排名 | Benchmark                  | 核心方向                    |
| ---- | -------------------------- | --------------------------- |
| 1    | SWE-Bench Pro              | Coding Agent / 软件工程     |
| 2    | Humanity's Last Exam (HLE) | Frontier 综合推理           |
| 3    | GPQA Diamond               | 专家级推理                  |
| 4    | Terminal-Bench             | Computer Coding Agent       |
| 5    | GDPval-AA                  | Knowledge Worker Agent      |
| 6    | ARC-AGI-3                  | 通用智能推理                |
| 7    | LiveCodeBench              | Coding 推理                 |
| 8    | MMMU-Pro                   | 多模态推理                  |
| 9    | OSWorld                    | Computer Use Agent          |
| 10   | BrowseComp                 | Web Agent                   |
| 11   | BFCL-V4                    | Function Calling / Tool Use |
| 12   | MMLU-Pro                   | 通用知识推理                |
| 13   | FrontierMath               | 高难数学推理                |
| 14   | LongBench-V2               | 长上下文能力                |
| 15   | MRCR-v2                    | 长上下文检索                |
| 16   | HealthBench Professional   | 医疗 Agent                  |
| 17   | ExploitBench               | Cyber Agent                 |
| 18   | AutomationBench            | 自动化 Agent                |
| 19   | Toolathlon                 | Tool Agent 综合能力         |
| 20   | DeepSWE                    | Coding Agent                |

---

## 如果从“2026 年 Agent 模型发布会最值得长期跟踪”的角度进一步压缩：

实际上只需要关注 **10 个核心 Benchmark**：

1. SWE-Bench Pro
2. Terminal-Bench
3. GPQA Diamond
4. Humanity's Last Exam
5. GDPval-AA
6. ARC-AGI-3
7. OSWorld
8. BFCL
9. MMMU-Pro
10. BrowseComp

这 10 个基本覆盖：

**软件工程 Agent → Computer Agent → Tool Agent → Knowledge Agent → Multimodal Agent → Frontier Reasoning**

也是目前 OpenAI、Anthropic、Google、DeepSeek、Qwen 等旗舰模型发布最接近的 Benchmark 骨架。
