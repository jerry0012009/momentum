# 别把 breakout 的判决边界继续画在 wick 上：`body-defined zone re-entry` 更像 15m 的 honest failure verdict
- 时间：2026-03-19 22:56 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/body-zone/accepted-price/reentry/failure-verdict/confirmation/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ Binance Futures 公开数据代理快检

## 1. 这次看了什么
这次继续看 **Harro Moen（MoDiggler75, 2026）** 的仓库 `crypto-trading-bot`，但重点不再是前一版的 `outside-close → back-inside-close` 状态机，而是 `backtest_4hr_breakout_v2.py` 里一个更适合我们 desk 的细节：作者把 breakout zone 的 `A/B` 定义成**第一根 4h candle 的最高/最低收盘价（也就是 body 边界）**，不是整根 wick 高低；同时还显式过滤 doji。对 15m 来说，这更像在区分：**wick 是探路，body 才是被市场接受的价格区。**

## 2. 核心结论
- **一句话核心结论**：对 `V3 final-verdict / breakout-short follow-up`，与其看到价格收回 wick 区就判失败，更值得先等它**收回 body-defined accepted zone**；这比“刚回箱体就反手”更诚实。
- **一句话证明方式**：repo 直接把 zone 写成 `highest/lowest closing price`，我又用 **Binance Futures BTC/ETH/SOL 15m、180 天** 做了同源代理快检：对同一批先 `wick breakout` 的事件，等到 **body-zone re-entry** 再判反向，整体比 `wick-zone re-entry` 更少被噪音骗。
- 快检结果（双边成本先按 **10 bps/side**）：
  - **4-bar**：`body verdict` 平均 **-15.3 bps**，好于 `wick verdict` 的 **-21.4 bps**；
  - **8-bar**：`body verdict` 平均 **-11.4 bps**，好于 `wick verdict` 的 **-18.6 bps**；
  - **long 侧（底部假破后收回）**改善最明显：8-bar 从 **-24.8 bps** 改善到 **-12.9 bps**；
  - **short 侧（顶部假破后收回）**也改善，但幅度较小：8-bar 从 **-12.1 bps** 到 **-9.9 bps**。
- 这说明它**还不够强到单独做 alpha**，但很像值得拿来收紧 failure verdict / retest_hold 的**判决边界**：不是“摸回去就算”，而是“回到被接受的 body 区才算”。
- 币种上也有明显异质性：这轮代理里 **SOL 的 body verdict 8-bar 已接近持平（+0.5 bps）**，但 **ETH 仍偏弱**，所以它更像 shared gate，不像全市场万能主信号。

## 3. 为什么和当前项目直接相关
- **V3 final-verdict / breakout-short follow-up**：这条最直接。之前的 `outside-close → back-inside-close` 已经告诉我们“回箱体”有信息；这次更进一步：**回到 wick 区不够，回到 body 接受区更像真的 failure acceptance。**
- **Fibonacci confirmation / retest_hold**：Fib 位最怕被 wick 噪音污染。若回踩只是扫到 wick 边缘，不该急着说 `retest_hold` 成立；更稳的定义应是：**价格重新回到/站回 parent body zone，再把 hold 质量上调。**
- **EMA / PSAR raw alpha focus**：EMA/PSAR 负责方向与持续性，但“趋势有没有被修复”不能只看一根 wick reclaim。把 **body-zone reclaim** 当 continuation repair gate，比单纯看 fast EMA 触碰更健康。

## 4. 可复刻的最小实验
- **研究假设**：把当前的 `wick inside verdict` 升级成 `body-zone inside verdict` 后，`breakout-short follow-up` 与 `Fib retest_hold` 的假确认率会下降，哪怕 trade count 少一点也值得。
- **公开数据源**：Binance Futures 公共 K 线（`/fapi/v1/klines`），15m；无需付费。
- **最小可计算定义**：
  1. 先定义 parent zone（首轮可直接用 rolling `16` 根 15m，或像 repo 那样用 UTC 首个 `4h` box）；
  2. `wick breakout`：`close > zone_high_wick` 或 `< zone_low_wick`；
  3. `wick verdict`：后续首次 `close` 回到 wick 区；
  4. `body verdict`：后续首次 `close` 回到 `zone_body_high=max(open_box, close_box)` / `zone_body_low=min(open_box, close_box)`；
  5. 可选第三层：只接受 **非 doji** verdict candle（body_pct 超过阈值）。
- **第一轮 bucket**：
  1. `wick_verdict`
  2. `body_verdict`
  3. `body_verdict + non_doji`
- **最先看的 4 个指标**：`4/8 bar post-cost expectancy`、`false-follow ratio`、`trade_count retention`、`entry-to-stop distance inflation`。
- **下一步怎么测**：先别把它当独立策略。直接把它接到三条收口线里最缺的两处：
  1. `V3 breakout-short follow-up`：把原来的 `back-inside-close` 改成 `back-into-body-zone close`；
  2. `Fib retest_hold`：把 `touch/reclaim` 改成 `accepted-body reclaim`；
  然后在 **BTC/ETH/SOL 15m，180d IS + 60d OOS** 上，只问一件事：**它能不能在 10 bps/side 下，把假确认率压低至少 8%，同时保住 50% 以上 trade count。** 能，就升格成 shared verdict spine；不能，就留在 evidence pool。

## 5. 风险与保留意见
- 这还是一个**很新的小仓库**（当前 GitHub 元数据约 `0 star / 0 fork`），我们继承的是规则骨架，不是权威结论。
- `body verdict` 天然会更晚，可能改善胜率却恶化 RR；所以必须同时看 `entry-to-stop` 是否显著变宽。
- 这轮代理快检只用了 **UTC 首 4h box + 固定 4/8 bar horizon**，只是为了测“边界定义是否更诚实”，不是生产级回测。
- ETH 样本里 body 版本没有明显救活表现，说明这条线更可能是**币种/状态相关 gate**，不是通用单点圣杯。
- repo 还提了 `doji` 过滤，但我这轮还没把 `non-doji verdict candle` 纳入正式对照；这正好是下一步最便宜的增量实验。

## 6. 来源
1. **Harro Moen (MoDiggler75). (2026). _crypto-trading-bot_.**
   - Venue / DOI：GitHub / N/A
   - Repo URL: <https://github.com/MoDiggler75/crypto-trading-bot>
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot>
   - Repo API: <https://api.github.com/repos/MoDiggler75/crypto-trading-bot>
   - Repo metadata snapshot：`created_at=2026-01-17`，`pushed_at=2026-02-07`，`0` star，`0` fork。
2. **关键实现：`backtest_4hr_breakout_v2.py`**
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot/blob/master/backtest_4hr_breakout_v2.py>
   - Raw URL: <https://raw.githubusercontent.com/MoDiggler75/crypto-trading-bot/master/backtest_4hr_breakout_v2.py>
3. **对照实现：`backtest_breakout_retest.py`**
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot/blob/master/backtest_breakout_retest.py>
   - Raw URL: <https://raw.githubusercontent.com/MoDiggler75/crypto-trading-bot/master/backtest_breakout_retest.py>
4. **本地代理快检产物**
   - `reports/artifacts/quant_digests/body_zone_reentry_proxy/signals.csv`
   - `reports/artifacts/quant_digests/body_zone_reentry_proxy/summary_all.csv`
   - `reports/artifacts/quant_digests/body_zone_reentry_proxy/summary_by_side.csv`
   - `reports/artifacts/quant_digests/body_zone_reentry_proxy/summary_by_symbol.csv`