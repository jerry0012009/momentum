# 别把这份 Hyperliquid repo 只读成“又一组策略回测”：对 short-cycle crypto desk，更该先补的是「Roll spread + Amihud + premium-tail」这层 shared market-quality gate

- 时间：2026-04-21 09:46 UTC
- 类型：GitHub / microstructure toolkit
- 主题类型：overlay
- 基础 alpha：**无独立 base alpha；它服务于 `mark-vs-oracle dislocation fade`、`funding/basis carry admission`、`breakout child execution` 这三类 raw alpha 的开仓否决 / size-down / universe 过滤。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay/filter/microstructure/market-quality/roll-spread/amihud/kyle-lambda/premium/basis/hyperliquid/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：工程经验 + repo 源码 + 公共数据快检

## 1. 这次看了什么
这次主看 2026 GitHub 仓库 **andreaambrosio / hype-backtesting**，但不再重复它已经被我们多次 intake 的 `basis reversion / funding carry / weekend reopen` 主策略分支，而是单独抽出它的 **`src/research/microstructure.py` market-quality toolkit**。这轮更值得拿回 desk 的，不是“又发现一条新 alpha”，而是：**给现有 raw alpha 补一层便宜、可公开复现、可直接映射到 `1m/3m/5m/15m` 的 market-quality gate。**

## 2. 核心结论
- **一句话核心结论：** 对 Hyperliquid 这类 perp venue，很多短周期 alpha 不是先死在方向，而是先死在 **spread / impact / premium tail / depth** 突然恶化；所以先补 market-quality gate，比继续硬抠同一批 basis/funding 参数更值。
- repo 明确把 microstructure toolkit 单列出来，包含 **Roll spread、Amihud illiquidity、Kyle’s lambda、basis decomposition、depth profile、funding carry attribution**，这说明作者自己也把“先量化可交易性”当成独立组件，不只当附属注释。
- 我做的 Hyperliquid 公共数据快检里，按 `day_ntl_vlm >= 1,000,000` 过滤后，**liquid 子集共有 `54` 个名字，绝对 premium 中位数约 `5.14 bps`，P95 约 `19.05 bps`**；这说明对 liquid names，premium tail 不是不存在，但明显有层级差异，完全可以先做 **universe 过滤 + percentile veto**。
- 同一个 repo README 还给出 live sample：**BTC premium 中位数约 `-3.22 bps`、ETH `-3.78 bps`、SOL `-8.43 bps`、TURBO `-9.64 bps`**。这不是让我们直接做 slow carry，而是提醒：**不同币的“正常 premium / liquidity 状态”底噪不同，阈值不能一把尺子量全场。**
- 所以这篇更适合作为 **shared gate / sizing overlay**：
  1. 给 `premium-dislocation fade` 做“只在 spread/impact 没爆炸时才接”；
  2. 给 `funding/basis carry` 做“只在 premium 尾部没有失控时才收租”；
  3. 给 `breakout / continuation` 做“薄书 + 高 impact 时降仓，不把噪音冲击误读成趋势”。

## 3. 为什么和当前项目有关
这轮没继续补 raw alpha，不是因为 raw alpha 不重要，而是因为这份 repo 里最像 raw alpha 的几条（basis / funding / weekend）在 digest 池里已经被反复 intake；再写一次边际信息很低。相反，**把它尚未入库的 market-quality 组件拆出来**，能直接服务多条已在池中的 raw alpha：
- `mark-vs-oracle premium fade`
- `funding / basis carry`
- `single-name breakout / continuation`
- `Hyperliquid cross-sectional overextension fade`

换句话说，它不是 alpha 本体，但它能提高现有 alpha 的 admission 质量，减少“方向对了但交易环境太差”的假阳性。

## 3.5 策略拆解（必填）
- 方向属性：无；属于共享风控 / 准入层
- 基础 alpha：无独立 base alpha
- regime：`liquidity-good / liquidity-fragile / premium-tail-stressed`
- filter / veto：`roll_spread_z`、`amihud_z`、`abs(premium)_pctile`、可选 `kyle_lambda_z`
- risk / sizing / execution overlay：高脆弱度时 `skip / size-down / maker-first / wider hurdle`

## 4. 可复刻的最小实验
**研究假设：** 现有 short-cycle alpha 在“market-quality 差”的 bar 上，post-cost PnL 明显更差；因此加 gate 后，trade count 会下降，但 net expectancy / drawdown / tail loss 会改善。

**最小实验口径：**
1. 先选 2 条已在池里的 raw alpha：
   - `premium-dislocation fade`
   - `15m breakout / continuation` 或 `funding carry child execution`
2. 数据源：Hyperliquid 公共 API（repo README 与 `config/settings.yaml` 明示 `https://api.hyperliquid.xyz`，无需 key）；更新频率可到分钟级 / 更高频；最小实验先落 `1m` 或 `5m` 聚合。
3. 每根 bar 计算：
   - `amihud = abs(ret_1m) / dollar_volume_1m`
   - `premium_bps = (mark - oracle) / oracle * 10_000`
   - `premium_tail = rolling_pctile(abs(premium_bps), 3d~7d)`
   - 若能拿到逐笔或更细数据，再补 `roll_spread` / `kyle_lambda`
4. 做三组对照：
   - baseline（无 gate）
   - veto：`premium_tail > 0.95` 或 `amihud_z > 2` 禁止开仓
   - size-down：上述条件触发时仓位砍半
5. 必看结果：`post-cost return`、`max drawdown`、`trade count`、`avg trade pnl`、`worst 5 trades`。

## 5. 来源与可复用点
### 主来源
- **Author / Year / Title / Venue：** Andrea Ambrosio (2026), *hype-backtesting*, GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/andreaambrosio/hype-backtesting>
- **Repo URL：** <https://github.com/andreaambrosio/hype-backtesting>
- **关键源码：**
  - `README.md`
  - `src/research/microstructure.py`
  - `research/run_hip3_analysis.py`
  - `config/settings.yaml`

### 理论地基（repo 自带引用）
- Roll, R. (1984). *A Simple Implicit Measure of the Effective Bid-Ask Spread*.
- Kyle, A. S. (1985). *Continuous Auctions and Insider Trading*.
- O'Hara, M. (1995). *Market Microstructure Theory*.
- Hasbrouck, J. (2007). *Empirical Market Microstructure*.
- Amihud, Y. (2002). *Illiquidity and Stock Returns*.

## 6. 这轮该记住什么
> **别再把 liquidity / spread / premium tail 只当 execution 备注。**
> 对 short-cycle crypto desk，它更像一层共享 admission gate：不是帮你“发明方向”，而是帮你少在最不该出手的时候出手。

## 7. 附：本轮 public-data 快检产物
- `reports/artifacts/quant_digests/2026-04-21_hl_marketquality_snapshot.csv`
- `reports/artifacts/quant_digests/2026-04-21_hl_marketquality_liquid_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_hl_marketquality_probe.md`
