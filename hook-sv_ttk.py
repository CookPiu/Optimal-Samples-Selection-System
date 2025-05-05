# PyInstaller hook for sv_ttk
from PyInstaller.utils.hooks import collect_data_files

# 确保sv_ttk的所有数据文件被包含在打包中
datas = collect_data_files('sv_ttk')