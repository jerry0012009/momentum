# partial-corr residual pair catch-up — fresh intake first verdict: background/P0

## 本轮执行小点
- target: `research/quant_digests/2026-04-22_1533_partialcorr-lagcatchup-thresholdcalibration-alpha.md`
- action: fresh intake：对 `BTC/ETH 残差化后按强度排名的 pair catch-up` 做 first verdict，只补 1 个最小 decisive blocker（放弃 repo 过严固定阈值后，这条 pair catch-up 是否相对既有 pairs family 仍有独立 after-cost 新增价值）
- verdict: `background/P0`

## 结论
`BTC/ETH 残差化后按强度排名的 pair catch-up` 的 fresh intake first verdict 已诚实收口 `background/P0`：放弃 repo 过严 fixed-threshold 后，当前可见 `15m` 基线只剩约 `+4.88bps/event` 的 gross catch-up，尚不足以覆盖最小双腿成本；唯一看似更厚的 `5m` pocket 只剩 `10` 笔极小样本，且 pair 结构仍集中在 `ADA/SUI / DOGE/ADA / ADA/AVAX / AVAX/SUI / AVAX/LINK` 这类已被现有 pairs admission / spread-fade 家族覆盖的 alt-alt 组合，没有证明相对已 live `Rank 424 / 431` 留下独立、可排队的新增 after-cost alpha。

## 最小证据
来源：
- `reports/artifacts/quant_digests/solipsirai_partialcorr_20260422/event_probe_summary.csv`
- `reports/artifacts/quant_digests/solipsirai_partialcorr_20260422/top12_pairs.csv`
- `research/optimization_loop/2026-04-19_0402_rank424_survivor_followup_promote_p2_pair_admission.md`

### 1) after-cost blocker 已足够回答
`15m` 最稳的可见基线是：
- pair selection: `top12_abs_partialcorr_ex_btc_eth`
- divergence `0.75%`
- hold `3 bars`
- events `529`
- mean gross `+4.8839bps`
- median gross `+3.0562bps`
- win rate `51.42%`

这说明在还没计入双腿 taker/maker、切换、同步成交与同币并发约束前，厚度就已经只有中个位数 bps。对 short-cycle crypto pairs desk 来说，这不足以支撑一个新的独立 front object：只要放入最小双腿 round-trip 成本，baseline 基本就会被吞掉。

### 2) 更厚 pocket 只是极小样本，不足以构成 survivor
`5m` 下最亮眼的一格是：
- divergence `1.0%`
- hold `3 bars`
- events `10`
- active pairs `5`
- mean gross `+31.20bps`
- win rate `90%`

但这里的事件数只有 `10`，明显属于薄样本 pocket，不能当成独立 after-cost alpha 的稳态证据。

### 3) pair distinctness 不成立
top pairs 主要是：
- `ADA/SUI`
- `DOGE/ADA`
- `ADA/AVAX`
- `AVAX/SUI`
- `AVAX/LINK`
- `LINK/SUI`

这类对象的研究主语，仍然是“alt-alt pair admission + spread/catch-up 的短线相对价值壳”。而 runtime 里已存在：
- `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`（已 live）
- `Rank 431 / cointegration maker-first + hard time-stop pairs`（已 live）

也就是说，这次 repo 真正新增的只有：
- `BTC/ETH residualization` 这个 pair ranking / admission 视角；
- `lead-lag divergence -> lagger catch-up` 这个轻度方向化 entry。

但在当前 artifact 里，这个新增层并没有证明自己能把同一批 alt-alt pairs 提升成新的、费后可独立排队的 family；更像是现有 pairs engine 的一个 ranking / admission / entry 变体。

## 为什么不是 keep_P1
要保留 survivor，至少需要满足二者之一：
1. 在最小双腿成本现实下，留下不是薄样本幻觉的 after-cost pocket；
2. 即使边际还薄，也已证明主语 distinctness 足够强，和已 live pairs family 不是同一类壳的换皮。

当前两条都没成立：
- `15m` 稳样本 gross 太薄；
- `5m` pocket 太稀；
- top pairs 与现有 pair-admission/live runner 家族高度重叠；
- repo 的真正价值更像“把过严固定阈值改成 rank-based residual admission”的 shared design hint，而不是新的独立 alpha 主语。

## 对 runtime 的影响
- 本轮小点完成并写回 `cycle_plan` 第 2 项：`done`
- `Fresh intake slot` 更新为该对象的 `background/P0` first verdict
- 该对象记入 `Background pool`，不进入 survivor

## 尾部步骤状态（非阻断）
- `publish_homepage_index.sh` 异步执行在 `2026-04-22 20:35:39 UTC` 收到 `SIGKILL` 失败（非阻断尾部失败，不影响本轮 verdict/state/log 生效）。
- 中文邮件摘要已成功发送（subject: `[momentum-bot3-auto] 残差化 pair catch-up 收口 P0`）。
