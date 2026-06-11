# bot3 optimization loop — Bollinger RSI vol-target mean reversion first verdict -> background/P0

- Time: 2026-04-25 00:07 UTC
- Target: `research/quant_digests/2026-04-24_2015_bollinger-rsi-voltarget-meanrev-shell.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this changed system belief
`Bollinger band 极端偏离 × RSI 同向确认 × realized-vol 缩放` 这条 repo 线目前不能保留到 `P1`：上游源码给出的是真实可执行但非常 textbook 的 band-touch + RSI gate + vol-scale 壳，而仓库公开“参考回测”口径主要落在 OU 合成日线/共享 backtester 演示，没有拿出能证明 `5m/15m` 单资产 mean-reversion pocket 在统一成本后独立成立的 artifact。

## Minimal decisive honesty check
只补了当前最小 blocker：这条 alpha 是否已经留下可独立交易的 after-cost single-asset mean-reversion pocket，而不是停在指标叠加叙事。

### 1. Strategy source confirms the live logic is plain indicator stack
上游 `mean_reversion_crypto.py` 的硬信号只有：
- `close <= lower_band and RSI < 30` 做多
- `close >= upper_band and RSI > 70` 做空
- 强度 = `abs(close - mid) / (upper - lower)`，截断到 `[0,1]`
- 仓位再乘 `target_vol / realized_vol`

这说明它确实是可运行策略壳，但 alpha 本体仍只是典型 `Bollinger touch + RSI extreme + vol targeting`，没有额外证明某个 crypto short-cycle pocket 的独立新信息。

### 2. Public backtest evidence is not the required desk pocket evidence
上游 `crypto_backtest_report.py` 暴露的“全策略回测报告”关键口径是：
- 用 `Ornstein-Uhlenbeck` 过程模拟 `BTC/ETH/SOL` **180 天日线数据**；
- 把该 Bollinger 策略与其他 crypto 策略一起跑共享 `run_crypto_backtest`；
- 输出的是日频汇总表/Sharpe/MaxDD/年化等排名。

这类演示说明“代码可跑”，但不能回答本 desk 当前 blocker：
- 没有 `15m` 主信号、`5m` 执行的真实 pocket artifact；
- 没有统一 friction ladder 下的单币/多币 after-cost 结果；
- 没有证明 edge 不是 OU 模拟均值回归环境自带的 lucky fit；
- README 也只宣称 `intraday / Bollinger reversion`，没有附上独立可核对的 crypto perp pocket 结果页。

### 3. Therefore first verdict must close as P0
按当前 cycle plan 的成功条件，只有当至少一个非单资产、非单 friction 档位 lucky-run 之外的 after-cost mean-reversion pocket 明显成立，且新增价值不只是 textbook RSI/Bollinger 组合，才允许 `keep_P1`。

这次最小 honesty check 没有拿到该证据，所以应直接收口为 `background/P0`，避免把一个“可运行但未证明 pocket”的 repo 壳继续占用 survivor/front-slot 资源。

## Runtime writeback summary
- `Fresh intake slot.latest_result` 更新为本 verdict
- `Fresh intake slot.source_record/latest_result_record` 指向本 intake 与本日志
- `cycle_plan` 第 2 项写成 `done`

## One-line result
`Bollinger RSI vol-target mean reversion` first verdict 直接收口 `background/P0`：上游公开证据只证明了可运行的 textbook band-touch + RSI + vol-scale 壳与 OU 合成日线参考回测，未留下统一成本后可独立成立的 `5m/15m` 单资产 mean-reversion pocket artifact。

## Tail-step status (non-blocking)
- Homepage refresh tail step `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终被 `SIGKILL` 终止（exec session: `young-basil`）。按 policy 归类为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知步骤已独立执行并成功发送。