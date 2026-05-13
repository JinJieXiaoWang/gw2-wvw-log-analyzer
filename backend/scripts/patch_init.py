import sys
filepath = 'app/data/init_all.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
start_marker = '# 字典类型种子数据'
end_marker = '# 角色定位种子数据'
start = content.find(start_marker)
end = content.find(end_marker)
if start == -1 or end == -1:
    print('Markers not found')
    sys.exit(1)

new_block = open('scripts/new_dict_seed.txt', 'r', encoding='utf-8').read()
new_content = content[:start] + new_block + content[end:]
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')
