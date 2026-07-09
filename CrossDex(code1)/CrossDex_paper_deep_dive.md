# CrossDex 论文精读

论文：
- `Cross-Embodiment Dexterous Grasping with Reinforcement Learning`
- arXiv: `2410.02479`
- ICLR 2025
- arXiv 提交日期：`2024-10-03`

相关链接：
- Paper: https://arxiv.org/abs/2410.02479
- OpenReview PDF: https://openreview.net/pdf?id=twIPSx9qHn
- Code: https://github.com/PKU-RL/CrossDex

## 1. 先给出总判断

这篇论文最重要的价值，不是在 dexterous grasping 里再多提一个 baseline，而是在认真回答一个你现在最关心的问题：

`能不能不要为每一只新灵巧手都重新从头设计 observation、action 和 policy，而是学一个跨 hand embodiment 的统一策略？`

CrossDex 给出的答案是：

1. 用 `human hand eigengrasps` 做统一动作空间
2. 用 `fingertips + palm positions` 做统一观测空间
3. 用 `retargeting` 把统一人手动作映射到具体机器人手关节

这三个设计合在一起，才是它真正的贡献。来源：摘要、Figure 2、Section 3-4。  
- [OpenReview PDF p.0-5](https://openreview.net/pdf?id=twIPSx9qHn)

## 2. 一句话理解

这篇论文想解决的问题是：

`不同 dexterous hands 的手指数、自由度、关节极限、连杆形状都不一样，如何训练一个单一策略，让它能控制多种 hand embodiment，并对未见过的新 hand 也具备 zero-shot transfer 和高效 finetuning 能力？`

这个问题和普通“多任务 grasping”不一样。普通多任务主要处理：

- 物体变了
- 姿态变了

CrossDex 处理的是：

- 机器人手本身也变了

这一步难度很高，因为 action space 和 proprioception 本身都不再统一。来源：Introduction。  
- [OpenReview PDF p.0-2](https://openreview.net/pdf?id=twIPSx9qHn)

## 3. Introduction 的核心逻辑

### 3.1 作者先指出了什么瓶颈

引言说得很直接：过去很多 dexterous grasping 方法都是“给定一只固定的手”来学。换一只手时，经常要重新：

- 收数据
- 跑仿真
- 调超参数

这在研究上和工程上都很贵。作者想做的是“universal grasping policy”，而不是 hand-specific policy。来源：Introduction。  
- [OpenReview PDF p.0 lines 17-33](https://openreview.net/pdf?id=twIPSx9qHn)

### 3.2 为什么 cross-embodiment 在灵巧手上更难

作者明确列了两个主要困难：

1. 不同手的 DoF 数、手指数和关节语义不同，动作空间不统一
2. 手的尺寸、形状、连杆差异会影响接触几何，单一 policy 很难共享

这个判断非常重要，因为它解释了为什么“直接把 joint angles padding 到同样维度”不是一个好答案。来源：Introduction。  
- [OpenReview PDF p.0-1 lines 27-45](https://openreview.net/pdf?id=twIPSx9qHn)

### 3.3 作者从哪里得到灵感

作者的核心灵感来自 `teleoperation`。

人类操作员明明只有一双人手，却能通过观察和同步调整，把动作迁移到多种机器人手上。于是作者就问：

`有没有可能把 human hand pose 当成不同 robot hands 之间的中间语言？`

这就是 CrossDex 的根本出发点。来源：Introduction。  
- [OpenReview PDF p.1 lines 45-58](https://openreview.net/pdf?id=twIPSx9qHn)

## 4. 方法主线

CrossDex 的方法其实很整齐，可以概括为：

`human hand latent action -> retargeting -> robot joint targets`

`robot-specific proprioception -> unified fingertip/palm geometry`

这两个“统一化”分别对应：

- 动作统一
- 观测统一

再叠加一个 teacher-student 训练框架，最后得到跨手型 vision policy。来源：Figure 2 与 Section 3-4。  
- [OpenReview PDF p.3-5](https://openreview.net/pdf?id=twIPSx9qHn)

## 5. 统一动作空间精读

## 5.1 为什么作者不用原始 robot joint action

如果每只手都直接输出自己的 joint targets，会有几个问题：

- 维度不同
- 每个关节的意义不同
- 新 hand 上 action semantics 不连续

所以 policy 学到的就不是“抓取策略”，而更像“这只手的专用肌肉记忆”。

### 5.2 为什么选 human hand eigengrasps

作者不是直接用完整 MANO 45 维手指轴角，而是先从 `GRAB` 数据集的人手交互数据里做 PCA，得到一组低维 `eigengrasps`。代码 README 也明确说 `results/pca_$N_grab.pkl` 就是从 GRAB 处理出的 eigengrasps。  
- [GitHub README](https://github.com/PKU-RL/CrossDex)

论文里把它当成统一动作空间。policy 输出的是低维 `w_t`，然后再经 retargeting 映射到具体 dexterous hand 的 joint position target。来源：Section 4.1 和 Figure 2。  
- [OpenReview PDF p.4-5](https://openreview.net/pdf?id=twIPSx9qHn)

这个设计很强，因为它把“动作”从：

- hand-specific motor command

变成了：

- hand-agnostic grasp intent

### 5.3 retargeting 在这里扮演什么角色

作者用 optimization-based retargeting，把当前的人手姿态映射成某一只机器人手的 joint positions。目标函数里优化的是机器人手 `fingertips + palm` 与人手关键点的相似性，同时加了时间平滑项，并受 joint limit 约束。来源：Equation 1-2。  
- [OpenReview PDF p.3 lines 213-255](https://openreview.net/pdf?id=twIPSx9qHn)

这一步很重要。CrossDex 并不是假设不同 robot hands 之间存在一个现成的一一关节映射，而是：

- 统一到 MANO/human hand
- 再从 human hand 到 robot hand 做 retarget

这比“手 A 到手 B”的直接映射泛化性更强。

## 6. 统一观测空间精读

## 6.1 为什么作者不信任 raw proprioception

论文明确指出，直接把 hand joint positions 放进 observation，会让 policy 依赖 embodiment-specific 结构，从而伤害对新 hand 的适应。于是他们把 hand joint positions 从 policy observation 里扔掉了，只保留：

- `fingertips and palm positions`

来源：Section 4.2。  
- [OpenReview PDF p.5 lines 315-328](https://openreview.net/pdf?id=twIPSx9qHn)

这其实是非常漂亮的设计判断。

因为对 grasp 来说，真正重要的常常不是“第 7 个关节现在是 0.31 rad”，而是：

- 手指尖和手掌相对于物体在哪里
- 它们正在形成什么样的包络几何

### 6.2 它到底保留了什么

state policy 输入包括：

- arm joint positions
- fingertips + palm positions
- object pose
- object visual code
- last action

vision policy 则把 object pose 换成 object point cloud。来源：Equation 形式说明和 Figure 2。  
- [OpenReview PDF p.3-5](https://openreview.net/pdf?id=twIPSx9qHn)

### 6.3 为什么这是“shared embodiment-unaware observation”

因为这套 observation 不需要知道：

- 这是 Allegro 还是 ShadowHand
- 每只手有多少关节
- 每个关节语义是什么

它只依赖 hand-object 交互最直接的几何量。作者在结论里也把这点单独列成贡献。  
- [OpenReview PDF p.9 lines 597-601](https://openreview.net/pdf?id=twIPSx9qHn)

对于你以后迁移到新的 `arm+hand` 组合，这点非常重要。

## 7. Teacher-Student 训练框架

作者没有直接从 point cloud 对所有对象和所有手一起跑 RL，而是采用 teacher-student。

流程是：

1. 按 object 分组
2. 对每组训练 state-based PPO teacher
3. 再把所有 teacher distilled 成一个 vision-based policy
4. 蒸馏用 DAgger 在线收轨迹，再用 BC 优化 student

来源：Section 3.1 和 4.3。  
- [OpenReview PDF p.3 lines 170-198](https://openreview.net/pdf?id=twIPSx9qHn)
- [OpenReview PDF p.5 lines 366-387](https://openreview.net/pdf?id=twIPSx9qHn)

这和 DexPoint/UniDexGrasp 系列的套路比较接近，但 CrossDex 把“多对象”进一步扩大成了“多对象 + 多 embodiment”。

## 8. 多任务与 embodiment randomization

作者在训练时做了一个很实用的小 trick：因为可用手型有限，所以他们对 hand-arm 连接处的 joint origin 加高斯噪声，相当于随机化 hand 的安装位置，来丰富 embodiment space。来源：Section 4.3 附近。  
- [OpenReview PDF p.5 lines 407-410](https://openreview.net/pdf?id=twIPSx9qHn)

这点对你特别有价值，因为它几乎直接回答了你“换新的 arm+hand 组合怎么办”的一部分问题：

- 不只是换手模型
- hand mount transform 也值得随机化

作者后面的消融也说明 randomization 有助于训练手和未见手上的表现。来源：Table 4 说明。  
- [OpenReview PDF p.8-9 lines 542-545, 587-589](https://openreview.net/pdf?id=twIPSx9qHn)

## 9. 实验设定

论文在 `45` 个 YCB 物体、`6` 种 dexterous hands 上测试，其中：

- 4 种 hand 用于训练
- 2 种 hand 用于 zero-shot 测试

训练手包含不同手指数、DoF 和形态，测试手则包括：

- `16-DoF, 4-fingered LEAP Hand`
- `12-DoF, 5-fingered Inspire Hand`

来源：Section 5.1。  
- [OpenReview PDF p.6 lines 432-439](https://openreview.net/pdf?id=twIPSx9qHn)

这说明 CrossDex 的 generalization 不是只在非常像的手之间转，而是真的跨了比较明显的结构差异。

## 10. 结果精读

## 10.1 主结果为什么有说服力

Table 1 是核心结果。CrossDex 相比基线：

- 在训练手上的 vision success `0.800`
- 在未见手上的 vision success `0.352`

而 strongest baseline `MT-Raw-OA` 在未见手 vision 只有 `0.162`。state zero-shot 里，CrossDex `0.391`，而 MT-Raw-OA 只有 `0.054`。来源：Table 1。  
- [OpenReview PDF p.6 lines 412-427](https://openreview.net/pdf?id=twIPSx9qHn)

这个结果的重点不是“绝对值已经完美”，而是：

`统一 observation + 统一 action` 确实比 raw joint-centric multi-task RL 更能转到新 hand。`

### 10.2 为什么它在训练手上不一定碾压

很值得注意的一点是，CrossDex 在 training hands 的 state 成绩 `0.885` 不是所有方法里最高，`MT-Raw-OA` 有 `0.914`。但 CrossDex 在 unseen hands 上明显更强。来源：Table 1。  
- [OpenReview PDF p.6 lines 424-427](https://openreview.net/pdf?id=twIPSx9qHn)

这非常符合直觉：

- raw joint observation/action 更容易 overfit 到训练手
- CrossDex 的抽象表示略牺牲一点 hand-specific 最优性，换来更强 transfer

如果你的目标是迁移新 `arm+hand`，这正是你想要的 tradeoff。

## 10.3 finetuning 结果更实用

论文强调 zero-shot 之外，CrossDex 还提供了更好的 finetuning initialization。作者说：

- CrossDex 在所有“unseen hand” finetuning 任务上都优于基线
- 从头训练的 `No-Pretrain` 在 multi-task 学习上会 struggle

来源：Table 2 的文字说明。  
- [OpenReview PDF p.7-8 lines 560-569](https://openreview.net/pdf?id=twIPSx9qHn)

这点对工程最有意义，因为现实里你未必要求完全 zero-shot；更常见的是：

- 先迁过去
- 再花一点预算继续 finetune

CrossDex 明显是在为这种使用方式服务。

## 10.4 cross-embodiment co-training 本身也有好处

作者还比较了：

- 每只手单独训练
- 所有手一起训练

结果是 joint training 在效率和稳定性上略好，同时性能接近甚至更好。来源：Section 5.3。  
- [OpenReview PDF p.7 lines 521-523](https://openreview.net/pdf?id=twIPSx9qHn)

这说明多 embodiment 数据本身不是噪声，反而能提供 regularization。

## 11. Ablation 最该看的点

## 11.1 eigengrasp 维度不是越大越好

作者比较了 `1-E, 3-E, 9-E, 18-E, 36-E, MANO`。结论是不同 `k` 下训练/测试比较稳定，但直接用原始 `45D MANO axis angles` 的 `CrossDex-MANO` 在 zero-shot adaptation 上更差。来源：Figure 4 文字说明。  
- [OpenReview PDF p.8 lines 529-541, 584-585](https://openreview.net/pdf?id=twIPSx9qHn)

这说明：

- 合理低维动作瓶颈是有价值的
- 不是动作空间越原始越好

## 11.2 retargeting objective 会影响 transfer

论文比较了：

- Position retargeting
- Vector retargeting
- DexPilot-style retargeting

结果上 `DexPilot` 和 `Position` 都比 `Vector` 更强。来源：Table 3 附近。  
- [OpenReview PDF p.7 lines 498-505](https://openreview.net/pdf?id=twIPSx9qHn)

这点很重要，因为它说明“统一动作空间”不是一句空话，retargeting 细节本身会直接影响可迁移性。

## 11.3 不要把 embodiment label 喂给策略

论文里一个很有意思的发现是，某些 baseline 在 state-based 阶段用 embodiment label 会得到高训练表现，但蒸馏到 vision policy 和未见手时掉得厉害。作者解释说，policy 会过度依赖这个 label。来源：Table 1 后的分析。  
- [OpenReview PDF p.7 lines 506-513](https://openreview.net/pdf?id=twIPSx9qHn)

这对你是一个很好的提醒：

- 如果你真想让策略转到新 hand，尽量别喂太多 hand identity

## 12. 为什么这篇论文对你特别有用

如果你的目标是：

- 未来换新的 `arm+hand` 组合
- 希望在现有开源项目上改
- 还不想每次都重写整套 policy interface

那么 CrossDex 最值得你借的是 4 件事：

1. `统一动作接口`
   用 human-centric latent action 代替 hand-specific joint targets。

2. `统一 hand observation`
   用 fingertip/palm geometry 代替 raw hand joints。

3. `retargeting as middleware`
   把“策略想做什么”和“这只手怎么动”解耦。

4. `mount randomization`
   训练时就把 hand-arm attachment 的变化考虑进去。

## 13. 它和 DexPoint / Robot Synesthesia / DexRepNet++ 的关系

### CrossDex 和 DexPoint 的区别

- DexPoint 更关注 sim2real point cloud grasping
- CrossDex 更关注 cross-embodiment policy interface

### CrossDex 和 Robot Synesthesia 的区别

- Robot Synesthesia 主要解决 visuotactile unified sensing
- CrossDex 主要解决多手型统一控制

### CrossDex 和 DexRepNet++ 的区别

- DexRepNet++ 更关注 hand-object structured representation
- CrossDex 更关注 embodiment invariance

所以如果你后面真的要迁一个新 `arm+hand`，CrossDex 比前面几篇都更直接相关。

## 14. 局限要看清楚

### 14.1 它主要做 grasp，不是 in-hand manipulation

作者自己在 limitation 里明确说，`in-hand reorientation`、`dynamic handover`、`functional grasping` 这些还没做。来源：Conclusion and Limitations。  
- [OpenReview PDF p.9 lines 603-609](https://openreview.net/pdf?id=twIPSx9qHn)

### 14.2 训练的 hand 还是偏少

只在 4 种训练 hand 上学，2 种 unseen hand 上测。作者也承认，如果训练时能覆盖更多 hands，泛化可能更强。来源同上。  
- [OpenReview PDF p.9 lines 603-606](https://openreview.net/pdf?id=twIPSx9qHn)

### 14.3 vision policy 绝对 zero-shot 成功率还不算很高

未见手上的 vision success `0.352`，说明“可转”不等于“已经很好用”。如果你要真落地，新 hand 上继续 finetune 仍然很现实。

### 14.4 统一观测的抽象会牺牲一些 hand-specific 性能

从 Table 1 也能看出来，training hands 上 raw-space baseline 在 state 训练里更高。

## 15. 我的最终评价

我会把这篇论文评价为：

`如果你的目标是迁移到新的 arm+hand 组合，它是目前最该认真读的那类论文之一。`

因为它不是单纯展示“又学会了一个 grasp task”，而是在系统层面提出了一个很有复用价值的接口设计：

- 动作统一到 human eigengrasps
- 观测统一到 fingertips/palm geometry
- 具体 hand control 下沉到 retargeting

这套思路对你未来做：

- 换手型
- 换 arm-hand 安装方式
- 甚至从 grasp 扩到 in-hand reorientation

都很有启发。

## 16. 你接下来最适合怎么用它

如果你后面真准备改开源代码，我建议这样借 CrossDex：

1. 不一定直接照搬它全部训练流程

2. 先继承它的 `policy interface`
   - unified action latent
   - fingertip/palm observation

3. 再把你的具体任务换成：
   - in-hand rotation
   - reorientation
   - functional grasp

4. 如果有新 hand，就优先补：
   - retargeting
   - keypoint definition
   - mount randomization

## 17. 参考来源

- OpenReview PDF: https://openreview.net/pdf?id=twIPSx9qHn
- arXiv abstract: https://arxiv.org/abs/2410.02479
- official code README: https://github.com/PKU-RL/CrossDex
