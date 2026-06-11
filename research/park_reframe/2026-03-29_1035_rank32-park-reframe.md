# 2026-03-29 10:35 UTC — Rank 32 park reframe

- source rank: `Rank 32 / EMA structure vs MA slope direction gate`
- current authoritative status: 原 `Rank 32` 仍是 `park / evidence pool`；其最自然窄派生 `Rank 32b` 已进入 `Paper / 正在自动运行`（见 `docs/TODO.md`）
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 本轮选哪条，为什么
- 本轮处理：`Rank 32`
- 选择理由：属于本任务要求的 `Rank 1~37` 已 parked 范围；上次 `bot6 park-reframe` 复盘是 `2026-03-21 00:30 UTC`，已超过 `7` 天；同时它有一个很典型的问题——**原 rank 不是纯 hard fail，但最自然的一刀已经被 `Rank 32b` 消费**，值得低频复核一次，确认是否还诚实地需要 `Rank 32c`。
- 本轮只做 park-reframe 判断；**不改** `docs/TODO.md` 顶部排班，也**不推翻** 原 `park` 审计结论。

## 2) 原 Rank 为什么会 park
原始证据来自：
- `research/optimization_loop/2026-03-17_1102_rank32-ema-slope-intake.md`
- `research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md`

原 Rank 32 比较的是：
- `ema_cross_only`
- `ema_cross_plus_slope_floor`
- `ema_cross_plus_slope_reclaim`

它被 park 的核心原因并不是“完全没 edge”，而是：
1. **正 pocket 主要建立在过薄交易密度上**：
   - `ema_cross_plus_slope_floor @ 6bps/side` 虽有 `mean_total_return≈+50.76%`、`positive_asset_ratio=3/3`
   - 但 `mean_trades≈75.7`、`mean_no_trade_ratio≈99.34%`
2. **更漂亮的 reclaim 版进一步把样本压得更稀**：
   - `ema_cross_plus_slope_reclaim @ 6bps/side` 仍为正，`positive_asset_ratio=3/3`
   - 但 `mean_trades≈25.0`、`mean_no_trade_ratio≈99.78%`
3. desk 当时已经把 blocker 写得很清楚：
   - 真正有信息量的更像 `aligned slope floor`
   - 不是那层更“好看”的 `spread-mid reclaim`
   - 但即便如此，**交易还是稀到不诚实地不该直接留在原 Rank 32 继续往前推**

所以原 Rank 32 的 `park` 是否掉的是：
- “把 `EMA cross + slope + reclaim` 当成一个仍可继续推进的完整候选”；
- 而不是否掉“slope floor 里可能留有 residual information”这个更窄命题。

## 3) 它更像 hard park 还是 soft park
**结论：soft park，但现在比 2026-03-21 更偏硬。**

为什么仍算 soft park：
- 原 clean replication 明确留下了 residual signal：`slope_floor` 明显优于 `cross_only`；
- 这说明问题更像“写法太厚/太稀”，不是主题完全错。

为什么现在更偏硬：
- 那条最自然、最窄、最诚实的一刀——**删掉 reclaim，只保留 EMA cross + aligned slope floor**——已经被正式派生成 `Rank 32b`；
- 且 `Rank 32b` 后续不只是停留在 queue note，而是已经完成 clean replication / promotion honesty，并进入当前 `Paper / 正在自动运行`；
- 换句话说，原 Rank 32 的主要 residual value 已经被消费过，不再适合围绕同主题继续派生第二个近义 `Rank 32c`。

## 4) 现有证据里有没有“可救信号”
**有，但这次不是新的可救信号，而是“旧可救信号已经被兑现并消耗掉”。**

当前仍成立的可救信息只有这一条：
- `edge` 更像坐落在 `slope floor`
- `reclaim` 更像过严、过审美化的确认层

而这条信号已经被：
- `research/optimization_loop/2026-03-18_0135_rank32b-clean-replication.md`
- `research/optimization_loop/2026-03-18_0236_rank32b-scope-promotion.md`
- `docs/TODO.md` 当前 `Rank 32b / narrow paper lanes`

完整消费。

本轮没看到足够新的旁证，能把 `Rank 32` 再诚实地收敛出第二条不同于 `32b` 的唯一主修改轴。相反，最近 desk 的新 digest 更像：
- 把 EMA 角色继续往 `context / filter / structure verdict` 上拆分；
- 或者去支持别的 raw-alpha family；
- **不是**再把 Rank 32 重新拆出一个独立 queue-facing 新候选。

## 5) 最值得改的唯一一刀是什么
如果必须回答“唯一一刀”，答案其实**仍然还是老答案**：

> **remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor**

也就是已经存在的：`Rank 32b`。

这恰恰说明本轮不该再 draft 新假设：
- 因为最值得改的一刀并没有变化；
- 而且它已经被实际执行、验证并推进到了 running paper lane；
- 现在再写一个 `Rank 32c`，大概率只是把 `32b` 换壳重讲，或者偷带第二轴（如 OI / session / band-pass / new exit），这不符合本任务的单轴最小改动原则。

## 6) 是否值得形成新的 derived hypothesis
**不值得。**

原因有三层：
1. **原 Rank 32 的 park 审计仍成立**：原命题之所以被 park，是因为正 pocket 主要靠极稀交易密度支撑，这个事实没有变。
2. **唯一自然 residual 已被既有 Rank 32b 消费**：删 reclaim、保留 slope floor 这条线已经不只是提案，而是实际落地并进入 paper continuity。
3. **没有足够新证据支持第二条不同主轴**：最近没有出现能把 Rank 32 诚实重写成另一条 queue-facing hypothesis 的新单轴证据；如果硬写，只会变成和 `Rank 25c / 35b / 8b` 一类近邻 EMA 角色调整互相重叠。

因此本轮更诚实的结论是：
- 原 `park` 保留；
- `Rank 32b` 继续代表这条主题已被消费的唯一自然救法；
- **不诚实新增 `Rank 32c`**。

## 7) trade on / trade off（仅对既有 residual 的复核）
本轮不新增 derived hypothesis，但为便于后续人工接手，仍复核既有 residual 一句：

- trade on：保留 higher-tf EMA 方向 + aligned slope floor，对 15m 只要求站回 fast EMA，不再额外要求 `spread-mid reclaim`
- trade off：放弃更严格、更好看的 reclaim 确认，换取略高 trade density；但即便这样，交易密度依然偏稀，所以这条 residual 更适合作为既有 `Rank 32b` 的 running paper continuity，而不是继续派生成新的 queue-facing 假设

## 8) 本轮结论
- 原 Rank 为什么 park：因为 positive pocket 主要建立在极薄交易密度上，尤其 reclaim 版进一步把样本压到过稀；原命题不够诚实地继续前推。
- 它更像：`soft park，但比 2026-03-21 更偏硬`
- 有没有可救信号：有，但只剩既有 `Rank 32b` 那条已兑现的 residual
- 最值得改的唯一一刀：仍是 `remove reclaim, keep slope floor`
- 是否值得形成新的 derived hypothesis：**否**
- 本轮最终结论：`keep_park`

## 9) 文件与提交流程说明
- 本轮只更新本日志、`research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md` 顶部排班
- 当前 git 工作区存在大量无关脏文件 / 运行中产物更新（含 `Rank 32b` paper continuity 相关文件），本轮**不做 commit**，避免混提
