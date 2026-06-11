# 别把这份 perp-calendar repo 只读成“carry 公式作业”：对 short-cycle crypto desk，更该先回答的是「annualized basis spread 偏离 × perp-vs-quarterly 回归」这条 raw alpha 壳到底够不够厚
- 时间：2026-04-21 12:45 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当 perpetual 与季度合约之间的年化 basis 偏离自身短窗中枢过大时，做 **long cheap leg / short rich leg**，赌 basis spread 向中枢回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 first verdict 偏弱）
- 主题标签：relative-value / stat-arb / carry / basis / perp-vs-calendar / annualized-basis / mean-reversion / Binance USDⓈ-M / 5m / 15m / repo / public-data
- 证据类型：工程经验 + repo rule shell + public-data first probe

## 1. 这次看了什么
这次看的是 2024 GitHub repo **joseamador0898 / hex_assesment**。repo 前半部分是 order-book streaming 小作业，真正和 desk 更相关的是 README 后半段：它把一条 **perpetual funding vs calendar implied rate** 的 relative-value 交易思路直接写出来了。

它的 base alpha 不复杂：
- 用 perp 这一腿代表浮动 funding / short-dated carry；
- 用季度合约这一腿代表更慢的到期 basis / implied financing；
- 当两者之间的 spread 偏离过大，就做 convergence。

对我们更有价值的读法，不是把它当“利率公式练习”，而是当成一条 **可直接写成 `entry / exit / sizing / cost` 的 raw alpha 壳**：
> **short-cycle 上真正能不能做，不取决于你懂不懂 carry，而取决于 basis spread 的短窗偏离有没有厚到足以盖过两腿摩擦。**

## 2. 一句话核心结论
这条 perp-vs-calendar basis 回归思路 **方向上是合理的 relative-value raw alpha**，但在 Binance USDⓈ-M 的 `BTC/ETH` `5m/15m` 最小实验里，当前看到的 **单笔 gross 只有 `1~2 bps` 量级，明显太薄**，如果按双腿 round-trip 粗扣 `8 bps`，整体就是负的。

## 3. 它是怎么证明这点的
不是靠空讲 carry，而是直接用 Binance 公开合约 K 线，把 `perp` 与 `2026-06-26` 季度合约的 **annualized basis** 做 rolling z-score，按 `|z|>=2` 入场、`zero-cross or timeout` 出场，统计实际每笔 spread-trade 的 gross / net bps。

## 4. 核心结论展开
- 这篇东西的 **base alpha 是清楚的**：`perp-vs-calendar basis mean reversion`，属于 relative-value / stat-arb / carry 家族，不是 filter。
- 它也确实能落成完整策略骨架：
  - signal：年化 basis 偏离
  - position：long cheap leg / short rich leg
  - exit：回归到中枢或 time-stop
  - sizing：双腿等名义或 beta-neutral
  - risk：basis 继续扩张、临近交割、单腿滑点、资金费率跳变
- 但这轮 portability probe 给的 first verdict 比较冷：
  - `15m`，`BTCUSDT vs BTCUSDT_260626`：`141` 笔，gross `+1.33 bps/笔`，net `-6.67 bps/笔`
  - `15m`，`ETHUSDT vs ETHUSDT_260626`：`174` 笔，gross `+2.20 bps/笔`，net `-5.80 bps/笔`
  - `5m`，`BTCUSDT vs BTCUSDT_260626`：`373` 笔，gross `+1.84 bps/笔`，net `-6.16 bps/笔`
  - `5m`，`ETHUSDT vs ETHUSDT_260626`：`500` 笔，gross `+2.14 bps/笔`，net `-5.86 bps/笔`
- 连把入场阈值提高到 `z>=3~4`、或把 timeout 拉长，这轮样本里也没翻正，说明问题不是“参数没抠对”，而更像是：
  - 这条 basis spread 本身在短周期上 **会回，但回得不够猛**；
  - 或者说它更适合做 **低频 carry / inventory overlay**，而不是 `5m/15m` 的主交易信号。

## 5. 为什么它仍然值得进研究池
尽管当前结果偏弱，这个题目还是值得保留，因为它补的是我们素材池里一个还不够系统化的 raw alpha 家族：
- 不是单资产方向，而是 **同一 underlier 不同期限之间的 financing spread**；
- 不是资金费率排行榜，而是 **期限结构里“慢 carry vs 快 carry”的相对扭曲**；
- 如果后续能接入更细的 mark / premium / funding / order-book 微观数据，它有机会从“太薄的 standalone alpha”变成：
  - carry 策略的 **entry timing layer**
  - delta-neutral inventory 的 **deploy / unwind overlay**
  - basis / funding 宽度异常时的 **risk-on / risk-off gate**

## 6. 策略拆解
- 方向属性：relative-value / stat-arb / carry / basis mean reversion
- 基础 alpha：perp 与季度合约之间的年化 basis 扭曲回归
- signal：`annualized_basis = (calendar / perp - 1) * 365 / ttm_days`，再做 rolling z-score
- entry：`z >= +2` 做空 calendar、做多 perp；`z <= -2` 反向
- exit：`z` 过零或 fixed timeout
- sizing：双腿等名义；若后续做更严谨版，可改成 DV01 / funding-beta / liquidity-aware sizing
- 主要风险：交割临近导致 basis 机械收敛、perp funding regime 切换、两腿流动性不对称、单腿先成交后的 exposure 裸露

## 7. 可复刻的最小实验
### 数据源
- Binance USDⓈ-M 公开 K 线
- 标的：`BTCUSDT / BTCUSDT_260626`、`ETHUSDT / ETHUSDT_260626`
- 公开性：公开可得，无需私有权限
- 更新频率：K 线分钟级；这轮实验用 `5m / 15m`

### 最小实验口径
1. 拉最近 `45d` 的 perp 与 quarterly 合约 K 线；
2. 计算 `annualized basis`；
3. 做 rolling z-score；
4. `|z|>=2` 入场，`zero-cross or timeout` 出场；
5. 统计 spread-trade 的 `gross/net bps`；
6. 做 `z=2/2.5/3/4` 与 `timeout` 网格敏感性。

## 8. 这轮我保留的判断
这条线 **可以算 raw alpha 候选**，但当前不该被高估。它最像的是：

> **概念上正确、工程上清晰、但在 `5m/15m` 上太薄，不够当 standalone 主信号；更适合往 carry / basis 组合层或 execution-timing 层迁移。**

换句话说，repo 值得学的是它的 **相对价值框架**，不是当前这版信号强度。

## 9. 下一步怎么测
- 把 `BTC/ETH` 扩到更多有季度合约的 liquid names，看是不是只有 majors 太有效率。
- 不只看 close-to-close basis，补 **mark / premium index / funding history**，改成更贴近 repo 原意的 `perp funding - calendar implied rate` 真 spread。
- 做 **event-conditioned** 版本：只在 funding 跳变、basis 突扩、或合约换月前后测试，不要默认全天候都交易。
- 如果后续仍然太薄，就把它正式降级为 **overlay / timing layer**，不要继续把它当主 alpha 炼丹。

## 10. 来源
- Jose Amador? / GitHub user `joseamador0898` (2024), **Hex Assessment - Quantitative Trading and Development**. GitHub repo. Repo URL: <https://github.com/joseamador0898/hex_assesment>
- Readable README URL: <https://raw.githubusercontent.com/joseamador0898/hex_assesment/main/README.md>
- Source audit 文件：`README.md`, `webstream_data.py`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/perp_calendar_summary_all_2026-04-21.csv`
  - `reports/artifacts/quant_digests/perp_calendar_summary_15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/perp_calendar_summary_5m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/perp_calendar_trades_15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/perp_calendar_trades_5m_2026-04-21.csv`
