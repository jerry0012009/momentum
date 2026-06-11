# liquid-perp cross-sectional funding carry × breakout net-bias fresh intake first verdict

- 时间：2026-04-22 21:29 UTC
- 执行者：bot3
- cycle_plan item：1
- target：`research/quant_digests/2026-04-22_1945_xs-fundingcarry-breakout-shell.md`
- verdict：`background/P0`

## 本轮只执行的小点
对 `liquid-perp cross-sectional funding carry × breakout net-bias` 做 fresh intake first verdict：只补 1 个最小 decisive blocker——如果 liquid majors 上 recent funding carry 方向虽对但常规 taker 太薄，它是否仍值得保留为独立前排对象，而不是只算 router / child-execution hint。

## 证据
- digest 自带的 recent Binance USDⓈ-M portability probe 已经把 base alpha 压到最小可判口径：`10` 个 liquid majors、每个 funding 结算点做一次横截面排序、`long highest funding / short lowest funding` 持有下一个 `8h`。
- 这个 probe 的方向并没有读反：`183` 次事件里 continuation 版本平均仅约 `+1.01bps/8h`，反向 reversal 约 `-1.01bps/8h`，说明它更像 `funding-rank continuation`，不是 mean-reversion。
- 但同一 probe 也直接给出了唯一决定性 blocker：粗扣一组多空 round-trip `8bps` 后，平均约 `-6.99bps/笔`、累计约 `-12.79%`；高低 funding 平均 spread 只有约 `1.88bps`，最近活跃 pocket 主要集中在 `SOL/AVAX/XRP/ADA` 这类少数币，厚度远不足以支撑 liquid-majors 上的独立 after-cost raw alpha。
- distinctness 也没有闭合：当前 desk 已有 live `Rank 389 / cross-venue net-carry ranking alpha` 承接 carry/ranking 家族，而本对象最近可见新增价值主要只剩 `8h parent router + 15m/5m maker-first child execution` 的实现提示；`breakout` 在 digest 里也只是 net-bias overlay，不是能单独把这条线抬成新前排对象的独立 base alpha。

## 结论
`liquid-perp cross-sectional funding carry × breakout net-bias` 的 fresh intake first verdict 已诚实收口 `background/P0`：recent liquid-majors probe 虽确认 funding-rank 方向更像 continuation，但 gross 只有约 `+1.01bps/8h`、统一最小双腿成本后约 `-6.99bps/笔`，且新增价值基本退化为 `8h parent router + maker-first child execution` 提示，未证明相对已 live `Rank 389` 留下可独立排队的 after-cost pocket。

## runtime 写回
- `Fresh intake slot.latest_result` 已更新为本 verdict。
- `cycle_plan` item 1 已写为 `done`。
- `Background pool.latest_parked/latest_parked_record` 已追加本轮收口记录。

## 尾部执行状态（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步执行后收到 `signal SIGKILL`，记为尾部非阻断失败，不回滚本轮 verdict/state/log。
- 邮件通知：`send_text_email.py` 已成功发送（subject: `[momentum-bot3-auto] funding carry breakout收口P0`）。
