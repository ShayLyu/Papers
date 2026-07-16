# 论文阅读库

本仓库收录机器人学习、灵巧操作、触觉感知与世界模型方向的论文。当前共整理 **57 篇 PDF**，按论文的主要研究问题归入 8 个领域；交叉方向以标签补充说明。

## 使用说明

- **PDF**：仓库中的论文原文。
- **arXiv**：唯一保留的外部链接类型；编号来自本地文件名。
- **PDF**：使用仓库内相对路径跳转。
- 同一论文只在一个主领域中列出，以便检索和维护。

## 目录

- [综述](#综述)
- [视觉-语言-动作模型与机器人基础模型](#视觉-语言-动作模型与机器人基础模型)
- [跨本体灵巧抓取与统一表征](#跨本体灵巧抓取与统一表征)
- [触觉与视触觉感知及操作](#触觉与视触觉感知及操作)
- [示教、遥操作、重定向与数据采集](#示教遥操作重定向与数据采集)
- [灵巧操作策略学习与控制](#灵巧操作策略学习与控制)
- [世界模型与模型式强化学习](#世界模型与模型式强化学习)
- [通用三维感知](#通用三维感知)

## 综述

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| Dexterous Manipulation through Imitation Learning: A Survey | 灵巧操作与模仿学习 | [PDF](Survey2025_1/2504.03515v5.pdf) · [arXiv](https://arxiv.org/abs/2504.03515) |
| Towards Robotic Dexterous Hand Intelligence: A Survey | 灵巧手硬件、感知、学习与评测 | [PDF](Survey2026_1/2605.13925v2.pdf) · [arXiv](https://arxiv.org/abs/2605.13925) |
| Understanding World or Predicting Future? A Comprehensive Survey of World Models | 通用世界模型综述 | [PDF](WorldModel/Survey/2411.14499v4.pdf) · [arXiv](https://arxiv.org/abs/2411.14499) |
| World Model for Robot Learning: A Comprehensive Survey | 面向机器人学习的世界模型 | [PDF](WorldModel/Survey/2605.00080v1.pdf) · [arXiv](https://arxiv.org/abs/2605.00080) |

## 视觉-语言-动作模型与机器人基础模型

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| Being-H0: Vision-Language-Action Pretraining from Large-Scale Human Videos | 人类视频预训练、VLA | [PDF](BeingH0/2507.15597v1.pdf) · [arXiv](https://arxiv.org/abs/2507.15597) |
| Cross-Hand Latent Representation for Vision-Language-Action Models | 多种灵巧手的共享动作表征 | [PDF](<Cross-Hand Latent Representation for Vision-Language-Action Models/2603.10158v1.pdf>) · [arXiv](https://arxiv.org/abs/2603.10158) |
| MLA: A Multisensory Language-Action Model for Multimodal Understanding and Forecasting in Robotic Manipulation | 多感官语言-动作建模 | [PDF](MLA/2509.26642v2.pdf) · [arXiv](https://arxiv.org/abs/2509.26642) |
| One-Policy-Fits-All: Geometry-Aware Action Latents for Cross-Embodiment Manipulation | 几何感知动作潜变量、跨本体策略 | [PDF](One-Policy-Fits-All/2603.14522v1.pdf) · [arXiv](https://arxiv.org/abs/2603.14522) |
| Latent Action Diffusion for Cross-Embodiment Manipulation | 共享潜在动作空间、扩散策略 | [PDF](paper/2506.14608v4.pdf) · [arXiv](https://arxiv.org/abs/2506.14608) |
| EgoVLA: Learning Vision-Language-Action Models from Egocentric Human Videos | 第一视角人类视频、VLA | [PDF](paper/2507.12440v3.pdf) · [arXiv](https://arxiv.org/abs/2507.12440) |
| HumDex: Humanoid Dexterous Manipulation Made Easy | 人形机器人灵巧操作与遥操作 | [PDF](paper/2603.12260v2.pdf) · [arXiv](https://arxiv.org/abs/2603.12260) |
| UniDex: A Robot Foundation Suite for Universal Dexterous Hand Control from Egocentric Human Videos | 通用灵巧手基础模型、人类视频 | [PDF](UniDex2026/UniDex_Arxiv.pdf) |
| π0: A Vision-Language-Action Flow Model for General Robot Control | 通用机器人 VLA、流模型 | [PDF](pi/pi0.pdf) |
| π0.5: A Vision-Language-Action Model with Open-World Generalization | 开放世界泛化 | [PDF](pi/pi05.pdf) |
| π0.7: A Steerable Generalist Robotic Foundation Model with Emergent Capabilities | 可控通用机器人基础模型 | [PDF](pi/pi07.pdf) |
| π*0.6: A VLA That Learns From Experience | 从经验持续改进的 VLA | [PDF](pi/pistar06.pdf) |

## 跨本体灵巧抓取与统一表征

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| CEDex: Cross-Embodiment Dexterous Grasp Generation at Scale from Human-like Contact Representations | 人形接触表征、规模化抓取生成 | [PDF](CEDex/2509.24661v1.pdf) · [arXiv](https://arxiv.org/abs/2509.24661) |
| Cross-Embodiment Dexterous Grasping with Reinforcement Learning (CrossDex) | 跨本体强化学习抓取 | [PDF](<CrossDex(code1)/2410.02479v1.pdf>) · [arXiv](https://arxiv.org/abs/2410.02479) |
| D(R, O) Grasp: A Unified Representation of Robot and Object Interaction for Cross-Embodiment Dexterous Grasping | 机器人-物体统一交互表征 | [PDF](<D(R,o)/2410.01702v4.pdf>) · [arXiv](https://arxiv.org/abs/2410.01702) |
| DemoGrasp: Universal Dexterous Grasping from a Single Demonstration | 单次示范、通用抓取 | [PDF](Demograsp/2509.22149v1.pdf) · [arXiv](https://arxiv.org/abs/2509.22149) |
| GraspGraphNet: Graph-Structured Multi-Embodiment Dexterous Grasp Generation | 图结构、多本体抓取生成 | [PDF](GraspGraphNet/2607.11031v1.pdf) · [arXiv](https://arxiv.org/abs/2607.11031) |
| One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation | 规范手表征、零样本形态泛化 | [PDF](OHRA/2602.16712v2.pdf) · [arXiv](https://arxiv.org/abs/2602.16712) |
| T(R,O)Grasp: Efficient Graph Diffusion of Robot-Object Spatial Transformation for Cross-Embodiment Dexterous Grasping | 空间变换图扩散 | [PDF](<T(R,O)/2510.12724v1.pdf>) · [arXiv](https://arxiv.org/abs/2510.12724) |
| UniDexGrasp++: Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning | 几何课程学习、通才-专家迭代 | [PDF](UniDexGrasp++/2304.00464v2.pdf) · [arXiv](https://arxiv.org/abs/2304.00464) |
| UniMorphGrasp: Diffusion Model with Morphology-Awareness for Cross-Embodiment Dexterous Grasp Generation | 形态感知扩散抓取 | [PDF](UniMorphGrasp/2602.00915v1.pdf) · [arXiv](https://arxiv.org/abs/2602.00915) |

## 触觉与视触觉感知及操作

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| DexMove: Learning Tactile-Guided Non-Prehensile Manipulation with Dexterous Hands | 触觉引导的非抓持操作 | [PDF](DexMove/829_DexMove_Learning_Tactile_G.pdf) |
| DexSkin: High-Coverage Conformable Robotic Skin for Learning Contact-Rich Manipulation | 高覆盖柔性机器人皮肤 | [PDF](DexSkin/510_DexSkin_High_Coverage_Conf.pdf) |
| FBI: Learning Dexterous In-hand Manipulation with Dynamic Visuotactile Shortcut Policy | 动态视触觉模仿学习 | [PDF](FBI/2508.14441v1.pdf) · [arXiv](https://arxiv.org/abs/2508.14441) |
| KineDex: Learning Tactile-Informed Visuomotor Policies via Kinesthetic Teaching for Dexterous Manipulation | 动觉示教、触觉知情视觉运动策略 | [PDF](KineDex/478_KineDex_Learning_Tactile_I.pdf) |
| Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation | 快慢双系统、视触觉扩散策略 | [PDF](RDP/2503.02881v3.pdf) · [arXiv](https://arxiv.org/abs/2503.02881) |
| Robot Synesthesia: In-Hand Manipulation with Visuotactile Sensing | 视触觉物体旋转 | [PDF](RobotSynesthesia2024/2312.01853v3.pdf) · [arXiv](https://arxiv.org/abs/2312.01853) |
| Tactile Beyond Pixels: Multisensory Touch Representations for Robot Manipulation | 多传感器触觉表征 | [PDF](TactileBeyondPixels/661_Tactile_Beyond_Pixels_Mult.pdf) |
| Text2Touch: Tactile In-Hand Manipulation with LLM-Designed Reward Functions | LLM 奖励设计、触觉手内操作 | [PDF](<Text2Touch(code 1)/2509.07445v1.pdf>) · [arXiv](https://arxiv.org/abs/2509.07445) |
| T-Rex: Tactile-Reactive Dexterous Manipulation | 触觉反应式灵巧操作 | [PDF](T-Rex/2606.17055v1.pdf) · [arXiv](https://arxiv.org/abs/2606.17055) |
| Vision-Free Object 6D Pose Estimation for In-Hand Manipulation via Multi-Modal Haptic Attention | 无视觉、多模态触觉 6D 位姿估计 | [PDF](<Vision-Free Object 6D Pose Estimation for In-Hand Manipulation via Multi-Modal Haptic Attention/11_Vision_Free_Object_6D_Pose_.pdf>) |
| Visuo-Tactile Object Pose Estimation for a Multi-Finger Robot Hand with Low-Resolution In-Hand Tactile Sensing | 低分辨率触觉、物体位姿估计 | [PDF](<Visuo-Tactile Object Pose Estimation for a Multi-Finger Robot Hand with Low-Resolution In-Hand Tactile Sensing/2503.19893v1.pdf>) · [arXiv](https://arxiv.org/abs/2503.19893) |
| ViTacFormer: Learning Cross-Modal Representation for Visuo-Tactile Dexterous Manipulation | 跨模态视触觉表征 | [PDF](ViTacFormer/2506.15953v2.pdf) · [arXiv](https://arxiv.org/abs/2506.15953) |

## 示教、遥操作、重定向与数据采集

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| ART-Glove: Articulated Tactile Glove for Contact-Grounded Dexterous Interaction Capture | 关节式触觉手套、接触示范采集 | [PDF](ART-Glove/2606.16370v1.pdf) · [arXiv](https://arxiv.org/abs/2606.16370) |
| DexterCap: Affordable and Automated Capture of Complex Hand-Object Interactions | 手-物交互捕捉 | [PDF](DexterCap/2601.05844v2.pdf) · [arXiv](https://arxiv.org/abs/2601.05844) |
| DexUMI: Using Human Hand as the Universal Manipulation Interface for Dexterous Manipulation | 人手通用接口、数据采集与策略学习 | [PDF](DexUMI/2505.21864v3.pdf) · [arXiv](https://arxiv.org/abs/2505.21864) |
| Learning Dexterous In-Hand Manipulation with Multifingered Hands via Visuomotor Diffusion | AR 遥操作、视觉运动扩散策略 | [PDF](<Learning Dexterous In-Hand Manipulation with Multifingered Hands via Visuomotor Diffusion/2503.02587v1.pdf>) · [arXiv](https://arxiv.org/abs/2503.02587) |
| Learning Dexterous Manipulation Using Contact Wrench Guidance From Human Demonstration | 人类示范、接触力旋量引导 | [PDF](<Learning Dexterous Manipulation Using Contact Wrench Guidance From Human Demonstration/2607.00033v1.pdf>) · [arXiv](https://arxiv.org/abs/2607.00033) |
| TopoRetarget: Interaction-Preserving Retargeting for Dexterous Manipulation | 保持交互拓扑的动作重定向 | [PDF](TopoRetarget/2606.16272v2.pdf) · [arXiv](https://arxiv.org/abs/2606.16272) |

## 灵巧操作策略学习与控制

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| DexFormer: Cross-Embodied Dexterous Manipulation via History-Conditioned Transformer | 历史条件 Transformer、跨本体控制 | [PDF](DexFormer/2602.08278v1.pdf) · [arXiv](https://arxiv.org/abs/2602.08278) |
| DexPoint: Generalizable Point Cloud Reinforcement Learning for Sim-to-Real Dexterous Manipulation | 点云强化学习、仿真到现实 | [PDF](DexPoint2022/2211.09423v2.pdf) · [arXiv](https://arxiv.org/abs/2211.09423) |
| DexReMoE: In-hand Reorientation of General Object via Mixtures of Experts | 混合专家、通用物体手内重定向 | [PDF](paper/2508.01695v1.pdf) · [arXiv](https://arxiv.org/abs/2508.01695) |
| DexRepNet++: Learning Dexterous Robotic Manipulation with Geometric and Spatial Hand-Object Representations | 几何与空间手-物表征 | [PDF](DexRepNet++/2602.21811v1.pdf) · [arXiv](https://arxiv.org/abs/2602.21811) |
| Dexterous Manipulation Based on Prior Dexterous Grasp Pose Knowledge | 抓取姿态先验、强化学习 | [PDF](<Dexterous Manipulation Based on Prior Dexterous Grasp Pose Knowledge/2412.15587v1.pdf>) · [arXiv](https://arxiv.org/abs/2412.15587) |
| In-Hand Manipulation of Articulated Tools with Dexterous Robot Hands with Sim-to-Real Transfer | 铰接工具、仿真到现实、触觉适配 | [PDF](<In-Hand Manipulation of Articulated Tools with Dexterous Robot Hands with Sim-to-Real Transfer/2509.23075v3.pdf>) · [arXiv](https://arxiv.org/abs/2509.23075) |
| Proximal Policy Optimization Algorithms | PPO 强化学习算法 | [PDF](ppo/1707.06347v2.pdf) · [arXiv](https://arxiv.org/abs/1707.06347) |

## 世界模型与模型式强化学习

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| World Models | 潜在空间世界模型 | [PDF](WorldModel/1803.10122v4.pdf) · [arXiv](https://arxiv.org/abs/1803.10122) |
| Learning Latent Dynamics for Planning from Pixels (PlaNet) | 像素潜在动力学规划 | [PDF](WorldModel/1811.04551v5.pdf) · [arXiv](https://arxiv.org/abs/1811.04551) |
| Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model (MuZero) | 学习模型规划 | [PDF](WorldModel/1911.08265v2.pdf) · [arXiv](https://arxiv.org/abs/1911.08265) |
| Dream to Control: Learning Behaviors by Latent Imagination (Dreamer) | 潜在想象控制 | [PDF](WorldModel/1912.01603v3.pdf) · [arXiv](https://arxiv.org/abs/1912.01603) |
| Mastering Diverse Domains through World Models (DreamerV3) | 通用世界模型强化学习 | [PDF](WorldModel/2301.04104v2.pdf) · [arXiv](https://arxiv.org/abs/2301.04104) |
| TD-MPC2: Scalable, Robust World Models for Continuous Control | 可扩展连续控制世界模型 | [PDF](WorldModel/2310.16828v2.pdf) · [arXiv](https://arxiv.org/abs/2310.16828) |

## 通用三维感知

| 论文 | 主题 | 链接 |
| --- | --- | --- |
| SAM 3D: 3Dfy Anything in Images | 单图三维重建与分割 | [PDF](SAM3D/2511.16624v2.pdf) · [arXiv](https://arxiv.org/abs/2511.16624) |

---

> 维护建议：新增论文时，将 PDF 放入独立目录，并在对应领域表格中补充正式标题、仓库内相对链接及 arXiv 链接；不添加其他站外链接。
