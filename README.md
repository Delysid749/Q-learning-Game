Apocalypse Gunner Q-Learning Project
====================================

1\. Project Overview
--------------------

This project utilizes the **Q-learning** algorithm to train and control a shooting game called “Apocalypse Gunner.” Its main functions include:

1.  **AI Training Mode**: During training, the Q-learning process continuously updates `q_value.json`, gradually learning better shooting or movement strategies to increase the number of enemies shot down and reduce collisions.
2.  **Player Manual Mode**: Users can run `apocalypse_gunner.py` directly, using the keyboard (left/right arrow keys and spacebar) to control the shooter in the game.
3.  **AI Automatic Mode**: By loading the trained Q-value table in `run_game.py`, the AI will automatically control the shooter and display gameplay on the screen.

The following sections detail everything from environment setup and training to running the game.

* * *

2\. Directory Structure
-----------------------

Based on the provided screenshot and code, here is an example of the project structure (please verify and adjust according to your actual setup):

```
Q-learning-Game
│
├── data
│   ├── game_logs
│   │   ├── game_play.log            # Log of the AI’s in-game actions
│   │   └── train_log.txt            # Training log
│   ├── train_result
│   │   ├── epsilon_alpha.png        # Epsilon and alpha variation during training
│   │   ├── hits_collisions.png      # Number of enemies shot down and collisions
│   │   └── reward_vs_episode.png    # Reward progression across episodes
│   └── q_value.json                 # Q-value table saved after Q-learning training
│
├── src
│   ├── AI_Gunner
│   │   ├── agent.py                 # QLearningAgent class: core Q-learning logic
│   │   ├── initialize_qvalues.py    # Initializes q_value.json
│   │   └── train_agent.py           # Training script
│   │
│   ├── assets                       # (Resource folder: images, sounds, etc.)
│   │   └── images / sounds
│   │
│   ├── Gunner_Game
│   │   ├── apocalypse_gunner.py     # Entry point for manual player-controlled gameplay
│   │   ├── environment.py           # Game environment (states/actions/rewards)
│   │   └── render.py                # Handles game rendering (images, sounds, UI, etc.)
│   │
│   ├── logs_config
│   │   └── log_config.py            # Logging system configuration (outputs to .txt/.log files)
│   │
│   ├── run_game.py                  # Entry script that uses the trained AI to control the game
│   └── train.py                     # Training entry script (with command-line parameter parsing)
│
├── .gitignore
├── README.md
└── requirements.txt
```

* * *

3\. Environment Requirements
----------------------------

1.  **Python 3.7+** or higher
2.  Third-party libraries:
    *   `pygame`: for graphics and event handling in the game
    *   `matplotlib`: for visualizing training curves

You can install the dependencies at once via:

```bash
pip install -r requirements.txt
```

If there is no `requirements.txt`, please manually install the necessary packages:

```bash
pip install pygame matplotlib
```

* * *

4\. Quick Start
---------------

### 4.1 Initializing the Q-Value Table

Before starting the training, you need to initialize (or load) the Q-value table `q_value.json`, so that the subsequent training will have a proper state-action record structure:

```bash
cd src/AI_Gunner
python initialize_qvalues.py
```

*   If `q_value.json` already exists, the script loads it and prints the number of existing states.
*   If the file does not exist, it generates zero-initialized Q-values for the predefined state ranges (enemy speed / xdiff / ydiff).

**Underlying Principle**  
`initialize_qvalues.py` iterates over all discretized state combinations `(enemy_speed, xdiff, ydiff)`, assigning 0.0 to each action `{0,1,2,...}` for that state, thus creating the fundamental Q-value structure.

* * *

### 4.2 Starting Training

Once initialization is complete, you can proceed with training.

#### Method: Using the encapsulated `train.py`

```bash
cd src
python train.py -iter 200
```

This script uses `argparse` to accept a `-iter` command-line parameter for specifying the number of training episodes, which defaults to 100.

**After Training**

1.  The Q-value table in `data/q_value.json` will be updated.
2.  Several visualization charts will be generated in `data/train_result/`:
    *   **reward\_vs\_episode.png**: Total rewards per episode
    *   **epsilon\_alpha.png**: Epsilon (exploration rate) and Alpha (learning rate) decay curves
    *   **hits\_collisions.png**: The number of enemies shot down vs. collisions per episode

**Core Q-Learning Principles**

* Uses an  $\epsilon$ \-greedy strategy to balance “exploration” and “exploitation.”

* Q-value update formula: 
  $$
   Q(s, a) \leftarrow Q(s, a) + \alpha\bigl[r + \gamma \max_{a'}\,Q(s', a') - Q(s, a)\bigr]
  $$

* Incorporates dynamic decay for the learning rate  $\alpha$  and exploration rate  $\epsilon$  to avoid overly unstable early learning or stagnation in later stages.

* * *

### 4.3 Running the Game

#### 4.3.1 Manual Player-Controlled Mode

```bash
cd src/Gunner_Game
python apocalypse_gunner.py
```

*   Left / Right arrow keys: move the character
*   Spacebar: shoot
*   If the shooter collides with an enemy, lives decrease by 1. The game ends when `gunner_lives` <= 0.

In this mode, **Q-learning is not used** for decisions. It is merely for gameplay testing or casual play.

#### 4.3.2 AI Automatic Mode

If you have already trained a Q-value table (`q_value.json`), you can let the AI control the shooter:

```bash
cd src
python run_game.py
```

*   `run_game.py` first creates **ApocalypseGunnerEnv** (with `is_training=False`).
*   Then it loads `QLearningAgent` and calls `agent.load()` to retrieve the latest Q table.
*   Within the game loop, **AI** automatically picks actions (`choose_action()`), and the effect is displayed in real time on the screen.

No manual input is required here. The AI decides movement or shooting according to the current state, consulting the Q table.

* * *

5\. Key Files and Their Functions
---------------------------------

| **File/Directory**         | **Function**                                                 |
| -------------------------- | ------------------------------------------------------------ |
| **data/**                  | Data and logs directory, including `q_value.json` (Q table), training/game logs, and visualization results |
| ├─ **game\_logs/**         | Training and gameplay logs (`train_log.txt`, `game_play.log`) |
| ├─ **train\_result/**      | Output charts for training (reward curves, exploration rate, collisions, etc.) |
| └─ **q\_value.json**       | Q table storing (state-action) -> Q-value after training     |
| **src/AI\_Gunner/**        | AI-related modules: Q-learning agent, initialization scripts, and training scripts |
| ├─ `agent.py`              | `QLearningAgent` class containing core methods like choose\_action(), update\_q(), decay\_parameters() |
| ├─ `initialize_qvalues.py` | Script for initializing/loading the Q table                  |
| └─ `train_agent.py`        | Training loop, visualization functions (plotting training curves), etc. |
| **src/assets/**            | Resource folder: images (`.png`), sounds (`.mp3`), etc.      |
| **src/Gunner\_Game/**      | The main game environment and rendering modules              |
| ├─ `apocalypse_gunner.py`  | Entry point for purely manual gameplay (no AI)               |
| ├─ `environment.py`        | Game environment: `reset()`, `step(action)`, `get_state()`, reward and termination criteria |
| └─ `render.py`             | Image and audio rendering, UI drawing, etc.                  |
| **src/logs\_config/**      | Logging configuration                                        |
| └─ `log_config.py`         | Sets up loggers for training and gameplay logs, including output paths/formats |
| **src/run\_game.py**       | A script for fully automated AI-controlled gameplay          |
| **src/train.py**           | Training entry point (with command-line arguments), alternative to calling `train_agent.py` directly |
|                            |                                                              |

* * *

6\. Logging and Visualization
-----------------------------

1.  **Logging System (logs\_config/log\_config.py)**
    *   `train_log.txt`: Records real-time information per training episode (total reward, exploration rate, learning rate, etc.).
    *   `game_play.log`: Logs the AI’s in-game performance.
    *   Use `logger.info(...)` for output; you can tweak the log level or file path in the script.
2.  **Visualization**
    *   `train_agent.py` invokes `matplotlib` to plot training curves, saving them in `data/train_result/`:
        *   `reward_vs_episode.png`: total reward progression over episodes
        *   `epsilon_alpha.png`: decay curves for epsilon / alpha
        *   `hits_collisions.png`: number of hits vs. collisions per episode

* * *

7\. Frequently Asked Questions (FAQ)
------------------------------------

1.  **Excessively Large Q Table / Memory Usage**
    *   Reduce the resolution of your state discretization or use function approximators (neural networks).
2.  **Slow or Non-Converging Training**
    *   Adjust the learning rate and exploration rate (and their decay factors).
    *   Refine the reward design for more consistent guidance.
    *   Increase the number of training episodes to ensure sufficient exploration.

* * *

8\. Conclusion and Outlook
--------------------------

* This project demonstrates how to employ **Q-Learning** to play a simple 2D shooting game. By customizing rewards, state encodings, and discrete actions, the AI incrementally learns to avoid collisions and shoot down enemies.

* As the complexity of states and actions grows, a pure Q-table might become unmanageable. Consider evolving it into a **Deep Q Network (DQN)** or other advanced reinforcement learning methods.

* If richer gameplay or visual features are desired, you can expand on the `pygame` foundation by adding more enemy types, level mechanisms, or action types.

  
