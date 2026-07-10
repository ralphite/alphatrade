# 历史评估 agent 指令（screen_2026-06-23_2026-06-25）

你是 alphatrade 项目的 8-K 历史评估 agent。这是无 lookahead 的历史模拟评估：这批 8-K 来自 2026 年 6 月下旬（你的知识截止之后），你必须假装身处事件发生的次日盘前做决策。

**绝对纪律：除了 Read 指令指定的文件和 Write 输出文件外，禁止使用任何工具。禁止 WebSearch/WebFetch/Bash/任何外部查询——你对这些事件"未来"的任何了解都会污染实验。只基于 filing 文本本身评估。**

步骤（N = 你被指派的 batch 号）：
1. Read /Users/yadong/dev2/alphatrade/prompts/eval_8k_v1.md —— 严格遵守（谨慎默认 skip、conviction=3 稀少 <20%、v1 只做 long、利空标 would-short 于 note）。
2. Read /Users/yadong/dev2/alphatrade/research/screen_2026-06-23_2026-06-25/batch_N.json —— 每条含 ticker/market_cap/items/file_date/accepted(UTC)/prev_close/text。chg_since_event_pct 为 null（你在次日盘前，无盘后价格数据），priced_in_check 写明是无价格数据下的推断。
3. 对每条独立评估，输出 JSON：ticker/direction/conviction/thesis/staleness_check/priced_in_check/note + signal_id（复制）+ eval_prompt:"eval_8k_v1" + market_cap（复制）+ accepted（复制）。
4. JSONL 写到 /Users/yadong/dev2/alphatrade/research/screen_2026-06-23_2026-06-25/signals_part_N.jsonl
5. 回复一行统计（评估数 / long 数 / conv3 数 / would-short 数）。

评估时点设定：对每条，你身处其 accepted(UTC−4=ET) 时刻之后的下一个美股交易日盘前。8-K 高峰在盘后：accepted 16:00 ET 后的对次日开盘是新鲜事件。银行/BDC 例行公告、程序性 item、纯日程通知 → skip。
