末日枪手 Q-Learning 项目
=============

1\. 项目概述
--------

本项目利用 **Q-Learning** 算法训练并控制一款名为 “Apocalypse Gunner”（末日枪手）的射击游戏。其主要功能包括：

1.  **AI 训练模式**：在训练过程中，Q-Learning会不断更新 `q_value.json`，逐步学习更优的射击或移动策略，以增加击落敌人数量并减少碰撞。
    
2.  **玩家手动模式**：用户可以直接运行 `apocalypse_gunner.py`，通过键盘（左右方向键和空格键）控制游戏中的射手。
    
3.  **AI 自动模式**：通过在 `run_game.py` 中加载训练好的 Q 值表，AI 将自动控制射手并在屏幕上展示游戏过程。
    

以下章节将详细介绍从环境搭建、训练到运行游戏的全部内容。

* * *

2\. 目录结构
--------

根据提供的截图和代码，项目结构示例如下（请根据实际情况确认并调整）：

```
Q-learning-Game
│
├── data
│   ├── game_logs
│   │   ├── game_play.log            # AI 在游戏中的操作日志
│   │   └── train_log.txt            # 训练日志
│   ├── train_result
│   │   ├── epsilon_alpha.png        # 训练过程中 ε 与 α 的变化曲线
│   │   ├── hits_collisions.png      # 击落敌人数与碰撞次数曲线
│   │   └── reward_vs_episode.png    # 各回合奖励进展曲线
│   └── q_value.json                 # Q-Learning训练后保存的 Q 值表
│
├── src
│   ├── AI_Gunner
│   │   ├── agent.py                 # QLearningAgent 类：核心 Q-Learning逻辑
│   │   ├── initialize_qvalues.py    # 初始化 q_value.json
│   │   └── train_agent.py           # 训练脚本
│   │
│   ├── assets                       # 资源文件夹：图片、音效等
│   │   └── images / sounds
│   │
│   ├── Gunner_Game
│   │   ├── apocalypse_gunner.py     # 玩家手动模式入口
│   │   ├── environment.py           # 游戏环境（状态/动作/奖励）
│   │   └── render.py                # 游戏渲染（图像、音效、UI 等）
│   │
│   ├── logs_config
│   │   └── log_config.py            # 日志系统配置（输出到 .txt/.log）
│   │
│   ├── run_game.py                  # 使用训练好的 AI 控制游戏的入口脚本
│   └── train.py                     # 训练入口脚本（含命令行参数解析）
│
├── .gitignore
├── README.md
└── requirements.txt
```

* * *

3\. 环境需求
--------

1.  **Python 3.7+** 或以上
    
2.  第三方库：
    
    *   `pygame`：用于游戏的图形和事件处理
        
    *   `matplotlib`：用于训练曲线可视化
        

可通过以下命令一次性安装所有依赖：

```bash
pip install -r requirements.txt
```

若无 `requirements.txt`，请手动安装：

```bash
pip install pygame matplotlib
```

* * *

4\. 快速开始
--------

### 4.1 初始化 Q 值表

在开始训练前，需要初始化（或加载）Q 值表 `q_value.json`，以便后续训练有合适的状态-动作记录结构：

```bash
cd src/AI_Gunner
python initialize_qvalues.py
```

*   若 `q_value.json` 已存在，脚本将加载并打印已存在的状态数。
    
*   若文件不存在，则生成针对预定义状态范围（敌机速度 / xdiff / ydiff）的零初始化 Q 值。
    

**原理说明**  
`initialize_qvalues.py` 遍历所有离散化状态组合 `(enemy_speed, xdiff, ydiff)`，为每个动作 `{0,1,2,...}` 赋值 0.0，从而构建基础 Q 值结构。

* * *

### 4.2 开始训练

完成初始化后，即可开始训练。

#### 方法：使用封装好的 `train.py`

```bash
cd src
python train.py -iter 200
```

该脚本通过 `argparse` 接收 `-iter` 参数指定训练回合数，默认为 100。

**训练后**

1.  `data/q_value.json` 中的 Q 值表将被更新。
    
2.  在 `data/train_result/` 目录下生成可视化图表：
    
    *   **reward\_vs\_episode.png**：各回合总奖励曲线
        
    *   **epsilon\_alpha.png**：ε（探索率）和 α（学习率）衰减曲线
        
    *   **hits\_collisions.png**：击落敌人数 vs. 碰撞次数曲线
        

**核心 Q-Learning原理**

*   使用 ε-贪婪策略平衡“探索”与“利用”。
    
*   Q 值更新公式：
    
    $$
    Q(s, a) \leftarrow Q(s, a) + \alpha\bigl[r + \gamma \max_{a'}\,Q(s', a') - Q(s, a)\bigr]
    $$
    
*   动态衰减学习率 α 与探索率 ε，以避免早期过度不稳定或后期学习停滞。
    

* * *

### 4.3 运行游戏

#### 4.3.1 玩家手动模式

```bash
cd src/Gunner_Game
python apocalypse_gunner.py
```

*   左/右 方向键：移动角色
    
*   空格键：射击
    
*   若射手与敌机碰撞，生命值减 1；当 `gunner_lives` ≤ 0 时游戏结束。
    

该模式**不使用 Q-Learning**决策，仅用于游戏测试或娱乐。

#### 4.3.2 AI 自动模式

若已训练好 Q 值表 (`q_value.json`)，可由 AI 控制射手：

```bash
cd src
python run_game.py
```

*   `run_game.py` 首先创建 **ApocalypseGunnerEnv**（`is_training=False`）。
    
*   然后加载 `QLearningAgent` 并调用 `agent.load()` 读取最新 Q 表。
    
*   在游戏循环中，**AI** 通过 `choose_action()` 自动选择动作并实时显示。
    

此模式无需手动输入，AI 根据当前状态并参考 Q 表决定移动或射击。

* * *

5\. 关键文件及其功能
------------

| **文件/目录** | **功能** |
| --- | --- |
| **data/** | 数据与日志目录，包括 `q_value.json`（Q 表）、训练/游戏日志及可视化结果 |
| ├─ **game\_logs/** | 训练与游戏日志 (`train_log.txt`、`game_play.log`) |
| ├─ **train\_result/** | 训练输出图表（奖励曲线、探索率、碰撞次数等） |
| └─ **q\_value.json** | 存储训练后 (状态-动作) → Q 值 的 Q 表 |
| **src/AI\_Gunner/** | 与 AI 相关的模块：Q-Learning agent、初始化脚本与训练脚本 |
| ├─ `agent.py` | `QLearningAgent` 类，包含 `choose_action()`、`update_q()`、`decay_parameters()` 等核心方法 |
| ├─ `initialize_qvalues.py` | 初始化/加载 Q 表 |
| └─ `train_agent.py` | 训练循环及可视化函数 |
| **src/assets/** | 资源文件夹：图片(`.png`)、音效(`.mp3`) |
| **src/Gunner\_Game/** | 游戏环境与渲染模块 |
| ├─ `apocalypse_gunner.py` | 完全手动模式入口 |
| ├─ `environment.py` | 游戏环境：`reset()`、`step(action)`、`get_state()`、奖励与终止条件 |
| └─ `render.py` | 图像与音频渲染、UI 绘制 |
| **src/logs\_config/** | 日志配置目录 |
| └─ `log_config.py` | 配置训练与游戏日志输出格式与路径 |
| **src/run\_game.py** | AI 全自动模式脚本 |
| **src/train.py** | 训练入口脚本（含命令行参数），可替代直接调用 `train_agent.py` |

* * *

6\. 日志与可视化
----------

1.  **日志系统 (`logs_config/log_config.py`)**
    
    *   `train_log.txt`：记录每回合训练实时信息（总奖励、探索率、学习率等）。
        
    *   `game_play.log`：记录 AI 在游戏中的表现日志。
        
    *   使用 `logger.info(...)` 输出，可在脚本中调整日志级别或路径。
    
2.  **可视化**
    
    *   `train_agent.py` 调用 `matplotlib` 绘制训练曲线，保存至 `data/train_result/`：
        
        *   `reward_vs_episode.png`：各回合总奖励进展
            
        *   `epsilon_alpha.png`：ε / α 衰减曲线
            
        *   `hits_collisions.png`：击落 vs. 碰撞 数量曲线
            

* * *

7\. 常见问题 (FAQ)
--------------

1.  **Q 表过大 / 内存占用高**
    
    *   降低状态离散化粒度，或使用函数逼近器（如神经网络）。
    
2.  **训练过慢或不收敛**
    
    *   调整学习率和探索率（及其衰减因子）。
        
    *   优化奖励设计以提供更一致的指导。
        
    *   增加训练回合数以确保充分探索。
        

* * *

8\. 结论与展望
---------

*   本项目展示了如何使用 **Q-Learning** 玩转一款简单的 2D 射击游戏。通过自定义奖励、状态编码与离散动作，AI 能逐步学习规避碰撞并击落敌人。
    
*   随着状态和动作复杂度增加，纯 Q 表可能难以扩展。可尝试演进为 **深度 Q 网络 (DQN)** 或其他先进强化学习方法。
    
*   如需更丰富的玩法或视觉效果，可基于 `pygame` 扩展更多敌机类型、关卡机制或动作类型。
