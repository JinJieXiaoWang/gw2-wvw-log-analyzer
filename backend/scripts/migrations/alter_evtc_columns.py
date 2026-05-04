import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config.database import _get_engine

engine = _get_engine()

alterations = [
    "ALTER TABLE evtc_agent MODIFY COLUMN prof BIGINT NOT NULL",
    "ALTER TABLE evtc_agent MODIFY COLUMN is_elite BIGINT NOT NULL",
    "ALTER TABLE evtc_event MODIFY COLUMN overstack_value BIGINT NOT NULL",
    "ALTER TABLE evtc_event MODIFY COLUMN skill_id BIGINT NOT NULL",
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
