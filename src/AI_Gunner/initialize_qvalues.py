import os
import json
from itertools import product

# 计算 Q-table 存储路径
q_table_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'q_value.json'))

# 检查是否存在旧的 Q-table
if os.path.exists(q_table_path):
    with open(q_table_path, "r") as f:
        q_table = json.load(f)
    print(f"已加载 Q-table，共 {len(q_table)} 个状态")
else:
    q_table = {}
    print("未找到 Q-table，创建新表")

# 定义游戏状态离散化范围
gunner_x_positions = [round(i / 500, 2) for i in range(0, 501, 50)]
enemy_y_positions = [round(i / 700, 2) for i in range(0, 701, 70)]
bullet_y_positions = [round(i / 700, 2) for i in range(0, 701, 70)]
actions = ["0", "1", "2"]  # 0: 左移, 1: 右移, 2: 射击

# 统计新增状态
new_states = 0

# 生成所有可能的状态组合
for gunner_x, enemy_y, bullet_y in product(gunner_x_positions, enemy_y_positions, bullet_y_positions):
    state_key = str((gunner_x, enemy_y, bullet_y))

    # 如果状态已存在，则跳过
    if state_key not in q_table:
        q_table[state_key] = {action: 0 for action in actions}  # 初始化新的状态
        new_states += 1

print(f"添加了 {new_states} 个新状态，总状态数: {len(q_table)}")

# 存储更新后的 Q-table
os.makedirs(os.path.dirname(q_table_path), exist_ok=True)
with open(q_table_path, "w") as f:
    json.dump(q_table, f, indent=4)

print(f"Q-table 更新完成，存储于: {q_table_path}")
