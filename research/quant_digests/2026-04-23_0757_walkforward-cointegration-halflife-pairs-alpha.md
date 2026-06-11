# 别把这篇 2023 crypto pairs 论文只读成“又一篇配对教材”：对 short-cycle desk，更该先保留的是「walk-forward cointegration admission × half-life-bounded spread fade」这条 raw alpha

- 时间：2026-04-23 07:57 UTC
- 类型：2023 SSRN 论文摘要/实现镜像复核（QuantBuffet / Harbourfront / Crossref / OpenAlex）+ Binance USDⓈ-M public-data walk-forward portability probe（2026-04-23）
- 主题类型：raw alpha
- 基础 alpha：**先用协整关系筛出会回归的 pair，再在 `1m/3m/5m/15m` 执行层对 spread 的极端偏离做反向 fade，赌的是两腿相对错价回归，而不是单腿方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/walk-forward/half-life/spread-zscore/15m/5m/paper/public-data/cost/risk
- 证据类型：paper abstract + strategy mirror + metadata + public-data portability

## 1. 这次看了什么
这次主看：
- **Chiara Lesa, Ronald Hochreiter (2023), _Cryptocurrency Pair Trading_**
- Venue：SSRN Electronic Journal
- DOI：`10.2139/ssrn.4433530`
- Readable URL：<https://doi.org/10.2139/ssrn.4433530>
- Mirror / summary：
  - QuantBuffet：<https://quantbuffet.com/en/2024/04/15/pairs-trading-in-cryptocurrencies/>
  - Harbourfront：<https://harbourfrontquant.substack.com/p/pairs-trading-in-the-cryptocurrency>
- Repo URL：N/A

先把一句话说透：**这篇东西的 base alpha 很清楚，就是 pair spread 的均值回复，不是 filter，不是 overlay。**

对当前 desk 来说，最值钱的不是“crypto 也能做 pairs”这种废话，而是更具体的三件事：
1. **pair admission 应优先保留 `cointegration-first`，而不是只看 distance；**
2. **short-cycle 上更自然的落地法是 walk-forward 重选 pair，而不是一组选到底；**
3. **风险控制别先本能套 hard stop，更该先看 half-life/time-stop/spread-normalization。**

## 2. 核心结论
- **一句话核心结论：** 对 short-cycle crypto desk，这篇 paper 最值得留下来的，不是“pairs 也能赚钱”，而是 **walk-forward 协整筛选 + half-life 约束后的 spread fade** 更像能复现的原型；很多看似“更安全”的 hard stop，反而可能把 MR edge 自己砍掉。
- **一句话证明方式：** 论文把 distance vs cointegration、daily vs intraday、with-stop vs no-stop 放在同一框架下比较；我再用 Binance USDⓈ-M 公共数据做了 `15m/5m` walk-forward portability probe，看今天这种 perp 环境里哪类 pair 还活着。
- 公开二级来源一致指向：**cointegration 选 pair 通常优于 distance，intraday 往往比慢频更强，但机械 stop-loss 会明显伤 edge。**
- 我这轮本地快检里，`15m` 最厚 pocket 是 **`BNBUSDT/DOGEUSDT`：14 笔、avg gross `+54.37 bps/笔`、粗扣 `8 bps` 后 avg net `+46.37 bps/笔`、cum net `+6.49%`、Sharpe `6.24`**。
- `15m` 第二个可留意 pocket 是 **`SOLUSDT/DOGEUSDT`：18 笔、avg net `+13.08 bps/笔`、cum net `+2.35%`**；其余 4 个 `15m` pair 都已转负，说明这条线不是“随便找两腿都能做”。
- `5m` 这次反而出现了更稳的横截面 pocket：**5 个 pair 里 3 个为正**，其中 `ADAUSDT/LINKUSDT` `+11.72 bps/笔`、`DOGEUSDT/LINKUSDT` `+10.02 bps/笔`、`ADAUSDT/DOGEUSDT` `+9.55 bps/笔`；说明这套东西可以直接进入 `5m` pairs raw alpha 候选池，而不是只留在 `15m`。

## 3. 为什么和当前项目有关
这轮和当前 desk 的关系非常直接：
- 它补的是 **raw alpha 素材池里的 pairs / stat-arb / relative-value**，不是又一层 shared gate；
- 它天然能写成完整策略：`entry / exit / sizing / risk / cost` 都有第一版骨架；
- 它和最近很多“更复杂的 basket / copula / ML pairs”不同，这条线更适合当 **plain-vanilla 可落地 baseline**；
- 如果后面要叠加 overlay，最自然的是 funding veto、深度 veto、maker-first execution，而不是先把本体搞复杂。

## 3.5 策略拆解（必填）
- 方向属性：**relative-value / market-neutral / pairs / mean reversion**
- 基础 alpha：**协整 pair 的 spread 偏离长期均衡后，未来更可能回归。**
- regime：**pair 关系仍稳定、ADF 仍过、half-life 仍在可交易区间。**
- filter / veto：**cointegration 失效、half-life 过长、两腿流动性不足、funding 冲突、事件窗异常波动。**
- risk / sizing / execution overlay：**rolling OLS hedge ratio、spread z-score 入场、time-stop/half-life stop、gross cap、maker-first 或 child execution。**

## 4. 可复刻的最小实验
**研究假设：** 如果用 walk-forward 方式反复重选 pair，并把 `half-life` 当 admission gate，crypto perp 上仍能留下少数成本后为正的 spread fade pocket。

**一个可计算定义：**
1. universe 先取 6~10 个 liquid USDT-M majors / mid-caps；
2. formation 窗用 `15m` 最近 `14d` 或 `5m` 最近 `7d`；
3. pair admission：`cointegration p`、`ADF p`、`half-life` 同时过线；
4. rolling OLS 算 hedge ratio，spread 标准化成 `z-score`；
5. `|z| >= 2` 入场，`z` 回到 `0~0.5` 退出；
6. 风控先只用 `time-stop = 1~1.5 × half-life`，不要先上 directional hard stop；
7. 成本先按 round-trip `8 bps`。

**最小回测切口：**
- 资产：`ADA / DOGE / LINK / SOL / BNB / XRP`
- 周期：`5m` 与 `15m`
- 样本：最近 `30~60d`
- 先看指标：`avg net bps/笔`、`trade count`，再看 `cum net` 与 `Sharpe`

**下一步怎么测：**
1. **A/B `cointegration-first` vs `distance-first`**；
2. **A/B `no-stop` vs `time-stop` vs `spread-stop`**；
3. **扫 `1.5σ / 2.0σ / 2.5σ` 与 `0.5× / 1.0× / 1.5× half-life` 的 time-stop**；
4. **把 `5m` 正 pocket 先做 top-1 strongest-only router**，不要一上来平铺所有 pair；
5. **补 maker/taker friction ladder（4/8/12 bps）**，确认 edge 不是只活在粗糙成本假设里。

## 5. 风险与保留意见
- 这轮主证据仍不是论文全文，而是 DOI metadata + 二级镜像 + 自己的 public-data probe；**可作 intake，但还不算 paper-faithful replication。**
- 当前正 pocket 高度集中在 **DOGE-linked** pairs，说明这更像近期 regime pocket，不应直接当“普适 pairs 圣杯”。
- `15m` 虽然出现超厚 pocket，但只有 2/6 pair 成本后为正；这条线的正确姿势更像 **先做 strongest-only / sparse deployment**。
- `no-stop` 不等于不控风险。这里真正该测的是 **half-life/time-stop 与 spread-normalization**，而不是把单腿 directional stop 生搬到 pairs MR 上。

## 6. 来源
1. **Lesa, C., & Hochreiter, R. (2023). _Cryptocurrency Pair Trading_. SSRN Electronic Journal.**
   - DOI：`10.2139/ssrn.4433530`
   - Readable URL：<https://doi.org/10.2139/ssrn.4433530>
2. **QuantBuffet strategy mirror**
   - <https://quantbuffet.com/en/2024/04/15/pairs-trading-in-cryptocurrencies/>
3. **Harbourfront summary**
   - <https://harbourfrontquant.substack.com/p/pairs-trading-in-the-cryptocurrency>
4. **Local portability artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/walkforward_pairs_portability_probe_2026-04-23.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/walkforward_pairs_portability_trades_2026-04-23.csv`
