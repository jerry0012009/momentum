# Rank 294 — Coinbase premium impulse × EMA trend alignment × 60m hold：fresh intake 首判 keep_P1

- 时间：2026-04-02 14:21 UTC
- 对象：`research/quant_digests/2026-04-02_1320_coinbase-premium-impulse-ema-alpha.md`
- 执行动作：按当前轮第一条 fresh intake 做 first verdict
- 结论：`keep_P1`，并进入 `Surviving candidate slot`
- 正式 Rank：`294`

## 为什么这轮不是直接升 P2
这条线已经具备独立 raw-alpha 主语，也不是把 repo 的 `130` 维 GA 外壳误当主语：
- 主体很清楚：`Coinbase premium impulse (CPDiff_Zscore) -> Binance/BTC directional continuation`
- filter 很清楚：`EMA` 趋势同向
- exit 很清楚：固定 `60m hold`
- clean-room path 很清楚：Coinbase/Binance 公共 `5m` K 线即可最小复现

但当前证据仍主要停留在：
- 最近约 `30d` 的本地快检；
- 以 `BTC` 为主，尚未回答时间稳定性 / 参数邻域稳定性；
- 成本后可存活迹象主要集中在 `CPDiff_Z + EMA alignment` 这一版，尚未证明不是短样本 pocket。

因此这轮最诚实的 first verdict 不是直接升 `P2`，而是：

> `Rank 294` 已具备独立 directional raw-alpha 主语、明确 `5m/15m` transfer 与最小 cost-aware clean-room path，因此 fresh intake 首判为 `keep_P1`；下一轮 survivor 唯一一次 follow-up 应优先回答“这是不是只靠单点参数和近 30 天样本撑起来的 pocket”。

## 为什么也不是回 P0
它没有被直接打回 background，原因是：
1. 不是空泛 headline：entry / filter / hold / execution path 都明确；
2. 不是纯 repo 叙事：已有最小本地 transfer check；
3. 不只是静态 premium level，而是更有经济解释的 `premium impulse`；
4. 在 digest 给出的最小结果里，`CPDiff_Z + EMA alignment + 60m hold` 在 `4 bps` 单边压力下仍显示成本后存活迹象，足以换一次 survivor follow-up。

## 对 survivor follow-up 的唯一明确问题
下一次唯一便宜检查应聚焦：
- 这条 edge 是否只存在于 `z=2.5 / EMA96 / hold=12` 的窄点位；
- 至少给出一个小邻域（如 `z_window / threshold / hold`）是否仍保留同向、成本后不塌的证据。

若小邻域不稳，默认回 `background/P0`；
若小邻域仍稳，再考虑升 `P2`。

## 本轮写回 runtime 的系统认知
`Rank 294`：`Coinbase premium impulse × EMA trend alignment × 60m hold` 已具备独立 directional raw-alpha 主语、明确 `5m/15m` clean-room path 与成本后存活迹象，因此 fresh intake 首判为 `keep_P1`，进入 survivor 槽位等待那唯一一次参数邻域 / 时间稳定性 follow-up。
