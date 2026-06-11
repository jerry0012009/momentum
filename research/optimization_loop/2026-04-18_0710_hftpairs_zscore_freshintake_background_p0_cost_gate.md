# 2026-04-18 07:10 UTC — half-life bounded pairs z-score fade fresh intake -> background/P0

## 执行动作
- 对 `research/quant_digests/2026-04-17_1556_hftpairs-zscore-halflife-shell.md` 执行当前轮最前的 pending 小点。
- 只回答这条 `half-life bounded pairs z-score fade` 是否值得作为新的 pairs/stat-arb front object 保留，并补 1 个最小 honesty / execution realism blocker。

## 本轮使用的现成证据
- Digest 已给出 public-data portability probe：
  - aggregate `4,646` 笔
  - `gross_avg_per_trade ≈ +4.24bps`
  - cost ladder：`8bps -> -3.76bps/trade`，`12bps -> -7.76bps/trade`，`20bps -> -15.76bps/trade`
- pair-level gross：
  - `LINK/SOL +2.98bps`
  - `ENA/XRP +3.72bps`
  - `AXS/FIL +6.04bps`
- 额外 honesty blocker 直接采用 digest 已明确暴露的 repo admission 缺口：`optimizer.py` 在“找不到正收益参数”时仍会把默认参数写进 `strategies.json`，因此当前可运行 pair 集合并不等于 admission passed 的可交易 pair 集合。

## 结论
`half-life bounded pairs z-score fade` 当前不值得保留为新的 front object，直接收口 `background/P0`。

## 为什么直接收口
1. **成本门槛先天压不过去。**
   当前 aggregate gross 只有 `+4.24bps/trade`，低于本轮 success criterion 指定的双腿 `8/12/20bps` 成本阶梯；一旦进入最宽松的 `8bps` round-trip，组合已转成 `-3.76bps/trade`。
2. **pair-level 也没有留下可独立承接的 survivor pocket。**
   三组 pair 的 gross 单笔都低于 `8bps`，说明即便只挑当前公开 probe 里最好的 `AXS/FIL`，也仍需要强执行假设才能存活，不能诚实地把它当作新的 queue-facing survivor。
3. **唯一最小 honesty blocker 已经足够决定 verdict。**
   repo 自身存在 `no-profitable-params -> 默认参数照样落地` 的 admission 风险；在 gross 本就低于最低成本梯度时，这个 admission 缺口只会放大伪可行 pair，不能把结论从 `background/P0` 翻成 `keep_P1`。

## runtime-impact sentence
`half-life bounded pairs z-score fade` 的公开可迁移证据只保留 `+4.24bps/trade` 的薄 gross，`8/12/20bps` 双腿成本后整体转负，且 repo 还存在 `no-profitable-params` 默认兜底 admission 缺口，未留下可独立承接的 survivor pair pocket，因此本轮 fresh intake 直接收口 `background/P0`。
