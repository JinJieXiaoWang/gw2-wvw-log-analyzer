import os

#!/usr/bin/env python3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.config.database import _get_engine

engine = _get_engine()
inspector = inspect(engine)

print("=== evtc_agent columns ===")
for c in inspector.get_columns("evtc_agent"):
    print(f"  {c['name']}: {c['type']}")

print("\n=== evtc_log columns ===")
for c in inspector.get_columns("evtc_log"):
    print(f"  {c['name']}: {c['type']}")
