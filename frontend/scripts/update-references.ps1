param(
    [string]$projectPath = "D:\Code\Gw2-wvw-log-analyzer\frontend\src"
)

Write-Host "=== Updating references ===" -ForegroundColor Cyan

$replacements = @(
    @{ O = "@/components/buildParser/"; N = "@/components/build/parser/" },
    @{ O = "@/components/build-library/"; N = "@/components/build/library/" },
    @{ O = "@/components/eiDetail/"; N = "@/components/combat/" },
    @{ O = "@/components/dict/"; N = "@/components/dictionary/" },
    @{ O = "@/components/skillRotation/"; N = "@/components/skill-rotation/" },
    @{ O = "@/components/logManagement/"; N = "@/components/log-management/" },
    @{ O = "@/components/aiAnalysis/"; N = "@/components/ai-analysis/" },
    @{ O = "@/components/theme/"; N = "@/components/common/theme/" }
)

$files = Get-ChildItem -Path $projectPath -Recurse -Filter "*.vue"
$files += Get-ChildItem -Path $projectPath -Recurse -Filter "*.ts"

foreach ($r in $replacements) {
    foreach ($f in $files) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content.Contains($r.O)) {
            $content = $content.Replace($r.O, $r.N)
            Set-Content -Path $f.FullName -Value $content -NoNewline
        }
    }
}

Write-Host "=== References updated ===" -ForegroundColor Cyan
