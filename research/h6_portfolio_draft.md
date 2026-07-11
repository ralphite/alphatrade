# H6 — AI 基建 sleeve 组合草案（可执行）

- **撰写**：组合构建 agent（Claude）
- **日期**：2026-07-10（周五收盘后）
- **上游**：`research/h6_ai_infra_thesis.md`（论点/周期位置/证伪信号）+ `HYPOTHESES.md` §H6（预注册形态与 kill 信号）
- **性质**：paper sleeve 草案，**已装填、待触发**。定位 = 组合的「宏观 beta 地板」候选，靠**分层选择 + 纪律性证伪**而非统计显著性（house style，同 H4c）。
- **纪律边界（写死）**：只做 long；排除市值 <$500M 或 ADV<$5M（流动性）；排除 thesis 标注「估值透支」的第一层拥挤名（VRT 48–53x、GEV、CRWV/NBIS）；明确**不追芯片巨头层**。
- **数据档级**：市值/表现/催化为 `[事实]`（2026-07 WebSearch 核实，见各标的脚注来源）；权重/倾斜/层归类为 `[推断]`。

---

## 0. 一句话结论与入场闸

**结论**：从 thesis 第二层候选出发，核实并扩展到 **16 个候选**，按「hyperscaler 无法软件绕过 × 多年 backlog × 估值不最离谱 × 关注度 < NVDA 级 × 流动性达标」筛出 **10 只等权（±2pp 倾斜）** 组成 sleeve，覆盖**发电/输配电/冷却/封装测试/电网软件**五层，单层 ≤31%，与 QQQ 近乎正交（仅 CEG 一只重叠）。

**入场闸（预注册，来自 `HYPOTHESES.md` H6 line 104）**：本草案 **go-live 触发 = 2026 Q2 hyperscaler capex 指引确认**（MSFT/GOOG/AMZN/META/ORCL，2026-07 底–08 初财报）。
- 若 **≥2 家下调**全年 capex 或转「优化/放缓」措辞 → **不入场**（草案作废/推迟）。
- 若指引**稳/升** → 次一交易日按 §5 目标权重建仓。
- 当前（2026-07-10）5 家 Q1 指引全部上调（2026 ~$700–725B），闸门**未证伪**，等 Q2 确认。

---

## 1. 候选漏斗（16 候选 → 10 入选）

| # | Ticker | 层 | 市值(2026-07) | 入选? | 一句话裁决 |
|---|---|---|---|---|---|
| 1 | **ETN** | 输配电/电气 | ~$160B | ✅ | 数据中心电气订单 +240% YoY，配电必需品 |
| 2 | **PWR** | 输配电/电网施工 | ~$100B | ✅ | record backlog $48.5B，熟练工瓶颈=护城河 |
| 3 | **POWL** | 输配电/开关柜 | ~$9.0B | ✅ | 小盘 torque，record $400M+ 单笔数据中心订单 |
| 4 | **VST** | 发电/IPP | ~$48B | ✅ | 层内最便宜（fwd ~18x），Meta/AWS 核电 PPA |
| 5 | **TLN** | 发电/IPP 核 | ~$17B | ✅ | Amazon 1,920MW/至 2042 核电 PPA，纯核 torque |
| 6 | **CEG** | 发电/IPP 核 | ~$90B | ✅ | post-Calpine 全美最大私营发电，PE~21 |
| 7 | **MOD** | 冷却 | ~$14.6B | ✅ | 液冷，fwd ~25x 只有 VRT 一半，$4B 长约 |
| 8 | **NVT** | 冷却+电气连接 | ~$25B | ✅ | 液冷分配+电气件双层受益 |
| 9 | **AMKR** | 封装/测试 OSAT | ~$17B | ✅ | CoWoS 全链最紧瓶颈，TSM 外第二源，最便宜 |
| 10 | **ITRI** | 电网软件 | ~$3.75B | ✅ | grid edge 软件纯标的，fwd 13.6x 最便宜 |
| 11 | **HUBB** | 输配电/电气件 | ~$27B | ❌ | 与 ETN/POWL/PWR 重叠，输配电层已满；NSI 收购加杠杆 |
| 12 | **ONTO** | 封装量测 | ~$15.3B | ❌ | trailing P/E 142 触估值纪律；AMKR 更便宜覆盖封装 |
| 13 | **STRL** | 数据中心场地施工 | ~$22B | ❌ | 与 PWR 施工重叠；YTD 大涨($685+)削弱安全边际 |
| 14 | **FN** | 光模块代工 | ~$17B | ❌ | CPO 换代风险+近月 -30%+SA 已清仓光模块；偏网络层非核心 |
| 15 | **GEV** | 发电设备 | ~$298B | ❌ | fwd ~60x 估值透支+Coatue 已减（thesis 明确规避） |
| 16 | **SNDK** | NAND 内存 | 数据异常 | ❌ | 深周期+贴近芯片层（明确规避）；公开市值数据不可靠 |

> 另有 thesis 已排除、本轮不再复核的名单见 §4（VRT / CRWV / NBIS / GLW / BE）。

---

## 2. 入选 10 标的详表

> 权重列：等权基线 10% = $2,500；倾斜上限 ±2pp（=±$500）；净倾斜和为 0，sleeve 满仓 $25k。

### 发电 / IPP 层（合计 29%）

**① VST — Vistra｜发电/IPP（气+核+零售）｜市值 ~$48B｜权重 11%（+1pp）** `[事实市值]`
- **mini-thesis**：受益——已签 Meta/AWS 2,600MW PJM 核电 PPA，气+核+零售一体化，Q1 record adj EBITDA $1.5B、FY26 FCFbG +20%。**为何未充分定价**：fwd ~18x（thesis）明显低于 CEG ~21x / GEV 60x，市场仍当它是传统 merchant IPP 而非 AI-power 平台，新增 PPA 的上行期权未计入（管理层明确「指引未含新 PPA 上行」）。
- **单标的最大风险**：merchant 电价 / PJM 容量价回落 + 核资产集中（单机组事故/监管）。
- **倾斜理由**：层内**最便宜**、PPA 上行期权最厚 → **+1pp**。
- 来源：[stockanalysis/VST](https://stockanalysis.com/stocks/vst/)、[Seeking Alpha](https://seekingalpha.com/article/4911248-vistra-a-buy-on-ai-demand-nuclear-power-and-strong-cash-flow)（$160、$48B、Q2 财报 2026-08-07）

**② TLN — Talen Energy｜发电/IPP（核）｜市值 ~$17B｜权重 10%（等权）** `[事实市值]`
- **mini-thesis**：受益——与 Amazon 签 1,920MW / 至 2042 核电 PPA + SMR/uprate 探索，Susquehanna 直连数据中心的 grid-connected IPP 范式，13.1GW 组合。**为何未充分定价**：纯核 IPP 长约现金流可见度高，但市值仅 $17B、覆盖度远低于 CEG，SMR 期权未定价。
- **单标的最大风险**：单一大客户（Amazon）+ 单一核心资产（Susquehanna）双重集中；behind-the-meter 直连的 FERC 监管不确定。
- **倾斜理由**：torque 高但集中度风险对冲 → 保持**等权**。
- 来源：[stockanalysis/TLN](https://stockanalysis.com/stocks/tln/)、[PowerMag PPA](https://www.powermag.com/talen-amazon-launch-18b-nuclear-ppa-a-grid-connected-ipp-model-for-the-data-center-era/)（$388、$16.7–17.6B）

**③ CEG — Constellation Energy｜发电/IPP（核）｜市值 ~$90B｜权重 8%（−2pp）** `[事实市值]`
- **mini-thesis**：受益——post-Calpine 全美最大私营发电商，24/7 无碳核电 + 5,650MW 长约、1GW uprate、$3.9B capex，trailing PE ~21 合理。**为何未充分定价**：市场担心 Calpine 整合，核电 fleet 对 AI-power 的稀缺性与长约锁定被低估。
- **单标的最大风险**：Calpine $16.4B 整合执行；且它是本篮子**唯一 Nasdaq-100/QQQ 成分**（与 H4c 的 QQQ/QLD 地板重叠）。
- **倾斜理由**：降 QQQ 重叠 + 整合风险 + 层内最拥挤/最被覆盖 → **−2pp**。
- 来源：[stockanalysis/CEG](https://stockanalysis.com/stocks/ceg/market-cap/)、[Calpine 收购](https://markets.financialcontent.com/stocks/article/marketminute-2026-3-10-constellation-energy-finalizes-164-billion-calpine-acquisition-solidifying-lead-in-ai-data-center-power-race)（$250、$90B、trailing PE 21.24）

### 输配电 / 电气层（合计 31%）

**④ ETN — Eaton｜输配电/电气（grid-to-chip）｜市值 ~$160B｜权重 9%（−1pp）** `[事实市值]`
- **mini-thesis**：受益——数据中心电气订单 +240% YoY，Q1 电气 Americas backlog +44%、总订单 $18.3B（+71% organic）、book-to-bill 1.2；卖的是每个机柜都要的配电。**为何未充分定价**：+29% YTD 但仍距分析师目标 ~5%，backlog 可见度到 2027+，市场仍按传统工业周期股给倍数。
- **单标的最大风险**：强周期——数据中心延期潮扩大 → 订单 air-pocket；大盘、涨幅已兑现较多。
- **倾斜理由**：层内最大、最 priced-in → **−1pp**。
- 来源：[stockanalysis/ETN](https://stockanalysis.com/stocks/etn/)、[TIKR](https://www.tikr.com/blog/eaton-stock-200-data-center-order-growth-and-a-7-trillion-market-puts-590-target-in-sight)（$408–422、~$160B、+29% YTD）

**⑤ PWR — Quanta Services｜输配电/电网施工（EPC）｜市值 ~$100B｜权重 10%（等权）** `[事实市值]`
- **mini-thesis**：受益——record backlog $48.5B（电网+地下+AI 数据中心），FY26 指引上调至营收 $34.7–35.2B；电网扩建的「人手」瓶颈，别人有钱也雇不到熟练工 = 护城河。**为何未充分定价**：市场按施工承包商的低估值锚定它，但它是电网现代化 + large-load interconnect 的唯一规模化 EPC。
- **单标的最大风险**：劳动力/执行、项目利润率 lumpy；「grid story 可能已 priced in」（Seeking Alpha 空方观点）。
- **倾斜理由**：**等权**。
- 来源：[8-K/EDGAR](https://www.sec.gov/Archives/edgar/data/0001050915/000119312526193918/d107542dex991.htm)、[Simply Wall St](https://simplywall.st/stocks/us/capital-goods/nyse-pwr/quanta-services)（~$100B、backlog $48.5B）

**⑥ POWL — Powell Industries｜输配电/开关柜｜市值 ~$9.0B｜权重 12%（+2pp）** `[事实市值]`
- **mini-thesis**：受益——record $400M+ 单笔数据中心项目、backlog $1.8B（+33%），arc-resistant 定制开关柜是数据中心/LNG/公用事业都要的硬瓶颈。**为何未充分定价**：小盘（$9B）、覆盖少、2025 关税冲击时被错杀，单季订单跳增未被平滑进估值。
- **单标的最大风险**：小盘、订单 lumpy、单季波动大、客户集中于能源/数据中心 capex。
- **倾斜理由**：层内**最便宜、torque 最大、最未被覆盖** → **+2pp**。
- 来源：[stockanalysis/POWL](https://stockanalysis.com/stocks/powl/)、[public.com/POWL](https://public.com/stocks/powl/market-cap)（$246.51、$8.97B、backlog $1.8B +33%）

### 冷却层（合计 20%）

**⑦ MOD — Modine｜数据中心冷却（液冷/CDU）｜市值 ~$14.6B｜权重 10%（等权）** `[事实市值]`
- **mini-thesis**：受益——Climate Solutions（数据中心冷却）销售 >$400M + 与某超大规模客户 $4B 长期产能协议，FY27 指引营收 +20–35%、record Q4 $954M。**为何未充分定价**：fwd ~25x 只有 VRT（48–53x）一半，市场仍给「汽车零部件」折价，未完全重估其数据中心冷却纯度的提升。
- **单标的最大风险**：传统 HVAC/汽车业务拖累 + 液冷竞争（Vertiv/Boyd/自研）激烈。
- **倾斜理由**：**等权**。
- 来源：[Simply Wall St/MOD](https://simplywall.st/stocks/us/capital-goods/nyse-mod/modine-manufacturing)、[Insider Monkey](https://www.insidermonkey.com/blog/modine-manufacturing-company-mod-gains-from-growing-data-centre-cooling-exposure-1788433/)（$277、$14.65B、$4B 长约）

**⑧ NVT — nVent Electric｜冷却+电气连接｜市值 ~$25B｜权重 10%（等权）** `[事实市值]`
- **mini-thesis**：受益——液冷分配 + 电气连接/保护「耗材」件双层受益，系统保护段是 AI 算力直接受益（RBC 点名）。**为何未充分定价**：估值比 VRT 温和，市场按传统电气件给倍数，液冷 attach 率提升的 mix 上行未计入。
- **单标的最大风险**：周期性；部分已随主题重估；液冷标准（直接芯片 vs 后门）技术路线不确定。
- **倾斜理由**：**等权**。
- 来源：[stockanalysis/NVT](https://stockanalysis.com/stocks/nvt/)、[MarketBeat/NVT](https://www.marketbeat.com/stocks/NYSE/NVT/)（$25–27B、液冷定位）

### 封装 / 测试层（合计 12%）

**⑨ AMKR — Amkor Technology｜先进封装/测试 OSAT｜市值 ~$17B｜权重 12%（+2pp）** `[事实市值]`
- **mini-thesis**：受益——CoWoS 是全链**最紧环节**（2026 售罄），AMKR 是 TSM 之外第二 OSAT 源 + Intel EMIB 合作，Q1 营收 +27% YoY、82.8% 来自 advanced，Arizona 联邦补贴扩产。**为何未充分定价**：估值远低于芯片设计/设备（「卖铲子的铲子」），advanced packaging 从「未来赌注」变「现实」但仍按传统 OSAT 周期估值。
- **单标的最大风险**：单客户（NVDA/Apple）集中、资本密集、良率/价格战。
- **倾斜理由**：全链最紧瓶颈 + 层内唯一标的 + 最便宜 → **+2pp**。
- 来源：[MacroTrends/AMKR](https://www.macrotrends.net/stocks/charts/AMKR/amkor-technology/market-cap)、[Seeking Alpha](https://seekingalpha.com/article/4884743-amkor-technology-advanced-packaging-turns-from-a-future-bet-to-reality)（~$17B、Q1 +27%）

### 电网软件层（合计 8%）

**⑩ ITRI — Itron｜电网软件（grid edge intelligence）｜市值 ~$3.75B｜权重 8%（−2pp）** `[事实市值]`
- **mini-thesis**：受益——grid edge intelligence / smart grid 软件+网络（Networked Solutions + Outcomes 段），公用事业 AI 负荷接入/负荷管理的必需软件层。**为何未充分定价**：股价 −35%/52wk、fwd ~13.6x（**全篮子最便宜**），市场因近期 backlog 消化/部署放缓杀估值，但电网数字化渗透的长期方向未变。
- **单标的最大风险**：**价值陷阱**——−35% 可能反映真实的订单放缓/执行问题，硬件周期拖累软件叙事。
- **倾斜理由**：叙事最弱、执行风险最高 → 小仓起步 **−2pp**（保留电网软件层的敞口，但不重仓押注反转）。
- 来源：[stockanalysis/ITRI](https://stockanalysis.com/stocks/itri/market-cap/)、[CNN/ITRI](https://www.cnn.com/markets/stocks/ITRI)（$86.74、$3.75B、fwd PE 13.6、−35%/52wk）

---

## 3. 组合层面检查

### 3.1 分层分布（纪律：单层 ≤35%）

| 层 | 标的 | 等权 | **倾斜后** |
|---|---|---|---|
| 发电/IPP | VST, TLN, CEG | 30% | **29%** |
| 输配电/电气 | ETN, PWR, POWL | 30% | **31%** |
| 冷却 | MOD, NVT | 20% | **20%** |
| 封装/测试 | AMKR | 10% | **12%** |
| 电网软件 | ITRI | 10% | **8%** |

→ 倾斜后**最大单层 = 输配电 31% ≤ 35%**，**通过**。发电与输配电双桶各约 30%，是本 sleeve 的两大支柱；封装/电网软件为单标的卫星仓。

### 3.2 与 QQQ 重叠度估计

- **名义重叠**：10 只中仅 **CEG** 属 Nasdaq-100/QQQ 成分（sleeve 内 8%，其在 QQQ 权重仅 ~0.4%）。其余 9 只均**非** QQQ 成分——ETN/PWR/VST/MOD/NVT 为 NYSE 工业/公用事业，POWL/ITRI 小盘 Nasdaq，AMKR/TLN 未进 Nasdaq-100。
- **因子正交度**：QQQ = mega-cap 科技/软件/芯片；本 sleeve = 工业电气/公用事业/OSAT/电网软件。二者**风格与因子近乎正交**，恰好为 H4c（QQQ/QLD 地板）提供有效分散。
- **结论**：重叠 ≈ **1/10 只、<1% 组合权重**，重叠度**很低**，达成「与主 sleeve 分散」的设计目标。

### 3.3 组合级风险

- **利率敏感性（重点）**：发电/IPP 桶 **29%**（VST/TLN/CEG）是主要利率敏感端——债券代理属性 + merchant 电价 + 长久期 PPA 现金流；10Y 上行时此桶 de-rate 最猛。**缓释**：①三家 IPP 均有长约 PPA 锁定现金流（非纯 merchant/纯 rate）；②**刻意不放数据中心 REIT**（EQIX/DLR），主动压低久期与纯利率暴露；③工业电气桶 50%（ETN/PWR/POWL/MOD/NVT）更偏 capex/订单驱动、利率敏感度低；④AMKR/ITRI 20% 随半导体/电网 capex 周期，直接利率暴露小。→ 组合对利率的**主要暴露集中且被限定在 ~29% 发电桶**，可控。
- **主题单因子**：10 只共享同一需求驱动（AI capex）；若 capex 拐点则同步 de-rate。这是 sleeve 定位内的**已知集中**，靠 §5 预注册减仓信号管理，**不靠分散消除**（thesis 已定性：这是主题 tilt，不是市场中性 alpha）。
- **其它**：工业电气层订单 air-pocket（数据中心延期）；封装单客户集中（AMKR-NVDA ~60% CoWoS）；ITRI 价值陷阱；neocloud 信用事件的 read-through（虽未直接持有，但会拖累全链 beta）。
- **流动性**：10 只市值区间 $3.75B–$160B，全部 >$500M；ADV 均远 >$5M（最小的 POWL/ITRI 日成交额亦 >$30M）。**通过纪律**。

---

## 4. 落选名单 + 一句话理由（审计留痕）

**本轮核实后剔除：**
- **GEV**（GE Vernova）— fwd ~60x、mega-cap $298B，thesis 明确「大涨后 Coatue 已减」，属**估值透支**、非「未充分定价」。
- **HUBB**（Hubbell）— 优质电气件但与 ETN/POWL/PWR 重叠，输配电层已达 31%（近上限）；NSI 收购新增 $2.8B 债务/整合。
- **ONTO**（Onto Innovation）— 先进封装/HBM 量测逻辑对，但 **trailing P/E 142** 触估值纪律（forward 待验证）；AMKR 已更便宜地覆盖封装层。
- **STRL**（Sterling Infra）— 数据中心场地开发，但与 PWR 施工暴露重叠，YTD 大涨（$685+）削弱安全边际。
- **FN**（Fabrinet）— 光模块代工逻辑对，但 **CPO/共封装换代**技术风险 + 近月 −30% + **SA 已清仓光模块**（LITE/COHR）= 负面聪明钱信号；且偏网络层，非本 mandate 核心。
- **SNDK**（SanDisk）— NAND 内存属深周期、**贴近本 mandate 明确规避的芯片层**；且公开市值/股价数据出现异常（多站返回 $280B / $1,814，不可靠），下真实仓前无法核实。

**thesis 已排除、本轮沿用（不复核）：**
- **VRT**（Vertiv）— fwd 48–53x（5 年高位），thesis 定性「估值透支」，纪律红线。
- **CRWV / NBIS**（neocloud）— 客户集中 + circular financing + Meta 自建云警钟（2026-07-01 单日 −14~17%），下行不对称、全链最脆弱。
- **GLW**（Corning）— 出现在 SA put book，光纤/玻璃被显示/电信业务稀释，无干净 AI 暴露。
- **BE**（Bloom Energy）— SA 主动从 15.9%→6.4% 大幅减仓（负信号）+ ~$879M 接近流动性下限 + 燃料电池单一技术风险。

---

## 5. 执行细节

### 5.1 Sleeve 规模与建仓表

- **规模**：$25,000 = 总组合 $100k 的 **25%**（H6 v1 形态 20–25%，取上限）。**paper only**。
- **建仓触发**：§0 入场闸通过后（2026 Q2 capex 确认稳/升），次一交易日收盘按下表建仓；分数股允许（paper）。

| 序 | Ticker | 层 | 目标权重 | **美元额** | 约股数* |
|---|---|---|---|---|---|
| 6 | **POWL** | 输配电/开关柜 | 12% | **$3,000** | ~12 |
| 9 | **AMKR** | 封装/OSAT | 12% | **$3,000** | ~43 |
| 1 | **VST** | 发电/IPP | 11% | **$2,750** | ~17 |
| 2 | **TLN** | 发电/IPP 核 | 10% | **$2,500** | ~6 |
| 5 | **PWR** | 输配电/施工 | 10% | **$2,500** | ~4 |
| 7 | **MOD** | 冷却 | 10% | **$2,500** | ~9 |
| 8 | **NVT** | 冷却+电气 | 10% | **$2,500** | ~17 |
| 4 | **ETN** | 输配电/电气 | 9% | **$2,250** | ~5.5 |
| 3 | **CEG** | 发电/IPP 核 | 8% | **$2,000** | ~8 |
| 10 | **ITRI** | 电网软件 | 8% | **$2,000** | ~23 |
| — | **合计** | — | **100%** | **$25,000** | — |

\*约股数按 2026-07-10 近似价估算，**以建仓日实价重算**；等权基线 10% = $2,500，倾斜 ±2pp = ±$500，净倾斜和 = 0。

### 5.2 月度再平衡规则

- **频率**：每月**最后一个交易日收盘**（与 H4c TOM 换仓在时间上错开记录）。
- **漂移带**：仅对偏离目标 **>±2.5pp（绝对）或 >±25%（相对）** 的标的交易，减少换手/滑点；带内不动。
- **滑点**：**2bps/边**（与 H4c/H6 口径一致），每笔单独记录。
- **现金/本金**：股息与漂移收益按目标权重再投入；sleeve 名义维持 $25k，内部再平衡，**不追加/抽取本金**（除非组合层面决定调 sleeve 大小）。
- **论点复查（H6 验证范式的核心）**：每次再平衡**同时**重跑 §5.3 五个减仓信号读数，写一行 **go / hold / trim** 结论存档（这是 H6「不做回测、用月度论点复查证伪」的落地动作）。

### 5.3 五个预注册减仓信号 → 监控映射

> 来自 thesis §4 + `HYPOTHESES.md` H6 line 105。触发动作按信号权重分级。

| 信号 | 监控源 / 频率 | 触发阈值 | 动作 | sleeve 内最受影响 |
|---|---|---|---|---|
| **① Hyperscaler capex 掉头（最高权重）** | MSFT/GOOG/AMZN/META/ORCL 财报电话会（CNBC/CreditSights）/ **季度** | ≥2 家同季**下调**全年 capex 或转「优化/放缓」 | **整个 sleeve 立即减半** | 全 sleeve（尤 AMKR/ETN/PWR/发电桶） |
| **② GPU 租赁/二手价走弱** | SemiAnalysis / Thunder Compute / IntuitionLabs / **月度** | 1yr 合约价**连 3 月**跌 **且** <$2/hr，或二手 H100 <$12k | 减算力需求敏感端 | AMKR（封装需求）、间接发电桶 |
| **③ 电力/PPA 价转弱（命脉）** | PJM 容量拍卖出清价、PJM West 长约 PPA、变压器/轮机 lead time、GEV/ETN backlog（Utility Dive/IEEFA/PJM/财报）/ **拍卖事件+季度** | 下次 PJM 容量拍卖明显 <$329/MW-day，或长约 PPA <$75/MWh，或 backlog 环比转降 / lead time 缩短 | 减发电+输配电层 | **发电 29% + 输配电 31%（共 60%）** |
| **④ AI 变现跟不上（反身性）** | capex/收入背离、cloud backlog 增速、合同取消、GPU 折旧会计（Forbes/公司/CNBC-Burry）/ **月度+财报** | 大额算力合同取消/缩表（尤 Meta/MSFT 对 CRWV/NBIS），或 cloud backlog 环比转降，或某家下调 GPU useful life/计提减值 | **减半至清仓**（全链 de-rate） | 全 sleeve |
| **⑤ 聪明钱/结构转向** | SA(CIK 0002045724)、Coatue(0001135730) Q2 13F；篮子等权 vs 200DMA；数据中心 ABS/CDS 利差（13f.info/EDGAR）/ **季度(13F)+周度(广度)** | Q2 13F 显示多家主题基金集体减电力/算力多头，或篮子等权破 200DMA，或数据中心 ABS 利差显著走阔 | 跟随减仓 | 全 sleeve |

**附：单一「一票否决」宏观信号** —— 某 neocloud 或重资本 AI 数据中心运营商**债务违约/再融资失败** = 主题级 kill，**不等其他信号确认**，直接清 sleeve。

### 5.4 近端监控日历

- **2026-07 底–08 初**：Q2 hyperscaler 财报 = **入场闸 + 信号①**（最关键节点）。
- **2026-08-05**：SNDK 财报（未持，内存 read-through / 信号②周边）。
- **2026-08-07**：VST 财报（持仓，backlog/PPA read-through / 信号③）。
- **2026-08-14**：SA / Coatue **Q2 13F**（信号⑤，验证「聪明钱是否仍做多电力」）。
- **滚动**：PJM 容量拍卖公告（信号③）、月度 GPU 价（信号②）、月末再平衡 + 论点复查。

---

## 6. 免责

本文为 paper 阶段组合草案，非个股推荐。市值/表现/催化为 2026-07 WebSearch 核实的 `[事实]`（部分聚合站数据档级为 B/C，下真实仓前须回一手源/实时报价核对）；权重/倾斜/层归类为 `[推断]`。**本草案在 §0 入场闸（Q2 capex 确认）通过前不建仓**；任何时点触发 §5.3 信号即按预注册动作执行，不做事后合理化。
