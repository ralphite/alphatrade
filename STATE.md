# STATE — loop agent 每轮唤醒先读这里

更新时间：2026-07-10 01:45 PDT（04:45 ET）
当前阶段：H1 关卡 2（forward paper trading）Day 0 启动日

## 已完成

- [x] 章程 PROJECT.md、假设登记 HYPOTHESES.md（H0 校准 + H1 8-K 事件驱动，含预注册 kill criteria）
- [x] 环境 .venv（python3.9 + pandas + yfinance 1.2.0）
- [x] src/：data.py(价格) edgar.py(8-K) ledger.py(paper账本+成本模型) scan_8k.py execute_signals.py manage_positions.py report.py backtest_h0.py
- [x] H0 校准回测通过：QQQ 隔夜+6.4%/日内-14.3%/BH+234.6%（2020-26, 净），算术自洽，成本模型生效
- [x] 首次 8-K 扫描已启动（2026-07-09..10 窗口）

## 运行手册（每轮唤醒照此执行）

1. `cat STATE.md`（本文件）；`.venv/bin/python src/ledger.py` 看账本
2. **盘前轮（~05:45 PDT / 08:45 ET）**：跑 `src/scan_8k.py`（默认昨今窗口）→ 读 queue/pending_*.json → 按 prompts/eval_8k_v1.md 逐条评估（可 spawn subagents 并行）→ 信号写 `signals/<ET日期>/signals.jsonl`（每行含 signal_id/ticker/direction/conviction/thesis/staleness_check/priced_in_check/eval_prompt=eval_8k_v1）
3. **开盘后（>=06:35 PDT）**：`src/execute_signals.py signals/<date>/signals.jsonl` 开仓；`src/manage_positions.py` 管理持仓
4. **盘中轮（每 45-60 分钟）**：scan_8k（增量，seen 自动去重）→ 评估新 filing → execute → manage
5. **收盘轮（~13:05 PDT / 16:05 ET）**：manage（触发 time-exit）→ `src/report.py` → 更新本文件与 journal/<date>.md → git commit
6. **盘后/周末**：只做研究改进（不动 forward 流程的 prompt/参数！），或写日报

## 纪律红线（详见 PROJECT.md / HYPOTHESES.md）

- eval_8k_v1 prompt 运行期内不可改；改 = 计数清零存 v2
- 只有 direction=long & conviction=3 执行；conviction<=2 是影子信号，必须照记
- paper only，绝不接真实账户/真钱
- 每轮结束前必须：更新 STATE.md 更新时间戳 + ScheduleWakeup 下一轮

## 市场时间备忘（机器本地 = PDT = ET-3）

- 开盘 06:30 PDT / 09:30 ET；收盘 13:00 PDT / 16:00 ET
- 今天 2026-07-10 周五。下一交易日 2026-07-13 周一。

## 下一步（本轮待办）

- [ ] 等 scan 完成 → 评估队列 → 写 signals/2026-07-10/signals.jsonl（盘前评估，开盘执行）
- [ ] git 首次 commit
- [ ] ScheduleWakeup 到 ~05:45 PDT 盘前轮
