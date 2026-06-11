# PSAR 别单扛 15m alpha：把它放到 30m/1h 做结构锚，EMA slope + micro filter 才更像可测 continuation
- 时间：2026-03-18 02:55 UTC
- 类型：GitHub
- 主题标签：ema/psar/raw-alpha/continuation/regime/filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 oscar0rdz 在 2025 年创建的 GitHub 仓库 **BotScalpingTwinRange**。它不是在说“PSAR 本身就是短周期 alpha”，而是把 **PSAR 30m / EMA 30m slope / ATR% / micro bias** 拆成不同层：PSAR 负责方向锚，EMA 负责趋势质量，ATR 负责 regime 与仓位，5m/1m 负责 timing。这个读法正好能补 `EMA / PSAR raw alpha focus` 还缺的一块：**PSAR 到底该做信号，还是做 gate。**

## 2. 核心结论
- **一句话核心结论**：对 15m desk 来说，PSAR 更像**高一层的结构锚 / flip veto**，不该继续硬扮成和 EMA 并列的原始入场 alpha。
- **一句话证明方式**：这个 repo 的关键不是 README 口号，而是源码里真的把角色拆开了——`trend.py` 用 `0.6 * psar_30_dir + 0.4 * ema_30_dir + slope_factor` 组合 macro score；`score_utils.py` 再把 `ATR% 0.7~1.8` 当甜蜜区、`<0.4` 或 `>2.5` 当坏环境；`risk_utils.py` 则把 `MICRO / NORMAL / EXPLOSIVE` 映射到不同 `SL/TP` 与持仓长度。
- 最值得复用的不是整套多周期机器人，而是 3 个角色分工：
  1. **PSAR 只管方向翻转许可**，不要单独负责 entry edge；
  2. **EMA slope / EMA dir 才是 continuation 质量层**，回答“顺势到底顺不顺”；
  3. **ATR 更像仓位与 regime 层**，回答“能不能做、该做多大”，而不是“方向是什么”。
- 这比继续讨论“PSAR vs EMA 谁更强”更有 desk 价值，因为当前真正需要的不是给 PSAR 找神奇参数，而是先把它从 raw alpha 身份里降级到**结构过滤 / 反手条件**。
- 之所以这轮值得优先认领它，而不是继续围绕 breakout-short / Fibonacci 再加材料，是因为那两条线刚拿到 fresh repo intake；反而 `EMA / PSAR raw alpha focus` 还缺一个足够具体的工程读法，告诉我们 **PSAR 放在哪一层才合理**。

## 3. 为什么和当前项目有关
它直接服务 `EMA / PSAR raw alpha focus`：
- 当前项目已经看到 **裸 EMA / 裸 PSAR 在成本后很脆**，但还没完全讲清楚 PSAR 的合适岗位；
- 这个 repo 给的更像一个可执行答案：**PSAR 用来定义“当前大方向有没有翻车”，EMA slope 用来定义“这段延续值不值得跟”，micro bias / range filter 用来定义“现在进是不是太吵”。**
- 对 `breakout-short follow-up` 和 `Fibonacci retest_hold` 也有间接启发：以后看到回踩或 breakdown，不一定先问“形态好不好看”，而要先问 **高层 PSAR/EMA 方向有没有已经反手**。

## 4. 可复刻的最小实验
- **研究假设**：在 `15m` crypto 上，把 PSAR 从“同级入场信号”降为“高一级 regime gate”，会比裸 `EMA` 或裸 `PSAR` 更稳，尤其能减少 flip 后立刻打脸的 early failure。
- **三臂最小定义**：
  1. `EMA_raw`：15m `ema_fast > ema_slow` + slope 过门槛即做多，反向做空；
  2. `PSAR_raw`：15m `close` 穿越 `PSAR` 翻向即入场；
  3. `PSAR_anchor + EMA_confirm`：`1h`（或 `30m`）PSAR 定方向，15m `EMA dir + slope` 做确认，5m 只做简单 micro veto（例如 fast<slow 时不追多）。
- **最小回测切口**：`BTC / ETH / SOL`，Binance perpetual，样本先做最近 `180~365` 天，`next-bar open` 入场，`hold 6~12 bars`，`no-overlap`，成本至少看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost return`、`positive_asset_ratio`、`trade_count`、`flip-to-fail rate`（可先定义成入场后 `4` 根内 hit stop 或反向信号出现）。
- **yes/no 问题**：如果 `PSAR_anchor + EMA_confirm` 没有明显改善 `flip-to-fail rate`，那就说明 PSAR 作为高层 gate 也不够值钱；如果它能在不把交易数压死的前提下明显减少 early failure，这条线就比继续找“PSAR 最佳参数”更值得推进。

## 5. 风险与保留意见
- 这仍是 **repo 工程证据**，不是论文级验证；仓库没有可信的公开 OOS 结果表，不能把它当成已验证 alpha。
- 原仓库主框架是 `30m / 5m / 1m`，还带 `ALWAYS_IN_MARKET` 与多对交易选择，直接搬到我们的 `15m` desk 很容易过厚、过忙、过拟合。
- README 里有一些“动态权重 / ADX”叙述，但真正该信的还是源码里能明确核到的部分；因此这轮更适合拿它当 **角色分工模板**，而不是整套执行模板。
- 如果最终发现 edge 全来自极短执行层而不是高层锚，那它对 15m 的帮助会明显缩水。

## 6. 来源
- oscar0rdz. (2025). *BotScalpingTwinRange*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/oscar0rdz/BotScalpingTwinRange>
  - Readable URL: <https://github.com/oscar0rdz/BotScalpingTwinRange/blob/main/README.md>
- 关键实现文件：
  - `psar_scalper/src/trend.py`: <https://github.com/oscar0rdz/BotScalpingTwinRange/blob/main/psar_scalper/src/trend.py>
  - `psar_scalper/src/score_utils.py`: <https://github.com/oscar0rdz/BotScalpingTwinRange/blob/main/psar_scalper/src/score_utils.py>
  - `psar_scalper/src/risk_utils.py`: <https://github.com/oscar0rdz/BotScalpingTwinRange/blob/main/psar_scalper/src/risk_utils.py>
  - `SISTEMA_30M_5M_1M.md`: <https://github.com/oscar0rdz/BotScalpingTwinRange/blob/main/SISTEMA_30M_5M_1M.md>
