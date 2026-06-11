# 别把这份 2026 options-arb 新仓库只当泛化 scanner：更该先测的是「Deribit-Aevo synthetic forward gap」完整 raw alpha
- 时间：2026-03-29 04:28 UTC
- 类型：2026 GitHub 新仓库 + Deribit / Aevo 公共 options 数据最小快检
- 主题类型：raw alpha
- 基础 alpha：同一标的、同一到期、同一 strike 的 call/put 在不同 venue 上会隐含出不同的 synthetic forward；当跨 venue `F = K·e^{-rT} + (C-P)` 出现足够大的价差时，做多便宜 synthetic forward、做空昂贵 synthetic forward，吃 parity 回归。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/relative-value/stat-arb/cross-venue/put-call-parity/synthetic-forward/deribit/aevo/btc/1m/3m/5m/15m/repo/external-data
- 证据类型：仓库证据（源码/测试/风控模块）+ 公共数据快检

## 1. 这次看了什么
先回答 base alpha：**这不是 filter，也不是“option 市场有点乱”的解释层；本体就是跨 venue synthetic forward 的 relative-value raw alpha。**

主材料是 **daiwanwei (2026) 的 GitHub 仓库 `options-arb`**。这份仓库表面上像一个大而全的 crypto options arbitrage 框架，但对当前 desk 最值得 intake 的，不是所有 scanner 一起上，而是其中最容易写成完整最小实验的一条：

**先在单 venue 内用 put-call parity 把 call/put 压成一条 synthetic forward，再跨 venue 比较这条 forward 的隐含价格。若同组合约在 Deribit 比 Aevo 便宜，就在 Deribit 做多 synthetic forward、在 Aevo 做空 synthetic forward。**

这条线之所以比继续补一个“shared gate / 确认层”更值得写，是因为它本身就能直接落成完整策略：`signal / entry / exit / sizing / risk / cost / kill-switch` 都能清楚定义，而且和当前已经很多的 perp momentum / funding / lead-lag 族群是正交补充。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得先复现的不是泛化“跨 venue options arb”，而是更窄也更可测的 **cross-venue synthetic forward gap**：把 call-put parity 先压成 forward，再交易 venue 之间的 forward 偏离。
- **一句话怎么证明：** 仓库没有停在概念层，而是直接给了 `scan_put_call_parity` 与 `scan_cross_venue_parity_dislocations` 两层检测、配套 risk manager、paper trader 和阈值测试；我再用 Deribit/Aevo 公共口径做了 live snapshot，至少确认这类 gap 现在仍然看得见。
- 仓库源码里的核心公式很直接：
  - 单 venue parity gap：`(C-P) - (S - K·e^{-rT})`
  - 单 venue synthetic forward：`F = K·e^{-rT} + (C-P)`
  - 跨 venue alpha：比较 `F_A` 与 `F_B`，当 `|F_A-F_B|` 超过阈值才出手。
- 仓库单元测试把这条线写得很清楚：`scan_cross_venue_parity_dislocations(..., min_forward_gap=100.0)` 只在 synthetic forward gap 足够大时才报信号；也就是说它默认不是“逢差就做”，而是先过成本/执行门槛再动。
- 风控骨架也不是空的：paper loop 里默认有 `max_position_per_instrument=100`、`max_position_per_underlying=500`、`max_margin_utilization=0.95`，并且 pre-trade 要同时检查 instrument / underlying / delta / gamma / vega / margin 六类限制。

我补的 **live quick check** 先不拿成交价硬吹收益，只回答“这种 dislocation 现在还有没有”：
1. 直接抓 **Aevo `GET /markets?asset=BTC`** 和 **Deribit `public/ticker`**，在 `BTC`、`±15% moneyness` 范围内配对出 **93** 组同时有 call+put 的 matched instruments。  
2. 这 93 组里，按 mark-based synthetic forward 估算，**62 组的绝对 gap > $5，23 组 > $10，3 组 > $20**。  
3. 在更靠近 ATM 的子样本里，我得到的 **median abs gap ≈ $7.94，p90 ≈ $16.53，max ≈ $27.59**；而且靠前的大 gap 多数是 **Aevo synthetic forward 比 Deribit 更贵**，说明至少存在可系统监控的 venue 偏向。  

翻成人话：**不是说现在就能无脑四腿开干，而是“先压成 synthetic forward 再看 venue gap”这件事，已经比直接盯 call premium / put premium 更像真正能做 first verdict 的 raw alpha。**

## 3. 为什么和当前项目有关
- 它是 **可独立复现的 raw alpha**，不是 overlay。  
- 它补的是当前素材池里相对少的 **options / static-arb / market-neutral relative-value** 方向，而不是继续在 perp momentum 家族里内循环。  
- 它能自然映射到 `1m / 3m / 5m / 15m`：不是说 K 线本体来自 15m，而是说 **quote snapshot / signal 生成可以按秒到分钟滚动，随后用 1m~15m 去做事件聚合、半衰期、收敛窗口与风控复盘**。  
- 和最近已有的 options 主题相比，这条线更底层：它不是单腿 premium，也不是同所 vertical no-arb，而是 **先做 parity 压缩，再比较跨 venue synthetic forward**，更接近可迁移的统一框架。  

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / cross-venue / 低净方向暴露
- 基础 alpha：同一 `underlying-expiry-strike` 的 synthetic forward 在不同 venue 上出现可观偏离，并在时间、成交或到期收敛中回归
- regime：优先在 **近到期、近 ATM、两边都有连续报价** 的组上开机；极深虚值、长期限、单边零报价时降级
- filter / veto：
  - 必须两边都有 call+put，且 contract spec 可对齐
  - gap 必须大于 **四腿费用 + legging buffer + 资金/保证金占用补偿**
  - 若任一腿只剩 `mark`、没有可执行 bid/ask，默认只记观察信号，不进交易信号
  - 到期前最后几分钟、盘口真空或单边锁死时 veto
- risk / sizing / execution overlay：
  - 若 `F_Deribit < F_Aevo`：Deribit 做多 synthetic forward（`long call + short put`），Aevo 做空 synthetic forward（`short call + long put`）
  - 仓位按两边最小可成交 size、保证金占用和 greeks 限额缩放
  - 优先先下流动性更好的腿，再设超短 timeout；若一边未成交，立即撤退或对冲

## 4. 可复刻的最小实验
- **研究假设：** `BTC` options 在 Deribit 与 Aevo 的同组 synthetic forward 会出现可重复的分钟级偏离；只要 gap 超过全成本与 legging 风险补偿，回归就能提供 post-cost edge。  
- **可计算定义：**  
  1. 每 `10s~60s` 抓一次 Deribit/Aevo 公共 options 数据；  
  2. 对每个共同的 `expiry × strike` 组合，分别取 call/put 价格计算 `F_venue = K·e^{-rT} + (C-P)`；  
  3. 定义 `gap = F_Deribit - F_Aevo`；  
  4. 当 `|gap| > threshold` 时入场，方向为 **long cheap synth / short rich synth**；  
  5. 当 gap 回到 50% 以内、反向穿越、或持有超时（比如 `5m / 15m / 60m`）时离场。  
- **最小回测切口：** 先只做 `BTC`、最近 `30` 天、近到期和次近到期、moneyness 先限制在 `|K/S-1| <= 10%`。  
- **最该先看 2 个指标：**  
  1. `break-even gap`：四腿全成本和 legging buffer 合起来到底要吃掉多少美元 / bps；  
  2. `gap half-life`：gap 出现后是几分钟内回归，还是只是 venue mark 方法长期不同。  

## 5. 下一步怎么测（必须）
1. **先把“mark-based 观察”升级成“可执行 quote-based 观察”。** 当前快检证明 gap 可见，但真正能不能做，取决于 bid/ask 和 size，不是 mark。  
2. **只盯近 ATM / 近到期。** 先别把长尾深虚值链条扫满；那更像报价噪声，不像可执行 alpha。  
3. **把 gap 统一换成 bps 和美元双口径。** 绝对美元 gap 好理解，但不同 strike/expiry 最终还是要看占 spot 的 bps 和占保证金的回报。  
4. **做 four-leg friction ladder。** 先跑乐观版（maker / mark-close），再跑现实版（taker + partial fill + one-leg timeout）；如果一上 friction 就塌，这条线只能留在研究池。  
5. **区分“收敛 alpha”与“venue 定价体制差异”。** 若 Aevo 长期系统性更贵，但不回归，那就不是短周期 alpha，而更像结构性 basis，需要改成 carry / inventory 研究题。  

## 6. 风险与保留意见
- 当前强证据主要来自 **repo 源码 + 单元测试 + public snapshot**，不是作者给出的长样本真实成交回测。  
- 我这轮 live quick check 用到的 **Aevo 是 mark price**，Deribit 有时也是 mark / ask fallback；这足以证明 dislocation 可见，但**不等于可成交**。  
- 这条线天然是 **四腿交易**，真正的敌人不是公式，而是 legging risk、保证金占用、跨 venue 转仓与风控联动。  
- Deribit 的 BTC options 报价以 BTC 计价，Aevo 更像 USDC 口径；若不认真做单位归一化，很容易把假 gap 当真钱。  
- 当前 snapshot 里大 gap 大多是 Aevo 更贵、Deribit 更便宜；如果这是长期制度差，不一定会在 `5m / 15m` 内回归。  

## 7. 来源
1. **daiwanwei. (2026). _options-arb_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/daiwanwei/options-arb`  
   - Repo URL: `https://github.com/daiwanwei/options-arb`
2. **`crates/arb-scanner/src/lib.rs` / `tests/cross_venue_parity.rs` / `tests/cross_venue.rs`（仓库内 synthetic forward / parity 逻辑与阈值测试）**  
   - Readable URL: `https://raw.githubusercontent.com/daiwanwei/options-arb/main/crates/arb-scanner/src/lib.rs`  
   - Repo URL: `https://github.com/daiwanwei/options-arb/tree/main/crates/arb-scanner`
3. **Deribit API Docs — public/get_instruments, public/ticker**  
   - Readable URL: `https://docs.deribit.com/`  
   - API base used: `https://www.deribit.com/api/v2/public/get_instruments`, `https://www.deribit.com/api/v2/public/ticker`
4. **Aevo Public Markets API**  
   - Readable URL: `https://api.aevo.xyz/markets?asset=BTC`  
   - 公开性：公开可得  
   - 更新频率：分钟内可重复抓取，适合 `10s~60s` 轮询最小实验
5. **Merton, R. C. (1973). _Theory of Rational Option Pricing_. Bell Journal of Economics and Management Science.**  
   - DOI: `10.2307/3003143`  
   - Readable URL: `https://www.jstor.org/stable/3003143`  
   - 用途：put-call parity 的经典理论地基；本次 digest 仍以 2026 repo + 公开 market data 为主线。
