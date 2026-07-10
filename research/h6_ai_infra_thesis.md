# H6 — AI 基建主题 sleeve 论文（决策级研究）

- **撰写**：宏观主题研究 agent（Claude）
- **日期**：2026-07-10（周五收盘后）
- **数据截止**：最新可得 13F 为 **Q1 2026（持仓日 2026-03-31）**，已滞后约 3.5 个月；Q2 2026 13F 要到 **2026-08-14** 才披露。
- **定位（house style，类比 H4c）**：这是一块**主题 tilt sleeve**，不是主 alpha 假设。它不满足「每日多信号」的验证形态，无法用池内差分快速证伪，因此**不占用 H1/H4 那条事件驱动验证管线**；它是组合的「宏观 beta 地板」候选，靠的是**分层选择 + 纪律性证伪**而非统计显著性。若要进 paper，应作为低频、月度再平衡的 sleeve 处理，并预注册第 4 节的减仓信号。
- **⚠️ 数据可靠性声明（重要）**：本文事实分三档——
  - **A 档（高）**：SEC EDGAR 原文、CNBC/Forbes/Motley Fool/Seeking Alpha/Utility Dive/PJM/公司 8-K。
  - **B 档（中）**：13f.info / whalewisdom / Quiver Quantitative（13F 聚合，头条结构可交叉验证）。
  - **C 档（低，需复核）**：davemanuel / elitecurrensea / annacoulling / insidermonkey 等 SEO 聚合站——**逐笔增减仓的精确 share count 来自 C 档**，多站头条方向一致但**下真实仓位前必须回原始 13F-HR 核对**。
  - 全文用 `[事实]`（含来源）与 `[推断]`（我的判断）标签区分。

---

## 0. 摘要与入场时点诚实评估

### 三句话摘要（决策用）
1. **周期位置**：AI 基建处于**资本开支狂热的中后段**——需求（hyperscaler capex ~$700B、2026 翻倍）与物理瓶颈（电力/变压器 4–5 年 lead time）都还是真实的硬约束，但**估值已大幅透支、且市场自己已经完成从「芯片巨头」向「电力/设备/第二层」的轮动**，靠 beta 躺赢的阶段（2023–2025）基本结束。
2. **最佳层**：**电力与电气设备层（发电+输配电+封装/测试）**——即 hyperscaler 无法用软件绕过、有多年在手订单（backlog）锁定、估值相对芯片链更合理的「铲子的铲子」；这也正是聪明钱（Situational Awareness 做多电力/内存/neocloud 同时做空芯片链、Coatue 从 NVDA 下沉到设备）用真金白银投票的方向。
3. **最大风险**：**AI 变现跟不上资本开支的反身性崩塌**——capex/收入背离已达 ~46%（超过 2001 电信的 32%）、circular financing、GPU 折旧会计争议（Burry 估 $176B 利润虚增）、以及 **Meta 自建云（2026-07-01）已给 neocloud 敲响第一记警钟**；一旦两家以上 hyperscaler 下调 capex，整条链会同步 de-rate，且第二层的 beta 并不比芯片低。

### 2026 年中入场 vs 2023 年入场——诚实的期望回报差异 `[推断]`
- **2023 年入场**：买的是**尚未成为共识的整条链**，享受了「盈利超预期 × 估值倍数扩张」的双击。锚点 `[事实]`：VST 自 2021 起 +695%、CEG 5 年 +540%（[24/7 Wall St, 2026-01-27](https://247wallst.com/investing/2026/01/27/ai-power-needs-are-soaring-is-vistra-energy-vertiv-or-constellation-the-better-buy/)）；NVDA、VRT、GEV 均为数倍到 10 倍级别。那是**非对称的、一生一次的多倍股窗口**。
- **2026 年中入场**：
  - 倍数扩张已大部分兑现——VRT ~48–53x fwd P/E（近 5 年高位）、ASML ~49x、CEG ~26x、GEV 溢价估值；NVDA 反而只 +5% YTD（fwd P/E 25.4）、AVGO +8% YTD，**megacap 芯片已经领跌**。
  - **市场已经先于你完成轮动**：2026 YTD 涨幅集中在中小盘、设备与电力，而非头条巨头。你想指的「第二层」，一部分已经不便宜。
  - 反身性/折旧/circular financing 风险已从「无人担心」变成「人人盯着」——**下行波动显著放大**（SOXX 单周 -10% 后反弹、neocloud 单日 -14~17%）。
  - **诚实的期望**：从这里入场，最好的电力/设备/封装层，基准情形是「跟着多年 backlog 复利、若 capex 周期再撑 2–3 年则中双位数~20%/年」，而**不再是 3–10 倍**；同时要接受 **-30% 到 -50% 的真实回撤概率**（capex 一旦转向）。**edge 从「主题 beta」变成了「分层选择 + 证伪纪律 + 择时减仓」**——这正是把它做成 sleeve、并预注册 kill 信号的理由。

---

## 1. 基金持仓侦察（复制聪明钱的公开信息）

### 1.1 Situational Awareness LP（Leopold Aschenbrenner）— 本主题最纯粹的 AI-native 聪明钱

- **背景** `[事实]`：前 OpenAI 研究员 Aschenbrenner 创立，论点为 AGI 2027–2030 到来；Q1 2026 13F 规模 **$13.68B（42 个持仓）**，较 Q4 2025 的 **$5.52B（29 个持仓）翻倍以上**。CIK `0002045724`，Q1 13F EDGAR 受理 2026-05-15、报备日 2026-05-18。（[13f.info](https://13f.info/manager/0002045724-situational-awareness-lp)，B 档；[Yahoo Finance](https://finance.yahoo.com/markets/options/articles/leopold-aschenbrenners-situational-awareness-files-174339413.html)，A 档）

**核心结构 = 杠铃：做多「电力+内存+neocloud」× 做空「整条芯片链」** `[事实，结构 A/B 档交叉验证；逐笔 share count 为 C 档待核对]`

前 10 大**多头（股票）**及环比变化（[davemanuel, 2026-05-19](https://www.davemanuel.com/2026/05/19/leopold-aschenbrenner-q1-2026-13f-situational-awareness/)，C 档）：

| Ticker | 公司 | 市值 | %书 | Q1 动作 | 环节 |
|---|---|---|---|---|---|
| BE | Bloom Energy | $879M | 6.4% | **减 35.6%**（从 15.9% 砍到 6.4%） | 燃料电池/behind-the-meter 电 |
| SNDK | SanDisk | $724M | 5.3% | 加 8.2% | NAND 内存 |
| CRWV | CoreWeave | $556M | 4.1% | 加 17.7% | neocloud |
| IREN | IREN | $401M | 2.9% | 加 34.5% | 挖矿转 AI 算力 |
| CORZ | Core Scientific | $389M | 2.8% | 减 9.6% | 算力/数据中心 |
| APLD | Applied Digital | $320M | 2.3% | 加 18.9% | AI 数据中心 |
| RIOT | Riot Platforms | $142M | 1.0% | 加 86.5% | 挖矿转算力 |
| CLSK | CleanSpark | $104M | 0.8% | **加 648%** | 挖矿转算力 |
| SEI | Solaris Energy Infra | $62M | 0.5% | 减 40.8% | 移动电源/发电 |
| TE | T1 Energy | $44M | 0.3% | 新建 | 电力 |

**新开的看跌期权（put）书（全部新建，Q1 2026）**——13F 按**标的名义价值**列示：

| Ticker | 名义 put | %书 |  | Ticker | 名义 put | %书 |
|---|---|---|---|---|---|---|
| SMH（半导体 ETF） | $2.04B | 14.9% |  | MU | $584M | 4.3% |
| NVDA | $1.57B | 11.5% |  | TSM | $535M | 3.9% |
| ORCL | $1.07B | 7.8% |  | ASML | $494M | 3.6% |
| AVGO | $1.01B | 7.4% |  | INTC | $159M | 1.2% |
| AMD | $969M | 7.1% |  | GLW | $21M | 0.2% |

**put 名义合计 ~$8.46B（占书 62%）**。（[davemanuel](https://www.davemanuel.com/2026/05/19/leopold-aschenbrenner-q1-2026-13f-situational-awareness/)，C 档；结构经 [Quiver Quantitative](https://www.quiverquant.com/news/Former+OpenAI+Employee%E2%80%99s+Hedge+Fund+Unveils+Massive+Nvidia+and+AI+Chip+Options+Positions) 与 [annacoulling](https://www.annacoulling.com/stock-trader-tips/situational-awareness-lp-q1-2026-13f-filings-explosive-growth-to-13-7b-doubling-down-on-ai-energy-infrastructure-while-hedging-the-semiconductor-layer/) 交叉印证，B 档）

**最近两个季度的方向变化（Q4 2025 → Q1 2026）** `[事实]`：
- Q4 2025 是**纯多头形态**：top 持仓为 BE、CRWV calls、INTC calls、LITE（Lumentum 光模块，曾占 8.68%）。
- Q1 2026 **质变为杠铃**：① 保留并加码电力/内存/neocloud 多头（但**把最大的 BE 从 15.9% 砍到 6.4%**——获利了结 or 降集中度）；② **清仓光模块**（LITE、Coherent 全退）、退出 INTC calls、Cipher/Hut8/EQT/Tower Semi/Liberty Energy/Kilroy；③ **全新叠加 $8.46B 做空芯片链的 put overlay**。

> **关键推断 `[推断]`**：最懂 AI 的钱，**不做多头条芯片巨头，反而系统性做空整条芯片链**，同时做多**电力、内存、算力承包商**。这与「AI 基建=买 NVDA」的散户直觉相反，强烈支持本论文的「第二层 > 芯片层」倾向。但**必须给三条 caveat**：(a) 13F 只披露 put 的**标的名义值，不含 premium/delta/行权价/到期日**——$8.46B 可能是廉价的深度虚值尾部对冲，绝不等于 $8.46B 的净空头暴露；(b) 这是**单一天（3-31）快照**，且已滞后 3.5 个月，Aschenbrenner 以高换手著称，现仓可能已大变；(c) 他的 AGI 时间表是**极端观点**，其组合是「押 AGI 硬件瓶颈在电力、软件/芯片会被商品化」的**特定叙事**，未必是稳健的风险收益判断。

### 1.2 Coatue（Philippe Laffont）— 已知重仓 AI、正在「沿链下沉」

`[事实]`（[Seeking Alpha](https://seekingalpha.com/news/4594622-quant-ratings-on-coatue-managements-top-holdings-tsm-gev-lrcx-amat-avgo)、[TipRanks](https://www.tipranks.com/news/coatue-soars-24-in-2026-with-strategic-bets-on-semiconductors-and-energy)、[elitecurrensea](https://elitecurrensea.com/stocks/coatue-asml-nvidia-trim-q1-2026-13f/) C 档）：
- Q1 2026 13F 规模 **$29.0B（前季 $39.96B）**，62 个持仓。前五：**TSM、GEV、LRCX、AMAT、AVGO**。
- **动作方向**：**第 11 次/12 季减持 NVDA**；新建 **ASML $655M**；**AMAT +79%**、**TSM +6.9%**；但 **GEV 减 23.7%**（对电力龙头获利了结）。基金 2026 年 +24%。
- **主题解读** `[推断]`：Coatue 在「**从最拥挤的 NVDA 下沉到制造它的设备（LRCX/AMAT/ASML/TSM）**」，同时**对已大涨的电力（GEV）反而减仓**——这是与 SA「做空芯片、做多电力」**部分矛盾**的信号。两家聪明钱在「芯片 vs 电力」谁更贵的问题上分歧，说明**层内估值已到需要择时的位置**，不宜无差别追高。

### 1.3 Viking（Andreas Halvorsen）与广谱信号
- Viking `[事实]`（[13f.info Q1 2026](https://13f.info/13f/000110380426000004-viking-global-investors-lp-q1-2026)）：$35.7B、77 持仓，前五 V / **TSM 4.22%** / SCHW / DIS / FTV——**AI 基建并非其核心**，唯一相关的头部仓是 TSM。作为「多元多空基本面基金」，它对本主题**不是高信号源**。
- 广谱 `[事实]`（[BBAE](https://www.bbae.com/blog/13f-highlights-where-top-investors-moved-in-q1-2026/)、[moomoo 超投汇总](https://www.moomoo.com/community/feed/after-analyzing-the-13f-holdings-of-dozens-of-super-investors-116590293483526)）：Q1 2026 顶级投资者的共识是「进一步集中于 **AI 基建 + 高护城河现金牛平台**」，宏观叙事从「无形资产（芯片/软件）」转向「**有形资产（电力、算力、物理基建）**」。

### 1.4 13F 的滞后性与局限（务必牢记）`[事实]`
1. **45 天滞后**：Q1 数据为 3-31 快照、5 月中才报备，**今天已 3.5 个月旧**；Q2 要等 **8-14**。高换手基金（如 SA）现仓可能已大幅不同。
2. **只含多头 + 长期权**：**不含股票空头、不含 put 的 premium/delta/行权价/到期**——所以「$8.46B put」不能读成 $8.46B 空头暴露。
3. **只含美国上市 13(f) 证券**：不含现金、外盘（如 SK Hynix、Siemens Energy、Hitachi）、大宗、私募、债。
4. **快照非轨迹**：看不到季中的高抛低吸；季末美化（window dressing）无法排除。
5. **规模 ≠ 信念**：名义美元受当季价格波动影响，减仓可能只是再平衡而非看空。

---

## 2. 产业链映射与周期位置（2026 年中真实状况）

### 2.1 分层地图：表现 / 估值 / 共识担忧

| 层 | 代表标的 | 2026 表现 `[事实]` | 估值粗量级 `[事实]` | 市场共识担忧 `[推断/事实混合]` |
|---|---|---|---|---|
| **芯片-巨头**（GPU/ASIC） | NVDA, AVGO, ORCL | NVDA **+5% YTD**、AVGO +8% YTD（**跑输**大盘）；SMH **+66% YTD** 但涨幅集中在中小盘/设备 | NVDA fwd P/E **25.4**（增速 65%，绝对倍数其实不贵） | capex/收入背离、circular financing、**聪明钱的做空标的**、折旧会计（Burry） |
| **内存/HBM** | MU, SNDK, SK Hynix(外) | HBM3E **2026 售罄**、价格同比双位数涨；DDR5 现 **$375 地板** | 内存股周期性强，倍数偏低 | 强周期（memory 永远周期）；**Micron HBM 份额仅 5–10%**（SK Hynix 50–62%）= 落后者风险 |
| **先进封装/测试** | TSM(CoWoS), AMKR | **CoWoS 2026 完全售罄**（~1M wafer、NVDA 占 ~60%），全链**最紧环节** | AMKR（#2 OSAT）估值远低于芯片设计 | 单客户（NVDA）集中、资本密集、良率 |
| **半导体设备** | ASML, LRCX, AMAT, KLAC | LRCX FY26 系统收入 +32%；受 AI/DRAM EUV 拉动 | **ASML fwd 49x**（历史区间上半）、LRCX 33x、AMAT ~38x（组内最便宜） | 倍数已高；中国/出口管制；WFE 见顶担忧 |
| **发电/IPP**（核/气） | GEV, CEG, VST, BE | GEV backlog **$263B**、燃气轮机**售罄至 2030–31**；VST-Meta 20 年 2,609MW 核电 PPA | GEV 溢价；CEG fwd **~26x**、VST **~18x** | 大涨后估值贵（**Coatue 已减 GEV**）；merchant 电价/监管；PPA 再定价 |
| **输配电/电气设备** | ETN, PWR, POWL, HUBB, NVT, GEV | ETN **+28% YTD**，数据中心订单 **+240% YoY**、电气 backlog +48%；PWR backlog **$44B**（+27.5%） | ETN 距目标价 5% 内；POWL/HUBB/NVT 相对温和 | 强周期；若数据中心延期加剧，订单可能 air-pocket；关税/原料 |
| **数据中心 REIT** | EQIX, DLR | DLR FFO/股 +8%、EQIX AFFO +9–11%；均大扩产 | REIT 估值受利率牵制 | 利率敏感；供给过剩恐慌；**产能被电力卡脖子** |
| **散热/冷却** | VRT, MOD, NVT | VRT ~$333、backlog **>$15B**；MOD Q4 FY26 收入 +47% | **VRT fwd 48–53x（5 年高位）**；MOD ~25x（比 VRT 便宜一半） | VRT 倍数极端、容错低；竞争（Delta/Boyd/自研）；单一主题 |
| **网络/光模块** | ANET, CIEN, COHR, LITE, FN, CRDO, ALAB | OFC 2026 主题转向 CPO/共封装光；SA **已清仓 LITE/COHR** | 分化大 | **技术换代风险**（CPO 可能颠覆可插拔）；订单 lumpy |
| **neocloud/算力** | CRWV, NBIS, IREN, APLD, CORZ | **2026-07-01 因 Meta 自建云单日 -14~17%**；CRWV backlog $99.4B、2026 capex 上调至 $35B | 高增长高估值/多亏损 | **客户集中**（CRWV $21B、NBIS $27B 均系 Meta）、circular financing、GPU 折旧、债务融资——**全链最脆弱** |
| **上游材料** | GOES 电工钢、铜 | 变压器 lead time 拉到 **4–5 年**；GOES + 铜短缺 | 无干净纯标的 | 美国 GOES **仅一家本土供应商**（AK Steel/Cleveland-Cliffs）；难以纯暴露 |

### 2.2 关键周期信号现状 `[事实]`

- **Hyperscaler capex 指引（Q1 2026 电话会，全部上调）**：MSFT、GOOG、AMZN、META、ORCL 合计 **2026 ~$700–725B，约为 2025 的 2 倍**。Amazon ~$200B；Alphabet **$175–185B**（Google Cloud backlog >$460B）；Meta **$125–145B**（**上调后股价 -6%**）；Microsoft FQ3 capex $30.88B（+84% YoY）。（[CNBC 2026-02-06](https://www.cnbc.com/2026/02/06/google-microsoft-meta-amazon-ai-cash.html)、[CreditSights](https://know.creditsights.com/insights/tech-raising-hyperscaler-capex-2026-estimates/)、[Futurum](https://futurumgroup.com/insights/ai-capex-2026-the-690b-infrastructure-sprint/)）→ **周期信号：仍在加速，尚无 hyperscaler 掉头。**
- **GPU 供需/价格（混合信号）**：H100 云租 2026-05 约 **$2.29–3.12/hr**，较峰值 **跌 64–75%**；二手 H100 SXM5 从 $40k（2023 末）跌到 $12–22k。**但 2026-03 起容量重新吃紧**，1 年期合约价回到 $2/hr 上方——**价格已从单边下跌转为企稳/局部反弹**。（[IntuitionLabs](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison)、[SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)、[Thunder Compute 2026-07](https://www.thundercompute.com/blog/ai-gpu-rental-market-trends)）→ **信号：需求端未证伪，但价格弹性说明供给正在追上，边际紧张度在波动。**
- **电力瓶颈（真实且在加剧）**：美国 2026 计划数据中心 **~12GW 中 ~7GW 被延期/取消**；变压器 lead time 拉到 **4–5 年**（HV 变压器/开关柜为 gating）；**PJM 容量价从 $28.92/MW-day（24/25）→ $269.92（25/26）→ $329.17（26/27，且已触价格上限）**；PJM West 10 年期太阳能 PPA **仍 >$90/MWh，近历史高 $95**。（[Utility Dive](https://www.utilitydive.com/news/pjm-board-backstop-auction-data-center-interconnection/809967/)、[IEEFA](https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10)、[pv-magazine 2026-05-11](https://pv-magazine-usa.com/2026/05/11/u-s-transformer-market-faces-severe-supply-constraints-as-lead-times-extend-to-four-years/)）→ **信号：电力是当下最硬、最未被证伪的瓶颈；PPA/容量价仍在高位=需求未松。**

### 2.3 周期位置判断 `[推断]`
综合：**需求侧（capex）与物理瓶颈（电力/变压器/CoWoS）都还没有出现拐点**，所以**主题尚未到该系统性清仓的时点**；但**估值侧、以及市场结构（megacap 已领跌、涨幅下沉到第二层、聪明钱开始对冲/减仓）都指向中后段**。类比：像是**牛市第 3–4 局而非第 1 局**——还能打，但要开始盯记分牌（第 4 节），并优先买「便宜的铲子」而非「贵的头条」。

---

## 3. 「第二层」候选（受益逻辑清晰、关注度低于 NVDA 级）

> 筛选标准：hyperscaler **无法用软件绕过** × **多年 backlog 锁定** × 估值相对芯片链**不算最离谱** × 媒体关注度低于 NVDA/megacap。均为 `[推断]` 层面的候选（估值/表现为 `[事实]`），**入场前需各自做基本面 + 最新估值复核**；不构成个股推荐。

| # | 标的 | 环节 | 一句话受益逻辑 | 一个主要风险 |
|---|---|---|---|---|
| 1 | **ETN**（Eaton） | 电气/grid-to-chip | 数据中心电气订单 +240% YoY、backlog +48%，卖的是每个机柜都要的配电，+28% YTD 仍距目标 5% | 强周期工业股，若数据中心延期潮扩大，订单会 air-pocket |
| 2 | **PWR**（Quanta） | 电网施工/劳务 | $2.4T TAM、$44B backlog，电网扩建的「人手」瓶颈，别人有钱也雇不到熟练工 | 劳动力/执行风险，项目利润率 lumpy |
| 3 | **AMKR**（Amkor） | 先进封装/测试（OSAT） | CoWoS 是全链最紧环节，AMKR 是 TSM 之外的第二供应源（Intel EMIB 合作），估值远低于芯片设计 | 单客户（NVDA）集中、资本密集、良率与价格战 |
| 4 | **POWL**（Powell） | 中压开关柜/电气总成 | 数据中心/电力/LNG 都要的定制开关柜，小盘、覆盖少，2025 关税冲击时被错杀 | 小盘、订单 lumpy，单季波动大 |
| 5 | **MOD**（Modine） | 数据中心冷却 | 液冷/CDU 直接受益，fwd ~25x 只有 VRT 的一半，收入 +47% | 有汽车传统业务拖累，散热竞争激烈 |
| 6 | **HUBB / NVT**（Hubbell / nVent） | 电气连接/机柜/液冷分配 | 卖变压器、连接件、液冷歧管的「耗材」型电气件，估值比 VRT 温和 | 周期性；部分已随主题重估 |
| 7 | **VST**（Vistra） | IPP（核+气） | fwd ~18x 明显低于 CEG ~26x，已签 Meta 20 年 2,609MW 核电 PPA，现金流实在 | merchant 电价敞口、监管、核资产集中 |
| 8 | **SNDK**（SanDisk） | NAND 内存 | AI 推理/存储拉动、SA 的第二大多头；内存涨价周期（DDR5 $375 地板） | 内存深度周期股，价格一转向盈利急跌 |
| 9 | **FN**（Fabrinet） | 光模块代工 | 光互联放量的「隐形代工厂」，关注度低于 COHR/ANET | CPO/共封装换代可能长期削弱可插拔需求 |

**关于上游材料** `[推断]`：变压器的真瓶颈在 **GOES 电工钢 + 铜**，理论上最「第二层」，但缺乏干净的纯标的——Cleveland-Cliffs（CLF）含 GOES 但被钢铁大宗周期稀释，铜矿（FCX 等）是宏观品种。**结论：上游主题正确但难以用美股干净表达，优先级低于电气设备。**

**刻意规避/降配的「第一层拥挤」** `[推断]`：VRT（48–53x）、GEV（大涨后 Coatue 已减）、CRWV/NBIS（最脆弱、客户集中+circular financing）——逻辑都对但**要么估值透支、要么风险不对称**，不属于「未被充分定价」，只适合小仓位或等回撤。

---

## 4. 证伪条件（出现即应减仓/退出的可监控信号）

> sleeve 若进 paper，以下预注册为 **kill / de-risk 触发器**。当前值均为 `[事实]`，阈值与判读为 `[推断]`。

**信号 1 — Hyperscaler capex 掉头（最高权重）**
- 监控：MSFT/GOOG/AMZN/META/ORCL 的季度 capex 指引方向。
- 当前值：全部**上调**，2026 ~$700–725B。
- **触发**：**≥2 家**在同一财报季**下调**全年 capex 指引，或明确提「优化/放缓」措辞 → **立即减半**。**下一个观察点：Q2 2026 财报（2026-07 底–08 初）**。

**信号 2 — GPU 租赁/二手价格持续走弱**
- 监控：H100/H200 1 年期合约云租价、二手 H100 SXM5 成交价。
- 当前值：现货较峰值 -64~75% 但 2026-03 起企稳、1 年期回到 >$2/hr。
- **触发**：1 年期合约价**连续 3 个月**下跌 **且** 跌破 $2/hr、或二手 H100 跌破 $12k → 说明算力需求侧真的松了 → 减仓 neocloud/算力层优先。

**信号 3 — 电力/PPA 价格转弱（本主题的命脉）**
- 监控：PJM 容量拍卖出清价、PJM West 长期 PPA 价、燃气轮机/变压器 lead time。
- 当前值：容量价 $329/MW-day（触顶）、PPA >$90/MWh（近历史高）、轮机售罄至 2030–31、变压器 4–5 年。
- **触发**：下一次 PJM 容量拍卖**明显低于 $329/MW-day**、或长期 PPA **跌破 ~$75/MWh**、或 GEV/ETN 财报里 **backlog 环比转降 / lead time 缩短** → 电力瓶颈在缓解 = 电力层的核心逻辑被削弱 → 减电力/电气层。

**信号 4 — AI 变现跟不上（反身性）恶化过阈值**
- 监控：capex/收入背离度、OpenAI/Anthropic 收入 run-rate、Google Cloud/CRWV backlog 增速、合同取消。
- 当前值：背离 ~46%（vs 2001 电信 32%）、Sequoia 估 ~$600B 收入缺口、OpenAI ~$25B ARR；**Meta 自建云已致 neocloud 2026-07-01 单日 -14~17%**（第一记警钟）。
- **触发**：出现**大额算力合同取消/缩表**（尤其 Meta/Microsoft 对 CRWV/NBIS）、或 hyperscaler cloud backlog **环比转降**、或折旧会计争议（Burry $176B）演变为**某家下调 GPU useful life / 计提减值** → 全链 de-rate 风险 → 减半至清仓。

**信号 5 — 聪明钱与主题内部结构转向**
- 监控：**2026-08-14 的 Q2 13F**（SA 是否平掉电力/内存多头或回补芯片 put；Coatue 是否继续减）、主题篮子广度（电力/电气等权指数是否跌破 200 日线）、内部人抛售、neocloud/数据中心债与 CDS 利差。
- 当前值：SA 做多电力/做空芯片、Coatue 沉入设备但减 GEV。
- **触发**：Q2 13F 显示**多家主题基金集体减电力/算力多头**、或篮子广度转熊（新高家数萎缩、等权破 200DMA）、或 **CRWV/Oracle/数据中心 ABS 利差显著走阔**（债市先于股市定价 capex 融资压力）→ 跟随减仓。

**（附）单一「一票否决」宏观信号 `[推断]`**：若出现**信用事件**——某 neocloud 或重资本 AI 数据中心运营商**债务违约/再融资失败**——视同主题级 kill，不等其他信号确认。

---

## 附：主要来源清单（按主题）

**基金 13F**：[13f.info-SA](https://13f.info/manager/0002045724-situational-awareness-lp)、[davemanuel-SA](https://www.davemanuel.com/2026/05/19/leopold-aschenbrenner-q1-2026-13f-situational-awareness/)、[Quiver-SA](https://www.quiverquant.com/news/Former+OpenAI+Employee%E2%80%99s+Hedge+Fund+Unveils+Massive+Nvidia+and+AI+Chip+Options+Positions)、[annacoulling-SA](https://www.annacoulling.com/stock-trader-tips/situational-awareness-lp-q1-2026-13f-filings-explosive-growth-to-13-7b-doubling-down-on-ai-energy-infrastructure-while-hedging-the-semiconductor-layer/)、[elitecurrensea-Coatue](https://elitecurrensea.com/stocks/coatue-asml-nvidia-trim-q1-2026-13f/)、[TipRanks-Coatue](https://www.tipranks.com/news/coatue-soars-24-in-2026-with-strategic-bets-on-semiconductors-and-energy)、[13f.info-Viking](https://13f.info/13f/000110380426000004-viking-global-investors-lp-q1-2026)、[BBAE 13F 综述](https://www.bbae.com/blog/13f-highlights-where-top-investors-moved-in-q1-2026/)

**Capex/周期**：[CNBC capex](https://www.cnbc.com/2026/02/06/google-microsoft-meta-amazon-ai-cash.html)、[CreditSights](https://know.creditsights.com/insights/tech-raising-hyperscaler-capex-2026-estimates/)、[Futurum](https://futurumgroup.com/insights/ai-capex-2026-the-690b-infrastructure-sprint/)、[Forbes-capex/收入背离](https://www.forbes.com/sites/jasonkirsch/2026/06/02/the-ai-capex-to-revenue-gap-is-widening---and-markets-are-starting-to-notice/)

**GPU 价格**：[IntuitionLabs](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison)、[SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)、[Thunder Compute](https://www.thundercompute.com/blog/ai-gpu-rental-market-trends)

**电力/电网**：[Utility Dive-PJM](https://www.utilitydive.com/news/pjm-board-backstop-auction-data-center-interconnection/809967/)、[IEEFA-PJM 容量价](https://ieefa.org/resources/projected-data-center-growth-spurs-pjm-capacity-prices-factor-10)、[pv-magazine-变压器](https://pv-magazine-usa.com/2026/05/11/u-s-transformer-market-faces-severe-supply-constraints-as-lead-times-extend-to-four-years/)、[Utility Dive-GEV 轮机](https://www.utilitydive.com/news/ge-vernova-gas-turbine-investor/807662/)、[Alphastreet-Eaton](https://news.alphastreet.com/eaton-etn-posts-record-q1-revenue-as-electrical-backlog-surges-48-on-data-center-demand/)

**半导体/内存/封装/设备**：[Benzinga-SMH](https://www.benzinga.com/etfs/sector-etfs/26/07/60290857/semiconductor-etfs-ai-2026-psi-smh-soxx-soxq-xsd)、[Silicon Analysts-CoWoS](https://siliconanalysts.com/analysis/foundry-allocation-status-q1-2026)、[Silicon Analysts-HBM](https://siliconanalysts.com/tools/hbm-analysis)、[GuruFocus-ASML PE](https://www.gurufocus.com/term/forward-pe-ratio/ASML)、[Morningstar-WFE](https://www.morningstar.com/stocks/raising-valuations-applied-materials-kla-lam-research-with-higher-ai-expectations-wfe)

**电力/散热/REIT/neocloud 估值**：[Motley Fool-CEG/VST](https://www.fool.com/coverage/better-buy/2026/06/25/constellation-energy-vs-ge-vernova-which-utilities-stock-is-a-better-buy-in-2026/)、[Seeking Alpha-VRT](https://seekingalpha.com/article/4890719-vertiv-holdings-the-15-billion-backlog-liquid-cooling-dominance-and-the-ai-infrastructure-trade-wall-street-is-still-underpricing)、[MarketWise-REIT](https://marketwise.com/investing/best-data-center-reits-ai-infrastructure/)、[24/7-neocloud/Meta](https://247wallst.com/investing/2026/07/01/nebius-coreweave-and-iren-tumble-on-metas-cloud-ambitions-is-this-the-end-of-the-neocloud-boom/)、[24/7-电力多倍股](https://247wallst.com/investing/2026/01/27/ai-power-needs-are-soaring-is-vistra-energy-vertiv-or-constellation-the-better-buy/)

**风险/证伪**：[CNBC-GPU 折旧/Burry](https://www.cnbc.com/2025/11/14/ai-gpu-depreciation-coreweave-nvidia-michael-burry.html)、[Man Group-AI 泡沫](https://www.man.com/insights/the-ai-bubble)、[Fool-Meta 警告 neocloud](https://www.fool.com/investing/2026/07/07/meta-platforms-just-gave-a-massive-warning-to-core/)

---
*免责：本文为主题研究备忘，非个股推荐；paper 阶段材料。所有逐笔 13F 数据下真实仓位前须回 SEC EDGAR 原文（CIK: SA `0002045724` / Coatue `0001135730` / Viking `0001103804`）核对。*
