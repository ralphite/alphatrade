# STATE — loop agent 每轮唤醒先读这里

更新时间：2026-07-10 13:40 ET（盘中）
当前阶段：H1 关卡 2（forward paper）Day 0 warmup 运行中；红队修复已完成并 commit

## 关键事实

- **Day-0（今天）全部信号 = warmup，不计正式样本**（凌晨批次受文本 bug + 时间戳缺失影响；且流程延误至开盘后 4h，盘前信号已过期）。
- 12 个 warmup 影子仓已开（13:35 ET）：5 conv2-long（BNED/AP/FBRX/NRIX/MARA）+ WDFC(3-vetoed-long) + 6 would-short(BYRN/PCSC/RIVN/CABO/FRMI/IONS)。退出 T+2 close（→ 7-14 周二收盘）或 ±4% stop。执行仓 0 个。
- **WDFC 案例（重要认知）**：8-K 盘后 16:09 发布 → 次日开盘 +22% gap → 盘中 fade -9%。明显的大 beat 没有"开盘买 drift"的肉；LLM 评估者在无实时涨跌数据时对 priced-in 的判断不可靠（已修复：queue 现带 chg_since_event_pct）。H1 的真机会假说调整方向：更模糊/更小/被忽视的事件。
- 红队 8 条 P0/P1 全部修复（excess 指标、章程滑点、shadow 账本、fresh-price 守卫、盘中 low 止损、事件前 ADV、accepted 分钟级时间戳、无正文跳过）。推进门收紧：n≥150 且 excess t≥2。

## 运行手册（每轮唤醒照此执行）

1. `cat STATE.md`；`.venv/bin/python src/ledger.py`（账本，一切看 excess）
2. **盘中轮（09:30–16:00 ET，每 45–60min）**：`src/scan_8k.py`（增量）→ 若有新队列：评估（subagent 批量，prompts/eval_8k_v1.md）→ conv3 过 red-team argue → `src/execute_signals.py signals/<ET日期>/signals.jsonl` → `src/manage_positions.py`
3. **收盘轮（16:05 ET）**：manage（time-exit）→ `src/report.py` → journal → STATE.md → git commit
4. **盘前轮（08:00–09:25 ET）**：scan 隔夜 8-K → 评估 → red-team → 开盘后 09:35 执行（信号必须 accepted 于上一收盘后，否则降 warmup/skip）
5. **盘后/周末**：研究改进（不碰 eval_8k_v1 与执行规则），周末任务清单见下

## 正式样本资格（缺一即 warmup 标记）

- accepted 时间戳存在且晚于上一交易日 16:00 ET
- 评估时 queue 带 chg_since_event_pct（priced-in 判断有数据依据）
- 信号产生后 30 分钟内以 fresh_price 成交

## 纪律红线

- eval_8k_v1 运行期内不可改；改 = 计数清零存 v2
- conv3 必须过 red-team（独立反驳 agent 或硬数据仲裁），veto 记 3-vetoed 影子
- 所有非 skip 信号（含 would-short）都开影子仓——conviction 单调性与 short 侧是核心自查
- paper only；指标以 excess（对 SPY）为准
- 每轮结束：更新本文件时间戳 + ScheduleWakeup（校准与 date 命令核对真实时间！今晨教训：假设的时间与真实时间差 4h）

## 市场时间

- 今天 2026-07-10 周五。收盘 16:00 ET。下一交易日 7-13 周一。
- warmup 影子仓 time-exit 到期：7-14 周二收盘。

## 环境备忘（2026-07-10 用户指示）

- remote = https://github.com/ralphite/alphatrade，工作流始终用 origin/main：**每次收盘轮 commit 后 push origin main**
- ../agentrunner/.env 可复用：含 GEMINI_API_KEY（Google Gemini）。用途候选：red-team 关的跨模型第二意见、评估者一致性实验（周末研究项）。不改 eval_8k_v1 主流程。

## 本轮待办

- [ ] 盘中增量 scan 结果 → 评估 → 可能的首批正式信号（若 accepted 今天 09:30 后）
- [ ] 15:50 ET 前最后一轮盘中检查；16:05 ET 收盘轮（report/journal/commit）
- [ ] 周末：H2 候选调研（earnings calendar 源、transcript 源）、无正文 filing 统计、conviction 校准分析
