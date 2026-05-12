
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：恢复所有模型文件
# 作者：AI Assistant
# 创建日期：2026-05-13

import subprocess
import os
import glob

# 获取所有模型文件
model_files = []

# 添加backend/app/models目录下的所有.py文件
for root, dirs, files in os.walk('backend/app/models'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file).replace('\\', '/')
            model_files.append(filepath)

print(f"找到 {len(model_files)} 个模型文件")

restored_count = 0
skipped_count = 0
error_count = 0

for filepath in model_files:
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath}: 文件不存在")
        skipped_count += 1
        continue
    
    try:
        # 从Git获取原始版本
        git_content = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], 
                                             stderr=subprocess.DEVNULL)
        
        # 写回文件
        with open(filepath, 'wb') as f:
            f.write(git_content)
        
        print(f"[RESTORED] {filepath}")
        restored_count += 1
        
    except subprocess.CalledProcessError:
        print(f"[SKIP] {filepath}: 无法从Git获取")
        skipped_count += 1
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        error_count += 1

print(f"\n总结: 恢复 {restored_count}, 跳过 {skipped_count}, 错误 {error_count}")
