# turning-point confirmed continuation fresh intake → background / P0

- 时间：2026-03-31 23:14 UTC
- 对象：`turning-point confirmed continuation`
- 来源：`research/quant_digests/2026-03-31_2248_turning-point-confirmed-tsmom-alpha.md`
- 结论：**不进入前排，直接回 `background/P0`**

## 这轮只回答一件事
把论文里的 `turning-point confirmed continuation` 诚实翻成当前 desk 可交易宇宙里的最小 clean-room 版本后，它有没有形成一个可审计、after-cost 仍站得住的 trend raw alpha pocket。

## 最小 clean-room 口径
为了避免把论文 headline 直接偷渡成 desk 结论，这轮只做一个很窄但因果顺序清楚的迁移：

1. 数据：`reports/artifacts/rank29_trigger_tf_monthly/cache/{BTC,ETH,SOL}USDT__5y__15m.csv`
2. 结构层：先把 `15m` bar 重采样成已收盘 `1h` bar；在 `1h` 上用与仓库既有 `confirmed swing` 一致的做法做 causal turning-point 确认（`lookback = 5`，pivot 必须等确认后才可用）
3. 方向定义：
   - 多头结构：最近确认低点抬高 + 最近确认高点抬高
   - 空头结构：最近确认高点降低 + 最近确认低点降低
4. 触发：
   - 多头：`1h close` 向上穿过 `prev_high`
   - 空头：`1h close` 向下跌破 `prev_low`
   这一步刻意只回答 digest 里最值钱的那部分——**关键 turning-point 被越过后的 continuation**
5. 执行：触发后的下一根 `15m open` 入场，`no-overlap`
6. 退出：
   - 固定持有 `4h / 8h / 12h` 三档（即 `16 / 32 / 48` 个 `15m` bar）
   - 若中途跌破/涨回失效位（多头看 `last_low`，空头看 `last_high`），则提前失效出场
7. 成本：统一看 `6 / 10 / 15 bps per side`

## 结果
### 1) 触发非常稀薄
5 年样本里，这个最小 causal 迁移只触发出：

- `BTC`: 2 个空头事件
- `ETH`: 1 个多头事件
- `SOL`: 1 个多头事件

也就是说，它还没来得及进入“有没有稳定 edge”的阶段，就先卡死在 **当前 perp majors universe 下几乎没有足够可交易事件数**。

### 2) 跨资产不成立
按 `4h / 8h / 12h` 三档持有看，只有 BTC 那两个空头事件在部分窗口里略微为正；ETH 与 SOL 的单次触发都为负。

聚合后表现：

- `4h hold @ 6bps/side`：3 个资产里只有 1 个为正，`positive_asset_ratio = 1/3`
- `8h hold @ 6bps/side`：仍只有 1/3 资产为正，平均 `mean_total_net ≈ -0.69%`
- `12h hold @ 6bps/side`：仍只有 1/3 资产为正，平均 `mean_total_net ≈ -1.10%`
- 成本提高到 `10 / 15 bps` 后并没有出现更清晰的 survive 口袋

### 3) 这不是一个足够诚实的 `keep_P1`
如果这条线要拿到 `keep_P1`，至少应该满足下面其中大部分：

- 当前可交易宇宙里，confirmed turning-point 的定义能稳定地产生足够事件数
- entry / exit / confirmation delay 有统一、可审计的 causal 边界
- after-cost continuation 不只是论文样本里好看，而是在当前 perp transfer 下仍留下最小 pocket
- 不是只靠单一币、单一方向、单一窗口的幸存

这轮结果都没满足：

- **事件太薄**：5 年只得到 4 次事件，连最小 admission 样本量都不够
- **跨资产不成立**：ETH/SOL 没给出可迁移的 continuation pocket
- **方向也不稳**：唯一略正的是 BTC 的少数空头事件，而不是一个双边都能站住的结构 raw alpha
- **解释最诚实的地方在于**：论文里的 turning-point continuation 更像一个结构观察框架或 trend family 的 confirmation 语言，但在当前 desk 的统一 perp majors 迁移里，还没形成能占前排资源的独立 raw alpha

## hard verdict
`turning-point confirmed continuation` 这条 intake **不分配 Rank，不进 keep_P1，直接记为 background/P0**。

一句话版：**论文里“结构确认后继续延续”这个想法有研究味道，但在当前 BTC/ETH/SOL perp 的最小 causal transfer 下，触发过稀、跨资产不成立，仍停留在 paper structure insight，而不是 desk 可审计的前排 raw alpha。**

## why this changes runtime truth
这轮把它从“看起来像值得做趋势 intake”的论文线，改写成了：

> 在当前 perp majors universe 下，它还不足以拿到 `keep_P1`；最诚实去向是 `background/P0`，而不是继续占用 fresh/survivor 槽位。

## 复现备注
本轮是内层 first verdict，不额外新建独立站点页；reader-facing 变化通过 optimization loop 记录与首页索引刷新承接。
