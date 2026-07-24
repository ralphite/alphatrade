# STATE — 每轮唤醒先读这里

更新时间:2026-07-24 16:00 ET(周五)
当前阶段:**重启日(7-24):daily runner(launchd)已装 + 广域策略普查进行中**

## 运行架构(2026-07-21 起)

- **执行层(无人值守)**:launchd `com.alphatrade.daily` 每天 13:10 本地(≈16:10 ET)跑 src/daily_close.py:交易日检查→TOM sleeve(初始化/换仓/mark)→影子仓管理→日报→git push。独立于 Claude 会话,机器休眠唤醒后补跑。日志 logs/daily_*.log
- **研究层(Claude loop,会话内)**:策略普查→回测→判定→新策略并入 daily runner
- 教训(7-11~7-21 十日中断):in-session loop 不可作为执行层;规则型策略 + launchd 才是正解

## 组合现状

- H4c TOM 轮动:执行器就绪,**今日 16:10 ET launchd 首跑将初始化 sleeve**($30k 名义)。下个换仓窗口 7-29(收盘 QQQ→QLD)
- H6 AI 主题:10 标的装填,入场门=7 月底 hyperscaler capex 指引(MSFT/GOOG 财报周即将到来)
- H8 期权:**用户否决数据投入,归档**
- 影子仓:已全部抢救结算(13 笔归档,positions 清空)

## 进行中(2026-07-21 下午启动)

- 广域策略普查:3 agent(A 系统性/B 事件披露/C 盲区+排雷)→ research/survey/ → 合并评分矩阵 → top 3-5 立即回测
- 评分标准(用户定的唯一目标):可快速验证性(免费数据≥200样本+forward频率)> 净alpha 量级 > 不踩已证伪范式 > <$1M 容量

## 纪律红线(不变)

- 已证伪不复活:LLM读文本抢定价/小中盘高换手/日内bar级/行业轮动动量
- 新假设:预注册→历史回测(池内差分+悲观成本)→OOS→forward
- paper only;每轮 date 核对;commit 后 push
