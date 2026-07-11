# H2 数据源调研：earnings call transcript 语气/guidance 变化分析

> 假设 H2：earnings call transcript 的语气/guidance 变化 vs 盘后价格反应。
> 调研日期：2026-07-10。预算约束：< $100/月。最小验证规模：每天 5–20 个财报的 transcript + 分析师预期数据。
> 关联：分析师预期（consensus EPS/revenue）同时是 SUE-PEAD（见 H4a）的先决数据。

---

## 0. TL;DR

- **推荐组合（forward 采集）**：`EarningsCall Premium ($69/mo) + FMP Starter ($22/mo)` = **$91/月**。EarningsCall 提供财报电话会结束后 ~15 分钟的 transcript（S&P 500 + 部分国际），FMP Starter 提供 forward consensus EPS/revenue 估计 + earnings calendar + 价格。两者都在 20/min~300/min 速率内，轻松覆盖每天 20 个财报。
- **$0 预检（先跑回测再花钱）**：`defeatbeta-api（免费 transcript 历史）+ finnhub 免费 earnings-surprise 端点（历史 actual vs consensus EPS）`。用来在花钱前确认「语气/guidance 信号是否存在」，缺点是非实时、覆盖/时效不保证。
- **最大局限**：便宜源的覆盖都偏向大盘（S&P 500 / 大中盘），小盘缺失严重（而 PEAD/语气效应往往在小盘最强）；且没有任何低价源能给「会中/结束即刻」的 in-call transcript——最快也要会后 ~15 分钟，若 H2 的 edge 在盘后前 15 分钟就被定价掉，低价方案抓不住。

---

## 1. 免费/低价 transcript 源（2026 现状）

| 源 | 覆盖范围 | 历史 | 时效（会后多快可得） | 价格 | API 限制 / 备注 |
|---|---|---|---|---|---|
| **EarningsCall** (earningscall.biz / `earningscall-python`) | 5,000+ 公司、55,000+ 场；S&P 500 + 加/欧/澳国际 | 多数公司回溯到 **2020** | **~15 分钟**（明确承诺；Ultimate+ 档带 real-time notification） | Starter $60 · Premium $69 · Ultimate $129 · Ultimate+ $155（年付 -20%）。**免费层仅 AAPL+MSFT 两家** | 速率：Starter 10/min、Premium 20/min、Ultimate 50/min、Ultimate+ 250/min。Python & JS SDK，无年度锁定。**近实时首选，性价比最高** |
| **API Ninjas** Earnings Call Transcript API | 广（按 ticker/CIK/date 查询，含 speaker 检索） | **Developer 档=近 5 年**；Business/Professional=**2005 起全量** | 会后 **数小时** | Developer $39 · Business $99 · Professional $199（均含商用授权，零数据保留）。免费层对 premium 端点有限、**无 SLA** | Developer 100k calls/mo、Business 1M、Professional 10M。免费层不适合生产。**Developer 档预算内但时效弱于 EarningsCall** |
| **FMP** (Financial Modeling Prep) transcript | 8,000+ 美股 + 有美国业务的国际公司 | 10+ 年 | 号称 real-time（实际会后小时级） | **transcript 被锁在 Ultimate $149/mo**（超预算）。Starter $22 / Premium $59 不含 transcript | 速率 Starter 300/min、Premium 750/min、Ultimate 3000/min；有 30 天带宽上限（Ultimate 150GB）。**transcript 端 = Ultimate，超预算；但 FMP 的价值在于 estimates（见 §3），不建议为 transcript 上 Ultimate** |
| **defeatbeta-api**（开源） | 美股大/中盘为主 | 有历史（HuggingFace 数据集） | **非实时**（社区/HF 批量更新，滞后不定） | **完全免费、无 rate limit** | Python-native、DuckDB+缓存、可 SQL；含 transcript/news/revenue breakdown，且内置 LLM 分析示例。**回测/历史 bootstrap 理想，live 采集不可靠** |
| **EarningsCall/earningscall-python**（同上 SDK） | — | — | — | — | 免费无 key = 仅 AAPL/MSFT；付费 key 解锁 5,000+ |
| **Motley Fool** | 小规模美股子集 | 有 | 常滞后 1 天+ | 免费（计入免费用户月度文章配额） | 无官方 API；有第三方 Apify scraper（提取 prepared+Q&A/参与者/ticker/季度）。ToS 灰区、无 SLA、覆盖窄 |
| **Seeking Alpha** | 广（曾是免费 transcript 先驱） | 有 | — | 现已付费墙：Premium $239/yr（~$20/mo）、Pro $2,400/yr | **无 transcript 官方 API**；抓取违反 ToS 且被激进反爬。不作为可编程源 |
| **Quartr**（企业向，参考） | 广、国际强 | 有 | 会后短时；2025-04 起含 speaker ID | 偏企业定价（不便宜） | 提到 webhook 推送；预算内不主推 |

**要点**
- **近实时最佳性价比 = EarningsCall**：15 分钟 SLA、Python SDK、$60–69/mo 覆盖 S&P 500 + 国际，速率足够每天 20 场。
- **FMP 的 transcript 不划算**：被单独锁进 Ultimate $149，超预算；FMP 应只买它的 estimates（Starter $22）。
- **免费真源只有两条**：defeatbeta（历史、非实时）与 EarningsCall 免费层（仅 AAPL/MSFT）。前者适合先跑回测证伪。

---

## 2. 实时性关键问题

### 2.1 transcript 会后多快可得
- **near-live（分钟级）**：EarningsCall 承诺 **会后 ~15 分钟**；earningscalls.dev 宣称「分钟级」、Enterprise 档有 webhook（零轮询）。
- **小时级**：API Ninjas「数小时」、FMP「real-time」实测小时级、Quartr 会后短时（含 speaker ID）。
- **无低价源提供「会中/结束即刻」的 in-call live transcript**——真正 live 只在 Quartr/企业级或自建方案里。
- **对 H2 的含义**：H2 要把「语气/guidance 变化」对齐「盘后价格反应」。15 分钟延迟对「盘后/次日漂移」窗口足够；但若 edge 集中在盘后前几分钟（call 一结束价格就跳），15 分钟已错过——这是低价方案对 H2 的核心时效风险，需在验证时明确测量「延迟敏感度」。

### 2.2 自建 audio-to-text（Whisper + 公司 IR 直播）可行性与成本
- **ASR 成本极低、非瓶颈**：Whisper large-v3（~3GB VRAM，Apache-2.0）；faster-whisper 在 L40S 上 ~25–30x 实时，large-v3 turbo 更快。自托管 GPU 转录 100 小时音频 spot 价 ~$1–2；OpenAI Whisper API $0.006/min（≈$0.36/hr）。按每天 5–20 场 × ~1hr = 150–600 hr/mo：OpenAI API 约 **$54–216/mo**，自托管算力可忽略但 +DevOps ~$276/mo（隐性）。
- **真正的难点是音频获取编排，不是转录**：每家 IR webcast 平台不同（Q4、Notified/Nasdaq、Zoom、电话拨入），播放器/URL 各异，部分需注册、部分仅电话音频；对每天 5–20 路不同的 live 流做稳定实时抓取 = 高工程量且脆弱。
- **结论**：为 H2 最小验证 **不值得自建**。EarningsCall $69/mo 已给 15 分钟文本。自建只在需要 <15 分钟/in-call 延迟、或需覆盖 API 缺失的小盘时才考虑（属 H2 立项后、要抢盘后前几分钟 edge 时的升级项）。

---

## 3. 配套数据：分析师预期（consensus EPS/revenue）低价源

> H2（guidance vs 预期）与 SUE-PEAD 都需要 consensus。核心区分：**forward 预测**（未来季度 consensus，H2 需要）vs **历史 surprise**（已报季度 actual vs consensus，SUE 计算需要）。

| 源 | 预期数据 | 最低可用档 & 价格 | 关键限制 |
|---|---|---|---|
| **FMP** | forward consensus EPS/revenue（Financial Estimates API）、price target consensus、ratings、earnings calendar | **Starter $22/mo**（估计数据 partial；Premium $59 更全） | 便宜且够用；Starter 覆盖主要公司的 forward consensus，深度（分析师数/修正）较浅。**forward 预期首选低价源** |
| **finnhub** | forward EPS/revenue estimates 端点 = **premium**；但**历史 earnings-surprise（actual vs consensus EPS）在免费层**；recommendation trends 免费 | 免费层（60/min）含 earnings surprise + recommendation；forward estimates 需付费（~$50/mo 起的 premium）。免费=个人/非商用 | **免费 earnings-surprise 端点 = SUE 历史回测的 $0 consensus 来源**（报告时点的 consensus EPS）。forward 深度估计需付费 |
| **Alpha Vantage** | earnings（actual vs estimate）、earnings calendar；estimates 数据有限 | 免费 5/min·25/day（太低）；Standard $49.99(75/min)、Premium $99.99(150)、Professional $149.99(300)、Enterprise $249.99(1200) | 免费 25/day 撑不住每天 5–20 财报 + 估计；付费才可用但比 FMP 贵、estimates 粒度弱。**不作预期首选** |

**要点**
- **forward consensus（H2 需要）**：`FMP Starter $22/mo` 最划算。
- **历史 consensus for SUE（SUE-PEAD 需要）**：`finnhub 免费 earnings-surprise` 端点可 $0 拿到报告时点 consensus EPS——回测阶段先用它证伪，省钱。
- Alpha Vantage 免费额度对本用例太低，付费又不如 FMP，略过。

---

## 4. 推荐组合（< $100/月）

### 推荐 A —— forward 采集主力（近实时）：**$91/月**
```
EarningsCall Premium  $69/mo   # transcript，会后~15min，S&P500+国际，20/min，含 speaker/section 便于抽 guidance
FMP Starter           $22/mo   # forward consensus EPS/revenue + earnings calendar + 价格
```
- 覆盖每天 20 个财报绰绰有余；15 分钟时效足以关联盘后/次日反应。
- 若只需 transcript 原始文本（不需 speaker 分段），可降到 EarningsCall Starter $60 → 组合 **$82/mo**。

### 推荐 B —— 更省、留 headroom（时效弱）：**$61/月**
```
API Ninjas Developer  $39/mo   # transcript，近5年，会后数小时，100k calls
FMP Starter           $22/mo   # forward consensus + calendar
```
- 便宜且预算内富余 $39，但 transcript 会后「数小时」——若 H2 edge 在盘后早段则抓不住。

### 推荐 C —— $0 预检（先证伪再花钱）：**$0–22/月**
```
defeatbeta-api        免费      # 历史 transcript（非实时），跑「语气/guidance 信号是否存在」的回测
finnhub 免费          $0       # 历史 earnings-surprise = 报告时点 consensus EPS（SUE 回测）
(+ FMP Starter $22 仅当需要 forward consensus 做样本)
```
- 花钱前用它确认信号存在性；确认后再上 A 做 forward paper。

**建议路径**：先 C（$0 回测证伪）→ 信号存活再上 A（$91/mo forward 采集）。

### 最大局限
1. **覆盖偏大盘**：EarningsCall/API Ninjas/FMP 便宜档都以 S&P 500 / 大中盘为主，小盘 transcript 缺失严重——而 PEAD/语气效应经验上在小盘最强，最小验证会系统性漏掉最肥的样本。
2. **无低价 in-call live transcript**：最快 ~15 分钟（EarningsCall），API Ninjas/FMP 更慢。若 H2 的 alpha 在 call 结束后前几分钟就被盘后定价掉，所有低价方案都抓不到；抢这段只能自建 Whisper+webcast（高工程量）或上企业级（超预算）。
3. **consensus 深度浅**：低价源的分析师数量/修正历史远不如 Refinitiv/FactSet，consensus 可能有偏、修正时点不精确，会给 H2/SUE 的「预期基准」引入噪声。

---

## 附：来源
- FMP transcript & pricing: https://site.financialmodelingprep.com/datasets/earnings-call-transcripts ; https://www.findmymoat.com/tools/financial-modeling-prep-fmp ; https://site.financialmodelingprep.com/developer/docs/stable/financial-estimates
- API Ninjas: https://api-ninjas.com/api/earningscalltranscript ; https://api-ninjas.com/pricing
- EarningsCall: https://earningscall.biz/ ; https://earningscall.biz/api-pricing ; https://github.com/EarningsCall/earningscall-python
- defeatbeta-api: https://github.com/defeat-beta/defeatbeta-api ; https://medium.com/@bwzheng2010/introducing-defeatbeta-api-311913e8e8e2
- finnhub: https://finnhub.io/pricing ; https://finnhub.io/docs/api/company-eps-estimates
- Alpha Vantage: https://www.alphavantage.co/premium/ ; https://getpulsesignal.com/pricing/alphavantage
- Motley Fool / Seeking Alpha: https://www.fool.com/earnings-call-transcripts/ ; https://about.seekingalpha.com/transcripts ; https://www.koyfin.com/blog/top-earnings-call-transcripts-platforms/
- Whisper 自建: https://www.assemblyai.com/blog/self-hosting-whisper ; https://brasstranscripts.com/blog/openai-whisper-api-pricing-2025-self-hosted-vs-managed ; https://blog.salad.com/whisper-large-v3/
