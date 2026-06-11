# negative funding 5davg carry router — fresh intake first verdict

- Time: 2026-04-20 06:59 UTC
- Target: `research/quant_digests/2026-04-20_0520_negative-funding-5davg-carry-router-alpha.md`
- Cycle plan slot: 1

## What I checked
只补本轮要求的最小 blocker：把 digest 里已经算出的 `5d avg funding 最负 top1` 后续 `1h/3h` realized carry，放到统一总成本口径下看它是否还能保住独立 after-cost pocket。

使用 artifact：
- `reports/artifacts/quant_digests/2026-04-20_hl_funding_carry_rank_summary.csv`

其中 `long_top_negative_5davg` 汇总为：
- `avg_next1 = +4.47bps`
- `avg_next3 = +13.07bps`
- `hit_next1 = 87.9%`
- `hit_next3 = 92.2%`

## Minimal cost-realism check
把这条想法按最宽松的 desk 可接受理解，先只看总交易成本，不额外夸大：
- `8bps total`（已经是很乐观的双腿总摩擦）：
  - `1h net ≈ -3.53bps`
  - `3h net ≈ +5.07bps`
- `12bps total`：
  - `1h net ≈ -7.53bps`
  - `3h net ≈ +1.07bps`
- `16bps total`（更接近双腿开平 + child execution 的常见保守口径）：
  - `1h net ≈ -11.53bps`
  - `3h net ≈ -2.93bps`

## Verdict logic
这里的关键不是命中率，而是 **净厚度太薄**：
- `1h` pocket 在最乐观 `8bps total` 下都已经转负；
- `3h` 虽然在 `8bps total` 还能留 `~+5bps`，但这还 **没有** 扣掉 digest 明确要求补的另外两个真实摩擦：
  1. 对冲腿 basis 偏移；
  2. funding 结算时钟 / child execution timing mismatch。
- 一旦把这两个现实项加回去，`3h` 这点薄余量没有足够缓冲，不足以支撑一个可独立承接的 carry front object。

## Result
`5d 平均 funding 最负一档 × next 1~3h carry persistence` 在统一双腿成本后只剩极薄甚至转负的净 carry，且尚未覆盖 hedge basis 与 funding 时钟错位；因此本轮 fresh intake 直接收口 `background/P0`，不保留为 survivor。

## Tail step note
- 已按约束独立执行首页刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- 该命令本轮异步返回 `SIGKILL`（无 stdout/stderr）；按 policy 记为非阻断尾部失败，不影响本轮已落地的 state/log/verdict
- 邮件摘要已独立发送成功
