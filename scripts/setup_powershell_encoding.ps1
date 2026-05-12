
# 模块功能：设置PowerShell编码以防止乱码
# 作者：AI Assistant
# 创建日期：2026-05-13

Write-Host "正在设置PowerShell编码..." -ForegroundColor Green

# 设置输出编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置默认编码
[System.Text.Encoding]::Default = [System.Text.Encoding]::UTF8

# 设置输入编码
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 创建PowerShell配置文件（如果不存在）
$profilePath = $PROFILE.CurrentUserCurrentHost
if (-not (Test-Path $profilePath)) {
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
    Write-Host "已创建PowerShell配置文件: $profilePath" -ForegroundColor Yellow
}

# 添加编码设置到配置文件
$profileContent = @'
# -*- coding: utf-8 -*-
# GW2日志分析器 - PowerShell编码配置
# 防止中文乱码问题

# 设置输出编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置默认编码
[System.Text.Encoding]::Default = [System.Text.Encoding]::UTF8

# 设置文件操作默认编码
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Get-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'

Write-Host "PowerShell编码已设置为UTF-8" -ForegroundColor Green
'@

if (-not (Get-Content $profilePath | Select-String -Pattern "GW2日志分析器")) {
    Add-Content -Path $profilePath -Value $profileContent -Encoding UTF8
    Write-Host "已添加编码配置到PowerShell配置文件" -ForegroundColor Yellow
}

Write-Host "PowerShell编码设置完成！" -ForegroundColor Green
Write-Host "请重新启动PowerShell或运行: . `$PROFILE" -ForegroundColor Cyan
