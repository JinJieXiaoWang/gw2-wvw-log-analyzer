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
        print('=== Indexes on evtc_event ===')
        cursor.execute("SHOW INDEX FROM evtc_event")
        for row in cursor.fetchall():
            print(f'  {row[2]}: column={row[4]} unique={row[1]} cardinality={row[6]}')
        
        print()
        print('=== Table info ===')
        cursor.execute("SHOW TABLE STATUS LIKE 'evtc_event'")
        row = cursor.fetchone()
        print(f'  Engine: {row[1]}')
        print(f'  Row_format: {row[3]}')
        print(f'  Avg_row_length: {row[5]}')
        print(f'  Data_length: {row[6]:,}')
        print(f'  Index_length: {row[8]:,}')
        print(f'  Auto_increment: {row[10]}')
        
        cursor.execute('SELECT COUNT(*) FROM evtc_event')
        exact_count = cursor.fetchone()[0]
        print(f'Exact row count: {exact_count:,}')
        print(f'Avg bytes per row (data): {row[6] / exact_count:.1f}')
        print(f'Avg bytes per row (index): {row[8] / exact_count:.1f}')
        
        print()
        print('=== Partition info ===')
        cursor.execute('''
            SELECT partition_name, table_rows, data_length, index_length
            FROM information_schema.partitions
            WHERE table_schema = DATABASE() AND table_name = 'evtc_event'
        ''')
        parts = cursor.fetchall()
        if parts and len(parts) > 1:
            for p in parts:
                print(f'  {p[0]}: rows={p[1]} data={p[2]} index={p[3]}')
        else:
            print('  Not partitioned (or single partition)')
        
        print()
        print('=== Potential duplicate events ===')
        cursor.execute('''
            SELECT log_id, time, src_agent, dst_agent, skill_id, value, COUNT(*) as cnt
            FROM evtc_event
            WHERE is_statechange = 0
            GROUP BY log_id, time, src_agent, dst_agent, skill_id, value
            HAVING cnt > 5
            ORDER BY cnt DESC
            LIMIT 10
        ''')
        for row in cursor.fetchall():
            print(f'  log_id={row[0]} time={row[1]} skill={row[4]} count={row[6]}')
        
        print()
        print('=== Exact duplicate count (all fields) ===')
        cursor.execute('''
            SELECT SUM(dup_count) as total_dups
            FROM (
                SELECT COUNT(*) as dup_count
                FROM evtc_event
                GROUP BY log_id, event_index, time, src_agent, dst_agent, value, buff_dmg, 
                         overstack_value, skill_id, src_instid, dst_instid, src_master_instid, 
                         dst_master_instid, iff, buff, result, is_activation, is_buffremove, 
                         is_ninety, is_fifty, is_moving, is_statechange, is_flanking, is_shields, is_offcycle
                HAVING COUNT(*) > 1
            ) t
        ''')
        dup_count = cursor.fetchone()[0]
        print(f'  Total duplicate rows: {dup_count or 0:,}')
        
finally:
    conn.close()
