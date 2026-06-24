# Flow-Factory 奖励模型全景介绍

本文整理自 Flow-Factory 的官方文档 `README.md` 与 `guidance/rewards.md`，并结合各奖励模型对应论文、模型卡与官方仓库进行扩展说明。目标是把这些奖励模型放到同一张图里理解：它们是谁提出的、解决什么问题、底层结构是什么、输入输出是什么、为什么有效、适合哪些生成任务，以及在细粒度维度上分别能评什么。

## 1. 先看总览表

### 1.1 Flow-Factory 内置奖励模型总表

| 名称                  | 提出团队 / 组织                     |              发表时间 | 奖励类型  | 核心主干 / 头部                                | 输入                                 | 输出                    | 主要解决的问题                   | 最适合的任务                |
| --------------------- | ----------------------------------- | --------------------: | --------- | ---------------------------------------------- | ------------------------------------ | ----------------------- | -------------------------------- | --------------------------- |
| PickScore             | 学术团队（Pick-a-Pic / PickScore）  |               2023-05 | Pointwise | CLIP-style 双塔；文本塔 + 图像塔；相似度打分头 | prompt + image                       | 标量偏好分              | 通用人类偏好、审美、整体质量排序 | Text-to-Image               |
| CLIP                  | OpenAI                              |               2021-02 | Pointwise | 文本编码器 + 图像编码器；对比学习相似度头      | prompt + image                       | 标量相似度              | 通用图文语义对齐                 | Text-to-Image / 检索 / 评估 |
| PickScore_Rank        | Flow-Factory 封装 PickScore         |              工程封装 | Groupwise | 复用 PickScore；组内排序逻辑                   | 同一 prompt 下多张图                 | 排序 / 相对奖励         | 同 prompt 多候选优选             | Text-to-Image               |
| ocr                   | PaddleOCR / PaddlePaddle 生态       | 2025 前后（PP-OCRv5） | Pointwise | OCR 检测 + 识别管线；文本正确性判别            | image（有时结合 prompt）             | 文本正确性分或奖励      | 图中文字是否写对                 | 带文字的 T2I / 海报 / UI    |
| clap                  | LAION-AI                            |               2022-06 | Pointwise | 音频编码器 + 文本编码器；对比学习相似度头      | audio + prompt                       | 标量相似度              | 音频与文本对齐                   | Text-to-Audio / Audio-Video |
| imagebind             | Meta FAIR                           |               2023-05 | Pointwise | 多模态统一 embedding 空间；共享投影头          | image/text/audio/video 等            | 标量跨模态对齐分        | 多模态一致性、音画同步           | T2A / T2V / I2V / AV        |
| GenEval               | 学术团队（Object-focused T2I 评估） |               2023-10 | Pointwise | Mask2Former + CLIP 等判别模块                  | prompt + image                       | 各对象属性是否满足      | 计数、颜色、位置、组合关系       | T2I                         |
| geneval2_soft_tifa    | GenEval2 / Facebook Research 生态   |               2025-12 | Pointwise | 本地 VLM（如 Qwen3-VL）+ 原子命题问答 + 聚合   | prompt + image + 原子清单            | 分项软分 / 总分         | 更细粒度的可解释 T2I 评测        | T2I                         |
| hpsv2                 | HPSv2 团队                          |               2023-06 | Pointwise | CLIP / OpenCLIP backbone + 偏好头              | prompt + image                       | 人类偏好分              | 更贴近人类喜好的 T2I 评分        | Text-to-Image               |
| vllm_evaluate         | Flow-Factory 通用接口               |              工程封装 | Pointwise | 远程 VLM-as-Judge；OpenAI-compatible API       | prompt + image / video / audio 等    | Yes/No + logprob reward | 任意自定义规则判断               | 通用                        |
| rational_rewards_t2i  | TIGER-AI-Lab                        |               2026-04 | Pointwise | Qwen3-VL-Instruct-8B 系 + 推理式 rubric head   | prompt + image                       | 分项评分 + 总分         | 复杂 rubric、解释型评审          | T2I                         |
| rational_rewards_edit | TIGER-AI-Lab                        |               2026-04 | Pointwise | Qwen3-VL-Instruct-8B 系 + 推理式 rubric head   | source image + edited image + prompt | 分项评分 + 总分         | 图像编辑质量、保真与改动正确性   | Image-to-Image              |
| qwen_image_bench      | Qwen / Alibaba 系                   |               2026-05 | Pointwise | Qwen3.6-27B judge；层级 rubric 评分            | prompt + image + dims_en             | 0-100 / 0-1 归一化分    | 生产级 T2I 多维评估              | Text-to-Image               |

### 1.2 这些奖励模型的共同理解方式

你可以把它们分成三类：

1. **语义相似型**：CLIP、PickScore、HPSv2、CLAP、ImageBind。它们的本质是把不同模态投到同一向量空间，再用相似度做 reward。
2. **可验证属性型**：ocr、GenEval、geneval2_soft_tifa。它们关注的是“有没有满足某个可检查条件”，例如文字、计数、颜色、位置、原子命题。
3. **VLM-as-Judge / rubric 型**：vllm_evaluate、rational_rewards_t2i、rational_rewards_edit、qwen_image_bench。它们更像“会读题、会解释、会分维度打分”的评审员。

Flow-Factory 的关键设计是：**模型与算法解耦**。也就是说，这些 reward 既可以服务于 GRPO、DPO、DiffusionNFT、AWM、DGPO、CRD、DPPO 等算法，也可以单独作为评测器使用。

---

## 2. 详细介绍每一个奖励模型

## 2.1 PickScore

### 它是什么

PickScore 是一个面向文本到图像生成的偏好打分模型，用来近似人类对生成图像的喜好。

### 谁提出的、什么时候提出的

由 PickScore / Pick-a-Pic 相关学术团队提出，发表于 2023 年 5 月。

### 核心架构

它是典型的 **CLIP-style 双塔结构**：

- 文本编码器：把 prompt 编成文本向量
- 图像编码器：把图像编成图像向量
- 打分头：通常是归一化后的余弦相似度或线性相似度，再乘温度系数

你可以把它理解成“更偏人类偏好的 CLIP”。

### 输入 / 输出

- 输入：prompt + 生成图像
- 输出：一个标量分数，越高通常代表越符合人类偏好

### 为什么有效

PickScore 不是只学“图文是否相关”，而是直接在**用户偏好数据**上学习“哪张图更像人会选的结果”。因此它比纯 CLIP 更贴近真实创作偏好。

### 适用场景

最适合：

- Text-to-Image 的整体质量奖励
- 候选图排序
- best-of-N 采样选择
- 通用审美、构图、整体可接受度评估

细分维度上，它更擅长：

- 整体图文一致性
- 整体视觉偏好
- 审美、完成度、自然性

不擅长：

- 文字逐字正确性
- 严格计数
- 复杂空间约束
- 多轮编辑中的局部保真

### 在训练里的价值

它特别适合做“软目标”，即让生成模型朝着更受人类喜欢的方向优化。

---

## 2.2 CLIP

### 它是什么

CLIP 是最经典的图文对比学习模型之一，也是很多后续奖励模型的基础。

### 谁提出的、什么时候提出的

OpenAI 提出，2021 年发表。

### 核心架构

- 图像编码器：常见为 ViT 或 ResNet
- 文本编码器：Transformer
- 训练目标：让匹配的图文对更近，不匹配的更远

### 输入 / 输出

- 输入：文本 + 图像
- 输出：图文相似度分数，或者相似度 logits

### 为什么有效

CLIP 通过海量图文对比学习，把“图和文本是否语义一致”这件事学进了共享 embedding 空间。它不需要为每个任务单独设计分类头，因此通用性很强。

### 适用场景

适合：

- 通用图文相似度奖励
- 零样本分类
- 检索
- T2I 的基础对齐奖励

细分维度上，它最擅长的是：

- 语义是否相关
- 大体描述是否匹配
- 物体级粗粒度一致性

它的短板是：

- 不能很好地区分细粒度属性绑定
- 对文字渲染、计数、位置关系不够强
- 容易把“像”与“对”混在一起

### 在 Flow-Factory 中的角色

CLIP 常作为最基础的 local reward，优点是简单、快、易部署。

---

## 2.3 PickScore_Rank

### 它是什么

这是 Flow-Factory 对 PickScore 的**组内排序封装**，不是新论文，而是工程层的 groupwise reward。

### 它解决什么问题

有时你不是想知道“一张图是否足够好”，而是想知道“同一个 prompt 下，哪张图最好”。这时绝对分数不如相对排序稳定。

### 核心思路

- 对同一 prompt 下的多个样本一起评估
- 用 PickScore 作为基础分
- 再做组内比较，得到排序或相对优势

### 适用场景

- best-of-N
- 组内采样选择
- 生成结果筛选
- 需要相对偏好的 RL 场景

### 为什么有效

相对比较通常比绝对打分更稳，也更符合人类实际选择方式。

---

## 2.4 ocr / PP-OCRv5

### 它是什么

这是一个**文字正确性奖励**。Flow-Factory 用它来奖励那些把图中文字真正写对的模型。

### 谁提出的、什么时候提出的

PaddlePaddle / PaddleOCR 生态提出。PP-OCRv5 属于 PaddleOCR 3.0 体系中的关键文本识别方案，官方技术报告在 2025 年发布。

### 核心架构

OCR 一般不是单个 head，而是一条识别链路：

1. 文本检测：找出文字区域
2. 文本方向校正：处理旋转、倒置
3. 文本识别：把图像文字转成字符序列
4. 规则比对：与目标文本比对，计算奖励

### 输入 / 输出

- 输入：图像，通常配合 prompt 中的目标文本要求
- 输出：文字是否识别正确、字符级或词级准确度、奖励分

### 为什么有效

图文模型经常会“画得像，但字是错的”。OCR 能把这类错误直接抓出来，特别适合这类强约束任务。

### 适用场景

非常适合：

- 海报
- 广告图
- UI 界面
- 包装设计
- 招牌
- 信息图
- 带标题、标注、说明文字的 T2I

细分维度上，它主要覆盖：

- 文字准确性
- 字符缺失 / 多字 / 错字
- 字形可读性
- 排版可辨识性

### 价值

如果你的训练目标包含“生成图中必须写对字”，ocr 往往是最必要的 reward 之一。

---

## 2.5 CLAP

### 它是什么

CLAP 是音频与文本的对齐模型，常被用作音频生成或音视频生成奖励。

### 谁提出的、什么时候提出的

LAION-AI 团队提出，2022 年发表。

### 核心架构

- 音频编码器
- 文本编码器
- 对比学习目标
- 共享 embedding 空间

它的形式非常像 CLIP，只是模态从 image/text 变成 audio/text。

### 输入 / 输出

- 输入：音频 + 文本 prompt
- 输出：音频与文本语义一致性的分数

### 为什么有效

因为它学会了“声音语义”和“语言描述”之间的对齐。比如“雷雨”、“鸟鸣”、“钢琴独奏”这种语义在向量空间中会对应稳定区域。

### 适用场景

- Text-to-Audio
- Audio-to-Text
- Audio-Video
- 音画一致性

细分维度：

- 声音类型是否对
- 声音氛围是否对
- 事件是否对
- 音频是否与文本提示一致

### 注意点

CLAP 更擅长“这是什么声音/氛围”，不一定擅长极细粒度时间同步或多轨音乐结构。

---

## 2.6 ImageBind

### 它是什么

ImageBind 是一个多模态统一嵌入空间模型，能把 image、text、audio、depth、thermal、IMU 等模态绑定到一起。

### 谁提出的、什么时候提出的

Meta FAIR 提出，2023 年发表。

### 核心架构

- 以图像为中心的多模态绑定框架
- 各模态各自编码，再投影到同一 embedding 空间
- 通过对齐训练，把多模态关系绑定起来

### 输入 / 输出

- 输入：任意支持模态中的一种或多种，例如 text+audio、image+audio、text+video
- 输出：跨模态相似度或对齐分数

### 为什么有效

它的关键点是：**不一定需要所有模态两两配对**，只要借助 image-paired 数据，就能把其他模态绑进同一空间。这样跨模态检索和对齐就变得可行。

### 适用场景

- Text-to-Audio
- Text-to-Video
- Image-to-Video
- Audio-Video 同步
- 多模态创作

细分维度：

- 语义对齐
- 声音是否贴合画面
- 视频是否与文本一致
- 多模态内容的整体一致性

### 价值

当你的任务不止一种模态时，ImageBind 比单模态奖励更灵活。

---

## 2.7 GenEval

### 它是什么

GenEval 是一个面向文本到图像的、对象中心的评测框架。

### 谁提出的、什么时候提出的

学术团队提出，2023 年发表。

### 核心架构

它不是一个单一的神经网络，而是一个**组合式判定管线**：

- 目标检测 / 分割模块：例如 Mask2Former
- 语义验证模块：例如 CLIP 或其他视觉判别器
- 规则聚合：判断某个属性是否满足

### 输入 / 输出

- 输入：prompt + image
- 输出：对象是否出现、数量是否对、颜色是否对、位置是否对等结构化结果

### 为什么有效

很多 T2I 失败不是“画得不好看”，而是“命题没满足”。GenEval 把问题拆成“对象是否出现、数量是否正确、属性是否绑定”这类更可验证的子任务。

### 适用场景

- T2I 的组合属性评估
- 对象计数
- 颜色绑定
- 空间位置
- 多对象共现

细分维度：

- 指令遵循
- 对象个数
- 颜色属性
- 空间关系
- 属性绑定

### 局限

它对大场景审美、风格统一性、整体艺术感不如 rubric 型 judge。

---

## 2.8 geneval2_soft_tifa

### 它是什么

它可以理解成 GenEval 的更细粒度、更结构化版本，强调“原子命题”的软匹配。

### 谁提出的、什么时候提出的

GenEval2 在 2025 年底提出。

### 核心架构

Flow-Factory 中的实现思路是：

- prompt 被拆成若干原子命题
- 本地 VLM 逐条问答判断
- 对每个命题给软分
- 再做 AM/GM 等聚合

### 输入 / 输出

- 输入：prompt + image + 原子命题列表
- 输出：细粒度分项分数和总分

### 为什么有效

传统单一总分容易掩盖失败模式。原子命题可以让你知道到底是“颜色错了”还是“位置错了”还是“对象没出现”。

### 适用场景

特别适合：

- 细粒度 T2I 评测
- 复杂指令遵循
- 组合语义验证
- 可解释 reward

### 细分维度

- 对象是否出现
- 对象数是否正确
- 属性是否绑定
- 关系是否成立
- 局部命题是否满足

---

## 2.9 HPSv2

### 它是什么

Human Preference Score v2，是一个专门用于评估文本到图像人类偏好的模型。

### 谁提出的、什么时候提出的

HPSv2 团队提出，2023 年发表。

### 核心架构

- 以 CLIP / OpenCLIP 为 backbone
- 用人类偏好数据进行微调
- 输出偏好分数

### 输入 / 输出

- 输入：prompt + image
- 输出：人类偏好分

### 为什么有效

HPSv2 的训练目标就是“预测人类更喜欢哪张图”，因此比单纯 CLIP 更贴合真实偏好。

### 适用场景

- T2I 总体偏好评估
- 候选图排序
- 通用视觉质量评分

### 细分维度

- 整体审美
- 细节自然性
- 画面完成度
- 偏好一致性

### 与 PickScore 的关系

两者都属于“偏好型图文 reward”。一般来说：

- PickScore 更像通用偏好基线
- HPSv2 更强调对人类偏好的直接拟合

---

## 2.10 vllm_evaluate

### 它是什么

这是 Flow-Factory 的通用 **VLM-as-Judge** 接口，不是固定模型，而是远程调用一个视觉语言模型来打分。

### 核心架构

- 远端 VLM
- OpenAI-compatible API
- 通过 Yes/No 问题和 logprob 计算 reward

### 输入 / 输出

- 输入：prompt + 图像 / 视频 / 音频等，外加 judge prompt
- 输出：标量 reward

### 为什么有效

当你有一个非常清晰的判定标准时，binary judge 往往很稳，且比复杂 rubric 更容易控制成本。

### 适用场景

- 任意自定义规则判断
- 需要二分类式判定的任务
- 复杂模态或复杂 prompt 的通用裁判

### 细分维度

完全取决于你怎么写 judge prompt，例如：

- 是否符合指令
- 是否存在某元素
- 是否有明显错误
- 是否满足某安全规范

### 优点

- 灵活
- 不依赖固定 reward head
- 易于扩展到新任务

### 缺点

- 依赖外部服务
- 成本较高
- 稳定性受 VLM 版本影响

---

## 2.11 rational_rewards_t2i

### 它是什么

这是一个带“理性解释”的 T2I rubric judge。

### 谁提出的、什么时候提出的

TIGER-AI-Lab 提出，2026 年发表。

### 核心架构

公开论文说明它基于 **Qwen3-VL-Instruct-8B** 体系，并通过 **Preference-Anchored Rationalization（PARROT）** 学会在给分前先生成结构化 critique。

### 输入 / 输出

- 输入：prompt + image
- 输出：分项 critique + 各维度分值 + 汇总 reward

### 为什么有效

相比“直接给一个总分”，它先解释再评分，更接近人类打分方式。这样有几个好处：

- 评审过程更可解释
- 分项信号更细
- 对训练更友好
- 更不容易把所有错误压成一个模糊分数

### 适用场景

- T2I 训练奖励
- 生成后评测
- prompt 优化
- critique-refine 循环

### 细分维度

通常会覆盖：

- 指令遵循
- 视觉保真
- 对象/属性正确性
- 构图合理性
- 审美质量
- 真实感

### 价值

这是更接近“会讲道理的评审员”的 reward。

---

## 2.12 rational_rewards_edit

### 它是什么

这是 rational_rewards_t2i 的图像编辑版本。

### 输入 / 输出

- 输入：source image + edited image + prompt
- 输出：分项 critique + reward

### 它解决什么问题

图像编辑比 T2I 更难，因为它同时要求：

- 保持原图不该变的部分
- 正确实现编辑目标
- 保证局部和整体都自然

### 适用场景

- Image-to-Image
- 图像编辑
- 局部重绘
- 风格迁移
- 文字编辑
- 基于参考图的改写

### 细分维度

- 编辑是否到位
- 原图内容保真
- 未编辑区域是否被破坏
- 局部自然性
- 结构完整性

### 为什么有效

编辑任务不能只看“结果图漂亮不漂亮”，更要看“改对没、改多没、原图保留对不对”。rational_rewards_edit 正是为此设计。

---

## 2.13 qwen_image_bench

### 它是什么

这是一个面向 Text-to-Image 的高维层级 judge。

### 谁提出的、什么时候提出的

Qwen 团队在 2026 年提出。

### 核心架构

公开信息显示它基于 **Qwen3.6-27B** 的 judge 模型，输出层级化评分结果：

- 5 个一级维度
- 23 个二级子能力
- 56 个三级可验证 rubric

### 输入 / 输出

- 输入：prompt + image + dims_en / checklist
- 输出：结构化层级评分，通常可归一化到 0-1 或 0-100

### 为什么有效

它比单一“好不好看”更接近专业评审流程。它的优点在于：

- 维度多
- 可解释
- 适合复杂真实创作场景
- 对模型优化更有方向感

### 适用场景

- 生产级 T2I 评估
- 复杂创作任务
- 创意生成
- 真实世界还原
- 多维度风格与质量评价

### 细分维度

官方总结的方向包括：

- Quality
- Aesthetics
- Alignment
- Real-world Fidelity
- Creative Generation

### 价值

这是一个非常适合“工业级 T2I 评测”的 judge，尤其当你不满足于只看 prompt alignment 时。

---

## 3. 按任务类型来选

## 3.1 Text-to-Image（T2I）

如果你的任务是普通文生图，优先顺序通常是：

1. **PickScore / HPSv2**：通用偏好和审美
2. **CLIP**：轻量语义对齐基线
3. **GenEval / geneval2_soft_tifa**：组合属性和可验证命题
4. **rational_rewards_t2i**：复杂 rubric
5. **qwen_image_bench**：最细的多维生产级评估

### T2I 常见细分维度

- 指令遵循
- 语义一致性
- 审美
- 构图
- 对象数量
- 颜色绑定
- 空间关系
- 文字准确性
- 真实感
- 创意性

---

## 3.2 Image-to-Image / Image Editing

优先顺序通常是：

1. **rational_rewards_edit**：编辑任务专用
2. **vllm_evaluate**：按你的编辑规则自定义 judge
3. **PickScore / HPSv2**：只看整体偏好时可辅助

### 常见细分维度

- 是否按指令编辑
- 原图内容保留程度
- 局部修改是否正确
- 是否引入副作用
- 视觉自然性

---

## 3.3 Text-to-Video / Image-to-Video

优先顺序通常是：

1. **ImageBind**：多模态对齐，尤其适合音画、图文、视频文本联动
2. **CLAP**：如果你关心声音描述与音频一致性
3. **vllm_evaluate**：自定义 judge

### 常见细分维度

- 文本与视频内容一致性
- 事件是否发生
- 画面连续性
- 运动是否自然
- 风格是否一致
- 时间维度的稳定性

---

## 3.4 Text-to-Audio / Audio-Video

优先顺序通常是：

1. **CLAP**：音频与文本对齐
2. **ImageBind**：跨模态一致性更广
3. **vllm_evaluate**：自定义判定

### 常见细分维度

- 声音类别
- 氛围
- 事件匹配
- 音画同步
- 多模态一致性

---

## 4. 按细分维度来理解这些奖励模型

## 4.1 指令遵循

适合：

- rational_rewards_t2i
- rational_rewards_edit
- qwen_image_bench
- vllm_evaluate
- geneval2_soft_tifa

原因：这些方法能直接读 prompt 并逐项核对。

## 4.2 文字准确性

适合：

- ocr
- rational_rewards_t2i
- qwen_image_bench
- geneval2_soft_tifa（在文字被拆成原子命题时）

原因：OCR 是最直接的硬约束信号。

## 4.3 合理性 / 逻辑合理性

适合：

- rational_rewards_t2i
- qwen_image_bench
- vllm_evaluate
- geneval2_soft_tifa

原因：rubric 型 judge 更适合检查“这个组合是否合理”。

## 4.4 颜色、位置、计数、属性绑定

适合：

- GenEval
- geneval2_soft_tifa
- rational_rewards_t2i
- qwen_image_bench

原因：这些维度需要对象级别或命题级别的核验。

## 4.5 审美 / 偏好

适合：

- PickScore
- HPSv2
- qwen_image_bench
- rational_rewards_t2i

原因：这些模型更贴近“人会不会喜欢”。

## 4.6 跨模态一致性

适合：

- CLIP
- CLAP
- ImageBind

原因：它们都是共享 embedding / 对比学习体系。

---

## 5. 为什么这些 reward 会有效

### 5.1 共享语义空间

CLIP、CLAP、ImageBind 这类模型的共同点是：把不同模态拉到同一个空间里。相似度本身就是 reward。

### 5.2 人类偏好监督

PickScore、HPSv2 更像是在学习“人会怎么选”。它们比纯语义匹配更贴近生成目标。

### 5.3 可验证的子任务拆解

GenEval、geneval2_soft_tifa、ocr 把大问题拆成小问题，让 reward 更稳定、更可解释。

### 5.4 先解释再评分

rational*rewards*\* 和 qwen_image_bench 通过 rubric、推理和层级评分，保留了人类判断的结构，因此更适合复杂任务。

---

## 6. 什么时候不该用它们

### 6.1 不要把“整体偏好模型”当成“绝对真理”

PickScore、HPSv2、CLIP 更适合整体偏好或语义对齐，不适合独立判断所有细节是否正确。

### 6.2 不要只用一个 reward 覆盖所有维度

例如只用 CLIP 会很容易忽略文字、计数、关系、局部编辑正确性。

### 6.3 注意任务与 reward 的匹配

- T2I 更适合偏好 + 组合属性 + rubric
- 编辑任务必须看保真
- 音频任务要用音频对齐模型
- 有文字的图像要加 OCR

---

## 7. 实践上的推荐组合

### 7.1 普通 T2I 训练

推荐组合：

- PickScore 或 HPSv2
- GenEval 或 geneval2_soft_tifa
- 必要时加 rational_rewards_t2i

### 7.2 带文字的海报 / UI / 信息图

推荐组合：

- OCR
- rational_rewards_t2i
- qwen_image_bench

### 7.3 图像编辑

推荐组合：

- rational_rewards_edit
- vllm_evaluate
- 视情况加偏好 reward

### 7.4 音频或音画生成

推荐组合：

- CLAP
- ImageBind
- vllm_evaluate

---

## 8. 最后给一个结论

如果把这些 reward 放到一条能力谱系上，可以这样理解：

- **CLIP / CLAP / ImageBind**：负责“像不像、对不对齐”
- **PickScore / HPSv2**：负责“人喜不喜欢”
- **ocr / GenEval / geneval2_soft_tifa**：负责“细节是否真的满足”
- **rational*rewards*\* / qwen_image_bench / vllm_evaluate**：负责“复杂任务下的结构化裁判”

对 Flow-Factory 这种 RL 训练框架来说，最重要的不是找到“唯一最强 reward”，而是根据任务把 reward 组合起来，让它们各司其职。

---

如果要继续深入，下一步最值得做的是把这篇文档再升级成一份**“按任务类型选 reward 的决策树”**，或者直接做成**“Flow-Factory 奖励模型选型手册”**。
