# 2026-03-29 12:48 UTC — Rank 236 / breakout-short-specific short-side admission score-veto first verdict

## 为什么这轮做它
- 按 `docs/BOT2_BOT3_STATE.md` 当前 `cycle_plan`，排在最前的 pending 小点是：
  - `Rank 236 / breakout-short-specific short-side admission score-veto`
- 本轮严格只执行这一个小点：
  - 只回答它在 `breakout-short` 专用 short-side baseline 上，`penetration/ATR` veto 是否还保留独立 admission 信息；
  - 不重排 `cycle_plan`，不额外展开后面的 conditional fresh intake。

## 本轮读取的关键证据
1. `research/optimization_loop/2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md`
2. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
3. `research/optimization_loop/2026-03-19_1011_rank86-clean-replication-keep-p1.md`
4. `research/optimization_loop/2026-03-19_1037_rank86-time-stability-park.md`
5. `research/quant_digests/2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md`
6. `research/quant_digests/2026-03-22_0858_breakout-bar-conviction-gate.md`
7. `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_pooled.csv`
8. `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_by_symbol_side_threshold.csv`

## 这轮只回答一个问题
`Rank 236` 在 `breakout-short` 专用 short-side baseline 上，是否已经有足够清楚、可复现、且不同于旧 `Rank 86` shared-gate 失败史的独立 admission 信息？

## 结论
- **结论：有，给 `keep_P1`。**
- 正式 verdict：**`Rank 236 / breakout-short-specific short-side admission score-veto = keep_P1`**。
- 因此它不再停留在 fresh intake 未判状态，而是进入 `Surviving candidate slot`，获得那唯一一次最小 follow-up 预算。

## 为什么不是“旧 shared gate 换壳”
### 1) 旧 `Rank 86` 失败的是 shared 角色，不是这条窄版主语
`Rank 86` 被 park 的 authoritative 原因很明确：
- 它把 `penetration×ATR` 写成 `breakout_short / fib_retest_short / ema_psar_follow_short` 三条 lane 共用的 shared admission gate；
- clean replication 后虽有 pooled 改善，但时间稳定性不过关；
- 尤其 `breakout_short + pen_plus_atr` 本身并没有被 shared 写法稳定救活。

所以被否掉的是：
- **“全 desk shared gate” 这个角色定义。**

而当前 `Rank 236` 的主语已经被收窄为：
- 只服务 `breakout-short`
- 只服务 `short-side`
- 只做 `admission score / veto`

这不是旧对象原样续命，而是把唯一残存信息压成一个更窄、更诚实、可直接证伪的新对象。

### 2) 现有短检证据确实支持“short-only breakout admission”，而不支持镜像 shared
`2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md` 的 pooled artifact 给出的信息很直接：
- **short 侧**：
  - `th=0.0`: `n=1477`, `avg_pnl_r=-0.0173`
  - `th=0.2`: `n=1100`, `avg_pnl_r=+0.0068`
  - `th=0.6`: `n=573`, `avg_pnl_r=+0.0489`
- **long 侧**：
  - `th=0.0`: `avg_pnl_r=-0.1197`
  - `th=0.2`: `avg_pnl_r=-0.0787`
  - `th=0.6`: `avg_pnl_r=-0.0324`

读法很清楚：
- `penetration/ATR` 在 short-side breakout proxy 上存在方向明确的 admission 信息；
- 但它并不支持被镜像外推成长侧 shared gate。

### 3) 不是单币幻觉，而是多币同向、阈值有差异
按 `summary_by_symbol_side_threshold.csv`：
- `BTC short`: 从 `th=0.0` 的 `-0.0589` 改善到 `th=0.6` 的 `+0.0980`
- `ETH short`: base 已略正，`th=0.2` 最好（`+0.0912`），说明它更像 score 而非单一全局硬阈值
- `SOL short`: 从 `-0.0337` 提升到 `th=0.4` 的 `+0.0093`、`th=0.6` 的 `+0.0303`

这说明：
- uplift 不是只靠单一币种撑住；
- 但最优阈值不一致，因此当前更诚实的定位依旧是 **admission score / veto**，而不是已经冻结好的统一部署参数。

### 4) 它和当前前排对象并不重复
- `Rank 151` 是 `EWMAC breakout alignment` 的 `band-pass honest gate`，核心信息是“中段分数放行、极端尾部别追”；
- `Rank 236` 是 `penetration/ATR` 的 short-side breakout admission score-veto；
- 二者同属 breakout family 的 gate，但变量主题、错误模式、部署角色都不同。

因此 `Rank 236` 不是在复述 `Rank 151`，而是另一条仍值得给一次最小 follow-up 的窄 admission 线。

## 为什么现在先给 `keep_P1`，而不是直接升 `P2`
因为当前证据虽然足够支持“它值得活过 fresh intake 首判”，但还没到 `P2 admission`：
- 现有主要是 digest/proxy 口径，不是挂到当前 frozen `breakout-short` 事件源上的 clean replication；
- 阈值最优点在 BTC/ETH/SOL 并不一致；
- 目前更像“有独立信息、值得继续”而不是“参数和兑现路径都已足够诚实”。

所以最诚实的 first verdict 是：
- **`keep_P1`，并把唯一 follow-up 用在当前 frozen breakout-short baseline 上做一次最小 clean replication / strict A/B。**

## 本轮 hard verdict
- **`Rank 236 / breakout-short-specific short-side admission score-veto = keep_P1`**
- 进入 `Surviving candidate slot`
- 后续唯一合法 follow-up 方向：
  - 只在当前 frozen `breakout-short` baseline 上做 `baseline vs short_only_penetration_veto/score` 的最小 clean replication；
  - 不顺手扩到 `Fib / EMA`，也不叠第二轴。

## 对 runtime 的直接影响
1. `cycle_plan` 第 3 项应写成 `done`。
2. 该项 `result` 应更新为：
   - `Rank 236` 已完成 first verdict：`penetration/ATR` 在 breakout-short short-side baseline 上保留独立 admission 信息、且多币 short 侧同向改善，不是旧 `Rank 86` shared gate 的翻案，因此本轮给 `keep_P1` 并进入 survivor 唯一 follow-up。
3. `Fresh intake slot.latest_result` 应更新为已完成首判并给出 `keep_P1`。
4. `Surviving candidate slot` 应切换到 `Rank 236`，并把 `followup_budget_remaining` 设为 `1`。
5. `Active P2 slot`、`Paper launch queue` 本轮不变。

## 备注
- 本轮没有把 `Rank 236` 升到 `P2`；
- 本轮也没有 reopen 旧 `Rank 86`；
- 本轮 reader-facing 的系统认知变化是：`Rank 236` 从 fresh intake 转为 `keep_P1 / surviving candidate`。