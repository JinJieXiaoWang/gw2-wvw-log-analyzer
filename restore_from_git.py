
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 模块功能：从Git恢复有乱码的文件
# 作者：AI Assistant
# 创建日期：2026-05-13

import subprocess
import os

# 需要恢复的文件列表（从fix_garbage_v2.py的输出中获取）
files_to_restore = [
    'backend/app/config/__init__.py',
    'backend/app/config/ai_config.py',
    'backend/app/config/database.py',
    'backend/app/config/database_settings.py',
    'backend/app/config/settings.py',
    'backend/app/core/ai_quality_fallback.py',
    'backend/app/core/zevtc/constants.py',
    'backend/app/core/zevtc/models.py',
    'backend/app/core/zevtc/parser_core.py',
    'backend/app/models/ai_report.py',
    'backend/app/models/batch_parse.py',
    'backend/app/models/ei_report.py',
    'backend/app/models/scoring_rule.py',
    'backend/app/routers/attendance.py',
    'backend/app/routers/config.py',
    'backend/app/routers/dashboard.py',
    'backend/app/routers/ei_analysis.py',
    'backend/app/routers/fights.py',
    'backend/app/routers/logs.py',
    'backend/app/routers/scoring.py',
    'backend/app/routers/test_dps_report.py',
    'backend/app/schemas/log.py',
    'backend/app/services/ai_service.py',
    'backend/app/services/auth_service.py',
    'backend/app/services/ei/report_service.py',
    'backend/app/services/ei/unified_service.py',
    'backend/app/services/score_query_service.py',
    'backend/app/services/score_recalculation_service.py',
    'backend/app/services/scoring_rule_service.py',
    'backend/app/services/system/database_manager.py',
    'backend/app/services/system/dictionary_service.py',
    'backend/app/services/system/dps_report_service.py',
    'backend/app/services/zevtc/batch_parse_service.py',
    'backend/app/services/zevtc/data_validator.py',
    'backend/app/services/zevtc/log_import_service.py',
    'backend/app/services/zevtc/rate_limiter.py',
    'backend/app/utils/dict_utils.py',
    'backend/app/utils/json_utils.py',
    'backend/scripts/cleanup_invalid_accounts.py',
    'backend/scripts/docs/generate_api_docs.py',
    'backend/scripts/format_code.py',
    'backend/scripts/sync_skill_icons.py',
    'backend/scripts/test_json_initializer.py',
    'backend/tests/api/test_auto_discovery.py',
    'backend/tests/api/test_logs.py',
    'backend/tests/api/test_notice.py',
    'backend/tests/api/test_upload.py',
    'backend/tests/integration/test_attendance_service.py',
    'backend/tests/integration/test_commander_tag.py',
    'backend/tests/integration/test_dashboard.py',
    'backend/tests/unit/test_account_validation.py',
]

restored_count = 0
skipped_count = 0
error_count = 0

for filepath in files_to_restore:
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath}: 文件不存在")
        skipped_count += 1
        continue
    
    try:
        # 从Git获取原始版本
        git_content = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], 
                                             stderr=subprocess.DEVNULL)
        
        # 写回文件
        with open(filepath, 'wb') as f:
            f.write(git_content)
        
        print(f"[RESTORED] {filepath}")
        restored_count += 1
        
    except subprocess.CalledProcessError:
        print(f"[SKIP] {filepath}: 无法从Git获取")
        skipped_count += 1
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        error_count += 1

print(f"\n总结: 恢复 {restored_count}, 跳过 {skipped_count}, 错误 {error_count}")
