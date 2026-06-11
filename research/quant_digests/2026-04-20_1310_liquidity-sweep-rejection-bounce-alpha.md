# 别把 smart-money-concepts 只读成 ICT 指标包：对 short-cycle crypto desk，更该先拆的是「downside liquidity sweep rejection → panic-bounce continuation」这条 raw alpha
- 时间：2026-04-20 13:10 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：向下扫穿前序流动性低点、但收盘重新站回区间内的 `liquidity sweep rejection`，随后做 `long` 的短周期反弹延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / liquidity-sweep / rejection / intraday / 5m / 15m / panic-bounce / Binance
- 证据类型：工程经验 + repo source audit + public-data portability probe

## 1. 这次看了什么
看的是 `joshyattridge/smart-money-concepts`（MIT，⭐1501，2026-04-03 仍有代码更新）。这个仓把 ICT/SMC 常见对象做成 Python 指标库：`swing highs/lows`、`liquidity`、`BOS/CHOCH`、`FVG`、`OB` 等。对我们更有用的，不是把整套术语原样搬进策略，而是先抽出一个最能独立下单的 base alpha：**价格先刺穿前序低点、但收盘重新站回去，这往往不是“趋势继续”，而更像一次短期挤兑后的反抽起点。**

## 2. 核心结论
- 一句话核心结论：**SMC 里最值得 desk 先拿来试的，不是复杂结构叙事，而是最朴素、最可 causal 化的 `downside sweep rejection` 多头反弹。**
- 一句话证明方式：**我没有直接照搬 repo 里带前视性的 swing 定义，而是改成 causal 的“过去 48 根 `15m` 最低点被扫穿、但本根重新收回”规则，并用 Binance USDⓈ-M 公共 K 线做了 10 个主流币 portability probe。**
- `15m` 全样本（10 个 liquid majors，最近 `1500` 根）里，downside+upside 双边混合不够干净；但**只保留 downside sweep→long** 后明显更像样：`n=386` 时 next `8/12` bars 约 `+7.39 / +8.58 bps gross`。
- 再加 stricter admission：`vol_z>0.5`、`|ret_z|>1`、`|CLV|<0.4`（说明是“刺破后收回”，不是收在极端边缘），`15m long-only` 只剩 `n=48`，但 next `4/8/12` bars 约 `+19.97 / +75.05 / +55.36 bps gross`，win rate 约 `66.7% / 72.9% / 62.5%`。
- 同刻若只做 strongest 一档（`vol_z + |ret_z|` 最高），`15m top1 long router` 约 `n=24`，next `8` bars 仍有 `+42.43 bps gross`，说明这条线不一定非得做全市场篮子。
- `5m` 直接压缩成更快版本（过去 `144` 根 `5m` 低点被扫穿后收回，近 `1500` 根样本）事件不多，但当前 pocket 很强：next `3/6/12` bars 约 `+23.40 / +26.90 / +32.08 bps gross`；所以它既可以是 `15m` 母信号，也可能有独立 `5m` 玩法。

## 3. 为什么和当前项目有关
这条线和最近 desk 在补的 raw alpha 池高度相关：它不是单纯 filter，也不是“结构解释学”，而是一条**可独立下单的短周期 mean-reversion / panic-bounce raw alpha**。同时它还能和已有组件自然拼接：
- 可接 `volume spike` 当 admission
- 可接 `market panic / event veto` 当风险边界
- 可接 `5m` child execution 优化入场
- 若后续想回到更完整的 SMC 框架，再把 `BOS/CHOCH/FVG` 当确认层，而不是先把系统复杂化

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产
- 基础 alpha：downside liquidity sweep rejection 后的短线反弹延续
- regime：更适合短时恐慌、局部流动性踩踏、但未演化成持续单边崩跌的环境
- filter / veto：`vol_z>0.5`、`|ret_z|>1`、`|CLV|<0.4`；若 BTC 同步大阴延续且未收回，可 veto
- risk / sizing / execution overlay：下一根开盘入场；先看 fixed hold `4~8` bars；止损可放 sweep 低点下方 `0.5~0.8 ATR`；单笔风险固定，粗扣 round-trip `8bps`

## 4. 可复刻的最小实验
- 研究假设：**被扫穿的前低如果当根被迅速收回，且伴随放量与异常波动，后面 `1~3h` 往往不是继续崩，而是恐慌后的 bounce 延续。**
- 可计算定义：
  - `prior_low = rolling_min(low.shift(1), 48)`（`15m`，约过去 `12h`）
  - `signal_long = low < prior_low and close > prior_low`
  - `strict gate = vol_z > 0.5 and abs(ret_z) > 1 and abs(CLV) < 0.4`
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`，先跑最近 `60~90d` 的 `15m`；再补 `5m` 最近 `30d`
- 最先看两个指标：`gross/net bps per trade`、`事件数 n`；第三个再看 `max adverse excursion`
- 下一步怎么测：
  1. 把 `15m strict long-only` 做成标准事件回测，加入 `8bps` round-trip 成本；
  2. 对比 `fixed hold 4/8/12` vs `ATR-trailing`；
  3. 增加 `BTC regime veto`（若 BTC 同向大跌未收回则不开）；
  4. 测 `15m` 母信号 + `5m` child limit entry 是否能把成本后 edge 留住。

## 5. 风险与保留意见
- repo 里的不少 SMC 对象依赖 swing/high-low 定义，天然容易带前视；**真正迁移到实盘时必须先做 causal 改写**，不能原样拿来。
- 当前 strongest pocket 明显偏 downside long，**upside sweep→short 在这批样本里并不好**；别把它误当成对称双边策略。
- `5m` 结果样本数还小（近 `1500` 根只抓到 `36` 笔），更像“值得继续追”的 pocket，不是已完成验证。
- 这类信号对极端趋势市很敏感；如果 sweep 本身是更大级别崩跌开始，反而容易抄在半山腰。

## 6. 来源
- Joshy Attridge. *smart-money-concepts*. GitHub repository.
- Repo URL: `https://github.com/joshyattridge/smart-money-concepts`
- Readable URL: `https://github.com/joshyattridge/smart-money-concepts/blob/master/README.md`
- Key source file: `https://github.com/joshyattridge/smart-money-concepts/blob/master/smartmoneyconcepts/smc.py`
- Probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-20_smc_liquidity_sweep_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-20_smc_liquidity_sweep_probe_events.csv`
  - `reports/artifacts/quant_digests/2026-04-20_smc_liquidity_sweep_probe_top1_router.csv`
  - `reports/artifacts/quant_digests/2026-04-20_smc_liquidity_sweep_5m_summary.csv`
