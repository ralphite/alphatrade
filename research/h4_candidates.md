# H4 候选清单 — 适合个人投资者（<$1M）的美股经典异象

生成时间：2026-07-10（周末研究窗口）
生成者：H4 研究 agent（WebSearch 2023-2026 文献/讨论 + 金融先验）
用途：下一阶段**日线粗筛回测**的输入清单。逐个进 backtest（无 LLM lookahead 问题，迭代最快）→ 存活者预注册 → forward paper。

---

## 0. 选材原则与本清单的读法

**硬门槛（全部满足才收录）**
- (a) 可用**日线 OHLCV + 基本面日历**（财报日期 / 指数事件 / IPO 日历 / FOMC 日历）回测，**不需要 tick / orderbook**。
- (b) **容量小**：机构做不了或看不上（微/小盘、单事件名义额小），<$1M 无冲击成本。
- (c) **信号频率高**：每周多个信号，能快速积累样本。
- (d) **持有期小时~数周**（低/中频）。

**排序轴**：按「**近年（2023-2026）仍有存活证据的强度**」从强到弱。注意这**不等于**「最适合本项目」——有的候选证据很强但净成本存疑（如短期反转），有的桶（日历/指数流）证据中等但机制最干净。每个候选都标注了 (a)(c) 的真实匹配度，便于按 backtest 队列筛选。

**规避红线（来自 H1 家族 495 样本的教训）**
> H1 家族（8-K 事件 T+0~2 交易）三方向全灭。机制遗产：明显文本事件在**盘后 30 分钟内定价完毕**、系统性**过冲**、过冲因**路径波动 + 成本不可交易**。
> ⟹ 本清单**刻意避开「读公开信息抢时间差」类机制**，全部偏向两类：
> 1. **结构性/机械性资金流**（指数调仓、ETF 再平衡、锁定期、月末再平衡、隔夜清算）——有人被合约/授权**强制**在可预测时点交易，你当流动性提供方收租；
> 2. **风险溢价 / 限制套利收割**（PEAD 微盘漂移、隔夜溢价、公告溢价）——套利成本高到机构不来，慢钱系统性underreact，你赚的是**结构补偿**而非信息。
>
> **关键区分**：本清单的 PEAD（#1）赚的是 T+1 之后**数周的慢漂移**（结构性 underreaction），不是 8-K 那种 T+0 抢定价——机制根本不同，不违反红线。

**成本口径（沿用 PROJECT.md，回测时强制）**：滑点 = max(50% × spread, 10bps)；市值 <$500M 或 spread>30bps **翻倍**；paper 成交价用信号时刻**之后**的下一个可得价格。所有评估用**池内差分 / 对 SPY 超额**，不用绝对收益。

---

## 1. 汇总表（按近年存活证据强度排序）

| # | 候选 | 桶 | 机制类型 | 信号频率 | 数据 (a) 匹配 | 近年存活证据 | 毛 edge 量级/笔 | 主要致命风险 |
|---|---|---|---|---|---|---|---|---|
| 1 | **PEAD 微/小盘（SUE 漂移，T+1 入场）** | 小盘 PEAD | 限制套利/underreaction | 财报季高（百/周），淡季稀 | ✅ 日线+财报日历 | **强**（2025 多篇复活） | +100~300bps / 20-40d | 财报季集中、gap 已走一半、微盘滑点 |
| 2 | **隔夜溢价横截面（close→open，attention 小盘）** | 隔夜 | 风险溢价+散户开盘herding | **日频，极高** | ✅ 日线 O/C 即可 | **强**（2025 多篇 + ETF 版） | +5~20bps / 夜 | 单笔 edge 小、spread 吃掉、隔夜 tail 风险 |
| 3 | **End-of-Day Reversal（15:30 买日内输家，持至收盘）** | 微观结构 | 散户尾盘 attention 买入+空头收盘管理 | **日频，极高** | ⚠️ 需 30min bar（非 tick） | **强**（2024-11 论文，2025 Quantpedia 亚军） | +10~24bps / 30min | 需日内 bar（历史难取）、收盘小盘 spread |
| 4 | **短期反转 / MAX 增强反转（微盘周频）** | 微观结构/反转 | 散户过度反应回归 | 周频，高 | ✅ 日线收盘即可 | 效应**强**、净利润**弱** | 毛 +100~166bps/周 | **交易成本吞掉毛收益**（文献明证） |
| 5 | **指数重构删除侧反转（Russell 2000 删除 + S&P 400/600 降级）** | 指数机械流 | 被动基金强制抛售→反转 | 低-中（6 月 Russell 爆发 + 季度 S&P） | ✅ 日线+指数事件日历 | 中-强（结构核心活，纳入侧已死） | +100~200bps / 20-60d | 频率块状、Russell 一年一次、需事件名单 |
| 6 | **月末效应（turn-of-month，小盘横截面）** | 日历 | 机构/养老金/401k 机械再平衡流 | 低-中（~6 天/月） | ✅ 日线 | 中（2024-2025 practitioner 确认活） | +40~70bps / 转月窗 | 频率边缘、edge 小、拥挤 |
| 7 | **Pre-FOMC 漂移** | 日历 | 不确定性溢价 / 政策前抢跑 | **低（8 次/年，不满足 (c)）** | ✅ 日线+FOMC 日历 | 弱-中（2015 后学界称已死，practitioner 称活） | +10~49bps / 事件 | 频率不达标、2015 后衰减明显 |
| 8 | **IPO 锁定期到期抛压（+ 到期后反转）** | 机械流/日历 | 内部人首次可卖→机械抛压 | 中（依 IPO 管线，几只/周） | ✅ 日线+IPO/锁定期日历 | 中（机制在，近年量化薄） | 空头 -100~200bps；反转多变 | 需借券（项目暂 long-only）、样本依赖 IPO 周期 |
| 9 | **财报公告溢价（盘前买入待报股）** | 日历/事件 | 散户 attention 买入待报股 | 财报季高 | ✅ 日线+财报日历 | **弱**（文献明证美股近年已消失） | 历史 +20~50bps；近年 ~0 | 已被 8-K 频繁披露稀释、可能已死 |
| 10 | **杠杆/反向 ETF 收盘再平衡流** | ETF 机械流 | LETF 尾盘按合约强制同向调仓 | 日频 | ⚠️ 需日内（尾盘） | **弱**（2024 综述称经济上不显著） | 宣称有，实测 ~0 | 综述判定方法有误+经济不显著、需日内 |

---

## 2. 候选详述

每个候选按用户要求给出：机制（谁输钱给你）｜文献原始表现｜发表后/近年衰减证据｜近年存活证据｜回测所需数据｜预期毛 edge 量级｜致命风险｜与本项目约束的匹配。

---

### #1 — PEAD 微/小盘（SUE 漂移，T+1 入场，持有 20-40 天）

- **机制（谁输钱给你）**：财报公布后，盈利惊喜（SUE）方向的价格反应**不完全**，在随后数周继续同向漂移。输钱方：(a) 反应慢、只在事后看新闻摘要的散户；(b) **因容量/流动性限制不覆盖微盘的机构**——漂移恰恰**存活在套利成本最高处**（微盘、无/少分析师覆盖、低价、低机构持股）。你赚的是**限制套利下的结构性 underreaction 补偿**，不是抢信息。
- **文献原始表现**：经典 long-short（买正惊喜、卖负惊喜）年化 **10%~25%**（Bernard-Thomas 以降）；漂移强度与套利成本正相关，微盘最强。
- **发表后/近年衰减证据**：Martineau (2022) 称非微盘漂移**2001 年起消退、2006 年在非 microcap 完全消失**——大盘、高覆盖处确实基本死了。整体 magnitude 在发达市场（尤其美股）因效率提升与机构关注而**下降**。
- **近年（2023-2026）存活证据**：**2025 年有两篇被接收的论文直接反驳 Martineau 2022**，用美股数据（2001-02 至 2024-12）重建 "earnings drift factor" 并称其**仍是主要市场因子**；一致结论是漂移**集中且存活于低流动性、低机构持股、高交易成本的小/微盘**。→ 排名第一：近年证据最新、机制最干净、与项目「小盘 PEAD」焦点直接对齐、且**与被证伪的 8-K 机制根本不同**（慢漂移 vs T+0 抢定价）。
- **回测所需数据**：日线 OHLCV + **财报日期日历** + 每股盈利实际 vs 预期（算 SUE；无预期时可用**盈利公布日 gap / 财报日超额收益**作代理惊喜，纯价格可得）。全部可从 yfinance/EDGAR/Stooq 拼出，**无需 tick**。
- **预期毛 edge 量级**：极端 SUE 微盘分位，T+1 开盘入场、持有 ~20-40 交易日，**毛 +100~300bps/笔**（漂移窗口累计）；温和惊喜 ~+30-80bps。
- **致命风险**：(1) **入场时点**——若 gap 已在 T+0 盘后走完大半（8-K 教训），T+1 入场只吃残余漂移；必须回测「gap 后剩余漂移」而非「事件到 T+N 全程」。(2) 微盘滑点：成本翻倍后可能吃掉温和惊喜档，只有极端 SUE 分位净为正。(3) 财报季**信号高度集中**（4 波/年），样本时间聚集、非独立。
- **匹配**：(a)✅ (b)✅微盘容量极小 (c)⚠️季节性（季内百/周，淡季稀）(d)✅数周。**建议首个回测**：用 knowledge-cutoff 后的窗口，池内差分（顶 SUE 分位 vs 底分位），T+1 open 入场，悲观成本。

---

### #2 — 隔夜溢价横截面（close→open，attention/散户小盘）

- **机制（谁输钱给你）**：美股累计收益绝大部分在**隔夜**赚到，日内约零/负。横截面上，过去隔夜表现好的股票继续隔夜跑赢（隔夜动量）、日内反转——两个 clientele 的「拔河」。输钱方：**开盘 herding 追高的散户**（收盘想好、开盘挂单，推高开盘价），你在收盘做流动性提供、隔夜持有收溢价。attention/知名品牌/新闻热度/期权活跃/近期高收益的股票隔夜溢价最大。
- **文献原始表现**：SPY close→open 显著 > open→close（2020Q3-2025Q3：SPY +47.1% CO vs +29.9% OC；QQQ +53.5% vs +30.3%）；长短组合周末隔夜收益约为工作日的 **1.5 倍**；**35% 的 ETF** 存在足够扭曲，使「收盘买、开盘卖」在**扣佣金后**仍有显著正 alpha。
- **发表后/近年衰减证据**：指数级隔夜溢价太知名 → 已被产品化（overnight ETF 如 NSPY 等），**大盘/指数版本拥挤**。单名股票隔夜动量的横截面 spread 随流动性上升而收窄。
- **近年（2023-2026）存活证据**：**2025 年多篇**（含 11.6M 价格观测的 Finance Research Letters 2025、Elm Wealth "Night Moves"）确认隔夜/日内分解稳健、跨年持续；散户驱动的 attention 隔夜溢价在**小盘/高散户占比**处仍在。
- **回测所需数据**：**日线 OHLCV 即可**（Open、Close 直接算 close→open 与 open→close）。排序信号用过去 N 日隔夜收益 + attention 代理（成交量/价格动量）。**零额外数据需求**——这是数据上最干净的候选。
- **预期毛 edge 量级**：选中的 attention 小盘，**每夜 +5~20bps 毛**；日频累积但单笔小。
- **致命风险**：(1) **单笔 edge 太小**，spread（尤其小盘）+ 两次成交（MOC 买、MOO 卖）极易吞掉；必须严格筛 spread。(2) 隔夜暴露**左尾**（盘后利空 gap down），long-only 无对冲。(3) 与大盘 beta 高度相关，「超额 vs SPY」才是真 edge，绝对隔夜正收益是 beta。
- **匹配**：(a)✅最干净 (b)✅小盘版容量小 (c)✅日频极高 (d)✅小时（一夜）。**回测要点**：横截面池内差分（高隔夜动量分位 vs 低），扣满 MOC+MOO 两腿成本，只保留 spread<阈值的样本。

---

### #3 — End-of-Day Reversal（15:30 ET 买入日内输家，持有至 16:00 收盘）

- **机制（谁输钱给你）**：个股在**尾盘 30 分钟（15:30-16:00）**出现横截面反转——当日从上一收盘到 15:30 的**最大输家**在最后半小时系统性跑赢最大赢家。作者明确排除流动性/gamma-hedging，归因于两条新渠道：**散户 attention 驱动的尾盘买入** + **空头尾盘风险管理平仓**。你在 15:30 买被错杀的输家，吃反弹。
- **文献原始表现**：按 15:30 前收益排序，买底 decile、卖顶 decile 的 long-short 在最后半小时**平均 +0.24%/天**（Baltussen, Da, Soebhag）；主要来自对日内输家的正向价格压力。
- **发表后/近年衰减证据**：论文极新（2024-11-29），尚无充分 OOS 衰减记录；但尾盘反转类策略一旦公开易被尾盘算法蚕食。
- **近年（2023-2026）存活证据**：**最新、最直接**——论文 2024 年 11 月发表，作者获 **2025 Quantpedia Awards 亚军**。样本内经济与统计显著性都很高。→ 就「近年证据新鲜度」而言最强，故排第三；但因数据门槛（见下）与收盘执行成本，未列更前。
- **回测所需数据**：**需要日内 30 分钟 bar**（拿 15:30 快照 + 收盘价），**非 tick/orderbook**。⚠️ 这**轻度超出**硬门槛 (a) 的「纯日线」，但仍在「不需要 tick」范围内。实操约束：yfinance 免费日内历史短（sub-hour ~60 天、1h ~730 天），**历史回测数据难取**，可能需付费日内源或只能做近端小样本。
- **预期毛 edge 量级**：long-short 24bps/天；**long-only 输家腿约 +10~24bps/笔**（持有仅 30 分钟）。
- **致命风险**：(1) **数据可得性**——历史日内 bar 是主要障碍，可能无法凑够样本做 cutoff 后回测。(2) **收盘小盘 spread**：15:30-16:00 小盘 spread 宽，毛 24bps 极易被吃光。(3) 极短持有（30min）对执行精度要求高，paper 成交假设偏乐观。
- **匹配**：(a)⚠️需日内 bar (b)✅ (c)✅日频 (d)✅小时（30min）。**建议**：先验证数据可得性再排期；若日内历史取不到，降级为 forward-only 观察。

---

### #4 — 短期反转 / MAX 增强反转（微盘，周频）

- **机制（谁输钱给你）**：过去一周/一月**跌得多**的股票下期反弹、涨得多的回落。MAX 增强版：对**近期有极端单日大涨（lottery 特征）**的股票做反转最强。输钱方：**追高 lottery/彩票型股票的过度反应散户**（尤其高 retail order imbalance 分位），你做均值回归对手盘。
- **文献原始表现**：微盘短期反转 **2.04%/月（t=10.28）**，megacap 仅 0.74%/月；**MAX 增强反转 1.66%/周**（vs 低 MAX 组 0.65%/周）；效应在小盘、高散户失衡处最强。
- **发表后/近年衰减证据**：**核心衰减不是效应消失，而是成本**——文献直接指出短期反转**平均月交易成本 1.94% 吞没了平均毛收益**。这是「毛强、净弱」的典型。
- **近年（2023-2026）存活证据**：效应本身**很活**——2025 年 J. Banking & Finance "Maxing out short-term reversals in weekly stock returns"、以及多篇微盘证据（t 值极高）。→ 效应存活证据强，但**净利润存活证据弱**，故排第四。
- **回测所需数据**：**日线收盘价即可**（算周/月反转信号 + MAX = 过去一月最大单日收益 + 成交量/换手作 retail imbalance 代理）。无需 tick。
- **预期毛 edge 量级**：微盘周频反转 **毛 +100~166bps/周**；但**扣满悲观成本后期望≈0 甚至为负**——这正是要回测证伪/证实的核心。
- **致命风险**：(1) **交易成本**是唯一且致命的问题；<$1M 个人无冲击成本是唯一希望，但微盘**穿越 spread** 仍是杀手。(2) 反转本质是「接下落的刀」，路径波动大（回忆 H1b 死于路径波动）。(3) 高换手 → 短期资本利得税（联邦最高 ~37%）进一步侵蚀。
- **匹配**：(a)✅ (b)✅微盘 (c)✅周频高 (d)✅数天。**回测要点**：**成本是主变量**——用真实 spread（不是固定 10bps）分层，只在 spread 极窄的微盘子集测净期望；若净期望在最优子集仍 ≤0 → 直接杀。

---

### #5 — 指数重构删除侧反转（Russell 2000 删除 + S&P 400/600 降级）

- **机制（谁输钱给你）**：被动指数基金必须在**生效日**机械买入纳入股、抛售剔除股。**删除/降级股遭强制抛售 → 短期超跌 → 随后反转跑赢**。输钱方：**被授权/合约绑定、必须在可预测时点交易的指数基金**（他们不在乎价格，只求 tracking）。你当流动性提供方，在强制抛压中接被错杀的删除股。
- **文献原始表现**：Russell 2000 **迁移纳入股**重构前 20 日 +1.2% 跑高、之后反转 -0.95%；**删除股呈强正动量、纳入新股长期表现差**（buy-and-hold 组合年均跑赢年度再平衡指数 2.22%、5 年 17.29%）；S&P 400/600 变动的价格冲击**约一半到四分之三是永久的、其余数日内回撤**。Research Affiliates "Nixed: The Upside of Getting Dumped" 系统记录删除股跑赢。
- **发表后/近年衰减证据**：**纳入侧（addition）的经典「index effect」基本已死**——Greenwood-Sammon (2025 JoF)：S&P 500 纳入宣告日超额从 1990s 的 7.4%/9.4% 降到近十年 **0.3%/0.8%**；删除侧负超额同样从大幅降到 2010-2020 的 0.1%。原因：迁移抵消流、市场提前预判、机构备好接盘。→ **不要碰纳入侧抢跑**。
- **近年（2023-2026）存活证据**：**删除侧/强制抛压反转的结构核心仍在**——2023-2024 Dimensional 证实**即便迁移股也承担重构成本**、CXO Advisory 记录重构套利策略；2020s ETF 化更深，微/小盘指数（S&P 400/600、Russell 2000）指数化资金 20 年增 12-35 倍 → 小盘处强制流的绝对额反而更大。S&P 500 纳入 pop 在 2021 后因散户+期权**局部回潮**（announcement day +4pct）——但那是抢跑，非本候选。
- **回测所需数据**：日线 OHLCV + **指数事件日历**（Russell 6 月重构名单、S&P 400/500/600 增删公告与生效日——公开可得）。无需 tick。
- **预期毛 edge 量级**：删除股生效日后反转，**+100~200bps/笔**（20-60 日窗口）；迁移股 run-up 后反转约 -0.95%（可做空侧或规避侧）。
- **致命风险**：(1) **频率块状**：Russell 一年一次（6 月末），S&P 增删按季度/不定期——(c) 边缘，需拼多个指数族才够样本。(2) 需准确的历史增删名单与生效日（数据工程量）。(3) 删除股基本面常真差，反转与「掉入价值陷阱」难分。
- **匹配**：(a)✅ (b)✅小盘删除股容量小 (c)⚠️块状 (d)✅数周。**回测要点**：聚焦**删除/降级侧**（纳入侧已死），生效日后入场做反转，池内差分对同期小盘基准。

---

### #6 — 月末效应（turn-of-month，小盘横截面）

- **机制（谁输钱给你）**：月末/月初数日股票系统性偏强，源于**机构机械再平衡 + 养老金/401k 定投流 + 基金业绩窗口装饰**——数万亿授权配置必须在**可预测时点**调整。输钱方：被日程绑定的机械资金流的对手。
- **文献原始表现**：转月窗口（月末最后 ~1 日 + 月初 ~3 日）集中了指数大部分正收益；经典 turn-of-month 溢价每窗 ~+0.4-0.7%。
- **发表后/近年衰减证据**：过于知名，指数级已部分被抢跑；单纯日期规则 edge 缩小。
- **近年（2023-2026）存活证据**：**中等**——2024-2025 practitioner（beyondpassive、harbourfrontquant "Do Calendar Anomalies Still Exist?"、Quantpedia turn-of-month screener）确认结构性再平衡流仍在、效应**因机制是机械的而较持久**。
- **回测所需数据**：**日线即可** + 交易日历（判定月末/月初）。无需 tick。
- **预期毛 edge 量级**：转月窗 **+40~70bps**（每月 1 窗）；横截面叠加小盘选择可略增。
- **致命风险**：(1) **频率**：每月仅 1 窗（~6 天）→ (c) 边缘；须横截面铺开多标的或与其他日历（月末+FOMC）叠加才够样本。(2) edge 小、拥挤，成本后余量薄。(3) 纯日历规则最易 data-mining，须严格 OOS（回忆 H5 单窗噪声教训）。
- **匹配**：(a)✅ (b)✅ (c)⚠️低 (d)✅数天。**回测要点**：横截面（转月窗内买小盘/高历史转月 beta 分位），多年 OOS，警惕单年驱动。

---

### #7 — Pre-FOMC 漂移

- **机制（谁输钱给你）**：FOMC 公告前 24 小时股指系统性上行——学界解读为**承担政策不确定性的风险溢价** + 部分前置抢跑。输钱方：公告前减仓避险者 / 提供隔夜风险承担的对手。
- **文献原始表现**：Lucca-Moench：S&P 500 在 FOMC 公告前 **24 小时平均 +49bps 且不回吐**；1994 年以来**约 80% 的年度股权溢价**在 FOMC 前 24 小时赚到。
- **发表后/近年衰减证据**：**显著衰减**——多篇（含 Finance Research Letters 2020 "The disappearing pre-FOMC announcement drift"）指出该漂移在 **2015 年后基本消失**（无论是否伴随记者会）。
- **近年（2023-2026）存活证据**：**冲突**——学界称已死；但 practitioner（quantseeker 2024 "The Pre-FOMC Drift is Alive"，测到 2024-12）称仍在，用 3x 杠杆 ETF 得税后 CAGR 8-9%、Sharpe ~0.6、仅 5% 时间在场。证据分歧 → 排第七。
- **回测所需数据**：日线 + **FOMC 会议日历**（公开）。无需 tick。
- **预期毛 edge 量级**：历史 +49bps/事件；**近年衰减后 ~+10-49bps**，高度依赖是否仍存活。
- **致命风险**：(1) **频率硬伤**：一年仅 8 次 FOMC → **不满足 (c)**；单独不可作主策略，只能作组合日历 overlay。(2) 2015 后衰减证据强，可能已死。(3) 事件驱动 + 宏观 beta，非容量小的独立 alpha。
- **匹配**：(a)✅ (b)—非容量类 (c)❌8 次/年 (d)✅1 日。**定位**：不作独立候选主力，作为**日历 overlay** 与 #6 等叠加提频；单独回测仅为确认是否已死。

---

### #8 — IPO 锁定期到期抛压（+ 到期后反转）

- **机制（谁输钱给你）**：IPO 后 90/180 天锁定期到期日是**内部人/VC 首次可在二级市场抛售**的时点 → 机械抛压 → 到期日附近负超额，随后可能反转。输钱方：被锁定期合约绑定、到期即抛的内部人（价格不敏感卖方）。你做空抛压 or 接到期后超跌反弹。
- **文献原始表现**：Brav-Gompers（2,794 只美股 IPO）锁定日 **-2% 超额**；VC-backed 更负；Field-Hanka 等确认到期后内部人抛售致负超额、异常放量。
- **发表后/近年衰减证据**：机制（合约强制）不会消失，但**幅度被提前定价**——到期日可预测，部分抛压前移；近年专门量化更新较薄。
- **近年（2023-2026）存活证据**：**中等**——机制结构性存在（锁定期条款是硬合约），但缺 2023-2026 的强新证据；PE-backed 无此效应（区分度需建模）。
- **回测所需数据**：日线 + **IPO 日期 + 锁定期到期日历**（招股书 180/90 天规则，可从 IPO 数据推算）。无需 tick。
- **预期毛 edge 量级**：空头侧到期窗 **-100~200bps**；到期后反转多变、不稳。
- **致命风险**：(1) **需借券做空**——项目现阶段 **long-only**（借券数据未接），空头抛压腿暂不可行；只能做「到期后反转」long 侧，但该侧证据更弱。(2) 样本量依赖 IPO 周期（IPO 荒年信号稀 → (c) 不稳）。(3) 小盘 IPO 借券 hard-to-borrow 成本高（回忆 H1b 借券成本教训）。
- **匹配**：(a)✅ (b)✅小盘 IPO 容量小 (c)⚠️依赖 IPO 管线 (d)✅数天。**定位**：**待借券基础设施就绪后**再立项；现阶段仅回测「到期后 long 反转」可行性。

---

### #9 — 财报公告溢价（盘前买入待报股，持有穿越公告）

- **机制（谁输钱给你）**：有**排定财报日**的股票在公告窗口系统性偏强——**散户 attention 买入**待报股 + 承担公告不确定性的风险溢价。输钱方：公告前买入待报股的散户 attention 需求。
- **文献原始表现**：Frazzini-Lamont：持有穿越公告窗口年化 **7%~18% 超额**、Sharpe 高于多数异象；高 attention（高历史公告期成交量）股溢价最高。
- **发表后/近年衰减证据**：**强负** —— Heitz et al. (2020) 明确记录该溢价在**美股近年已消失**，归因于 2004 披露新规后公司**8-K 频繁披露重大事件**稀释了「财报日集中定价」。
- **近年（2023-2026）存活证据**：**弱**——主流证据指向「已死/大幅衰减」。收录仅为完整覆盖「日历/事件」桶并作为对照。
- **回测所需数据**：日线 + **财报日期日历**。无需 tick。
- **预期毛 edge 量级**：历史 +20~50bps/公告窗；**近年可能 ~0**。
- **致命风险**：(1) **可能已死**（8-K 稀释）——与项目已证伪的 8-K 主题相邻，需警惕重复踩坑。(2) long-only 穿越公告 = 暴露公告 gap 双向 tail。(3) 与 #1 PEAD 部分重叠但更弱（PEAD 赚公告后漂移，此候选赚公告前溢价）。
- **匹配**：(a)✅ (b)—一般 (c)✅财报季高 (d)✅数天。**定位**：低优先；若回测证实近年已死则归档，作为 #1 PEAD 的负向对照。

---

### #10 — 杠杆/反向 ETF 收盘再平衡流

- **机制（谁输钱给你）**：杠杆/反向 ETF 为维持每日目标杠杆，必须在**尾盘同向调仓**（涨了要加买、跌了要加卖标的敞口）→ 理论上放大尾盘同向动量。输钱方：被合约绑定、每日收盘机械再平衡的 LETF。
- **文献原始表现**：早期文献报告 LETF 再平衡需求与尾盘收益/波动有统计显著关联。
- **发表后/近年衰减证据**：**2024 年综述**（AIMS QFE 2024）结论：多数论文**方法有严重缺陷**，经济关联**不显著**；政策担忧不被总体证据支持。
- **近年（2023-2026）存活证据**：**弱**——2024 综述基本否定其可交易经济显著性。收录仅为完整覆盖用户点名的「ETF 再平衡」桶并给出**否定结论**。
- **回测所需数据**：需**日内（尾盘）数据** + LETF AUM/敞口估算。⚠️ 超出纯日线、且需 AUM 数据。
- **预期毛 edge 量级**：宣称有，**实测经济上 ~0**。
- **致命风险**：(1) **经济不显著**（2024 综述）。(2) 需日内 + 每日 AUM 估算，数据重、(a) 不满足。(3) 大盘标的、机构环伺，非容量小的个人 edge。
- **匹配**：(a)❌需日内+AUM (b)❌大盘 (c)✅日频 (d)✅小时。**定位**：**建议不立项**；列此仅为对「ETF 再平衡」桶给出诚实否定，避免重复研究。

---

## 3. 给 backtest 队列的优先级建议

**第一梯队（先跑，数据干净 + 近年证据强 + 机制干净）**
1. **#1 PEAD 微/小盘**——机制最干净、与项目焦点对齐、日线可测；核心验证「gap 后剩余漂移」是否 > 悲观成本。
2. **#2 隔夜溢价横截面**——数据零门槛（日线 O/C）、日频样本快；核心验证「扣 MOC+MOO 两腿 + 小盘 spread 后」净超额。
3. **#4 短期反转/MAX**——效应确定强，**唯一变量是成本**；快速用真实 spread 分层证伪/证实，是最快能出结论的一个。

**第二梯队（结构机制好，但有数据/频率/借券工程量）**
4. **#5 指数删除侧反转**——需建增删名单日历；聚焦删除/降级侧（纳入侧已死）。
5. **#6 月末效应**（横截面）——低频，作组合底仓；严格 OOS 防单年噪声。

**第三梯队（先解决前置条件再排期）**
6. **#3 End-of-Day Reversal**——先确认日内 30min 历史数据可得性；不可得则 forward-only。
7. **#8 IPO 锁定期**——待借券基础设施；现阶段仅测 long 反转侧。
8. **#7 Pre-FOMC**——仅作日历 overlay，单独频率不达标。

**建议不立项（诚实否定，避免重复研究）**
- **#9 财报公告溢价**：文献明证美股近年已死，且与已证伪的 8-K 主题相邻。
- **#10 杠杆 ETF 收盘流**：2024 综述判经济不显著 + 需日内/AUM。

**方法论提醒（沿用项目红线）**：每个立项候选先在 HYPOTHESES.md 登记 edge/对手盘/kill criteria → cutoff 后窗口回测（**池内差分 + 悲观成本 + 对 SPY 超额**）→ **OOS 独立窗口**（防 H5 式单窗噪声）→ 才 forward paper。**成本不是脚注，对 #4/#2 是主变量**。

---

## 4. 参考来源（2023-2026 为主）

**Factor zoo / 复制危机**
- Jensen, Kelly, Pedersen, "Is There a Replication Crisis in Finance?", J. of Finance 2023 — https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13249（82% 可复制、13 themes、跨 93 国 OOS）

**隔夜 / 日内**
- "Intraday and overnight return anomalies: Evidence from 11.6 million price observations", Finance Research Letters 2025 — https://www.sciencedirect.com/science/article/abs/pii/S1544612325018926
- Elm Wealth, "Night Moves: Is the Overnight Drift the Grandmother of All Market Anomalies?" — https://elmwealth.com/night-moves-overnight-drift/
- "ETFs' high overnight returns: The early liquidity provider gets the worm" — https://www.sciencedirect.com/science/article/abs/pii/S138641812030032X

**PEAD**
- UCLA Anderson Review, "Is Post-Earnings Announcement Drift a Thing? Again?"（2025 两篇反驳 Martineau 2022）— https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/
- Quantpedia, Post-Earnings Announcement Effect — https://quantpedia.com/strategies/post-earnings-announcement-effect

**End-of-Day Reversal**
- Baltussen, Da, Soebhag, "End-of-Day Reversal"（2024-11）SSRN — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009 ｜ 全文 — https://www3.nd.edu/~zda/EOD.pdf
- Erasmus, 2025 Quantpedia Awards 亚军 — https://www.eur.nl/en/news/end-day-reversal-pattern-second-place-quantpedia-awards-2025

**短期反转 / MAX**
- Chen, Cohen, Liang, Sun, "Maxing out short-term reversals in weekly stock returns", J. Banking & Finance 2025 — https://www.sciencedirect.com/science/article/abs/pii/S0927539825000301 ｜ SSRN — https://papers.ssrn.com/sol3/Delivery.cfm/4622831.pdf
- Quantpedia, Short-Term Reversal（含成本 1.94%/月吞没毛收益）— https://quantpedia.com/strategies/short-term-reversal-in-stocks
- Swedroe, "The MAX Anomaly Revisited" — https://larryswedroe.substack.com/p/the-max-anomaly-revisited-what-new

**指数重构 / index effect**
- Greenwood & Sammon, "The Disappearing Index Effect", J. of Finance 2025 — https://onlinelibrary.wiley.com/doi/10.1111/jofi.13410 ｜ NBER w30748 — https://www.nber.org/system/files/working_papers/w30748/w30748.pdf
- Alpha Architect, "Markets Becoming More Efficient: The Disappearing Index Effect" — https://alphaarchitect.com/disappearing-index-effect/
- Research Affiliates, "Nixed: The Upside of Getting Dumped"（删除股跑赢）— https://www.researchaffiliates.com/publications/press-exclusive/1043-nixed-the-upside-of-getting-dumped
- Dimensional, "Even Migrating Stocks Face Index Reconstitution Costs" — https://www.dimensional.com/be-en/insights/even-migrating-stocks-face-index-reconstitution-costs
- CXO Advisory, "Strategies for Exploiting Index Rebalancing?" — https://www.cxoadvisory.com/miscellaneous/strategies-for-exploiting-index-rebalancing/
- Sherwood News, "The S&P 500 inclusion effect springboard is back"（纳入抢跑 2021 后局部回潮）— https://sherwood.news/markets/the-s-and-p-500-inclusion-effect-springboard-is-back-in-a-big-way/

**日历 / Pre-FOMC / 月末**
- Lucca & Moench, "The Pre-FOMC Announcement Drift", NY Fed SR512 — https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf
- "The disappearing pre-FOMC announcement drift", Finance Research Letters 2020 — https://www.sciencedirect.com/science/article/abs/pii/S1544612320315956
- QuantSeeker, "Trading the Fed: The Pre-FOMC Drift is Alive"（测到 2024-12）— https://www.quantseeker.com/p/trading-the-fed-the-pre-fomc-drift
- Harbourfront Quant, "Do Calendar Anomalies Still Exist?" — https://harbourfrontquant.substack.com/p/do-calendar-anomalies-still-exist
- Quantpedia, Turn of the Month — https://quantpedia.com/screener/Details/41

**IPO 锁定期**
- Uppsala thesis, "Lockup expiration after IPO – Potentially abnormal returns"（Brav-Gompers -2% 综述）— https://uu.diva-portal.org/smash/get/diva2:1792892/FULLTEXT01.pdf
- "Short selling around the expiration of IPO share lockups" — https://www.sciencedirect.com/science/article/abs/pii/S0378426617302339

**财报公告溢价**
- Frazzini & Lamont, "The Earnings Announcement Premium and Trading Volume", AQR/NBER — https://www.aqr.com/library/working-papers/the-earnings-announcement-premium-and-trading-volume
- "The Disappearing Earnings Announcement Premium"（Heitz et al., 美股已消失）— https://www-2.rotman.utoronto.ca/userfiles/seminars/files/G_%20Narayanamoorthy%20paper.pdf

**杠杆 ETF**
- "The market impact of leveraged ETFs: A Survey of the literature", AIMS QFE 2024（经济上不显著）— https://www.aimspress.com/article/doi/10.3934/QFE.2024031?viewType=HTML
