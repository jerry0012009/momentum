# 外部参考价锚定 × 分层 spread-capture maker shell（OctoBot Market Making, 2026）
- 时间：2026-04-12 18:30 UTC
- 类型：GitHub repo / strategy docs source audit
- 主题类型：raw alpha
- 基础 alpha：`用更液体 venue 的 reference price 当 fair value，在本地 venue 围绕它维持多层 bid/ask 去吃 spread + 回摆；当 reference price 漂移、挂单缺失或成交后立即重构挂单簿，尽量少把逆向选择白送给搬砖者`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / maker / market-making / reference-exchange / fair-value / spread-capture / liquidity-provision / inventory / cross-venue / order-book / 1m / 3m / 5m / 15m
- 证据类型：repo source audit + strategy docs

## 1. 这次看了什么
这次主看的是 `Drakkar-Software/OctoBot-Market-Making`，但真正有研究价值的不是它的营销 README，而是它在 `Drakkar-Software/OctoBot` 主仓里那套可读源码：`packages/tentacles/Trading/Mode/market_making_trading_mode/*`。这题之所以值得进池，不是因为它“又是一个做市框架”，而是因为它把 **base alpha 讲清楚了**：

> **不是** 预测 5m/15m 方向，**而是** 用更液体外部市场给本地盘口一个 fair-value 锚，然后靠多层被动挂单去吃 local oscillation / spread capture；reference price 一旦漂移到让现有 bid/ask 失真，就撤改单重建，减少被跨所搬砖者摘走的逆向选择。

换句话说，这不是 `mm-live` 那种 **OFI -> next-few-second drift** 的预测型 maker alpha；它更像 **reference-exchange anchored liquidity provision**：把“公允价锚定 + 分层深度分布 + 成交后自动补回 + 过期单撤换”做成一套完整壳。

## 2. 核心结论
- 这题我认为可以诚实归进 **raw alpha**，因为它的 alpha 本体不是 inventory 管理，也不是风险覆盖层，而是：**本地价格会围绕更液体 venue 的 fair value 回摆，maker 只要持续把报价带贴着 reference price 重建，就能重复吃 spread / micro-reversion**。
- 这套 repo 给出的不是空壳，而是比较完整的可落地逻辑：
  - 默认配置就是 `3` 档 bid + `3` 档 ask，`min_spread=2`、`max_spread=10`、`reference_exchange="local"`；
  - 文档明确写了：当 reference price 改变、订单被成交/取消、或订单簿已不再符合配置时，会自动调整；若需要整本替换，会 **one by one cancel**，尽量避免出现空簿；
  - 资金使用上，策略会使用可用资金，但上限不是无限开，而是 **最多覆盖目标交易对日成交量的 `2%`，且只覆盖 order-book 前 `3%` 深度内所需库存**。
- 从源码看，触发条件非常直接：
  - `on_new_reference_price()` 会检查：是否缺少任一侧挂单；或者 **最高买单已经高于 reference price**；或者 **最低卖单已经低于 reference price**。只要出现这些失配，就触发 `_ensure_market_making_orders()` 重建挂单。
  - `_mark_price_callback()` 订阅参考交易所价格更新；`order_filled_callback()` 在订单成交后也会立刻触发一次补单/重建。
- 对我们 desk 真正有价值的旁支想法，不是照搬它默认的 `%` 级宽价差，而是 **把它的结构迁到更短、更窄、更 desk 化的 bp 级 maker 壳**：
  - reference venue：Binance / Bybit / Hyperliquid 这类更液体市场；
  - local venue：流动性更薄、但 maker fee / rebate 或 spread 更肥的 venue / 合约；
  - quote policy：3x3 或 5x5 分层挂单，但 spread 改成更现实的 `8~80 bps` 区间，而不是 README/默认配置里的 `%` 级粗尺度。

## 3. 为什么和当前项目有关
这题不是当前阶段最优先的 `pairs / stat-arb / carry` 新论文，但它仍然值得本轮作为新 digest，原因很简单：
- **不重复**：我在现有 digest 里没检到 `OctoBot` / `reference exchange` / 这套 `market_making_trading_mode`；
- **base alpha 清楚**：不是“做市框架”这种空话，而是 **外部 fair value 锚定下的被动 spread capture**；
- **能直接落地完整策略**：entry / refresh / sizing / order count / depth budget / stale replacement / fill callback 都已有明确壳；
- **和当前素材池互补**：
  - 我们已经有 `OBI/OFI` 一类 **预测型 maker alpha**；
  - 这题补的是 **锚定型 maker alpha**：不先赌几秒 drift，而是先保证自己别偏离更液体市场的公允价太远。

所以它更像给 maker 方向补一条和 `OBI × skew`、`OFI × fair value shift` 并列的第二主线：**external fair-value anchoring**。

## 3.5 策略拆解（必填）
- 方向属性：中性偏 liquidity provision / spread capture，不是 bar-close directional trend model
- 基础 alpha：`local venue quotes revert around liquid-venue fair value -> passive ladder around reference price captures spread and local mean reversion`
- regime：适合价差能覆盖手续费、且 local venue 明显比 reference venue 更薄、更慢、更容易回摆的市场
- filter / veto：
  - reference feed 失效 / 过时；
  - local spread 窄到覆盖不了 fee；
  - 本地盘口跳空、缺档或取消率异常；
  - inventory 接近上限时只补单不扩仓，或只挂减仓侧
- risk / sizing / execution overlay：
  - `bids_count / asks_count`
  - `min_spread / max_spread`
  - 预算上限：`min(组合预算, 覆盖日成交量 2% 且只看前 3% 深度所需库存)`
  - order refresh on `reference update / filled order / missing orders / stale book`
  - full replacement 时逐笔撤单，避免一瞬间空簿

## 4. 可复刻的最小实验
**研究假设**：在更薄的本地市场上，只要参考更液体 venue 的 fair value 重建多层报价带，哪怕不显式预测未来几秒方向，也能比“只用本地 mid 静态挂网格”拿到更好的 fill-adjusted net edge。

**最小定义**：
1. 选一组同币对、双 venue：
   - reference：Binance / Bybit / Hyperliquid 之一；
   - local：Gate / MEXC / Bitmart / 某个薄一些的 perp 或 spot venue。
2. 每 `250ms~1s` 更新一次 external reference mid（或 mark price）。
3. 在 local venue 维护 `3x3` 或 `5x5` ladder：
   - 内层 spread：`8~20 bps`（液体 perp）或 `20~40 bps`（薄 alt）；
   - 外层 spread：`30~80 bps` 或更宽；
   - 价格分布用 inside-out 均匀层或轻度递增层。
4. 触发刷新：
   - 缺少某侧挂单；
   - best bid 已高于 reference；
   - best ask 已低于 reference；
   - 或 reference 漂移超过首层半价差的一定比例。
5. 预算：
   - 先做缩尺版：每侧固定 notional；
   - 再做 repo 风格版：不超过当日目标市场成交量 `2%`、且库存只覆盖前 `3%` 深度。

**最该先看**：
- `fill-adjusted net bps`
- 成交后 `1s / 5s / 30s` markout
- `inventory half-life`
- `cancel/replace per minute`
- `empty-book seconds`

**和当前短周期框架怎么接**：
- `1m / 3m`：这是主评估周期，最能看出 maker alpha 是否真实存在；
- `5m / 15m`：不要把它硬翻成 15m 裸方向信号，而应把这两个周期主要用于 **regime gating**（波动、价差、流动性、inventory unwind 节奏）。

## 5. 风险与保留意见
- 这题的 edge 强依赖 **本地 venue 比 reference venue 更慢 / 更薄**。如果两边都同样高效，alpha 很容易退化成“只是挂单管理更整齐”。
- repo 默认 `min_spread=2`、`max_spread=10` 看起来更像 `%` 级展示配置；对我们 desk 的主战场，这个默认值太粗，必须缩到更现实的 bps 尺度。
- 这类策略最怕 **queue position / hidden liquidity / cancel latency / maker rebate 变化**。如果没有 fill simulator，只看 mid-price 回摆，纸面 edge 会被高估。
- 它虽然能归进 raw alpha，但和 `OFI -> drift` 不一样：这里的 alpha 更像 **reference-price anchored passive edge**。如果用户只接受“显式预测未来方向”的 raw alpha，会更愿意把它叫作 `complete maker shell`。

## 6. 下一步怎么测
1. 先做 `reference=Binance, local=Gate/Bitmart/MEXC` 的双 venue 回放器；
2. 只测 `BTC / ETH / SOL + 2~3 个薄一点的 alt perp`，别一开始铺太宽；
3. 做三组对照：
   - A：local-mid anchored static ladder
   - B：external-reference anchored ladder（本题）
   - C：external-reference + inventory skew / OBI veto
4. 先别追求复杂 shape，先看 B 是否已经明显优于 A；若没有，就别往上叠更复杂 alpha。

## 7. 来源
- Drakkar-Software. (2026). *OctoBot*. GitHub.
  - Repo URL: `https://github.com/Drakkar-Software/OctoBot`
  - GitHub metadata：`updated_at = 2026-04-12T18:17:26Z`
  - 关键文件：
    - `packages/tentacles/Trading/Mode/market_making_trading_mode/config/MarketMakingTradingMode.json`
    - `packages/tentacles/Trading/Mode/market_making_trading_mode/reference_price.py`
    - `packages/tentacles/Trading/Mode/market_making_trading_mode/order_book_distribution.py`
    - `packages/tentacles/Trading/Mode/market_making_trading_mode/market_making_trading.py`
    - `packages/tentacles/Trading/Mode/market_making_trading_mode/resources/MarketMakingTradingMode.md`
- Drakkar-Software. (2026). *OctoBot-Market-Making*. GitHub.
  - Repo URL: `https://github.com/Drakkar-Software/OctoBot-Market-Making`
  - GitHub metadata：`updated_at = 2026-04-09T10:28:58Z`
- 关键源码/文档要点（本次 audit 用到）：
  - 默认配置：`asks_count=3`、`bids_count=3`、`min_spread=2`、`max_spread=10`、`reference_exchange="local"`
  - 文档行为：reference price 变化、订单成交/取消、订单簿过期时自动更新；full replacement 会逐笔撤单；预算上限为目标市场日成交量 `2%` 且只覆盖前 `3%` 深度
  - 触发逻辑：`buy max > reference_price` 或 `sell min < reference_price` 或订单缺失时，触发重建；订单成交后也会立刻补单
