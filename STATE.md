# STATE — 每轮唤醒先读这里

更新时间:2026-07-29 21:10 ET(周三晚,云端例行)
当前阶段:**三 sleeve 组合运行中(launchd 无人值守)+ 研究队列继续**

## ⚠️ 2026-07-29 云端例行:数据网络被封锁,kill 核查与研究均未执行

本次云端 session 的出站网络策略(egress policy)拒绝了全部行情数据主机:
`query1/query2.finance.yahoo.com`(yfinance 底层)、`stooq.com`、`data.sec.gov`/`www.sec.gov`、
`alphavantage.co`、`api.twelvedata.com`、`fred.stlouisfed.org` 全部返回代理层 403(策略拒绝,非临时故障,已按规程不重试/不绕过)。
WebFetch 工具直连 Yahoo chart API 同样 403。
**后果**:H9/H12/H4c 的 kill 条件核查(第 2 步)、研究队列推进(第 3 步)本次均无法执行——不是"没触发",而是"没能核查"。三 sleeve 持仓与本地执行层健康检查(读 git log / ledger,均为本地文件,不需要网络)仍正常完成,见下方日报。
**需要人工处理**:若要让云端例行继续覆盖第 2/3 步,需要在环境的出站策略里放行至少一个行情数据源(stooq.com 最轻量);否则这两步只能继续由本地 launchd 执行层(有网络)承担,云端例行退化为"仅健康检查+持仓播报"。

## 组合(paper $100k)

| Sleeve | 规模 | 状态 | 规则 |
|---|---|---|---|
| TOM(H4c) | $29k | 轮动暂停,恒 QQQ+窗口影子 | 效应死于 regime,影子 12 月转正才复活 |
| IEF 月末(H9) | $20k | 现金,**7-27 首笔买入** | 月末倒数第 5 交易日收盘买,月末收盘卖 |
| VIX carry(H12) | $10k | **在场 SVXY 175sh@56.83** | 昨收 VIX<VIX3M 持有,倒挂即离场 |
| 现金/名义 | ~$41k | — | 待新 sleeve |

执行层:launchd com.alphatrade.daily 每日 13:10 本地(明天首次自动触发验证)。
H6 主题 sleeve($25k 拟)待下周 hyperscaler capex 门。

## 判定累计(14 个假设)

存活:H9(IEF 月末)、H12(VIX carry)、H6(待门)。暂停:H4c。
已杀:H1×3、H2、H5、H7、H4a、H4b、H8(用户否决)、H10(insider 9.0 分头名,n=2110 显著为负)、H11(CEF 单 regime)、C3/C4。

## 方法论(强制)

- 三段分解(2016-19/2020-23/2024-26)——"2020-23 假效应"已杀 3 候选
- 池内差分;悲观成本;预注册 kill;极端日审计(尾部类策略)
- 评分=排队顺序,数据=判决

## 研究队列

1. 宏观公告日日历(FOMC 已有日期;NFP=首周五规则;CPI 需查日程)
2. 13D 跟随(7.0)
3. 普查 A/B/C 报告中未测的长尾候选复查

## 下周日程

7-27(一):H9 首笔买入(launchd)|7-28/29:MSFT/GOOG 财报窗口开启(H6 门)|7-29:FOMC+TOM 影子窗口|7-31:H9 平仓|8-01:NFP
