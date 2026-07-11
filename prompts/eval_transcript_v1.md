# eval_transcript_v1 — earnings call transcript 评估 prompt（版本 1，2026-07-10 预注册）

> 纪律：H2 预检与 forward 共用本 prompt。运行期不得修改；改 = v2 + 计数清零。

## 假设背景（评估者须知）

H2 假设：transcript 中管理层的 guidance 行为与语气，预测财报后 **数周**（T+2 至 T+22 交易日）的漂移——不是预测盘后即时反应（那已被 H1 证伪且被市场秒级定价）。你要找的是「慢变量」：市场读 headline 数字很快，但消化管理层措辞的微妙含义很慢。

## 输入

- ticker、公司名、财报所属 fiscal quarter、report_date
- transcript 全文（prepared remarks + Q&A）

## 评估指令

只基于 transcript 文本（禁止使用任何外部知识/后续走势记忆——若你认出这家公司并记得其后来的股价，忽略该记忆），输出 JSON：

```json
{
  "ticker": "...",
  "guidance_action": "raise" | "maintain" | "lower" | "none_given",
  "tone": -2 | -1 | 0 | 1 | 2,
  "qa_quality": 1 | 2 | 3,
  "forward_signal": "long" | "skip",
  "thesis": "一句话：管理层在说什么市场需要几周才能消化的东西",
  "red_flags": "捕捉到的回避/对冲措辞，无则空"
}
```

定义：
- guidance_action：本次电话会中对未来指引的动作。raise=上调（明确数字或明确措辞）；maintain=重申；lower=下调；none_given=未给。
- tone：管理层整体语气。+2=罕见的强信心（具体、量化、主动给上行细节）；+1=偏正面；0=中性/程序化；-1=谨慎防御；-2=明显回避/警告。校准：多数电话会应落在 -1..+1，±2 应稀少（<15%）。
- qa_quality：Q&A 环节质量。3=直接、量化、不回避尖锐问题；2=普通；1=回避、模糊、拒答多。
- forward_signal：**long 仅当 guidance_action=raise 且 tone>=+1 且 qa_quality>=2**（规则固定，不许自由裁量）；否则 skip。
