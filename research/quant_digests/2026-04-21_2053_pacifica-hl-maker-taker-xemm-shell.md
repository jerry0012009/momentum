# 别把这份 XEMM 仓只读成“跨所做市工程”：对 short-cycle crypto desk，更该先回答的是「maker-on-thin-venue × taker-hedge-on-deep-venue」这条 raw alpha 壳到底够不够厚

- 主题类型：raw alpha
- 基础 alpha：`在薄簿盘口挂 maker，等被动成交后立即去深流动性 venue 做 taker 对冲，赚跨 venue best-price gap - fees - slippage - latency`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 一句话结论
这份 2026 Rust 仓给的是一套很完整的 **maker/taker cross-exchange relative-value raw alpha 骨架**：Pacifica 挂单，Hyperliquid 秒级对冲，外加 fill-detection、profit cancel、refresh、slippage guard，全链条都写了。问题是我用公开盘口做了 90 秒 quick probe 后，`BTC/ETH/SOL` 的**理论瞬时 edge 在 repo 默认费率下全程为负**：最好一档也只有 `-2.33 ~ -3.34bps`，离 repo 自己要求的 `+15bps` 安全垫还差一大截。所以它更像“高质量执行壳 + 极端错价 pocket 策略”，不像可以默认常开的一般性 alpha。

## 为什么这篇值得进研究池
因为它不是泛泛而谈的“做市/搬砖概念”。这个 repo 把 desk 真正在意的那几层都写清楚了：
1. **base alpha**：吃 `thin venue maker quote` 与 `deep venue taker hedge` 的价差；
2. **entry**：只有当 Pacifica maker 限价、配上 Hyperliquid taker 对冲后仍有正 edge 才下单；
3. **exit**：Pacifica 一旦成交，马上在 Hyperliquid 打对冲；
4. **risk**：profit decay 取消、订单过期刷新、fill dedup、REST+WS 双通道、slippage 上限；
5. **cost**：maker/taker fee、tick rounding、latency safety margin 都显式建模。

换句话说，它很适合当作 **microstructure / relative-value / inventory-light execution alpha** 的完整策略模板。

## 来源信息
### GitHub 仓库
- Author / Repo: `djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID`
- Year: 2026（当前可见活跃更新）
- Title: *XEMM Rust - Cross-Exchange Market Making Bot on Pacifica (Maker) and Hyperliquid (Taker)*
- Repo URL: <https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID>
- Readable URL: 同上 README
- 备注：README 明确写明策略灵感来自 Hummingbot 的 XEMM，但这份实现把 Pacifica × Hyperliquid 的低延迟执行细节补得更完整。

### 本轮重点审阅文件
- `README.md`
- `src/strategy/opportunity.rs`
- `src/config.rs`
- `src/app.rs`
- `src/connector/pacifica/trading.rs`
- `src/connector/hyperliquid/trading.rs`
- `config.json`

## 它的 raw alpha 到底是什么
别把它误读成“只要跨所就有利可图”。

这里真正的 base alpha 是：

> **同一标的在两所的最佳买卖价并不总同步；如果薄簿 venue 的 maker 报价，能在成交后立刻用深簿 venue 的 taker 单对冲，并且净价差覆盖 maker fee + taker fee + slippage + latency buffer，那么这笔 fill 本身就是 alpha。**

也就是：
- **Pacifica 买入 maker → Hyperliquid 卖出 taker**
- **Pacifica 卖出 maker → Hyperliquid 买入 taker**

它不是趋势、不是均值回复、不是 funding carry，而是一条 **microstructure / cross-venue relative-value** 的原生 alpha。

## repo 里最值得学的，不是“跨所”三个字，而是这套计算与风控骨架

## 1) opportunity evaluator 直接把可交易条件写成公式
在 `src/strategy/opportunity.rs` 里，仓库把两个方向都写成了显式净边计算：

### Pacifica 买 / Hyperliquid 卖
```text
buy_limit_price = (HL_bid * (1 - takerFee)) / (1 + makerFee + profitRate)
```
然后再按 Pacifica tick **向下取整**，重新计算真实可拿到的 `buy_profit_bps`。

### Pacifica 卖 / Hyperliquid 买
```text
sell_limit_price = (HL_ask * (1 + takerFee)) / (1 - makerFee - profitRate)
```
再按 Pacifica tick **向上取整**，计算 `sell_profit_bps`。

这个写法的好处是：
- 不是先看“价差大不大”，而是直接问 **扣完费、按 tick rounding 后，还剩多少 bps**；
- `profit_rate_bps` 本质上不是收益预测，而是 **安全垫 / latency buffer**；
- 这套写法可以很容易迁移到别的 `maker venue × taker hedge venue` 组合。

## 2) 它给的是完整策略，不只是信号函数
`README` + `src/app.rs` 里能看出这套壳已经把完整执行流程补齐：
- 实时 orderbook 监控；
- opportunity 评估；
- Pacifica 下 maker 限价单；
- 成交后 Hyperliquid 立即对冲；
- 若利润掉太多则 cancel；
- 若订单太久没成交则 refresh；
- fill detection 用 5 层冗余；
- hedge 默认走 Hyperliquid WebSocket，失败再 REST fallback。

对 desk 来说，这比“只给一个 spread 阈值”值钱很多，因为它已经把 `entry / hedge / cancellation / stale-order risk / fill-dedup` 串成了一条可执行骨架。

## 3) 默认参数已经透露了作者对现实摩擦的判断
`config.json` / `src/config.rs` 默认值：
- Pacifica maker fee：`1.5bps`
- Hyperliquid taker fee：`4.0bps`
- target `profit_rate_bps`：`15bps`
- `profit_cancel_threshold_bps`：`3bps`
- `order_refresh_interval_secs`：`60s`
- Hyperliquid market-order slippage 容忍：`5%`（执行保护阈值，不是预期真实滑点）

这说明作者默认口径不是“看到正 gap 就上”，而是：
**只有 edge 大到足够覆盖费率、滑点、延迟和 quote decay，才值得挂单。**

## 本轮 public-data quick probe：默认大币口径下，这条 alpha 目前不够厚
### 数据源与公开性
- Pacifica public REST：`https://api.pacifica.fi/api/v1/info`、`/api/v1/book?symbol=...&agg_level=1`
- Hyperliquid public info API：`https://api.hyperliquid.xyz/info` with `{"type":"l2Book","coin":...}`
- 全部公开可得，无需 API key

### 采样口径
- 标的：`BTC / ETH / SOL`
- 频率：`1s` 采样
- 样本：每个标的 `90` 个 snapshot（约 `90s`）
- 计算：
  - `Pacifica buy maker -> Hyperliquid sell taker`
  - `Pacifica sell maker -> Hyperliquid buy taker`
  - 扣 repo 默认 `1.5bps maker + 4.0bps taker`
  - 不额外假设滑点，只看最乐观 top-of-book 理论边

### 关键结果
#### BTC
- `best_edge_mean ≈ -4.21bps`
- `median ≈ -4.31bps`
- `max ≈ -2.33bps`
- `raw_best_gap_mean ≈ +1.29bps`
- `>0bps hit = 0 / 90`

#### ETH
- `best_edge_mean ≈ -4.96bps`
- `median ≈ -5.07bps`
- `max ≈ -3.34bps`
- `raw_best_gap_mean ≈ +0.54bps`
- `>0bps hit = 0 / 90`

#### SOL
- `best_edge_mean ≈ -4.38bps`
- `median ≈ -4.56bps`
- `max ≈ -2.69bps`
- `raw_best_gap_mean ≈ +1.12bps`
- `>0bps hit = 0 / 90`

### first verdict
- 原始跨所 best-price gap **不是没有**，但均值只有 `0.54~1.29bps`；
- repo 默认费率总和就先吃掉 `5.5bps`；
- 所以公开大币 top-of-book 上，这条线目前更像 **长期负 carry 的费率陷阱**；
- 若还要再加真实 slippage、fill uncertainty、未完全成交、Pacifica quote 被 sniped 的风险，实际只会更差。

## 这对 1m / 3m / 5m / 15m 有什么意义
这条线本质是 **sub-minute / event-time alpha**。

所以：
- 它**不是** `15m` 主信号；
- 更像 `1m/3m` 甚至更细粒度的 microstructure shell；
- 若真要和当前 desk 周期对齐，更适合作为：
  - 独立的 microstructure sleeve；
  - 或 `1m/3m` 的 execution alpha；
  - 再由 `5m/15m` higher-level regime 决定是否放开仓位。

## 对当前 desk 最有价值的迁移点
即便这轮 first verdict 偏负，这份 repo 仍然很值得留：

### 可直接复用的部分
1. **双边 maker/taker edge 公式**：可以直接搬到别的 venue 对上；
2. **profit decay cancel**：成交前 edge 掉太多就撤，这是所有 quote-based alpha 都该有的；
3. **fill-detection 冗余设计**：WS fill、WS position、REST poll、position monitor、pre-cancel safety；
4. **hedge queue + WS-first execution**：适合后续任何 fill-triggered hedge 场景；
5. **tick-aware rounding 后重算真实 bps**：避免“理论正 edge，落地后变负”。

### 更适合 desk 的读法
不要把它看成“Pacifica × Hyperliquid 专用 bot”，更适合把它抽象成：

> `maker-on-thin-venue × taker-on-deep-venue × post-rounding net-edge gate`

这个壳未来可以迁到：
- CEX / DEX；
- 同一所不同产品簿深层级；
- prediction market / options venue / perp venue 之间的 quote dislocation；
- 任何“先被动成交、后主动对冲”的 inventory-light relative-value 任务。

## 它当前为什么还不值得比继续补 raw alpha 更高优先级
答案很直接：
- 它当然是 raw alpha；
- 但在公开大币主流盘口上，这轮 first verdict 很明确：**边太薄**；
- 所以它不该替代我们继续补更厚的趋势 / MR / xs / stat-arb 主线；
- 更合理的位置是：**放进 microstructure / execution alpha 素材池**，等以后有更强 venue 组合或更低费率条件时再回收。

## 下一步怎么测
按优先级建议三步走：

### 1) 先把“瞬时最优价差”升级成“可成交容量后的净边”
不是只看 top-of-book，而是：
- 取 Pacifica maker 挂单价对应的可成交 size；
- 取 Hyperliquid 对冲时实际要吃掉的深度；
- 计算 `depth-weighted hedge price`；
- 再扣 maker/taker fee，重算 `net_edge_bps`。

### 2) 只做“极端错价 pocket”统计，不做全时段均值
当前均值肯定不够厚，下一步该测：
- `raw_gap > 5bps / 8bps / 10bps` 时的出现频率；
- 这些 pocket 是否集中在特定时段、特定币、特定波动状态；
- 是否只有小币或事件期才值得挂。

### 3) 做 fill realism paper test
用模拟 paper 口径复现：
- Pacifica 挂单后只在“价格触及且未明显穿透”时才算 fill；
- 对冲用 Hyperliquid 吃一档/多档；
- 加 `latency_ms`、`cancel lag`、`partial fill`；
- 输出 `fill rate / cancel rate / realized edge / tail loss`。

如果这三步之后，仍没有稳定 pocket，就把它定性为：
**高质量执行模板，但不是当前 desk 的主 raw alpha。**

## 本轮产物
- 研究笔记：`research/quant_digests/2026-04-21_2053_pacifica-hl-maker-taker-xemm-shell.md`
- Probe 脚本：`reports/artifacts/quant_digests/xemm_pacifica_hl_probe_2026-04-21.py`
- Probe 明细：`reports/artifacts/quant_digests/xemm_pacifica_hl_probe_detail_2026-04-21.csv`
- Probe 汇总：`reports/artifacts/quant_digests/xemm_pacifica_hl_probe_summary_2026-04-21.csv`
