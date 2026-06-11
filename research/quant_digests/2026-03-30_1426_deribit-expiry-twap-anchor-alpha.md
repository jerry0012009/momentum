# 别把这份 2025 Deribit TWAP repo 只当 near-expiry scanner：更该先测的是「settlement-TWAP anchor gap」事件型 options raw alpha
- 时间：2026-03-30 14:26 UTC
- 类型：2025 GitHub 仓库 + Deribit 官方公共 API 管线核验
- 主题类型：raw alpha
- 基础 alpha：**BTC 日度到期期权在最后 `30m` 会向“最终按 settlement TWAP 决定的价值”收敛；若 live option price 相对 rolling-TWAP fair value 出现足够大的偏离，可做同所、同合约、事件窗内的 expiry-window mean reversion / relative-value 交易。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/event-driven/expiry-window/twap-settlement/deribit/same-venue/relative-value/near-expiry/btc/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：仓库证据（源码/参数/实时采集逻辑）+ Deribit 公共 API 可验证性

## 1. 这次看了什么
先回答 base alpha：**这不是 filter，也不是“options expiry 附近会更热闹”的解释层；本体就是 near-expiry option premium 相对 settlement-TWAP anchor 的可交易偏离。**

主材料是 **cbyhre (2025) 的 GitHub 仓库 `Deribit-TWAP-Arbitrage`**。它最值得 desk intake 的点，不是“又一个 options scanner”，而是把一个很具体、很短窗口、很适合 `1m/3m/5m` 事件研究的 alpha 讲清了：

1. Deribit 到期期权的最终结算不是盯单点 spot，而是盯 **到期前 30 分钟的 BTC index TWAP**；
2. repo 每 **5 秒** 抓一次 BTC index，并维护 **30 分钟 rolling average**；
3. 再把这个 rolling TWAP 当作临时 settlement anchor，去和 live option `mark_price` / `mark_iv` 算出来的“our price”对比；
4. 如果二者偏得足够大，就不是 generic noise，而是一个可以直接写成 `entry / exit / sizing / cost` 的事件型 raw alpha 候选。

这条线比继续补一个 shared gate 更值得写，因为它天然就是**独立可下单的完整策略骨架**，而且它补的是当前池子里相对少的 **options expiry microstructure / event-driven relative-value**，不再只是 perp trend / funding / lead-lag 内循环。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最该先复现的，不是“监控快到期期权”，而是更窄也更可执行的 **settlement-TWAP anchor gap**：在最后 `30m` 内，用 rolling TWAP 近似最终结算锚，交易 option premium 向该锚值回归的 drift。
- **一句话怎么证明：** 源码没有停在概念层，而是把数据抓取频率、rolling window、定价函数、到期时间计算都写成了可运行脚本；我再用 Deribit 公共 API 做了可得性核验，确认 **事件窗 universe、最终交割标签、日度到期链条** 都能公开拿到。

对当前 desk 最有用的 3 个数据点：

1. **repo 参数非常短窗**：`UPDATE_INTERVAL = 5s`、`ROLLING_WINDOW_MINUTES = 30`，明确就是为 expiry-window alpha 设计，不是慢频框架。  
2. **当前 live universe 足够密**：我用 `public/get_instruments` 查到写作时最近一档 BTC option expiry 是 **2026-03-31 08:00 UTC**，仍有 **54** 个未到期合约；这说明日度事件窗是可以持续滚动采集的。  
3. **最终标签公开可回填**：`public/get_last_settlements_by_currency` 显示上一个 BTC 日度到期（`2026-03-30 08:00 UTC`）的最终 settlement index 为 **67,356.39**；其中 `BTC-30MAR26-67000-C` 的最终 `mark_price = 0.005291 BTC`（约 **$356.39**），`BTC-30MAR26-67500-P` 的最终 `mark_price = 0.002132 BTC`（约 **$143.61**）。换句话说，**事件结束后的真实 payout 标签是公开、可程序化回填的**。

翻成人话：**这条 alpha 不是猜“明天 BTC 涨跌”，而是赌“快到点了，option price 会往最终结算锚靠”。** 这比继续造一个模糊 filter 更像能快速做 first verdict 的 raw alpha。

## 3. 为什么和当前项目有关
- 它是 **可独立复现的 raw alpha**，不是 overlay。  
- 它补的是当前素材池里较少的 **options / expiry microstructure / same-venue event-driven RV**，和已经很多的 perp trend / cross-sectional / funding 族群正交。  
- 它天然映射到 `1m / 3m / 5m / 15m`：不是说主信号来自 K 线形态，而是 **最后 30 分钟本身就是一个分钟级事件窗**；你完全可以用 `5s~60s` quote snapshot 生成信号，再按 `1m/3m/5m` 聚合和评估半衰期。  
- 相比 3/29 那篇 cross-venue synthetic forward parity，这次更像**单 venue、单合约、结算机制驱动**的 raw alpha，逻辑更简单，first verdict 更快。

## 3.5 策略拆解（必填）
- 方向属性：same-venue / near-expiry / event-driven / relative-value / mean reversion  
- 基础 alpha：live option premium 与“最终按 30m settlement TWAP 决定的 fair value”之间存在短暂偏离，并在到期逼近时收敛  
- regime：只在 **到期前最后 `30m`** 开机；优先 **近 ATM（如 `|K/S-1| <= 5%~10%`）**、有连续报价、买卖盘未真空的日度 / 次日度到期合约  
- filter / veto：
  - 只做剩余到期时间 `<= 30m` 的合约
  - `abs(edge)` 必须超过 **手续费 + 滑点 + latency buffer + inventory buffer**
  - 深虚值且长期零成交/零盘口的腿默认只记观察，不开仓
  - 最后 `1~2m` 若盘口明显恶化，宁可不做
- entry / exit：
  - 定义 `edge_t = model_price_twap - market_price`
  - `edge_t > hurdle`：做多被低估的 option
  - `edge_t < -hurdle` 且可安全做空时：做空被高估的 option；若裸 short 风险不接受，则降级成**只做 long-underpriced 版本**
  - 当 `|edge_t|` 回落到开仓时的 `30%~50%`、或持有到最后 `1~2m`、或 rolling-TWAP 方向反转时离场
- sizing / risk / cost：
  - 仓位按 **premium-at-risk** 而不是按名义 Delta 一把梭；单腿 premium 风险和总 gamma/vega 暴露要封顶
  - 若做 short 版本，必须设 **单合约保证金上限 / 单 expiry 总风险上限 / 宕机 kill-switch**
  - 成本先按 taker 费 + 半个 spread + `5s~15s` 延迟缓冲估计；若成本一加就塌，这条线就只留在研究池

## 4. 可复刻的最小实验
- **研究假设：** Deribit BTC 日度到期期权在最后 `30m` 内，会围绕 rolling settlement-TWAP fair value 出现可重复的分钟级收敛；只要偏离超过全成本和执行缓冲，就能留下 post-cost edge。  
- **可计算定义：**  
  1. 用 `public/get_instruments` 找最近到期、剩余时间 `<= 30m` 的 BTC options；  
  2. 每 `5s~30s` 抓 `public/get_index_price` 与 option quote（repo 用 `public/get_book_summary_by_currency`）；  
  3. 维护过去 `30m` 的 BTC index rolling average，得到 `twap_now`；  
  4. 用当前 `mark_iv` + `twap_now` + 剩余到期时间估一个 `model_price_twap`；  
  5. 计算 `edge_t = model_price_twap - market_price`，只在 `|edge_t| > hurdle` 时交易；  
  6. 事件结束后用 `public/get_last_settlements_by_currency` 回填最终 settlement label。  
- **最小回测切口：** 先只做 BTC、最近 `20~60` 个日度到期事件、近 ATM 合约、采样频率 `5s/15s/30s` 三档。  
- **最该先看 2 个指标：**  
  1. `edge half-life`：信号出现后几分钟内回归；  
  2. `post-cost hit rate`：扣掉 fees + spread + latency 后还能否为正。

## 5. 下一步怎么测（必须）
1. **先补“盘口可执行性”而不是继续看 mark。** repo 当前更像 fair-value monitor；真正 first verdict 要把 `mark_price` 升级成 `best bid/ask` 或 conservative mid。  
2. **只盯最后 30 分钟的近 ATM 小宇宙。** 别把整条链都扫进来；深虚值更像报价噪音，不像可执行 alpha。  
3. **做 long-only 与 long/short 双版本。** 如果 short 版本的保证金和尾部风险太差，就保留 long-underpriced 版本先看是否仍有 edge。  
4. **把 edge 同时写成 BTC、美元和 premium-return 三种口径。** 不同 strike 的 option 绝对价差不可直接横比。  
5. **先做 20~60 个到期事件的 friction ladder。** 乐观版（mid / maker）能看见只是第一步；真正决定是否晋级的是现实版（taker + spread + latency）还能不能活。

## 6. 风险与保留意见
- 当前强证据主要来自 **repo 源码 + Deribit 公开机制 + API 可得性**，不是作者给出的长样本成交级回测。  
- repo 用的是 **rolling average + 当前 IV** 的 fair-value 近似，不是完整的最终 settlement path 预报；它更像实时代理，不是 oracle。  
- 这条线越靠近到期，越吃 **盘口深度、更新延迟、成交优先级**；慢脚会把理论 edge 吃完。  
- 若某些 option 长时间没交易，`mark` 可能滞后；因此 **quote-based / trade-based 版本** 才是能不能进入实盘候选池的分水岭。  
- 若最终发现 edge 只在极少数 expiry / 极少数 strike 才出现，这条线也可能更适合作为 **event-clock execution sleeve**，而不是全天候主策略。

## 7. 来源
1. **cbyhre. (2025). _Deribit-TWAP-Arbitrage_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/cbyhre/Deribit-TWAP-Arbitrage`  
   - Repo URL: `https://github.com/cbyhre/Deribit-TWAP-Arbitrage`
2. **`Option_Scraper.py`（repo 内 rolling-TWAP / option pricing / 到期时间计算主逻辑）**  
   - Readable URL: `https://raw.githubusercontent.com/cbyhre/Deribit-TWAP-Arbitrage/main/Option_Scraper.py`  
   - Repo URL: `https://github.com/cbyhre/Deribit-TWAP-Arbitrage/blob/main/Option_Scraper.py`
3. **Deribit API Docs / public endpoints**  
   - Readable URL: `https://docs.deribit.com/`  
   - API base used: `https://www.deribit.com/api/v2/public/get_instruments`, `https://www.deribit.com/api/v2/public/get_index_price`, `https://www.deribit.com/api/v2/public/get_book_summary_by_currency`, `https://www.deribit.com/api/v2/public/get_last_settlements_by_currency`
4. **Deribit settlement records（公开可得）**  
   - 用途：回填日度到期期权最终 settlement index / final mark_price，给事件级 backfill 提供公开标签
