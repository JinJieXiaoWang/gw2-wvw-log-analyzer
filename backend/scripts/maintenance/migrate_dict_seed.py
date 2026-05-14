import re

filepath = 'app/data/init_all.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('# 字典类型种子数据')
end = content.find('# 角色定位种子数据')

new_block = open('scripts/maintenance/new_dict_seed.txt', 'r', encoding='utf-8').read()

new_content = content[:start] + new_block + content[end:]
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Replaced successfully')
