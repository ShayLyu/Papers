# DexPoint 阅读笔记

论文：
- `DexPoint: Generalizable Point Cloud Reinforcement Learning for Sim-to-Real Dexterous Manipulation`
- arXiv: `2211.09423`
- CoRL 2022

相关链接：
- Paper: https://arxiv.org/abs/2211.09423
- PMLR PDF: https://proceedings.mlr.press/v205/qin23a/qin23a.pdf
- Project: https://yzqin.github.io/dexpoint/
- Code: https://github.com/yzqin/dexpoint-release

## 1. 一句话理解

DexPoint 想解决的问题是：

`如何只在仿真中训练一个灵巧手 RL policy，让它在真实世界里仅靠单视角点云 + 本体感觉，就能对同类别新物体完成 dexterous grasp / door opening。`

它的核心不是“发明了一个很复杂的新 RL 算法”，而是把下面几件事组合得非常实用：

1. 用 `point cloud` 作为主要视觉表示
2. 用 `imagined hand point cloud` 补足手指被遮挡的问题
3. 用 `contact-based reward` 改善纯 RL 的探索和抓取稳定性
4. 用 `multi-object training` 提高对新物体的泛化

## 2. 这篇论文的目标边界

DexPoint 主要做的是：

- dexterous grasping
- door opening
- sim-to-real
- category-level generalization

它**不是**做：

- in-hand rotation
- 触觉感知
- foundation model / diffusion / imitation learning 主路线

所以如果你后面想做 `in-hand rotation`，DexPoint 更适合被你当成：

- 环境设计参考
- sim2real 设计参考
- 观测表示参考
- reward 设计参考

而不是直接把任务原样照搬。

## 3. 论文要解决的核心难点

论文里其实抓得很准，主要有三类困难：

### 3.1 新物体泛化

传统 dexterous policy 常常只对单个物体有效，换个瓶子、换个把手就不行。

DexPoint 通过：

- 点云表示
- 多物体联合训练

来做 category-level generalization。

### 3.2 sim2real 的感知落差

真实机器人里你拿到的是：

- 单视角点云
- 有噪声
- 有遮挡
- 手和物体接触后，手指区域更容易丢失

这会直接影响策略对“手-物关系”的判断。

### 3.3 纯 RL 很难学到“正确接触”

如果 reward 只鼓励手接近物体，策略很可能学出奇怪动作：

- 用手背碰
- 卡住
- 接触方式不稳定

所以他们设计了 contact-based reward，让策略更容易学出“像抓取”的接触结构。

## 4. 论文最核心的两个贡献

## 4.1 Imagined Hand Point Cloud

这是这篇论文最值得你认真消化的点。

问题：

- 相机只能看到部分手指
- 接触时遮挡更重
- RL 又只能吃有限点数

做法：

- 利用手部运动学模型和关节角
- 通过 forward kinematics 算每个 finger link 的位姿
- 再从 hand mesh 上采样点
- 合成一份“想象出来的 hand point cloud”
- 和真实观测点云拼接起来一起喂给策略

本质上它是在做：

`用机器人自身可知的几何先验，补偿视觉观测里缺失的手部信息。`

这个想法为什么重要：

- 不依赖 tactile sensor
- 比直接让网络自己从 proprioception 推断接触几何更直接
- 对 sim2real 很友好，因为真实机器人也有 joint encoder

对你后面做 `in-hand rotation` 的启发很强：

- rotation 过程中遮挡会比 grasp 更严重
- 物体在掌内滚动时，手-物相对关系更关键
- imagined hand/object representation 很可能更重要

## 4.2 Contact-Based Reward

他们没有把 contact 当 observation 输入，而是把它用于 reward。

关键逻辑是：

- thumb 必须接触物体
- 另外至少两个手指接触物体

这样 reward 才激活。

直觉上，这在鼓励：

- 拇指参与对握
- 多指包络物体
- 避免无意义触碰

这个设计很聪明，因为：

- 训练时仿真里能拿到 oracle contact
- 部署时不需要真实触觉传感器
- 既利用了仿真优势，又不把真实部署卡死

对于你未来的 `in-hand rotation`，这会启发两件事：

1. 训练时可以大量使用 sim 中的 privileged contact 信息做 reward
2. 但不要把策略过度依赖于真实系统难拿到的 contact observation

## 5. 任务设定

论文用了两个任务：

1. `grasping`
   目标是抓住物体并移动到目标位姿

2. `door opening`
   目标是先转动门把手，再拉开门

硬件/系统设定：

- Allegro Hand: `16-DoF`
- XArm6: `6-DoF`
- 总 action 维度：`22`
- 相机：`RealSense D435`
- 仿真：`SAPIEN`
- sim timestep: `0.005s`
- control timestep: `0.05s`

这个“手 + 臂”的系统设定很重要，因为它不是只在固定底座上玩手指，而是把 arm 也纳入控制。

## 6. 观测、动作、网络

### 6.1 观测

观测包含 4 部分：

1. 相机观测点云
2. 机器人 proprioception
3. imagined hand point cloud
4. 目标位置 / 目标位姿信息

点云预处理包括：

1. 裁剪工作空间
2. 均匀下采样到 `512` 点
3. 给仿真点云加距离相关高斯噪声
4. 从相机坐标系变换到机器人 base 坐标系

### 6.2 动作

动作一共 `22` 维：

- 6 维 arm 末端位姿控制
- 16 维 hand 关节控制

其中：

- arm 通过 IK 求 joint motion
- hand 用 position controller
- arm 和 hand 都用了 PD 控制

### 6.3 网络和 RL

- RL 算法：`PPO`
- 视觉 backbone：`PointNet`
- 观察点和 imagined 点拼接
- 每个点附一个 one-hot 标记，说明它是 observed 还是 imagined

这说明论文的重点不在“更强的 RL 算法”，而在：

- representation
- reward
- sim2real-friendly system design

## 7. 实验结论

### 7.1 多物体训练明显提升新物体泛化

论文比较了：

- single-object training
- multi-object training

结果是：

- 单物体训练在已见物体上可能略好
- 多物体训练在未见物体上明显更强

这和你后面想做“泛化的 in-hand rotation”高度一致。

### 7.2 imagined point cloud 和 contact reward 都很关键

消融结果非常直观：

- 去掉 imagined point cloud，性能下降
- 去掉 contact reward，性能几乎崩掉
- 两者都去掉，几乎学不出来

这说明 DexPoint 的有效性高度依赖这两个设计，而不是 PPO 本身。

### 7.3 sim2real 成功依赖“仿真点云和真实点云尽量像”

项目页里强调了一个非常实用的结论：

`simulation 和 real world 的 point cloud 相似性，是成功 sim2real transfer 的关键因素之一。`

这句话非常值得记住，因为它直接影响你后面做环境时的重点：

- 不只是改 reward
- 不只是做 domain randomization
- 还要尽量让观测通道本身对齐

## 8. 这篇论文对你最有用的地方

如果你的目标是：

- 纯仿真
- 以后尝试 sim2real
- 想做 in-hand rotation

那么 DexPoint 对你最有价值的不是“任务本身”，而是下面 5 点：

1. `point cloud policy`
   如果你不想严重依赖 RGB，DexPoint 很适合当参考

2. `imagined geometry`
   这是你后面做 hand-centric 表示时最值得借鉴的设计

3. `privileged reward, non-privileged policy`
   训练时用 contact，测试时不用 contact observation，这个套路很强

4. `multi-object training`
   如果你要做 generalizable rotation，一定要早早引入

5. `sim2real preprocessing`
   crop / downsample / noise / frame alignment 这套流程非常实战

## 9. 这篇论文的局限

你读的时候也要带着批判性看，它不是万能底座。

### 9.1 任务还不是 in-hand manipulation 主线

DexPoint 更偏：

- 抓取
- 接触建立
- 目标搬运

而 `in-hand rotation` 更关心：

- 物体在掌内重定位
- 连续接触切换
- rolling / sliding / finger gaiting

这部分 DexPoint 并没有直接覆盖。

### 9.2 依然比较依赖 carefully designed reward

虽然这很实用，但也意味着：

- reward engineering 成本高
- 换任务时需要重新设计

### 9.3 点云来自单视角，遮挡仍是硬问题

imagined hand point cloud 只补了“手”，没有完整解决“物体被遮挡后的状态恢复”。

如果做 in-hand rotation，这个问题会更严重。

### 9.4 代码更像研究原型，不一定是最省事的工程底座

从 repo 说明看，DexPoint 提供了：

- 环境
- 示例
- 训练入口

但训练代码与 `DexArt` 共享接口，很多东西读起来可能不会特别“开箱即用”。

## 10. 建议你的阅读顺序

### 第一遍：只抓主线

按这个顺序读：

1. Abstract
2. Introduction
3. Figure 1
4. Figure 3
5. Section 3.1 Reward
6. Section 3.2 Imagined Hand Point Cloud
7. Table 1
8. Table 2
9. Real-world evaluation

第一遍不要陷入公式细节，只回答 3 个问题：

1. 它到底想解决什么问题？
2. 它的关键 trick 是什么？
3. 这些 trick 为什么对 sim2real 有帮助？

### 第二遍：带着你的任务去读

第二遍建议专门问：

1. 哪些设计可以迁移到 `in-hand rotation`？
2. 哪些设计只适合 grasping？
3. 如果我要改任务，reward 怎么改？
4. 如果物体在掌内完全遮挡，point cloud 够不够？

## 11. 建议先看的代码入口

根据 repo README，最值得先看的入口是：

1. `example/state_only_env.py`
   先理解最小环境

2. `example/example_use_pc_env.py`
   理解点云观测怎么进环境

3. `example/example_use_imagination_env.py`
   理解 imagined point cloud 怎么接进去

4. `example/example_dexpoint_grasping.py`
   这是最接近论文实验的环境入口

然后再去找：

- env 定义
- reward 实现
- observation 构造
- PointNet backbone
- PPO 训练入口

## 12. 你接下来最适合做的事

如果我们要继续一起读 DexPoint，我建议下一步分成两条：

### 路线 A：论文精读

我继续帮你逐节拆：

- Intro
- Method
- Reward
- Observation
- Experiment

### 路线 B：代码精读

我去把 repo clone 下来或者按 GitHub 结构读源码，帮你回答：

- 环境类从哪进
- point cloud 在哪生成
- imagined point cloud 在哪实现
- reward 在哪写
- PPO 训练脚本怎么调用

如果你的目标是“尽快上手改代码”，建议优先走路线 B。
