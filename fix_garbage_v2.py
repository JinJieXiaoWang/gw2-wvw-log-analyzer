import subprocess
import difflib
import re
import os
import sys

def has_garbage(line):
    if '\ufffd' in line:
        return True
    if re.search(r'[\u0560-\u058F]', line):
        return True
    if re.search(r'[\u4e00-\u9fff][\?\ufffd]', line):
        return True
    if re.search(r'(日期|说明|功能|用法|作者|依赖|模块|创建|更新|类型|管理|服务|路由|模型|数据|验证|测试|脚本|文档|配置|核心|工具|中间件|初始化|包初|包)[\?\ufffd]', line):
        return True
    return False

def normalize_line(line):
    """移除中文字符和全角标点，保留ASCII结构"""
    return re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', line).strip()

def fix_file_tracked(filepath):
    try:
        git_bytes = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], stderr=subprocess.DEVNULL)
        git_content = git_bytes.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError:
        return False, "No git version"
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        curr_content = f.read()
    
    # 快速检查：如果整个文件没有乱码，跳过
    if not has_garbage(curr_content):
        return False, "No garbage"
    
    git_lines = git_content.splitlines()
    curr_lines = curr_content.splitlines()
    
    # 建立git版本索引: normalize -> [original_lines]
    git_index = {}
    for line in git_lines:
        norm = normalize_line(line)
        if norm:
            git_index.setdefault(norm, []).append(line)
    
    fixed_lines = []
    changes = 0
    
    for curr_line in curr_lines:
        if not has_garbage(curr_line):
            fixed_lines.append(curr_line)
            continue
        
        # 策略1: 精确normalize匹配
        norm = normalize_line(curr_line)
        if norm in git_index:
            candidates = git_index[norm]
            if len(candidates) == 1:
                fixed_lines.append(candidates[0])
                changes += 1
                continue
            else:
                # 多个候选，选最相似的
                best = max(candidates, key=lambda g: difflib.SequenceMatcher(None, curr_line, g).quick_ratio())
                fixed_lines.append(best)
                changes += 1
                continue
        
        # 策略2: 处理合并行 (如 "模型# 作者" -> "模型\n# 作者")
        # 常见模式: 乱码字符后面紧跟 # 开头的新注释行
        merged = re.match(r'^(.*?[\?\ufffd])(#\s+.*)$', curr_line)
        if merged:
            part1_raw = merged.group(1)
            part2_raw = merged.group(2)
            norm1 = normalize_line(part1_raw)
            norm2 = normalize_line(part2_raw)
            
            found1 = git_index.get(norm1)
            found2 = git_index.get(norm2)
            
            if found1 and found2:
                fixed_lines.append(found1[0])
                fixed_lines.append(found2[0])
                changes += 1
                continue
            elif found1:
                fixed_lines.append(found1[0])
                fixed_lines.append(part2_raw)
                changes += 1
                continue
            elif found2:
                fixed_lines.append(part1_raw)
                fixed_lines.append(found2[0])
                changes += 1
                continue
        
        # 策略3: 对整个文件找最相似行（限制为包含乱码的行）
        # 先检查git中是否有行的开头/结尾和当前行匹配
        best_ratio = 0.0
        best_line = None
        for git_line in git_lines:
            # 快速过滤：如果长度差异太大，跳过
            if abs(len(git_line) - len(curr_line)) > 20:
                continue
            ratio = difflib.SequenceMatcher(None, curr_line, git_line).quick_ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_line = git_line
        
        if best_ratio > 0.6 and best_line and not has_garbage(best_line):
            fixed_lines.append(best_line)
            changes += 1
        else:
            fixed_lines.append(curr_line)
    
    if changes > 0:
        # 保留原始换行符
        if '\r\n' in curr_content:
            new_content = '\r\n'.join(fixed_lines)
        else:
            new_content = '\n'.join(fixed_lines)
        # 移除BOM
        if new_content.startswith('\ufeff'):
            new_content = new_content[1:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, f"Fixed {changes} lines"
    
    return False, "No changes made"

# 处理tracked文件
result = subprocess.check_output(['git', 'diff', '--name-only']).decode().split('\n')
tracked_files = [f.strip() for f in result if f.strip().startswith(('backend/', 'frontend/')) and os.path.isfile(f.strip())]

fixed_count = 0
still_garbage = []
for filepath in tracked_files:
    fixed, msg = fix_file_tracked(filepath)
    if fixed:
        fixed_count += 1
        print(f"[FIXED] {filepath}: {msg}")
    
    # 检查是否还有乱码
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    if has_garbage(text):
        still_garbage.append(filepath)

print(f"\nFixed {fixed_count}/{len(tracked_files)} files")
if still_garbage:
    print(f"Still has garbage ({len(still_garbage)} files):")
    for f in still_garbage[:30]:
        print(f"  {f}")
