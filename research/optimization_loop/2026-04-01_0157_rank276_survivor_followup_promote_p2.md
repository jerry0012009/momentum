# 2026-04-01 01:57 UTC — Rank 276 survivor 唯一 follow-up：source-faithful cost ladder 通过，`promote_P2`

## 本轮执行对象
- target: `Rank 276 / BTC 15m Donchian overshoot fade × 10bps breach threshold`
- 来源：`research/optimization_loop/2026-04-01_0144_rank276_donchian_overshoot_fade_keep_p1.md`
- 运行角色：bot3 survivor 唯一 cheap decisive follow-up
- 结论：`promote_P2`

## 先做的合法性回退
当前 `cycle_plan` 的第一个 `pending` 小点原本是新的 fresh intake（`0034_cex-dex-priority-fee-delay-arb-alpha`），但 runtime 里仍存在合法且未收口的 `Surviving candidate slot = Rank 276`，这与 fixed policy 里“已有前排对象的收口优先于新的发现”冲突。

因此本轮没有沿着歪路径继续开新 intake，而是直接回退到唯一合法动作：

> 对 `Rank 276` 做那唯一一次 source-faithful reproduction follow-up，并在 `promote_P2` 与 `回 background/P0` 之间给出单一出口 verdict。

## 本轮只回答一个问题
用 repo 自带的公开 raw CSV 和完全同源的规则，重放 `BTC 15m Donchian overshoot fade × 10bps threshold`，然后直接看它在 `3 / 5 / 8 / 10 bps` 成本下是否仍留下诚实的 after-cost pocket。

## 本轮实际做了什么
### 1) 直接使用 source repo 的公开数据与精确规则
来源仓库：
- `https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW`

本轮没有自己改 spec，而是按 repo 原始结构重放：
- 数据：repo 自带 `data/raw/BTCUSDT_15m_raw.csv`，并沿 `02_data_clean.py` 的口径与 `ETH/DOGE` 对齐时间戳；
- 核心规则：
  - `N = 200`
  - `VOL_WINDOW = 50`
  - `threshold = 10 bps`
  - `max_hold = 40 bars`
  - `vol_filter = rolling_vol > in-sample 60th percentile`
  - `IS_END = 2025-12-31`
- 回测逻辑：严格照 `05_breakout_extension.py` 的 contrarian fade / opposite-signal-or-time-stop / position-diff cost 计法执行。

### 2) 生成本地 artifact
- `reports/artifacts/rank276_donchian_source_faithful_followup/rank276_source_faithful_cost_ladder_20260401.json`
- `reports/artifacts/rank276_donchian_source_faithful_followup/rank276_source_faithful_cost_ladder_20260401.csv`

## 关键结果
### 1) `5 bps` reproduction 与 repo 表格逐项对齐，不再只是 digest 转述
本地重放得到的 `5 bps` 结果与 repo `breakout_extension_comparison.csv` 的 `Test A — Threshold` 完全一致：

- IS net PnL：`3827.21 USD`
- OOS net PnL：`9872.83 USD`
- IS Sharpe：`0.4513`
- OOS Sharpe：`1.6722`
- IS/OOS trades：`50 / 35`
- IS/OOS total cost：`5000 / 3500 USD`
- IS/OOS win rate：`56.00% / 62.86%`

这一步改变系统认知的地方在于：

> `Rank 276` 现在已经不是“repo 自报 5bps 还行”的二手判断，而是我们用 source 自带 raw CSV 与同源代码逻辑亲手复现并逐项对齐的对象。

### 2) after-cost pocket 不只停在 `5 bps`，OOS 到 `8 / 10 bps` 仍为正
同一 exact spec 下，成本梯度结果如下。

#### OOS（2026-01-01 ~ 2026-02-28）
- `3 bps`：net `11272.83 USD`，Sharpe `1.9089`，`35` trades，avg net/trade `322.08 USD`
- `5 bps`：net `9872.83 USD`，Sharpe `1.6722`，`35` trades，avg net/trade `282.08 USD`
- `8 bps`：net `7772.83 USD`，Sharpe `1.3167`，`35` trades，avg net/trade `222.08 USD`
- `10 bps`：net `6372.83 USD`，Sharpe `1.0794`，`35` trades，avg net/trade `182.08 USD`

也就是说，这条线在最关键的 OOS 段里不是“刚好只在 5bps 勉强过线”，而是 **到 10bps 仍留有清晰正 pocket**。

### 3) 但 edge 也没有厚到可以直接吹成 P3
IS 更薄：
- `8 bps` 只剩 net `827.21 USD`，Sharpe `0.0974`
- `10 bps` 已转负到 net `-1172.79 USD`，Sharpe `-0.1380`

翻成人话：
- 这条线已经足够证明“不是 coursework 偶然物”；
- 但它也不是那种对成本完全不敏感、厚得夸张的 alpha；
- 更准确的描述是：**source-faithful OOS pocket 真实存在，但厚度中等，下一步该进入 admission，而不是直接 paper 化。**

## survivor verdict
**`promote_P2`**

### 会改变系统认知的一句话
`Rank 276` 的 survivor 唯一 follow-up 已经用 repo 原始公开 raw CSV 与同源规则完成 source-faithful reproduction：`5bps` 结果与 source 表格完全一致，且 OOS 在 `8bps`、`10bps` 下仍分别保留约 `+7772.83 USD`、`+6372.83 USD` 的净值，因此它不是只停留在 coursework headline 的脆弱故事，而是值得进入正式 `P2 admission` 的单币 after-cost mean-reversion 候选。

## 为什么不是回 background/P0
如果这轮结果是：
- `5bps` 复现对不上 source；
- 或者一旦换成我们自己的重放，`8/10bps` 立刻塌掉；
- 或者交易数稀薄到几乎不可复查；

那就该直接回背景。

这轮不是：
- `5bps` 精确对齐 source；
- OOS `35` 笔，不是极端稀样本；
- 成本拉到 `10bps` 仍保留正 pocket；
- 对象边界仍然干净，没被扩写成泛 breakout 叙事。

所以 survivor 预算用完后的最诚实出口不是 `background/P0`，而是 `P2`。

## 进入 P2 后最该问的 admission 轴
下一轮不该再重复问“这条线存不存在”，而应直接进入 admission：
1. `time stability`：这条 OOS pocket 是否集中在 1~2 个特定周段；
2. `honesty / execution realism`：spot vs perp、maker/taker 分腿后还剩多少；
3. `parameter stability`：`N / threshold / max_hold` 是否只在一个点上好看；
4. `effectiveness after cost`：扩到更保守成本壳后净边衰减有多快；
5. `re-scope risk`：它是否其实只适合 BTC 单币、不能轻率外推到 alts。
