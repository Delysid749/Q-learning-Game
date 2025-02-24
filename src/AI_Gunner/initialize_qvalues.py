import os
import json

# Q-table 存储路径
q_table_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'q_value.json'))

# 检查是否存在旧的 Q-table
if os.path.exists(q_table_path):
    with open(q_table_path, "r") as f:
        q_table = json.load(f)
    print(f"已加载 Q-table，共 {len(q_table)} 个状态")
else:
    q_table = {}
    print("未找到 Q-table，创建新表")

ENEMY_SPEEDS = [2]

# xdiff 范围 [-500, 500], 步长 20
xdiff_range = range(-500, 501, 20)

# ydiff 范围 [-700, 700], 步长 20
ydiff_range = range(-700, 701, 20)



q_values = {}

for es in ENEMY_SPEEDS:
    for xd in xdiff_range:
        for yd in ydiff_range:
            state_key = str((es, xd, yd))  # 确保与 environment.get_state() 返回形式对应
            q_values[state_key] = {0: 0.0, 1: 0.0, 2: 0.0}  # 将Q值初始化为全0

with open(q_table_path, "w") as f:
    json.dump(q_values, f, indent=4)

print("成功初始化Q值，并存储到 data/q_value.json!")
