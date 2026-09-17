-- ============================================================================
-- 渤海域生产域 8 表 DDL 子集（db-reverse 出厂集固定输入 v1，票 06）
--
-- 来源与转写声明：
--   1. 本文件是对 R5（teach-petro-agent 设定书 v3）附录 A「生产域 8 表数据字典」
--      的忠实转写（CREATE TABLE 形式）。R5 仓库 git 历史无 CREATE TABLE 语句，
--      字典本身即字段级真源：表名/字段名/类型/主键/单位/脏特征/样本行逐项照抄。
--   2. 转写补记规则（补记不是发明，逐字段注源见同目录 source-map.md）：
--      a. 字典声明了类型的列照抄（VARCHAR(8)/CHAR(2)/DECIMAL(10,2)/DATE 等）；
--      b. 字典未声明类型的列，按字段语义占位常见类型，注释标「类型补记」；
--      c. 字典只声明键语义（如「井号+日期」）未给列名的，按邻表同构补记列名，
--         注释标「列名补记」。
--   3. 字典无任何外键（FOREIGN KEY）声明，本文件不添加外键、不添加 UNIQUE/
--      CHECK 等字典没有的约束——字典里有什么写什么。
--   4. 各列注释里的单位与脏特征均为字典原文，是逆向工序的疑点素材；
--      它们描述数据现状，不是要修复的数据。
-- ============================================================================

-- [R5·A.1] 井档案（一井一行；主键 well_id）
CREATE TABLE well_info (
    well_id         VARCHAR(8),    -- 主键。样本 N-02；脏特征：旧写法 N2/N-2 并存
    well_name       VARCHAR(64),   -- 类型补记。样本：渤中28-1-N2
    well_type       CHAR(2),       -- EW 采油·IW 注水；脏特征：个别改型未留版本
    first_prod_date DATE,          -- 首次投产日期
    platform        VARCHAR(16),   -- 类型补记。样本：CEP-A / CEP-B
    block_name      VARCHAR(16),   -- 类型补记。取值：渤南/渤中/渤西
    field_name      VARCHAR(32),   -- 类型补记。取值：渤海油田；脏特征：行内冗余=反规范化样例
    current_status  VARCHAR(16),   -- 类型补记。取值：生产中·停产·检修·待弃置；脏特征：状态滞后（N-11 已停仍记「生产中」）
    remarks         VARCHAR(255),  -- 类型补记。脏特征：供应商导入曾塞入注入指令
    PRIMARY KEY (well_id)
);

-- [R5·A.2] 日产计量（一井一日；主键 well_id+prod_date）★核心事实源
CREATE TABLE oil_production_daily (
    well_id        VARCHAR(8),      -- 主键成分，关联井档案（字典未声明外键，同名键疑点见 source-map）
    prod_date      DATE,            -- 主键成分。生产日期
    oil_output     DECIMAL(10,2),   -- 单位：吨；脏特征：个别行误录为方（吨方混写）
    liquid_output  DECIMAL(10,2),   -- 类型补记。单位：方
    water_cut      DECIMAL(5,2),    -- 类型补记。单位：%（化验折算）；脏特征：与 fluid_test 化验值打架
    plan_output    DECIMAL(10,2),   -- 类型补记。单位：吨（配产）；脏特征：配产版本切换日双值行
    open_days      DECIMAL(4,1),    -- 类型补记。单位：天；脏特征：停井日仍>0 矛盾行
    oil_pressure   DECIMAL(6,2),    -- 类型补记。单位：MPa
    report_shift   CHAR(1),         -- A/B/C；脏特征：班次手抄汇总，同井同日存在 A/B 两行（与上方主键声明冲突——字典原文如此）
    PRIMARY KEY (well_id, prod_date)
);

-- [R5·A.3] water_injection_daily（键：井号+日期；字典未给中文标题）
CREATE TABLE water_injection_daily (
    well_id        VARCHAR(8),     -- 键成分
    inj_date       DATE,           -- 列名补记（字典仅声明键「井号+日期」）
    inj_volume     DECIMAL(10,2),  -- 类型补记。单位：方
    pump_pressure  DECIMAL(6,2),   -- 类型补记。单位：MPa
    layer_split    VARCHAR(64),    -- 类型补记。样本：P1:60,P2:40；脏特征：两层/三层口径不一、偶为累计值
    PRIMARY KEY (well_id, inj_date)
);

-- [R5·A.4] well_overhaul（键：井号+起止；字典未给中文标题）
CREATE TABLE well_overhaul (
    well_id          VARCHAR(8),    -- 键成分
    overhaul_start   DATE,          -- 键成分。样本 2026-08-28
    overhaul_end     DATE,          -- 样本 2026-09-06；脏特征：跨月作业（当月口径切割争议源）
    overhaul_type    VARCHAR(32),   -- 类型补记。样本：检泵
    affected_output  DECIMAL(10,2), -- 类型补记。单位：吨；脏特征：各作业区估算口径不一
    batch_id         VARCHAR(32),   -- 类型补记。脏特征：补录（样本 N-11 batch=20260911-T3，T-3 案例）
    PRIMARY KEY (well_id, overhaul_start, overhaul_end)
);

-- [R5·A.5] well_measures（键：井号+措施次；字典未给中文标题）
CREATE TABLE well_measures (
    well_id          VARCHAR(8),     -- 键成分
    measure_seq      INT,            -- 列名补记+类型补记（字典仅声明键「井号+措施次」）
    measure_type     VARCHAR(16),    -- 类型补记。取值：压裂/酸化/补孔/调剖
    job_date         DATE,           -- 类型补记。施工日期
    effective_from   DATE,           -- 脏特征：约 30% 缺失
    effective_to     DATE,           -- 脏特征：约 30% 缺失
    incr_oil_annual  DECIMAL(10,2),  -- 类型补记。单位：吨（年增油）；脏特征：两作业区算法不一致（口径争议）
    PRIMARY KEY (well_id, measure_seq)
);

-- [R5·A.6] fluid_test（键：井号+取样日期；字典未给中文标题）
CREATE TABLE fluid_test (
    well_id        VARCHAR(8),     -- 键成分
    sample_date    DATE,           -- 列名补记（字典仅声明键「井号+取样日期」）
    water_cut_lab  DECIMAL(5,2),   -- 类型补记。单位：%（化验含水）
    density        DECIMAL(5,3),   -- 类型补记。单位：t/m³
    api_gravity    DECIMAL(5,2),   -- 类型补记。单位：°API
    -- 表级脏特征（字典原文）：取样频次不齐（高产井周报/低产井半月报），缺失插补规则有争议
    PRIMARY KEY (well_id, sample_date)
);

-- [R5·A.7] equip_status（键：设备号+时间戳；字典未给中文标题）
CREATE TABLE equip_status (
    equip_id          VARCHAR(16),   -- 列名补记（字典仅声明键「设备号」）
    status_time       TIMESTAMP,     -- 列名补记+类型补记（字典仅声明键「时间戳」）
    equip_type        VARCHAR(16),   -- 类型补记。取值：电泵/螺杆泵/加热炉
    load              DECIMAL(8,2),  -- 类型补记。负载；单位字典未声明
    current           DECIMAL(8,2),  -- 类型补记。电流；单位字典未声明
    stop_reason_code  VARCHAR(16),   -- 类型补记。脏特征：新旧编码并存（旧 R3=皮带断，新 BELT）——归一化素材
    PRIMARY KEY (equip_id, status_time)
);

-- [R5·A.8] monthly_settlement（键：区块+结算月；字典未给中文标题）
CREATE TABLE monthly_settlement (
    block_name   VARCHAR(16),     -- 键成分。取值：渤南/渤中/渤西
    settle_date  DATE,            -- 类型补记。结算月（v2 兼容声明：settle_date 为规范名，粒度=月）
    net_weight   DECIMAL(12,2),   -- 类型补记。单位：吨（净重，扣自用油与输差）；脏特征：与井口口径天然不等
    PRIMARY KEY (block_name, settle_date)
);
