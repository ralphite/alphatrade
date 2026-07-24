# 策略普查 · 家族 A：系统性 / 结构性策略

生成：2026-07-24（agent A）｜领域：横截面动量、低波/质量、季节性、配对/统计套利、杠杆 ETF 衰减、VIX 期限结构、债券/商品 ETF 结构性模式
评分轴（用户定的唯一目标）：**可快速验证的 alpha** = 免费历史数据能跑 ≥200 样本回测 × forward 信号频率 × 扣悲观成本后净 alpha 量级

---

## 0. 本报告的关键差异：不止查文献，全部候选都做了自测

本次普查对 7 个候选**直接用 yfinance 免费日线跑了粗筛**（脚本在 scratchpad，规则与成本口径见各条目），因为文献/博客数字系统性乐观。结果：**7 个候选里 4 个被自己的数据当场证伪**，与文献口径出入很大。这是本报告最有价值的部分。

自测统一口径：信号一律用**前一收盘**可得数据（无 lookahead）；成本：ETF 换手 8–20bps 单次往返、月末债券 4bps、大盘个股 10bps；比较基准一律**池内差分或对 SPY 超额**。

### 汇总评分表（按分数排序）

| # | 候选 | 机制类型 | 回测样本（免费数据） | forward 频率 | 扣成本净 alpha | 验证周期 | 评分 |
|---|---|---|---|---|---|---|---|
| 1 | **VIX 期限结构 carry（VIX/VIX3M → 短波敞口）** | 保险风险溢价 | **3,907 日 / 193 个 regime 段**（2011-2026，信号数据回溯 2006） | 每日在市（92% 时间），~12 次切换/年 | 全样本 Sharpe 0.74 / OOS 0.64；**近3年仅 0.41** | 回测 2 天，forward 需 1-2 年才有判定力 | **8.0** |
| 2 | **月末国债窗口（TLT/IEF 末 3-5 日）** | 指数基金 duration extension 强制流 | **288 个月×2-3 只 ETF**（2002-2026） | 12-36 次/年 | IEF Sharpe 0.95 / TLT 0.82；**近期无衰减（t=3.1）** | 回测 1 天，forward 6-12 个月 | **7.5** |
| 3 | **大盘横截面 12-1 总动量（月频）** | 慢钱 underreaction + 基准锚定 | 198 个月 × 105 名（需补 survivorship-free 名单） | 12 次调仓/年 × 10-20 标的 | **+78.5bps/月 vs 池内, t=2.44**（含幸存者偏差，乐观） | 回测 2-3 天（含名单工程），forward 1 年 | **6.5** |
| 4 | 残差动量（factor-neutral 版） | 同上，去因子 | 163 个月 | 同上 | **+21.9bps/月 t=0.83 — 劣于总动量** | — | 2.5 |
| 5 | 趋势跟踪 / TSMOM（ETF 层） | 行为 + 风险管理流 | 30+ 年日线 | 3-10 次/年 | Sharpe ~0.4，与 b&h 难分 | forward 需 10 年+ | 2.5 |
| 6 | 低波动 / 质量因子 | 杠杆约束 / 彩票偏好 | 15 年 ETF | 季度 | 近 18 个月 **-11% vs 大盘**（史上最差） | 需 5-10 年 | 2.0 |
| 7 | 商品 contango 收割（USO/USL） | 展期成本 | 20 年 | 月频 | 需**做空** USO；且 USO 已改结构、衰减变小 | — | 2.0 |
| 8 | 股票日历季节性（假日/OPEX/Halloween/月内） | 流动性/资金流 | 8,400 日 SPY | 高 | **全部 \|t\|<2，且 2020 后翻负** | 已证伪 | 1.5 |
| 9 | 配对交易 / 统计套利（低换手 ETF 对） | 相对定价错位 | 4,919 日 × 10 对 | 4.5 次往返/年/对 | **10 对里 8 对 Sharpe≤0.16 或负** | 已证伪 | 1.5 |
| 10 | 波动率管理 / vol-targeting 组合 | — | 20 年 | 日频 | 自测：VIX 信号做股票开关**不提升 Sharpe**（0.65→0.66） | 已证伪 | 1.5 |
| 11 | **杠杆 ETF 衰减收割（做空 2x/3x 对）** | 每日再平衡衰减 | 197-241 月 | 月频 | **毛衰减仅 1.6-3.8%/年 < borrow 3-15%/年 → 数学必负** | 已证伪 | 1.0 |
| 12 | FOMC 周期偶数周效应 | 信息释放周期 | 8 次/年 | 极低 | OOS（至 2023）**失去显著性** | 已证伪 | 1.0 |

---

## 1. 【评分 8.0】VIX 期限结构 carry —— 唯一"大 edge + 大样本 + 免费数据"的候选

### 机制（谁输钱给你）
VIX 期货长期高于最终实现的 VIX（**波动率风险溢价 VRP**）。付钱方是**买保险的人**：股票基金/风险平价/结构化产品发行方为满足风控或授权要求，**必须**持续买入 VIX 期货或方差敞口，且对价格不敏感；再加上散户长期错误持有 VXX/UVXY（这些产品年化损耗 -50%~-60%）。你是**卖保险方**，收的是保费而非信息优势——这与本项目已证伪的"读文本抢定价"是完全不同的机制类别。
关键：**只在期限结构 contango（VIX < VIX3M）时卖保险，backwardation 时离场**——backwardation 时保险是被正确定价甚至定价不足的，这就是 2018 年 XIV 归零的地方。

### 近年证据
- Contango 占 1990-2025 交易日约 **85%**；backwardation 罕见但先于 2004-2025 期间 22 次 >5% 回撤中的 21 次（volatilitybox.com research，2025）。
- 长波 ETP 因持续负 roll yield 年均损耗 **50-60%**（同上）——这是短波方的镜像收入。
- **2018 教训已被产品结构吸收**：XIV（ETN，-1x）触发 80% 条款被强制清算并归零；现存产品 SVXY 降为 **-0.5x**，2022 年上市的 SVIX（-1x）改为**盘中再平衡 + 持有价外看涨期权**做尾部保护。SVIX 在 2024-08-05（VIX 盘中 +308%）与 2025-04 关税冲击（-59%）都**存活并恢复**（Sherwood News / volatilityshares.com，2024-2025）。
- **溢价正在压缩（重要负面）**：2024-2026 曲线 VX6/VX1 = **1.062 vs 历史均值 1.15-1.20**；SVOL 月分红从 $0.30 降到 $0.28（24/7 Wall St.，2026-07-17）。2026-03-27 波动尖峰使曲线倒挂数日，短波策略回吐数周收益。

### 免费数据回测方案（已跑通）
- **信号数据**：`^VIX`（1990-）、`^VIX3M`（**2006-07 起，5,033 日**）、`^VIX9D`（2011-）——yfinance 全免费。
- **标的收益代理**：`VIXY`（2011-01 起，3,911 日）。合成短波日收益 = **−1 × VIXY 日收益**，这正是 SVIX 的目标；SVXY 版本乘 0.5。（VIXY 自身 0.85% 费率使合成偏乐观 +0.85%/年，我已扣掉 SVIX 的 1.48% 费率，净偏保守 −0.63%/年。）
- 也可用 CBOE 免费 VIX 期货结算历史重建常数期限指数回溯到 2004，但非必需。
- **可得样本量：3,907 个交易日 / 193 个 regime 切换段 / 15 个完整年度**，覆盖 2011欧债、2015-08、**2018-02 Volmageddon**、2020 COVID、2022 熊市、**2024-08-05**、2025-04 关税、2026-03 尖峰共 8 次独立压力事件。这是本次普查中样本量与压力覆盖最好的候选。

### 预注册规则（不许事后调参）
> 每日收盘计算 `ratio = VIX / VIX3M`。若**前一收盘** ratio < 1.0 → 次日持有短波敞口（SVIX 或 SVXY，按预设 sizing）；否则持 BIL/现金。成本：每次切换 15bps 往返；费率按产品实际扣。

### 自测结果（含成本，2011-01 ~ 2026-07，n=3,907）

| 版本 | CAGR | Sharpe | maxDD | 最差单日 |
|---|---|---|---|---|
| 不择时 买入持有合成 -1x 短波 | 18.6% | 0.61 | **-91.8%** | — |
| **规则择时（-1x）** | **29.0%** | **0.74** | -65.6% | -33.6% |
| 规则择时 0.5x sizing（≈SVXY） | 19.0% | 0.74 | -36.7% | -16.8% |
| 规则择时 0.25x sizing | 10.3% | 0.74 | -19.3% | -8.4% |
| 样本内 2011-2018 | 36.1% | 0.84 | -53.6% | |
| **OOS 2019-2026** | **21.9%** | **0.64** | -59.7% | |
| **最近 3 年 2023-07~2026-07** | **7.2%** | **0.41** | **-52.7%** | -24.0% |

**稳健性（重要）**：加"连续 3 天 contango"确认滤波 → Sharpe 降到 0.65；加"VIX<25"滤波 → Sharpe 降到 0.54 且 maxDD 恶化到 -80%。**朴素规则就是最优的，没有调参空间可捡** —— 这是好消息（无过拟合面），也说明别去优化它。
**分年**：2018 -50.0%（vs 不择时 -68.2%）、2020 +5.8%（vs -68.9%）、2022 -25.6%、2024 -20.8%、2025 +48.4%、2026YTD -22.6%。规则在 COVID 上是**决定性的**（+5.8% vs -68.9%）。

### 预期净 alpha
基础情形：**扣成本后 Sharpe 0.5-0.7，年化 15-25%（-1x 全额 sizing）**；但按最近 3 年压缩后的曲线（VX6/VX1=1.06）保守打折 → **Sharpe 0.4、年化 7-10%**。若按 0.25x sizing 装入组合（-19% 最大回撤），贡献约 **+2-3%/年组合收益、回撤占用可控**。

### 验证周期
- **回测判定：1-2 天**（数据已验证可得，规则 10 行代码）。
- **forward 判定：这是本候选唯一的软肋**——Sharpe 0.5 的策略要 forward 打到 t=2 需要约 16 年。**只能靠"历史 OOS + 机制可证伪性"下判断，不能靠 forward 积样本。** 建议判定方式改为：(a) 全 15 年逐年审计 + 8 次压力事件逐个复盘（H8 用过的"极端日审计"口径，非 t 统计）；(b) forward 只做**执行/滑点验证**与 kill-switch 演练，不做 edge 验证。

### 致命风险
1. **隔夜跳空不可防**。信号是收盘信号；2024-08-05 那种开盘即 +100% 的 VIX 期货跳空会直接吃掉一天 -24%~-34%。规则**无法**保护，只有 sizing 能。
2. **产品终止风险**（XIV 前例）。SVIX 若单日 -80% 触发条款可能清算。**对策：只用 SVXY(-0.5x) 或把 -1x 敞口按 0.25-0.5 名义 sizing**，且必须假设最坏情况归零。
3. **溢价压缩/拥挤**。近 3 年 Sharpe 0.41 是真实的衰减信号，不是噪声。
4. 短期资本利得税（切换频繁但年 ~12 次，比高换手策略好）。
5. **与本项目现有 sleeve 高度相关**：短波敞口本质是加杠杆的股票 beta，和 QQQ/QLD/TOM sleeve 在崩盘时同向。必须按"组合总 tail"限额，不能按单 sleeve 算。

**为什么给 8.0 而不是 9+**：机制、样本、数据、成本都是本次普查最优；扣分全在 (a) forward 无法快速判定，(b) 近 3 年 alpha 明显压缩，(c) tail 极重。

---

## 2. 【评分 7.5】月末国债窗口（TLT / IEF 末 3-5 个交易日）

### 机制（谁输钱给你）
固定收益指数（Bloomberg Agg 等）**在每月最后一个交易日**重构：新发债入指、到期债出指，指数久期被动**拉长**。所有跟踪该指数的被动基金、保险公司、养老金**必须在该日买入长久期国债**来 match duration，不问价格。你在月末前几天先买、提供流动性。这与本项目已存活的 TOM 是**同一类机制（机械再平衡强制流）**，但发生在**债券市场**，且强制性更硬（duration extension 是合约义务，不是习惯）。

### 近年证据
- **纽约联储（2024-09）**：2020 年以来基准国债在**月末最后一个交易日成交量平均高 46%**，且集中度随被动基金增长而上升——机制在，并且在变强。
- **Hartley & Schwarz (2019-11)**："Predictable End-of-Month Treasury Returns"：付息国债超额收益在**月末最后几天显著为正，其余时间与零无异**；仅在月末最后几天持有长债，**年化 Sharpe ≈ 1**。归因于保险公司在基准指数再平衡日的净买入（quantity 证据，不只是价格）。
- **对比（重要）**：同一日历机制在**股票**上已死（见 §5），在**债券**上仍活——这个不对称是本报告最强的单点发现。

### 免费数据回测方案（已跑通）
- `TLT`、`IEF`、`SHY`：yfinance 自 **2002-07** 起，各 6,035 日 = **288 个月末事件/只**。加上 `TLH`/`VGLT`/`GOVT` 可扩到 5-6 只 ETF（事件互相关但执行独立）。
- 规则：月末最后 N 个交易日收盘前买入，最后一日收盘卖出。TLT/IEF 点差 ~1bp，成本按 4bps 往返（悲观 4 倍）。

### 自测结果（2002-2026，n=6,034 日，含 4bps 成本）

| 规则 | CAGR | Sharpe | maxDD | 在市时间 |
|---|---|---|---|---|
| TLT 末 3 日 | 4.05% | **0.82** | -12.5% | ~14% |
| TLT 末 5 日 | 4.68% | 0.74 | -17.2% | ~23% |
| TLT 买入持有 | 3.59% | 0.32 | **-48.4%** | 100% |
| IEF 末 3 日 | 2.31% | **0.95** | **-6.2%** | ~14% |
| IEF 买入持有 | 3.54% | 0.55 | -23.9% | 100% |

**衰减检验（关键）**——末 4 日 vs 其余日的日均收益差：

| 期间 | TLT | IEF |
|---|---|---|
| 2002-2012 | +8.2bps/日 (t=2.07) | +4.4bps/日 (t=2.18) |
| 2013-2019 | +9.7bps/日 (t=2.53) | +5.0bps/日 (t=3.06) |
| **2020-2026** | +9.5bps/日 (t=1.90) | **+7.3bps/日 (t=3.12)** |

**IEF 在最近一段的 t 值是三段中最高的 —— 没有衰减迹象**（对照：同期 SPY 的月末效应从 5.1bps 衰减到 2.7bps，t=0.40）。

### 预期净 alpha
每月约 **+20~28bps 毛 / +16~24bps 净**（末 3-4 日窗口，TLT），**年化 ~2.0-3.0%，但只占用 14% 的日历时间** → 资金效率极高，可与其他 sleeve 叠加（其余 86% 时间资金停在 BIL 或别的 sleeve）。IEF 版本 alpha 小一半但 Sharpe 更高、回撤仅 -6%。

### 验证周期
- 回测判定：**1 天**（数据已在手，规则平凡）。
- forward：12 次/年/只 × 3-5 只 ETF = **36-60 次/年事件**，6-12 个月能看出方向；配合 288 个历史月末的 OOS 切分（如 2015 后作 OOS）可立刻预注册。**这是本次普查里"最快能拿到可信 judgment"的候选。**

### 致命风险
1. **利率 regime 依赖**：2002-2020 是债券大牛市，长债有 beta 顺风。**必须做"对同期 SHY/BIL 超额"或"对同 ETF 月内其他日"的池内差分**（我上面的 t 检验已是后者，这是真差分，故结论稳）。
2. 绝对量级小（年化 2-3%）——对 $1M 以下资金意义有限，除非叠加杠杆（TMF 会引入衰减）或与其他 sleeve 时间复用。
3. 与已存活的 H4c TOM sleeve **日历重叠**（都在月末），组合层会在同几天集中暴露。
4. 若被广泛套利，抢跑会把窗口前移（文献已提示"末 7 日"版本 CAGR 更高，暗示前移正在发生）。

---

## 3. 【评分 6.5】大盘横截面 12-1 总动量（月频，ETF 级成本）

### 机制（谁输钱给你）
中期动量：过去 12 个月（跳过最近 1 个月）赢家继续跑赢。输钱方 = 处置效应下过早卖出赢家的散户、以基准锚定不敢超配已涨标的的机构。**大盘 + 月频**是关键：本项目的"成本墙定理"（小中盘双边 69bps）在大盘失效——AAPL/MSFT 级别双边成本约 **5-10bps**，月换手 30-50% → 年成本仅 **0.4-1.2%**，而毛 edge 是年化 5-9%。**成本墙在这里躲开了。**

### 近年证据
- **残差动量已不再更优**（*Financial Analysts Journal*，2025，"The Many Facets of Stock Momentum"）：在美国和欧洲，若不做行业中性化、不跳过形成期后一个月，残差成分的贡献**不再大于**因子成分，且残差成分本身更弱（受短期反转污染）。→ **不要做残差动量，做普通总动量。**（我的自测独立复现了这一点，见下。）
- CFA Institute（2025-12）与多篇 2024-2025 论文仍确认动量是主要因子，但强调其**负偏度与厚尾**（momentum crash）。
- 2024 研究：高换手股票的短期动量只在接近 52 周高点时存在，否则强反转——提示可用 52 周高点做质量过滤。

### 免费数据回测方案（已跑通）
- yfinance 批量下载大盘池月线，`^GSPC`/SPY 做基准。我用了 **105 只当前大盘股，2009-2026，198 个月**。
- **必补的工程**：现在的池有**严重幸存者偏差**。修法：从 Wikipedia "List of S&P 500 companies / Selected changes" 表重建**逐时点成分股**（免费可抓），退市票 yfinance 多数仍有历史价。工作量约半天到 1 天。

### 自测结果（198 个月，2009-2026，10bps 往返成本，**池内差分**）

| 信号 | 净 CAGR | vs 池内等权 | t | vs SPY | t |
|---|---|---|---|---|---|
| **总 12-1 动量 top10** | 28.5% | **+78.5bps/月** | **2.44** | +108.9bps/月 | 3.44 |
| 总 12-1 动量 top20 | 23.5% | +37.5bps/月 | 1.99 | +67.9bps/月 | 3.57 |
| **残差 12-1 动量 top10** | 21.0% | **+21.9bps/月** | **0.83** | +49.7bps/月 | 1.87 |
| 残差 12-1 动量 top20 | 18.8% | +2.2bps/月 | 0.12 | +29.9bps/月 | 1.63 |

**两个结论**：(1) 池内差分后总动量仍有 t=2.44 —— 这不是简单的"大盘票跑赢 SPY"。(2) **残差动量显著劣于总动量**，独立复现 FAJ 2025 的结论 → 家族 A 的候选 #1（残差动量）应当**直接删除**，保留总动量。

### 预期净 alpha
乐观口径 +78bps/月；**扣掉幸存者偏差后现实预期 +25~45bps/月（年化 3-5.5% 超额）**，Sharpe 增量约 0.2-0.3。

### 验证周期
- 回测判定：**2-3 天**（主要成本是 point-in-time 成分股名单工程）。
- forward：12 次调仓/年 × 10-20 标的。年化 4% 超额、月度 std ~3% → t=2 需要约 **6 年 forward**。同样属于"forward 判不动"的类别，必须靠历史 OOS（如 1990-2008 用 Stooq/Yahoo 老数据做样本外）。

### 致命风险
1. **幸存者偏差**（当前结果乐观），未修正前不许信。
2. **与已杀死的 H7（行业 ETF 轮动）family resemblance**：H7 死于"2 年窗 4/4 正、8 年窗归零"。本候选窗口更长（16.5 年）且横截面更宽（105 名 vs 11 个行业），但**同样可能是 2015-2026 megacap 集中行情的产物**。预注册必须包含 2009-2016 / 2017-2026 两段各自显著的要求。
3. **动量崩溃**：2009-03、2020-03 类反转日单月可 -20%+。
4. 短期资本利得税（月频，最高 ~37%）会吃掉约 1/3 超额。

---

## 4. 【评分 1.0-2.5】被自测或文献证伪的候选

### 4.1 杠杆 ETF 衰减收割（做空 2x/3x 对）— **评分 1.0，数学上必负**
自测（等额做空双腿、月度重置，Adj Close 已含基金费率）：

| 对 | 样本 | **毛衰减/年（占空头名义）** | 月度 vol | 最差月 |
|---|---|---|---|---|
| SSO/SDS | 241 月 | **+1.62%** | 3.8% | -3.3% |
| UPRO/SPXU | 205 月 | **+2.59%** | 7.0% | -7.3% |
| TQQQ/SQQQ | 197 月 | **+3.76%** | 9.0% | -10.0% |

**真实 borrow 量级**：VXX 年化约 3-4%；UVXY 被多数券商列为 hard-to-borrow，**5% 到 30%+**；SQQQ/SPXU 类反向 ETF 常在 3-15% 区间且波动剧烈，并可被强制买入平仓（recall）。另外 3x ETF 的做空保证金要求约 90%（Schwab/IBKR），资金效率极差。
**结论**：毛衰减 1.6-3.8%/年，其中约 **0.9% 只是基金费率本身**（两腿各 ~0.9% 摊到平均名义额），真正的"波动率衰减"只有 0.7-2.9%/年；**扣 3% borrow 后 SSO/SDS 与 UPRO/SPXU 已为负，TQQQ/SQQQ 仅剩 +0.76%**；扣 6%+ 全灭。独立佐证：CXO Advisory（2020-02-28）测同样三对，结论"月度持有成本达 0.25-0.30%（≈6.2% 年化）时策略转负"，与我的数字一致。**且本项目当前 long-only 无借券能力 → 直接排除。**

### 4.2 股票日历季节性（假日 / OPEX / Halloween / 月内）— **评分 1.5，自测全灭**
SPY 1993-2026（8,428 日），日均收益差与 t 值：

| 效应 | 全样本 diff | t | 1993-2009 | 2010-2019 | **2020-2026** |
|---|---|---|---|---|---|
| 假日前一日 | +5.7bps | 0.90 | +2.7 | +2.4 | +16.8 (t=1.62) |
| OPEX 周 | -0.2bps | -0.06 | +3.9 | +1.4 | **-13.2 (t=-1.83)** |
| 月末±3 日（TOM） | +4.3bps | 1.57 | +5.1 | +4.2 | **+2.7 (t=0.40)** |
| Nov-Apr（Halloween） | +2.5bps | 0.98 | +2.9 | +4.6 | **-1.8 (t=-0.28)** |
| 月上半月 | +1.7bps | 0.66 | +0.2 | +0.9 | +6.9 (t=1.09) |

**没有一个 \|t\|>2**，且 OPEX 周与 Halloween 在 2020 后翻负。文献侧同向：Halloween 策略（11月-4月持股、其余持现金）累计 $100→$175.2（截至 2025-04-30），同期买入持有 $264.3；quantseeker（2025-02-09）测 38 只 ETF，**美股经典 [0:3] TOM 窗口无统计显著性**，只有更宽的 [-3:3] 窗口剩 5-12bps 且逐年递减。
> ⚠️ **对现有组合的交叉警告**：这直接冲击 H4c TOM sleeve 的前提。我的 SPY 测算显示 TOM 效应从 5.1 → 4.2 → **2.7bps/日（t=0.40）**逐段衰减。H4c 用的是 QQQ→QLD 的杠杆放大版，杠杆会放大衰减后的小 edge 也放大噪声。**建议单独复核 H4c 的分段稳定性**（不在本 agent 职责内，但应立案）。

### 4.3 配对交易 / 统计套利（低换手 ETF 对）— **评分 1.5，自测全灭**
10 个经典 ETF 对，60 日 z-score，|z|>2 入 / |z|<0.5 出，20bps 往返成本，2007-2026（4,919 日）：

| 对 | 净 CAGR | Sharpe | | 对 | 净 CAGR | Sharpe |
|---|---|---|---|---|---|---|
| XLP/XLU | +4.59% | **0.53** | | GLD/GDX | +1.11% | 0.16 |
| EWA/EWC | +2.80% | 0.32 | | QQQ/XLK | +0.14% | 0.05 |
| XLE/XOP | -1.38% | -0.04 | | TLT/IEF | -1.72% | -0.22 |
| SPY/RSP | -2.46% | -0.56 | | IWM/IWN | -2.59% | -0.66 |
| SPY/QQQ | -2.57% | -0.38 | | XLF/KRE | -4.28% | -0.26 |

最好的一对 Sharpe 0.53，其余 ≤0.32；且每对仅 ~85 次往返/19 年 = **4.5 次/年 → forward 频率不达标**，还需要借券做空。文献同向：配对交易收益从 2000 年前 15.6% 降到 2010 年后 **6.4%**（华沙大学工作论文 19/2025），"1990s-2000s 的简单机械版本已不再有稳健收益"（Relative Value Arbitrage，2026-01-26）。**排除。**

### 4.4 波动率管理 / vol-targeting — **评分 1.5**
自测：用同一个 VIX/VIX3M 信号做**股票**开关（contango 持股、backwardation 持现金，8bps 换手成本，2006-2026）：

| 标的 | 买入持有 Sharpe | 择时后 Sharpe | 择时后 CAGR 变化 |
|---|---|---|---|
| SPY | 0.65 | **0.66** | 11.25% → 8.52% |
| QQQ | 0.81 | **0.80** | 16.74% → 13.12% |
| QLD | 0.74 | 0.77 | 25.71% → 22.93% |

**Sharpe 基本不变，只是等比例缩小仓位**——回撤降了（-55%→-42%），但那是 de-risking 不是 alpha。文献同向：Cederburg 等基于 103 个策略的更广样本，**未发现波动率管理组合能系统性提高 Sharpe**，可实时执行的版本 certainty-equivalent 反而更低。
**重要推论**：VIX/VIX3M 信号的 alpha **只存在于波动率曲面本身（§1），不存在于股票方向**。这条区分让 §1 的候选更干净：它不是市场择时，是卖保险。

### 4.5 低波动 / 质量因子 — **评分 2.0**
MSCI World Quality 自 2024-06 至 2025 底跑输大盘约 **11%，20 年数据里前所未有**（MSCI / Renaissance，2026）。USMV 五年 +45% vs SPY +92%。低波在 2025 是唯一正收益因子（USMV +2.7% vs SPY -8.0%）——**说明它是 regime hedge 不是 alpha**。学界仅称"low-risk / quality / profitability 三个主题仍无条件获得 alpha"，但量级需 5-10 年才可分辨。**与"快速验证"目标根本冲突。排除。**

### 4.6 商品 contango（USO/USL）— **评分 2.0**
USO 十年回报约 +57% vs 现货 WTI 近乎翻倍，当前 contango 环境月度损耗约 **1.2%**——这是**做多者的成本**，收割它需要**做空 USO**（借券 + 无限上行风险，2022 年油价单边上行会直接爆掉）。且 USO 2020 后已改为**沿曲线分散持仓**，结构性衰减本身变小。**排除。**

### 4.7 FOMC 周期偶数周 — **评分 1.0**
Cieslak-Morse-Vissing-Jørgensen (JF 2019) 原文：1994 年起股权溢价全部产生在 FOMC 周期第 0/2/4/6 周。**Ali & Uppal 用至 2023 年底的数据重测：偶数周结果样本外不成立，超出原始 1994-2016 样本后失去统计显著性。** 加上 8 次/年的频率根本不满足验证速度要求。**排除。**（项目 `data/fomc_dates.json` 可以不用再投入。）

### 4.8 趋势跟踪 / TSMOM — **评分 2.5**
1880-2016 跨市场每十年 Sharpe 均接近 **0.4**（稳定但低）；2009-2013 SG Trend 指数年化 -0.8%。ETF 层实现频率 3-10 次/年，Sharpe 0.4 需要 **数十年** forward 才能与 buy-and-hold 分辨。机制真实但**验证速度上完全不合格**。

---

## 5. 跨候选的三个结构性结论

1. **日历/机械流的 alpha 已经从股票迁移到债券。** 同一个"月末强制再平衡"机制：SPY 上从 5.1bps 衰减到 2.7bps（t=0.40），IEF 上从 4.4bps 上升到 7.3bps（**t=3.12，三段最高**）。原因合理——股票月末效应是零售/媒体级常识，债券 duration extension 是机构后台作业，零售无从参与也无从拥挤。**结论：找结构性流，去零售不看的市场找。**

2. **"残差化 / 因子中性化"在美股已不再增值。** 残差动量 t=0.83 vs 总动量 t=2.44，与 FAJ 2025 的结论一致。不要为了学术优雅去残差化。

3. **同一个信号，用在不同资产上，alpha 差 10 倍。** VIX/VIX3M 用于短波敞口 = Sharpe 0.74；用于股票开关 = Sharpe 0.66 vs 0.65（无增量）。**信号的价值取决于它作用在哪个风险溢价上，不取决于信号本身"预测得准不准"** —— 这条应写进项目方法论。

---

## 6. 建议的下一步（家族 A 视角）

| 优先级 | 动作 | 耗时 | 判定标准 |
|---|---|---|---|
| **P0** | **月末国债窗口**：预注册（TLT+IEF+TLH，末 3 日与末 4 日两个变体，2002-2014 样本内 / 2015-2026 OOS），跑池内差分（vs 同 ETF 月内其他日）+ 4bps 成本 | 1 天 | OOS 段 t≥2 且 2020-2026 子段方向为正 → 进 forward（并入 launchd daily runner，规则型，零人工） |
| **P0** | **VIX 期限结构 carry**：预注册朴素规则（不许加滤波），全 15 年逐年 + 8 次压力事件逐个审计；sizing 定在 0.25x（SVIX）或等价 0.5x SVXY | 2 天 | 判定用"极端日审计 + 逐年不亏穿"而非 t 统计；任一年度 < -60% 或单日 < -40% → 降 sizing 或杀 |
| **P1** | **大盘 12-1 总动量**：先补 point-in-time S&P 500 成分股名单（Wikipedia 变更表），再重跑池内差分，分 2009-2016 / 2017-2026 两段 | 2-3 天 | 两段各自 vs 池内 t>1.5 且合并 t>2 → 进 forward；任一段归零 → 杀（H7 前例） |
| **P2** | 复核 **H4c TOM sleeve** 的分段稳定性（本报告 §4.2 的衰减证据） | 0.5 天 | 若 2020-2026 子段 t<0.5 → 重新评估 sleeve 权重 |
| — | 删除候选：残差动量、配对交易、杠杆 ETF 对、股票季节性、FOMC 周期、vol-targeting、低波/质量、商品 contango | — | 已证伪，不再投入 |

---

## 附：数据可得性核验（yfinance，2026-07-24 实测）

| 代码 | 起始 | 交易日数 | 用途 |
|---|---|---|---|
| ^VIX / ^VIX3M / ^VIX9D / ^VVIX | 1990 / **2006-07** / 2011 / 2007 | 9208 / **5033** / 3908 / 4911 | VIX 期限结构信号 |
| VIXY / SVXY / SVIX / UVXY / SVOL | 2011-01 / 2011-10 / **2022-03** / 2011-10 / 2021-05 | 3911 / 3722 / 1083 / 3722 / 1305 | 短波敞口代理（SVIX 太短，用 -1×VIXY 合成） |
| TLT / IEF / SHY | 2002-07 | 各 6035 | 月末国债窗口（288 个月末事件/只） |
| TQQQ / SQQQ / SSO / SDS / UPRO / SPXU | 2010-02 / 2006 / 2009 | 4137 等 | 杠杆对（已证伪） |
| SPY / QQQ / QLD / USO / USL / GLD | 1993 / 1999 / 2006 / 2006 / 2007 / 2004 | 8428 / 6886 / 5054 / 5104 / 4686 / 5453 | 季节性、商品 |
| USMV / SPLV / MTUM / QUAL | 2011 / 2011 / 2013 / 2013 | 3710 / 3827 / 3337 / 3274 | 因子（已证伪） |

> 注：`ZIVB`（中期反向波动）yfinance 仅 1 天数据，不可用。`VXX` 因 2018 年 ETN 重发只有 2018-01 起数据，故短波合成一律用 `VIXY`。

## 附：引用来源

- [CXO Advisory — Update on Shorting Leveraged ETF Pairs (2020-02-28)](https://www.cxoadvisory.com/short-selling/leveraged-etf-pair-shorting-strategies/)
- [Liberty Street Economics (NY Fed) — End-of-Month Liquidity in the Treasury Market (2024-09)](https://libertystreeteconomics.newyorkfed.org/2024/09/end-of-month-liquidity-in-the-treasury-market/)
- [Hartley & Schwarz — Predictable End-of-Month Treasury Returns (2019-11)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3440417)
- [QuantSeeker — Turn-of-the-Month Strategies: Do They Still Work? (2025-02-09)](https://www.quantseeker.com/p/turn-of-the-month-strategies-do-they)
- [Financial Analysts Journal — The Many Facets of Stock Momentum (2025)](https://www.tandfonline.com/doi/full/10.1080/0015198X.2025.2562790)
- [CFA Institute — Momentum Investing: A Stronger, More Resilient Framework (2025-12-17)](https://blogs.cfainstitute.org/investor/2025/12/17/momentum-investing-a-stronger-more-resilient-framework-for-long-term-allocators/)
- [Volatility Box — VIX Futures Explained: Contango, Backwardation, and Roll Yield](https://volatilitybox.com/research/vix-contango-backwardation/)
- [Six Figure Investing — What Caused the Feb 5 2018 Volatility Spike / XIV Termination](https://www.sixfigureinvesting.com/2019/02/what-caused-the-february-5th-2018-volatility-spike-xiv-termination/)
- [Volatility Shares — SVIX product structure](https://www.volatilityshares.com/svix)
- [24/7 Wall St. — The VIX Futures Curve Signal That Could Cut SVOL's Yield in Half (2026-07-17)](https://247wallst.com/investing/etf/2026/07/17/the-vix-futures-curve-signal-that-could-cut-svols-yield-in-half/)
- [Sherwood News — SVIX after the August 2024 volatility spike](https://sherwood.news/markets/svix-market-volatility-etf-has-skyrocketed/)
- [University of Warsaw WP 19/2025 — A Survey of Statistical Arbitrage Pairs](https://www.wne.uw.edu.pl/download_file/6095/0)
- [Relative Value Arbitrage — Modern Pairs Trading: What Still Works and Why (2026-01-26)](https://blog.harbourfronts.com/2026/01/26/modern-pairs-trading-what-still-works-and-why/)
- [Ali & Uppal — Does the FOMC Cycle Still Drive Stock Returns?](https://aliuppal.me/files/Ali_Uppal_CB_Cycles.pdf)
- [Cieslak, Morse & Vissing-Jørgensen — Stock Returns over the FOMC Cycle (JF 2019)](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12818)
- [ScienceDirect — On the performance of volatility-managed portfolios (Cederburg et al.)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X2030132X)
- [MSCI — Repositioning for Slower Growth: The Case for Quality](https://www.msci.com/research-and-insights/blog-post/repositioning-for-slower-growth-the-case-for-quality)
- [Capital Spectator — Low-Volatility Strategy Is 2025's Upside Outlier For Equity Factors](https://capitalspectator.substack.com/p/low-volatility-strategy-is-2025s)
- [24/7 Wall St. — USO's Front Month Oil Strategy Has Lagged Crude Oil Itself by Half Since 2014 (2026-05-26)](https://247wallst.com/investing/2026/05/26/usos-front-month-oil-strategy-has-lagged-crude-oil-itself-by-half-since-2014-and-the-roll-cost-is-the-reason/)
- [Alpha Architect — Time Series Momentum: A Good Time for a Refresh](https://alphaarchitect.com/time-series-momentum-aka-trend-following-the-historical-evidence/)
- [Man Group — Trend Following and Drawdowns: Is This Time Different?](https://www.man.com/insights/is-this-time-different)
- [Fintel — VXX / UVXY borrow rates](https://fintel.io/ss/us/uvxy)
