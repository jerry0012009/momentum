# 别把 `first major breakout` 只读成“创新高”：对 15m desk，更值得先偷的是 `base-age first break` shared gate
- 时间：2026-03-19 14:19 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/first-major-break/base-age/consolidation-duration/continuation/filter/repo/crypto/15m
- 证据类型：repo 规则启发（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Jermaine Ragsdale (2025) 的 `trading-breakout-scanner`**。我没有照搬它整套“6 条 breakout checklist”，而是只抽其中最适合当前 desk 的旁支：
**`First Major Breakout` 不是在说“只追 6 个月新高”，而是在说：先区分这是不是一段 base 之后的第一次有效逃逸。`**

把它翻成我们 15m 可测语言，就是：
- 先定义 `up/down break event`：收盘上破 / 下破前 `20` 根 Donchian 极值；
- 再算 `base_age`：距离上一次**同方向 break** 已经过了多少根 bar；
- 当前 setup 不是问“有没有破”，而是问：**这次信号，是否站在一个“够久没破过”的 first break 后面。**

这比继续堆一个新指标更值得，因为我们最近已经补了：
- **tightness**（close-range compression）
- **level memory**（same-level consecutive sweep）

还缺的正好是第三个维度：**duration / age**。也就是：这次不是第几次碰线，而是这条线前面到底憋了多久。

## 2. 核心结论
1. **一句话核心结论**：`first major break` 在 15m 上更像 shared admission / size overlay，不像独立 alpha；尤其适合回答 breakout-short follow-up、Fib retest_hold、EMA/PSAR continuation 里最关键的那句：**现在这一下，是“第一次像样逃逸”，还是“已经反复破来破去”的噪音延续？**
2. **一句话证明方式**：我用现有 BTC/ETH/SOL `120d / 15m` 本地 cache，复用当前 desk 三套 archetype（`ema_psar_long` / `fib_retest_long` / `breakout_short`），比较：
   - `baseline`
   - `first_major_break_24 / 36` 严格 gate
   - 更贴 desk 的 `hybrid36`：**long 只有在最近 4 根内出现 `recent_up_break_age >= 36` 才放行；short 若 `recent_down_break_age < 36` 或没有 fresh down-break，只给 `0.5x`。**
3. `hybrid36` 的 shared 代理结果（6bps/side，next-bar open，hold 8 bars）：
   - `baseline mean_total_return`：**-28.85%**
   - `hybrid36 mean_total_return`：**-10.10%**
   - `trade_count_retention`：**74.12%**
   - `mean_position_size`：**0.73x**
4. 分 setup 看更清楚：
   - **EMA/PSAR long**：`-5.26% -> +0.60%`，`positive_asset_ratio 33% -> 67%`，但 retention 只剩 **13.64%**；说明它像“只保留最干净 continuation pocket”的 admission gate。
   - **Fib retest_long**：`-7.60% -> -0.03%`，几乎打平，retention **19.51%**；这更像在告诉我们：Fib 回踩值不值得做，前面那次上破是不是 fresh 很重要。
   - **breakout_short**：`-15.99% -> -10.68%`；并没有翻正，但在**不删事件、主要靠不 fresh 时半仓**的前提下，损失明显收窄。
5. 更诚实的 desk 读法是：
   - **不要把它升成新主策略；**
   - **先把它当 shared `admission + size-down` 层，尤其适合给 breakout-short 与 Fib/EMA continuation 做 final-verdict / follow-up 过滤。**

## 3. 为什么和当前三条收口线直接相关
### 3.1 比继续在旧线里切更值得的原因
如果这轮不做三条收口线以外的题，最合理的理由必须是：它能直接补上三条线当前缺的一块。`base-age first break` 满足这一点。

我们现在已经有：
- “压得够不够紧”（compression）
- “是不是同一水平位反复 sweep”（level-memory）
- “破位后有没有立刻 back-inside / wick rejection / fail-fast”（post-break failure）

但还没有一个简单变量回答：
**这次破位前，到底平静了多久？**

这就是 `base_age` 的价值：它不是又一个新指标，而是把当前几条线缺的“时间维度”补上。

### 3.2 对三条线分别怎么用
- **V3 final-verdict / breakout-short follow-up**：
  下破之后，若最近 down-break 本来就不 fresh，就别把 follow-up 当 continuation 加仓理由；更诚实的是降仓、放慢，甚至只当 fail-to-follow 的观察阶段。
- **Fibonacci confirmation / retest_hold**：
  0.618/0.5 的回踩值不值得信，不只看“回没回到位”，也看回踩之前那次上破是不是 fresh；不是 fresh 的回踩，更像 old level 噪音回抽。
- **EMA / PSAR raw alpha focus**：
  EMA/PSAR 自己负责方向，但最容易死在 choppy continuation。`base_age` 刚好能给它一个简单 admission gate：**只有 fresh first break 后的 continuation 才保留。**

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（本轮快检复用本地缓存）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/literature/tmp_first_major_break_quickcheck_15m_20260319.csv`
  - `reports/artifacts/literature/tmp_first_major_break_quickcheck_setup_15m_20260319.csv`
  - `reports/artifacts/literature/tmp_first_major_break_hybrid_quickcheck_15m_20260319.csv`
  - `reports/artifacts/literature/tmp_first_major_break_hybrid_setup_15m_20260319.csv`

### 4.2 最小可复现实验口径（建议先做这个）
把三条 archetype（`breakout_short / fib_retest_long / ema_psar_long`）统一接一层 `first-break age overlay`：
1. 定义：
   - `up_break_event_t = close_t > rolling_high_20(t-1)`
   - `down_break_event_t = close_t < rolling_low_20(t-1)`
   - `base_age_up_t = bars_since_previous(up_break_event)`
   - `base_age_down_t = bars_since_previous(down_break_event)`
2. 在每个 setup 触发时，读最近 `L=4` 根内是否出现过同方向 `break_event`，以及对应的 `base_age`。
3. 做三臂对照：
   - A：baseline（不加 overlay）
   - B：strict gate（`base_age >= 24/36/48` 才放行）
   - C：desk 版 hybrid（long strict gate；short 在 `base_age` 不 fresh 时半仓而不是直接删单）
4. 固定执行：`next-bar open`、`hold 8 bars`、成本 `6 / 10 / 15 bps per side`、no-overlap。

首轮只看 5 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `positive_asset_ratio`
- `early_fail_4bars`
- `setup-wise contribution`（不要只看 overall，重点盯 breakout_short 是否真被救）

### 4.3 如果要继续往前走，最值得补哪一刀
优先补**二维联动**，不要单独继续炼 `base_age`：
- `base_age × close-range compression`
- `base_age × same-level sweep count`
- `base_age × post-break back-inside / reclaim`

真正值得的不是“更大的 age 阈值”，而是确认：
**长 base + 第一破 + 不立刻 back-inside**，是不是才是我们要的 continuation pocket。

## 5. 风险与保留意见
- 这是 shared setup 代理快检，不是完整策略回测；
- `EMA/PSAR` 的改善目前带有明显样本收缩，不能把少交易直接误读成 alpha；
- `breakout_short` 虽然亏损收窄，但仍未翻正，所以现在更像 `size-down/veto` 证据，不是 short 侧的 final promotion；
- `base_age` 只回答“多久没破过”，不回答“这次破得够不够真”，所以最好和 `compression / reclaim / body-wick / volume` 联动，而不是单独使用。

## 6. 来源
1. **Ragsdale, J. (2025). _trading-breakout-scanner_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/jmragsdale/trading-breakout-scanner>  
   - Repo URL: <https://github.com/jmragsdale/trading-breakout-scanner>
2. **仓库公开描述中的 breakout 筛选骨架**：`Market Leader / First Major Breakout / New 6-Month Highs / Volume Confirmation / Strong Momentum / Trend Confirmation`。  
   - Readable URL: <https://github.com/jmragsdale/trading-breakout-scanner>
3. **公开行情数据源**  
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>