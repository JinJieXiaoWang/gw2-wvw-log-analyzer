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
        
        print('=== Core business needed: normal events ===')
        
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0 AND buff = 0 AND (value > 0 OR buff_dmg > 0)
        ''')
        dmg_events = cursor.fetchone()[0]
        print(f'  Damage events (buff=0, value>0 or buff_dmg>0): {dmg_events:,}')
        
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0 AND is_activation != 0
        ''')
        activation_events = cursor.fetchone()[0]
        print(f'  Skill activation events (is_activation!=0): {activation_events:,}')
        
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0 AND buff = 1
        ''')
        buff_events = cursor.fetchone()[0]
        print(f'  Buff events (buff=1): {buff_events:,}')
        
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0
              AND (buff = 1 OR is_activation != 0 OR value > 0 OR buff_dmg > 0)
        ''')
        core_normal = cursor.fetchone()[0]
        print(f'  Core normal events total (union): {core_normal:,}')
        print(f'  Normal events to filter: {676905 - core_normal:,} ({(676905 - core_normal) * 100 / 676905:.1f}% of normal)')
        
        print()
        print('=== Core business needed: statechange events ===')
        core_sc_values = [1, 2, 3, 4, 5, 6, 7, 11, 34, 37]
        placeholders = ','.join(str(v) for v in core_sc_values)
        cursor.execute(f'''
            SELECT is_statechange, COUNT(*) as cnt
            FROM evtc_event
            WHERE is_statechange IN ({placeholders})
            GROUP BY is_statechange
            ORDER BY cnt DESC
        ''')
        core_sc_total = 0
        for row in cursor.fetchall():
            print(f'  SC={row[0]} count={row[1]:,}')
            core_sc_total += row[1]
        
        cursor.execute(f'''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange != 0 AND is_statechange NOT IN ({placeholders})
        ''')
        filter_sc = cursor.fetchone()[0]
        print(f'  Core SC total: {core_sc_total:,}')
        print(f'  SC to filter: {filter_sc:,} ({filter_sc * 100 / 568179:.1f}% of statechange)')
        
        print()
        print('=== Summary ===')
        print(f'  Total events: {total:,}')
        print(f'  Core needed: {core_normal + core_sc_total:,}')
        print(f'  Can be filtered: {total - (core_normal + core_sc_total):,}')
        print(f'  Filter ratio: {(total - (core_normal + core_sc_total)) * 100 / total:.1f}%')
        
        print()
        print('=== Per-log core events vs total ===')
        cursor.execute('''
            SELECT 
                log_id,
                COUNT(*) as total,
                SUM(CASE WHEN is_statechange = 0 AND (buff = 1 OR is_activation != 0 OR value > 0 OR buff_dmg > 0) THEN 1 ELSE 0 END) as core_normal,
                SUM(CASE WHEN is_statechange IN (1,2,3,4,5,6,7,11,34,37) THEN 1 ELSE 0 END) as core_sc
            FROM evtc_event
            GROUP BY log_id
            ORDER BY total DESC
        ''')
        for row in cursor.fetchall():
            core_total = row[2] + row[3]
            print(f'  log_id={row[0]} total={row[1]:>7,} core={core_total:>7,} filter={row[1]-core_total:>7,} ({(row[1]-core_total)*100/row[1]:.1f}%)')
        
        print()
        print('=== Empty normal events ===')
        cursor.execute('''
            SELECT COUNT(*) FROM evtc_event
            WHERE is_statechange = 0 AND buff = 0 AND is_activation = 0 AND value = 0 AND buff_dmg = 0
        ''')
        empty_normal = cursor.fetchone()[0]
        print(f'  Count: {empty_normal:,} ({empty_normal * 100 / 676905:.1f}% of normal events)')
        
        cursor.execute('''
            SELECT result, COUNT(*) as cnt
            FROM evtc_event
            WHERE is_statechange = 0 AND buff = 0 AND is_activation = 0 AND value = 0 AND buff_dmg = 0
            GROUP BY result
            ORDER BY cnt DESC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(f'    result={row[0]} count={row[1]:,}')
        
        cursor.execute('''
            SELECT iff, COUNT(*) as cnt
            FROM evtc_event
            WHERE is_statechange = 0 AND buff = 0 AND is_activation = 0 AND value = 0 AND buff_dmg = 0
            GROUP BY iff
            ORDER BY cnt DESC
        ''')
        for row in cursor.fetchall():
            name = {0: 'FRIEND', 1: 'FOE', 2: 'UNKNOWN', 3: 'NPC'}.get(row[0], f'IFF_{row[0]}')
            print(f'    iff={name} count={row[1]:,}')
        
finally:
    conn.close()
