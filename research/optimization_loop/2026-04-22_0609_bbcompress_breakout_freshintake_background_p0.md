# bot3 auto — BB compression breakout fresh intake 收口 background/P0

- 时间：2026-04-22 06:09 UTC
- 执行小点：cycle_plan item 3
- 对象：`research/quant_digests/2026-04-22_0515_bbcompress-consensus-breakout-shell.md`
- 动作：conditional fresh intake first verdict

## 结论

`BB compression breakout × EMA/MACD consensus` 的 fresh intake first verdict 已诚实收口 `background/P0`：全池 `15m/5m` 统一 `8bps` 后明显为负，表面正 pocket 虽覆盖 `SOL/AVAX/BNB/XRP` 等多个 alt，但全部集中在单一 `2026-04` 样本窗且不同 interval/horizon 下不一致，没有证明至少两个非单一月份支撑的独立 after-cost breakout alpha；因此它当前只适合作为 breakout router / volatility regime component，不保留 survivor。

## 最小 decisive blocker

本轮只补了一个 blocker：`BB compression breakout` 的正收益是否跨出少数 alt / 单一月份，形成可独立承接的 after-cost breakout alpha。

## 证据

- digest 原始 broad-pool：`15m hold4` 238 笔，gross `-4.43bps/trade`，统一 `8bps` 后 `-12.43bps/trade`；`5m hold12` 259 笔，gross `-4.39bps/trade`，net `-12.39bps/trade`。
- symbol pocket 看似有多币：`15m hold8` 的 `SOL net8≈+10.83bps`、`AVAX net8≈+9.05bps`，`5m hold24` 的 `XRP net8≈+9.60bps`、`BNB net8≈+6.72bps`。
- 但对 trade artifact 做 month × symbol 检查后，所有 `n>=3` 的正 month-symbol pocket 都只出现在 `2026-04`：没有第二个月份支撑；且正 pocket 在 `15m` 与 `5m` 的 symbol/horizon 上不一致。

## runtime 写回

- Fresh intake slot 更新为本对象的 `background/P0` verdict。
- cycle_plan item 3 写为 `done`。
- 不创建 survivor slot；item 4 的前置条件因此在下一轮应视为不成立。

## tail status

- homepage index publish: attempted as independent tail command but produced no output and was terminated as non-blocking tail failure; verdict/state/log are not rolled back.
- email notification: sent successfully to configured recipient.
