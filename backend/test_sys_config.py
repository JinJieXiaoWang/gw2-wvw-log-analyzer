# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.config.database import SessionLocal
from app.services.sys_config_service import SysConfigService

db = SessionLocal()
try:
    service = SysConfigService(db)
    before = service.get_all_settings()
    print("当前配置:")
    for k, v in before.items():
        print(f"  {k} = {v}")
    
    service.set_config("watermark_enabled", False)
    service.set_config("watermark_text", "")
    print("\n已重置为默认值")
    
    after = service.get_all_settings()
    print("\n重置后:")
    print(f"  watermark_enabled = {after.get('watermark_enabled')}")
    print(f"  watermark_text = {after.get('watermark_text')}")
finally:
    db.close()
