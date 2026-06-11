# 别把这篇 2024 JFM 论文只读成“市场效率检验”：对 short-cycle desk，更该先测的是「inverse put-call parity gap × option-perp triangle close」这条 options relative-value raw alpha

- 时间：2026-04-04 20:57 UTC
- 类型：2024 *Journal of Financial Markets* 开放获取文章（ScienceDirect article page / abstract / highlights）+ Crossref metadata + Deribit 公共 API live snapshot sanity check
- 主题类型：raw alpha
- 基础 alpha：**同币种、同 strike、同 expiry 的 call / put / perpetual 三角定价会围绕 inverse put-call parity 收敛；做的是期权-永续相对错价闭合，不是赌 BTC / ETH 单边方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/relative-value/stat-arb/put-call-parity/option-perpetual/triangle-close/inverse-options/deribit/btc/eth/1m/3m/5m/15m/paper/public-data/cost/risk
- 证据类型：论文原文摘要/亮点 + 衍生品定价地基 + 交易所公共 live 数据

## 1. 先回答一句：base alpha 是什么？

**base alpha = option strip 与 perpetual leg 之间的三角错价会向 inverse put-call parity 回归。**

换成人话：
不是“BTC 要涨 / 跌”，而是：
- 同一个 `strike + expiry` 下，`call - put` 应该和某个由 perp / forward 决定的理论关系对齐；
- 一旦期权腿和永续腿短时间脱锚，就会出现一个**可平仓、可对冲、可回归**的 relative-value pocket；
- 盈利来源是 **triangle mispricing close**，不是单边方向判断。

所以这不是 filter、不是 regime、也不是纯解释。
它本体就是一条 **options relative-value / stat-arb raw alpha**。

## 2. 为什么这轮值得选它？

最近 digest 已经补了很多：
- pairs / cointegration / spread forecast
- basis / funding / carry
- breakout / TSMOM / fade
- 以及一条 options 的 IV calendar spread

但**还没有把 option-perp parity 这条更“交易壳完整”的 raw alpha 单独立起来**。

这篇 2024 JFM 论文的价值，不在于“市场有效性又被检验了一遍”，而在于它给了我们一条很适合 short-cycle desk 的落地读法：

> **把 crypto inverse options + perpetual futures 看成一个可分钟级扫描的三角错价系统。**

这比再写一篇“又一个 shared gate / 确认层”更符合你这轮的优先级：
**优先补可独立复现、可直接落地完整策略的 raw alpha 候选。**

## 3. 这篇论文真正提供了什么？

主材料：

**Alexander, Carol; Chen, Xi; Deng, Jun; Wang, Tianyi (2024). _Arbitrage opportunities and efficiency tests in crypto derivatives_. Journal of Financial Markets. DOI: 10.1016/j.finmar.2024.100930.**

从论文摘要和 highlights，至少能拿到 4 个对 desk 有直接用处的结论：

1. **作者明确提出了“fiat-currency-free put-call parity”关系。**  
   这很关键。它不是拿传统股票期权那套硬平移，而是针对 crypto inverse / coin-margined 结构重写了 parity。

2. **论文不只看 options-only，也看 option–perpetual cross-market。**  
   这正是我们最关心的地方：
   不只是“同 expiry 的 call / put 有没有静态无套利缺口”，而是**期权链和 perpetual 之间能不能形成可执行的 cross-market relative-value shell**。

3. **Bitcoin 衍生品市场通常比 Ether 更有效，但 Ether 的套利机会更肥。**  
   换句话说：
   - BTC 更像“更干净、更难做”的市场；
   - ETH 更像“摩擦更大、但 pocket 更明显”的市场。

4. **在保守交易成本情景下，套利机会仍可能有利润空间。**  
   这点很重要，因为它把题目从“理论无套利”推进到了“cost 后还有没有肉”。

论文摘要还特别提到：
- 更长到期（`>= 15 days`）的期权，市场效率在变高；
- 交易量、区块链拥堵等状态变量，会影响套利利润的可实现性。

对我们来说，这些都不是“背景知识”，而是**可直接写进回测切片的 regime / liquidity 变量**。

## 4. desk 版最小可计算定义：先别装太复杂

如果先不完全照搬论文的全套套利检验，而是做一个**最小可复现代理**，可以先用下面这个 live proxy：

```text
proxy_gap = (C_mid - P_mid) - (1 - K / F_mid)
```

其中：
- `C_mid` = call 中间价（以 coin 计价）
- `P_mid` = put 中间价（以 coin 计价）
- `K` = strike（USD）
- `F_mid` = perpetual 中间价（用 perp 代 forward proxy）

这不是论文里全部细节的逐字复刻，但它足够诚实地抓住那条**inverse parity 脱锚**主线。

更直白地说：
- `proxy_gap > 0`：option strip 相对 perp **偏贵**；
- `proxy_gap < 0`：option strip 相对 perp **偏便宜**；
- 我们要赚的是 `proxy_gap → 0` 的闭合过程。

## 5. live honesty check：今天 Deribit 公共 API 至少说明这条线不是空想

我用 Deribit 公共 API 做了一个最小 sanity check（`2026-04-04 20:56 UTC`），结果写到了：

- `reports/artifacts/quant_digests/deribit_option_perp_parity_20260404/summary.json`

### 5.1 当前链上/盘口可得性：足够做分钟级实验

当前 active options 数量：
- **BTC：872** 张未到期合约
- **ETH：736** 张未到期合约

这意味着：
- 题目不是“只有论文，没有数据”；
- 至少在 Deribit BTC / ETH 上，`1m / 3m / 5m / 15m` 的快照实验完全能跑起来。

### 5.2 当前最近到期 ATM 近似 parity gap

以最近到期、最接近 ATM 的一组合约做一眼快照：

**BTC**
- `BTC-5APR26-67000-C` mid = **0.0055 BTC**
- `BTC-5APR26-67000-P` mid = **0.0020 BTC**
- `BTC-PERPETUAL` mid = **67253.75**
- `proxy_gap = -0.000273 BTC` ≈ **2.73 bps of underlying**

**ETH**
- `ETH-5APR26-2050-C` mid = **0.00775 ETH**
- `ETH-5APR26-2050-P` mid = **0.00195 ETH**
- `ETH-PERPETUAL` mid = **2061.725**
- `proxy_gap = +0.000113 ETH` ≈ **1.13 bps of underlying**

这组数字说明两件事：

1. **数据路径是活的。**  
   我们能直接从公共 API 拿到 `call / put / perp` 三条腿并即时算 gap。

2. **错价量级已经落在“可以研究 execution / cost 后是否可活”的区间。**  
   不是几十个点那种显然假报价，也不是完全贴死成 0。

当然，单帧快照**不等于 edge 证明**。它只说明：
> 这条线不是抽象理论，而是现在就能算、现在就能监控的 live mispricing process。

## 6. 怎么把它改写成完整策略？

### 6.1 Entry：先做“可交易 pocket”，别做论文式全覆盖

第一轮先只做 BTC / ETH、只扫流动性最好的一层：

1. 选最近 `2~4` 个到期；
2. 每个到期只保留 `25Δ ~ 75Δ` 或 ATM 附近若干 strike；
3. 计算 `proxy_gap_bps = abs(proxy_gap) * 10000`；
4. 只有当下面条件同时满足才进场：
   - `|proxy_gap| > threshold`（例如 `2 / 3 / 5 bps` 三档）
   - 信号连续存在 `2~3` 帧，不是一闪而过
   - call / put / perp 三腿都有可成交 bid/ask
   - option spread 不超过过去分位数阈值

方向上，别写得太玄：
- **gap 为正** → option strip 相对 perp 偏贵，优先做 **short rich strip / long cheap hedge**；
- **gap 为负** → option strip 相对 perp 偏便宜，优先做反向。

第一轮不追求理论上最纯的复制组合，先做**paper 主线 + perp hedge 的 executable shell**。

### 6.2 Exit：闭合、超时、失真，三种出场够用了

先用这 3 个最朴素的退出：
- `|proxy_gap|` 回到 close band（例如 `< 1 bps`）
- 持有超时（例如 `15m / 30m / 60m`）
- 任一腿流动性恶化 / spread 突然放大 / 接近 expiry gamma 区间

也就是说，先把它当 **分钟到小时级 mispricing close trade**，不是隔夜价值投资。

### 6.3 Sizing：先按 Greeks 上限，不按名义资金等权

这条线最怕的不是方向看错，而是：
- gamma 突然跳起来
- 某一腿先成交、另一腿打不进去
- 你以为做的是 relative-value，实际吃成了方向暴露

所以第一轮 sizing 建议：
- 先做**很小的单笔 notional**；
- 每个 expiry 单独设上限；
- 约束 `delta / gamma / vega` 暴露，而不是只看 USD notional；
- 接近到期时，仓位上限应明显更低。

### 6.4 Cost：这是这条线的生死线

至少显式记 4 类成本：
- option 手续费
- option bid/ask spread
- perp 手续费
- perp funding / 对冲滑点

如果第一轮回测里不把 **半个 spread / 一个 spread / 1.5 个 spread** 三档跑出来，这条线的结果就不诚实。

## 7. 这条线最容易犯什么错？

### 错法 1：把“理论套利”误当“随时可成交套利”

很多 parity gap 只是：
- 报价 stale
- 某一腿量太薄
- 第三腿对冲一打就没了

所以 **可成交性** 比公式漂亮更重要。

### 错法 2：把它误写成方向策略

这条线的收益来源不是“猜 BTC 下一根往哪走”，而是**option strip 与 perp 之间的相对错价收敛**。

如果回测里最后主要 PnL 来自方向暴露，那说明策略壳写歪了。

### 错法 3：太贴近到期，结果被 gamma / pin risk 吃掉

论文说 longer-dated options 更有效；
对 short-cycle desk 来说，这不等于“只做超近月最刺激”。

更诚实的做法是：
- 把最近到期当作 **研究样本之一**；
- 但在实盘壳上，要给 `DTE`（days to expiry）单独设 veto / size-down 规则。

## 8. 当前最诚实的 verdict

**Verdict：值得直接进 raw alpha 素材池，而且比继续补一个 shared filter 更值。**

原因很简单：
- 它的 **base alpha 清楚**；
- 公共数据**现在就能拿**；
- `entry / exit / sizing / risk / cost` 都能写出第一版；
- 而且它扩的是我们当前池子里相对稀缺的那一支：
  **crypto options × perp relative-value。**

如果后面实验发现：
- 信号只存在于不可成交报价；
- cost 后完全没肉；
- 或者 gap 虽大但闭合极慢；

那也没关系，至少这轮 intake 补的是一条**像样的 raw alpha 假设**，而不是又一个模糊确认层。

## 9. 下一步怎么测（直接排最小实验）

### 实验 A：14 天 `1m / 5m` snapshot collector

对 BTC / ETH：
- 每分钟抓 `call / put / perp` 三腿中间价与 spread；
- 只保留最近 `2~4` 个 expiry、ATM 附近若干 strike；
- 记录 `proxy_gap`、报价宽度、成交可行性、持续时间。

先回答最关键的问题：
**gap 是不是能持续到足以执行，而不是单帧毛刺？**

### 实验 B：paper-style executable shell backtest

事件定义：
- `entry`：`|proxy_gap| > 2/3/5 bps` 且连续 `2~3` 帧存在
- `exit`：回到 `<1 bps` / 超时 / 流动性丢失
- `cost`：option 半 spread、整 spread、1.5 spread 三档；perp maker/taker 双档

目标不是先追最高 Sharpe，
而是先确认：
**cost 后还剩不剩可重复 pocket。**

### 实验 C：BTC vs ETH 分桶

论文明确说：
- BTC 更有效
- ETH 套利机会更肥

所以不要合并回测看总收益。
要至少分成：
- BTC
- ETH
- 近月 vs 次近月
- 近 ATM vs 更偏翼部

先看哪一桶真正有 pocket。

### 实验 D：加一层实盘诚实过滤

只要任一条件满足就 veto：
- 任一腿没有双边报价
- option spread 过宽
- 距到期太近
- funding timestamp / 大波动窗口临近

这层不是 alpha 本体，
但它决定这条 alpha 能不能从“论文关系式”变成“可执行策略”。

## 10. 来源

1. **Alexander, C., Chen, X., Deng, J., & Wang, T. (2024). _Arbitrage opportunities and efficiency tests in crypto derivatives_. Journal of Financial Markets.**  
   - Venue: *Journal of Financial Markets*  
   - DOI: `https://doi.org/10.1016/j.finmar.2024.100930`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S138641812400048X`

2. **Alexander, C., Chen, D., & Imeraj, A. (2023). _Crypto quanto and inverse options_. Mathematical Finance.**  
   - Venue: *Mathematical Finance*  
   - DOI: `https://doi.org/10.1111/mafi.12410`  
   - Readable URL: `https://doi.org/10.1111/mafi.12410`

3. **Deribit API Documentation.**  
   - Readable URL: `https://docs.deribit.com/`

## 11. 本地 artifacts

- `reports/artifacts/quant_digests/deribit_option_perp_parity_20260404/summary.json`

一句话收尾：**这篇 2024 JFM 对我们最值钱的，不是“crypto 衍生品市场也会更有效”，而是它给了一条可在 `1m/3m/5m/15m` 直接开测的 options-perp 三角错价 raw alpha。**
