import os
import logging

# 计算日志目录路径
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'game_logs'))
os.makedirs(log_dir, exist_ok=True)  # 确保目录存在

# 定义不同的日志文件
log_files = {
    "train": os.path.join(log_dir, "train_log.txt"),
    "q_value": os.path.join(log_dir, "q_value_updates.log"),
    "game": os.path.join(log_dir, "game_play.log"),
    "debug": os.path.join(log_dir, "debug.log")
}

# 设置日志格式
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建日志记录器
loggers = {}

for log_name, log_path in log_files.items():
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)  # 设置日志级别
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    loggers[log_name] = logger

# 公开全局日志对象
train_logger = loggers["train"]
q_value_logger = loggers["q_value"]
game_logger = loggers["game"]
debug_logger = loggers["debug"]

print(f"日志系统初始化完成，日志存储于: {log_dir}")
