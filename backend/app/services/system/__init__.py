# -*- coding: utf-8 -*-
"""
system 服务模块
包含：dashboard_service 等系统服务
"""

from .dashboard_service import (
    get_overview,
    get_trends,
    get_profession_distribution,
    get_map_stats,
    get_top_players,
    get_recent_fights,
    get_parse_status_distribution,
    get_ai_score_distribution,
    get_buff_overview,
)

# 服务接口聚合类
class DashboardService:
    def get_overview(self, db, days=30):
        return get_overview(db, days)
    
    def get_trends(self, db, days=30, metric="damage"):
        return get_trends(db, days, metric)
    
    def get_profession_distribution(self, db, days=30):
        return get_profession_distribution(db, days)
    
    def get_map_stats(self, db, days=30):
        return get_map_stats(db, days)
    
    def get_top_players(self, db, days=30, sort_by="damage", limit=20):
        return get_top_players(db, days, sort_by, limit)
    
    def get_recent_fights(self, db, limit=10):
        return get_recent_fights(db, limit)
    
    def get_parse_status_distribution(self, db):
        return get_parse_status_distribution(db)
    
    def get_ai_score_distribution(self, db, days=30):
        return get_ai_score_distribution(db, days)
    
    def get_buff_overview(self, db, days=30):
        return get_buff_overview(db, days)

dashboard_service = DashboardService()
