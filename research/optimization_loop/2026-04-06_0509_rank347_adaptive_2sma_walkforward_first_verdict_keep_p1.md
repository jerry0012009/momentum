# Rank 347 / adaptive 2-SMA walk-forward perp trend fresh intake -> keep_P1

- 时间：2026-04-06 05:09 UTC
- 对象：`research/quant_digests/2026-04-06_0357_adaptive-2sma-walkforward-perp-trend-alpha.md`
- 槽位：Fresh intake
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`（进入唯一 `Surviving candidate slot`）

## 本轮为什么给 `keep_P1`
这条对象**虽然仍属于 trend / momentum continuation 家族**，但它和刚被打回 `background / P0` 的 `AdaptiveTrend rolling-Sharpe basket` 不是同一种“包装层”主语：

- `AdaptiveTrend` 那条的新增值主要来自 **rolling Sharpe 选币 + ATR exit + 70/30 allocation**，核心是组合层 / 风控层 / 资产筛选层的 trend packaging；
- 当前这条 `adaptive 2-SMA` 的主语更窄也更原生：**单资产 perp 上的 fast/slow MA 方向切换 + walk-forward 参数刷新**；
- 它不是拿一整套 basket construction 去重新包装旧趋势，而是在问一个更基础、也更值得当前 desk 保留的问题：
  **“在显式成本口径下，单资产 perp 的最朴素趋势壳，是否因 walk-forward + slow-window bias 而仍值得保留为 baseline？”**

这句系统认知和上一条对象是不同的，所以它不是简单重复 intake。

## 为什么它已经足够构成 distinct raw-alpha shell
按 digest 里的现有证据，这条线已经把 3 个前排首判该回答的点压出来了：

1. **独立主语足够清楚**
   - `entry / flip` = `fast_ma > slow_ma` 做多、反向做空；
   - `adaptation` = walk-forward 重选参数；
   - `cost boundary` = 论文与 toy probe 都显式把交易成本放进净收益；
   - 因而它是可单独命名、可当天复刻、可单独 falsify 的 raw alpha 壳，而不只是 overlay。

2. **新增值不只是“又一个 trend 参数调优”**
   - 真正新增信息不是某组 magic windows，而是：
     **参数必须 walk-forward，且短周期 desk 不该默认偏快窗口，反而该先从 slow-window bias 开始。**
   - 这条信息会直接改变后续实验设计，不只是给老 baseline 再补一层修辞。

3. **和当前 desk 的 `15m/5m / after-cost` 口径存在可迁移边界**
   - digest 的 Hyperliquid `5m` toy probe 已经给出一个诚实边界：
     快窗口 in-sample 很亮，但 OOS 易坏；
     `32/192`、`48/192` 这种更慢组合在 `1.5bps/side` 压力口径下反而更稳；
   - 这说明当前对象至少已经压出“先保留为 slow-window baseline，再做 survivor follow-up”的合理前提，而不是一篇只能留作背景阅读的 trend 常识文。

## 为什么这轮还不直接升 `P2`
还不能直接进 `P2`，因为当前证据仍有两个缺口没有补：

1. **cross-asset portability 尚未回答**
   - 现有快检主要还是 `BTC`；
   - `ETH` 或其他高流动大币是否复制 slow-window after-cost pocket 仍未确认。

2. **walk-forward 相对固定参数的 honest advantage 还只停留在 paper 摘要 + toy framing**
   - 现在更像“实验设计方向已清楚”，
   - 还不是“admission 所需证据已成形”。

所以最诚实的落点不是直接升 `P2`，而是：
**先给正式 Rank，保留为唯一 survivor，用那唯一一次 follow-up 去回答 `ETH/BTC × 15m/5m × fixed-vs-walk-forward × slow-window` 是否真的形成可迁移的 after-cost baseline。**

## 会改变系统认知的话
`Rank 347` 不是被打回的 `AdaptiveTrend` 组合包装重复件；它把 `single-asset perp 2-SMA direction + walk-forward parameter refresh + slow-window bias` 压成了一个独立、成本后可定义边界的 trend baseline，因此当前 fresh intake 首判应给 `keep_P1`，并进入唯一 `Surviving candidate slot`。

## 对 runtime 的直接影响
- 当前对象获得正式 `Rank 347`；
- `Fresh intake` 这一步已完成首判；
- `Rank 347` 进入唯一 `Surviving candidate slot`，并保留 **1 次** 决定性 follow-up 预算；
- 后续若 follow-up 不能把 `ETH/BTC × 15m/5m × fixed-vs-walk-forward` 的 after-cost baseline 压清，则按 policy 直接收口，不再拖长。
