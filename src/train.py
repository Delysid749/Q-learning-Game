import argparse

from AI_Gunner.train_agent import train

# 训练文件入口
if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="训练 ApocalypseGunnerEnv 环境中的 Q-learning 代理")
    parser.add_argument("-iter", type=int, default=100, help="训练的回合数，默认为 100")
    args = parser.parse_args()

    # 根据传入参数启动训练
    train(num_episodes=args.iter)
