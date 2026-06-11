# Breakout 不是穿线就完：ATR 弹性回踩区 + bounce reclaim，更像 15m 可测的 retest_hold 确认层
- 时间：2026-03-18 02:26 UTC
- 类型：GitHub
- 主题标签：breakout-short / retest-hold / confirmation / atr / mtf / repo / crypto / 15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 TheVision333 在 2026-02-23 更新的 GitHub 仓库 **trading-bot**。它表面上是一个 breakout + retest 的加密交易机器人，但对我们更值钱的不是“整套策略照抄”，而是它把 **breakout → 等回踩 → 看是否站回/压回 → 再入场** 写成了一个带因果约束的状态机，直接贴近 `V3 breakout-short follow-up` 和 `Fibonacci confirmation / retest_hold` 两条收口线。

## 2. 核心结论
- **一句话核心结论**：对 15m 来说，`retest_hold` 更像一个**波动率缩放的确认层**，而不是“碰到那根线就算回踩成功”。
- **一句话证明方式**：这个 repo 不是靠画图讲故事，而是把确认 swing 的滞后、HTF 只向后对齐、retest 超时取消、深度失效和 bounce 入场全部写进代码状态机里，至少把“不能偷看未来”这件事先做诚实了。
- 最值得复用的模块有 3 个：
  1. **breakout candle quality**：要求实体至少占整根 K 线范围的 `50%`，且多头 close 在区间顶部 `30%`、空头在底部 `30%`；
  2. **ATR retest zone**：不是死守固定百分比，而是要求价格在突破位附近 `0.5 ATR` 内完成回踩；
  3. **retest invalidation + bounce reclaim**：若 close 穿越突破位超过 `1 ATR` 或 `20` 根内不回踩，setup 直接作废；真正入场要等价格重新站回/压回该水平，且 bounce K 线方向一致。
- 这比单纯 `Fibonacci 点位回踩` 更适合 desk：Fib 线位仍可保留，但真正决定要不要做单的，应该是 **“回踩有没有在可容忍波动区间内完成、且有没有出现 re-claim / re-break”**。
- 对 `breakout-short follow-up` 也有直接启发：repo 的 short 侧不是“跌破就空”，而是先确认 breakdown candle 够像样，再等价格回抽失败、RSI 在回抽期没有重新变强，才允许继续追空。

## 3. 为什么和当前项目有关
这轮值得做它，是因为它几乎同时服务三条收口线里最紧的两条：
- 对 `V3 final-verdict / breakout-short follow-up`：它给了一个很清楚的 **continuation vs failure** 分界，重点不是跌破本身，而是“回抽后能不能重新压回去”。
- 对 `Fibonacci confirmation / retest_hold`：它提供了比“回到 Fib 线附近”更可计算的升级版——**ATR 宽度回踩区 + reclaim**。
- 对 `EMA / PSAR raw alpha focus`：这套东西更适合先当 **entry veto / confirmation overlay**，而不是再让 EMA 或 PSAR 单独扛 alpha。

## 4. 可复刻的最小实验
- **研究假设**：在 `15m` crypto 上，把 `retest_hold` 从“固定线位触碰”改成“`0.5 ATR` 回踩区 + bounce reclaim”，能减少假突破/假跌破，尤其能帮助 `breakout-short` 的 continuation 判断。
- **可计算定义**：
  - level：先用当前已有的 `confirmed swing high/low`；Fib 版本可把 level 改成 `38.2/50/61.8` 回撤位；
  - breakout：close 首次收在 level 之外；
  - retest：之后 `1~8` 根 15m K 内，价格回到 level 附近 `<= 0.5 ATR`；
  - entry：回踩后 close 再次收回突破方向，且 bounce K 线与方向一致；
  - invalidation：若 close 反向穿越 level 超过 `1 ATR`，或超时仍未回踩，则取消 setup。
- **最小回测切口**：`BTC / ETH / SOL`，Binance perpetual，`15m` 信号，`1h` 作为 HTF 结构过滤；样本先做最近 `180~365` 天；成本至少看 `6 / 10 / 15 bps per side`。
- **最先看的 2 个指标**：`成本后收益` + `false-break rate`（可先定义成入场后 `4` 根内 hit stop 或 `H+4/H+8` continuation 为负）。如果这两项没改善，就别再给 retest_hold 继续加装饰。

## 5. 风险与保留意见
- 这只是 **高信号 repo intake**，不是论文验证；仓库里目前没有可信的公开结果表，不能把它当成已验证 alpha。
- 原仓库主回测在 `1h / 4h`，下放到 `15m` 后，`RVOL / ADX / RSI / MACD / EMA / HTF structure` 这一整串过滤可能会把交易数压得太低。
- 它的真正价值更像 **确认层骨架**，不是独立主信号；如果直接整套搬运，很可能变成“条件很多、交易很少、OOS 很脆”。
- swing 结构虽然做了确认滞后处理，但 `SWING_LOOKBACK=5`、`RETEST_TIMEOUT=20` 等参数仍需要 15m 语境下重新标定。

## 6. 来源
- TheVision333. (2026). *trading-bot: Crypto trading bot with breakout and retest strategies - backtesting on Binance, live execution on Hyperliquid*.
  - Repo URL: <https://github.com/TheVision333/trading-bot>
  - Repo API summary: <https://api.github.com/repos/TheVision333/trading-bot>
  - Key files:
    - `strategy/retest_signals.py`: <https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/retest_signals.py>
    - `strategy/market_structure.py`: <https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/market_structure.py>
    - `strategy/mtf.py`: <https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/mtf.py>
    - `config.py`: <https://raw.githubusercontent.com/TheVision333/trading-bot/main/config.py>
