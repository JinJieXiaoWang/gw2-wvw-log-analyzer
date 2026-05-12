
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：恢复所有Git跟踪的文件
# 作者：AI Assistant
# 创建日期：2026-05-13

import subprocess
import os

# 获取所有Git跟踪的有修改的文件
result = subprocess.check_output(['git', 'diff', '--name-only']).decode().split('\n')
files_to_restore = [f.strip() for f in result if f.strip()]

print(f"找到 {len(files_to_restore)} 个有修改的文件")

restored_count = 0
skipped_count = 0
error_count = 0

for filepath in files_to_restore:
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath}: 文件不存在")
        skipped_count += 1
        continue
    
    # 只处理.py和.vue文件
    if not (filepath.endswith('.py') or filepath.endswith('.vue') or filepath.endswith('.ts') or filepath.endswith('.js')):
        print(f"[SKIP] {filepath}: 非目标文件类型")
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
