# KineDex 精读笔记

原文：`478_KineDex_Learning_Tactile_I.pdf`  
标题：KineDex: Learning Tactile-Informed Visuomotor Policies via Kinesthetic Teaching for Dexterous Manipulation  
会议：CoRL 2025  
项目页：https://dinomini00.github.io/KineDex/

## 1. 一句话总结

KineDex 的核心想法是：不要再让人通过 VR、手套或视频去“遥控/重定向”灵巧手，而是让人直接用手带着机器人灵巧手完成任务，在真实接触中采集视觉、关节、本体、触觉和指尖力数据；再用 inpainting 去掉示教时人手造成的视觉遮挡，用带触觉输入和力目标输出的 Diffusion Policy 学会接触丰富的灵巧操作。

这篇论文真正想解决的不是单纯“怎么让策略更强”，而是更上游的问题：高质量触觉示教数据到底怎么采。它的判断很清楚：灵巧操作失败的很多原因不是视觉不够，而是接触过程里的力、滑移、压强、顺应性没有被自然记录和利用。

## 2. 背景与痛点

灵巧手任务通常需要三个东西同时成立：

- 手指姿态要对：比如夹住、旋转、插入、按压。
- 接触力要对：比如鸡蛋不能捏碎，牙膏又必须挤出。
- 反馈要真实：操作者需要知道“有没有碰到、碰得多重、是不是滑了”。

传统数据采集方法主要有两类：

- Teleoperation：用 VR、数据手套、手部追踪，把人的动作映射到机器人手。
- Video retargeting：从人类视频里估计手部轨迹，再转成机器人动作。

论文认为它们有两个关键缺陷：

- Human hand 和 robot hand 运动学不一致，重定向轨迹容易失真。
- 操作者缺少机器人端真实触觉反馈，接触任务高度依赖经验和试错。

KineDex 的切入点是 kinesthetic teaching，也就是人直接物理带动机器人硬件。它把“遥控一个手”换成“戴着/抓着这个手去做任务”。这个变化朴素，但很有力量，因为触觉数据在真实接触中自然产生，人也能实时感受到力反馈。

## 3. 论文贡献

论文贡献可以拆成三层：

- 数据采集范式：提出 hand-over-hand kinesthetic teaching，让操作者直接引导机器人灵巧手，采集触觉增强的示教。
- 训练数据修复：用 Grounded-SAM 分割示教画面中的人体区域，再用 ProPainter 做视频 inpainting，缓解训练时有人手、推理时无人手造成的视觉 OOD。
- 策略与控制：在 Diffusion Policy 基础上加入触觉输入，并让策略同时预测目标关节位置和目标指尖力；部署时用 force-informed target position 做力控制。

## 4. 系统流程

整体 pipeline 是：

1. 操作者通过环形绑带直接带动机器人灵巧手执行任务。
2. 系统同步记录多视角 RGB、机器人本体信息、触觉矩阵、指尖 3D 力。
3. 对采集视频做人体 mask 和 inpainting，得到更接近推理时分布的视觉观测。
4. 用处理后的视觉、触觉、本体输入训练 Diffusion Policy。
5. 策略输出动作 chunk：目标末端姿态、手关节角、五个指尖法向力。
6. 部署时用力目标修正关节目标，让手指不仅“到达位置”，还真正“压出力”。

可以把 KineDex 理解成三个模块拼起来：

- Kinematic alignment：动觉示教绕开 retargeting mismatch。
- Visual de-occlusion：inpainting 解决人手遮挡带来的训练/推理域偏移。
- Force-aware execution：策略预测力，控制器把力目标转成虚拟位移。

## 5. 数据采集设计

硬件设置包括：

- Franka Emika Panda 机械臂。
- Robotera XHand1 灵巧手。
- 两个 RGB 相机：一个正面全局视角，一个腕部近距离视角。
- XHand1 共 12 DoF：每根手指 2 个关节，拇指和食指额外有旋转关节。
- 每根手指 120 个触觉 sensing points。

动觉示教的操作方式：

- 四个非拇指手指背面安装环形绑带，操作者右手像戴手套一样带动机器人手指。
- 由于人手和机器人拇指形态不匹配，拇指由操作者左手单独控制。
- 机器人接触物体时产生的力会直接传到操作者手上，因此操作者获得真实 haptic feedback。

每条 demonstration 记录的数据：

- Visual observations：正面相机和腕部相机 RGB 图像。
- Proprioception：机械臂 TCP/末端位姿、灵巧手关节位置。
- Tactile sensing：五指触觉矩阵。
- Fingertip force：每个指尖的 3D 力向量，由局部触觉点聚合得到。

这里的关键优势是：示教者不是看屏幕猜力，而是直接在物理世界中感到力。这对牙膏挤压、注射器按压、拧瓶盖这类任务非常重要。

## 6. 视觉预处理：为什么必须 inpainting

原始 kinesthetic demonstration 有一个明显副作用：相机会拍到操作者的人手和身体。

如果直接用这些图像训练策略，推理时环境里没有人手，视觉输入分布会变，策略会出现严重 OOD。论文中的消融非常直接：不做 inpainting 的版本在 9 个任务上成功率全是 0/20。

预处理流程：

1. 用 Grounded-SAM 找出视频帧中操作者身体/手部区域。
2. 生成对应 mask。
3. 用 ProPainter 对 masked region 做视频 inpainting。
4. 用 inpainted RGB 作为策略训练输入。

论文也承认，ProPainter 没有针对机器人场景专门预训练，修复并不完美。但实验说明，只要足够减少“人手强特征”的干扰，就已经能训练出可用策略。

这个设计比 DexForce 的 trajectory replay 更可扩展。DexForce 为了得到干净图像，需要回放示教轨迹重新拍无人手画面；长时程任务中回放容易误差累积，也更慢。KineDex 直接编辑视频，代价更低。

## 7. 策略学习

KineDex 使用 Diffusion Policy 作为主干，输入是多模态观测，输出是 force-informed action。

观测空间：

- 多视角 RGB：`o_t`
- 触觉：`q_t`
- 本体/关节状态：`x_t`

动作空间：

- 目标关节/末端位置：`x_d`
- 目标指尖力：`f_d`

因此策略建模为：

```text
p(x_d, f_d | o_t, q_t, x_t)
```

论文只监督每个指尖力向量中的法向力分量 `f_z`，因为这是指尖主要能主动施力的方向。

附录里的策略细节：

- 保留官方 Diffusion Policy 的 U-Net diffusion model 和 multi-view visual encoder。
- 新增 tactile encoder。
- 触觉输入形状为 `5 x 120 x 3`。
- 每根手指共享一个 1D convolutional encoder。
- 五指特征拼接后经过两层 MLP，得到固定长度 tactile embedding。
- tactile embedding 与视觉、本体特征融合后输入策略。
- 动作为 23 维：末端 6 DoF + 灵巧手 12 joint angles + 5 fingertip normal force targets。
- action chunk 长度为 16。
- 机械臂控制频率 100 Hz，灵巧手控制频率 50 Hz。

主要训练配置：

| 配置 | 数值 |
| --- | --- |
| Observation horizon | 2 |
| Action horizon | 16 |
| 图像分辨率 | 240 x 320 |
| Optimizer | AdamW |
| AdamW betas | 0.95, 0.999 |
| Learning rate | 1e-4 |
| Batch size | 64 |
| Inference denoising iterations | 16 |
| Temporal ensemble steps | 8 |
| Temporal ensemble adaptation rate | -0.01 |

数据规模：

- 简单任务如 picking、plugging、insertion：每任务约 100 条 demonstrations。
- 更难任务如 toothpaste squeezing、syringe pressing：每任务约 150 条 demonstrations。
- 所有 baseline 每个任务训练 500 epochs。

## 8. Force Control：论文最关键的控制细节

常规位置控制是：

```text
u = K_p (x_d - x) + K_d (dot{x}_d - dot{x})
```

问题是：接触任务里，位置相同不代表力相同。示教时人可能在同一个指尖位置上施加不同压力，但如果策略只复现关节位置，机器人可能只是轻轻碰到物体，完全没有完成挤压、拧紧、按压所需的力。

KineDex 的处理方式是把目标力转换成虚拟位移，也就是 force-informed target position：

```text
x_tip_d  = x_tip  + K_tip  * f_d
x_base_d = x_base + K_base * f_d
```

直觉上，控制器假装目标位置在物体内部一点点。因为物体挡住手指，位置误差会持续存在，PD 控制就会产生持续压力。预测力越大，虚拟位移越大，实际接触力也越大。

这个方法的好处是实现简单，不需要复杂的显式力控制器；但它依赖一些前提：

- 指尖已经与物体接触或接近接触。
- 目标力方向大致沿手指主要施力轴。
- `K_tip` 和 `K_base` 调得合适。
- 物体接触刚度变化不能太离谱。

论文中 `K_tip` 和 `K_base` 是跨任务固定的超参，说明这套控制方法在他们的任务集合里有一定泛化性。

## 9. 实验任务

论文设计了 9 个 contact-rich dexterous manipulation 任务：

| 任务 | 关键难点 |
| --- | --- |
| Bottle Picking | 半满水瓶内部质量移动，需要稳定抓取 |
| Cup Picking | 纸杯轻且可变形，需要轻柔接触 |
| Egg Picking | 生鸡蛋易碎，需要精细力控制 |
| Cap Twisting | 拧瓶盖，需要扭矩、稳定夹持和手指协调 |
| Nut Tightening | 螺母旋紧，需要旋转和下压力 |
| Peg Insertion | 木钉插孔，需要空间对齐和接触引导 |
| Charger Plugging | 插头插入插座，需要精确对齐和插入力 |
| Toothpaste Squeezing | 开盖并挤牙膏，需要序列动作和连续压力调节 |
| Syringe Pressing | 握住注射器并按压活塞，需要单手稳定施力 |

这组任务覆盖了抓取、搬运、旋转、插入、挤压、按压等不同接触模式，比只做 pick-and-place 更能体现触觉和力控制的价值。

## 10. 主实验结果

每个任务 20 次试验，成功次数如下：

| 方法 | Bottle | Cup | Egg | Cap | Nut | Peg | Charger | Toothpaste | Syringe | 平均成功率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| KineDex | 17 | 20 | 17 | 15 | 16 | 15 | 12 | 9 | 13 | 74.4% |
| w/o Force Control | 0 | 16 | 5 | 2 | 7 | 0 | 0 | 0 | 0 | 16.7% |
| w/o Tactile Input | 15 | 17 | 18 | 10 | 12 | 16 | 10 | 3 | 8 | 60.6% |
| w/o Inpainting | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0% |

核心观察：

- KineDex 在多数任务上超过 70%，普通抓取任务接近满分。
- 去掉 force control 后，平均成功率从 74.4% 掉到 16.7%，说明“预测并执行力”是接触任务的关键。
- 去掉 tactile input 后，平均成功率降到 60.6%，整体仍能做一些视觉足够的任务，但在 Cap Twisting、Toothpaste Squeezing、Syringe Pressing 这类强接触任务上明显下降。
- 去掉 inpainting 后全灭，说明视觉域偏移不是小问题，而是系统级问题。

论文特别指出，在 Cap Twisting、Toothpaste Squeezing、Syringe Pressing 三个接触密集任务上，去掉触觉输入平均成功率下降 26.7%。这说明触觉不是锦上添花，而是在视觉遮挡、接触状态不可见时提供了关键补充。

## 11. 与 Teleoperation 的数据采集对比

论文复现了 Open-TeleVision 风格的遥操作系统，用 Meta Quest 3 做操作者接口，机器人平台是 Franka + Inspire Hand。为了公平，KineDex 对比实验也使用同一 Inspire Hand。

五个任务的 demonstration collection 成功次数：

| 方法 | Bottle | Cup | Cap | Charger | Syringe | 平均成功率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| KineDex | 20 | 20 | 20 | 18 | 20 | 98% |
| Teleoperation | 19 | 9 | 7 | 0 | 4 | 39% |

效率上：

- Syringe Pressing 中，KineDex 单条 demonstration 时间约为 teleoperation 的一半。
- Bottle Picking 中，KineDex 用时不到 teleoperation 的三分之一。

论文给出的解释很合理：

- Teleoperation 缺少真实触觉反馈，操作者容易用力过大或过小。
- VR 远程视觉反馈不自然，细粒度操作更难。
- retargeting 和系统延迟增加了调整时间。

用户研究也支持这个结论。5 位参与者都认为 KineDex 更适合采集准确触觉数据、更适合复杂任务；80% 认为 KineDex 更容易使用。

## 12. 为什么这篇论文有效

KineDex 的强点不是某一个模块特别炫，而是把“数据采集、视觉修复、触觉策略、力执行”这四件事串成了闭环。

很多灵巧操作论文容易只在 policy 侧卷模型，但 KineDex 把问题前移到 demonstration 的质量。它的逻辑链是：

```text
真实物理示教 -> 真实触觉/力数据 -> 去除人手视觉偏移 -> 多模态模仿学习 -> 力感知执行
```

这条链每一环都对应一个具体失败模式：

- retargeting mismatch：用 hand-over-hand 解决。
- 没有触觉反馈：用真实接触解决。
- 人手遮挡：用 inpainting 解决。
- 只复现姿态不复现力：用 force-informed action 和虚拟位移解决。

因此它不像是简单堆模块，而是围绕 contact-rich dexterous manipulation 的失败原因逐个补洞。

## 13. 局限与隐含风险

论文显式提到两个局限：

- Inpainting 在更严重遮挡下可能失效，需要用机器人场景数据 fine-tune。
- 当前由于拇指形态不匹配，需要两只人手控制一只机器人手，不利于双手示教扩展。

除此之外，我认为还有几个隐含问题：

- 力控制方法偏启发式，`K_tip`、`K_base` 对不同手型、物体刚度和接触材质可能敏感。
- 只监督法向力 `f_z`，对切向力、摩擦、滑移和扭矩的建模不足。
- Inpainting 可能会生成视觉伪影，策略是否学到了物体真实状态还是修复纹理中的偏差，需要更多分析。
- 任务虽然有 9 个，但仍是固定场景下的单任务训练，跨物体、跨场景、跨机器人泛化还没充分验证。
- 用户研究只有 5 人，结论方向明确，但统计强度有限。

## 14. 对 DexHand 项目的启发

如果我们把这篇论文映射到 DexHand 相关研发，可以提炼出几条很实用的路线：

- 数据采集优先级很高：如果目标是接触丰富任务，先设计能采到真实触觉和真实力的数据闭环，而不是先堆更大的策略模型。
- 触觉数据要和动作目标绑定：仅把触觉作为 observation 可能不够，最好也让 action 显式包含力或接触目标。
- 视觉遮挡要正面处理：动觉示教天然会引入人手遮挡，必须提前设计去遮挡方案，比如 inpainting、重放、透明手套、相机布局规避等。
- 控制器和策略不能割裂：策略输出什么，控制器是否能 faithfully execute，是接触任务成败的核心。
- 消融设计值得借鉴：w/o force control、w/o tactile input、w/o inpainting 这三个 baseline 很直接，能分别验证力执行、触觉感知、视觉预处理的必要性。

## 15. 复现/实现检查清单

如果要复现一个 KineDex-like 系统，至少需要确认：

- 灵巧手是否能被人安全、低阻力地物理带动。
- 每根手指是否有足够密度的触觉/力估计。
- 示教时是否能同步记录 RGB、关节、本体、触觉、力。
- 人手遮挡是否可通过 mask + video inpainting 处理到足够干净。
- policy 是否能融合视觉、本体和触觉输入。
- action 是否包含显式力目标。
- 控制器是否能把力目标稳定转换为真实接触力。
- 是否有足够接触密集任务来验证系统，而不是只测 pick-and-place。

## 16. 最值得记住的点

KineDex 的本质不是“Diffusion Policy 加了触觉”，而是“用动觉示教采到真实触觉和力，再让策略学会并执行这些力”。  

在灵巧操作里，姿态只是故事的一半；另一半是接触过程中的力。KineDex 把这另一半从数据采集一直保留到控制执行，所以它能在牙膏挤压、注射器按压、拧瓶盖这类任务上显著超过去掉力控制或触觉输入的版本。
