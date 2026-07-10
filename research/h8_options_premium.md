# H8 — 指数期权卖方（premium selling）可行性论文（决策级研究）

- **撰写**：策略研究 agent（Claude）
- **日期**：2026-07-10（周五收盘后）
- **触发**：零售 bar 级免费数据的短线 edge 已被 H1 家族（495 样本）与 H7（行业轮动/日内模式）系统性证伪。剩余符合「日内多笔、可积累样本」频率且**文献扎实**的方向只剩指数期权卖方。本文回答唯一的立项问题：**这个方向是否值得项目投入基础设施（数据 + 期权 paper 执行器）？**
- **⚠️ 数据可靠性声明（重要，沿用 H6 house style）**：
  - **A 档（高）**：SSRN/学术论文（Wharton、LBS）、BIS Bulletin、CBOE 官方研究、CFA Institute、券商官方文档（IBKR / tastytrade / Cboe DataShop）、sixfigureinvesting（XIV 事后分析业内公认）。
  - **B 档（中）**：披露方法论的从业者回测（spintwig、Option Alpha 的 25k/230k 笔样本研究、7circles 汇总）、主流财经媒体（Forbes / Bloomberg / Risk.net / Bank of England Bank Underground）。
  - **C 档（低，仅作方向印证）**：SEO / 营销博客（optionstradingiq、各类 "guide" 站）——方向可交叉印证，**精确数字不采信**。
  - 全文用 `[事实]`（含来源+日期）与 `[推断]`（我的判断）区分。
- **一句话定位**：这是**四个方向里证据基础最强、但也是最不适合本项目「2-3 周 t 检验快速验证」范式的一个**。核心张力见第 0 节。

---

## 0. 摘要与核心张力（决策用）

### 三句话摘要
1. **可行性判断 = conditional yes**：vol risk premium（卖方系统性获得的保险费）是金融学最稳健的异象之一，2024 Wharton 与 2019-21 零售期权实证均确认「0DTE 买方负期望、卖方拿到显著溢价」`[事实]`；零售可用 SPX/XSP 的 **defined-risk**（iron condor / credit spread）以极低成本、1256 税收优惠、无 pin/assignment 风险来卖，基础设施投入很小（IBKR paper API + Polygon 期权数据 ~$29-100/月）。**值得投，但前提是把它当 defined-risk、regime-aware 的 sleeve，不是当一个能在 3 周内跑出 t≥2 的统计 edge。**
2. **最大风险 = 「验证范式的类别错误」而非「策略无 edge」**：卖 premium 的盈亏结构是**高胜率 + 肥左尾**（ERN 5-delta naked put 回测：96% 胜率，但 3.3% 的亏损单吃掉近一半利润，均盈 $13 / 均亏 $163 `[事实]`）。这意味着**平静的 3 周 paper 会给出漂亮但完全误导的 t 值**——真相全在你还没抽到的尾部里（2018-02-05 XIV 单日 -90%、2020-03 naked put 涨 5-10 倍被强平、2024-08-05 VIX 盘中破 65）。本项目的整条流水线是为「多独立样本检测小 edge」设计的，而 premium selling 的样本高度相关、信息量集中在罕见亏损日，**短窗 t 检验对它失效**。
3. **建议的第一步**：**不要**照搬 H1 的「攒 150 样本算 t 值」模板。先做**离线诚实回测**（用 Polygon/ORATS 的 NBBO 报价、以 bid 卖/ask 买、绝不用 mid、含 1256 与交易所费），把一个固定规则的 **0DTE XSP/SPX defined-risk iron condor** 放在 2018-2026 全样本（含三个极端日）上跑一遍——**先看它在最坏日的 defined 单日亏损是否落在预算内、以及扣掉现实滑点后 VRP 是否还剩正期望**；这一步用现有基础设施（yfinance 不够、需买 ~$29-100/月期权数据）几天内可完成，是**最低成本的 go/no-go 闸**，通过后再谈 forward paper。

### 核心张力（本文最重要的一句 `[推断]`）
> **频率与文献两个「符合」是矛盾地共存的。** 0DTE 的日频让你能快速攒名义样本数；但正因为 edge 来自「卖保险」，其盈亏是负偏 + 横截面高相关（所有空 vol 仓在同一个下跌日一起爆），**名义样本数 ≫ 有效独立样本数**，且信息几乎全在尾部。所以「符合日内多笔频率」这个优点，对「用样本量做统计验证」这件事**几乎不产生价值**。谁要是用 3 周的绿色 P&L 曲线说「验证通过」，谁就掉进了这个策略最经典的陷阱（"picking up pennies in front of a steamroller"）。**这不是否决理由，而是必须重写验证范式的理由。**

---

## 1. 策略形态与证据（2023-2026 现状）

### 1.1 为什么卖方有 edge：vol risk premium 的量级与学术确认

- **VRP 的量级** `[事实]`：SPX 的 implied vol 长期系统性高于随后 realized vol，30 天滚动窗口正常区间 **2-4 个 vol 点**，长期均值约 **3-5 个 vol 点**；2025-10 的快照 IV ~22% vs RV ~12%，缺口 ~10 点（[SharpeTwo VRP guide](https://sharpetwo.com/blog/variance-risk-premium/)、[RobotWealth](https://robotwealth.com/the-volatility-risk-premium-in-a-tumultuous-market/)，B 档）。**这个缺口就是卖方的毛 edge 来源**——买方为「未来会动多少」付了历史上兑现不了的钱。
- **学术确认（A 档，决策关键）**：
  - **零售 0DTE 买方负期望**：Bryzgalova / Pavlova / Sikorskaya 用 2019-2021 美国零售期权账户**真实成交**数据，发现**最短到期（0DTE）亏损率最差、单笔期望收益为负**，分布右偏（罕见大赢）（[Coriva 综述引该研究](https://coriva.eu.org/en/0dte-options-guide/)，转述 A 档论文）。买方系统性亏 = 卖方系统性赢（扣成本前）。
  - **0DTE 的 VRP「显著偏高」且卖方获补偿**：2024 Wharton/合作者论文（Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov，[SSRN 5641974](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)，A 档）发现 0DTE 的存在通过改变做市商对冲需求**降低**了标的日内波动，且「0DTE 的 volatility risk premium 显著偏高，反映卖方为承担短期期权风险要求的高补偿」。→ **卖方 edge 在 0DTE 上不是变小而是偏大，但那正是承担尾部风险的对价。**
- **推断 `[推断]`**：VRP 是本项目至今研究过的所有方向里**证据基础最硬**的一个（对比：8-K underreaction 被三窗口证伪、行业动量 8 年归零）。它不是「会不会存在」的问题，而是「零售扣掉滑点/佣金/税/尾部后**还剩多少、能不能活着拿到**」的问题。

### 1.2 三种形态的实证表现（胜率/盈亏比/年化/回撤）

> 下表混合 A/B 档；所有数字**回测口径不一（DTE、delta、管理规则、杠杆各异），不可横向直接比较**，仅用于建立「量级手感」。

| 形态 | 风险性质 | 胜率 | 盈亏比（均盈:均亏） | 年化/回报 | 最大回撤 | 尾部特征 | 来源档 |
|---|---|---|---|---|---|---|---|
| **0DTE Iron Condor**（5pt 翼、近收盘、45 手） | **defined** | ~80-90% | 均盈 **$1,052** : 均亏 **-$2,181**（≈1:2） | 高（回测 CAGR 依杠杆） | **-27.8%** | Monte Carlo(1990-2025)：正常市 ~75% 时间盈利，~5% 极端日重亏；**年内 45% 概率出现 >20% 回撤** | B（[studylib/Pearce 回测](https://studylib.net/doc/27926930/ultra-short-dated-option-spreads-as-a-fund-strategy--pearce-)、[kniyer Monte Carlo](https://github.com/kniyer/spx0dte-strategies/blob/main/MONTE_CARLO_FINDINGS.md)） |
| **Naked put**（45DTE、5-delta，ERN 规则，2018-02..2020-06） | **undefined** | **>96%** | 均盈 **$13.29** : 均亏 **-$163.45**（≈**1:12**）；最大亏 -$428 | **CAGR ~24%**（2.4x 杠杆） | 优于 buy&hold（低杠杆时） | **3.33% 的亏损单（330 单里 11 单）吃掉近一半利润**；净利仅为收取权利金的 **55%** | B（[7circles/spintwig 汇总](https://the7circles.uk/options-9-ern-backtests-by-spintwig/)） |
| **Short strangle**（16-delta、45DTE，tastytrade 规则） | undefined（可加翼变 IC） | 高（未给单一数字） | 负偏 | — | — | 管理规则：IVR 50-100% 才开、50% 权利金止盈、2x credit 止损、21DTE 前平；**21DTE 后日 P/L 变不可预测** | C/B（[tastytrade 综述](https://talkmarkets.com/article/managing-winners-managing-early-and-managing-based-on-theta)、[SteadyOptions](https://steadyoptions.com/articles/selling-short-strangles-and-straddles-does-it-work-r516/)） |
| **Covered strangle** | 半 defined（有正股垫） | — | — | — | — | 本质是「持股 + 卖 put + 卖 call」，对**指数**卖方研究相关性低，暂不展开 | — |

**关键读法 `[推断]`**：
- **defined vs undefined 是生与死的分界，不是风格偏好**。naked 版年化更高（$13 均盈看着小但杠杆放大 + 极少亏），但那 24% CAGR 是**用无界尾部换来的**；一个 2020-03 就能把它归零（见第 2 节）。iron condor 用 -$2,181 的 defined 最大亏换掉了无界尾部。**本项目 <$1M、paper-first、纪律优先 → 只考虑 defined-risk 版本，naked 直接排除。**
- **高胜率是幻觉放大器**：96% 胜率会让人（和让短窗 t 检验）以为策略稳，但**净利只有权利金的 55%、且一半利润系于 3.3% 的交易日** —— 这就是负偏。胜率越高，单个样本的信息量越低，越需要看到亏损日才知道真相。

### 1.3 从业者真实战绩的「现实检验」（B 档，重要祛魅）

- Option Alpha 分析 **>25,000 笔**（后扩至 **230,000 笔**）真实 0DTE 交易：**只有 49.64% 的 0DTE 交易者是盈利的**；真正「样本 >100 笔且净盈利」的只占约 **20%**（[Option Alpha 0DTE 研究](https://optionalpha.com/blog/0dte)、[performance 页](https://optionalpha.com/blog/0dte-options-strategy-performance)）。周一显著最赚，周二/四/五 P/L 为负。
- **推断 `[推断]`**：backtest 里 VRP 明明为正，但一半真实交易者亏钱——差额被**执行滑点 + 尾部纪律崩溃 + 过度交易**吃掉了。这条数据对本项目是好消息也是警告：好消息是「机构级纪律 + 诚实成本模型」正是我们的比较优势；警告是**「回测有 edge」到「真金拿到 edge」之间的漏损极大，paper 阶段必须把成本悲观到骨头里**。

### 1.4 0DTE 市场结构（2024-2026 现状）

- **成交占比** `[事实]`：2025 年 SPX 0DTE 日均约 **230 万张**、占 SPX 期权量 **~59%**（下半年个别月 >60%）；占全美期权总量（2025 全年 152 亿张、日均 ~6,100 万张）约 **24%**（[SpotGamma](https://spotgamma.com/record-0dte-volume-reshapes-the-sp-500/)、[cryptobriefing](https://cryptobriefing.com/0dte-options-record-retail-volume/)，B/C 档）。2024 Q4 起 0DTE 已成 SPX 最活跃到期，单独超过其余所有到期之和（[Numerix](https://www.numerix.com/resources/blog/zero-day-options-0dte-start-2025-bang)，B 档）。
- **零售占比** `[事实]`：Cboe 估 2025-08 零售约占 SPX 0DTE 量 **53%**（5 月 ~54%）——**流动性极深且散户对手盘充足**（[cryptobriefing 引 Cboe](https://cryptobriefing.com/0dte-options-record-retail-volume/)，B 档）。
- **做市商行为 `[事实]`**：Wharton 论文与 Cboe 研究一致认为——0DTE 因**不积累隔夜库存**，做市商净 gamma 敞口被买卖双向流动大致抵消，日内波动影响是**episodic（单边流 + 薄流动性时才显著）**而非系统性放大（[Cboe gammasqueezes.pdf](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf)，A 档）。
- **推断 `[推断]`**：市场结构对**卖方零售**是有利的——流动性深、点差窄（尤其 SPY penny-wide）、对手盘（买 0DTE 的散户）持续负期望地送钱。**结构性顺风真实存在，这不是拥挤到失效的 trade。**

---

## 2. 尾部风险的诚实定价（本节是全文良心）

### 2.1 卖 premium 的本质 = 卖保险

平时每天收一点保费（正 carry / theta），极端日一次性赔付。**长期净盈利 = Σ保费 − Σ赔付**，而赔付高度集中在极少数日。任何只看「平时」的验证都是幸存者偏差。下面把三个历史极端日对各形态的**单日损失量级**摆清楚。

### 2.2 三个历史极端日的实测损失（A/B 档）

| 事件 | 触发 | 波动 | 对**卖方**的单日打击 | 对**defined vs naked** 的含义 |
|---|---|---|---|---|
| **2018-02-05 Volmageddon** | 短 vol 产品反身性挤压 | VIX **17.31→37.32（+115%，史上最大单日升幅）** | **XIV 单日 -90%+**（$108→$4），AUM $1.9B→$63M，两周内清盘 | naked/杠杆短 vol = **一天归零**；[sixfigureinvesting](https://www.sixfigureinvesting.com/2019/02/what-caused-the-february-5th-2018-volatility-spike-xiv-termination/)、[CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products)（A 档） |
| **2020-03 COVID crash** | 疫情 | SPX **23 天 -34%**；VIX >80 | 45DTE **naked put 涨 5-10 倍**，很多人**在能反应之前就被强平**；保证金要求最高 **+300%**；tastytrade 45/21 框架散户被团灭 | defined-risk 亏损被封顶在（翼宽−权利金），能活；naked = 保证金螺旋 + 强平；[7circles](https://the7circles.uk/options-9-ern-backtests-by-spintwig/)、[FIA 白皮书](https://www.fia.org/sites/default/files/2020-10/FIA_WP_Procyclicality_CCP%20Margin%20Requirements_1.pdf)（B/A 档） |
| **2024-08-05 日元套息崩盘** | BOJ 7-31 加息至 0.25% → carry unwind | VIX **盘中破 65**（前周 ~16-23），史上最大级单日 vol 冲击之一 | 卖 VIX/指数 strangle 者「毁灭性亏损」（20 call 变 45+ 点实值）；**保证金追缴→被迫买回→点差走阔→自我放大** | 单边挤兑放大机制在 defined-risk 上仍痛但有底；naked 上是爆仓；[BIS Bulletin 90](https://www.bis.org/publ/bisbull90.pdf)（A 档）、[navnoorbawa 复盘](https://navnoorbawa.substack.com/p/volatility-arbitrage-how-funds-profited)（C 档） |

- **附：单一账户级前车之鉴 `[事实]`**：James Cordier / OptionSellers.com 2018 年因 naked 天然气期权期权在一次逼空中**亏光并倒欠客户 ~$150M**（[beststockstrategy 复盘](https://beststockstrategy.com/optionsellers/)，C 档，事件本身 A 档公认）。**naked 卖方的经典墓志铭。**
- **系统性尾部（供参考，非基准情形）`[事实]`**：JPMorgan 的 Peng Cheng 测算——若 SPX **5 分钟内跌 1% 可再引发 5% 下跌**；**盘中跌 5% 可触发 $300 亿 0DTE 抛售、指数再跌 20%**（[EBC 引 JPM](https://www.ebc.com/forex/0dte-options-the-hidden-driver-of-market-volatility)，C 档转述）。反方（BofA、Bank of England Bank Underground）认为 0DTE **不积累库存**、影响局部，「Volmageddon 2.0」被夸大（[Bank Underground 2024-12](https://bankunderground.co.uk/2024/12/04/zero-day-options-and-financial-market-vulnerability/)，A 档；[BofA via Advisor Perspectives](https://www.advisorperspectives.com/articles/2023/02/23/bank-of-america-says-options-driven-volmageddon-2-0-warning-is-overblown)，B 档）。**推断 `[推断]`**：系统性 volmageddon 2.0 概率低但非零；对一个 **defined-risk、小仓位**的零售卖方而言，即便它发生，单日损失也被合约结构封顶——**这正是坚持 defined-risk 的全部理由**。

### 2.3 能让 <$1M 账户在极端日存活的仓位纪律（预注册硬约束）

> 目标：**任何单日（含 limit-down / VIX 一夜翻倍）都不产生账户级损伤**。以名义 $100k paper 账户为例。

1. **只做 defined-risk，永久禁止 naked / undefined**（naked 的存在本身就使「survive worst day」不可证明）。single 铁律，等同 H1 家族的「不得复活」。
2. **全组合「已定义最大亏损」预算封顶**：所有未平仓 defined-risk 头寸的**最大可能亏损之和 ≤ 账户的 5%**（$100k → $5,000）。因为极端日**所有空 vol 仓会同时走到最大亏损**，这个和就是你的真实单日 VaR。5% 是「痛但能第二天照常交易」的量级。
3. **单一到期日风险再收紧**：单个 expiry 的最大亏损和 ≤ 账户 2-3%。0DTE 尤其要小，因为无隔夜调整机会。
4. **持有期内不加仓摊平**（naked 卖方最常见的死法：亏了就 roll/加倍）。规则化止损（如 2x credit 或触及短腿）优先于「扛」。
5. **事件日过滤**：预注册跳过 FOMC / CPI / 大级别财报日的 0DTE 卖出（学术与从业者一致建议，波动可瞬间 explode）。
6. **推断 `[推断]`**：满足 1+2 后，**数学上**最坏单日 ≤ -5%，2018/2020/2024 三个极端日都活得下来；代价是年化被这层保险性封顶压低——**但「活着」是本项目的第一性原则（PROJECT.md 目标：可持续、稳定），不是可谈判项。**

---

## 3. 零售可及的执行与数据

### 3.1 券商 paper trading API 现状（A 档，官方文档）

| 券商 | paper/API 能力 | 期权 greeks/链 | 适配本项目度 `[推断]` |
|---|---|---|---|
| **IBKR** | TWS API（TCP socket）+ Web API；**paper 账户持久**、模拟资金；Python/Java/C++/C# | reqMktData 默认返回 delta/gamma/theta/vega，可正/反算 IV；`/iserver/secdef/strikes` 取链（[TWS API options](https://interactivebrokers.github.io/tws-api/options.html)、[greeks](https://interactivebrokers.github.io/tws-api/option_computations.html)） | **最佳**：paper 持久（能持有 45DTE 多日仓）、实时 greeks/报价可喂给自建 ledger、支持 SPX/XSP | 
| **tastytrade** | Open API + **sandbox（certification env）**；免费；Python SDK（[pypi tastytrade](https://pypi.org/project/tastytrade/)） | 实时 stocks/options/ETF 行情，可下单（[developer.tastytrade.com](https://developer.tastytrade.com/)） | **次选**：**sandbox 每 24h 重置、清空所有持仓**（[sandbox 文档](https://developer.tastytrade.com/sandbox/)）→ 无法持有多日仓、无法当账本。0DTE（当日平）可用，但仍建议只借它取报价 | 

- **关键结论 `[推断]`**：本项目**已有自建 JSONL ledger**（H1 用的那套），所以**不需要券商的 paper 账户来记账**——只需要券商 API 提供**真实 NBBO 报价 + greeks 来喂成交模型**。据此 **IBKR TWS API（持久 paper + 实时 greeks + 支持 SPX/XSP）是明确最优**；tastytrade sandbox 的 24h 重置对多日 defined-risk spread 是硬伤，仅 0DTE 场景勉强可用。

### 3.2 SPX vs SPY vs QQQ vs IWM：成本 / 税收 / 流动性（决策关键表）

| 维度 | **SPX / XSP** | **SPY** | **QQQ** | **IWM** |
|---|---|---|---|---|
| 到期 | **每日**（含 0DTE） | **每日** | **每日** | **仅每周**（无每日 0DTE）`[事实]` |
| 结算 | **现金结算、European、无 assignment/pin 风险** | 实物、American、有提前行权/pin 风险 | 实物、American | 实物、American |
| **税收** | **Section 1256：60/40**，有效税率 ~26.8% vs 37%；同样 $100k 利润联邦税 SPX **~$23k** vs SPY **~$40.8k**（差 **$17.8k**）；无 wash-sale；亏损可回抳 3 年（[daystoexpiry](https://www.daystoexpiry.com/blog/spx-section-1256-tax)、[Cboe XSP tax](https://www.cboe.com/tradable_products/sp_500/mini_spx_options/tax_benefit/)，A/B 档） | 普通短期利得（最高 37%） | 同 SPY | 同 SPY |
| 流动性/点差 | 深；点差比 SPY 宽（绝对值大） | **全球最活跃、ATM penny-wide（$0.01-0.03）** | 次于 SPY，IV/权利金更高 | 最不活跃，但 IV 最高 `[事实]` |
| 佣金拖累（占策略收入，ERN 回测）| **SPX 1.20%** | **SPY 6.36%** | ~SPY 量级 | 更高 |
| 合约规模 | 大（SPX ~10x SPY；XSP = SPX 的 1/10 ≈ SPY 名义） | 小 | 小 | 小 |
| 小账户适配 | XSP 兼得 1256 + 现金结算 + 小规模 → **小账户理想** | 门槛最低、点差最友好、数据最便宜 | 权利金最厚 | 资本门槛最低 |

来源：[SPX vs SPY/QQQ 0DTE 选择](https://greekslab.com/blog/spx-vs-spy-vs-qqq-choosing-the-best-underlying-for-0-dte-trading)、[24/7 Wall St 3 ETF 卖方](https://247wallst.com/investing/2026/06/25/so-you-want-to-sell-0dte-options-3-etfs-that-make-it-possible/)、[TradingBlock SPY vs SPX](https://www.tradingblock.com/blog/0dte-spy-vs-spx-options)（B/C 档）。

- **推断 `[推断]`**：**执行首选 XSP**（mini-SPX）——同时拿到 1256 税收（把最高 37% 短期利得砍到 ~26.8%，对高换手卖方是巨大真实 edge）、现金结算（0DTE 卖方**最怕的 pin/assignment 风险直接消失**）、合约规模适配 <$1M 账户、佣金拖累最低。**SPY/QQQ 仅用于「数据便宜、先跑通管线」的开发期**；一旦上真实规模逻辑，迁到 XSP/SPX。

### 3.3 历史期权数据源：能否支撑诚实回测？（A/B 档）

| 源 | 价格 | 覆盖 | 适配度 `[推断]` |
|---|---|---|---|
| **yfinance（现用）** | 免费 | **无历史期权链/greeks/IV**，仅当前链 | **不够**：无法回测。这是本方向需要**新数据基础设施**的根本原因 |
| **Polygon.io（2025-10 更名 Massive）** | 期权档 **$29-399/月**；付费档含 flat files（S3 批量）、trades/quotes/greeks/IV，**2014 起** | 全美期权 | **最佳性价比**：$29-100/月即可拿到 SPY/QQQ 历史链做诚实回测（[polygon.io/options](https://polygon.io/options)、[定价](https://apis.io/plans/polygon-io/polygon-io-plans-pricing/)） |
| **ORATS** | 基础 **~$100/月** | 历史 IV surface、skew、fair value、EOD 回测引擎（**pre-2018 强**） | 好：自带回测引擎，省自建成本 |
| **Cboe DataShop** | **SPX 历史需 CGI license，$1,000/月起**；无 license 仅 T+1 延迟指数报价 | 官方 tick/EOD/greeks | **SPX 原始数据是真门槛**：$1,000/月对本项目过重。**用 XSP/SPY 数据替代**（Polygon 便宜） |
| **CBOE 免费** | 免费 | **仅** SPX volume + put/call ratio 归档，**无报价/链** | 不足以回测 |

- **诚实模拟的最低要求 `[推断]`（本项目 PROJECT.md「成本悲观化」在期权上的具体化）**：
  1. **绝不用 mid 价成交**。卖腿按 **bid** 成交、买腿按 **ask** 成交（或 mid 再扣 spread 的 50%，取更悲观者）——这是期权 paper 自欺的头号来源。iron condor 的**低 delta 翼上，点差常是权利金的很大比例**，用 mid 会凭空造出不存在的 edge。
  2. **含全部费用**：佣金（~$0.65/腿）+ 交易所/监管费（SPX/XSP 指数费 ~$0.40-0.50/合约），一个 4 腿 IC 开+平 = 8 腿的费用不可忽略。
  3. **成交价用信号时刻之后的下一个可得报价**（同 PROJECT.md，永不用信号时刻价）。
  4. **用真实 NBBO 报价数据**（Polygon quotes 档），不用理论 BS 价倒推——BS 价系统性乐观。
  5. **回测必须覆盖极端日**（2018-02、2020-03、2024-08），且**单独报告这些日的 defined 单日亏损**，不能只看聚合 CAGR。

---

## 4. 建议的最小验证路径与决策建议

### 4.1 决策建议：**CONDITIONAL YES**（值得投基础设施，但必须重写验证范式）

- **YES 的部分**：edge 证据是四方向里最硬的（VRP，A 档学术确认）；执行零售可及且有 1256/现金结算的真实结构性优势；基础设施投入很小（**$29-100/月 Polygon 期权数据 + 免费 IBKR paper API + 复用现有 ledger**，无需新增重资产）。
- **CONDITIONAL 的部分（不可谈判的前提）**：
  1. **只做 defined-risk**（naked 永久禁止，等同 H1「不得复活」红线）。
  2. **放弃「2-3 周 t 检验判生死」的范式**——对负偏 + 高相关的 premium selling，短窗 t 值是**反指标**（平静期越漂亮越危险）。改用**（a）离线全样本诚实回测（含三个极端日）+（b）多月/跨 regime forward + 强制经历 ≥1 次 vol spike**，判据不是「均值 t≥2」而是「**扣悲观成本后 VRP 净捕获 > 0，且最坏单日 defined 亏损落在预算内**」。
  3. 若用户坚持要「像 H1 那样 3 周内用样本量证伪」→ 那对这个策略是**类别错误，此时建议 NO**（会被平静期假绿骗）。
- **一句话 `[推断]`**：这**不是**第五个「攒样本算 t 值」的统计假设，而是与 **H4c（TOM 资金流）、H6（AI 基建）并列的第三类「结构性/论点驱动 sleeve」**——收益来源是 VRP 这个结构性事实 + 纪律，不是可快速 t 检验的交易 edge。**按 sleeve 立项、按 sleeve 验证。**

### 4.2 第一个最小形态（建议固定规则版，预注册）

> **H8 v1 拟定形态**（离线回测先行，通过才 forward）：

- **标的/结构**：**0DTE XSP iron condor**（开发期先用 SPY 数据跑通，因数据便宜）。
- **固定规则（示例，回测前冻结）**：每交易日 **10:00 ET** 开一个 IC；短腿 **~10-16 delta**（或固定 ~0.3% OTM）；翼宽 **$5**（XSP 口径，SPX 则 $10-25）；**50% 权利金止盈 / 2x credit 止损 / EOD 强平**，先到为准；**跳过 FOMC/CPI/大事件日**。
- **仓位**：单 IC 最大亏损 = 翼宽 − 权利金；按第 2.3 节，全组合 defined 最大亏损和 ≤ 账户 5%、单日 ≤ 2-3%。

### 4.3 信号频率与样本积累（诚实版）

- **名义信号数**：0DTE 每标的 1/天。SPX/XSP + SPY + QQQ 三个 ≈ **3/天**（IWM 仅每周，非每日）；若再加不同入场时点可到 ~5/天，但**都高度相关**。
- **积累 100 名义样本**：单标的 1/天 → **约 5 个月**（21 交易日/月）；三标的 3/天 → **约 6-7 周**。
- **有效独立样本 ≪ 名义数**：所有空 vol 仓在同一下跌日一起爆，横截面相关近 1；且信息集中在罕见亏损日。**所以「6-7 周攒 100 样本」这句话对统计验证基本无意义**——你可能 6 周都没遇到一个真正的亏损 regime，t 值会假性漂亮。**这是本方向与 H1 最根本的不同，必须在立项时写死。**

### 4.4 预注册 kill / 判据（按 sleeve 范式，非 t 检验范式）

> 与 H1 的「n≥150 且 t≥2」**刻意不同**。以下为 H8 专属判据（立项前冻结）：

1. **离线闸（go/no-go，最先跑）**：固定规则版在 **2018-2026 全样本 + 三个极端日**上，扣**悲观 NBBO 成交 + 费用 + 1256 后**：（a）净 VRP 捕获 > 0；**且**（b）三个极端日的**单日 defined 亏损均 ≤ 预算**（≤ 账户 5%）。任一不满足 → **不进 forward，归档**。
2. **Forward 判据**：paper 跑满 **≥3 个月且至少穿越 1 次 VIX >30 的 vol spike**；滚动净 P&L（扣悲观成本）为正**且**实际最坏单日亏损 ≤ 预注册预算。
3. **Kill 触发**（任一即停或大改）：
   - 任何单日实际亏损 **> 预算**（说明 defined-risk 结构或 sizing 失效）→ 立即停，查结构。
   - defined 最大亏损日出现频率**显著高于入场 delta 隐含的概率**（如 12-delta 短腿却频繁被击穿）→ 入场定价错，大改。
   - 扣悲观成本后 3 个月净 P/L < 0 **且**已穿越至少一次正常波动 → VRP 未能净捕获，kill。
   - 发现回测用了 mid 价/理论价而非 NBBO → 结果作废、清零重跑（自欺红线）。
4. **不设「样本数不够就继续攒」的宽限**——因为攒样本对本策略不解决问题；解决问题的是**跨 regime 时间 + 极端日压力测试**。

### 4.5 落地第一步（最低成本 go/no-go）

1. 订 **Polygon 期权 Starter/Developer 档（$29-100/月）**，拉 SPY/QQP 2018-2026 历史链 + NBBO quotes。
2. 写一个 **0DTE IC 固定规则离线回测器**，严格按第 3.3 节的悲观成交/费用口径。
3. **单独输出三个极端日（2018-02-05、2020-03-16 前后、2024-08-05）的 defined 单日 P&L**。
4. 若离线闸通过 → 才接 IBKR TWS API 做 forward paper（复用现有 ledger）；不通过 → 归档，写清死因（与 H1/H5/H7 同待遇）。
5. **预计成本**：数据 ~$29-100/月 + 几天 agent 开发。**这是四方向里 go/no-go 单位成本最低的一个**——即便最终 no，代价也很小。

---

## 附：主要来源清单（按主题）

**VRP / 学术**：[Wharton 0DTE SSRN 5641974](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)、[0DTE liquidity providers SSRN 4881008](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4881008)、[Coriva 综述(引 Bryzgalova 零售研究)](https://coriva.eu.org/en/0dte-options-guide/)、[SharpeTwo VRP guide](https://sharpetwo.com/blog/variance-risk-premium/)、[RobotWealth VRP](https://robotwealth.com/the-volatility-risk-premium-in-a-tumultuous-market/)、[Cboe SVRPO dashboard](https://www.cboe.com/us/indices/dashboard/svrpo/)

**形态回测**：[Pearce ultra-short IC 回测](https://studylib.net/doc/27926930/ultra-short-dated-option-spreads-as-a-fund-strategy--pearce-)、[kniyer 0DTE Monte Carlo](https://github.com/kniyer/spx0dte-strategies/blob/main/MONTE_CARLO_FINDINGS.md)、[7circles/spintwig ERN naked put](https://the7circles.uk/options-9-ern-backtests-by-spintwig/)、[Option Alpha 0DTE 25k+ 研究](https://optionalpha.com/blog/0dte)、[Option Alpha performance](https://optionalpha.com/blog/0dte-options-strategy-performance)、[fattail 负偏](https://fattail.ai/credit-spread-options/)

**市场结构**：[Cboe gammasqueezes.pdf](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf)、[SpotGamma 0DTE 占比](https://spotgamma.com/record-0dte-volume-reshapes-the-sp-500/)、[cryptobriefing 48%/零售占比](https://cryptobriefing.com/0dte-options-record-retail-volume/)、[Numerix 2025](https://www.numerix.com/resources/blog/zero-day-options-0dte-start-2025-bang)、[Bank Underground 0DTE 脆弱性](https://bankunderground.co.uk/2024/12/04/zero-day-options-and-financial-market-vulnerability/)、[Risk.net 0DTE 动态](https://www.risk.net/insight/markets/7959202/zero-day-options-unique-market-dynamics-and-risk-considerations)、[BofA volmageddon 2.0 被夸大](https://www.advisorperspectives.com/articles/2023/02/23/bank-of-america-says-options-driven-volmageddon-2-0-warning-is-overblown)

**尾部事件**：[sixfigureinvesting XIV 2018](https://www.sixfigureinvesting.com/2019/02/what-caused-the-february-5th-2018-volatility-spike-xiv-termination/)、[CFA Institute Volmageddon](https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products)、[BIS Bulletin 90 (2024-08)](https://www.bis.org/publ/bisbull90.pdf)、[FIA CCP margin 白皮书](https://www.fia.org/sites/default/files/2020-10/FIA_WP_Procyclicality_CCP%20Margin%20Requirements_1.pdf)、[OptionSellers/Cordier 复盘](https://beststockstrategy.com/optionsellers/)、[EBC 引 JPM 系统性情景](https://www.ebc.com/forex/0dte-options-the-hidden-driver-of-market-volatility)

**执行/税收/数据**：[IBKR TWS API options](https://interactivebrokers.github.io/tws-api/options.html)、[IBKR greeks](https://interactivebrokers.github.io/tws-api/option_computations.html)、[tastytrade developer](https://developer.tastytrade.com/)、[tastytrade sandbox](https://developer.tastytrade.com/sandbox/)、[daystoexpiry 1256](https://www.daystoexpiry.com/blog/spx-section-1256-tax)、[Cboe XSP tax](https://www.cboe.com/tradable_products/sp_500/mini_spx_options/tax_benefit/)、[greekslab SPX/SPY/QQQ](https://greekslab.com/blog/spx-vs-spy-vs-qqq-choosing-the-best-underlying-for-0-dte-trading)、[24/7 3 ETF 卖方](https://247wallst.com/investing/2026/06/25/so-you-want-to-sell-0dte-options-3-etfs-that-make-it-possible/)、[Polygon options](https://polygon.io/options)、[Polygon 定价](https://apis.io/plans/polygon-io/polygon-io-plans-pricing/)、[Cboe DataShop](https://datashop.cboe.com/)

---
*免责：本文为策略可行性研究备忘，非投资建议；paper 阶段材料。所有从业者回测数字口径不一、不可横向比较，且含幸存者偏差；下真实规模决策前须以本项目自建的悲观成本回测复核。核心结论：edge（VRP）真实，但验证范式必须从「快速 t 检验」改为「defined-risk sleeve + 极端日压力测试 + 跨 regime 时间」。*
