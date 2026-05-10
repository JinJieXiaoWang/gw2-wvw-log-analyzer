import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config.database import _get_engine

engine = _get_engine()

sql = "ALTER TABLE evtc_agent MODIFY COLUMN name_raw VARBINARY(68)"

with engine.connect() as conn:
    print(f"Executing: {sql}")
    conn.execute(text(sql))
    conn.commit()
    print("OK")
