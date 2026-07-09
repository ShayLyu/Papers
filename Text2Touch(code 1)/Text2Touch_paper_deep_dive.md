# Text2Touch 论文精读

论文：
- `Text2Touch: Tactile In-Hand Manipulation with LLM-Designed Reward Functions`
- arXiv: `2509.07445`
- CoRL 2025
- arXiv 提交日期：`2025-09-09`

相关链接：
- arXiv: https://arxiv.org/abs/2509.07445
- PMLR: https://proceedings.mlr.press/v305/field25a.html
- OpenReview PDF: https://openreview.net/pdf?id=U9zcbQVDGa
- Project: https://hpfield.github.io/text2touch-website/

## 1. 先给出总判断

这篇论文和 `DexPoint`、`Robot Synesthesia`、`DexRepNet++` 很不一样。

它的核心问题不是：

- 观测怎么表示
- 触觉怎么融合
- backbone 怎么换

而是：

`对于复杂 tactile in-hand manipulation，reward function 到底能不能也自动化设计，而且真的比人工调 reward 更强？`

所以这篇论文最重要的贡献不是一个新的 tactile encoder，而是：

- 把 `LLM-based reward design` 推进到 `tactile in-hand rotation`
- 让它在 `70+ environment variables` 的复杂环境里仍然可用
- 最后通过 `teacher-student sim2real distillation` 上到真实 Allegro Hand

如果一句话概括：

`Text2Touch 是一篇“reward engineering 自动化”论文，而不是一篇“感知表示创新”论文。`

来源：论文摘要和引言。  
- [PMLR Abstract](https://proceedings.mlr.press/v305/field25a.html)
- [OpenReview PDF p.1](https://openreview.net/pdf?id=U9zcbQVDGa)

## 2. 一句话理解

这篇论文要解决的问题是：

`高自由度触觉灵巧手的 reward 太难手工设计了，能不能让 LLM 直接根据任务描述和环境变量，自动写出更短、更稳、并且真能在真实机器人上工作的 reward function？`

作者选择的验证任务也很狠：

- `multi-axis in-hand object rotation`
- `palm-up` 和 `palm-down` 两种手朝向
- `real-world vision-based tactile sensing`

这不是一个玩具任务，所以如果这件事成立，说明 LLM 设计 reward 在 dexterous tactile manipulation 上确实有研究价值。来源：摘要。  
- [PMLR lines 10-14](https://proceedings.mlr.press/v305/field25a.html)

## 3. Introduction 的核心逻辑

### 3.1 作者指出的真正瓶颈

引言开头非常直接：灵巧手里最痛苦的环节之一不是网络结构，而是 reward 设计。传统方法通常需要专家反复：

- 猜 reward term
- 调权重
- 观察策略崩在哪
- 再继续调

这个过程慢、脆弱，而且容易注入人类偏见。来源：引言第一页。  
- [OpenReview PDF p.1 lines 23-39](https://openreview.net/pdf?id=U9zcbQVDGa)

### 3.2 为什么触觉让问题更难

作者特别强调，过去 LLM 自动写 reward 的工作主要处理：

- 视觉
- proprioception

而没有碰 tactile。原因很现实：

- tactile 信号复杂
- 与接触、滑移、局部力学强相关
- 高自由度手本来就难学

把 tactile 也纳入 reward 设计，复杂度会明显上升。来源：引言。  
- [OpenReview PDF p.1 lines 38-56](https://openreview.net/pdf?id=U9zcbQVDGa)

### 3.3 这篇论文真正想证明什么

作者想证明的不只是“LLM 能写 reward”，而是 3 件事：

1. 在复杂 tactile 环境里，LLM 仍能写出有效 reward
2. 合适的 prompting 比“直接让 LLM 随便写”重要得多
3. 这种 reward 设计出来的 teacher policy 可以蒸馏成真实可部署的 tactile student

所以这篇论文同时在验证：

- 方法论：LLM 做 reward 是否成立
- 工程实践：复杂环境里怎么 prompt 才能成立
- 真实部署：sim2real 是否成立

## 4. 任务为什么很有代表性

作者做的是 `gravity-invariant, multi-axis in-hand object rotation`，要求机器人把物体悬空握持，并绕三条互相垂直的轴旋转，同时还要支持：

- `palm-up`
- `palm-down`

这点很关键，因为它比普通桌面支撑下的 rotation 难很多。物体不能靠手掌托住，策略必须真正学会：

- 稳定接触
- finger gaiting / local contact repositioning
- 姿态维持

来源：引言和方法。  
- [OpenReview PDF p.1 lines 46-56](https://openreview.net/pdf?id=U9zcbQVDGa)
- [OpenReview PDF p.3 lines 115-124](https://openreview.net/pdf?id=U9zcbQVDGa)

这也是它和 `Robot Synesthesia` 的区别之一。后者更偏多模态统一表示；Text2Touch 更强调：

- tactile 很重要
- 但当前最大的瓶颈可能是 reward 不是表示

## 5. 系统设定与观测

真实系统是：

- `Allegro Hand`
- `TacTip` 视觉式触觉传感器
- 触觉 + proprioception 作为 student 部署输入

作者在真实部署阶段明确说，student 只接收：

- joint positions
- joint velocities
- tactile observations

运行频率 `20Hz`。来源：方法 `3.5`。  
- [OpenReview PDF p.4 lines 212-221](https://openreview.net/pdf?id=U9zcbQVDGa)

这个设定说明两件事：

1. 真实部署时并不依赖外部视觉 policy 输入
2. 触觉在这里不是辅助，而是主感知通道之一

如果你后面想做 tactile-centric rotation，这篇会很有参考价值。

## 6. 方法主线精读

## 6.1 它基于什么框架

Text2Touch 构建在 `Eureka` 这类 LLM 自动生成 reward 的思路上，但作者发现原始 Eureka 式 prompt 放到这个任务上几乎不工作。来源：`3.1` 和 `3.3`。  
- [OpenReview PDF p.3-4](https://openreview.net/pdf?id=U9zcbQVDGa)

所以他们做的核心不是简单“套个 GPT-4”，而是针对复杂 tactile 环境重新设计 prompt 结构。

## 6.2 Iterative LLM Reward Design

整体流程是：

1. 给 LLM 任务自然语言描述
2. 给 LLM 环境代码/变量上下文
3. LLM 生成 reward candidates
4. 用 PPO 分别训练这些 reward 下的 teacher policy
5. 用 task fitness 选最好的 reward
6. 把结果反馈给 LLM，下一轮继续改

这本质上还是一个：

- `LLM propose`
- `RL evaluate`
- `feedback refine`

的闭环。来源：`3.1`。  
- [OpenReview PDF p.3 lines 105-150](https://openreview.net/pdf?id=U9zcbQVDGa)

### 为什么自然语言任务描述值得注意

作者没有把 prompt 写得特别细，而是选择一句相对抽象但关键的信息：

`通过 regrasping 或 finger gaiting，将物体重新定位和重新定向到目标位置和姿态，并在操作中局部地脱开与重建接触。`

这个设计很重要，因为作者发现：

- prompt 太简单，不足以描述任务
- prompt 太具体，会带入人类偏见

这给你的启发是：如果以后你也想尝试 LLM 辅助 reward，任务语言描述本身就是很重要的研究变量。来源：`3.1 Natural Language Task Description`。  
- [OpenReview PDF p.3 lines 115-120](https://openreview.net/pdf?id=U9zcbQVDGa)

## 6.3 为什么要引入 Scalable Bonus / Penalty

这是论文一个非常实用的点。

原版 Eureka 风格常常把 success bonus 作为外部固定标量加到 reward 上。但作者发现，LLM 生成 reward 的数值尺度变化太大，一个固定 bonus 经常根本不匹配。于是他们把：

- success bonus `B`
- early termination penalty `P`

作为可缩放变量显式放进 prompt 环境里，让 LLM 自己把它们纳入 reward 表达式。来源：`3.2 Scaling Bonuses and Penalties`。  
- [OpenReview PDF p.3 lines 160-176](https://openreview.net/pdf?id=U9zcbQVDGa)

这个改动看似小，实际上非常关键。作者后面直接说，如果不给 `B` 和 `P` 这种可缩放变量，任务基本不可能成功。来源：Table 1 附近说明。  
- [OpenReview PDF p.5 lines 228-233](https://openreview.net/pdf?id=U9zcbQVDGa)

这说明：

- LLM 自动写 reward 不是“随便问一句就能成”
- 你必须把 reward 的尺度控制问题也纳入 prompt 设计

## 6.4 为什么要 Modified Prompt Structuring

作者的环境有 `70+` 个变量，远多于 Eureka 原始示例里的约 `10` 个变量。于是直接给环境代码时，LLM 经常出现：

- 语法错误
- 变量类型错
- 引用了不存在的变量

为了解决这个问题，作者额外提供了显式的 reward function signature，把可用变量名字和类型都列出来。来源：`3.3 Modified Prompt Structuring`。  
- [OpenReview PDF p.4 lines 178-189](https://openreview.net/pdf?id=U9zcbQVDGa)

这是这篇论文很有价值的地方：它不是只展示“我们用 LLM 成功了”，而是把成功所依赖的 prompt engineering 细节讲清楚了。

## 6.5 Sim-to-Real Teacher-Student

reward 发现阶段训练的是 privileged teacher。之后作者：

- 用 teacher rollout
- 训练 student 去回归 teacher action
- student 只看 tactile + proprioception

这和 `Robot Synesthesia` 的 teacher-student 思路很像，但这里 teacher-student 不是为了多模态编码，而是为了：

- 先让 reward discovery 在更容易的 privileged setting 里进行
- 再把结果迁到真实可观测输入

来源：`3.4` 和 `3.5`。  
- [OpenReview PDF p.4 lines 190-221](https://openreview.net/pdf?id=U9zcbQVDGa)

## 7. 这篇论文真正的新意在哪里

很多人第一次看标题会以为它的创新是：

- “LLM 也能做机器人”

但我觉得更准确的理解是：

### 新意 1

把 `LLM reward generation` 推到 `tactile in-hand manipulation` 这种更复杂的场景。

### 新意 2

证明在变量很多的环境里，`prompt structure` 本身就是成败关键。

### 新意 3

把自动生成出来的 reward 真的走完了：

- simulation
- distillation
- hardware deployment

这比只在仿真里展示高分要有说服力得多。

## 8. 结果精读

## 8.1 Prompting Strategy Verification

Table 1 是全篇最重要的证据之一。作者比较四种 prompt 方式，发现只有他们的 `Bonus/Penalty + Modified` 组合才在多数 LLM 上真正解决任务。比如：

- GPT-4o: `5.46` Rots/Ep, `84%` Solve Rate
- Gemini-1.5-Flash: `5.48`, `31%`
- o3-mini: `5.38`, `28%`

而原始 prompt 或缺失 bonus/penalty 的 prompt 基本接近零成功。来源：Table 1。  
- [OpenReview PDF p.5 lines 225-233](https://openreview.net/pdf?id=U9zcbQVDGa)
- [Project Key Results](https://hpfield.github.io/text2touch-website/)

这个结果的意义不是“哪个 LLM 最强”，而是：

`正确的问题包装方式，比单纯换更大的模型更关键。`

## 8.2 LLM 生成的 reward 比人工 reward 更短但更强

Table 2 很有冲击力。以 baseline 为对照：

- baseline: `4.92` best Rots/Ep
- Gemini-1.5-Flash: `5.48`
- GPT-4o: `5.46`
- o3-mini: `5.38`

同时，代码复杂度显著下降。项目页显示这些 LLM 生成 reward 通常只用了：

- 更少环境变量
- 更少代码行数
- 更低 Halstead Volume

作者总结为：LLM reward 一边提高性能，一边让 reward 更短、更易解释。来源：Table 2 与项目页。  
- [OpenReview PDF p.5-6 lines 259-290](https://openreview.net/pdf?id=U9zcbQVDGa)
- [Project LLM Statistics](https://hpfield.github.io/text2touch-website/)

这个结论很重要，因为它反驳了一个常见担心：

- 自动生成 reward 会不会只是“堆很多乱七八糟的项”？

在这篇里，恰恰相反。

## 8.3 Distilled Student 也优于人工 baseline

Table 3 显示，在只保留 tactile + proprioception 的 student 上，LLM 生成 reward 蒸馏出来的模型在 OOD mass 和 OOD shape 测试里仍优于 baseline。比如：

- baseline: OOD mass `2.94`, OOD shape `2.44`
- Gemini: `3.38`, `2.68`
- GPT-4o: `3.35`, `2.62`

来源：Table 3。  
- [OpenReview PDF p.6 lines 305-328](https://openreview.net/pdf?id=U9zcbQVDGa)
- [Project Distilled Observation Models](https://hpfield.github.io/text2touch-website/)

这说明 LLM reward 的收益不是只停留在 privileged teacher 上，而是真能通过 distillation 传到部署模型。

## 8.4 真机结果是最关键的

真实机器人评估包括：

- 三个 rotation axes: `x, y, z`
- 两种 hand orientation: `palm-up`, `palm-down`
- 十个 household objects

项目页给出的总平均结果是：

- baseline: `0.99` rotations, `20.0s` TTT
- GPT-4o: `1.18`, `20.7s`
- Gemini-1.5-Flash: `1.28`, `23.8s`
- Deepseek-R1-671B: `1.37`, `25.1s`

来源：Table 4 和项目页。  
- [OpenReview PDF p.7 lines 342-346](https://openreview.net/pdf?id=U9zcbQVDGa)
- [Project Real-World Policy Results](https://hpfield.github.io/text2touch-website/)

这里最值得注意的是：

- 提升不只是更快转
- 还表现为更长的未失稳时间

也就是说，reward 的改进确实改变了策略稳定性，不只是鼓励“莽着转”。

## 9. 和 AnyRotate 的关系

论文明确说，Stage 2 和 Stage 3 的 teacher-student 与 real-world pipeline 都冻结为 `AnyRotate` 的设定，只改 Stage 1 的 reward 设计。来源：实验部分。  
- [OpenReview PDF p.5 lines 237-238](https://openreview.net/pdf?id=U9zcbQVDGa)

这点特别重要，因为它让结论更干净：

- performance gain 主要来自 reward
- 不是来自更换 student architecture 或 sim2real pipeline

所以这篇论文的研究变量控制得很好。

## 10. 这篇论文对你最有价值的地方

如果你的目标是：

- 纯仿真起步
- 以后做 sim2real
- 聚焦 `in-hand rotation`

那么 Text2Touch 给你的价值主要不在“最终用 LLM”，而在这些方法论：

### 10.1 reward 是第一类研究对象

很多 dexterous paper 默认 reward 只是实现细节，这篇论文相当于提醒你：

- 在高难接触任务里，reward 设计本身就是核心研究问题

### 10.2 tactile 任务尤其需要 reward 设计

因为 tactile 能感知：

- slip
- 局部不稳定
- 接触状态

但这些东西如果没有进入 reward，很难自动变成正确行为偏置。

### 10.3 复杂环境里，自动 reward 需要结构化 prompt

如果你以后也想试 LLM 辅助 reward，不是“直接把 env 丢进去”就够了，你需要：

- 可缩放 bonus/penalty
- 详细变量签名
- 反馈驱动迭代

### 10.4 teacher-student 仍然是最现实的 sim2real 方式

尤其当 reward discovery 发生在 privileged teacher 上时。

## 11. 它和 Robot Synesthesia 的差别

这两篇很容易被混在一起，因为都在做：

- tactile
- in-hand manipulation
- sim2real

但它们切入点完全不同。

### Robot Synesthesia 更关心

- tactile 怎么几何化
- vision 和 tactile 怎么统一表示
- why input-level fusion matters

### Text2Touch 更关心

- reward 怎么自动生成
- prompt 怎么写才不崩
- LLM reward 是否真的比人工 reward 强

所以如果你以后做项目：

- `Robot Synesthesia` 更像感知/表示论文
- `Text2Touch` 更像训练目标/奖励设计论文

## 12. 局限也要看清楚

### 12.1 它没有主要创新观测表示

如果你的重点是“触觉应该怎么编码”，这篇不如 Robot Synesthesia。

### 12.2 它依赖大量计算做 reward search

作者写得很清楚，最终训练是 `8 billion steps`，reward discovery 每轮也要 `150 million steps`。来源：方法和附录训练参数。  
- [OpenReview PDF p.4 lines 194-211](https://openreview.net/pdf?id=U9zcbQVDGa)
- [OpenReview PDF p.39 lines 2839-2845](https://openreview.net/pdf?id=U9zcbQVDGa)

这意味着：

- 对普通复现者来说成本不低

### 12.3 它的“自动化”仍然不是零人工

作者依然人工设计了：

- 环境
- fitness
- curriculum
- sim2real distillation pipeline
- prompt 框架

也就是说，LLM 自动化的是 reward 函数细节，不是整个研究流程。

### 12.4 对不同任务的可迁移性还要继续验证

当前核心验证任务还是多轴 rotation，是否能同样推广到：

- insertion
- tool use
- articulated in-hand manipulation

还需要更多证据。

## 13. 对你当前研究最直接的建议

如果你未来真的做 `in-hand rotation`，我建议这样借这篇论文：

1. 不必一开始就复现它的 LLM reward pipeline。

2. 先把它当成一个强提醒：
   `reward design` 在 rotation 里值得单独做实验。

3. 当你有了 baseline 之后，可以尝试更小成本的变体：
   - 先人工列出 reward components
   - 再让 LLM 重组、删减、改尺度
   - 不必一开始全自动 search

4. 如果你后面做 tactile 版本，这篇尤其值得回头再看。

## 14. 我的最终评价

我会把 Text2Touch 评价为：

`一篇很新、很有想法、切入点和常见 dexterous 表示论文完全不同的工作。`

它最强的地方不是提出了新的 tactile encoder，而是实打实证明：

- 在复杂 tactile in-hand rotation 里
- LLM 生成的 reward 可以超过认真手调的 baseline
- 而且这种改进能通过 distillation 落到真实机器人上

如果你后面要做汇报，这篇特别适合用来讲一个很新的角度：

- dexterous manipulation 的瓶颈不只有 perception 和 policy
- `reward design itself can be a frontier`

## 15. 参考来源

- PMLR paper page: https://proceedings.mlr.press/v305/field25a.html
- OpenReview PDF: https://openreview.net/pdf?id=U9zcbQVDGa
- Project page: https://hpfield.github.io/text2touch-website/
- arXiv abstract: https://arxiv.org/abs/2509.07445
