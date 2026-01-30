import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import IterableDataset, DataLoader, get_worker_info
from torch.utils.tensorboard import SummaryWriter
import os
import json
import numpy as np
import random
from model import NNUE
from board import Situation, Red, Black

public_device = 'cuda' if torch.cuda.is_available() else 'cpu'

log_dir = "runs"
os.makedirs(log_dir, exist_ok=True)
writer = SummaryWriter(log_dir)

def collect_json_files(root_path,num=-1):
    print("正在收集 JSON 文件路径...")
    if not os.path.exists(root_path):
        raise FileNotFoundError(f"找不到数据目录: {root_path}")

    files = []
    for root, _, fs in os.walk(root_path):
        for f in sorted(fs):
            if f.endswith('.json'):
                files.append(os.path.join(root, f))
                if num > 0 and len(files) >= num:
                    break
        if num > 0 and len(files) >= num:
            break

    print(f"找到 {len(files)} 个 JSON 文件")
    return files

class NNUEDataset(IterableDataset):
    def __init__(self, json_files, clip_value=1000.0):
        self.json_files = json_files
        self.clip_value = clip_value

    def __iter__(self):
        worker_info = get_worker_info()
        if worker_info is None:
            iter_files = self.json_files
        else:
            worker_id = worker_info.id
            num_workers = worker_info.num_workers
            iter_files = [self.json_files[i] for i in range(len(self.json_files)) if i % num_workers == worker_id]

        random.shuffle(iter_files)

        for file_path in iter_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"跳过文件 {file_path}: {e}")
                continue

            samples_in_file = []
            for ply in data:
                for step in ply.get('data', []):
                    for move in step.get('data', []):
                        vl = float(move['vl'])
                        fen = move['fen_after_move']
                        samples_in_file.append((fen, vl))

            random.shuffle(samples_in_file)

            for fen, vl in samples_in_file:
                try:
                    clipped_vl = max(-self.clip_value, min(self.clip_value, vl))
                    norm_vl = clipped_vl / self.clip_value

                    aug_situations = [
                        Situation(fen),
                        Situation(fen).flip_left_and_right(),
                        Situation(fen).flip_up_and_down(),
                        Situation(fen).flip_left_and_right().flip_up_and_down()
                    ]
                    sit = aug_situations[np.random.randint(0, 4)]

                    x = torch.tensor(sit.matrix.copy(), dtype=torch.float32).view(-1)
                    y = torch.tensor(norm_vl, dtype=torch.float32).unsqueeze(0)
                    flag = torch.tensor(sit.actor_flag, dtype=torch.long)

                    yield x, y, flag
                except Exception as e:
                    # print(e.args)
                    pass

def create_dataloader(json_files, batch_size=32, clip_value=1000.0, num_workers=4):
    dataset = NNUEDataset(json_files, clip_value)
    dataloader = DataLoader(dataset, batch_size=batch_size, num_workers=num_workers)
    return dataloader

if __name__ == "__main__":
    print(f"使用设备: {public_device}")
    print(f"TensorBoard 日志将保存到: {log_dir}")
    #
    lr = 1e-5
    batch_size = 128
    epochs = 10000
    num_files = -1
    num_workers = 1

    model = NNUE(input_size=7 * 9 * 10).to(public_device)

    model.load_state_dict(torch.load("models/epoch_1.pth",map_location=public_device))

    optimizer = optim.RAdam(model.parameters(), lr=lr)

    # 更改为均方误差损失函数用于训练
    criterion_train = nn.MSELoss()
    # 保留平均绝对误差作为评估指标
    criterion_eval = nn.L1Loss()

    hparams = {
        'lr': lr,
        'batch_size': batch_size,
        'optimizer': 'RAdam',
        'loss': 'MSELoss',  # 记录实际使用的损失函数
        'epochs': epochs,
        'data_files': num_files,
        'device': public_device,
        'num_workers': num_workers
    }
    json_files = collect_json_files(root_path=r"F:\chess_data",num=num_files)
    #
    random.shuffle(json_files)
    #
    train_dataloader = create_dataloader(json_files, batch_size=batch_size, num_workers=num_workers)

    model.train()
    global_step = 0

    print(f"\n开始训练，batch_size={batch_size}")
    print(f"数据加载为流式，不预先计算总样本数和总步数。")
    print(f"训练将进行直到所有数据处理完毕。")

    for epoch in range(epochs):
        print(f"\n=== 第 {epoch+1}/{epochs} 轮训练 ===")
        model_dir = "models"
        os.makedirs(model_dir, exist_ok=True)
        model_name = f"epoch_{epoch+1}.pth"
        model_path = os.path.join(model_dir, model_name)

        epoch_mse_loss = 0.0
        epoch_l1_loss = 0.0
        step = 0

        for x_batch, y_batch, flags_batch in train_dataloader:
            x_batch = x_batch.to(public_device)
            y_batch = y_batch.to(public_device)
            flags_batch = flags_batch.to(public_device)

            optimizer.zero_grad()
            all_scores = model(x_batch)
            selected_indices = flags_batch.unsqueeze(1)
            selected_scores = torch.gather(all_scores, 1, selected_indices)

            # 使用 MSE 损失进行反向传播
            loss = criterion_train(selected_scores, y_batch)
            loss.backward()
            optimizer.step()

            # 计算 L1 损失用于监控
            l1_loss = criterion_eval(selected_scores, y_batch)

            epoch_mse_loss += loss.item()
            epoch_l1_loss += l1_loss.item()
            global_step += 1
            step += 1

            # 记录 MSE 和 L1 损失
            writer.add_scalar('Loss/step', loss.item(), global_step)
            writer.add_scalar('L1_Loss/step', l1_loss.item(), global_step)
            writer.add_scalar('Learning Rate', optimizer.param_groups[0]['lr'], global_step)

            if global_step % 1000 == 0:
                torch.save(model.state_dict(), model_path)
                print(f"模型已保存至: {model_path}")
                print(f"步骤 {global_step}, MSE损失: {loss.item():.6f}, L1损失: {l1_loss.item():.6f}")

        if step > 0:
            avg_mse_loss = epoch_mse_loss / step
            avg_l1_loss = epoch_l1_loss / step
            writer.add_scalar('Loss/epoch', avg_mse_loss, epoch)
            writer.add_scalar('L1_Loss/epoch', avg_l1_loss, epoch)
            print(f"第 {epoch+1} 轮平均损失: MSE={avg_mse_loss:.6f}, L1={avg_l1_loss:.6f}")
        else:
            print(f"第 {epoch+1} 轮没有处理任何样本。")

        torch.save(model.state_dict(), model_path)
        print(f"模型已保存至: {model_path}")

    print(f"\n训练完成！")
    print(f"使用以下命令查看 TensorBoard：")
    print(f"  tensorboard --logdir={log_dir}")

    writer.close()