# Flow-Factory 奖励系统与内置/扩展奖励模型全景技术文档

本手册系统地总结和介绍了 **Flow-Factory**（面向生成式扩散模型与流匹配的强化学习微调框架）中内置支持及推荐扩展的核心奖励模型（Reward Models）。这些模型充当了强化学习对齐（如 GRPO、PPO、ReMax 算法）中的“人类意图裁判”，指导生成模型在画面质量、指令遵循和逻辑合理性上不断进化。

---

## 🧭 奖励模型矩阵概览

| 奖励模型名称              | 提出机构 & 时间               | 模型类型             | 核心评判维度                   | 核心架构底座                   |
| ------------------------- | ----------------------------- | -------------------- | ------------------------------ | ------------------------------ |
| **CLIP**                  | OpenAI (2021)                 | Pointwise (绝对得分) | 宏观图文相关性                 | 双塔 Transformer/ViT 架构      |
| **PickScore**             | 特拉维夫大学等 (2023)         | Pointwise (绝对得分) | 人类综合审美、画面完成度       | OpenCLIP-ViT-H-14              |
| **PickScore_Rank**        | Flow-Factory 团队 (2025/2026) | Groupwise (组内相对) | 消除 Prompt 难度偏差的相对优势 | 内置 PickScore + 排序算子      |
| **vllm_evaluate**         | Flow-Factory 团队 (2025/2026) | Pointwise (绝对得分) | 基础逻辑、数量、空间方位       | 远程大 VLM (如 Qwen2-VL)       |
| **rational_rewards_t2i**  | 滑铁卢大学 TIGER Lab (2026)   | Pointwise (具理裁判) | 复杂属性绑定、长文本对齐       | RationalRewards-8B-T2I         |
| **rational_rewards_edit** | 滑铁卢大学 TIGER Lab (2026)   | Pointwise (具理裁判) | 指令编辑、背景非编辑区保持     | RationalRewards-8B-Edit        |
| **OCR 奖励机制**          | Flow-Factory 扩展集成         | Pointwise (硬匹配)   | 文字拼写、印刷排版准确性       | 检测(DBNet) + 识别(CRNN/TrOCR) |
| **GenEval**               | 华盛顿大学/MIT (2023)         | Pointwise (多维硬验) | 组合性生成、多物体及颜色绑定   | 开集检测器 + 属性分类器管线    |

---

## 🔍 奖励模型详解

### 1. CLIP (Contrastive Language-Image Pre-training)

- **提出机构与时间**：OpenAI，2021 年 1 月。
- **能力与解决的问题**：评估图像与文本之间的宏观跨模态语义匹配度。在扩散模型微调的早期，主要用来解决生成图像“货不对板”、彻底偏离 Prompt 核心词（图文不相关）的痛点。
- **核心架构**：
- **主干（Backbone）**：典型的双塔结构。文本端使用 Transformer 编码器，图像端使用 ViT 或 ResNet 编码器。
- **Head**：无复杂的回归 Head。最终的特征向量经过 $L_2$ 归一化后，直接计算图像向量与文本向量的点积（余弦相似度），再乘以一个可学习的温度标量。

- **输入与输出**：
- **输入**：提示词文本（`prompt: List[str]`）和生成的图像（`image: List[Image]`）。
- **输出**：Pointwise 标量分数（余弦相似度，通常在 0.1 ~ 0.4 之间）。

- **为什么有效**：在数以亿计的互联网图文对上进行了超大规模的对比学习（Contrastive Learning）预训练，构建了极其鲁棒的图文共同嵌入空间，能够提供粗粒度对齐的基本梯度。
- **适用场景与细分维度**：
- **任务类型**：Text-to-Image (T2I)、Text-to-Video (T2V) 任务的基础对齐微调。
- **细分维度**：**指令遵循 - 宏观语义相关性**。对微观的空间方位（如“在...左边”）、物体数量、复杂的反义词及多重否定极不敏感。

---

### 2. PickScore

- **提出机构与时间**：特拉维夫大学等开源社区研究团队（Yuval Kirstain 等），2023 年 5 月。
- **能力与解决的问题**：准确预测真实人类对生成图像的**主观偏好与审美标准**。解决了传统 CLIP 只注重语义匹配、无法分辨图像“美丑”、“肢体崩坏程度”以及“视觉噪点”的局限。
- **核心架构**：
- **主干（Backbone）**：基于强大的开源多模态底座 OpenCLIP-ViT-H-14。
- **Head**：在计算图文内积后，接入一个 Pairwise（两手对比）交叉熵损失头进行偏好预测训练。在独立运行时，通过单向激活直接输出该图像对文本的绝对偏好概率映射。

- **输入与输出**：
- **输入**：提示词文本（`prompt`）和生成的图像（`image`）。
- **输出**：Pointwise 绝对偏好标量得分。

- **为什么有效**：模型在当时全球最大的真实人类交互偏好数据集 _Pick-a-Pic_（包含超过 50 万条真实人类对同一 Prompt 生成的多张图进行投票的记录）上进行了专项微调，使其深刻理解了人类的“审美共识”。
- **适用场景与细分维度**：
- **任务类型**：Text-to-Image (T2I) 的画质飞跃与全方位偏好对齐。
- **细分维度**：**合理性 - 审美合理性、画面完成度、视觉无瑕疵、人类偏好综合对齐**。

---

### 3. PickScore_Rank

- **提出机构与时间**：由 Flow-Factory 团队于 2025/2026 年基于 PickScore 原生算法封装封装。
- **能力与解决的问题**：解决强化学习（特别是 GRPO、PPO 等算法）在文生图微调中，由于不同 Prompt 的“天生难度不同”，导致绝对分数（Pointwise）在批次间剧烈波动、引发训练不稳定的问题。
- **核心架构**：
- **主干（Backbone）**：内置并共享 PickScore 的神经网络。
- **Head**：**Groupwise 排序算子**。在 Flow-Factory 内部，它会对同一个 Prompt 采样生成的多个样本（Group）分别计算 PickScore 绝对得分，然后使用 `argsort` 算子在组内计算相对排名。

- **输入与输出**：
- **输入**：同一个提示词对应的**一组**生成图像列表（数量等于 `group_size`）。
- **输出**：组内各个样本的相对排名得分（Groupwise 奖励，通常归一化到 `[0, 1]` 之间）。

- **为什么有效**：通过将绝对值转化为相对序分值（Ranking-based reward），天然提供了均值和方差稳定的奖励分布。不论 Prompt 难度多高、绝对分多低，组内最好的样本永远获得高奖励，最差的永远获得最低奖励，消除了优势估计（Advantage Estimation）的系统偏差。
- **适用场景与细分维度**：
- **任务类型**：配合 GRPO 或 DGPO 等基于组内对比的 Text-to-Image 强化学习训练。
- **细分维度**：**组内相对优势（Relative Preference Matching）**，能有效防止生成模型寻找奖励漏洞（Reward Hacking）。

---

### 4. vllm_evaluate

- **提出机构与时间**：Flow-Factory 框架自身开发，2025-2026 年。
- **能力与解决的问题**：利用前沿多模态大模型（VLM）的常识与视觉逻辑能力进行灵活的规则判别。解决了轻量判别模型（CLIP）无法理解复杂、长尾、或含有空间逻辑指令的问题。
- **核心架构**：
- **主干（Backbone）**：远程托管在 vLLM 服务上的前沿大视觉语言模型（如 Qwen2-VL / Qwen3-VL）。
- **Head**：**Token Logprobs（对数概率）提取 Head**。该机制不让 VLM 生成长篇大论，而是设计一个精简的“Yes/No”单字回答 Prompt，在 vLLM 返回的 completions 结果中直接读取 “Yes” 或 “No” 对应 Token 的对数概率，并转化为平滑的连续标量。

- **输入与输出**：
- **输入**：生成的图像，以及自定义的简短二分类裁判提示词（例如：“图中是否正好有三只猫？回答 Yes 或 No”）。
- **输出**：根据 “Yes” 的概率计算出的平滑标量奖励值。

- **为什么有效**：利用了百亿参数量级 VLM 的超强视觉感知与常识推理能力，同时用 Logprobs 避开了文本解析失败的风险，提供了高质且具备梯度的平滑信号。
- **适用场景与细分维度**：
- **任务类型**：Text-to-Image (T2I)、Image-to-Image (I2I) 的细粒度条件约束。
- **细分维度**：**指令遵循 - 空间方位关系（如左/右/上/下）、数量计数、基础目标存在性检验**。

---

### 5. rational_rewards_t2i (Rational Rewards T2I)

- **提出机构与时间**：滑铁卢大学 TIGER Lab（文航教授团队），2026 年 4 月（源于最新论文 _RationalRewards_）。
- **能力与解决的问题**：**攻克了传统标量奖励模型面临的“奖励黑客（Reward Hacking）”致命缺陷**（即生成器通过生成某些取巧的局部特征骗取高分，但实际画质在倒退）。该模型要求 VLM **在打分前必须生成显式的、多维度的推理批判（Critique）**。
- **核心架构**：
- **主干（Backbone）**：采用 `RationalRewards-8B-T2I` 模型底座（通过其特有的 PARROT 框架进行偏好锚定合理化训练）。
- **Head**：自回归文本生成头。它依据长文量规（Rubric）输出结构化的、包含思维链（CoT）的批判文本，最后由 Flow-Factory 解析器将文本内的多维度得分聚合为标量。

- **输入与输出**：
- **输入**：生成的图像、原始 T2I 提示词（Prompt）以及详细的评估指标量规（Rubric）。
- **输出**：结构化的多维度分析评语与细分维度得分（聚合后作为最终的 Pointwise 奖励）。

- **为什么有效**：

1. **隐式正则化约束**：模型打高分的前提是必须在自回归文本中生成符合逻辑、有理有据的批判理由， unsupported（无证据）的高分通不过语言模型的自校准。
2. **PARROT 框架**：在偏好数据上实现了低方差校准，克服了普通 VLM 裁判随机构造评分、方差过大的 RL 微调灾难。

- **适用场景与细分维度**：
- **任务类型**：前沿 Text-to-Image (T2I) 高级强化学习微调（如 FLUX.1、SD3.5、Wan2.1 的 GRPO 微调）。
- **细分维度**：**合理性 - 逻辑合理性、指令遵循 - 属性绑定（Attribute Binding，如红衣服绿帽子）、复杂场景长文本对齐**。

---

### 6. rational_rewards_edit (Rational Rewards Edit)

- **提出机构与时间**：滑铁卢大学 TIGER Lab，2026 年 4 月。
- **能力与解决的问题**：专门针对图像编辑（Image Editing）与图生图（Image-to-Image）任务。传统的 T2I 奖励模型无法同时接收原图和修改图，导致无法评估“原图非编辑区域的保持度（Preservation）”与“编辑区域的修改准确度（Modification）”之间的微妙平衡。
- **核心架构**：
- **主干（Backbone）**：支持双图/多图输入（Multi-Image Session）的视觉语言大模型（如 `RationalRewards-8B-Edit`）。
- **Head**：自回归的多维度批判与打分头。

- **输入与输出**：
- **输入**：**原始图（Source Image）**、**编辑后的图（Edited Image）**、编辑指令（Instruction）以及编辑评估量规。
- **输出**：包含“背景一致性保持”和“修改指令执行度”的结构化理性批判及聚合标量分。

- **为什么有效**：其训练数据和量规深度耦合了编辑任务的双重核心指标（不要把没叫你改的地方也改掉，叫你改的地方必须改到位），能指导扩散模型或流匹配模型在保持原图主体特征（如人脸、背景、构图）的同时，进行精准局部替换。
- **适用场景与细分维度**：
- **任务类型**：Image-to-Image (I2I), 指令驱动的图像编辑（Instruction-Guided Image Editing）。
- **细分维度**：**指令遵循 - 编辑准确性、画面一致性 - 背景/特征保持度（Consistency & Preservation）**。

---

### 7. OCR 奖励机制 (Optical Character Recognition)

- **提出机构与时间**：Flow-Factory 扩展支持的外部/开源 OCR 专家模型（如百度 PaddleOCR 团队系列，或微软 TrOCR）。
- **能力与解决的问题**：解决文生图模型在生成带有文字的图像时，经常出现“乱码、拼写错误、笔画变形、漏字”等**文字渲染灾难**。
- **核心架构**：
- **主干（Backbone）**：专业的文本检测模型（如 DBNet）+ 文本识别模型（如 CRNN 或 ViT-based 序列编码器）。
- **Head**：CTC 解码头或 Attention 文本生成头。在 Flow-Factory 端，将提取到的字符串与 Prompt 中期望渲染的真实字符计算编辑距离（Levenshtein Distance）或相似度。

- **输入与输出**：
- **输入**：生成的图像。
- **输出**：提取出的所有文本字符串列表（经计算后映射为代表文本正确性的标量 Reward）。

- **为什么有效**：文字作为拓扑结构特殊的视觉信号，其容错率极低。扩散模型很容易在像素层面模糊带过，而专门的 OCR 模型能够对字符实现硬匹配检验，给策略网络最直接、“无法通过视觉技巧蒙混过关”的硬惩罚。
- **适用场景与细分维度**：
- **任务类型**：Text-to-Image 中的文字海报生成、电商图设计、书写与标牌生成任务。
- **细分维度**：**指令遵循 - 文字准确性（Text Rendering Accuracy）**。

---

### 8. GenEval

- **提出机构与时间**：华盛顿大学、MIT 等开源团队（Dhruba Ghosh 等），2023 年 10 月提出。在 Flow-Factory 中被用作针对组合性（Compositional）生成的自动化硬核判定奖励。
- **能力与解决的问题**：解决大模型在生成包含多个物体、复杂属性绑定的组合提示词时的能力缺失（例如：“一个红色的气球在两只小狗之间”）。
- **核心架构**：
- **主干（Backbone）**：是一个**多模型联合管线（Pipeline）**。通常集成了一个开集目标检测模型（如 Grounding DINO 或 FC-CLIP）和一个专门的属性/颜色分类器。
- **Head**：检测器的 Bounding Box（边界框）输出和分类器的概率输出。Flow-Factory 调用其评估逻辑，将其与经过程序化（Parsing）拆解后的原始 Prompt 目标原子属性进行精确硬校验。

- **输入与输出**：
- **输入**：生成的图像，以及通过规则拆解后的物体-属性依赖树。
- **输出**：覆盖单一物体、双物体、物体计数、颜色绑定、位置关系等多个维度的硬对准率（0 到 1 之间的数值）。

- **为什么有效**：它打破了“将图文对齐视为一个整体模糊打分”的黑盒。通过引入最顶尖的目标检测器，将“有没有小狗”、“是不是两只”、“小狗是不是白色”这些物理事实拆解成可量化的目标级客观任务，判定极其冷酷和精准。
- **适用场景与细分维度**：
- **任务类型**：高度复杂的组合式 Text-to-Image (T2I) 强化学习优化。
- **细分维度**：**指令遵循 - 组合能力（Compositional Capabilities）、数量计数（Counting）、颜色/属性绑定（Color Attribution）、空间布局（Position）**。

---

## 🛠️ Flow-Factory 奖励系统三大工程优化重点

除了卓越的模型支持，Flow-Factory 在**奖励算力调度上**也做出了极具工业价值的工程创新：

### 1. 异步奖励计算流水线（Async Reward Pipeline）

由于像 `RationalRewards` 这样功能强大但体量庞大的 VLM 裁判，通常需要部署在远程的 vLLM 集群上，网络 HTTP 交互延迟（I/O Bound）会极大地拖慢 RL 训练。Flow-Factory 允许在 YAML 中配置：

```yaml
rewards:
  - name: "remote_rational_t2i"
    reward_model: "flow_factory.rewards.my_reward_remote.RemotePointwiseRewardModel"
    async_reward: true # 开启异步计算
    num_workers: 4 # 4线程并发请求
```

当主线程的 GPU 还在对当前/下一批次进行扩散采样（Sampling）时，多线程计算组件已经在后台并发地向远程 VLM 发送评分请求，**将网络 I/O 延迟与 GPU 采样时间完美重叠**，从而大幅度消除了训练等待。

### 2. GDPO 多奖励解耦优势聚合（Advantage Aggregation）

当需要同时挂载多个奖励（如用 PickScore 管审美，用 GenEval 管数数）时，传统做法直接对奖励求和（`sum`）会导致分值尺度大的模型彻底淹没尺度小的模型。Flow-Factory 提供了 **GDPO 策略**：

$$A_{total} = \sum_{i} w_i \cdot A_i$$

它先在组内对每个奖励模型**分别独立计算出相对优势（Advantage）并实施 Batch Normalization 归一化**，最后再进行加权合并。这使得多目标强化学习微调的训练极其平稳。

### 3. 隔离式远程奖励服务器（Remote Reward Server）

针对部分奖励模型面临的“环境依赖冲突”（例如：奖励模型需要 PyTorch 1.x、旧版 transformers 或特定版本的 Python 3.8，而 Flow-Factory 核心框架运行在 PyTorch 2.x 和 Python 3.10 上），Flow-Factory 设计了完善的 **Remote Reward Server 架构**。

开发者可以在独立的 Anaconda 环境中通过框架内置的 `RewardServer` 基类一键拉起 HTTP 服务，而主微调进程仅需配置 `server_url` 即可实现全自动的序列化通信与跨进程调用。
