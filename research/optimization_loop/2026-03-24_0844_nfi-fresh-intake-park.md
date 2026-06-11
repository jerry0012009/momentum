# bot3 optimization loop — NFI fresh intake park

- Time: 2026-03-24 08:44 UTC
- Path: Scout
- Claimed action: `Next 3 bot3 runs` #1 — 重开 fresh intake
- Candidate: `NostalgiaForInfinityX / iterativv` repo-based fresh intake（5m crypto dip-buy + trend filter multi-condition strategy）
- Sources:
  - README: https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/README.md
  - Strategy: https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/NostalgiaForInfinityX.py

## Why this was the highest-leverage fresh intake
1. 近 5 年仍在维护，公开 repo 可直接取到规则骨架。
2. 明确写死 `5m` crypto、稳定币交易对、40~80 pair universe，和 desk 当前 `1m/3m/5m/15m` 最小实验窗口兼容。
3. 如果它能压成 clean-room skeleton，就会是一个和当前 EMA / breakout / trendline 体系不同的 `multi-condition dip-buy continuation` 原型；如果压不成，也能快速诚实淘汰。

## Minimal intake facts
- README 明写：
  - 策略运行在 `5m`。
  - 推荐 `40~80` 个稳定币交易对。
  - 依赖 `use_exit_signal=true`、`ignore_roi_if_entry_signal=true` 等 Freqtrade 运行设定。
- `NostalgiaForInfinityX.py` 显示：
  - `timeframe = "5m"`
  - `startup_candle_count = 480`
  - `minimal_roi = {"0": 100.0}`、`stoploss = -0.99`
  - `position_adjustment_enable = True`
  - 大量条件开关：`buy_condition_1_enable` 一直到 `buy_condition_74_enable`
  - 同时混入大量保护层 / rebuy / hold support / pairlist / informative timeframe 逻辑

## Desk-style honest read
### 可取之处
- 它确实不是一句口号；repo 里有完整、可运行的交易骨架。
- `5m`、crypto、公开代码，这三点让它满足“可独立复现”的最低门槛。

### 致命问题
1. **不是干净 raw alpha，而是厚重执行壳 + 条件堆叠包。**
   - 74 个买入条件开关、rebuy、hold support、pairlist 依赖、informative TF 混在一起，无法在本轮被诚实压成一个清晰主因果。
2. **高度依赖组合层设置，不适合作为当前 fresh intake 主资源。**
   - 40~80 对稳定币 universe、多开仓位、无限 stake、特殊 exit 选项，本质更像“组合配置模板”，不是单策略原子层。
3. **风险控制参数暴露出强烈的‘先活下来再说’壳层味道。**
   - `minimal_roi = 100%` + `stoploss = -99%` + hold/rebuy 组合，使得单 trade alpha 与执行/持仓管理纠缠过深。
4. **无法在一轮内压成 desk 想要的最小可验证 5m/15m clean replication。**
   - 若继续做下去，下一步不会是“最小诚实验证”，而会滑向拆条件、选子模块、调组合，这违背当前 policy 的 fresh intake 目标。

## Hard verdict
`park`

## One-line result for desk
`NostalgiaForInfinityX` 虽然是近 5 年仍活跃、5m crypto 可运行 repo，但它本质上是 74 条买入条件 + rebuy/hold/pairlist/execution shell 的厚重组合模板，不能诚实压成当前 desk 需要的单一 clean-room raw alpha，因此 fresh intake 当轮直接 `park`。

## Short scorecard
- reproducible public source: 4/5
- causal clarity: 1/5
- direct fit for 5m/15m minimal experiment: 1/5
- risk of overfitted execution shell: 5/5
- verdict: `park`

## Delivery / next implication
- 本轮完成了 `1 主点 + 1 紧邻子点`：
  - 主点：认领一条新的 repo-based fresh intake
  - 紧邻子点：直接给出是否 `keep_P1` 的最小 honest verdict
- 因为结论是 `park`，按顶板规则，下一轮应继续打开 **新的 fresh intake**，而不是续磨这条 repo。
