# alphatrade

个人投资者（<$1M，美股）用 AI agent 寻找可持续盈利方式的实验。全程 paper trading。由 Claude（loop agent）自主运营：假设生成 → 历史盲测 → 预注册判定 → forward paper → 组合化。

**实时仪表盘**：见 Claude 会话中的 artifact 链接｜**方法论**：[PROJECT.md](PROJECT.md)｜**全部假设与判定**：[HYPOTHESES.md](HYPOTHESES.md)｜**每日操作**：[RUNBOOK.md](RUNBOOK.md)

## 当前组合（三支柱 + 基准仓，$100k paper）

| Sleeve | 配置 | 状态 | 核心逻辑 |
|---|---|---|---|
| H4c TOM 轮动 | 30% | forward 运行 | 月末机械资金流：月末倒数第3交易日收盘 QQQ→QLD，次月第2交易日收盘回。六年回测 +27.7%/年 vs QQQ +20.3% |
| H6 AI 基建主题 | 25% | 装填待触发 | 电力/输配电/封装层 10 标的（非芯片层）。入场门：7月底 hyperscaler capex 指引 |
| H8 期权 vol premium | 待定 | 等数据批准 | XSP defined-risk 卖方。验证=全历史回测+极端日审计（非 t 统计） |
| QQQ 基准仓 | 其余 | — | 未部署资金的默认位置 |

## 关键实证结论（2026-07-10/11，全部预注册判定）

1. **「LLM 读公开文本→短中期交易信号」范式在十个形态上全灭**（8-K 多空×3、earnings transcript、日内模式×4、行业轮动、小盘隔夜）。市场对公开文本的定价快于且过度于一切零售入场时点。LLM 的正确角色 = 研究引擎，不是信号生成器。
2. **成本墙定理**：小中盘个股双边成本 ~69bps ≈ 可得毛 edge 的 14 倍 → 免费日线×高换手×个股 = 数学必死。
3. **池内差分是唯一可信基准**：对照池 vs SPY 的超额随窗口翻转 ±100bps；不做池内差分的回测都是自欺。
4. 幸存空间：结构性资金流（TOM ✓）、主题信念+证伪纪律（H6）、波动率风险溢价（H8）。

## 方法论骨架

- **预注册**：假设的 edge 来源/对手盘/kill criteria 先写死再测；in-sample 归纳必须过 OOS（H5/H4a 均被此拦截）
- **无 lookahead 历史盲测**：用评估模型 knowledge cutoff 之后的数据，评估 agent 禁用一切外部查询
- **成本悲观化**：滑点按市值/时段分层（15-300bps），做空加 borrow，绝不用 mid 价
- **红队关**：重大结论必过独立 adversarial agent；跨模型（Gemini）第二意见
- **全程留痕**：每个信号（含未执行）、每次判定、每个被杀死的假设都在 git 历史里

## 数据资产

约 1,500 条 8-K filing 队列（含全文）、559 条 LLM 无 lookahead 盲评（8-K 459 + transcript 100）、~74k 条含成本收益模拟、13 个影子仓 forward 对照、4 份深度研究报告（research/）。
