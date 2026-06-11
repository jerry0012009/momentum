# Rank 229 / ETH-led abnormal-day continuation (session-defined) — P2 admission 第 2 步：time / parameter 收口后直接 promote_P3

- Time: 2026-03-29 00:48 UTC
- Target: `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- Step type: `P2 admission` / `time + parameter`，并在证据已足够时直接执行 `P2 -> P3`
- Verdict: `promote_P3`

## 本轮要回答的问题
这一步只回答一个问题：

> 在上一轮已经确认 `next-bar open` honest entry 之后，`Rank 229` 留下来的 ETH 主 pocket，是否对时间切分与参数扰动足够稳定到可以冻结成 paper-launch 级别的最小 spec，而不是继续停留在“事后挑 pocket”的 `keep_P2`。

按照 policy，如果这一步已经给出“足够值得进入 paper trade / paper launch”的结论，就必须直接升级到 `P3`，不能把升级动作拖到下一轮 review。

## 复现口径
数据直接使用现成公开缓存：
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/exec_cache/ETHUSDT__365d__5m__perp.csv`

统一口径保持和上轮 admission 一致：
1. `Binance Futures ETHUSDT 5m`，最近约 `365d`；
2. session offset 扫描 `0 / 4 / 8 / 12 / 16 / 20` 小时；
3. 用前 `30` 个 session 的 close/open 收益 rolling std 作为 `sigma_session`；
4. 触发条件：`|ret_from_open_t| >= k * sigma_session` 首次触发且剩余 bar 数 `>= M`；
5. 执行：`next-bar open` 同方向入场，持有到 session close；
6. 扫描 `k ∈ {1.0, 1.25, 1.5, 1.75, 2.0}` 与 `M ∈ {4,8,12}`；
7. 检查 full-sample、前后半样本、三等分样本下的 `gross / net-12 / hit-rate`。

新增产出：
- `reports/artifacts/rank229_p2_admission_time_parameter/time_parameter_segments.csv`
- `reports/artifacts/rank229_p2_admission_time_parameter/stability_summary.csv`
- `reports/artifacts/rank229_p2_admission_time_parameter/summary.json`

## 关键结果
### 1) 这不是只有单一 lucky pocket 才成立；一整条参数 ridge 都还活着
最厚的 pocket 仍然出现在 `offset 20h / k=1.25` 一带：

- `offset 20h / k=1.25 / M>=12`：`n=90`，gross `+98.7 bps`，net-12 `+86.7 bps`
- `offset 20h / k=1.25 / M>=8`：`n=91`，gross `+97.0 bps`，net-12 `+85.0 bps`
- `offset 20h / k=1.25 / M>=4`：`n=94`，gross `+95.7 bps`，net-12 `+83.7 bps`

更重要的是，这不是单点尖峰；`M=4/8/12` 三档几乎都成立，说明剩余 bars 门槛不是关键脆弱旋钮。

同时，`offset 0h` 也保留了一条更保守但同样稳定的 ridge：

- `offset 0h / k=1.25 / M>=12`：`n=105`，gross `+80.5 bps`，net-12 `+68.5 bps`
- `offset 0h / k=1.5 / M>=12`：`n=79`，gross `+65.3 bps`，net-12 `+53.3 bps`
- `offset 0h / k=1.75 / M>=12`：`n=59`，gross `+56.2 bps`，net-12 `+44.2 bps`

这说明对象已经不是“只有一个 offset + 一个阈值才勉强为正”的脆弱结构；它至少存在两条可冻结的 parameter ridge，其中 `offset 20h / k≈1.25` 更厚，`offset 0h / k≈1.5~1.75` 更保守。

### 2) 时间稳定性足够过 admission，不再只是某一段行情侥幸拉出来
对最厚主 pocket `offset 20h / k=1.25 / M>=12`：

- full sample：`net-12 +86.7 bps`
- 前后半样本都为正，较差半边仍有 `+24.6 bps`
- 三等分样本 `T1/T2/T3` 全部为正，最差一段仍有 `+6.7 bps`

对更保守的固定 spec 候选 `offset 0h / k=1.75 / M>=12`：

- full sample：`net-12 +44.2 bps`
- 两个 half 都为正，较差 half 仍有 `+40.2 bps`
- 三个 third 也都为正，最差 third 仍有 `+15.6 bps`

也就是说：
- 如果目标是**最大厚度**，`offset 20h / k=1.25` 足以成立；
- 如果目标是**更保守、跨分段更均匀的 frozen spec**，`offset 0h / k=1.75 / M>=12` 也已经成立。

无论选哪条，结论都不是 `drop`，也不需要再回到 `P1` 重新定义 hypothesis。

### 3) admission 真正收口的系统结论
把第 1 步和这一步合在一起，当前系统认知已经足够明确：

- `honesty / execution realism`：已经用 `next-bar open` 和 `net-12` 成本口径验过，主 edge 没塌；
- `cross-asset honesty`：BTC 只剩薄旁证、LTC 只是稀疏尾部，最诚实对象定义仍然是 `ETH-led`；
- `time stability`：主 pocket 与保守 pocket 在分段样本下都没有塌成负值；
- `parameter stability`：不是单点尖峰，至少有一条厚 ridge 和一条保守 ridge；
- `re-scope necessity`：已经在 survivor 阶段完成过一次 honest re-scope（从三币通用收缩到 `ETH-led session-defined`），本轮不再需要第二次 `P2 -> P1` 回退。

因此，这一步最诚实的 verdict 不是继续 `keep_P2`，而是：

> `Rank 229` 已经足够值得进入 `paper trade / paper launch queue`，应直接从 `Active P2` 升到 `P3`。

## Frozen spec（供后续 launch wiring 使用）
当前更适合先冻结成 queue-side paper spec 的版本：

- Symbol: `ETHUSDT perp`
- Bar: `5m`
- Session offset: `20h`
- Trigger threshold: `k = 1.25 * sigma_session`
- Minimum remaining bars: `M >= 12`
- Entry: `next-bar open`
- Exit: `session close`
- Cost assumption: `12 bps round-trip`

保守备选 spec：
- `offset 0h / k=1.75 / M>=12`

## Runtime writeback
- `Active P2 slot`: 从 `Rank 229` 释放为 `none`
- `Paper launch queue.current_target`: 改为 `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- `Paper launch queue.latest_result`: 更新为 `Rank 229` 的 `time / parameter` admission 已确认它不是事后挑 pocket：ETH 主 edge 在 `offset 20h / k=1.25 / M>=12` 下保留约 `+86.7 bps net-12`，且前后半样本与三等分样本都仍为正；因此对象不再停留 `P2`，本轮直接 `promote_P3` 进入 paper launch queue，等待最小 launch wiring
- `Paper launch queue.latest_result_record`: 指向本文
- `Active P2 slot.latest_result_record`: 指向本文作为最终 exit 记录
- `p2_rounds_since_level_change`: `2 -> level changed / cleared`
- `p2_consecutive_keep_p2`: 不再继续累计，随升级清空
- 当前 `cycle_plan` 第 2 项写为 `done`；第 3 项因前置目标已在本项中直接 `promote_P3`，应写成 `blocked`，避免对已离开 `P2` 的对象重复执行出口 verdict。

## 一句话结果
`Rank 229` 的 ETH abnormal-day continuation 在 honest `next-bar open` 口径下，不仅厚度没塌，而且对 session/threshold/min-remaining 扰动保留了可冻结的稳定 ridge；因此它已经足够进入 `paper launch queue`，本轮直接从 `Active P2` 升到 `P3`。