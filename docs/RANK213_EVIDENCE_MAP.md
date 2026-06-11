# Rank213 evidence map

更新时间：2026-05-06

## 目的

把 Rank213 相关结果按“能回答什么问题”分层，避免后续开发把 frozen30、as-of、monthly-volume causal universe、shadow/live execution audit 混成同一条证据。

## 当前一句话结论

Rank213 当前应该被读成：`frozen30` 是运行/执行口径，`monthly_volume_causal` 才是当前更重要的历史 sanity check。去掉选池未来函数风险后，旧 baseline 明显变弱，所以不能再写成“历史滚动 Top30 已长周期验证通过”。

## 先读这段

- `frozen30`：回答“当前 runner / paper lane 怎么跑”。它不是历史滚动选池证明。
- `monthly_volume_causal`：回答“如果每个月只用上个月已经发生的 K 线数据选池，Rank213 还站不站得住”。当前答案是：明显站不稳。
- `asof_frozen_seed`：只修正“币没上市不能交易”，不等于每月滚动 Top30。
- `live_audit_shadow`：只回答最新 gate、残仓、执行漂移，不回答长期 alpha。

## 无未来函数版本：上月 K 线选池回测

这里的“上月 K 线选池”具体指：在每个月开始时，只使用上一完整自然月 Binance UM perpetual `1d` K 线里的 `quote_volume` 总和，选出当月 Top30 universe；然后在这个当月 universe 上运行原 Rank213 的 15m / veto / gate / 4bps 成本规则。它不会用当月或未来月份的表现来决定当月池子。

样本：`2020-02-01T00:00:00Z` 到 `2026-04-10T18:00:00Z`，rebalance `18087` 次。

| 版本 | 含义 | 开仓率 | 单次均值 | 累计净收益 | 最大回撤 | 当前读法 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1) plain baseline | 原始 15m Rank213 排名逻辑，不加 veto，不加 gate；每次都交易。 | 100.00% | -1.58 bps | -98.09% | -99.62% | 亏损或弱化明显，不支持继续用旧故事解释 Rank213。 |
| 2) baseline + veto | 在 baseline 上加入 short-leg jump veto；仍然每次都交易。 | 100.00% | -2.53 bps | -99.60% | -99.79% | 亏损或弱化明显，不支持继续用旧故事解释 Rank213。 |
| 3a) veto + fixed gate | 沿用 frozen30 研究里的固定 gate；gate OFF 时空仓。 | 3.54% | -0.23 bps | -37.13% | -48.63% | 亏损或弱化明显，不支持继续用旧故事解释 Rank213。 |
| 3b) veto + percentile gate q60 | 用 monthly-volume 历史自身的 expanding percentile q60 gate；这是研究候选，不是当前 live 规则。 | 16.44% | 0.18 bps | 6.47% | -71.22% | 全样本略正，但回撤很深，只能当候选研究，不能当已过关。 |

核心读法：旧 frozen30 的 `baseline+veto+gate` 在同一长样本里看起来是正的，但换成上月 K 线 causal 选池后变成约 `-37.13%`。这说明旧结果很可能被静态名单 / 幸存者偏差放大。

## 证据分层

| 层级 | 证据面 | 默认入口 | universe / causality | 当前读法 |
| --- | --- | --- | --- | --- |
| Current Runtime | `current_runtime_frozen30`<br/>Frozen admission 30-symbol runner<br/>status=`paused_runtime` | `paper/rank213_largecap_xs_jump_veto.html` | frozen30<br/>static admission seed; not a rolling historical top30<br/>cadence=3h non-overlapping frozen seed baskets | This is the frozen paper/live reference lane definition. Live automation is paused; this lane is not evidence that historical rolling top30 selection works. |
| Live Audit | `live_audit_shadow`<br/>Raw-bar shadow / dryrun / live canary audit<br/>status=`paused_audit` | `paper/rank213_largecap_xs_jump_veto_shadow_runner.html` | frozen30 execution universe<br/>execution audit; consumes current frozen universe and latest raw-bar recompute<br/>cadence=15m official-close audit plus canary pending manager | Use this lane to understand latest decision, gate state, basket completeness, residuals, and execution drift when automation is enabled. Live automation is currently paused; do not read this lane as long-history alpha evidence. |
| Causal Historical | `monthly_volume_causal`<br/>Monthly-volume causal universe rebuild<br/>status=`primary_historical_evidence` | `paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html` | monthly_volume_top30<br/>select each month by previous full calendar month's Binance UM perpetual 1d quote volume<br/>cadence=15m rank213 rules on monthly rebuilt universe | This is the current primary historical sanity check for rolling selection. It materially weakens the old Rank213 story. |
| Candidate Research | `baseline_refresh`<br/>Monthly-volume baseline refresh<br/>status=`research_only` | `paper/rank213_largecap_xs_jump_veto_monthly_volume_baseline_refresh.html` | monthly_volume_top30<br/>same causal monthly volume universe as rebuild; different daily baseline candidates<br/>cadence=daily rebalance / next-day close-to-close hold | Useful as a first falsification of new mother baselines, not an apples-to-apples replacement for original 15m Rank213. |
| Candidate Research | `baseline_v2_four_direction`<br/>Baseline V2 four-direction initial review<br/>status=`research_only` | `paper/rank213_baseline_v2_four_direction_review.html` | monthly_volume_top30<br/>same causal monthly volume universe; first three directions use daily next-day backtest, fourth needs historical perp data<br/>cadence=daily rebalance / next-day close-to-close hold for price baselines | Useful as the next baseline research map. The first direction is strongest so far, but drawdown remains too high; the perp overlay needs historical funding/basis/OI data before evaluation. |
| Candidate Research | `age90_14d_second_round_validation`<br/>age90_14d_skip1d_voladj second-round validation<br/>status=`second_round_research_only` | `paper/rank213_age90_14d_second_round_validation.html` | monthly_volume_top30<br/>previous full-month quote-volume universe; age >= 90d; score uses t-15d to t-1d only<br/>cadence=daily rebalance / top3-bottom3 / 4bps per-basket research cost | Strongest current replacement-baseline candidate, but still research-only. Cost sensitivity, 2022-2023 weakness, and lack of minute/orderbook execution validation prevent live promotion. |
| Live Canary | `age90_14d_phase3_validation`<br/>age90_14d_skip1d_voladj — current live canary (2026-05-06)<br/>status=`live_canary_active` | `paper/rank213_age90_14d_phase3_validation.html` | monthly_volume_top30<br/>previous full-month quote-volume universe; age >= 90d; score uses t-15d to t-1d only; signal skips most recent day for causality<br/>cadence=daily rebalance / top3-bottom3 / $20 per leg / maker-first entry + horizon exit | Phase 3 did not pass formal live promotion (drawdown, cost sensitivity, walk-forward fragility, weak short-side). User chose to proceed with tiny-live canary for real-money falsification since 2026-05-06. Live engine signal formula cross-validated against backtest — identical output. |
| Partial Causality | `asof_frozen_seed`<br/>As-of universe long-history review<br/>status=`limited_historical_evidence` | `paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html` | frozen seed with onboard-time availability<br/>symbols only participate after onboard time; no rolling top30 reselection<br/>cadence=15m rolling research cadence | Useful to prevent symbols from trading before listing, but insufficient to validate historical rolling universe selection. |
| Formal Frozen Evidence | `formal_frozen_gate`<br/>Formal frozen baseline / veto / gate review<br/>status=`superseded_by_monthly_volume_for_historical_claims` | `paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html` | frozen seed with as-of availability<br/>formal gate is causal; original frozen universe selection remains survivorship-risky<br/>cadence=15m rolling research cadence | Keep as formal definition and frozen-gate reference, but do not use it alone as long-history proof after monthly-volume rebuild weakened the result. |
| Deprecated / Risk | `retired_marketcap_rebuild`<br/>Monthly marketcap universe rebuild<br/>status=`retired` | `paper/rank213_largecap_xs_jump_veto_monthly_marketcap_universe_rebuild.html` | retired marketcap proxy<br/>retired; replaced by monthly volume proxy due proxy distortions<br/>cadence=historical exploration | Do not use for current decisions. Kept only as audit trail. |

## 当前关键数值

- `monthly_volume_universe_rebuild`：样本 `2020-02-01T00:00:00Z` 到 `2026-04-10T18:00:00Z`。
- 该口径下旧 Rank213 plain baseline：`-98.09%`。
- 该口径下 baseline + veto：`-99.60%`。
- 该口径下 baseline + veto + fixed gate：`-37.13%`。
- 该口径下 percentile q60 gate：全样本轻微正，但最大回撤仍深，不能视为过关。
- frozen30 固定名单同规则下看起来更强，但它不是滚动历史选池证明。

## 后续开发规则

1. 新功能如果依赖“策略长期有效”，默认必须先引用 `monthly_volume_universe_rebuild` 或更新后的 causal universe 证据，不能只引用 frozen30 或 as-of 页面。
2. 新功能如果只是执行审计、残仓对账、basket parity、systemd 编排，可以引用 live/shadow artifacts，但文案必须写成 execution audit。
3. 页面或报告标题里必须显式包含 universe 口径：`frozen30`、`asof-frozen-seed`、`monthly-volume-causal`、`live-audit` 之一。
4. 任何回测表格必须同时展示 `universe_mode`、`selection_causality`、`cadence`、`sample_start/end`。
5. 下一步再把报告页逐步改为从这些 manifest 读取口径字段。

## Manifest 来源

- `reports/artifacts/rank213_evidence_map/manifests`
