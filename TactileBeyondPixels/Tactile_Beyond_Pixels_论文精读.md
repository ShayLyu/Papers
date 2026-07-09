# Tactile Beyond Pixels 论文精读

论文：
- `Tactile Beyond Pixels: Multisensory Touch Representations for Robot Manipulation`
- CoRL 2025
- 当前本地版本：`661_Tactile_Beyond_Pixels_Mult.pdf`

相关链接：
- 本地 PDF: [661_Tactile_Beyond_Pixels_Mult.pdf](/Users/shay/Desktop/DexHand/TactileBeyondPixels/661_Tactile_Beyond_Pixels_Mult.pdf)
- Digit 360 相关背景文献：`Digitizing touch with an artificial multimodal fingertip`

## 1. 先给结论

这篇论文最值得记住的，不是“把 tactile image 之外的信号也喂给模型”，而是它明确提出了一个更强的判断：

`机器人触觉不该再被等同于像素，而应该被当成一个天然的多模态时空感知问题。`

作者给出的答案是 `Sparsh-X`：

1. 用 `image + audio + IMU + pressure` 四种触觉模态一起建表示
2. 用 `self-supervised pretraining` 在约 `1M` 段无标注接触数据上先学通用 touch representation
3. 再把这个表示迁移到 `物理属性理解 + 模仿学习 + sim-to-real tactile adaptation`

如果一句话总结全文：

`这篇论文证明了，多模态触觉表征不仅能做“感知”，还能真正进入策略学习闭环，并在真实机器人操作里带来稳定收益。`

## 2. 一句话理解

Sparsh-X 想解决的问题是：

`面对 Digit 360 这种同时输出图像、振动、运动和压力的传感器，怎样学到一个统一的、多任务可迁移的触觉表征，让机器人不仅能“看见接触”，还能“听见接触、感觉到接触、估计接触状态”，并把这些信息用于操作策略。`

它的核心判断是：

- 触觉图像擅长表达接触形状、接触斑块和局部变形
- 音频擅长表达接触建立/脱离、碰撞、摩擦等高频事件
- IMU 擅长表达动态运动与加速度变化
- pressure 擅长表达法向受力与接触强度

这些模态是互补的，不应该各自为战。

## 3. 这篇为什么重要

过去很多 tactile learning 工作，默认“触觉 = 类 GelSight 的图像”。这确实推动了很多任务，但也留下一个隐含瓶颈：

`只看 elastomer 形变图像，很多接触动态信息其实是缺失的。`

比如：

- 接触刚发生或刚脱离时，高频振动信号往往比图像更敏感
- 打滑、摩擦、冲击这类事件，音频和 IMU 常常更直接
- 法向受力大小，pressure 往往比纯视觉重建更稳
- 真实操作里的“是否卡住 / 是否对齐 / 是否要掉”，本质上都依赖多种触觉线索联合判断

所以这篇论文的重要性在于，它把研究问题从：

- `如何从 tactile image 学表示`

推进到：

- `如何从多模态 touch 学一个可迁移、可用于 policy learning 的统一表示`

这一步对灵巧操作非常关键。

## 4. 论文的核心贡献

作者的贡献可以概括成三件事：

1. 提出 `Sparsh-X`，第一个面向 `image/audio/motion/pressure` 四模态统一触觉表征的 backbone。
2. 构建基于 `Digit 360` 的大规模多模态触觉预训练数据，约 `18.6` 小时、约 `1M` 样本、来自 `6` 个传感器。
3. 证明这种表示不只在 benchmark 上好看，而且能显著帮助真实机器人策略学习，包括 `插头插入` 和 `手内旋转`。

我觉得第三点尤其重要，因为很多 representation paper 最后停在分类精度，但这篇是明确往 manipulation policy 里走了一步。

## 5. 方法主线

整篇论文可以压缩成下面这条主线：

1. 采集大规模无标注多模态触觉序列
2. 训练 `Sparsh-X` 做自监督多模态表征学习
3. 冻结 encoder，只训练小型 decoder / policy 头
4. 在物理属性理解和真实操作任务上验证表征质量

这里有两个设计选择很关键：

- 作者主要评估 `frozen representations`
- 作者强调 `multisensory fusion + pretraining` 两者缺一不可

这意味着他们想回答的不是“这个大模型能不能把任务刷高”，而是更基础的问题：

`预训练得到的触觉表示本身，到底有没有把对操作有用的物理属性编码进去？`

## 6. Sparsh-X 架构怎么理解

Sparsh-X 是一个 transformer backbone，但不是把所有 token 粗暴拼一起做全注意力，而是分两阶段：

1. 前半段先做各模态内部建模
2. 后半段再通过 bottleneck token 做跨模态融合

论文里的具体配置是：

- 总层数 `L = 12`
- 其中 `Lf = 8` 层做 unimodal processing
- `Lb = 4` 层做 fusion
- 每层使用 `B = 4` 个 bottleneck tokens

这个设计的直觉很清楚：

- 每种模态先各自提炼本模态时序/空间特征
- 再通过少量共享 bottleneck 汇总跨模态信息
- 比直接把全部 token 拼起来做全连接 attention 更省算力，也更有结构先验

可以把 bottleneck token 理解成：

`少量“跨模态摘要槽位”，专门负责在图像、音频、IMU、压力之间交换信息。`

## 7. 四种输入模态是怎么处理的

这篇论文有价值的一点，是它没有停留在概念层，而是把四种模态如何对齐、切窗、tokenize 说得比较具体。

### 7.1 Tactile Image

- 采样频率 `30 fps`
- 用时间步长为 `5` 的两帧图像沿 channel 维拼接
- 图像裁剪并缩放到 `224 x 224`
- patch size 为 `16 x 16`

这里的关键不只是“用图片”，而是保留短时变化，让模型看到接触斑块如何变化。

### 7.2 Audio

- 来自两个 contact microphones
- 采样率 `48 kHz`
- 使用约 `0.55 s` 窗口
- 转为 `log-mel spectrogram`
- 两个麦克风谱图拼接成 `224 x 256`

这部分特别重要，因为它让模型直接获得高频振动信息。接触建立、摩擦、轻碰撞，这些 often 在音频域最清楚。

### 7.3 IMU

- 3 轴加速度
- 采样率 `400 Hz`
- 窗口约 `0.55 s`

IMU 提供的是一种“接触中的动态身体感”，对滑动、冲击、抖动很有帮助。

### 7.4 Pressure

- 采样率 `200 Hz`
- 窗口约 `1.1 s`

pressure 是最直接的法向受力线索之一，也是这篇论文能把 force estimation 做好的关键原因之一。

## 8. 为什么这种多模态设计是合理的

如果我们从“操作里需要什么信息”来反推，Sparsh-X 的模态组合其实很自然：

- `image` 回答“接触形状和位置怎样”
- `audio` 回答“有没有瞬时事件发生”
- `IMU` 回答“当前动态变化怎样”
- `pressure` 回答“压得多重、受力多大”

单一模态常常只能看到其中一部分。

这也是为什么论文里 repeatedly 强调：

`physical properties useful for manipulation` 不是单一信号能完整表达的。

## 9. 自监督预训练怎么做

作者使用的是 teacher-student self-distillation 路线，风格接近 `DINO / DINOv2` 这一类。

训练过程大意是：

1. 各模态 token 化
2. 加 register token 和 positional embedding
3. 对 student 输入做不同强度 masking
4. teacher 输出作为 pseudo-label
5. 用 clustering + cross-entropy 做蒸馏训练

几个关键点：

- `local masks` 只保留 `10%-50%` 信号
- `global masks` 保留 `50%-100%` 信号
- 训练 `200 epochs`
- 用 `16 x A100`
- batch size `128`
- optimizer 是 `AdamW`

这个预训练设计背后的核心思想是：

`让模型在严重缺失、局部缺失、全局缺失的多模态触觉输入下，仍然学会恢复和对齐接触语义。`

对真实机器人非常有意义，因为真实触觉天生就有噪声、异步和部分信息缺失。

## 10. 预训练数据集值不值得重视

很值得。

论文的 SSL 数据来自两个平台：

1. 带 `Digit 360` 的 `Allegro hand`
2. 带同类传感器的 `mobile picker`

总计：

- `18.6` 小时
- `约 1M` 样本
- `6` 个不同 Digit 360 设备

数据来源分两类：

- Allegro hand 在装有 LEGO 和弹珠的 tray 里随机 rummage
- picker 执行 tap、slide、pick、place、drop 等原子操作

这点很关键，因为它说明作者有意识地覆盖：

- 多接触
- 动态接触
- 不同表面粗糙度、硬度、摩擦
- 物体内在属性和外在接触属性

换句话说，这个数据集不是围绕单一任务采的，而是围绕“接触多样性”采的。对 representation learning 来说，这是更对的思路。

## 11. 论文到底在测什么能力

作者围绕两个核心问题做实验：

1. `Sparsh-X 学到了哪些物理属性？`
2. `这些表征怎样真正帮助策略学习？`

这两个问题对应两大实验板块：

- 物理属性理解 benchmark
- manipulation policy learning

这个评估设计是合理的，因为它分别测：

- 表征本身有没有内容
- 表征能不能转化成操作收益

## 12. 物理属性理解部分怎么看

### 12.1 Object-Action-Surface Classification

任务是联合识别：

- 抓的是哪种物体
- 做的是哪种动作
- 接触的是哪种外部表面

这不是普通分类，它实际上在逼模型同时理解：

- 物体 intrinsic property
- 接触表面 extrinsic property
- 动作动态模式

结果上，多模态明显优于单模态。

论文给出的几个关键信息是：

- `audio + IMU` 相比更弱配置能带来明显提升
- `all modalities` 相比 `image only` 约有 `13%` 提升
- 低数据量下，预训练表示相比端到端从头学优势更明显

我的理解是，这个任务本质上在验证：

`Sparsh-X 是否把“我碰到了什么、怎么碰、在什么表面上碰”统一编码到了同一个 latent 里。`

答案基本是肯定的。

### 12.2 Material-Quantity Estimation

这个实验非常有意思。

作者让带 Digit 360 的夹爪去摇晃瓶子，识别：

- 材料种类
- 填充量

其中材料包括：

- solids：`corn kernels / lentils / vitamin pills / rice`
- liquids：`water / oil`

填充量有：

- `full / half / quarter`

这项任务对“纯 tactile image”其实并不友好，因为很多关键线索来自：

- 晃动时的内部撞击声音
- 振动频率与阻尼
- 质量分布变化

所以多模态优势非常自然。

论文结果是：

- `Sparsh-X(all modalities)` 在所有训练预算下都最好
- 相比 `E2E(image only)`，准确率提升约 `20.5%`
- 附录里在 `33%` 标注数据下给出 `87.5% vs 68.8%` 的混淆矩阵对比

这是全文里我觉得最有说服力的 benchmark 之一，因为它非常符合“Beyond Pixels”这个题目。

### 12.3 Normal Force Estimation

这里作者用半球探针按压 Digit 360，估计法向力。

结果：

- 全模态误差约 `35 mN`
- 相比 `image only` 提升约 `17%`

这个实验的意义在于，它证明：

`pressure 和其他模态的联合表示，确实在力感知上比只看 elastomer 图像更有优势。`

这并不意外，但作者把它用统一 backbone 做出来了，这点很重要。

## 13. Policy Learning 部分是全文最关键的落地价值

如果只看 representation benchmark，这篇已经不错；但真正让它更上一层的是后面的 policy experiments。

作者做了两个方向：

1. `plug insertion via imitation learning`
2. `in-hand rotation via sim-to-real tactile adaptation`

这两个任务选得也很好：

- 插入任务考验细粒度接触对齐
- 手内旋转考验持续接触稳定性与 slip 恢复

一个偏“精确对位”，一个偏“持续接触控制”。

## 14. 插头插入实验怎么理解

任务设定是：

- Allegro hand 预抓住插头
- 机器人把插头插进固定插座
- 收集 `100` 条 kinesthetic teleoperation demonstrations
- 输入包括 wrist camera、关节/腕部状态、以及三个手指的触觉表示

policy 架构借鉴 `ACT`，输出长度为 `H = 8` 的末端执行器位姿序列。

这个任务非常适合检验触觉是否真的有用，因为：

- 视觉会有 aliasing
- 插孔容差紧
- 最后那一点点对齐往往靠接触而不是靠看

结果很强：

- `vision only` 很差
- `Sparsh-X + all modalities` 成功率达到 `90%`
- 相比 `end-to-end tactile image only policy` 提升 `63%`
- 相比只用外部视觉，论文图中给到 `500%` 的提升量级

我对这一节的理解是：

`多模态 touch 在插入任务里的价值，不是提供更多“冗余信息”，而是提供视觉无法可靠给出的最后一毫米接触判别。`

尤其是：

- audio 能提示初始碰撞或触碰
- image 和 pressure 能提示法向/剪切接触变化
- 多模态融合让策略更容易判断“该继续压、该调整、还是已经偏了”

## 15. 一个很诚实、也很重要的细节

论文提到，在插入任务上：

- 对 `image only` 来说，`end-to-end` 竟然比 `frozen pretrained representations` 更好

这是个非常值得注意的结果。

它说明：

1. 预训练表示并不总是无条件优于任务特化 encoder
2. 当任务分布很窄、接触图像变化很细微时，专门为该任务优化的图像编码器可能更敏感
3. 但一旦加入其他模态，Sparsh-X 的整体优势就重新体现出来

我反而觉得这让论文更可信，因为作者没有把结果讲成“预训练万能论”。

## 16. 手内旋转实验为什么更有意思

第二个实验其实更有研究味道。

作者基于 `Hora` 这类 sim 中用 privileged information 训练的手内旋转策略，问了一个很好的问题：

`既然真实世界里现在有丰富触觉了，能不能把这些触觉用于“补回”仿真里那些特权信息，从而让 real-world policy 更接近 privileged setting？`

这就是论文的 `tactile adaptation` 思路。

## 17. Tactile Adaptation 是怎么做的

作者用的是 `ControlNet` 风格的连接方式：

- 冻结原始 base policy
- 训练一个 tactile adaptation module
- 通过 `zero-initialized convolution` 把触觉信息渐进式注入原策略

输入是：

- 四个手指过去 `1.5s` 的 Sparsh-X 表示
- 与 Hora 原本使用的 proprioceptive history 对齐

训练目标也很克制：

- 不是直接全盘重训策略
- 而是让 tactile adaptation module 去逼近带 tactile 信息的 privileged latent 修正

这个设计很漂亮，因为它尽量保证：

- 原始 policy 不会被轻易破坏
- 触觉只作为稳定增量进入

## 18. 手内旋转结果说明了什么

结果最关键的一句是：

`Sparsh-X tactile adaptation 将 vertical drift 降低了 90%。`

此外：

- 在降低摩擦时，`all modalities` 版本最稳
- 在增加物体质量时，带 tactile adaptation 的策略能更好适应
- 它优于只做 finetune 的 Hora，也优于 proprio-only imitation baseline

这说明什么？

说明真正起作用的不是“又多收了点成功数据”，而是：

`触觉表示真的提供了和 slip、摩擦、质量变化有关的状态信息。`

而这些信息，恰恰就是手内操作最需要、但纯 proprioception 最难稳定恢复的部分。

## 19. 这篇论文最强的地方

我认为有四点。

### 19.1 问题定义是对的

它没有把问题局限在“更好的 tactile image encoder”，而是直接挑战：

`touch is multisensory`

这个方向判断本身就很重要。

### 19.2 表征和策略打通了

很多 paper 到 benchmark 就结束了，这篇明确证明：

- 预训练表示可以进 imitation learning
- 也可以进 sim-to-real adaptation

这对后续工作很有启发。

### 19.3 评估维度比较完整

作者同时测：

- 分类
- 物质量估计
- 力估计
- 插入
- 手内旋转

所以我们更容易相信它不是某个单一任务上的巧合。

### 19.4 结论不夸张

作者承认了：

- tactile image 模态的数据多样性可能还不够
- frozen encoder 不是最终最优解
- force 实验目前只覆盖 normal force
- shear force 与复杂多接触还没解决

这种表述比较扎实。

## 20. 这篇论文的局限

论文自己提到以及我认为值得补充的局限主要有下面几类。

### 20.1 预训练数据规模仍然不算“foundation model”级别

虽然 `1M` 样本和 `18.6h` 已经不小，但和视觉 foundation model 相比仍然很早期。

更重要的是，数据多样性主要还是来自有限平台和有限类型动作，不是真正开放世界触觉。

### 20.2 tactile image 的传感器多样性偏弱

作者明确说 image modality 的设备多样性最弱，光学伪影可能限制泛化。

这会影响一个关键问题：

`Sparsh-X 究竟是在学“可迁移触觉语义”，还是部分在记住某些 Digit 360 特有成像统计特征？`

### 20.3 模态同步与实时性仍是工程瓶颈

附录里说：

- 单个 GPU `RTX 4090` 上 Sparsh-X 推理本身可到 `50 Hz`
- 但处理四个手指全模态时，端到端大约 `20 Hz`
- `log-mel spectrogram` 构建仍是主要瓶颈

这意味着如果以后要上更高控制频率、更复杂操作，音频处理链还需要优化。

### 20.4 力感知评估还比较受控

normal force estimation 是在受控按压实验里做的。

但真实操作里更难的是：

- shear force
- 多点同时接触
- 接触几何不断变化
- 软物体与非刚体

这些还没有被真正覆盖。

## 21. 对我们做灵巧手/触觉工作的启发

如果把这篇论文转成方法论，我觉得至少有五个启发。

### 21.1 不要再把 tactile 等同于图像

如果硬件允许，触觉建模应该从一开始就按多模态系统来设计，而不是 image-only 后期补丁式加传感器。

### 21.2 预训练数据采集要围绕“接触多样性”

不是只采某个任务成功 demo，而是主动覆盖：

- tapping
- sliding
- impact
- rubbing
- grasp / release
- different materials / frictions / masses / surfaces

这类数据更适合学通用 touch prior。

### 21.3 表征学习和 policy learning 不必分裂

Sparsh-X 说明：

- 表征可以先独立学
- 再以 frozen feature 方式进入 policy
- 也可以作为 adaptation module 的输入

这是很实用的模块化路线。

### 21.4 sim-to-real 里的“特权信息恢复”是很有潜力的切入点

很多 sim 里能拿到、real 里拿不到的信息，其实不一定只能靠 proprioception 去猜。

触觉可能正是最自然的桥梁。

### 21.5 未来很值得研究 modality dropout 和 task-dependent fusion

不同任务对不同模态依赖不一样：

- 插入可能更依赖 image + pressure
- 打滑检测可能更依赖 audio + IMU
- 力控制可能更依赖 pressure

所以未来完全可以进一步研究：

- task-aware fusion
- adaptive modality selection
- missing modality robustness

## 22. 我对这篇论文的总体评价

如果只看新颖性，它不是那种靠极复杂架构取胜的论文。

但如果看研究价值，我认为它非常好，因为它做对了三件事：

1. 抓住了一个真实而重要的问题定义
2. 给出结构清楚、工程上可实现的统一方案
3. 用真实操作任务证明了多模态触觉表示的价值

它未必已经是“最终答案”，但很可能代表了一个正确方向：

`未来机器人触觉基础模型，大概率不会只基于 tactile pixels，而会基于多模态触觉时序。`

## 23. 最后浓缩成几句话

如果只记住这篇论文三句话，我建议记下面这三句：

1. `Touch is not just pixels; it is inherently multisensory.`
2. `Multisensory tactile pretraining can encode manipulation-relevant physical properties.`
3. `这些表征不仅能做 benchmark，还能切实提升真实机器人策略学习和 sim-to-real adaptation。`

从这个意义上说，`Tactile Beyond Pixels` 这个标题是非常准确的。
