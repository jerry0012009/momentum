# Rank 350 — survivor follow-up: tradable alt bucket × explicit after-cost verdict = background / P0

- Time: 2026-04-06 10:02 UTC
- Source target: `Rank 350 / BTC lead × low-liquidity alt lag`
- Prior level: `Surviving candidate slot`
- Verdict: `background / P0`
- Survivor budget used: `1/1` (fully consumed)

## Why this changes runtime truth

`Rank 350` 的唯一 survivor follow-up 已经把最关键的 admission 问题问清：现有证据只说明 `BTC 先发现 -> 极低成交 alt 慢半拍补价` 在论文样本和最小 portability probe 里存在超短半衰期相关性，但还没有把它压成 **可成交 alt bucket × 明确 after-cost** 下仍保留可迁移净增量的前排对象；因此它不能诚实升 `P2`，应在此轮收口回到 `background / P0`。

## Decisive read

1. **可见 lag 只活在最薄的 1m 小币桶里**
   - 本地 probe 的 `leadlag_by_horizon.csv` 只覆盖 `QKC / GNO / PIVX / CITY / BIFI` 这类低交易频次样本。
   - `1m` 横截面 `median lead_edge = +0.0089`，而 `3m/5m/15m` 全部转负，说明 alpha 半衰期极短，且主要依赖最薄的那一层 alt bucket。
   - 同一份 summary 里 `1m avg_trade_count_per_bar` 只有约 `12.4 ~ 19.9`，这更像“刚好够观察到慢半拍”的薄层口袋，不是已经被压成 desk 可迁移交易桶的证据。

2. **当前证据没有把“tradable bucket”压实**
   - digest 明确写的是 `low-trade-count but still tradable alt bucket`，但并未给出更硬的成交门槛：没有 quote-volume / spread / notional capacity / fill ratio 的定量下限。
   - 也没有回答：一旦把 universe 从 paper 里的超薄现货小币，收窄到 desk 真正能稳定成交的 alt bucket，这个 `BTC lead -> alt lag` 还剩多少净边。

3. **after-cost 仍停在叙事层，不足以支撑升 P2**
   - paper 引用的费用口径是 `0.02% fee`，但当前 survivor follow-up 没有给出本地 post-cost PnL、round-trip cost、或 fill-adjusted edge。
   - 现有 portability probe 只有相关性/lead-edge，没有把 `1m hold` 变成明确的 `gross -> net` 净增量结论。
   - 对这种 `1m 主半衰期` 的 pocket，若没有明确 after-cost 留存，默认不能把相关性直接当作可交易 alpha admission。

4. **因此本轮应诚实收口，而不是继续拖成开放式 P1/P2**
   - Rank 350 已经用掉 survivor 的唯一一次 follow-up。
   - 这次 follow-up 没把对象推进到“可成交 alt bucket × explicit after-cost 下仍成立”的门槛。
   - 按 policy，此时不应继续留在前排，也不应再补一轮泛化稳定性；最诚实的出口就是 `background / P0`。

## Runtime result sentence

`Rank 350`：唯一 survivor follow-up 已收口——现有证据仍只把 `BTC lead × low-liquidity alt lag` 压成依赖超薄 `1m` 小币桶的相关性口袋，尚未证明其在可成交 alt bucket 与明确 after-cost 下保留可迁移净增量，因此对象不升 `P2`，直接退回 `background / P0`。

## Delivery notes

- `reports/site/index.html` 已用 `python3 scripts/build_site_index.py` 刷新。
- `publish_homepage_index.sh` 的 `/var/www/momentum-report/index.html` 安装步骤需要 `sudo`，本轮 cron 运行态无 elevated 能力，因此未能完成外层站点落盘；邮件摘要已正常发出。
