# 别把这份 2026 BTC 均值回归 repo 只读成日线作业：对 short-cycle desk，更该先测的是 `thresholded oversold crash × symmetric rebound exit`
- 时间：2026-04-08 19:00 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：单资产在短时间发生极端负收益后，做反向均值回归，直到同口径动量修复到正阈值再平仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：single-asset / mean-reversion / oversold-bounce / event-driven / BTC / ETH / SOL / 5m / 15m / public-data
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
我这次看的是 `silas0700/Bitcoin-Mean-Reversion-Backtest`（2026，GitHub）。source audit 主要覆盖 `README.md` 和 `Mean_Reversion_Strategy.py`：repo 的规则非常直接——买入“短时间内跌得离谱”的 BTC，等同口径动量回到正阈值再平仓，并且显式把 taker fee 设成 `0.05%/side`。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是“看起来超卖就抄底”，而是 **`k-bar 累计跌幅 < -阈值` 的极端 oversold 事件 -> 做 bounce -> `k-bar 累计涨幅 > +阈值` 离场**。
- repo 原始日线口径其实不是“稳定常开策略”，而是**极端事件 alpha**：README 给出的 train 最优参数是 `7 days / 37.5% crash`，对应 `Train Sharpe 1.50`、`Train CAGR 53.12%`、`Train MDD -17.54%`；但 2025 out-of-sample 直接变成 `0 trades`，而 buy-and-hold 是 `-27.17%`。这不是坏消息，反而说明它提醒了一个更重要的 desk 事实：**真正有用的 oversold bounce 往往非常稀疏，不能把阈值放松成“天天都想抄底”**。
- 我用 Binance USDⓈ-M 近 `120d` 公共 `5m/15m` 数据按同类逻辑做了 portability probe（long-only、进出都按 taker `5 bps/side`）：
  - `5m`：ETH 在 `12 bars / 3%` 下有 `18` 笔、平均约 `+136.2 bps/笔`、累计约 `+23.0%`；SOL 同参有 `16` 笔、平均约 `+119.8 bps/笔`、累计约 `+14.9%`。
  - 但同样是 ETH，若把阈值放松到 `12 bars / 1%`，会变成 `188` 笔、平均约 `-5.2 bps/笔`、累计约 `-14.5%`。**结论很硬：这条线吃的是“极端事件后的反弹”，不是普通回踩。**
  - `15m`：BTC 在 `4 bars / 2%` 下还有 `14` 笔、平均约 `+68.0 bps/笔`、累计约 `+7.8%`；但 ETH / SOL 同参都转负，说明它当前更像 **major-only / BTC-first** 的事件壳，而不是全币种通用模板。
- 所以这轮最值得带走的不是 repo 的日线参数，而是一个更适合 short-cycle 的翻译：**只做“极端 oversold”事件，不做泛化均值回归；先从 major、固定硬阈值、long-only 版本开始。**

## 3. 为什么和当前项目有关
这条线和当前 desk 的关系很直接：
- 它补的是 **single-asset mean reversion raw alpha**，不是又一篇 pairs / carry / overlay。
- 它能很快映射到 `1m/3m/5m/15m`：只要有公开 K 线，就能先做最小实验。
- 它还天然适合作为后续“过滤层”母体：比如 liquidation spike、OI jump、funding stretch、VPIN/toxic flow，都可以以后再加；但 **第一步先把 raw alpha 本体做干净**。

## 3.5 策略拆解（必填）
**Strategy shell（当前最小可复现版）**
- **Universe**：先只做 `BTC / ETH / SOL` 这类 top-liquid majors；当前证据不支持一上来就广撒 alt basket。
- **Entry**：当过去 `k` 根累计收益 `< -θ`，下一根开盘/收盘做多。
- **Exit**：当过去 `k` 根累计收益 `> +θ` 平仓；若要更实盘，可额外测试 `max-hold` 兜底。
- **Sizing**：第一版先固定名义仓位；第二版再比较 vol-target / ATR-target。
- **Risk**：long-only；单标的同时仅持一笔；避免多次连续补仓把它变成 martingale。
- **Cost**：先按 taker-taker `10 bps round-trip`；如果这都活不下去，就不用再讲更复杂执行。

**当前最值得先记住的 desk 版本**
- `5m`: `lookback=12 bars`、`threshold=3%`，优先看 ETH / SOL
- `15m`: `lookback=4 bars`、`threshold=2%`，优先先看 BTC

## 4. 下一步最该怎么测
1. **先做 fixed-threshold vs vol-normalized-threshold**：把 `3%` / `2%` 换成 `ret_z` 或 `ATR-normalized move`，看不同币之间能否更稳定迁移。
2. **做 major-only admission**：只在 `BTC/ETH/SOL/BNB` 上跑，不要直接扩到长尾；目标是确认这是不是“高流动性大币的极端事件 bounce”。
3. **做 exit A/B**：
   - A：repo 的 `+θ` 对称退出
   - B：`time stop 4/8/12 bars`
   - C：`+θ` 或 `VWAP/EMA 回归` 二选一
   看哪种更适合 `5m/15m`。
4. **做 event layering，但放在第二轮**：只有 base alpha 站住后，再叠 `liquidation / OI / funding / toxic flow` 过滤器；不要反过来把 filter 当 alpha 本体。

## 5. 风险与边界
- **极度稀疏**：repo 的原始日线版本已经证明，阈值一旦设得足够极端，交易会非常少；这是它的本性，不是 bug。
- **跨币不对称**：当前 `15m` 证据明显偏向 BTC，说明不能默认 ETH/SOL 会复制同样表现。
- **阈值一放松就容易死**：ETH `5m 12 bars / 1%` 已经给出反例，说明普通回踩并不够支撑成本后均值回归。
- **当前仍是 long-only 读法**：是否存在“极端上涨后做 short fade”的对称 alpha，本轮没有证明，别偷换。

## 6. 来源与可复现线索
### Repo
- **Maintainer / Year**: `silas0700` / 2026
- **Title**: *Bitcoin Mean Reversion Backtest*
- **Venue**: GitHub
- **DOI**: None
- **Readable URL**: <https://github.com/silas0700/Bitcoin-Mean-Reversion-Backtest>
- **Repo URL**: <https://github.com/silas0700/Bitcoin-Mean-Reversion-Backtest>
- **Audited files**:
  - `README.md`
  - `Mean_Reversion_Strategy.py`

### Public data used for portability probe
- **Source**: Binance USDⓈ-M Futures public klines
- **Publicness**: 公开可得，无需私有 key
- **Frequency used**: `5m / 15m`
- **Sample**: 近 `120d`
- **Minimal replication lens**: `top-liquid majors` 上测试 `k-bar crash -> symmetric rebound exit`，先看 `post-cost expectancy / trade` 与 `trade count` 是否同时成立

## 7. 一句话结论
这条线值得进研究池，但**正确姿势不是“跌了就抄底”**，而是：**只做 major、只做极端 oversold 事件、先用高阈值版本拿 first verdict。**
