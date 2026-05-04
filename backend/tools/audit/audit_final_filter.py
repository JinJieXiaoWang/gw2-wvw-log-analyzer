# -*- coding: utf-8 -*-
import pymysql
from app.config.database_settings import db_settings

conn = pymysql.connect(
    host=db_settings.MYSQL_HOST, port=db_settings.MYSQL_PORT,
    user=db_settings.MYSQL_USER, password=db_settings.MYSQL_PASSWORD,
    database=db_settings.MYSQL_DATABASE, charset=db_settings.MYSQL_CHARSET,
)

try:
    with conn.cursor() as cursor:
        total = 1245084
        
        # Core statechanges needed by all backend services
        core_sc = [1, 2, 4, 5, 6, 7, 11, 12, 37]
        placeholders = ','.join(str(v) for v in core_sc)
        
        # Core normal events: buff=1 OR is_activation!=0 OR value>0 OR buff_dmg>0 OR value<0 (healing)
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0
              AND (buff = 1 OR is_activation != 0 OR value > 0 OR buff_dmg > 0 OR value < 0)
        ''')
        core_normal = cursor.fetchone()[0]
        
        # Core statechange events
        cursor.execute(f'''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange IN ({placeholders})
        ''')
        core_sc_count = cursor.fetchone()[0]
        
        core_total = core_normal + core_sc_count
        filter_count = total - core_total
        filter_pct = filter_count * 100 / total
        
        print('=== FINAL FILTER ANALYSIS ===')
        print(f'Total events: {total:,}')
        print(f'Core normal events: {core_normal:,}')
        print(f'Core statechange events: {core_sc_count:,}')
        print(f'Core total: {core_total:,}')
        print(f'Can be filtered: {filter_count:,} ({filter_pct:.1f}%)')
        print()
        
        # Per-log breakdown
        print('=== Per-log final filter ===')
        cursor.execute(f'''
            SELECT 
                log_id,
                COUNT(*) as total,
                SUM(CASE WHEN is_statechange = 0 AND (buff = 1 OR is_activation != 0 OR value > 0 OR buff_dmg > 0 OR value < 0) THEN 1 ELSE 0 END) as core_normal,
                SUM(CASE WHEN is_statechange IN ({placeholders}) THEN 1 ELSE 0 END) as core_sc
            FROM evtc_event
            GROUP BY log_id
            ORDER BY total DESC
        ''')
        for row in cursor.fetchall():
            core = row[2] + row[3]
            print(f'log_id={row[0]} total={row[1]:>7,} core={core:>7,} filter={row[1]-core:>7,} ({(row[1]-core)*100/row[1]:.1f}%)')
        
        # What gets filtered (by statechange type)
        print()
        print('=== Filtered statechange breakdown ===')
        cursor.execute(f'''
            SELECT is_statechange, COUNT(*) as cnt
            FROM evtc_event
            WHERE is_statechange != 0 AND is_statechange NOT IN ({placeholders})
            GROUP BY is_statechange
            ORDER BY cnt DESC
        ''')
        for row in cursor.fetchall():
            print(f'  SC={row[0]} count={row[1]:,}')
        
        # What normal events get filtered
        print()
        print('=== Filtered normal events ===')
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0
              AND buff = 0 AND is_activation = 0 AND value = 0 AND buff_dmg = 0 AND value >= 0
        ''')
        filtered_normal = cursor.fetchone()[0]
        print(f'  Normal events with no damage, no activation, no buff: {filtered_normal:,}')
        
        # Space savings estimation
        print()
        print('=== Space savings estimation ===')
        avg_row_bytes = 190  # data + index per row
        saved_mb = filter_count * avg_row_bytes / 1024 / 1024
        core_mb = core_total * avg_row_bytes / 1024 / 1024
        print(f'  Current total: ~{(total * avg_row_bytes / 1024 / 1024):.1f} MB')
        print(f'  After filter: ~{core_mb:.1f} MB')
        print(f'  Saved: ~{saved_mb:.1f} MB ({filter_pct:.1f}%)')
        
        # Daily ingestion estimate (assuming 50 logs/day, avg 300k events each)
        print()
        print('=== Daily ingestion projection ===')
        daily_logs = 50
        daily_events_per_log = 300000
        daily_total = daily_logs * daily_events_per_log
        daily_core = daily_total * (core_total / total)
        daily_saved = daily_total - daily_core
        print(f'  Before filter: {daily_total:,} events/day')
        print(f'  After filter: {daily_core:,.0f} events/day')
        print(f'  Saved: {daily_saved:,.0f} events/day')
        
finally:
    conn.close()
