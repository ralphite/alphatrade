# RUNBOOK — 交易日操作手册（loop agent 逐轮执行）

## 盘前轮（08:00–09:25 ET，每日一次）

1. `date` 核对时间 → `git pull -q origin main`（防多端漂移）
2. `.venv/bin/python src/scan_8k.py`（隔夜 8-K 增量）→ 有队列则 subagent 评估（prompts/eval_8k_v1.md）→ 信号标记新鲜度資格 → `execute_signals.py`（影子流维护模式：只记录影子，无执行仓）
3. `.venv/bin/python src/manage_positions.py`（隔夜 gap 后的止损检查）
4. 检查 ../agentrunner/.env 是否新增 POLYGON_API_KEY → 有则触发 H8 go/no-go 流程

## 盘中轮（09:30–16:00 ET，每 30–45 分钟）

1. scan_8k 增量 → 评估 → 影子记录
2. manage_positions（止损穿越检测）
3. H6 监控（仅财报季）：hyperscaler capex 新闻扫描

## 收盘轮（16:05 ET，每日一次）

1. `.venv/bin/python src/manage_positions.py`（time-exit 触发）
2. `.venv/bin/python src/tom_sleeve.py`（TOM 换仓判定与 mark——每日必跑，换仓日自动执行）
3. `.venv/bin/python src/report.py` → journal 更新 → STATE.md 时间戳
4. `git add -A && git commit && git push origin main`
5. 重大变化 → 更新 artifact 仪表盘（保持常新）

## 周历（2026-07 下旬关键日）

- 7-13 周一：TOM sleeve 初始化（收盘轮）；影子仓 held 1/2
- 7-14 周二收盘：11 个 Day-0 影子仓 time-exit（H1 对照数据完结，记入 journal）
- 7-22 前后：MSFT/GOOG 等 Q2 财报季开启 → H6 监控启动
- 7-28：TOM 换仓前夜核对（7 月倒数第 3 交易日 = 7-29）
- 7-29：**三事叠加**——TOM 收盘换 QLD + FOMC 决议日 + 财报周
- 7 月底：H6 入场门判定（capex 指引）→ 通过则按 research/h6_portfolio_draft.md 建仓 paper sleeve

## 异常处理

- yfinance 限流/超时 → 重试 3 次后跳过该标的并记 events
- fresh_price stale → 拒绝成交记 no_fresh_price（纪律：绝不用陈旧价格成交）
- loop 中断恢复 → 读 STATE.md + 本文件 + `git log --oneline -5` 重建上下文
