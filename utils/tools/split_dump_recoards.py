import os
import shutil

def split_folder(input_folder, output_folder, num_splits):
    # 获取文件夹中的所有文件
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # 计算每份包含的文件数量
    files_per_split = len(files) // num_splits

    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 分割文件并复制到新的文件夹中
    for i in range(num_splits):
        split_folder_name = os.path.join(output_folder, f'split_{i+1}')
        os.makedirs(split_folder_name, exist_ok=True)

        start_index = i * files_per_split
        end_index = (i+1) * files_per_split if i != num_splits - 1 else len(files)

        for j in range(start_index, end_index):
            shutil.copy(os.path.join(input_folder, files[j]), os.path.join(split_folder_name, files[j]))

# 示例用法
input_folder = 'D:\dump_2'
output_folder = 'D:\dump_3'
num_splits = 16

split_folder(input_folder, output_folder, num_splits)