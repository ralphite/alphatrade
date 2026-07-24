# Form 345 内部人交易数据管线

SEC 官方 **Insider Transactions Data Sets（Form 3/4/5 结构化季度数据）** → 内部人公开市场买入表 →
集群买入事件表。为 survey 评分 9.0 的 **insider cluster buying** 假设提供可回测的事件表。

代码：`src/insider_pipeline.py`｜数据源页面：
<https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets>

---

## 1. 快速使用

```bash
.venv/bin/python src/insider_pipeline.py all        # 下载 + 解析 + 集群 + 统计（全量约 20 分钟）

# 或分步
.venv/bin/python src/insider_pipeline.py download   # 只补新季度（已存在的 zip 自动跳过）
.venv/bin/python src/insider_pipeline.py buys       # zip → data/insider_buys.parquet（约 3 分钟）
.venv/bin/python src/insider_pipeline.py clusters   # buys → data/insider_clusters.csv（约 30 秒）
.venv/bin/python src/insider_pipeline.py stats      # 打印汇总统计

# 换集群口径（不覆盖默认产物之前记得先备份 csv）
.venv/bin/python src/insider_pipeline.py clusters --min-insiders 3 --min-value 100000 --window 5
```

**季度更新**：SEC 在季度结束后约 5 周发布（2026Q1 于 2026-04-06 发布）。跑 `download` 会自动
探测新季度，未发布的返回 404 并跳过；然后重跑 `buys` + `clusters` 即可。

依赖：`pandas`、`requests`、`pyarrow`（写 parquet；缺失时自动退回 `data/insider_buys.csv.gz`）。
SEC 合规：User-Agent = `alphatrade research ralph.wen@gmail.com`，请求间隔 0.4s。

---

## 2. 文件

| 路径 | 内容 | 大小 |
|---|---|---|
| `data/form345/zip/{YYYY}q{N}_form345.zip` | SEC 原始季度 zip，**2015Q4 – 2026Q1 共 42 个** | 425 MB |
| `data/form345/parse_log.csv` | 每季度的原始/丢弃/保留行数（数据质量留痕） | 2 KB |
| `data/insider_buys.parquet` | **每行 = 一笔内部人公开市场买入** | 7.8 MB / 305,350 行 |
| `data/insider_clusters.csv` | **每行 = 一个集群买入事件**（主交付物） | 2.1 MB / 7,909 行 |

zip 与 parquet 已进 `.gitignore`（可从 SEC 重新生成）。解压出的 TSV 只在内存里过一遍，
每季度处理完立刻删除 `data/form345/_tmp/`，磁盘峰值 < 550 MB。

---

## 3. 过滤口径（`buys` 步骤）

从 `NONDERIV_TRANS.tsv` 起手，逐条与 `SUBMISSION.tsv`（申报日/发行人/ticker/10b5-1）和
`REPORTINGOWNER.tsv`（内部人身份）拼接：

| 规则 | 理由 |
|---|---|
| `TRANS_CODE == 'P'` 且 `TRANS_ACQUIRED_DISP_CD == 'A'` | 只要公开市场买入，排除授予/行权/赠与/扣税卖出 |
| `DOCUMENT_TYPE ∈ {4, 4/A}` | 剔除 Form 3（初始持仓，无交易）与 Form 5（年度补报，实测中位金额仅 $620 且天然迟报） |
| `AFF10B5ONE` 为真 → **丢弃** | 10b5-1 计划性买入不含信息（见下方覆盖率警告） |
| 股数 > 0 且价格 > 0 | 无价格无法算金额（约占 P 行 2–3%） |
| 单价 ≤ $1,000,000/股 | 申报人把总金额填进单价栏（见坑 #6） |
| ticker 可归一化 | 剔除 `NONE`/`N/A`/空及无法归属的自由文本（见坑 #7） |
| `TRANS_DATE ≤ FILING_DATE` | 数据录入错误，全样本仅 42 行 |
| 跨 accession 去重 | 4/A 修正单会把原始单的交易重报一遍（全样本 4,565 行） |

### 已知坑（改代码前必读）

1. **同一张 Form 4 内部出现两行完全一样的交易是合法的**（同日不同账户/经纪商分笔，实测占
   "重复行" 的 87%）。去重必须**只跨 accession 做**，代码里用 `_occ` 组内序号保留重数。
   一刀切 `drop_duplicates` 会系统性低估买入金额约 9%。
2. **一张 Form 4 可以有多个 reporting owner**（基金系 GP/LP/个人联合申报，占 P 类申报行的
   8–32%）。因此交易行**不按 owner 展开**（展开会让金额翻倍），owner 折叠进 `owner_ciks`
   管道分隔字段；集群里数"不同内部人"用并查集（见 §4）。
3. **`AFF10B5ONE` 2023 年才有数据**。SEC 2022-12 才在 Form 4 封面加上 10b5-1 勾选框：
   字段非空率 2016–2022 < 2%，2023 年 82%，2024 年起 100%。
   → **2023 年之前的 10b5-1 剔除等于没做**。回测若要跨年比较，必须把这个覆盖率断点当作
   已知的样本构成变化处理（或干脆只在 2024+ 上做 10b5-1 分层）。
   兜底字段 `flag_10b5_1_footnote`（脚注文本里出现 "10b5-1"）全期可用，但它是 accession
   级匹配、会误伤同一张申报单里的其他交易，故**只做 flag 不做删除**。
4. **`TRANS_PRICEPERSHARE` 是 SEC 数据集里的 2 位小数值**，与 Form 4 XML 原始值可能差
   ~0.01%（实测 QDEL 案例：XML 23.5921 vs 数据集 23.59）。对金额门槛无实质影响。
5. **2016 年之前的交易日不代表覆盖**。管线只拉 2015Q4 起的申报；`trans_date` 出现 2001–2015
   的行全部是**迟报**（有一笔滞后 8,767 天）。买入表按 `trans_date` 分年统计时，2015 及更早
   的年份是残缺的，别拿来做时间序列。
6. **单价栏有申报人手误**。实测 KYN / NTG / TYG / DNP 等封闭式基金的单价填成 $5,000,000
   （实际 $5–20/股），OTIVF 填成 $1,040,000。管线按 `price > $1,000,000` 硬丢弃 —— 上限设在
   $1M 是因为全样本最贵的**真实**标的是 BRK.A（~$408k/股，113 笔），一刀切到几万会误杀它。
   **股数栏的同类手误无法用绝对阈值拦**（把总额填进股数栏），残留最大单笔金额达 $24.8 万亿。
   集群表因此提供 `max_trans_value_usd` 列：**回测前建议先按它过滤**（`> $1e8` 的事件 70 个，
   `> $1e9` 的 29 个，其中 COTY $1.75B、SYNT $3.4B 是真实的 PE/并购交易，不是错误，但对
   $100k 级别的组合同样没有意义）。
7. **`ISSUERTRADINGSYMBOL` 是自由文本**，实测垃圾形态：交易所前缀（`NYSE:FBC`、`ASX:CRN`）、
   引号/括号包裹（`"""TARA"""`、`(CALX)`、`?OSH?`、`AREN]`）、双重股权并列
   （`ISCA, ISCB`、`HEI, HEI.A`、`UHAL,UHALB`）。清洗分三级：保守正则 → 同 `issuer_cik`
   众数回填 → 并列写法取第一个 token。**单字母 token 一律拒绝**（`N O G`、`Z AND ZG`）——
   猜成 `N` / `Z` 会映射到别家公司的真实 ticker，比丢掉这行危险得多。
   仅靠正则会丢掉 ISCA（1,026 行）、HEI、CRDA 这类"每次都写并列"的发行人，故第三级必需。

---

## 4. 集群检测口径（`clusters` 步骤）

**默认规则**：同一 `ISSUERCIK`，交易日滚动 **7 个日历日**内，**≥2 个不同内部人实体**买入，
且合计金额 **≥ $250,000**。

三个不那么显然的实现选择：

**(a) 发行人主键用 `ISSUERCIK` 不用 ticker。** ticker 会改名、会被退市公司复用；用 CIK 才不会
在回测里制造生存偏差（survey 预注册的致命风险 #5）。

**(b) "不同内部人" = 并查集连通分量，不是 distinct owner CIK。** 一张基金系联合申报单上可以
挂 10 个关联实体 CIK；按 distinct CIK 数，单张申报单就能凭空构成 "10 人集群"。做法：任意两张
申报单只要共享一个 owner CIK 就并成同一个内部人实体，再数连通分量。
残余风险：完全不共享 CIK 的关联实体（如 GP 与 LP 各自单独申报）仍会被算作 2 人 —— 用
`any_tenpercent` / `n_insiders_exec` 字段可以把这类筛掉。

**(c) 重叠的达标窗口会被合并成一个事件。** 先以每笔交易为锚点判定其后 7 日窗是否达标，再把
共享交易的达标窗口并成一个事件 —— 一段连续买入行动 = 一个事件，避免同一波买入生成几十个
高度重叠的样本、把回测的有效样本量灌水。代价是连续买了几个月的公司只出一个事件
（`full_trans_span_days` 可以看出跨度）。

### 4.1 `signal_date` —— 回测必须用这一列

**`signal_date` 才是无前视的建仓可得时点，不是 `last_filing_date`。**

一个 3 人集群可能在第 2 个人申报时就已经满足门槛，此时集群已经对公众可见；等到第 3 个人
申报（`last_filing_date`）才建仓会白白丢掉几天收益，而按 `first_trans_date` 建仓则是明目张胆
的前视。`signal_date` 的定义是：把事件成员按申报日逐日回放，**首次**出现"某个 7 日交易窗内
≥2 个内部人实体且合计 ≥$250k"的那一天。实测 39.0% 的事件 `signal_date < last_filing_date`。

**配套的前视防护**：主字段（`n_insiders` / `total_value_usd` / `has_ceo_or_cfo` / `n_trans` /
`first_trans_date` / `last_trans_date` / `avg_price` …）**一律只统计 `signal_date` 当天已申报可见
的那部分交易**。`full_*` 前缀的列是整段买入行动的事后口径，**只能用于描述统计，绝不能进
入筛选条件** —— 用 `full_total_value_usd > X` 过滤就是前视，因为那笔钱在建仓时还没申报。

### 4.2 集群表字段

| 列 | 说明 |
|---|---|
| `ticker` / `issuer_cik` / `issuer_name` | 发行人；**join 价格用 ticker，去重/配对用 cik** |
| **`signal_date`** | **信号可得日 = 建仓日的下限**（当日盘后可见，实际成交价应取 T+1） |
| `first_trans_date` / `last_trans_date` | PIT 可见买入的首笔/末笔交易日 |
| `last_filing_date` | 整段最后一笔的申报日（任务口径；**回测别用它建仓**） |
| `n_insiders` / `n_insiders_exec` | 内部人实体数（并查集）／其中 director+officer 的实体数 |
| `n_trans` | PIT 可见的买入笔数 |
| `total_value_usd` / `value_exec_usd` | PIT 合计金额／其中 director+officer 部分 |
| `total_shares` / `avg_price` | PIT 合计股数／成交均价（= 金额/股数） |
| `max_trans_value_usd` | PIT 内单笔最大金额，**离群过滤把手**（见 §3.6） |
| `has_ceo` / `has_cfo` / `has_ceo_or_cfo` | 头衔正则命中（`RPTOWNER_TITLE` + `RPTOWNER_TXT`） |
| `n_director_trans` / `n_officer_trans` | 由 director / officer 发起的买入笔数 |
| `any_tenpercent` | 是否含 10% 股东（PE/VC，与高管信念无关，36.5% 的事件含） |
| `any_10b5_1_footnote` | 脚注提到 10b5-1（早年 10b5-1 的唯一线索，见 §3.3） |
| `trans_span_days` | PIT 首末交易日跨度 |
| `signal_lag_days` | `signal_date - last_trans_date`，**信号新鲜度**，中位 1 天 |
| `filing_lag_days` | `last_filing_date - full_last_trans_date` |
| `full_n_insiders` / `full_n_trans` / `full_total_value_usd` / `full_last_trans_date` / `full_trans_span_days` | 事后口径，**禁止用于筛选** |
| `year` | `signal_date` 的年份 |

### 4.3 买入表字段（`insider_buys.parquet`）

`accession` / `issuer_cik` / `issuer_name` / `ticker` / `doc_type` / `security_title` /
`trans_date` / `filing_date` / `shares` / `price` / `value_usd` / `filing_lag_days` /
`owner_ciks`（管道分隔）/ `owner_names` / `n_filing_owners` / `is_director` / `is_officer` /
`is_tenpercent` / `is_other` / `is_ceo` / `is_cfo` / `owner_titles` / `direct_ownership` /
`aff10b5one_raw` / `flag_10b5_1` / `flag_10b5_1_footnote` / `src_quarter`

> 买入表不只是中间产物：**池内差分的对照池就在里面** —— "同期有 Form 4 买入但未构成集群"
> 的标的，正是 survey 预注册要求的第一类对照池。

---

## 5. 产出概况（2016-01-04 – 2026-03-31）

- 内部人买入 **305,350 笔**，7,500 个发行人
- 集群事件 **7,909 个**，覆盖 **3,570 个 ticker**（与 survey 推算的 ~8,800 同量级）
- 逐年 528–1,089 个事件；2020Q1（疫情抄底）500 个为季度峰值，2024 年 528 个为年度低谷
- 中位集群金额 **$765k**；**52%** 含 CEO 或 CFO；**42%** 有 ≥3 个内部人
- **申报滞后**：单笔买入中位 **2 天** / P90 5 天；集群 `signal_lag_days` 中位 **1 天** / P90 4 天。
  70.5% 的集群在末笔交易后 **≤2 天**即可见 —— 这正是 survey 里 Ozlen "70–80% alpha 发生在
  不可观测窗口内" 与 Kang "次月 +2.1%" 能同时为真的原因：可交易窗口确实只有 2 天。
- 尾部：2.8% 的事件 `signal_lag_days > 45` 天（10% 股东迟报，最长 3,204 天），**回测应预注册
  一条 `signal_lag_days ≤ N` 的过滤**，否则会混入信息早已失效的陈旧信号。
- 事件高度分散：1,838 个 ticker 只出现 1 次，中位 1 次，最多 25 次（CNBKA）。

### 与 survey 实测数的对账

survey（`research/survey/family_b_event.md`）在 2025Q1 用朴素口径数出 221 个集群，本管线同季
**173 个**。用本管线的数据复现朴素口径（按 ticker 分组、展开 owner CIK 计数、不做并查集）得
**250 个** —— 差异全部来自本管线更严的口径：并查集折叠联合申报、剔除 10b5-1、剔除 Form 5、
剔除无价格/坏 ticker 行、重叠窗口合并。方向正确，本管线更保守。

### 已知残留问题（不影响交付，但回测端要知道）

- **42 个事件存在 `(issuer_cik, signal_date)` 重复**（占 0.5%）：同一发行人两段交易日相隔较远
  的买入行动，因为迟报而在同一天浮出水面。回测建仓时应按 `(issuer_cik, signal_date)` 去重，
  否则会在同一标的同一天开两个仓。
- **3 行 `issuer_name` 为空**（申报人漏填），`issuer_cik` / `ticker` 正常。

---

## 6. 回测端的注意事项（本管线不做回测，只列交接项）

1. **建仓时点用 `signal_date` 的下一个可得价格**（章程 §4：永不用信号时刻价格）。
2. **只用 PIT 字段做筛选**，`full_*` 一律不得进入条件（§4.1）。
3. **对照池必须池内差分**：`insider_buys.parquet` 里"有买入但未构成集群"的标的 + 同日期/同市值
   分层的无事件池。survey 预注册的致命风险 #3：集群买入密集出现在市场大跌后（2018Q4 312 个、
   2020Q1 500 个），不做日期匹配测出来的是抄底 beta 不是 alpha。
4. **先跑流动性分层**（survey 致命风险 #2）：若 alpha 单调集中在 ADV < $1M 层 → 直接杀。
5. **10% 股东单列**（`any_tenpercent`，36.5%）；`n_insiders_exec ≥ 2` 是纯高管口径（84.6%）。
6. **10b5-1 剔除在 2023 年前无效**（§3.3），跨年比较时当作已知的样本构成断点。
7. **退市股**：用 `issuer_cik` 而非当前存活票池取价，否则系统性高估（survey 致命风险 #5）。
8. **先按 `max_trans_value_usd` 滤离群，再按 `(issuer_cik, signal_date)` 去重**（§5 已知残留问题）。
