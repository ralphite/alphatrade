# H6 入场门判定 — Q2 CY2026 Hyperscaler Capex 指引

**判定日期**：2026-08-01
**预注册条件出处**：`HYPOTHESES.md` L104-105、`research/h6_ai_infra_thesis.md` 第 4 节
**入场门原文**：「2026 年 7 月底-8 月初 Q2 hyperscaler 财报 capex 指引确认——若 **≥2 家下调** → 不入场；指引稳/升 → sleeve 上线。」

---

## 0. 判定结果（一句话）

**PASS —— 0/5 家下调，全部持平或上调。** 入场门按预注册口径通过。
**但**：第 4 节「信号 5」的债市分项**已部分触发**（CoreWeave CDS 走阔至隐含 50% 违约概率），详见第 3 节。

---

## 1. 五家 capex 逐一核对

信号 1 监控的是 MSFT/GOOG/AMZN/META/ORCL 五家。全部已发布，无「待发布」。

| 公司 | 发布日 | 当季 capex 实际 | 全年指引（新） | 全年指引（旧） | 方向 |
|---|---|---|---|---|---|
| **MSFT** | 2026-07-29（FQ4，6月季） | **$41.0B**（含融资租赁 $5.6B） | CY2026 **~$175B** | ~$190B | **稳**（见下方重要注解） |
| **GOOG** | 2026-07-22（Q2） | **$44.9B**（去年同期的 2 倍） | FY2026 **$195–205B** | $180–190B | **升** |
| **META** | 2026-07-29（Q2） | **$31.1B**（vs 去年 $17.0B） | FY2026 **$130–145B** | $125–145B | **稳偏升**（下限抬高） |
| **AMZN** | 2026-07-30（Q2） | **$54.2B**（vs 去年 $32.1B） | CY2026 **~$220B** | ~$200B | **升** |
| **ORCL** | 2026-06-10（FQ4） | FY26 全年 $55.7B | FY2027 **~$70B 净 / $90–95B 毛** | FY26 $55.7B | **升** |

四家日历年口径合计 ≈ **$732B**（MSFT 175 + GOOG 200 中值 + META 137.5 中值 + AMZN 220）。
若把 MSFT 还原到会计调整前的可比口径（$190B），合计 ≈ **$747B**。
论文第 2.2 节写的是「2026 ~$700–725B」→ **实际略超原估**。

### ⚠️ MSFT 的重要注解（唯一可能被误判为「下调」的一家）

MSFT 的**表面数字确实从 ~$190B 降到 ~$175B**。机械读数会记成「下调」。但成因是纯会计：

- CFO Amy Hood 宣布：**自 FY27 起把数据中心和办公楼的折旧年限从 15 年延长到 25 年**。
- 连带效果：更多未来数据中心租约从**融资租赁**（计入 capex）转为**经营租赁**（不计入 capex）。
- Hood 原话：调整后 CY2026 capex 预期约 $175B，**"our underlying investment plans remain unchanged"**（底层投资计划不变）。
- 且明确：**FY27 capex 将同比增长**，理由是「全公司组合的需求信号」。
- 市场解读一致：CNBC 当日标题是 **"Microsoft jumps 8% as it boosts capital spending plans, citing demand"**（微软上涨 8%，上调资本开支计划）。股价 +8%。

**判定口径**：记为**「稳」，不记「下调」**。理由=真实投入未变 + 下一财年明确增长 + 市场按「上调」定价。此判断是本次唯一的主观裁量点，特此留痕。

**顺带核对信号 4**：第 4 节信号 4 的触发器之一是「某家**下调** GPU useful life / 计提减值」。MSFT 做的是**反方向**（**延长**年限，且对象是楼和数据中心壳体，不是 GPU）→ **信号 4 未触发**。
但这是一个**盈利质量黄旗**：延长折旧年限会美化利润表，租赁重分类会缩小报表 capex——两者都让数字比实际更好看。留档，不触发动作。

---

## 2. 管理层关于 AI 需求的原话（判断「稳/升」的定性佐证）

全部四家的口径高度一致：**需求仍然大于供给**。没有任何一家出现「优化 / 放缓 / 消化期」措辞（这是信号 1 的第二条触发路径）。

- **MSFT / Amy Hood**：需求持续超过可用产能（demand continued to exceed available capacity）；Azure 增长 43%，下季指引仍约 45%（固定汇率）。Nadella：本季新增 31 个数据中心（全年 88 个）、再加 1GW 产能，**两年内产能翻倍的目标不变**。
- **GOOG / Anat Ashkenazi**：**"demand continues to outpace supply across the industry"**；并确认 **2027 年支出将显著超过 2026 年**。Pichai：**"We're in very early innings of what feels like a secular shift"**、"过去一年我们对前景**更加**看多"。Cloud 增长 82%，backlog 涨到 **$514B**（论文记录的上一个数是 >$460B → **环比上升，未转降**）。
- **META / Zuckerberg**：算力**远远不够**满足所有需求（nowhere near enough compute）；收到大量外部租用算力的报价，同时内部用途也很多；计划做**对外出租 AI 算力**的大生意。
- **AMZN / Andy Jassy**：**"even at that amount, we will still not have enough capacity to meet all the demand we have in 2026, and I believe this dynamic will also be true in 2027 too."** 产能紧张预计延续到 2027，2028 的需求已经很强。

### 诚实的削弱项：涨价 vs 放量

**MSFT 和 AMZN 都把 capex 上调明确归因于「内存/元件涨价」**（Jassy：rising memory prices pushed its capex estimate higher；MSFT：elevated memory and component pricing）。

→ **意味着这轮美元 capex 的上调，有一部分是价格通胀，不是产能放量。**真实机柜/GW 增量小于美元增幅。这不改变「未下调」的判定，但**不应把 $732B 全部当作物理产能需求的证据**。
→ 反向读数：这对论文候选 #8 **SNDK（NAND）** 是正面的——内存涨价周期被 hyperscaler 侧确认。

---

## 3. 减仓信号快查（第 4 节 kill 触发器）

| 信号 | 触发阈值 | 最新实测 | 状态 |
|---|---|---|---|
| **1 Hyperscaler capex 掉头** | ≥2 家下调 / 提「优化放缓」 | 0/5 下调，全部需求>供给 | **未触发** |
| **3 电力/PPA 转弱** | PJM 容量价明显<$329、PPA<$75、GEV/ETN backlog 转降 | 见下，全部反向 | **未触发（且更紧）** |
| **4 AI 变现跟不上** | 大额合同取消 / backlog 转降 / 下调 GPU 年限或减值 | GOOG backlog 涨到 $514B；MSFT 延长（非缩短）年限 | **未触发** |
| **5 聪明钱与结构转向** | 13F 集体撤离 / 篮子破 200DMA / **CRWV·数据中心债利差走阔** | **债市分项已触发**，13F 未到 | **⚠️ 部分触发** |
| **2 GPU 租赁价** | 1年期连跌 3 月且<$2/hr | **本次未查** | 未知 |
| **附 一票否决** | neocloud 违约 / 再融资失败 | 未发生（但在逼近） | **未触发** |

### 3.1 电力层（信号 3）——全部反向，瓶颈比论文写的时候**更紧**

- **PJM 2027/28 容量拍卖**：出清 **$333.44/MW-day**，**再次触到价格上限**，比 26/27 的 $329.17 **还高 1.3%**。
  更硬的一点：只买到 134,479 MW，**比可靠性需求少 6,623 MW**——供给缺口是实打实的。
  数据中心贡献了 27/28 年负荷预测增量约 5,250MW 中的约 5,100MW。
  → 触发条件是「明显低于 $329」→ **完全反向，未触发**。
- **PPA 价格**：LevelTen Q1 2026 指数，全国均价太阳能 **$64.49/MWh**（同比 **+13%**）、风电 **$79.40/MWh**（同比 **+24%**），**双双创该指数历史新高**。文章特别点名 **PJM 和 MISO 是太阳能 PPA 涨幅最大的区域之一**。分析师预期高位再持续「一到两年」。
  → 触发条件是「长期 PPA **跌破** ~$75」；实际是**创新高且在涨**→ **未触发**。
  **数据缺口（诚实标注）**：我只找到 **Q1 2026** 的 LevelTen 印数，**没找到论文引用的「PJM West 10 年期太阳能 PPA >$90/MWh」的 Q2 2026 更新值**。方向明确向上，但该具体序列的最新点位未验证。
- **ETN Q2 2026（2026-07-30）**：营收 **$8.5B 创纪录 +21%**，**数据中心订单 +240%**，backlog **同比 +103%**，book-to-bill 1.2，**上调全年指引**。估算全美在建数据中心 32GW（约 70% 与 AI 相关）。
- **GEV Q2 2026**：backlog **$176B**，订单 $24.2B（有机 **+88%**），电气化订单 **+66%**，**年内数据中心订单已超 $5B，是 2025 全年的 2 倍多**；燃气轮机产能爬坡到 2026Q3 的 20GW。
  → 两家的 backlog 都在**环比上升**，触发条件是「转降」→ **未触发**。

### 3.2 ⚠️ 意外信号：neocloud 债市开始定价违约（信号 5 部分触发）

这是本次核查唯一的坏消息，且**不是我原本要找的东西**。

- **2026-07-29**：**CoreWeave 5 年期 CDS 报约 855bp，按常用模型隐含约 50% 的 5 年违约概率**。本月保护成本上涨超 50%，创去年 12 月以来最高。当日 **CRWV -9%、NBIS -10%**。
- 近一个月：**CRWV -36%、NBIS -43%**。
- CoreWeave 正在**为一笔 $2.6B 贷款加价（sweeten terms）以安抚债权人**；2026 年内还有 **$4.2B 本金到期**。
- 行业层面存在 **2026–2028 年的「再融资墙」**：CRWV / NBIS / Lambda / Crusoe / APLD 的 GPU 抵押贷款集中到期。
- Bloomberg 2026-07-29 已把这写成主题：《Wall Street Picks AI Winners and Losers as Credit Swaps Surge》。
- 对冲性事实：**NVDA 据报（WSJ，约 7/27）正在洽谈为 OpenAI 的俄亥俄 10GW 园区提供 $250B 融资担保**，消息一出 neocloud 股票反弹。circular financing 的强度在加大——**这既是托底，也让论文第 4 节担心的「循环融资」问题更严重**。

**对照预注册条款**：
- 信号 5 第三条触发器写的是「**CRWV/Oracle/数据中心 ABS 利差显著走阔（债市先于股市定价 capex 融资压力）→ 跟随减仓**」→ **这一条按字面已经触发**。
- 「一票否决」写的是「某 neocloud **债务违约 / 再融资失败**」→ **尚未发生**。CRWV 仍能融到钱，只是**变贵了**。所以**不构成主题级 kill**。
- 缓冲事实：**H6 v1 组合本来就明确规避 neocloud 层**（论文原文把 CRWV/NBIS 列入「刻意规避的第一层拥挤」）。直接持仓敞口 = **0**。
- 但传导风险真实存在：neocloud 是数据中心建设需求的一部分，融资断裂会反向打到电力/电气层的订单。这正是信号 5 存在的理由。

---

## 4. 机械判定

### 入场门（HYPOTHESES.md L104）

| 项 | 值 |
|---|---|
| 已发布家数 | **5/5**（MSFT、GOOG、META、AMZN、ORCL） |
| 待发布 | **无** |
| 下调家数 | **0** |
| 上调家数 | **3**（GOOG、AMZN、ORCL） |
| 持平家数 | **2**（MSFT 实质持平+FY27 增长；META 下限抬高） |
| 门槛 | ≥2 家下调 → 不入场 |
| **判定** | **PASS —— sleeve 可按预注册规则上线** |

判定是**完整的**，不存在「当前可判部分 / 还差什么」——五家全部已发布，无缺口。

### 但有一个预注册没覆盖的情况，需要用户决策

预注册规则把**入场门**（信号 1）和**减仓触发器**（信号 2-5）当成两套先后使用的东西，**没有写明「入场当天就已经有一个减仓信号亮着」该怎么办**。

现在的事实状态是：
- 入场门（信号 1）：**干净通过**，而且是强通过（$732B、三家上调、四家 CEO 都说需求 > 供给）。
- 减仓信号 5 的债市分项：**已经亮了**。
- 减仓信号 5 的 13F 分项：**2026-08-14 才揭晓**（SA 是否平掉电力/内存多头、Coatue 是否继续减）。

三个可选处理方式（**这是用户的决策，不是本文档的建议**）：
1. **按字面执行**：入场门 PASS → sleeve 全额上线（20–25%）。信号 5 的减仓条款留待上线后正常触发。
2. **等 8-14 的 13F**：信号 5 的另一半两周后揭晓，等两周补齐再定规模。代价=两周时间，收益=信号 5 完整可判。
3. **减半上线**：按信号 5 已触发的字面后果（「跟随减仓」）折半执行，13F 出来后再定去留。

**不建议的做法**：因为看到 CDS 消息就否掉入场门。入场门是预注册的、条件明确的、且**干净通过**了；用一个事后看到的、不在入场门里的信号去推翻它，正是预注册机制要防的那种自由裁量。

---

## 5. 下一个检查点

| 日期 | 事项 | 关联信号 |
|---|---|---|
| **2026-08-14** | **Q2 13F 披露**——SA 是否平掉电力/内存多头或回补芯片 put；Coatue 是否继续减 | 信号 5（另一半） |
| 持续 | CRWV CDS / $4.2B 本金到期兑付 / 再融资是否成功 | 一票否决 |
| 未查 | GPU 1 年期租赁合约价（是否连跌 3 月且破 $2/hr） | **信号 2（本次未核查，建议补）** |
| 下季 | MSFT/GOOG/META/AMZN Q3 财报（10 月底） | 信号 1 |
| 待定 | LevelTen Q2 2026 PPA 指数、PJM West 10 年期报价 | 信号 3（本次只拿到 Q1 印数） |

---

## 6. 来源

**财报**
- Microsoft FQ4 2026（2026-07-29）：[CNBC](https://www.cnbc.com/2026/07/29/microsoft-msft-q4-earnings-report-2026.html)、[Microsoft IR](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)、[Investing.com 财报电话会记录](https://www.investing.com/news/transcripts/earnings-call-transcript-microsoft-q4-2026-beats-forecasts-stock-jumps-8-93CH-4822020)、[Directions on Microsoft](https://www.directionsonmicrosoft.com/microsoft-expect-capacity-constraints-capex-acceleration-to-continue/)
- Alphabet Q2 2026（2026-07-22）：[CNBC](https://www.cnbc.com/2026/07/22/google-earnings-q2-goog-live-updates.html)、[Seeking Alpha](https://seekingalpha.com/news/4617114-alphabet-signals-195b-205b-2026-capex-while-expanding-third-party-capacity-as-a-bridge)、[Alphabet IR](https://abc.xyz/investor/events/event-details/2026/2026-Q2-Earnings-Call-2026-GgTAq7Is0z/default.aspx)、[Pichai 致投资者](https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2026/)
- Meta Q2 2026（2026-07-29）：[Meta 新闻稿](https://www.prnewswire.com/news-releases/meta-reports-second-quarter-2026-results-302838214.html)、[CNBC](https://www.cnbc.com/2026/07/29/meta-q2-earnings-report-2026.html)、[Seeking Alpha](https://seekingalpha.com/news/4621106-meta-expects-q3-2026-revenue-of-61b-64b-while-narrowing-2026-capex-to-130b-145b)、[Q2 电话会记录 PDF](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q2/META-Q2-2026-Earnings-Call-Transcript.pdf)
- Amazon Q2 2026（2026-07-30）：[CNBC](https://www.cnbc.com/2026/07/30/amazon-amzn-q2-earnings-report-2026.html)、[Fortune（Jassy 原话）](https://fortune.com/2026/07/30/andy-jassy-amazon-capex-demand-aws-pga-tour/)、[MLQ](https://mlq.ai/news/amazons-aws-growth-jumps-to-37-as-jassy-raises-2026-capex-plan-to-220-billion/)、[Investing.com 幻灯片](https://www.investing.com/news/company-news/amazon-q2-2026-slides-aws-surges-37-free-cash-flow-turns-negative-93CH-4826472)
- Oracle FQ4 2026（2026-06-10）：[Oracle IR](https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/default.aspx)、[CNBC](https://www.cnbc.com/2026/06/10/oracle-orcl-q4-earnings-report-2026.html)、[MLQ](https://mlq.ai/news/oracle-reports-557b-fy2026-capex-guides-to-70b-net-outlay-in-fy2027/)

**电力层**
- PJM 2027/28 基础容量拍卖：[PJM Inside Lines](https://insidelines.pjm.com/pjm-auction-procures-134479-mw-of-generation-resources/)、[PJM 新闻稿 PDF](https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2025-releases/20251217-pjm-auction-procures-134479-mw-of-generation-resources.pdf)、[RTO Insider](https://www.rtoinsider.com/121911-pjm-capacity-auction-clears-max-price-falls-short-reliability-requirement/)
- PPA 价格：[Utility Dive / LevelTen Q1 2026 指数（2026-04-17）](https://www.utilitydive.com/news/wind-solar-ppa-prices-levelten/817780/)
- ETN Q2 2026（2026-07-30）：[Businesswire 新闻稿](https://www.businesswire.com/news/home/20260730561562/en/Eaton-Reports-Record-Second-Quarter-2026-Results-with-Strong-Organic-Growth-Accelerating-Orders-and-Backlog-and-Raises-Organic-Growth-Guidance)
- GEV Q2 2026：[GEV 8-K PDF](https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000147/gev2q2026form8-k.pdf)、[Investing.com 幻灯片](https://in.investing.com/news/company-news/ge-vernova-q2-2026-slides-backlog-hits-176b-guidance-raised-93CH-5508094)

**信用/neocloud**
- [Bloomberg 2026-07-29《Wall Street Picks AI Winners and Losers as Credit Swaps Surge》](https://www.bloomberg.com/news/articles/2026-07-29/wall-street-picks-ai-winners-and-losers-as-credit-swaps-surge)
- [CNBC 2026-07-26 更贵的公司债对 AI 建设意味着什么](https://www.cnbc.com/2026/07/26/what-more-expensive-corporate-debt-could-mean-for-the-ai-buildout.html)
- [Bloomberg 2026-07-16 CoreWeave 推销与 Anthropic/Jane Street 合同挂钩的贷款](https://www.bloomberg.com/news/articles/2026-07-16/coreweave-markets-loan-tied-to-anthropic-jane-street-contracts)
- [Investing.com CoreWeave 为 $2.6B 贷款加价](https://www.investing.com/news/stock-market-news/coreweave-said-to-sweeten-26-billion-loan-terms-amid-debt-concerns-4821421)
- [24/7 Wall St. 2026-07-29 NBIS -10% / CRWV -9%](https://247wallst.com/investing/2026/07/29/nebius-drops-10-coreweave-sinks-9-as-rising-credit-swap-costs-hit-the-ai-cloud-trade/)
- NVDA $250B 担保洽谈：[Yahoo Finance](https://finance.yahoo.com/technology/ai/articles/coreweave-nebius-gain-report-links-132711335.html)、[TipRanks 2026-07-27](https://www.tipranks.com/news/crwv-nbis-iren-why-are-neocloud-stocks-rising-in-pre-market-today-7-27-26)

> CDS 具体点位（855bp / 隐含 50%）来自二级媒体转述 Bloomberg 报道，未直接从 Bloomberg 终端核对，**点位精度按二手来源看待**；但「利差显著走阔」这一事实有 Bloomberg 和 CNBC 双重独立佐证。
