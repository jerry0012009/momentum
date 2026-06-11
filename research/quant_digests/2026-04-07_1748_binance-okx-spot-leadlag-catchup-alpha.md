# 别把这份 2025 cross-venue notebook 只读成相关性 EDA：对 short-cycle desk，更该先测的是「Binance spot impulse × OKX delayed catch-up」这条 raw alpha
- 时间：2026-04-07 17:48 UTC
- 类型：GitHub repo / notebook source audit
- 主题类型：raw alpha
- 基础 alpha：同一标的在跨所之间存在**非对称秒级 lead-lag**；当 Binance 现货先走出显著冲击、而 OKX 还没完全跟上时，做 OKX 方向性 catch-up。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：cross-venue / lead-lag / same-underlier / spot / event-time / microstructure / 1m / 3m / binance / okx / btc
- 证据类型：工程经验 / notebook 内嵌结果

## 1. 这次看了什么
这次主看 GitHub 仓库 **`ybektas20/crypto_ll`** 里的 `eda.ipynb`。它不是完整交易系统，而是一份把 **Binance BTCUSDT 现货/永续** 与 **OKX BTC-USDT 现货/永续** 逐笔成交对齐后，直接做跨所 lead-lag 相关性扫描的 notebook。仓库保存了输出，不只是空代码：样本覆盖 `2025-06-03` 到 `2025-06-04`，Binance perp 样本约 `218,756` 笔，OKX spot / perp 分别约 `308,461` / `577,663` 笔，OKX 内部 spot+perp 对齐后约 `1,464,400` 行。

## 2. 核心结论
- **一句话核心结论：** 这份材料最值钱的不是“两个所很相关”，而是 **领导权不对称**：在它的样本里，`Binance spot -> OKX spot` 的领先强于反方向。
- notebook 直接给出的 lag-scan 结果里，`spot_binance_spot_okx_corr` 的**最大相关系数约 `0.4332`，出现在 lag=`17`**；反方向 `spot_okx_spot_binance_corr` 的**最大相关仅约 `0.3387`，出现在 lag=`19`**。
- 该 notebook 还给了时间尺度：按 `timestamp.diff(21)` 统计，**21 个对齐观测点平均约 `2.61s`**，中位数约 `2.06s`。也就是说，这里最该关注的不是 15m，而是 **秒级到 1m 内** 的跟随补价 pocket。
- **一句话证明方式：** 它是靠**逐笔成交对齐 + 滞后相关扫描**把这个判断撑起来的，不是靠主观“看图觉得谁先谁后”。
- notebook 还画了 rolling correlation，这提醒我们：这不是恒定不变的机械边，而更像**可切换的微观结构 regime alpha**，需要领导权强度过滤。

## 3. 为什么和当前项目有关
这条线和我们最近积累的 `pairs / funding / basis` 不同：它是更短、更“原始”的 **same-underlier cross-venue lead-lag raw alpha**。对当前 desk 有两层价值：
1. 直接扩充 `1m / 3m` 高强度素材池，不必再把跨所只读成静态价差回归；
2. 以后还能反哺已有 `XEMM / quote-gap-close / maker-taker hedge` 壳，作为**领导权 admission** 或 **no-chase veto**。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 跨所 lead-lag directional
- 基础 alpha：**Binance 现货短冲击领先，OKX 同标的延迟补价**
- regime：仅在 `leader-follower` 相关仍稳定、两所价差未被费用吃掉、且事件窗口内 Binance 仍是 leader 时启用
- filter / veto：低流动性时段禁做；若 follower 已完成大部分补价、或两所方向同时剧烈反转，则 veto
- risk / sizing / execution overlay：仓位按 leader 冲击强度与 follower 未补价幅度缩放；默认极短 time-box；优先 maker on follower / taker 只在 edge 明显覆盖手续费与冲击时使用

## 4. 可复刻的最小实验
- **研究假设：** 当 Binance BTC 现货在最近 `3s~10s` 内出现显著单向冲击，而 OKX BTC perp/spot 同窗仍落后时，OKX 后续 `3s~30s` 有同向补价。
- **一个可计算定义：**
  - `leader_impulse = ret_binance_spot_{3s}`
  - `follower_gap = ret_binance_spot_{3s} - ret_okx_perp_{3s}`（或 `- ret_okx_spot_{3s}`）
  - 仅当 `|leader_impulse| > z1` 且 `follower_gap` 与 `leader_impulse` 同号、并且 gap 超过费用门槛时开仓。
- **最小回测切口：** BTC，Binance + OKX 公共逐笔成交；先做 `1s / 5s / 15s` 聚合，再降到 `1m` 检查是否还剩可迁移边；样本先取 7~30 天。
- **entry / exit / sizing / risk / cost：**
  - entry：leader 冲击确认后的下一秒在 follower 侧入场；
  - exit：`3s / 10s / 30s` time-box 或 gap 收敛 `50%~80%`；
  - sizing：按 `gap / realized short-horizon vol` 缩放，单笔不超过盘口可吃深度阈值；
  - risk：若 leader 在持仓期内反转、或 follower 先走过头，则立即平；
  - cost：必须显式计入 maker/taker、滑点、跨所时钟偏差与网络延迟。
- **最该先看哪 1~2 个指标：** `post-cost bp/trade`、`edge-after-latency`；其次看 `hit rate within 10s`。

## 5. 风险与保留意见
- notebook 证据强在**方法清楚、结果直给**，弱在它还不是 production backtest：没有完整 fill model、没有手续费/滑点/排队位置。
- 这条边很可能对**延迟和时钟同步**极敏感；如果我们拿不到足够快的公共数据或执行路径，alpha 会迅速塌缩成解释型现象。
- 当前保存输出主要展示的是 **spot 对 spot** 的领导关系；把它迁到 `spot -> perp` 或 `perp -> perp`，必须重新做 clean replication，不能偷推。
- 如果把它硬拉到 `5m / 15m`，大概率会被均值化掉；更诚实的定位是 **`1s~1m` 微结构 raw alpha**，或作为更慢策略的 execution/confirmation 组件。

## 6. 来源
1. **ybektas20 (2025). _crypto_ll_. GitHub repository.**  
   - Authors / Year / Title / Venue：`ybektas20` / 2025 / *crypto_ll* / GitHub  
   - Readable URL：`https://github.com/ybektas20/crypto_ll`  
   - Repo URL：`https://github.com/ybektas20/crypto_ll`
2. **Notebook:** `eda.ipynb`  
   - Raw URL：`https://raw.githubusercontent.com/ybektas20/crypto_ll/master/eda.ipynb`
3. **Repo metadata sanity:** GitHub repo description = `researching the lead-lag relationships between okx and binance for spot and perps`，最近 push 时间为 `2025-06-06`。
