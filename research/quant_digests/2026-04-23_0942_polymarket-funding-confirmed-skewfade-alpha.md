# 别把这个 2026 Polymarket Rust bot 只读成“预测市场多策略拼盘”：对 short-cycle desk，更该先拆的是「retail skew × funding-confirmed fade」这条可独立落地的 raw alpha

- 时间：2026-04-23 09:42 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/strategies/basis_impl.rs` + repo metadata）
- 主题类型：raw alpha
- 基础 alpha：**跨 venue 相对错价均值回复：当 Polymarket 小时级 YES/NO 隐含概率明显偏向一侧，但 Binance 现货短时并未同向加速、且 perpetual funding 站在反方向时，反做被 retail 挤贵的一侧，赌的是 skew 回归而不是单腿追方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/mean-reversion/polymarket/binance/funding/skew-fade/cross-venue/short-horizon/repo/external-data/cost/risk
- 证据类型：repo source + strategy code + config semantics

## 1. 这次看了什么
这次主看：
- **Michael Bordash (2026), `mbordash/RustPolyBot`**
- Repo URL：<https://github.com/mbordash/RustPolyBot>
- Readable README：<https://raw.githubusercontent.com/mbordash/RustPolyBot/main/README.md>
- Strategy source：<https://raw.githubusercontent.com/mbordash/RustPolyBot/main/src/strategies/basis_impl.rs>
- Repo metadata：public GitHub repo，创建于 `2026-03-22`，最近一次 push `2026-04-22`
- License：GPL-3.0

先把一句话说透：**这篇东西的 base alpha 是 cross-venue relative-value / mean-reversion，不是 filter，不是 overlay。**

它不是在说“funding 可以预测价格”这么空的话，而是把一个更适合我们 desk 的短周期壳写得很清楚：
1. **Polymarket order book 给出 crowd skew；**
2. **Binance spot velocity 负责否决“真在单边飞”的情况；**
3. **Binance perpetual funding 给出 smart-money 方向确认；**
4. **真正交易的是被挤贵的 YES 或 NO token 的反向 fade。**

## 2. 核心结论
- **一句话核心结论：** 对 short-cycle desk，这个 repo 最值得保留的不是“又一个预测市场 bot”，而是它把 **retail skew fade × funding confirmation × flat-price veto** 写成了一条能独立复现的完整 raw alpha 壳。
- **一句话证明方式：** 证据不是论文回测，而是源码级规则拆解：`basis_impl.rs` 把 entry / exit / sizing / fee gate / expiry guard 全部明文写出来，足够直接翻译成你自己的 research harness。
- 这条线最像什么：**跨 venue 的 implied-probability mispricing 回归**，而不是传统方向动量。
- 它最值钱的点不在“用了 funding”，而在 **funding 只是 confirm，不是单独触发**；真正的 base alpha 仍然是 **skew 本身过度偏离 0.5**。
- 代码里给出的默认阈值很具体：**entry skew threshold = `7¢`，极端 skew bypass = `2× threshold`，TP = `+7%`，SL = `-9%`，skew-collapse exit = 回到 `3.5¢` 内，BTC velocity veto = `$25/5s`，BTC strike buffer = `$175`，max entry price = `$0.58`。**

## 3. 为什么和当前项目有关
这轮和当前 desk 的关系很直接：
- 它补的是 **raw alpha 素材池里的 relative-value / mean-reversion / carry-adjacent**，不是又一层 shared gate；
- 它天然是 **短周期**：repo 主战场就是 hourly Up/Down 市场，评估循环写到 **每 `50ms`** 扫一次快照，数据更新明确是实盘级；
- 它特别适合当前研究阶段，因为规则可拆、变量可解释、能快速做 **first verdict**；
- 即便你最后不做 Polymarket，本体思路也能迁移到别的二元市场/事件市场/赔率市场：**先找 crowd skew，再用外部主市场价格与 carry 信号做 veto/confirm。**

## 3.5 策略拆解（必填）
- 方向属性：**relative-value / cross-venue / mean-reversion / skew fade**
- 基础 alpha：**当 YES/NO 隐含概率偏得太离谱时，未来更可能向公平价回归。**
- regime：**Binance 现货并未同向急速移动，且 oracle 价格仍靠近 strike，说明这个市场还没“被现实价格直接判死刑”。**
- filter / veto：**高 velocity 禁做；距 strike 太远禁做；高 taker fee 禁做；离 expiry 太近禁做。**
- risk / sizing / execution overlay：**fractional-Kelly 尺寸缩放、entry price ceiling、TP/SL、skew-collapse 提前止盈、expiry guard。**

## 4. 源码里到底写了什么
### 4.1 入场逻辑
`src/strategies/basis_impl.rs` 里的顺序非常清楚：
1. **先过 expiry guard**：离收盘太近不做；
2. **必须有 strike**：没 strike 就没法判断这个 binary 市场是否已被现货价格“决定”；
3. **先过 fee gate**：两边 taker fee 只要有一边太高，就直接跳过；
4. **按币种切不同常数**：BTC / ETH / SOL 用不同 velocity 阈值与 strike buffer；
5. **现货必须够平**：若 `abs(velocity)` 超过上限，说明这不是“错价回归”，而可能是现货真的在单边重定价；
6. **现货不能离 strike 太远**：否则 YES/NO 的高低价未必是 crowd 错，而可能只是结果已经快被现实锁定；
7. **用 YES mid 计算 skew**：`yes_mid - 0.50`，而不是拿 bid 或 ask 单边看；
8. **skew 必须超过阈值**：绝对值不够大，不做；
9. **funding 要与 fade 方向一致，除非 skew 极端到直接 bypass**；
10. **最后再看 entry price**：买 NO 或买 YES 时，ask 不得太贵。

这套顺序很像我们当前喜欢的“**先定义 raw alpha，再逐层加 veto**”而不是反过来。

### 4.2 出场逻辑
源码里 exit 也不是一句“到点就平”：
- **TP**：利润达到 `+7%`；
- **SL**：亏损到 `-9%`，但要先过最小持有时间，避免 phantom fill / 极短噪声误杀；
- **Skew-collapse exit**：如果 skew 已经显著回到 `0.5` 附近且仓位已有盈利，就别死等 full TP；
- **Expiry exit**：过近到期直接走。

这很重要，因为它说明作者不是把 funding 当成慢频因子，而是确实在做 **短持有、事件窗内回归**。

### 4.3 仓位
源码里还有独立函数 `basis_trade_size(skew_abs)`：
- 以 **entry threshold 的倍数** 映射仓位；
- `1× threshold` 对应最小 size；
- 到 `BASIS_KELLY_MAX_MULTIPLIER`（README 里给的是 `3×`）放大到最大 size；
- 本质是 **signal-strength sizing**，不是固定手数。

## 5. 为什么这条线像 raw alpha，而不只是 funding overlay
因为 funding 在这里不是主信号，而是 **confirming signal**。

真正的交易对象是：
- `YES mid` 偏得过高 → 说明 crowd 把 YES 买贵了；
- 但如果 Binance 现货也在快速往上冲，那这未必是错价；
- 只有当 **现货没怎么动**，同时 **funding 还偏向反方向** 时，才更像“赔率被 retail 挤歪了”。

换句话说：
- **base alpha = skew mean reversion**
- **funding = side confirmation**
- **velocity / strike distance / fees / expiry = veto layer**

这正符合当前 intake 规则：能把 `base alpha / filter / overlay` 拆干净，就值得进池。

## 6. 可复刻的最小实验
**研究假设：** 在 Polymarket hourly BTC/ETH/SOL binary 市场里，若某一侧隐含概率对 `0.5` 的偏离足够大，同时 Binance spot 处于低 velocity 且 perp funding 与 crowd 偏向相反，则该侧被挤贵的概率更大，后续数分钟到数十分钟存在回归 edge。

**一个可计算定义：**
1. 数据源：
   - Polymarket CLOB best bid/ask + market close time + strike；
   - Binance spot mid / recent `1s~5s` velocity；
   - Binance perp funding（`fapi/v1/premiumIndex`）；
2. 定义 `yes_mid = (yes_bid + yes_ask)/2`；
3. 定义 `skew = yes_mid - 0.5`；
4. 当 `|skew| >= 0.07` 时产生候选；
5. 若 `abs(spot_velocity_5s) < cap` 且 `abs(oracle - strike) < buffer`，继续；
6. 若 `skew > 0` 且 funding < 负阈值，则买 `NO`；若 `skew < 0` 且 funding > 正阈值，则买 `YES`；
7. 若 `|skew| >= 0.14`，可测试 bypass funding 版本；
8. 出场先用 `TP/SL/skew-collapse/expiry` 四段式。

**最小回测切口：**
- 标的：Polymarket `BTC/ETH/SOL` hourly Up/Down markets
- 周期：事件窗内原始时间戳，研究汇总可折到 `1m/3m/5m`
- 样本：先抓最近 `2~4` 周
- 先看指标：`avg net bps/trade`、`median hold time`、`skew-collapse hit rate`、`fee-after hit rate`

**下一步怎么测：**
1. **先做 raw alpha baseline：只用 `|skew|` 入场，不上 funding confirm**，看本体有没有 edge；
2. **再做 A/B：`skew only` vs `skew + funding` vs `skew + funding + flat-velocity veto`**；
3. **单独扫 `0.05 / 0.07 / 0.09` 的 skew threshold**，确认现在这条线是不是被参数写死；
4. **单独做 fee ladder**：`50 / 100 / 200 / 300 bps`；因为这条策略对 taker cost 非常敏感；
5. **检查 hold-time 分布**：若 edge 只存在于超短窗，就要把执行层当主问题，而不是继续研究高层因子；
6. **如果要迁到纯 crypto perp desk**，可测试替代版：把 Polymarket 的 `yes_mid-0.5` 换成“事件市场隐含概率 / 预测市场概率 / 链上赔率”的 crowd skew proxy。

## 7. 数据源、公开性、更新频率、最小复现实验口径
- **Polymarket CLOB / Gamma API**
  - 用途：YES/NO bid-ask、market metadata、close time、strike
  - 公开性：公开可读
  - 更新频率：盘口实时 / WS 级
- **Binance spot / oracle price**
  - 用途：短时 velocity、是否已接近/穿过 strike
  - 公开性：公开可读
  - 更新频率：秒级到实时
- **Binance perp funding (`/fapi/v1/premiumIndex`)**
  - 用途：funding sign confirm
  - 公开性：公开可读
  - 更新频率：repo README 写的是每 `60s` 轮询注入快照

**最小可复现实验口径：** 只要你能连续抓取 `Polymarket top-of-book + strike/close` 和 `Binance spot/funding`，就能先做 event-time replay；甚至不需要先接实盘下单接口。

## 8. 风险与保留意见
- 这是 **repo-based intake**，不是论文；当前强项是“规则清楚”，弱项是“没有同等强度的公开大样本业绩证明”。
- Repo 只有 **5 stars**，不能把它当成已验证 edge，只能当作 **高可复刻候选壳**。
- 这条线对 **taker fee、流动性、延迟** 很敏感，代码里也明确加了 fee gate；所以它很可能是“执行决定生死”的策略，不是纸面 alpha 自动成立。
- 这套逻辑的原始战场是 **prediction market × crypto perp**，不能直接当作 Binance perp 单市场 alpha；若迁移到纯 perp，需要重新找 crowd skew proxy。
- 不过从研究价值看，它仍值得入池，因为它把 **crowd mispricing → external-market veto/confirm → mean-reversion trade** 这条链写得很完整。

## 9. 来源
1. **Michael Bordash (2026), `RustPolyBot`**
   - Repo：<https://github.com/mbordash/RustPolyBot>
2. **README.md**
   - <https://raw.githubusercontent.com/mbordash/RustPolyBot/main/README.md>
3. **Basis strategy source**
   - <https://raw.githubusercontent.com/mbordash/RustPolyBot/main/src/strategies/basis_impl.rs>
4. **GitHub repo metadata / commit history**
   - <https://api.github.com/repos/mbordash/RustPolyBot>
   - <https://api.github.com/repos/mbordash/RustPolyBot/commits?per_page=5>
