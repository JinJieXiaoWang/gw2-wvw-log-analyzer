
-- Table: account_characters

CREATE TABLE account_characters (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	account_name VARCHAR(100) NOT NULL, 
	character_name VARCHAR(100) NOT NULL, 
	profession VARCHAR(50), 
	first_seen_date DATE NOT NULL, 
	last_seen_date DATE NOT NULL, 
	seen_count INTEGER, 
	PRIMARY KEY (id)
)



-- Table: builds

CREATE TABLE builds (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	slug VARCHAR(100) NOT NULL COMMENT 'URL标识', 
	title VARCHAR(100) NOT NULL COMMENT 'Build标题', 
	profession VARCHAR(50) NOT NULL COMMENT '职业名称', 
	profession_color VARCHAR(20) COMMENT '职业颜色(HEX)', 
	elite_spec VARCHAR(50) COMMENT '精英特长', 
	`role` VARCHAR(20) NOT NULL COMMENT '主角色: dps/support', 
	sub_roles JSON COMMENT '子角色列表: boon/heal/tank/cc', 
	armor_type VARCHAR(100) COMMENT '护甲类型', 
	weapons JSON COMMENT '武器配置(JSON)', 
	relic VARCHAR(100) COMMENT ' relic', 
	rune VARCHAR(100) COMMENT '符文', 
	food VARCHAR(100) COMMENT '食物', 
	wrench VARCHAR(100) COMMENT '扳手(通用技能)', 
	infusion VARCHAR(100) COMMENT '灌注', 
	attr_requirements JSON COMMENT '属性要求列表', 
	bd_code VARCHAR(255) NOT NULL COMMENT 'GW2 Build Code', 
	trait_lines JSON COMMENT '特性线配置(JSON)', 
	rotation_commands JSON COMMENT '循环指令(JSON)', 
	mechanics JSON COMMENT '机制说明(JSON)', 
	videos JSON COMMENT '视频链接(JSON)', 
	author VARCHAR(50) NOT NULL COMMENT '作者', 
	word_count INTEGER COMMENT '字数统计', 
	is_meta BOOL COMMENT '是否推荐配置', 
	created_at DATETIME COMMENT '创建时间' DEFAULT now(), 
	updated_at DATETIME COMMENT '更新时间' DEFAULT now(), 
	PRIMARY KEY (id)
)



-- Table: members

CREATE TABLE members (
	id INTEGER NOT NULL COMMENT '成员ID' AUTO_INCREMENT, 
	account_name VARCHAR(100) NOT NULL COMMENT '账号名称', 
	guild_tag VARCHAR(20) COMMENT '公会标签', 
	join_date DATE COMMENT '加入日期', 
	PRIMARY KEY (id)
)



-- Table: storage_cleanup_records

CREATE TABLE storage_cleanup_records (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	cleanup_type VARCHAR(50) NOT NULL COMMENT '清理类型：manual/auto/scheduled', 
	start_time DATETIME COMMENT '开始时间' DEFAULT now(), 
	end_time DATETIME COMMENT '结束时间', 
	files_deleted INTEGER COMMENT '删除文件数', 
	space_freed FLOAT COMMENT '释放空间（字节）', 
	status VARCHAR(20) COMMENT '状态：in_progress/completed/failed', 
	error_message TEXT COMMENT '错误信息', 
	triggered_by VARCHAR(100) COMMENT '触发者', 
	PRIMARY KEY (id)
)



-- Table: storage_monitor_records

CREATE TABLE storage_monitor_records (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	record_time DATETIME COMMENT '记录时间' DEFAULT now(), 
	total_size FLOAT NOT NULL COMMENT '总存储使用量（字节）', 
	file_count INTEGER NOT NULL COMMENT '文件总数', 
	log_file_count INTEGER COMMENT '日志文件数量', 
	warning_triggered BOOL COMMENT '是否触发警告', 
	PRIMARY KEY (id)
)



-- Table: sys_dict_data

CREATE TABLE sys_dict_data (
	dict_code INTEGER NOT NULL AUTO_INCREMENT, 
	dict_sort INTEGER NOT NULL COMMENT '排序顺序', 
	dict_label VARCHAR(200) NOT NULL COMMENT '字典标签', 
	dict_value VARCHAR(200) NOT NULL COMMENT '字典值', 
	dict_type VARCHAR(100) NOT NULL COMMENT '字典类型', 
	data_type VARCHAR(100) COMMENT '数据类型', 
	css_class VARCHAR(200) COMMENT 'CSS样式类/颜色值', 
	list_class VARCHAR(100) COMMENT '列表样式类', 
	is_default INTEGER NOT NULL COMMENT '是否默认值：0-否，1-是', 
	status INTEGER NOT NULL COMMENT '状态：0-启用，1-禁用', 
	remark TEXT COMMENT '备注说明', 
	PRIMARY KEY (dict_code), 
	CONSTRAINT _dict_type_value_uc UNIQUE (dict_type, dict_value)
)



-- Table: sys_dict_type

CREATE TABLE sys_dict_type (
	dict_id INTEGER NOT NULL AUTO_INCREMENT, 
	dict_type VARCHAR(100) NOT NULL COMMENT '字典类型编码', 
	dict_name VARCHAR(200) NOT NULL COMMENT '字典类型名称', 
	status INTEGER NOT NULL COMMENT '状态：0-启用，1-禁用', 
	sort_order INTEGER NOT NULL COMMENT '排序顺序', 
	remark TEXT COMMENT '备注说明', 
	is_system INTEGER NOT NULL COMMENT '是否系统预置：0-否，1-是', 
	PRIMARY KEY (dict_id)
)



-- Table: sys_user

CREATE TABLE sys_user (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	username VARCHAR(50) NOT NULL COMMENT '用户名', 
	password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希', 
	`role` VARCHAR(20) NOT NULL COMMENT '角色：super_admin/operator/user/guest', 
	is_active BOOL COMMENT '是否启用', 
	is_predefined BOOL NOT NULL COMMENT '是否预定义', 
	email VARCHAR(100) COMMENT '邮箱', 
	created_at DATETIME COMMENT '创建时间' DEFAULT now(), 
	last_login DATETIME COMMENT '最后登录时间', 
	token_version INTEGER NOT NULL COMMENT '令牌版本（用于密码修改后使旧token失效）', 
	PRIMARY KEY (id)
)



-- Table: ai_reports

CREATE TABLE ai_reports (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	report_type VARCHAR(50) NOT NULL COMMENT '报告类型', 
	target_type VARCHAR(50) NOT NULL COMMENT '目标类型', 
	target_id INTEGER NOT NULL COMMENT '目标ID', 
	content TEXT NOT NULL COMMENT '报告内容', 
	summary TEXT COMMENT '报告摘要', 
	ai_score FLOAT COMMENT 'AI评分', 
	created_by INTEGER COMMENT '创建者ID', 
	created_at DATETIME COMMENT '创建时间' DEFAULT now(), 
	is_public INTEGER COMMENT '是否公开', 
	is_deleted INTEGER COMMENT '是否删除', 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by) REFERENCES sys_user (id)
)



-- Table: batch_parse_tasks

CREATE TABLE batch_parse_tasks (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	task_name VARCHAR(255) COMMENT '任务名称', 
	status VARCHAR(20) COMMENT '状态：pending/processing/completed/failed/partial', 
	total_count INTEGER COMMENT '总数量', 
	processed_count INTEGER COMMENT '已处理数量', 
	success_count INTEGER COMMENT '成功数量', 
	failed_count INTEGER COMMENT '失败数量', 
	created_at DATETIME COMMENT '创建时间' DEFAULT now(), 
	started_at DATETIME COMMENT '开始时间', 
	completed_at DATETIME COMMENT '完成时间', 
	created_by INTEGER COMMENT '创建者ID', 
	error_message TEXT COMMENT '错误信息', 
	log_ids JSON COMMENT '日志ID列表', 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by) REFERENCES sys_user (id)
)



-- Table: evtc_log

CREATE TABLE evtc_log (
	log_id BIGINT NOT NULL COMMENT '日志实例主键' AUTO_INCREMENT, 
	log_uuid CHAR(36) NOT NULL COMMENT '全局唯一UUID(v4)', 
	filename VARCHAR(255) NOT NULL COMMENT '原始上传文件名', 
	file_sha256 CHAR(64) NOT NULL COMMENT '原始文件SHA-256指纹(去重用)', 
	file_size_compressed INTEGER NOT NULL COMMENT 'zevtc压缩后大小(字节)', 
	file_size_raw INTEGER NOT NULL COMMENT 'evtc解压后大小(字节)', 
	file_path VARCHAR(500) COMMENT '文件存储路径', 
	parse_status ENUM('pending','parsing','completed','failed','partial') NOT NULL COMMENT '解析状态', 
	parse_time_ms INTEGER COMMENT '解析耗时(毫秒)', 
	dps_report_permalink VARCHAR(500) COMMENT 'dps.report 报告链接', 
	parsed_at DATETIME COMMENT '解析完成时间', 
	error_message TEXT COMMENT '解析失败时的错误信息', 
	upload_time DATETIME COMMENT '上传时间，毫秒精度' DEFAULT now(), 
	upload_ip VARCHAR(50) COMMENT '上传者IP地址', 
	uploaded_by INTEGER COMMENT '上传者ID', 
	PRIMARY KEY (log_id), 
	UNIQUE (log_uuid), 
	UNIQUE (file_sha256), 
	FOREIGN KEY(uploaded_by) REFERENCES sys_user (id)
)



-- Table: batch_parse_task_items

CREATE TABLE batch_parse_task_items (
	id INTEGER NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	task_id INTEGER NOT NULL COMMENT '关联任务ID', 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	status VARCHAR(20) COMMENT '状态：pending/processing/completed/failed/retrying', 
	started_at DATETIME COMMENT '开始时间', 
	completed_at DATETIME COMMENT '完成时间', 
	error_message TEXT COMMENT '错误信息', 
	retry_count INTEGER COMMENT '已重试次数', 
	max_retries INTEGER COMMENT '最大重试次数', 
	next_retry_at DATETIME COMMENT '下次重试时间', 
	error_code VARCHAR(50) COMMENT '错误代码：429/timeout/parse_error/unknown', 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES batch_parse_tasks (id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id)
)



-- Table: ei_phase

CREATE TABLE ei_phase (
	phase_id BIGINT NOT NULL COMMENT '主键ID' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	phase_index INTEGER NOT NULL COMMENT '阶段索引', 
	name VARCHAR(100) NOT NULL COMMENT '阶段名称', 
	start_ms INTEGER NOT NULL COMMENT '阶段开始时间（毫秒）', 
	end_ms INTEGER NOT NULL COMMENT '阶段结束时间（毫秒）', 
	breakbar_phase SMALLINT COMMENT '是否为破蔑视阶段（1=是，0=否）', 
	targets_json JSON COMMENT '目标信息JSON', 
	PRIMARY KEY (phase_id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id) ON DELETE CASCADE
)



-- Table: ei_player

CREATE TABLE ei_player (
	player_id BIGINT NOT NULL COMMENT '主键ID' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	agent_index INTEGER COMMENT '关联evtc_agent索引', 
	account VARCHAR(100) COMMENT '玩家账户名', 
	character_name VARCHAR(100) NOT NULL COMMENT '角色名称', 
	profession VARCHAR(50) NOT NULL COMMENT '职业', 
	group_id SMALLINT COMMENT '小队编号（1-5）', 
	has_commander_tag SMALLINT COMMENT '是否有指挥官标记（1=是，0=否）', 
	is_fake SMALLINT COMMENT '是否为假玩家（宠物、召唤物等）', 
	weapons_json JSON COMMENT '武器配置JSON', 
	consumables_json JSON COMMENT '食物与扳手配置JSON', 
	dps_all_json JSON COMMENT 'dpsAll数组JSON', 
	stats_all_json JSON COMMENT 'statsAll数组JSON', 
	defenses_json JSON COMMENT 'defenses数组JSON', 
	support_json JSON COMMENT 'support数组JSON', 
	buff_uptimes_json JSON COMMENT 'buffUptimes数组JSON', 
	rotation_json JSON COMMENT 'rotation数组JSON', 
	death_recap_json JSON COMMENT 'deathRecap数组JSON', 
	PRIMARY KEY (player_id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id) ON DELETE CASCADE
)



-- Table: ei_report

CREATE TABLE ei_report (
	report_id BIGINT NOT NULL COMMENT '自增主键' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志', 
	report_type VARCHAR(50) NOT NULL COMMENT '报告类型: detailed_wvw, raid, fractal', 
	ei_version VARCHAR(50) COMMENT 'EI 解析器版本，如 3.21.1.0', 
	summary_json JSON COMMENT 'EI 报告摘要数据(JSON)', 
	log_data_path VARCHAR(500) COMMENT '完整 _logData JSON 压缩文件路径', 
	graph_data_path VARCHAR(500) COMMENT '完整 _graphData JSON 压缩文件路径', 
	cr_data_path VARCHAR(500) COMMENT 'Combat Replay 数据压缩文件路径', 
	log_name VARCHAR(200) COMMENT '战斗名称', 
	duration_ms BIGINT COMMENT '战斗时长(毫秒)', 
	player_count BIGINT COMMENT '玩家数量', 
	target_count BIGINT COMMENT '目标数量', 
	success VARCHAR(10) COMMENT '是否成功', 
	recorded_by VARCHAR(100) COMMENT '录制者角色名', 
	recorded_account_by VARCHAR(100) COMMENT '录制者账号', 
	map_id BIGINT COMMENT '地图ID', 
	region VARCHAR(50) COMMENT '服务器区域', 
	wvw VARCHAR(10) COMMENT '是否为WvW', 
	created_at DATETIME COMMENT '记录创建时间' DEFAULT now(), 
	updated_at DATETIME COMMENT '记录更新时间' DEFAULT now(), 
	PRIMARY KEY (report_id), 
	UNIQUE (log_id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id) ON DELETE CASCADE
)



-- Table: ei_skill_map

CREATE TABLE ei_skill_map (
	map_id BIGINT NOT NULL COMMENT '主键ID' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	skill_key VARCHAR(20) NOT NULL COMMENT 'JSON中的技能键(s12345)', 
	gw2_skill_id INTEGER NOT NULL COMMENT 'GW2官方技能ID', 
	name VARCHAR(100) COMMENT '技能名称', 
	auto_attack SMALLINT COMMENT '是否为自动攻击（1=是，0=否）', 
	can_crit SMALLINT COMMENT '是否可暴击（1=是，0=否）', 
	is_swap SMALLINT COMMENT '是否为武器切换（1=是，0=否）', 
	is_instant_cast SMALLINT COMMENT '是否为瞬发（1=是，0=否）', 
	is_trait_proc SMALLINT COMMENT '是否为特性触发（1=是，0=否）', 
	icon VARCHAR(500) COMMENT '技能图标URL', 
	PRIMARY KEY (map_id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id) ON DELETE CASCADE
)



-- Table: ei_target

CREATE TABLE ei_target (
	target_id BIGINT NOT NULL COMMENT '主键ID' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	agent_index INTEGER COMMENT '关联evtc_agent索引', 
	name VARCHAR(100) NOT NULL COMMENT '目标名称', 
	enemy_player SMALLINT COMMENT '是否为敌方玩家（1=是，0=否）', 
	total_health BIGINT COMMENT '总生命值', 
	final_health BIGINT COMMENT '最终生命值', 
	health_percent_burned INTEGER COMMENT '生命燃烧百分比', 
	dps_all_json JSON COMMENT 'dpsAll数组JSON', 
	defenses_json JSON COMMENT 'defenses数组JSON', 
	PRIMARY KEY (target_id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id) ON DELETE CASCADE
)



-- Table: fights

CREATE TABLE fights (
	id INTEGER NOT NULL COMMENT '战斗记录ID' AUTO_INCREMENT, 
	log_id BIGINT NOT NULL COMMENT '关联日志ID', 
	start_time DATETIME NOT NULL COMMENT '战斗开始时间', 
	end_time DATETIME COMMENT '战斗结束时间', 
	duration_sec INTEGER COMMENT '战斗时长(秒)', 
	duration_ms BIGINT COMMENT '战斗时长(毫秒)', 
	map_name VARCHAR(100) COMMENT '地图名称', 
	server_name VARCHAR(100) COMMENT '服务器名称', 
	recorded_by VARCHAR(100) COMMENT '录制者角色名', 
	recorded_account VARCHAR(100) COMMENT '录制者账号', 
	total_damage BIGINT COMMENT '总伤害量', 
	total_healing BIGINT COMMENT '总治疗量', 
	kill_count INTEGER COMMENT '击杀数', 
	death_count INTEGER COMMENT '死亡数', 
	player_count INTEGER COMMENT '玩家数量', 
	is_ai_analyzed BOOL COMMENT '是否已完成AI分析', 
	created_at DATETIME COMMENT '记录创建时间' DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(log_id) REFERENCES evtc_log (log_id)
)



-- Table: fight_stats

CREATE TABLE fight_stats (
	id INTEGER NOT NULL COMMENT '主键ID' AUTO_INCREMENT, 
	fight_id INTEGER NOT NULL COMMENT '关联战斗记录ID', 
	member_id INTEGER NOT NULL COMMENT '关联成员记录ID', 
	account VARCHAR(100) NOT NULL COMMENT '玩家账户名', 
	character_name VARCHAR(100) COMMENT '角色名称', 
	profession VARCHAR(50) COMMENT '职业', 
	group_id INTEGER COMMENT '小队编号（1-5）', 
	team_id INTEGER COMMENT '队伍ID（0=蓝队，1=红队，2=绿队）', 
	has_commander_tag INTEGER COMMENT '是否有指挥官标记（1=是，0=否）', 
	damage BIGINT COMMENT '总伤害量', 
	dps INTEGER COMMENT '每秒伤害', 
	power_damage BIGINT COMMENT '直伤伤害', 
	condi_damage BIGINT COMMENT '症状伤害', 
	breakbar_damage BIGINT COMMENT '破蔑视伤害', 
	healing BIGINT COMMENT '治疗量', 
	critical_rate NUMERIC(5, 2) COMMENT '暴击率（百分比）', 
	flanking_rate NUMERIC(5, 2) COMMENT '背击率（百分比）', 
	glance_rate NUMERIC(5, 2) COMMENT '偏斜率（百分比）', 
	missed INTEGER COMMENT '未命中次数', 
	killed INTEGER COMMENT '击杀敌人数量', 
	downed INTEGER COMMENT '击倒敌人数量', 
	interrupts INTEGER COMMENT '打断次数', 
	swap_count INTEGER COMMENT '切换目标次数', 
	damage_taken BIGINT COMMENT '承受伤害量', 
	blocked_count INTEGER COMMENT '格挡次数', 
	evaded_count INTEGER COMMENT '闪避次数', 
	dodge_count INTEGER COMMENT '翻滚次数', 
	down_count INTEGER COMMENT '倒地次数', 
	dead_count INTEGER COMMENT '死亡次数', 
	boon_strips INTEGER COMMENT '移除增益次数', 
	condition_cleanses INTEGER COMMENT '清除症状次数', 
	resurrects INTEGER COMMENT '复活队友次数', 
	condi_cleanse_ally INTEGER COMMENT '清除队友症状次数', 
	boon_strips_ally INTEGER COMMENT '移除队友增益次数', 
	might_uptime NUMERIC(5, 2) COMMENT '力量覆盖（百分比）', 
	fury_uptime NUMERIC(5, 2) COMMENT '狂怒覆盖（百分比）', 
	quickness_uptime NUMERIC(5, 2) COMMENT '急速覆盖（百分比）', 
	alacrity_uptime NUMERIC(5, 2) COMMENT '敏捷覆盖（百分比）', 
	protection_uptime NUMERIC(5, 2) COMMENT '保护覆盖（百分比）', 
	stability_uptime NUMERIC(5, 2) COMMENT '稳定覆盖（百分比）', 
	ai_score NUMERIC(5, 2) COMMENT 'AI评分', 
	score_grade VARCHAR(10) COMMENT '评分等级（S/A/B/C/D）', 
	PRIMARY KEY (id), 
	FOREIGN KEY(fight_id) REFERENCES fights (id), 
	FOREIGN KEY(member_id) REFERENCES members (id)
)


