#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：创建部署包
# 作者：帅妹妹丶.8297
# 创建日期：2026-05-04

import os
import zipfile
from datetime import datetime
from pathlib import Path


def get_project_version():
    """获取项目版本号"""
    # 尝试从 git 获取最新 commit
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%h'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return datetime.now().strftime('%Y%m%d')


def create_zip_package():
    project_root = Path(__file__).parent
    version = get_project_version()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'gw2_backend_deploy_{version}_{timestamp}.zip'
    zip_filepath = project_root / zip_filename
    
    print(f"[*] 创建部署包: {zip_filename}")
    print(f"{'='*60}")
    
    # 需要包含的文件和目录
    include_patterns = [
        'app/',
        'scripts/',
        'docs/',
        'main.py',
        'requirements.txt',
        'README.md',
        '.env.example',
        'pyproject.toml',
    ]
    
    # 需要排除的模式
    exclude_patterns = [
        '__pycache__/',
        '*.pyc',
        '.git/',
        '.gitignore',
        'uploads/',
        '*.log',
        '*.tmp',
        'tests/',
        'tools/',
        '.env',
        '*.zip',
    ]
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = 0
        
        for include in include_patterns:
            include_path = project_root / include
            
            if include_path.is_file():
                # 单个文件
                arcname = str(include_path.relative_to(project_root))
                zipf.write(include_path, arcname)
                total_files += 1
                print(f"[+] 添加文件: {include}")
            
            elif include_path.is_dir():
                # 目录
                for root, dirs, files in os.walk(include_path):
                    # 排除目录
                    dirs[:] = [d for d in dirs if not any(
                        exclude.rstrip('/') in os.path.join(root, d) 
                        for exclude in exclude_patterns
                    )]
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        # 检查是否需要排除该文件
                        should_exclude = False
                        for exclude in exclude_patterns:
                            if exclude.endswith('/') and exclude[:-1] in str(file_path):
                                should_exclude = True
                                break
                            if exclude.startswith('*.') and str(file_path).endswith(exclude[1:]):
                                should_exclude = True
                                break
                            if exclude in str(file_path):
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            arcname = str(file_path.relative_to(project_root))
                            zipf.write(file_path, arcname)
                            total_files += 1
    
    file_size = zip_filepath.stat().st_size / (1024 * 1024)
    
    print(f"{'='*60}")
    print(f"[+] 部署包创建完成！")
    print(f"   文件名: {zip_filename}")
    print(f"   文件数: {total_files}")
    print(f"   大小: {file_size:.2f} MB")
    print(f"{'='*60}")
    
    return zip_filepath


if __name__ == "__main__":
    create_zip_package()
