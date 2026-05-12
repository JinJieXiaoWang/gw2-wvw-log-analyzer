import re
import os
import shutil
from pathlib import Path

# ==================== 配置 ====================
PROJECT_ROOT = Path('d:/Code/Gw2-wvw-log-analyzer')
FRONTEND_SRC = PROJECT_ROOT / 'frontend' / 'src'
BACKUP_DIR = PROJECT_ROOT / 'frontend' / 'src_backup'
DESIGN_TOKENS_PATH = FRONTEND_SRC / 'config' / 'designTokens.ts'

# 颜色值匹配正则（引号包裹的）
HEX_COLOR_RE = re.compile(r"['\"](#[0-9a-fA-F]{3,8})['\"]")
RGB_COLOR_RE = re.compile(r"['\"](rgba?\s*\([^)]+\))['\"]")

# 已有的颜色常量映射（小写颜色值 -> 常量路径）
EXISTING_COLORS = {
    '#165dff': 'Colors.primary.DEFAULT',
    '#4080ff': 'Colors.primary.light',
    '#0e42d2': 'Colors.primary.dark',
    '#ff7d00': 'Colors.secondary.DEFAULT',
    '#ff9a2e': 'Colors.secondary.light',
    '#d25f00': 'Colors.secondary.dark',
    '#141414': 'Colors.neutral.bg',
    '#2a2a2a': 'Colors.neutral.card',
    '#333333': 'Colors.neutral.cardHover',
    '#3d3d3d': 'Colors.neutral.border',
    '#4d4d4d': 'Colors.neutral.borderLight',
    '#e5e5e5': 'Colors.neutral.text',
    '#909399': 'Colors.neutral.textSecondary',
    '#666666': 'Colors.neutral.textDisabled',
    '#00b42a': 'Colors.status.success',
    '#f53f3f': 'Colors.status.error',
    '#0fcef5': 'Colors.status.info',
    '#00c896': 'Colors.ai.DEFAULT',
}

# 新增颜色常量映射（将在 designTokens.ts 中添加）
NEW_COLORS = {
    '#3b82f6': 'Colors.palette.blue',
    '#ef4444': 'Colors.palette.red',
    '#22c55e': 'Colors.palette.green',
    '#f59e0b': 'Colors.palette.amber',
    '#a855f7': 'Colors.palette.purple',
    '#06b6d4': 'Colors.palette.cyan',
    '#ec4899': 'Colors.palette.pink',
    '#84cc16': 'Colors.palette.lime',
    '#f97316': 'Colors.palette.orange',
    '#6366f1': 'Colors.palette.indigo',
    '#14b8a6': 'Colors.palette.teal',
    '#e11d48': 'Colors.palette.rose',
    '#8b5cf6': 'Colors.palette.violet',
    '#10b981': 'Colors.palette.emerald',
    '#f43f5e': 'Colors.palette.crimson',
    '#eab308': 'Colors.palette.yellow',
    '#d946ef': 'Colors.palette.fuchsia',
    '#0ea5e9': 'Colors.palette.sky',
    '#ff4d6a': 'Colors.palette.roseBright',
    '#00b4ff': 'Colors.palette.skyBlue',
    '#9d4edd': 'Colors.palette.violetBright',
    '#ffaa00': 'Colors.palette.orangeBright',
    '#00d68f': 'Colors.palette.mint',
    '#ffd700': 'Colors.palette.gold',
    '#ff6b6b': 'Colors.palette.coral',
    '#ff8a65': 'Colors.palette.salmon',
    '#ff6b35': 'Colors.palette.orangeRed',
    '#ff5722': 'Colors.palette.deepOrange',
    '#ffb347': 'Colors.palette.peach',
    '#ffa500': 'Colors.palette.orangeGold',
    '#4caf50': 'Colors.palette.materialGreen',
    '#00e5a0': 'Colors.palette.aqua',
    '#ff8a80': 'Colors.palette.lightRed',
    '#4a6fa5': 'Colors.palette.steelBlue',
    '#6b7280': 'Colors.palette.gray',
    '#6c757d': 'Colors.palette.grayLight',
    '#888888': 'Colors.palette.grayMedium',
    '#f1f5f9': 'Colors.palette.slate100',
    '#e2e8f0': 'Colors.palette.slate200',
    '#94a3b8': 'Colors.palette.slate400',
    '#64748b': 'Colors.palette.slate500',
    '#0f172a': 'Colors.palette.slate900',
    '#0d0d0f': 'Colors.palette.dark',
    '#0a1420': 'Colors.palette.navy',
    '#d09c59': 'Colors.palette.sand',
    '#ffffff': 'Colors.palette.white',
    '#e85d04': 'Colors.palette.warrior',
    '#faa307': 'Colors.palette.guardian',
    '#7b8fa1': 'Colors.palette.engineer',
    '#06d6a0': 'Colors.palette.ranger',
    '#8d0801': 'Colors.palette.necromancer',
    '#4361ee': 'Colors.palette.mesmer',
    '#2ec4b6': 'Colors.palette.revenant',
    '#e85000': 'Colors.palette.warriorAlt',
    '#ffb400': 'Colors.palette.guardianAlt',
    '#7b5ba6': 'Colors.palette.mesmerAlt',
    '#ff9b1a': 'Colors.palette.engineerAlt',
    '#19b1e5': 'Colors.palette.elementalistAlt',
    '#a4c600': 'Colors.palette.rangerAlt',
    '#0078e8': 'Colors.palette.necromancerAlt',
    '#8a4baf': 'Colors.palette.revenantAlt',
    '#d4a574': 'Colors.palette.weaponsmith',
    'rgba(15, 23, 42, 0.9)': 'Colors.palette.slate900Alpha90',
    'rgba(148, 163, 184, 0.2)': 'Colors.palette.slate400Alpha20',
    'rgba(148,163,184,0.2)': 'Colors.palette.slate400Alpha20',
    'rgba(148, 163, 184, 0.1)': 'Colors.palette.slate400Alpha10',
    'rgba(148,163,184,0.1)': 'Colors.palette.slate400Alpha10',
    'rgba(255,255,255,0.08)': 'Colors.palette.whiteAlpha08',
    'rgba(255, 255, 255, 0.04)': 'Colors.palette.whiteAlpha04',
    'rgba(255, 255, 255, 0.05)': 'Colors.palette.whiteAlpha05',
    'rgba(255, 255, 255, 0.02)': 'Colors.palette.whiteAlpha02',
    'rgba(255, 255, 255, 0.85)': 'Colors.palette.whiteAlpha85',
    'rgba(0, 0, 0, 0.3)': 'Colors.palette.blackAlpha30',
    'rgba(0,0,0,0.3)': 'Colors.palette.blackAlpha30',
    'rgba(0, 0, 0, 0.4)': 'Colors.palette.blackAlpha40',
    'rgba(0,0,0,0.4)': 'Colors.palette.blackAlpha40',
    'rgba(0, 0, 0, 0.5)': 'Colors.palette.blackAlpha50',
    'rgba(0,0,0,0.5)': 'Colors.palette.blackAlpha50',
    'rgba(0, 0, 0, 0.6)': 'Colors.palette.blackAlpha60',
    'rgba(0,0,0,0.6)': 'Colors.palette.blackAlpha60',
    'rgba(0, 0, 0, 0.1)': 'Colors.palette.blackAlpha10',
    'rgba(0, 0, 0, 0.45)': 'Colors.palette.blackAlpha45',
    'rgba(239, 68, 68, 0.1)': 'Colors.palette.redAlpha10',
    'rgba(34, 197, 94, 0.1)': 'Colors.palette.greenAlpha10',
    'rgba(59,130,246,0.2)': 'Colors.palette.blueAlpha20',
    'rgba(59, 130, 246, 0.2)': 'Colors.palette.blueAlpha20',
    'rgba(59,130,246,0.3)': 'Colors.palette.blueAlpha30',
    'rgba(59, 130, 246, 0.3)': 'Colors.palette.blueAlpha30',
    'rgba(22, 93, 255, 0.2)': 'Colors.primary.alpha20',
    'rgba(22, 93, 255, 0.3)': 'Colors.palette.primaryAlpha30',
    'rgba(255, 125, 0, 0.1)': 'Colors.secondary.alpha10',
    'rgba(255, 125, 0, 0.3)': 'Colors.palette.secondaryAlpha30',
    'rgba(0, 200, 150, 0.3)': 'Colors.ai.alpha20',
}

# 合并映射
COLOR_MAP = {**EXISTING_COLORS, **NEW_COLORS}


def find_comment_regions(text):
    """找出文本中所有注释区域，返回 (start, end) 列表"""
    regions = []
    in_string = False
    string_char = None
    i = 0
    while i < len(text):
        c = text[i]
        if c in "'\"" and not in_string:
            in_string = True
            string_char = c
            i += 1
            continue
        if c == string_char and in_string:
            if i > 0 and text[i-1] == '\\':
                i += 1
                continue
            in_string = False
            string_char = None
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c == '/' and i + 1 < len(text):
            if text[i+1] == '/':
                start = i
                end = text.find('\n', i)
                if end == -1:
                    end = len(text)
                regions.append((start, end))
                i = end
                continue
            elif text[i+1] == '*':
                start = i
                end = text.find('*/', i + 2)
                if end == -1:
                    end = len(text)
                else:
                    end += 2
                regions.append((start, end))
                i = end
                continue
        i += 1
    return regions


def is_in_comment(pos, comment_regions):
    """检查位置是否在注释区域内"""
    for start, end in comment_regions:
        if start <= pos < end:
            return True
    return False


def replace_colors_in_text(text):
    """替换文本中的颜色值（跳过注释），返回新文本和替换次数"""
    comment_regions = find_comment_regions(text)
    replacements = []
    
    for match in HEX_COLOR_RE.finditer(text):
        if not is_in_comment(match.start(), comment_regions):
            color = match.group(1).lower()
            if color in COLOR_MAP:
                replacements.append((match.start(), match.end(), COLOR_MAP[color]))
    
    for match in RGB_COLOR_RE.finditer(text):
        if not is_in_comment(match.start(), comment_regions):
            color = match.group(1).lower()
            normalized = re.sub(r'\s+', ' ', color)
            if normalized in COLOR_MAP:
                replacements.append((match.start(), match.end(), COLOR_MAP[normalized]))
            elif color in COLOR_MAP:
                replacements.append((match.start(), match.end(), COLOR_MAP[color]))
    
    if not replacements:
        return text, 0
    
    # 按位置倒序替换，避免位置偏移
    replacements.sort(key=lambda x: x[0], reverse=True)
    new_text = text
    count = 0
    for start, end, const_path in replacements:
        new_text = new_text[:start] + const_path + new_text[end:]
        count += 1
    
    return new_text, count


def has_import_colors(content):
    """检查文件是否已经 import 了 Colors"""
    return bool(re.search(r"import\s+\{[^}]*Colors[^}]*\}\s+from\s+['\"]@/config/designTokens['\"]", content))


def has_import_designtokens(content):
    """检查文件是否已经 import 了 DesignTokens"""
    return bool(re.search(r"import\s+\{[^}]*DesignTokens[^}]*\}\s+from\s+['\"]@/config/designTokens['\"]", content))


def add_import(content, import_line):
    """在文件顶部添加 import"""
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('/**') or line.startswith(' *') or line.startswith(' */'):
            insert_idx = i + 1
    lines.insert(insert_idx, import_line)
    return '\n'.join(lines)


def extend_design_tokens():
    """扩展 designTokens.ts，添加 palette 分组"""
    with open(DESIGN_TOKENS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'palette:' in content:
        print("  designTokens.ts 已包含 palette，跳过扩展")
        return
    
    palette_code = """  /* ============================================
     扩展调色板 (Extended Palette)
     ============================================ */
  palette: {
    // 标准图表色板
    blue: '#3b82f6',
    red: '#ef4444',
    green: '#22c55e',
    amber: '#f59e0b',
    purple: '#a855f7',
    cyan: '#06b6d4',
    pink: '#ec4899',
    lime: '#84cc16',
    orange: '#f97316',
    indigo: '#6366f1',
    teal: '#14b8a6',
    rose: '#e11d48',
    violet: '#8b5cf6',
    emerald: '#10b981',
    crimson: '#f43f5e',
    yellow: '#eab308',
    fuchsia: '#d946ef',
    sky: '#0ea5e9',

    // 扩展色板
    roseBright: '#FF4D6A',
    skyBlue: '#00B4FF',
    violetBright: '#9D4EDD',
    orangeBright: '#FFAA00',
    mint: '#00D68F',
    gold: '#FFD700',
    coral: '#FF6B6B',
    salmon: '#FF8A65',
    orangeRed: '#FF6B35',
    deepOrange: '#FF5722',
    peach: '#FFB347',
    orangeGold: '#FFA500',
    materialGreen: '#4CAF50',
    aqua: '#00E5A0',
    lightRed: '#FF8A80',
    steelBlue: '#4A6FA5',

    // 中性色扩展
    gray: '#6b7280',
    grayLight: '#6C757D',
    grayMedium: '#888888',
    slate100: '#f1f5f9',
    slate200: '#e2e8f0',
    slate400: '#94a3b8',
    slate500: '#64748b',
    slate900: '#0f172a',
    dark: '#0D0D0F',
    navy: '#0A1420',
    sand: '#D09C59',
    white: '#ffffff',

    // 职业色
    warrior: '#E85D04',
    guardian: '#FAA307',
    thief: '#9D4EDD',
    elementalist: '#FF6B6B',
    engineer: '#7B8FA1',
    ranger: '#06D6A0',
    necromancer: '#8D0801',
    mesmer: '#4361EE',
    revenant: '#2EC4B6',

    // Alpha 变体
    slate900Alpha90: 'rgba(15, 23, 42, 0.9)',
    slate400Alpha20: 'rgba(148, 163, 184, 0.2)',
    slate400Alpha10: 'rgba(148, 163, 184, 0.1)',
    whiteAlpha08: 'rgba(255, 255, 255, 0.08)',
    whiteAlpha04: 'rgba(255, 255, 255, 0.04)',
    whiteAlpha05: 'rgba(255, 255, 255, 0.05)',
    whiteAlpha02: 'rgba(255, 255, 255, 0.02)',
    whiteAlpha85: 'rgba(255, 255, 255, 0.85)',
    blackAlpha30: 'rgba(0, 0, 0, 0.3)',
    blackAlpha40: 'rgba(0, 0, 0, 0.4)',
    blackAlpha50: 'rgba(0, 0, 0, 0.5)',
    blackAlpha60: 'rgba(0, 0, 0, 0.6)',
    blackAlpha10: 'rgba(0, 0, 0, 0.1)',
    blackAlpha45: 'rgba(0, 0, 0, 0.45)',
    redAlpha10: 'rgba(239, 68, 68, 0.1)',
    greenAlpha10: 'rgba(34, 197, 94, 0.1)',
    blueAlpha20: 'rgba(59, 130, 246, 0.2)',
    blueAlpha30: 'rgba(59, 130, 246, 0.3)',
    primaryAlpha30: 'rgba(22, 93, 255, 0.3)',
    secondaryAlpha30: 'rgba(255, 125, 0, 0.3)'
  },
"""
    
    pattern = r"(export const Colors = \{)"
    content = re.sub(pattern, r"\1\n" + palette_code, content, count=1)
    
    with open(DESIGN_TOKENS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  designTokens.ts 已扩展")


def task1_color_refactor():
    """任务一：硬编码颜色值集中化"""
    print("=" * 60)
    print("Task 1: Hard-coded color centralization")
    print("=" * 60)
    
    # 1. 备份
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(FRONTEND_SRC, BACKUP_DIR)
    print(f"Backup created: {BACKUP_DIR}")
    
    # 2. 扩展 designTokens.ts
    print("\nExtending designTokens.ts ...")
    extend_design_tokens()
    
    # 3. 扫描并替换
    total_replacements = 0
    files_modified = 0
    
    for root, dirs, files in os.walk(FRONTEND_SRC):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', '.git', '__pycache__']]
        for file in files:
            if not (file.endswith('.vue') or file.endswith('.ts')):
                continue
            
            filepath = Path(root) / file
            relative = filepath.relative_to(FRONTEND_SRC)
            
            if file == 'designTokens.ts' and 'config' in str(relative):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  Read failed: {relative} - {e}")
                continue
            
            if file.endswith('.ts'):
                text_to_process = content
                is_vue = False
            else:
                script_match = re.search(r'(<script[^>]*>)(.*?)(</script>)', content, re.DOTALL)
                if not script_match:
                    continue
                text_to_process = script_match.group(2)
                is_vue = True
            
            new_text, count = replace_colors_in_text(text_to_process)
            
            if count == 0:
                continue
            
            files_modified += 1
            total_replacements += count
            
            if is_vue:
                full_new_script = script_match.group(1) + new_text + script_match.group(3)
                new_content = content[:script_match.start()] + full_new_script + content[script_match.end():]
            else:
                new_content = new_text
            
            # 添加 import
            if not has_import_colors(new_content) and not has_import_designtokens(new_content):
                new_content = add_import(new_content, "import { Colors } from '@/config/designTokens'")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  [{count:3d}] {relative}")
    
    print(f"\nTask 1 completed:")
    print(f"  Files modified: {files_modified}")
    print(f"  Colors replaced: {total_replacements}")
    return total_replacements, files_modified


def task2_class_wrap():
    """任务二：class 超长属性换行"""
    print("\n" + "=" * 60)
    print("Task 2: Long class attribute wrapping")
    print("=" * 60)
    
    total_fixed = 0
    files_modified = 0
    
    for root, dirs, files in os.walk(FRONTEND_SRC):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', '.git', '__pycache__']]
        for file in files:
            if not file.endswith('.vue'):
                continue
            
            filepath = Path(root) / file
            relative = filepath.relative_to(FRONTEND_SRC)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_match = re.search(r'(<template>)(.*?)(</template>)', content, re.DOTALL)
            if not template_match:
                continue
            
            template = template_match.group(2)
            
            # 匹配 class="..."（单行，class值不含换行）
            # 注意：跳过 :class 绑定，因为它的值是 JS 表达式，不适合简单换行
            # 使用 \s+ 确保 class 前面至少有一个空白字符，避免匹配到 :class 中的 class
            single_line_class_re = re.compile(r'(\s+)(class)="([^"]*)"')
            
            changes = []
            matches = list(single_line_class_re.finditer(template))
            
            # 按位置倒序处理
            for match in reversed(matches):
                leading_ws = match.group(1)
                attr_name = match.group(2)
                class_value = match.group(3)
                full_match = match.group(0)
                
                # 跳过 class 值已包含换行的
                if '\n' in class_value:
                    continue
                
                if len(class_value) > 80:
                    # 计算行首缩进（基于 match 所在行的起始位置）
                    line_start = template.rfind('\n', 0, match.start())
                    if line_start == -1:
                        line_start = 0
                    else:
                        line_start += 1
                    
                    base_indent = ''
                    for c in template[line_start:match.start()]:
                        if c in ' \t':
                            base_indent += c
                        else:
                            break
                    
                    # 计算缩进：基于行首缩进 + 额外 2 空格
                    indent = base_indent + '  '
                    prefix_newline = '\n'
                    
                    attr_prefix = f'{indent}{attr_name}="'
                    
                    words = class_value.split()
                    lines = [words[0]]
                    current_len = len(words[0])
                    
                    for word in words[1:]:
                        if current_len + 1 + len(word) > 75:
                            lines.append(word)
                            current_len = len(word)
                        else:
                            lines[-1] += ' ' + word
                            current_len += 1 + len(word)
                    
                    # 构建带缩进的多行属性
                    lines[0] = attr_prefix + lines[0]
                    cont_indent = ' ' * len(attr_prefix)
                    for i in range(1, len(lines)):
                        lines[i] = cont_indent + lines[i]
                    lines[-1] += '"'
                    
                    new_attr = prefix_newline + '\n'.join(lines)
                    
                    template = template[:match.start()] + new_attr + template[match.end():]
                    changes.append(1)
                    total_fixed += 1
            
            if changes:
                files_modified += 1
                new_content = content[:template_match.start()] + template_match.group(1) + template + template_match.group(3) + content[template_match.end():]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  [{len(changes):3d}] {relative}")
    
    print(f"\nTask 2 completed:")
    print(f"  Files modified: {files_modified}")
    print(f"  Classes wrapped: {total_fixed}")
    return total_fixed, files_modified


if __name__ == '__main__':
    os.chdir(PROJECT_ROOT)
    
    # 执行任务一
    t1_replacements, t1_files = task1_color_refactor()
    
    # 执行任务二
    t2_fixed, t2_files = task2_class_wrap()
    
    print("\n" + "=" * 60)
    print("Batch refactoring completed")
    print("=" * 60)
    print(f"Task 1 (Color centralization):")
    print(f"  Files modified: {t1_files}")
    print(f"  Colors replaced: {t1_replacements}")
    print(f"Task 2 (Class wrapping):")
    print(f"  Files modified: {t2_files}")
    print(f"  Classes wrapped: {t2_fixed}")
    print(f"Total files modified: {t1_files + t2_files}")
