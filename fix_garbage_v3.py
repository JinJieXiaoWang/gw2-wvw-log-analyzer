import subprocess
import re
import os

def has_garbage(line):
    if '\ufffd' in line:
        return True
    if re.search(r'[\u0560-\u058F]', line):
        return True
    if re.search(r'[\u4e00-\u9fff][\?\ufffd]', line):
        return True
    if re.search(r'(日期|说明|功能|用法|作者|依赖|模块|创建|更新|类型|管理|服务|路由|模型|数据|验证|测试|脚本|文档|配置|核心|工具|中间件|初始化|包初|包|使用|用法|界面|测试|环境|事件|目标|基准|基础|性能|内存|缓存|数据库|字段|映射|评分|分数|统计|状态|通知|公告|菜单|设置|系统|用户|账号|角色|职业|技能|天赋|特性|增益|战斗|日志|成员|出勤|导出|导入|报告|分析|解析|处理|查询|插入|更新|删除|清空|重置|同步|异步|轮询|调度|队列|工作|线程|进程|并发|锁|事务|回滚|提交|连接|池|会话|Cookie|Token|认证|授权|密码|哈希|加密|解密|签名|验证|校验|检查|确认|取消|关闭|开启|启动|停止|重启|加载|保存|读取|写入|下载|上传|复制|移动|重命名|删除|移除|添加|新建|编辑|修改|变更|调整|优化|改进|修复|解决|处理|跳过|忽略|跳过|禁止|允许|启用|禁用|激活|失效|过期|超时|延迟|等待|阻塞|挂起|恢复|继续|完成|结束|终止|中断|异常|错误|失败|成功|警告|信息|调试|追踪|记录|输出|输入|返回|传入|传出|参数|变量|常量|枚举|类|对象|实例|方法|函数|过程|回调|钩子|装饰|包装|代理|适配|桥接|组合|继承|多态|封装|抽象|接口|实现|模块|包|库|框架|引擎|驱动|工具|助手|服务|组件|控件|元素|节点|属性|特性|标签|标识|名称|标题|描述|摘要|详情|内容|文本|字符串|数字|整数|浮点|布尔|数组|列表|字典|集合|元组|映射|键|值|对|项|索引|偏移|长度|大小|容量|范围|区间|边界|限制|阈值|上限|下限|最小|最大|平均|总和|计数|数量|比例|比率|百分比|频率|速率|速度|延迟|耗时|周期|间隔|时间|日期|时刻|时区|时长|持续|截止|过期|有效|无效|合法|非法|正确|错误|正常|异常|默认|自定义|预设|模板|样式|主题|颜色|字体|尺寸|布局|位置|对齐|方向|顺序|优先级|权重|等级|级别|分类|分组|排序|过滤|筛选|搜索|匹配|查找|替换|删除|插入|追加|前置|反转|随机|洗牌|采样|抽样|聚合|分组|折叠|展开|扁平|嵌套|递归|迭代|循环|遍历|访问|引用|指针|地址|内存|堆|栈|队列|列表|数组|字典|集合|元组|树|二叉|平衡|红黑|AVL|B|B+|Trie|堆|大根|小根|斐波那契|二项|配对|散列|开放|封闭|链|冲突|再散|布隆|跳表|并查|线段|树状|稀疏|差分|前缀|后缀|自动|马拉车|KMP|BM|Rabin-Karp|Z|Manacher|Aho-Corasick|后缀|数组|树|DAG|并查|强连通|双连通|桥|割点|拓扑|关键|最短|最长|最小|最大|最优|次优|近似|启发|贪心|动态|回溯|分支|剪枝|递归|尾递归|分治|归并|快速|堆|桶|计数|基数|希尔|插入|选择|冒泡|鸡尾酒|地精|梳|侏儒|猴子|睡眠|爆炸|量子|DNA|遗传|蚁群|粒子|模拟|退火|禁忌|神经|深度|卷积|循环|Transformer|注意力|嵌入|向量|矩阵|张量|梯度|下降|上升|动量|自适应|学习|率|批次|周期|迭代|轮次|步|微调|预训练|迁移|强化|监督|半监督|无监督|自监督|对比|生成|判别|编码|解码|变分|自编码|对抗|扩散|流|标准化|批归一|层归一|实例|组|权重|偏置|激活|损失|目标|优化|正则|丢弃|早停|检查点|日志|监控|可视|绘图|图表|图形|图像|视频|音频|信号|采样|量化|编码|压缩|特征|提取|选择|降维|主成分|独立|线性|判别|因子|潜在|主题|词袋|TF-IDF|Word2Vec|GloVe|FastText|BERT|GPT|CLIP|Diffusion|Stable|Midjourney|DALL-E|生成|创作|绘画|作曲|写作|翻译|摘要|问答|对话|聊天|机器|人|代理|智能|专家|知识|图谱|本体|语义|推理|推断|演绎|归纳|溯因|假设|证明|定理|公理|引理|推论|命题|谓词|逻辑|模态|时序|描述|一阶|高阶|lambda|组合|范畴|类型|系统|语言|语法|词法|语义|上下文|无关|正则|自动机|图灵|有限|下推|线性|递归可枚举|停机|不可判定|NP|完全|难|复杂|算法|数据结构|栈|队列|列表|数组|字典|集合|元组|树|二叉|平衡|红黑|AVL|B|B+|Trie|堆|大根|小根|斐波那契|二项|配对|散列|开放|封闭|链|冲突|再散|布隆|跳表|并查|线段|树状|稀疏|差分|前缀|后缀|自动|马拉车|KMP|BM|Rabin-Karp|Z|Manacher|Aho-Corasick|后缀|数组|树|DAG|并查|强连通|双连通|桥|割点|拓扑|关键|最短|最长|最小|最大|网络|流|匹配|二分|匈牙利|KM|稳定|婚姻|指派|覆盖|独立|支配|着色|路径|欧拉|哈密顿|旅行商|背包|子集|划分|调度|作业|流水|贪心|动态|线性|整数|混合|二次|凸|非凸|约束|满足|SAT|SMT|MILP|NLP|启发|元|进化|遗传|蚁群|粒子|模拟|退火|禁忌|神经|深度|强化)[\?\ufffd]', line):
        return True
    return False

def normalize_line(line):
    # 移除中文字符、全角标点、Armenian字母、空白
    line = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u0560-\u058F]', '', line)
    line = re.sub(r'\s+', '', line)
    return line

def find_matching_lines(git_lines, target_norm):
    """在git_lines中找到连续多行，其normalize组合等于target_norm"""
    git_norms = [normalize_line(l) for l in git_lines]
    n = len(git_lines)
    
    # 限制最大窗口大小为15行
    max_window = min(15, n)
    
    for start in range(n):
        combined = ''
        for end in range(start, min(start + max_window, n)):
            combined += git_norms[end]
            if combined == target_norm:
                return git_lines[start:end+1]
            # 如果combined已经比target长，提前终止
            if len(combined) > len(target_norm):
                break
    return None

def fix_file(filepath):
    try:
        git_bytes = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], stderr=subprocess.DEVNULL)
        git_content = git_bytes.decode('utf-8', errors='replace')
    except subprocess.CalledProcessError:
        return False, "No git version"
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        curr_content = f.read()
    
    if not has_garbage(curr_content):
        return False, "No garbage"
    
    git_lines = git_content.splitlines()
    curr_lines = curr_content.splitlines()
    
    # 建立git单行索引
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
        
        # 策略1: 单行精确匹配
        norm = normalize_line(curr_line)
        if norm in git_index:
            candidates = git_index[norm]
            if len(candidates) == 1:
                fixed_lines.append(candidates[0])
                changes += 1
                continue
            else:
                fixed_lines.append(candidates[0])
                changes += 1
                continue
        
        # 策略2: 多行匹配（处理合并行）
        matched = find_matching_lines(git_lines, norm)
        if matched:
            fixed_lines.extend(matched)
            changes += 1
            continue
        
        # 策略3: 保留原样（无法修复）
        fixed_lines.append(curr_line)
    
    if changes > 0:
        if '\r\n' in curr_content:
            new_content = '\r\n'.join(fixed_lines)
        else:
            new_content = '\n'.join(fixed_lines)
        if new_content.startswith('\ufeff'):
            new_content = new_content[1:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, f"Fixed {changes} lines/merged blocks"
    
    return False, "No changes"

# 处理所有tracked且仍有乱码的文件
result = subprocess.check_output(['git', 'diff', '--name-only']).decode().split('\n')
tracked_files = [f.strip() for f in result if f.strip().startswith(('backend/', 'frontend/')) and os.path.isfile(f.strip())]

fixed_count = 0
still_garbage = []
for filepath in tracked_files:
    fixed, msg = fix_file(filepath)
    if fixed:
        fixed_count += 1
        print(f"[FIXED] {filepath}: {msg}")
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    if has_garbage(text):
        still_garbage.append(filepath)

print(f"\nFixed {fixed_count} files")
if still_garbage:
    print(f"Still has garbage ({len(still_garbage)} files):")
    for f in still_garbage[:50]:
        print(f"  {f}")
