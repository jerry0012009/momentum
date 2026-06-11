# 2026-03-30 01:30 UTC｜bot3 optimization loop｜Rank 5 park residual -> double-clock open-impulse plus pre-close reversal residual

## 本轮执行小点
- target: `Rank 5 park residual -> double-clock open-impulse plus pre-close reversal residual`
- action: 只回答最近 double-clock 证据是否已让 `Rank 5` 从既有 `open-impulse quality shared gate` 的残余，收敛成新的独立 queue-facing 对象；主语必须锁定为 `double-clock open-impulse plus pre-close reversal residual`，不得回退成泛 session-clock family。

## 读取证据
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`
- `research/park_reframe/2026-03-19_1334_rank5-park-reframe.md`
- `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
- `research/park_reframe/INDEX.md`
- `research/quant_digests/2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`

## 审计结论
### 1) 原 Rank 5 的可救残余已被既有 `Rank 5b` 消费
`2026-03-19` 的 reframe 已经把原 `session-aware intraday TSMOM` 最诚实的一刀固定为：
- 不再把开段信息直接写成尾段 standalone trade；
- 只把 `first-30m impulse quality` 降级成 shared continuation gate / sizing layer；
- 这就是既有 `Rank 5b` 的边界。

因此，若今天要把 `Rank 5` 再推成新的 queue-facing 对象，必须证明它留下了一个**不同于 `Rank 5b`、同时又仍然挂得住 `Rank 5 residual` 名义**的更窄单轴对象。

### 2) `2026-03-23` 的新证据并没有把对象收窄，反而把主题抬升成更大的 raw-alpha family
double-clock digest 的核心主张不是单独保留 `open impulse`，而是：
- leg A：`open-impulse momentum`
- leg B：`pre-close reversal`
- 真正更像完整策略的是两腿组合的 `double-clock raw alpha`

这说明 session-clock 主题确实未死，但它指向的是一个**更完整、也更上位**的 `open-impulse + pre-close reversal` family，而不是可诚实挂回 `Rank 5` 的窄 residual。

### 3) 当前仍缺少“挂回 Rank 5 residual”的对象边界
若硬把它写成 fresh intake，会同时发生三件事：
1. 不再只是 `Rank 5b` 那种角色降级；
2. 新增 `pre-close reversal` 第二条腿；
3. 从 shared gate / sizing layer 重新跳回 standalone raw alpha。

这已经不是在 `Rank 5` 上切一刀，而是在新开一条 `double-clock raw-alpha` 家族。按当前 policy，这类对象若要进前排，应作为新的 family intake 被独立认领，而不是伪装成 `Rank 5 park residual` 的窄 reframe。

## 本轮 verdict
- verdict: `继续留在 park_reframe，不进入前排`
- result_sentence: `Rank 5 park residual` 的最新 double-clock 旁证抬升的是更上位的 `open-impulse + pre-close reversal` 完整时钟 raw-alpha family，而不是它自身可独立挂板的窄 residual；当前唯一诚实残余仍是既有 `Rank 5b`，因此继续留在 `park_reframe`，不进入前排。

## 为什么这会改变系统认知
这一步把 `Rank 5 residual` 和“新的 double-clock family”明确切开：
- `Rank 5 residual` 不能再被当成通向该 double-clock 方向的合法前排入口；
- 若后续要推进该主题，应该走**新的 family intake**，而不是继续在 `Rank 5` 下派生。

## 回写范围
- `docs/BOT2_BOT3_STATE.md`
  - `Fresh intake slot.latest_result`
  - `Fresh intake slot.latest_result_record`
  - `cycle_plan` 第 3 项的 `result/status`

## 结论
`Rank 5 park residual` 的最新 double-clock 旁证抬升的是更上位的完整趋势时钟 raw-alpha family，而不是它自身；它仍只是既有 `Rank 5b` 之外不够独立的弱旁支，因此继续留在 `park_reframe`，不进入前排。
