import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config.database import _get_engine

engine = _get_engine()

alterations = [
    "ALTER TABLE evtc_agent MODIFY COLUMN address BIGINT UNSIGNED NOT NULL",
    "ALTER TABLE evtc_event MODIFY COLUMN src_agent BIGINT UNSIGNED NOT NULL",
    "ALTER TABLE evtc_event MODIFY COLUMN dst_agent BIGINT UNSIGNED NOT NULL",
]

with engine.connect() as conn:
    for sql in alterations:
        print(f"Executing: {sql}")
        try:
            conn.execute(text(sql))
            print("  OK")
        except Exception as e:
            print(f"  ERROR: {e}")
    conn.commit()

print("Done.")
