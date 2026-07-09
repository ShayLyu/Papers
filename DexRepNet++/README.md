# DexRepNet++ 论文精讲

论文：
- `DexRepNet++: Learning Dexterous Robotic Manipulation with Geometric and Spatial Hand-Object Representations`
- arXiv: `2602.21811v1`
- PDF: [2602.21811v1.pdf](/Users/shay/Desktop/DexHand/DexRepNet++/2602.21811v1.pdf)

## 1. 这篇论文到底在解决什么

这篇论文的核心问题不是“怎么把 PPO 调得更好”，而是：

`在灵巧手操作里，策略到底应该看见什么，才能真正泛化到新物体、新视角、甚至新手型？`

作者的判断很明确：

- 现有很多工作把重点放在 `RL 算法`、`示教数据规模`、`奖励设计` 上
- 但真正决定泛化能力的，往往是 `hand-object interaction representation`

也就是说，策略失败常常不是因为“不会学”，而是因为“输入表示本身没把接触几何和空间关系表达对”。

所以这篇论文提出了一个新的表示：

`DexRep = 几何 + 空间 + 局部接触线索 的手-物交互表示`

然后把它接到策略网络前面，去做三类典型灵巧操作任务：

- 抓取 `Grasping`
- 手内重定向 `In-Hand Reorientation`
- 双手交接 `Handover`

## 2. 一句话结论

如果只用一句话概括这篇论文：

`DexRepNet++ 的关键贡献，不是换了一个更大的策略网络，而是把“物体怎么长、手离哪里近、哪里可能接触”编码成了一个更贴近操作本质的输入表示。`

这使得策略：

- 在仿真里对 unseen objects 泛化更强
- 对 partial point cloud 更稳
- 对不同手指数量的 hand morphology 有迁移性
- 在真实世界也更容易落地

## 3. 为什么作者觉得“全局形状特征”不够

论文对很多现有做法的批评很到位。

常见输入大概有三类：

- 机器人本体状态：关节角、速度、末端位姿
- 物体全局几何编码：比如 PointNet 提取的 global feature
- 粗糙的 hand-object 相对位置

这些表示的问题是：

- 它们经常更像“识别这个物体是什么”，而不是“告诉你该怎么接触它”
- 对物体姿态、尺度、遮挡、全局外形变化很敏感
- 很难把“哪个局部结构适合抓、手指现在离接触面多近、接触法向是什么”直接交给策略

作者的观点可以概括成一句话：

`灵巧操作真正依赖的不是整个物体的全局外观，而是局部可接触几何和手-物空间关系。`

比如：

- 两个杯子的整体形状可能差很多，但把手局部几何很像
- 两把工具的主体不同，但边缘、柄部、凸起等局部区域可以复用相近策略

这就是 DexRep 的出发点。

## 4. DexRep 的核心设计

DexRep 由三部分组成：

1. `Occupancy Feature`
2. `Surface Feature`
3. `Local-Geo Feature`

三者分别回答三个不同问题。

### 4.1 Occupancy Feature：物体在手周围“占了哪些空间”

作者以手的一个锚点为中心，建立局部 voxel grid，判断每个体素是否被物体占据。

它提供的是：

- 粗粒度空间布局
- 手附近哪里有东西
- 大致碰撞/对齐关系

你可以把它理解成：

`手周围的局部三维占据地图`

它的优点是：

- 直观
- 抗噪
- 对局部空间结构表达稳定

它更像是“全局但局部化”的空间提示。

### 4.2 Surface Feature：手指关键点离物体表面有多远、法向朝哪边

作者在手上预定义若干关键点。对每个关键点，去找物体上最近的点，并提取：

- 距离
- 物体表面法向

它编码的是：

- 当前手和物体的相对接近程度
- 潜在接触是否合理
- 接触表面的朝向

这是非常“接触驱动”的表示，因为灵巧操作很多时候就是在控制：

- 哪根手指先接近
- 以什么方向接近
- 接触建立后怎么稳定

### 4.3 Local-Geo Feature：接触附近那一小块几何长什么样

这是最“学习型”的部分。

作者先用 PointNet 对物体点云做预训练编码；然后对每个手部关键点，找到最近的物体点，取该点对应的局部几何特征。

它想补足的是：

- Occupancy 太粗
- Surface Feature 维度低、表达力有限

Local-Geo 负责描述：

- 该接触区域附近的精细局部几何
- 例如边缘、曲面、把手、薄片、突起等细节

这部分是论文里最重要的“泛化来源”之一。

## 5. 三个特征合起来，各自分工是什么

这是这篇论文最好理解的方式：

- `Occupancy` 负责“哪里有东西”
- `Surface` 负责“离得多近、朝向如何”
- `Local-Geo` 负责“接触附近几何细节是什么”

所以 DexRep 不是单一特征，而是一个分层表示：

- 粗空间布局
- 中等粒度接触关系
- 细粒度局部几何

这也是为什么它比只用 `robot state` 或 `global PointNet feature` 更强。

## 6. 策略网络怎么吃 DexRep

作者不是把所有输入一股脑拼起来，而是做了模块化编码。

大致流程是：

1. 先计算机器人 proprioception `f_prop`
2. 计算 DexRep 三部分特征 `f_o / f_s / f_l`
3. 每一部分先过各自的全连接层
4. Local-Geo 因为幅值变化更大，先做 batch normalization
5. 最后把这些 embedding 拼接起来喂给 MLP policy

对于双手任务，还会给第二只手也算一套特征，再拼进去。

这套设计说明作者并不认为：

`“有了好表示，网络就随便接”`

相反，他们意识到不同特征的数值尺度、语义作用都不同，所以做了显式分流编码。

## 7. 三个任务分别怎么训练

### 7.1 Grasping：先 BC，再 RL

抓取任务中，作者先用 GRAB 人类示教数据做 retargeting，把人手轨迹转成 Adroit hand 的演示，再做：

- `Behavior Cloning` 预训练
- `DAPG` 微调

这是因为抓取任务有比较好的示教来源，直接 warm start 更稳。

### 7.2 In-Hand Reorientation：从零开始 RL

手内重定向没有依赖示教 warm start，而是直接从随机初始化开始学。

### 7.3 Handover：同样从零开始 RL

双手交接任务也是直接 RL，从而验证 DexRep 在双手协同场景里的可用性。

所以整篇论文不是在证明“示教很强”，而是在证明：

`无论有没有 demonstrations，这个表示都能帮策略学得更快更稳。`

## 8. 这篇论文的实验设计很完整

它不只是做一个主表，而是围绕“表示是否真的有效”做了多维验证：

- 主任务效果
- 训练收敛速度
- 统计显著性
- partial point cloud 鲁棒性
- 预训练数据规模影响
- hand morphology 变化
- friction 和超参数敏感性
- sim-to-real

这让论文说服力比“只做 benchmark 刷分”强很多。

## 9. 关键结果一：抓取任务非常强

### 9.1 MuJoCo 抓取

论文 Table I 给出的抓取成功率：

- `DAPG`: seen `36.3±8.2`, unseen `21.5±12.3`
- `ILAD`: seen `64.8±3.3`, unseen `22.6±3.1`
- `Ours`: seen `96.5±0.9`, unseen `88.1±2.0`

这个结果非常夸张，因为 unseen 提升不是几个点，而是直接大幅拉开。

### 9.2 Isaac Gym 抓取

同样在 Isaac Gym 中：

- `DAPG`: seen `21.0`, unseen `12.5`
- `ILAD`: seen `32.0`, unseen `24.5`
- `IBS`: seen `57.0`, unseen `54.0`
- `UniDexGrasp`: seen `79.0`, unseen `72.5`
- `UniDexGrasp++`: seen `85.4`, unseen `78.2`
- `Ours`: seen `96.5`, unseen `96.4`

这说明 DexRep 的收益并不局限于某个模拟器。

### 9.3 为什么这个结果重要

作者强调：

- 训练只用了 `40` 个训练物体
- 测试却在 `5355` 个 unseen 形状上评估

也就是说，这不是靠“记住很多训练对象”取胜，而是真在学可泛化的 interaction prior。

## 10. 关键结果二：手内重定向和双手交接也成立

Table II 的 unseen 结果：

### In-Hand Reorientation

- `Base`: `50.1±6.2`
- `GeoDex`: `76.3±3.0`
- `GeoDex-50k`: `81.1±1.5`
- `Ours`: `86.0±3.9`

### Handover

- `Base`: `36.8±2.9`
- `Ours-Throw`: `60.0±1.2`
- `Ours-Catch`: `72.1±3.8`
- `Ours-Dual`: `77.3±1.9`

这两个结果很关键，因为它们说明 DexRep 不是“只对 grasping 有用”的特化设计，而是：

`对不同接触模式、不同时序结构、不同控制难度的灵巧任务都有收益。`

尤其 handover 里：

- 只给 throw hand 用 DexRep 有提升
- 只给 catch hand 用 DexRep 提升更大
- 双手都用时最好

这很符合直觉：接住物体这一侧更依赖局部空间和接触几何。

## 11. 关键结果三：DexRep 学得更快

论文在训练曲线里反复强调一件事：

`DexRep 不只是最终分数更高，收敛也更快。`

作者给出的一个很直观的观察是：

- 在 grasping 中，DexRep 大约 `600 iterations` 已基本收敛
- 到 `iteration 200` 左右，全局 PointNet 特征的成功率还接近 `0`
- 而 DexRep 已经达到约 `60%`

这说明好表示的价值不只是 benchmark 漂亮，而是：

- 更省样本
- 更省算力
- 更容易训练稳定

这在灵巧手任务里非常重要，因为接触动力学本来就难学。

## 12. 关键结果四：partial point cloud 下依然很稳

这是我认为这篇论文最实用的部分之一。

很多仿真工作默认用完整点云，但现实里常见的是：

- 单相机
- 遮挡严重
- 点云缺失
- 法向估计有噪声

作者专门模拟了：

- 第一视角 partial point cloud `Ours-Part-1st`
- 第三视角 partial point cloud `Ours-Part-3rd`
- 完整点云 `Ours-Full`

真实世界 Table VIII 的平均成功率：

- `pGlo-Part-1st`: `16.7`
- `pGlo-Part-3rd`: `24.2`
- `pGlo-Full`: `26.7`
- `Ours-Part-1st`: `65.8`
- `Ours-Part-3rd`: `70.0`
- `Ours-Full`: `85.0`

如果再加 teacher-student distillation：

- `Distilled Ours-Part-1st`: `76.7`
- `Distilled Ours-Part-3rd`: `79.2`

这说明两件事：

1. DexRep 在部分观测下仍然能工作，不会一下子崩掉
2. 完整点云教师策略还能进一步蒸馏给 partial 输入策略

这个结果离真实部署非常近。

## 13. 关键结果五：真实世界成绩也很强

### 13.1 已知 CAD 模型

Table VII 平均成功率：

- `Hand2obj-CAD`: `27.7`
- `pGlo-CAD`: `61.7`
- `Ours-CAD`: `82.5`

说明即便在已知 CAD、可以做配准的情况下，DexRep 也明显强于基线。

### 13.2 与 full/partial real-world 设置结合

上面 Table VIII 已经看到：

- `Ours-Full` 平均 `85.0`
- `Ours-Part-3rd` 平均 `70.0`
- 蒸馏后 partial 还能到 `79.2`

这个结果已经很像“可以拿去做真实抓取系统”的强度了。

## 14. 关键结果六：对不同 hand morphology 有迁移性

作者做了一个很有意思的实验：

- 从五指手上拆掉部分手指
- 构造 `2-finger / 3-finger / 4-finger` 的不同手型
- 看表示能不能迁移

结果里，DexRep 在 unseen objects 上分别达到：

- `2-finger`: `65.4%`
- `3-finger`: `78.2%`
- `4-finger`: `81.5%`

这说明 DexRep 编码的主要是：

- 局部几何
- 手-物空间结构

而不是某一只手专属的 motor pattern。

这是它很有潜力往 cross-embodiment 方向走的一点。

## 15. 关键结果七：训练物体数量不是越多越无限涨

作者在 Isaac Gym 里把训练物体数量从：

- `20`
- `40`
- `200`
- `500`
- `900`

一路加上去。

结论是：

- 训练物体越多，泛化确实更强
- 但超过 `200` 之后，收益开始明显递减

这个发现很有价值，因为它告诉我们：

`好的表示可以减少“靠海量对象堆出来”的依赖。`

也就是说，DexRep 并不是只能靠数据量吃红利，它本身就在提高样本效率。

## 16. 消融实验告诉我们什么

### 16.1 单个特征都不如三者组合

论文比较了：

- 只用 `Hand2obj`
- 只用 global PointNet `pGlo`
- 只用 `Surf`
- 只用 `Occ`
- 只用 `LGeo`
- 两两组合
- `DexRep + pGlo`
- 完整 `DexRep`

结论很清楚：

- 单独特征有帮助，但不够
- 两两组合更好
- 完整 `Occ + Surf + LGeo` 最强
- 再加 global PointNet，收益并不明显，甚至不一定值得

这说明作者的设计不是“拍脑袋叠模块”，而是三个分量真的互补。

### 16.2 Local geometry 比 global embedding 更关键

论文做 t-SNE 分析后指出：

- global feature 相似的物体，抓取成功率可能差很多
- 例如外观整体像，但局部厚度、边缘、接触区域细节不同

所以：

`能决定操作成败的，往往不是“物体像不像”，而是“接触局部长得像不像”。`

这正是 DexRep 优于纯 global feature 的根本原因。

## 17. 超参数经验非常实用

作者专门消融了两个关键几何超参数：

- voxel edge length `l_v`
- maximum perception distance `δ_max`

给出的经验结论很实用：

- 通用任务里，`l_v` 取 `0.01m ~ 0.02m` 比较合适
- `δ_max` 取 `0.1m` 左右比较稳
- 对精细手内操作，更推荐 `l_v = 0.01m`, `δ_max = 0.1m`

从表里看：

- grasping 最佳组合能到 `96.4`
- reorientation 最佳是 `86.0`
- handover 最佳是 `77.3`

作者还解释了原因：

- `δ_max` 太大，会让稀有的大距离值增多，学习变难
- `l_v` 太大，会让 occupancy 过粗，尤其不利于 handover 的姿态编码

这部分很像“工程指导手册”，对复现很有帮助。

## 18. 这篇论文最值得学的思想

### 18.1 表示要服务于接触，而不是服务于识别

这篇论文最有启发性的地方，是把操作表示和视觉识别表示分开看。

很多工作默认：

`只要把物体 encode 好，策略就能自己学会接触。`

DexRepNet++ 的观点是：

`操作不等于识别。`

机器人不一定需要最好的 object identity embedding，它更需要：

- 哪里能接触
- 怎么接触
- 接触附近几何长什么样

### 18.2 “局部几何复用”是泛化的关键

这篇论文本质上在押一个假设：

`不同物体之间，可复用的不是完整形状，而是局部交互模式。`

我认为这个判断是对的，而且很适合灵巧手。

### 18.3 好表示能直接提升 RL 的可学性

DexRep 不是只提升最终分数，它还提升：

- 收敛速度
- 稳定性
- seed 间方差

这说明 representation learning 在机器人 RL 里不是配角，而是主角之一。

## 19. 这篇论文的局限

论文很强，但也不是没有边界。

### 19.1 仍然依赖点云质量

尽管 partial point cloud 实验已经不错，但 DexRep 还是建立在：

- 点云可获得
- 法向可估计
- 关键点到表面的最近邻关系可计算

如果场景透明、反光、极端遮挡，效果仍可能受影响。

### 19.2 Local-Geo 仍需要预训练编码器

Local-Geo 不是完全手工几何，它依赖一个预训练 PointNet 编码器。  
这意味着：

- 预训练数据质量会影响下游表现
- 编码器本身仍可能带来 domain gap

### 19.3 对复杂动态对象和非刚体的验证还不够

本文重点还是刚体对象的 dexterous manipulation。  
如果对象是：

- 柔性
- 可变形
- 有明显关节

DexRep 这套局部几何表示是否仍然足够，需要更多验证。

## 20. 如果你要复现，这篇论文最该抓住什么

如果从工程角度复现，我建议优先抓住这 5 件事：

1. `手部关键点设计`
   DexRep 的很多信息都围绕 hand keypoints 展开，这部分不能随便改。

2. `局部而不是全局`
   重点不是把物体整个编码得更大更强，而是把接触附近编码清楚。

3. `Occ + Surf + LGeo 三者协同`
   不要只复现其中一个模块然后期待接近原文结果。

4. `grasping 的 BC warm-start`
   这对训练稳定性很重要。

5. `partial point cloud 路线很值得单独做`
   如果目标是真机部署，这部分甚至比 full point cloud 主结果更重要。

## 21. 我对这篇论文的总体评价

我会把它看成一篇：

`把“灵巧操作的泛化”从算法问题，重新拉回表示问题的论文。`

它最强的地方不只是分数高，而是逻辑完整：

- 为什么现有表示不够
- 为什么要看局部几何和空间关系
- 为什么三种特征能互补
- 为什么这会带来更快训练和更强泛化
- 为什么它在 partial observation 和 real-world 里仍然成立

如果你正在做：

- dexterous grasping
- in-hand manipulation
- hand-object representation learning
- sim2real 的点云输入策略

这篇论文非常值得细读。

## 22. 最后的高频问题

### Q1：DexRepNet++ 真正的新东西是什么？

不是单纯换 backbone，而是提出了 `DexRep` 这种面向接触的表示，并系统证明它比 robot state 或 global object feature 更适合灵巧操作。

### Q2：为什么它比 PointNet 全局特征强？

因为操作决策更依赖 `局部可接触几何`，而不是 `整物体类别级语义`。

### Q3：为什么 partial point cloud 结果这么重要？

因为真实系统通常拿不到完整点云。能在 partial observation 下保持高成功率，说明这条路线更接近落地。

### Q4：这篇论文最像在补哪一类工作的短板？

最像是在补：

- 只重算法不重表示
- 只重全局形状不重局部接触
- 只在 full observation 里表现好

这些路线的短板。

## 23. 一段最短总结

`DexRepNet++ 的本质，是把“手怎么接近物体、接触哪里、局部几何长什么样”编码成策略真正有用的输入。`

相比只看 robot state 或 global object embedding，这种表示更适合灵巧操作，因此带来了：

- 更强的 unseen object 泛化
- 更好的 sample efficiency
- 更强的 partial point cloud 鲁棒性
- 更可信的 sim-to-real 潜力

