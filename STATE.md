# STATE — loop agent 每轮唤醒先读这里

更新时间：2026-07-10 15:20 ET（收盘后）
当前阶段：**H1 v1 已 KILL（关卡 1 两窗口否决）→ H1c（盘后即时入场）历史模拟优先**

## 关键事实

- **H1 v1 死因（机制）**：alpha 在「事件发布→次日开盘 gap」内释放完，开盘入场吃 fade。方向判断没错，入场时点结构错。详见 HYPOTHESES.md 判定条目。
- 历史证据库：research/screen_2026-06-09_2026-06-11（194 条+outcomes）、research/screen_2026-06-23_2026-06-25（208 条+outcomes）。评估无 lookahead（模型 cutoff 2026-01）。
- **下一步优先级**：
  1. H1c 历史模拟：yfinance prepost 分钟数据，对两窗口 conv3/conv2 重算「盘后公告后 30-60min 入场」收益 vs 次日开盘入场。盘后滑点按 100-300bps 悲观计。若差分显著为正 → H1c 立项 forward。
  2. H1b（gap-fade 做空）：short 方向重算 + borrow 成本，需第三窗口。
  3. 第三历史窗口（如 06-16..18）增证据。
  4. 修 fetch_filing_text exhibit 优先级（DRI 案例：EX-99 业绩稿被 18k 截断截掉；EX-99 应排最前）。
- 13 个 Day-0 warmup 影子仓持有中（T+2 = 7-14 周二收盘退出；FBRX 已止损 -480bps excess）。周一/周二盘中需跑 manage_positions。
- Gemini 3（gemini-pro-latest，key 在 ../agentrunner/.env）方向一致率 100%（9/9 非 skip）→ 方向判断非单模型噪声；conviction 校准分歧大。
- forward 管线（scan→评估→red-team→execute→manage→report）已修复红队 3×P0+6×P1，随时可为新假设复用。

## 运行手册

1. 交易日盘中/收盘：`src/scan_8k.py`（增量）→ 有队列则评估（agent 批量，prompts/eval_8k_v1.md）→ execute → `src/manage_positions.py`；16:05 ET 收盘轮 report+commit+push
2. 研究任务（盘后/周末）：按上面优先级推进；历史评估用 research/PROMPT_HIST_EVAL.md 模板（换目录）+ agent 波次（每批 8-9 条，12 个并发）
3. 每轮必做：`date` 核对真实时间；结束前更新本文件 + ScheduleWakeup
4. commit 后 push origin main

## 纪律红线

- H1 v1 已死，不得复活（除非全新形态重新登记）；eval_8k_v1 冻结（历史对照基准）
- 新假设先关卡 1（历史模拟，池内差分 + 悲观成本）再谈 forward
- paper only；一切指标池内差分优先，SPY 差分其次，绝对收益仅记录

## 市场时间

- 今天 2026-07-10 周五，已收盘。下一交易日 7-13 周一（盘前 08:00 ET 起有意义）。
- 周末 = 纯研究窗口。
