# bot3 optimization loop — high-corr pair ratio z-score fade × threshold escalation fresh intake -> background/P0

- 时间：2026-04-25 16:40 UTC
- cycle_plan 项：1
- target: `research/quant_digests/2026-04-25_1542_correlation-zfade-threshold-pocket-alpha.md`
- action: fresh intake：对 `high-corr pair ratio z-score fade × threshold escalation` 做 first verdict，只补 1 个最小 decisive blocker（这条 pair z-fade 在统一成本与持有窗口径下是否真的还保留至少一个可交易 pocket，还是只剩 `gross>0` 但净值几乎全被四腿 friction 吃掉的执行壳）

## 本轮只回答的 decisive question
在统一四腿 taker 成本口径下，这条相关性 pair ratio z-score fade 是否至少还留有一个足以支撑 `keep_P1` 的明确 pocket，而不是只剩 gross 为正、费后被吃穿的执行壳。

## 读取与最小复核
已读取 digest 与本地 artifact：
- `research/quant_digests/2026-04-25_1542_correlation-zfade-threshold-pocket-alpha.md`
- `reports/artifacts/quant_digests/2026-04-25_correlation_pair_zfade_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_correlation_pair_zfade_sweep.csv`

最小 honesty / execution realism 复核只看一个问题：`sweep` 里是否存在统一四腿 taker `16 bps` 下仍为正的 pocket。

复核结果：
- sweep 共 `90` 组参数。
- `avg_net16_bps > 0` 的 pocket：`0` 组。
- 即使放宽到较乐观 `12 bps`，也仅剩 `2` 组、且都集中在同一对 `LINK/UNI`：
  1. `5m / lookback=144 / |z|>3 / max_hold=12`：`69` 笔，`avg_net12_bps ≈ +2.32`，但 `avg_net16_bps ≈ -1.68`
  2. `15m / lookback=96 / |z|>3 / max_hold=12`：`60` 笔，`avg_net12_bps ≈ +0.29`，但 `avg_net16_bps ≈ -3.71`
- baseline pooled probe 也只到 `gross ≈ +2.24 bps/笔`、`net16 ≈ -13.76 bps/笔`，说明 repo 默认相关性+ratio z-fade 主体在现实四腿 friction 下明显不够厚。

## 结论
这条 `high-corr pair ratio z-score fade × threshold escalation` fresh intake 已诚实收口 `background/P0`：统一四腿 taker `16 bps` 成本下，`90` 组 `5m/15m` sweep 没有任何费后为正 pocket；最像样结果也只是在同一对 `LINK/UNI` 上于较乐观 `12 bps` 口径勉强转正，一旦回到统一 `16 bps` 即重新转负，因此当前没有足以支撑 `keep_P1` 的 after-cost pocket，这条线更像 pairs/stat-arb 的 cost-awareness / threshold-router 提示，而不是值得前排保留的新候选。

## 对 runtime 的回写
- `Fresh intake slot.latest_result`：更新为该对象已收口 `background/P0`
- `Fresh intake slot.latest_result_record`：指向本文
- `cycle_plan[1]`：`status -> done`
- `cycle_plan[1].result`：写入本轮会改变系统认知的一句话结论

## 尾部动作
- best-effort 刷新首页（`publish_homepage_index.sh` 本轮异步进程 `delta-crest` 最终以 `SIGKILL` 结束，按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效）
- 发送中文邮件摘要（已发送）
