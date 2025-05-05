# hook-pulp.py
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集pulp模块的所有数据文件
datas = collect_data_files('pulp')

# 特别关注solverdir目录，确保CBC求解器被包含
import os
import pulp

# 获取pulp库的安装路径
pulp_path = os.path.dirname(pulp.__file__)
solverdir_path = os.path.join(pulp_path, 'solverdir')

# 添加CBC求解器目录
if os.path.exists(solverdir_path):
    cbc_path = os.path.join(solverdir_path, 'cbc')
    if os.path.exists(cbc_path):
        # 添加所有CBC求解器文件
        for root, dirs, files in os.walk(cbc_path):
            for file in files:
                if file.endswith('.exe'):
                    source = os.path.join(root, file)
                    target = os.path.relpath(source, pulp_path)
                    datas.append((source, os.path.dirname(target)))

# 收集所有子模块
hiddenimports = collect_submodules('pulp')