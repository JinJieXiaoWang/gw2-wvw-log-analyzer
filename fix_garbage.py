import subprocess
import difflib
import re
import os
import sys

# 获取所有git diff的backend和frontend文件
result = subprocess.check_output(['git', 'diff', '--name-only']).decode().split('\n')
files_to_fix = [f.strip() for f in result if f.strip().startswith(('backend/', 'frontend/')) and os.path.isfile(f.strip())]

def normalize_for_compare(line):
    """移除中文字符用于比较行结构"""
    # 保留ASCII、数字、常见标点、下划线
    # 但保留?和�以便检测乱码
    return re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', line).strip()

def has_garbage(line):
    """检测行是否包含乱码特征"""
    # U+FFFD 替换字符
    if '\ufffd' in line:
        return True
    # Armenian letters (frontend乱码常见)
    if re.search(r'[\u0560-\u058F]', line):
        return True
    # 中文上下文中不该出现的? (如 创建日期?2026, 说明?# )
    if re.search(r'[\u4e00-\u9fff][\?\ufffd]', line):
        return True
    # 全角冒号变成? 的情况：日期?、说明?、功能?
    if re.search(r'(日期|说明|功能|用法|作者|依赖|模块|创建|更新)[\?\ufffd]', line):
        return True
    return False

def fix_file(filepath):
    try:
        git_bytes = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], stderr=subprocess.DEVNULL)
        git_content = git_bytes.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError:
        return False, "No git version (untracked)"
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            curr_content = f.read()
    except Exception as e:
        return False, f"Read error: {e}"
    
    git_lines = git_content.splitlines()
    curr_lines = curr_content.splitlines()
    
    # 为git版本的每一行建立索引 (normalize -> list of lines)
    git_norm_map = {}
    for i, line in enumerate(git_lines):
        norm = normalize_for_compare(line)
        if norm:
            git_norm_map.setdefault(norm, []).append(line)
    
    fixed_lines = []
    changes = 0
    
    for curr_line in curr_lines:
        if not has_garbage(curr_line):
            fixed_lines.append(curr_line)
            continue
        
        # 尝试精确normalize匹配
        norm = normalize_for_compare(curr_line)
        if norm in git_norm_map:
            # 如果有多个匹配，选择最相似的
            candidates = git_norm_map[norm]
            if len(candidates) == 1:
                fixed_lines.append(candidates[0])
                changes += 1
                continue
            else:
                best = max(candidates, key=lambda g: difflib.SequenceMatcher(None, curr_line, g).ratio())
                fixed_lines.append(best)
                changes += 1
                continue
        
        # 尝试模糊匹配（处理合并行的情况）
        # 如果当前行是多个git行的合并，尝试拆分
        # 策略：如果当前行包含 `# 作者` 或 `# 说明` 等模式，且前面有乱码
        merged_match = re.match(r'^(.*[\?\ufffd])(#\s*.*)$', curr_line)
        if merged_match:
            part1 = merged_match.group(1)
            part2 = merged_match.group(2)
            
            # 尝试在git版本中找到对应的两行
            norm1 = normalize_for_compare(part1)
            norm2 = normalize_for_compare(part2)
            
            fixed1 = None
            fixed2 = None
            
            if norm1 in git_norm_map:
                candidates = git_norm_map[norm1]
                fixed1 = max(candidates, key=lambda g: difflib.SequenceMatcher(None, part1, g).ratio())
            
            if norm2 in git_norm_map:
                candidates = git_norm_map[norm2]
                fixed2 = max(candidates, key=lambda g: difflib.SequenceMatcher(None, part2, g).ratio())
            
            if fixed1 and fixed2:
                fixed_lines.append(fixed1)
                fixed_lines.append(fixed2)
                changes += 1
                continue
            elif fixed1:
                fixed_lines.append(fixed1)
                fixed_lines.append(part2)  # 保留第二部分
                changes += 1
                continue
        
        # 尝试在整个git文件中找最相似的单行
        best_ratio = 0
        best_line = None
        for git_line in git_lines:
            ratio = difflib.SequenceMatcher(None, curr_line, git_line).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_line = git_line
        
        if best_ratio > 0.7 and best_line and not has_garbage(best_line):
            fixed_lines.append(best_line)
            changes += 1
        else:
            fixed_lines.append(curr_line)
    
    if changes > 0:
        # 保留原始换行符风格
        if '\r\n' in curr_content:
            new_content = '\r\n'.join(fixed_lines)
        else:
            new_content = '\n'.join(fixed_lines)
        
        # 移除BOM
        if new_content.startswith('\ufeff'):
            new_content = new_content[1:]
        
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(new_content)
        return True, f"Fixed {changes} lines"
    
    return False, "No changes needed"

total_fixed = 0
total_files = 0
for filepath in files_to_fix:
    fixed, msg = fix_file(filepath)
    if fixed:
        total_fixed += 1
        print(f"[FIXED] {filepath}: {msg}")
    elif "No git version" in msg:
        # untracked file, skip for now
        pass
    else:
        # Check if file still has garbage
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if has_garbage(content):
            print(f"[STILL_HAS_GARBAGE] {filepath}: {msg}")

total_files = len(files_to_fix)
print(f"\nSummary: Fixed {total_fixed}/{total_files} tracked files")
