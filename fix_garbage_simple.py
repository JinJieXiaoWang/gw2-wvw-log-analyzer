
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：简单修复乱码文件
# 作者：AI Assistant
# 创建日期：2026-05-13

import os
import re

# 常见的乱码模式
garbage_patterns = [
    (r'\?\s*$', ''),  # 结尾的问号
    (r'\?\s*"', '"'),  # 引号前的问号
    (r'\?\s*\)', ')'),  # 括号前的问号
    (r'\?\s*,\s*$', ','),  # 逗号前的问号
    (r'\?\s*:\s*$', ':'),  # 冒号前的问号
    (r'创建日期\?', '创建日期：'),
    (r'说明\?$', '说明：'),
    (r'状态\?$', '状态'),
    (r'数量\?$', '数量'),
    (r'大小\?$', '大小'),
    (r'精度\?$', '精度'),
    (r'名称\?$', '名称'),
    (r'账号\?$', '账号'),
    (r'时间\?$', '时间'),
    (r'记录\?$', '记录'),
    (r'秒\?$', '秒)'),
    (r'用\?$', '用)'),
    (r'查询\?$', '查询'),
    (r'\?\s*—\s*', ' — '),
    (r'\?\s*""",\s*$', '""",'),
    (r'\?\s*""",\s*$', '""",'),
]

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"[ERROR] 无法读取: {filepath}")
        return False
    
    original_content = content
    
    # 应用修复规则
    for pattern, replacement in garbage_patterns:
        content = re.sub(pattern, replacement, content)
    
    # 检查是否有未终止的字符串
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # 检查未终止的字符串
        if line.count('"') % 2 != 0:
            # 简单处理：在行尾添加引号
            if not line.rstrip().endswith('"'):
                lines[i] = line + '"'
    
    content = '\n'.join(lines)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {filepath}")
        return True
    else:
        return False

# 修复backend/app/models目录下的所有文件
def fix_directory(directory):
    fixed_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    fixed_count += 1
    print(f"\n修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    fix_directory('backend/app/models')
    print("\n完成!")

