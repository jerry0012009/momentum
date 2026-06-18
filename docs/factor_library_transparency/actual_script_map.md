# 因子库真实执行链路与脚本地图

> Phase 12D-G-R · 研究解释页

## 一句话总览

这页不是代码目录，也不是全部脚本列表。它只解释当前因子库主链路中真正相关的脚本，以及哪些脚本属于其他 momentum 功能。

## 11 个执行链路分区

1. **数据下载与缓存** — Binance USDT perpetual 1h K线
2. **Universe 构建** — Top50 by previous month quote_volume，PARTIAL survivorship bias
3. **Bars 过滤与标准化** — full cache → filtered by universe
4. **Factor Values 计算** — build_factor_values / batch / crypto_native
5. **Forward Return Labels** — 1h/4h/24h/72h close-to-close
6. **Signal Panel 构建** — 不是回测/交易/paper trade
7. **Signal Evaluation 协议** — 10A/10A-R/10B/10C/10D
8. **Cost / Liquidity / Capacity** — 不是最终交易回测
9. **Paper Signal / Rolling Monitoring** — 不是定时任务，不是 future paper trade
10. **Transparency Docs / Showcase** — Apache 直接服务，不需要 publish 脚本
11. **其他 momentum 功能** — NOT_FACTOR_LIBRARY_MAINLINE

## Survivorship Bias

PARTIAL mitigation — dynamic universe 包含后来退市的 symbol 在其活跃月份的数据，但无显式 delisted/PIT 数据完全验证。

## Not for production use.
No real execution. No alpha claim. Phase 13 NOT STARTED.
