# STATE — loop agent 每轮唤醒先读这里

更新时间：2026-07-10 20:45 ET（周五晚）
当前阶段：**组合成形期：H4c forward（执行器就位）+ H6 待入场门（7月底 capex 指引）+ 研究线继续**

## 今日终局（Day 0 完整战绩）

- 管线从零建成 + 红队修复 9 项（P0×3+P1×6）+ H0 校准通过
- **H1 v1 KILLED**：两窗口 402 样本，conviction 层无池内差分优势；机制=次日开盘入场吃 fade
- **H1c KILLED**：盘后 30min 入场 n=20，gap 捕获 -305bps (t=-3.0)；定价在盘后 30min 内完成
- **H1b KILLED**：做空叙事型 long 信号 n=39 含止损+borrow，-183bps (t=-2.6)，67% 被路径波动止损打掉
- **H5 OOS 否决**：5.02 漂移是窗口 2 单窗噪声（OOS -7bps）
- 机制遗产：(1) 8-K alpha 在盘后 30min 释放完毕 (2) 定价系统性过冲 (3) 过冲因路径波动+成本不可交易
- 历史数据资产：4 个窗口 714 条 filing 队列（含全文缓存）、459 条 LLM 盲评、495 条 outcome 模拟
- forward 影子流降级为最小维护：仅盘前一轮扫描+评估+影子记录；现有 11 个影子仓周二（7-14）收盘退出，周一/周二需跑 manage_positions

## 下一步优先级

1. **H4 筛选（周末主线）**：agent 正在产出 research/h4_candidates.md（经典小容量异象清单）→ 逐个日线回测（无 LLM lookahead 问题，迭代最快）→ 存活者预注册 → 下周 forward
2. H2（transcript 长尺度）：仅设计，不急跑
3. 周末杂务：report.py 补 shadow 平仓统计；fetch_filing_text EX-99 优先级（DRI 案例）；周一盘前恢复最小 forward 流
4. 记忆维护：把今天的机制知识存入长期记忆

## 纪律红线（不变）

- H1 家族不得复活（三方向证伪）；eval_8k_v1 冻结
- 新假设：先登记（edge/对手盘/kill criteria）→ 历史回测（池内差分+悲观成本）→ OOS 窗口 → 才 forward
- 一切判定预注册；in-sample 归纳必须 OOS 验证（H5 教训）
- paper only；每轮 `date` 核对时间；commit 后 push origin main

## 市场时间

- 周末（7-11/12）市场关闭 = 纯研究窗口
- 下一交易日 7-13 周一：盘前 08:00 ET 最小 forward 流 + 影子仓 manage
- 7-14 周二收盘：11 个影子仓 time-exit

## 周末队列（2026-07-11/12）

- [x] H4c 执行器 tom_sleeve.py（日历已验证：7-29 收盘 QQQ→QLD，8-04 收盘回）——周一收盘轮初始化 sleeve 并纳入日常流程
- [ ] EOD reversal 回测（30min bar，60 天窗口）——下一轮
- [ ] FOMC 漂移（需准确 2020-26 FOMC 日历，agent 查证后回测）
- [ ] H6：7 月底 Q2 财报季监控清单（MSFT/GOOG/AMZN/META capex 指引日期）
- [x] report.py shadow 平仓统计修复
- [ ] fetch_filing_text EX-99 优先级修复（低优先）
- 周一 08:00 ET 起：最小 forward 流恢复 + 影子仓 manage；周二收盘 11 个影子仓退出
