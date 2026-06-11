# 别把这份 Deribit×OKX 期权仓只读成“跨所搬砖”：对 short-cycle crypto desk，更该先拆的是「同标的同到期同 strike 的 quote gap capture」这条 raw alpha 壳
- 时间：2026-04-22 03:53 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：同一 BTC 期权合约在 Deribit 与 OKX 之间的 bid/ask 错价回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：relative value / options / cross-venue / quote-gap / maker-first / hedge / cost / risk
- 证据类型：工程经验 + 公开数据

## 1. 这次看了什么
读了 `Hudie/crypto_algo_trading` 里的 `strategy/catch_gap.py`，再用 Deribit 与 OKX 公共期权 ticker 做了一个 BTC 期权同合约跨所快检。

## 2. 核心结论
- 这份代码不是只会“报价提醒”，而是完整写了：开仓阈值、双腿对冲、post-only、撤单、余额检查、单笔上限。
- 1 分钟左右的 live snapshot 里，492 个可匹配合约对中，约 6~12 个出现正向 quote gap；但 >0.25% 的极少，>0.5% 也只有少数，>1.0% 几乎没有。
- 所以它更像“能跑的跨所期权价差壳”，不是常态厚边机器；真正值钱的是它把 entry / hedge / cancel / size 讲清楚了。

## 3. 为什么和当前项目有关
它能直接补 `momentum` 的 `relative value / options / cross-venue` 素材池，也提醒我们：短周期 desk 里，quote gap 有时比方向更重要，但必须先过手续费与对冲深度。

## 3.5 策略拆解（必填）
- 方向属性：相对价值
- 基础 alpha：同一期权合约跨 venue 的 bid/ask 错价
- regime：只做可成交、合约重叠、剩余期限还够的合约
- filter / veto：价差阈值、腿深度、余额/风险上限、gap 消失即撤单
- risk / sizing / execution overlay：双腿先后对冲、post-only、单笔上限、余额约束、取消全部订单

## 4. 可复刻的最小实验
- 假设：Deribit 与 OKX 的同标的同到期同 strike 期权会偶发可交易错价。
- 定义：`gap = best_bid_rich_venue - best_ask_cheap_venue`，只保留 `gap > 0` 的合约对。
- 最小切口：BTC 期权，Deribit vs OKX，当前全链路公共 ticker 快照；先看 1 分钟内 12 次轮询的正 gap 命中率，再测 5m/15m 的持续性。
- 先看指标：`positive gap` 数量、`gap > 0.5bp/1bp` 命中数、以及扣两腿费用后的净边。

## 5. 风险与保留意见
- 这类机会很薄，常态下可能只够做 maker-first，不够做纯 taker。
- 期权腿深度、隐波、希腊值与撮合延迟会迅速吃掉表面 edge。
- 现在的 live 快检只证明“有错价、且壳完整”，还没证明长期净利润。

## 6. 来源
- Hudie. `crypto_algo_trading`.
- Repo URL: <https://github.com/Hudie/crypto_algo_trading>
- Audited files: `strategy/catch_gap.py`, `strategy/deribit_cross_future.py`, `strategy/deribit_cross_remote_future.py`, `strategy/deribit_perpetual_n_future_arb.py`
- Public data: Deribit / OKX option tickers
- Probe artifact: `reports/artifacts/quant_digests/2026-04-22_deribit_okx_option_gap_probe_summary.csv`
