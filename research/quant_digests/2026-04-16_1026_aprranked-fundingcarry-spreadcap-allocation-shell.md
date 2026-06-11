# 别把这份 2026 funding-arbitrageur 仓库只读成 paper-mode demo：对 short-cycle desk，更该先抄的是「APR-ranked funding carry × spread-cap admission × reserve-aware allocation」

- 时间：2026-04-16 10:26 UTC
- 类型：2026 GitHub 新仓库 source audit（README + `arbitrageur/engine.py` + `arbitrageur/config.py` + `arbitrageur/exchange.py` + `main.py` + `tests/test_engine.py` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：**在同一标的上做 `long spot + short perp` 的 delta-neutral carry，但不是“只看 funding>0 就上”，而是先过三层 admission（funding 阈值、年化 APR 阈值、spot-perp spread 上限），再按可用资金与单币上限分配仓位。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（可先落地 paper-mode 完整流程；live 仍需补真实撮合/平仓恢复）
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/delta-neutral/apr-ranking/spread-cap/admission/reserve-aware/allocation/binance/bybit/spot-perp/1m/3m/5m/15m/repo/cost/risk
- 证据类型：repo source audit

---

## 1) 这次看的材料

### Repo 主体
- **Author：** Rezzecup
- **Year：** 2026（repo 创建于 2026-03-12）
- **Title：** *Funding Rate Arbitrageur (Binance Spot x Bybit Perpetual)*
- **Venue：** GitHub
- **DOI：** N/A
- **Readable URL：** <https://github.com/Rezzecup/funding-rate-arbitrageur-binance-bybit>
- **Repo URL：** <https://github.com/Rezzecup/funding-rate-arbitrageur-binance-bybit>

### 本轮重点读到的源码事实（不是 README 口号）
1. `engine.py`：
   - 先把 8h funding 换算成年化 APR：`annualize_from_8h_rate()`。
   - 仅保留满足三条件的机会：
     - `funding_rate_pct_8h >= funding_rate_threshold`
     - `spread_pct <= max_spread_pct`
     - `estimated_apr >= min_apr_estimate`
   - 机会按 `estimated_apr` 降序排序后再分配预算。
2. `config.example.yaml`：默认阈值是
   - `funding_rate_threshold = 0.01`（8h）
   - `min_apr_estimate = 12.0`
   - `max_spread_pct = 0.05`
3. 资金分配不是全仓梭哈：
   - `reserve_pct` 先留存
   - `max_per_asset_pct` 限制单币暴露
   - 同时避免重复开同一 symbol。
4. `main.py`：明确只开放 `paper`，`live` 模式公开版主动禁用。

---

## 2) 一句话先回答：这篇东西的 base alpha 是什么？

> **base alpha = post-admission 的 funding carry（delta-neutral）：只在 funding 足够高、年化足够厚、现货-永续价差没超成本容忍时，做 `long spot + short perp`，赚 funding，而不是赌方向。**

这不是纯 filter；它本体就是 raw alpha（carry / relative-value / stat-arb）。

---

## 3) 为什么它值得进当前 short-cycle 素材池

### 3.1 它补的是“admission-first 的 carry 骨架”

我们最近 funding 相关主题很多，但常见问题是：
- 只看单一 funding 数值；
- 忽略 spread 成本；
- 没有统一的仓位预算与容量约束。

这个 repo 的价值不在“funding carry 新不新”，而在它把最容易漏掉的三件事写成了硬规则：
1. `APR gate`（避免低边际 carry）；
2. `spread cap`（避免 paper edge 被执行摩擦吃掉）；
3. `reserve + max_per_asset`（避免“看起来中性，实际上集中爆仓”）。

### 3.2 它和 04-15 那篇 CEX/DEX 论文不重复

- 04-15 论文主线是：**spread shock reversion + duration/forced-exit**。
- 这份 repo 主线是：**admission + allocation 的 carry 执行壳**。

前者更偏“什么时候错价会回摆”，后者更偏“怎么把可交易机会排队、预算、执行”。

---

## 4) 策略拆解（entry / exit / sizing / risk / cost）

### 4.1 Entry（alpha 本体）
对每个 symbol（默认 BTC/ETH/SOL/BNB/ARB）：
1. 拉取 spot/perp + funding snapshot；
2. funding 转成年化 APR；
3. 满足三条件才进候选池：
   - `funding_8h >= th_funding`
   - `apr >= th_apr`
   - `spread_pct <= th_spread`
4. 候选按 `apr` 降序，优先分配。

### 4.2 Exit（repo 公开版需补，但规则已可直接定义）
最小可落地退出规则建议：
- `funding_8h < 0` 或 `< th_funding_exit`：平仓；
- `spread_pct > th_spread_stop`：平仓；
- `time_stop`：持有超过 `N` 个 funding 周期强退；
- `hedge_break`：双腿名义偏离超阈值（如 0.5%）强制再平衡/平仓。

### 4.3 Sizing（源码已有）
- 总资金先扣 `reserve_pct`；
- 每币最大仓位 `max_per_asset_pct`；
- 候选池按可用资金均分并受单币上限截断。

### 4.4 Risk（需从 paper-mode 走向可交易）
- 交易所/腿级限额；
- 资金费率翻负连续 `k` 次即降权；
- 异常成交（一腿成交一腿失败）恢复策略；
- 波动上升阶段动态收紧 `max_spread_pct`。

### 4.5 Cost（必须显式）
- maker/taker 手续费
- 双腿滑点
- 借币或资金占用成本
- 提现/跨所搬运摩擦（若涉及）

---

## 5) 面向 `1m/3m/5m/15m` 的最小实验

> 这条 alpha 的自然频率是 funding 结算周期（慢于 1m），但 **admission/执行/风控** 完全可以短周期化。

### 数据源与口径
- 数据源：Binance/Bybit 公开 funding 与行情 API（或 CCXT 统一口径）
- 公开性：公开可得
- 更新频率：funding 事件级 + 行情分钟级
- 最小可复现实验口径：
  - 用 `1m` 刷新 admission 状态；
  - 用 `5m/15m` 执行调仓与风险检查；
  - 以每次 funding 结算为结算节点记账。

### Baseline v0（可当周跑完）
1. Universe：`BTC/ETH/SOL`
2. 参数起点：
   - `th_funding = 0.01%/8h`
   - `th_apr = 12%`
   - `th_spread = 0.05%`
3. Exit：
   - funding 翻负 or spread 超 0.08%
   - 最长持有 3 个结算周期
4. 记账：
   - `gross funding`
   - `net after fees/slippage`
   - `holding time`
   - `hedge drift`

---

## 6) 下一步怎么测（直接可执行）

做 5 组 A/B（每组都记 post-cost）：

1. **APR gate A/B：`8% / 12% / 20%`**
   - 看提高 admission 门槛后，是否“少做但更干净”。
2. **Spread cap A/B：`3bp / 5bp / 8bp`**
   - 找到 cost cliff 前的稳定区间。
3. **Allocation A/B：equal budget vs APR-proportional budget**
   - 检验“高 APR 倾斜”是否真的提升 net。
4. **Exit A/B：funding<0 即退 vs funding<0 连续两次才退**
   - 平衡过度交易与尾部回撤。
5. **Execution cadence A/B：1m 风控检查 vs 5m 风控检查**
   - 看短周期检查能否显著降低单腿失配损失。

关键观察指标：
- `net bps / cycle`
- `gross→net retention`
- `spread-stop hit rate`
- `single-leg failure rate`
- `capital utilization`
- `PnL concentration by symbol`

---

## 7) 风险与保留意见

1. 公开版 `live` 禁用，真实执行风控并未在仓库中验证。
2. repo 默认 mock 数据路径可跑通，但不代表真实市场可交易性。
3. 未实现完整平仓/异常恢复时，carry 策略会在极端行情暴露“伪中性风险”。
4. funding edge 常见问题不是“信号不存在”，而是“成本后剩不下”。

---

## 8) 一句话结论

> **这份 2026 repo 值得 intake 的点，不是“funding carry”本身，而是它把 carry 交易前最关键的 admission + allocation 规则写成了可执行骨架；对 short-cycle desk，优先价值是把它改成“1m 监控、5m/15m 执行、结算周期记账”的 cost-aware 壳。**

---

## 9) 来源

1. **Rezzecup (2026), _Funding Rate Arbitrageur (Binance Spot x Bybit Perpetual)_**, GitHub Repository.
   - Readable URL: <https://github.com/Rezzecup/funding-rate-arbitrageur-binance-bybit>
   - Repo URL: <https://github.com/Rezzecup/funding-rate-arbitrageur-binance-bybit>
2. **GitHub API metadata（仓库创建时间、stars、topics）**
   - <https://api.github.com/repos/Rezzecup/funding-rate-arbitrageur-binance-bybit>
3. **源码直链（本轮核对）**
   - <https://raw.githubusercontent.com/Rezzecup/funding-rate-arbitrageur-binance-bybit/main/README.md>
   - <https://raw.githubusercontent.com/Rezzecup/funding-rate-arbitrageur-binance-bybit/main/arbitrageur/engine.py>
   - <https://raw.githubusercontent.com/Rezzecup/funding-rate-arbitrageur-binance-bybit/main/arbitrageur/config.py>
   - <https://raw.githubusercontent.com/Rezzecup/funding-rate-arbitrageur-binance-bybit/main/config.example.yaml>
   - <https://raw.githubusercontent.com/Rezzecup/funding-rate-arbitrageur-binance-bybit/main/main.py>
