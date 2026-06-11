# 2026-04-25 22:54 UTC · Rank 26 park reframe revisit

## Selected rank
- `Rank 26`
- selection note:
  - 本轮仍严格限定在 `Rank 1~37` 已 `park` 条目内；`50+` 与 `80~110` 号段近两天已连续覆盖，本轮按轮转回到 `25~49`
  - `Rank 26` 上次 bot6 复盘是 `2026-04-18 18:23 UTC`，已超过默认 `7` 天回避窗口
  - 目标不是重开 old verdict，而是回答：4 月下旬新增的 trend/state 证据，有没有给 old `Rank 26` 带来一条不同于既有 `Rank 26b` 的新单轴

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - `research/park_reframe/2026-04-18_1823_rank26-park-reframe.md`
- new side evidence:
  - `research/optimization_loop/2026-04-21_0534_cttrend_xs_techstack_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-23_0743_stochrsi_macd_freshintake_background_p0.md`

## 1) 原 rank 为什么 park？
原 `Rank 26 / regime_triplet state gate` 被 park 的核心原因没有变化：它把 `regime_triplet` 写成了 **strict allow/deny entry gate**，要求 baseline 方向成立后，还必须满足：
- `long = up_regime`
- `short = down_regime`

它不是完全没有 pocket；它一度升到 `P2`，full scope（`BTC/ETH/SOL`）下也确实出现过低成本正值：
- `strict_up_down @ 6bps/side ≈ +14.65%`
- `positive_asset_ratio = 2/3`
- `10bps/side ≈ +2.44%`

但 genuinely verdict-changing 的最小诚实检查早就把最自然 rescue 做完了：
- 剥离 `BTC` 弱腿，只看 `ETH+SOL-only`
- `15bps/side ≈ +2.29%`，但只剩 `1/2` 资产为正
- `20bps/side ≈ -11.17%`
- `15bps` 时间桶仍有明显破口：`bucket_1 ≈ -8.44%`

因此原 `park` 的审计意义要保留：
> 失败的是 old `Rank 26` 把 regime 信息放在 strict entry gate 主职责层，不是 state / trend-readiness 主题整体归零。

## 2) 它更像 hard park 还是 soft park？
**本轮仍判为 `soft park`，但已比 4 月 18 日那轮更接近 `hard park with consumed residual`。**

原因：
1. old line 确实留过一点 residual value，否则不会先升 `P2`，也不会自然派生出 `Rank 26b`；
2. 但原线最自然的一刀早已被消费成 `Rank 26b`；
3. `ETH+SOL-only` 的最小窄救法也没把它修成干净 `P3`；
4. 4 月下旬的新证据继续把“state / trend-readiness 有用”的宿主往 **完整 trend shell / timing shell / ranking/router** 上移，而不是把 old strict gate 拉回 queue-facing 独立对象。

## 3) 有没有“可救信号”？
**有主题层面的残余，但没有 old `Rank 26` 壳内的新可救信号。**

### A. CTREND 多时域技术状态聚合
`2026-04-21_0534_cttrend_xs_techstack_freshintake_background_p0.md` 给出的结论很清楚：
- `15m` top-vs-bottom continuation spread 连 gross 都没保住；
- `5m` 更差；
- 剩余价值更像 `ranking/router` 提示层，而不是独立 front raw alpha。

这说明：把更多 state / trend-readiness 变量继续聚合，**不会自然把 old Rank 26 strict gate 救活**；反而更像把主题上移成 symbol-selection / router 角色。

### B. StochRSI × MACD trend-aligned pullback
`2026-04-23_0743_stochrsi_macd_freshintake_background_p0.md` 也给出类似收口：
- `5m` 不是可独立承接的主 alpha；
- `15m hold4` 只剩大约 `+1bp/trade` 的极薄 net8 pocket；
- 剩余正值又集中在少数币；
- 更诚实的定位是 shared `trend-readiness / entry-timing` 提示，而不是新 front slot。

这进一步说明：trend/state 主题若还有信息，更像完整 pullback/timing shell 的局部 admission 层，而不是足以从 old `Rank 26` 再诚实切出 `Rank 26c`。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然只有既有 `Rank 26b`：**

> `demote strict up/down entry gate into an asymmetric veto-only regime overlay`

也就是：
- 不再要求 long 必须 `up_regime` / short 必须 `down_regime` 才 allow；
- 保留现有 base setup 自己负责触发；
- `regime_triplet` 只在明显坏环境时做 veto：
  - long 遇到 `down_regime` veto
  - short 遇到 `up_regime` veto

本轮没有第二刀比这更诚实；再往前写，只会变成：
1. 同义重讲 `26b`；或
2. 偷带第二轴，把对象换成新的 trend / pullback / ranking 宿主。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

理由：
1. 原 `park` verdict 没被推翻；
2. old `Rank 26` 唯一诚实 residual 仍只到既有 `Rank 26b`；
3. 4 月下旬新增证据强化的是“新 trend/timing shell 或 router 宿主”，不是 old `Rank 26` 的新单轴；
4. 若现在再 draft `Rank 26c`，更像重复记账，不像新增决策价值。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `regime_triplet` 作为 strict entry gate 对 friction / time bucket 过敏；最自然的 `ETH+SOL-only` 窄救法也没把它修成干净 `P3`。

### 它更像 hard park 还是 soft park？
`soft park`，但已比 4 月 18 日那轮更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但主要是 state / trend-readiness 作为新 trend shell、timing shell、ranking/router 宿主内的局部信息；可救的是主题，不是 old `Rank 26` 壳。

### 最值得改的唯一一刀是什么？
仍然只是既有 `Rank 26b`：把 strict gate 降级成 asymmetric veto-only regime overlay。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已比 4 月 18 日那轮更接近 hard park with consumed residual；4 月下旬新增的 CTREND tech-stack 与 StochRSI/MACD pullback 证据继续说明，state / trend-readiness 主题若还有价值，更像新的 trend/timing shell 或 ranking/router 宿主，而不是足以把 old Rank 26 再诚实派生成 Rank 26c；旧线唯一自然 residual 仍只到既有 Rank 26b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。

## 邮件短标题
- `Rank 26 继续 park，唯一残余仍只到 26b`
