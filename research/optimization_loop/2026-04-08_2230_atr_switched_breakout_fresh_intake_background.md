# 2026-04-08 22:30 UTC · ATR-switched price-velocity × volume-expansion breakout shell · fresh intake first verdict

## 本轮执行小点
- target: `research/quant_digests/2026-04-08_0925_atr-switched-velocity-volume-breakout-shell.md`
- action: 判断 `ATR-switched price-velocity × volume-expansion breakout shell` 是否已足够压成独立 breakout raw alpha，而不是只是在既有 breakout family 里加一个 ATR-switching admission layer
- success_criterion: 必须给出明确 first verdict：若对象能把 `ATR-switched window + price velocity + volume expansion breakout` 压成一个不被既有 breakout / volatility-regime / volume-confirmation family 吸收、且成本后口径至少保留明确可迁移主语的唯一 queue-facing 主语，则写成 `keep_P1`；若当前新增信息仍主要是“窗口切换可作为 breakout 壳的调参 / admission discipline”、未证明对 plain breakout family 有独立增量，则明确写成 `background / P0`

## 读取到的关键上下文
1. 当前 digest 本体来自同一个 `yeshunyi/crypto-momentum-strategy` repo，但其核心结构与 `research/quant_digests/2026-03-25_1730_velocity-volume-leader-continuation.md` 已经高度重合：
   - 都是 `price-velocity` 触发；
   - 都要求 `volume_ratio > 1.5` 与 `RSI` 不过热；
   - 都采用 `50%` 试探 + 再破前高补 `50%` 的二段式入场；
   - 都把 `ATR` 用作 regime / risk shell 的核心部件。
2. 这次新 digest 的真正新增，不在于发明了新的 base alpha，而在于把旧对象重读成：`ATR 状态决定观察窗与涨速阈值`，也就是把 regime-switch 语义往前提。
3. 但按当前项目的 fresh-intake first-verdict 标准，关键不是“讲法是否更 desk-friendly”，而是它有没有形成一个 **不被既有 breakout / leader-continuation family 吸收的独立 queue-facing 主语**。

## 本轮判断
### first verdict
- 结论：`background / P0`

### 为什么不是 `keep_P1`
- **独立主语没有变。** 这条线的 raw alpha 仍然是短窗 `price-velocity breakout / leader continuation`，不是新的 breakout 身体；`ATR-switch` 主要决定看 `15m / 10m / 5m` 哪个窗口、配什么阈值，更像 admission / regime layer。
- **与既有 intake 明显重叠。** `2026-03-25_1730_velocity-volume-leader-continuation.md` 已经把同 repo 的核心骨架压成了 `动态阈值 leader continuation + 二段式入场`；本次版本只是把 `ATR-switch` 说得更靠前，并没有把对象从旧的 velocity/volume continuation family 里剥离出来。
- **新增 portability 指令仍停在 A/B 设计层。** 这次 digest 给出的“拿 `fixed-window breakout` 对照 `ATR-switched breakout`”是合理实验建议，但它本身不是已经完成的独立证据；在没有证明 ATR-switch 相对 plain breakout 有稳定、可迁移的 after-cost 增量前，不够支撑 fresh intake 进前排。
- **更诚实的归位是 family absorb，而不是新开前排。** 当前最合理的读法是：`ATR-switch` 可作为既有 breakout / leader-continuation 家族里的一个 regime-aware admission note 保留，但还不值得单列一个新的 queue-facing raw alpha。

## 会改变系统认知的话
`ATR-switched price-velocity × volume-expansion breakout shell` 目前仍只是既有 `velocity / volume breakout` 家族上的 regime-aware admission 改写，尚未证明相对 plain breakout 有独立且可迁移的 after-cost 增量，因此本轮 fresh intake first verdict 直接收口为 `background / P0`。

## runtime write-back
- `Fresh intake slot` 更新为本对象的 first verdict 结果
- `cycle_plan[3]` 写成 `done`
- `Background pool.latest_parked` 更新为同一句，表示最新被诚实收口的对象回到背景池

## 产出
- log: `research/optimization_loop/2026-04-08_2230_atr_switched_breakout_fresh_intake_background.md`
