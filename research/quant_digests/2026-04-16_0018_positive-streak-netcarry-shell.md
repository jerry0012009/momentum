# 别把这份 2026 funding-arb bot 只读成 Telegram 执行器：对 short-cycle desk，更该先测的是「positive-net-APR streak admission × negative-hours stop」这条完整 raw alpha 壳

- 主题类型：raw alpha
- 基础 alpha：**同一标的在不同 perpetual venue 上存在可交易的 net carry differential；做 `short 高 funding leg + long 低 funding leg` 的 delta-neutral 对冲配对，赚 funding spread，而不是赌方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/cross-venue/perp-perp/relative-value/stat-arb/delta-neutral/net-carry/positive-streak-admission/negative-hours-stop/liquidation-distance-auto-close/telegram-bot/backpack/lighter/hyperliquid/grvt/aster/1m/3m/5m/15m/repo/cost/risk

## 1. 这次看的是什么

这次主看的是 **`kohtabeloff/funding-arb-bot`（2026）**。表面上它像个 Telegram 交易机器人：连 5 家交易所、给你发信号、还能手动点按钮开平仓。

但如果只把它读成“执行面板”，就会错过它真正对我们 desk 更有价值的部分：**它把一条早就知道存在的 cross-venue funding carry，往“什么样的 spread 值得上、上了以后什么时候该滚、什么时候该硬关”推进了一步。**

它最值得 intake 的，不是“跨所 funding 有差异”这个老结论，而是 repo 给了一套**更像能直接上线的 admission + protection 壳**：

1. **只报 `MIN_PAIR_APR >= 50%` 的 pair；**
2. **不是只看当前一刻 net APR，而是显示这对 pair 已经持续正 net APR 多久（`pair_streak`）；**
3. **短暂掉到负 carry 不立刻砍，给 `4h` 宽限；**
4. **若 net APR 直接恶化到 `-50%`，或者任一腿离强平太近，就自动平仓；**
5. **信号、仓位、历史、设置都写进 SQLite，说明它不是纯概念图，而是完整的策略壳。**

翻成人话：
**这份 repo 真正可带走的，不是“哪里 funding 高”这种排行榜，而是“同一条 cross-venue carry alpha，怎样用持续性准入 + 负 carry 宽限退出，把它从扫描器推进到更像 production 的完整壳”。**

---

## 2. 一句话结论

> **这份 repo 最值钱的，不是又证明了一次 same-underlier cross-venue net carry 能做，而是把它写成了更像 production 的版本：`50%+ net APR 准入`、`positive streak`、`4h negative-hours stop`、`15% liquidation-distance auto-close`。对 short-cycle desk，下一步最值得先测的不是“每次 funding diff 为正就开”，而是“只做持续为正且没明显恶化的 pair”。**

---

## 3. 为什么它能算 raw alpha，而不是纯风控/工具

先把话说死：

- **alpha 本体**不是 Telegram，也不是 SQLite，也不是 liquidation warning；
- **alpha 本体**就是 **same-underlier、cross-venue 的 net carry differential**。

repo 里的关键函数 `find_pair_opportunities(...)` 已经把这个写得很直白：

- 同一 symbol；
- 不同 venue；
- 若两边 funding/APR 异号，`net_apr = |apr_a| + |apr_b|`；
- 若同号，`net_apr = ||apr_a| - |apr_b||`；
- 自动决定哪边 `LONG`、哪边 `SHORT`；
- 只保留超过门槛的 pair。

所以它不是“风控先于 alpha”的材料，恰恰相反：
**它先承认 base alpha 就是 cross-venue carry，然后再在 admission / hold / forced-exit 层补全。**

这对我们 desk 是对的，因为当前更缺的不是“funding differential 存不存在”，而是：

- 哪些 spread 值得做；
- 哪些只是瞬时噪声；
- 进场后负 carry 多久该忍、多久不该忍；
- 什么时候该把“看起来中性”的 pair 当成会炸的坏仓位处理掉。

---

## 4. 这份 repo 新增的、真正值得 intake 的点

### 4.1 `positive net APR streak`：不是只看当前数值，而是看它活了多久

repo 在 `main.py` 里专门维护了一个 `_funding_streak` 状态表：

- `_update_pair_net_streaks(...)`
- `get_pair_streak_hours(...)`
- `FUNDING_DIP_TOLERANCE_HOURS = 4.0`

逻辑非常直接：

- 对所有 **当前 net APR > 0** 的 pair，记录它从什么时候开始持续为正；
- 如果中间掉下去，但掉下去时间 **不超过 4 小时**，**不重置 streak**；
- 掉下去太久，才重新计时；
- 最终每个信号会显示 `pair_streak`，例如 `Net APR ~38.5% ⏱ 47h`。

这件事的重要性在于：

**它把“当前很肥”与“已经持续存在”分开了。**

很多 funding spread 看起来大，只是某个时点临时抽风；但 desk 真正想拿的是：

- 已经持续存在一段时间；
- 不是刚跳出来 5 分钟；
- 没有被最近几小时的负 carry 反复击穿；
- 更像结构性资金错配，而不是瞬时噪声。

所以这轮最值得复现的不是 plain `net_apr` 排名，而是：

> **`positive-streak gated net carry`**：只做 `net_apr` 为正且持续时间够长、并允许短暂 dip 的 pair。

这比“只要当前 diff 为正就开”更接近真实可活的 short-cycle carry pocket。

### 4.2 `negative-hours stop`：不要一负就砍，也不要无限死扛

repo 的保护阈值写得很死：

- `NEG_APR_HARD_CLOSE = -50.0`
- `NEG_APR_WAIT_HOURS = 4.0`

README 也明确写了自动平仓条件：

- Net APR 掉到 **`-50%` 以下**：立即关；
- Net APR 变负且在设定时长内不恢复：关；
- 参数可在 bot 设置里修改。

这其实是在回答一个很实战的问题：

**carry pair 的恶化，并不一定要等到价格层面完全炸开才处理。**

更诚实的持仓管理是：

- 如果只是短暂 funding wobble，可以忍；
- 如果已经进入“继续持有只是在付 carry”的状态，而且持续太久，就该退出；
- 如果直接变成明显反向 carry，就别再讲故事，先砍。

这比很多 funding 策略里常见的“开了以后只等 settlement / 只看手动关”更完整。

### 4.3 `liquidation-distance auto-close`：把“市场中性”当成有杠杆风险的仓位来管

repo 还明确做了强平距离保护：

- `LIQ_WARN_PCT = 20.0`
- `LIQ_AUTO_CLOSE_PCT = 15.0`
- `PRICE_WARN_PCT = 10.0`
- `PRICE_AUTO_CLOSE_PCT = 15.0`

即：

- 任一腿离强平小于 `20%` 先报警；
- 小于 `15%` 自动平；
- 如果某交易所拿不到强平价，就退化为看入场后价格偏离百分比。

这很重要，因为 cross-venue carry 最容易自欺的一点就是：

> “反正我两边对冲了，所以方向风险很小。”

实际上并不是。

不同 venue 的：

- 保证金规则
- 标记价格
- 强平逻辑
- 盘口深度
- 资金费率更新节奏

都不一样。**pair 在组合层面接近中性，不等于任一单腿不会先被炸掉。**

repo 至少诚实地把这件事写进了自动化规则里，而不是假设“对冲 = 安全”。

### 4.4 它真的不是空壳：有 DB、持仓、历史、可扩仓

repo 不是只有扫描器。`db/database.py` 里有：

- `positions` / `funding_history` / `settings` 表；
- 原子保存双腿；
- 开仓、加仓、关仓；
- 已平 pair 历史；
- funding 统计查询。

README 里还明确暴露了：

- 默认每腿 `POSITION_SIZE_USD = 100`
- 可在 Telegram 里手动 `Add` 加仓；
- 设置持久化到 DB；
- 启动资金最低测试建议 `10~15 USD / leg`。

这意味着它不是“讲一个 carry 故事”的 repo，而是已经把 **entry / monitoring / scaling / exit / logging** 串起来了。

对我们来说，这正是“可直接落地完整策略”的标准之一。

---

## 5. 它和之前几篇 funding digest 的关系：哪里重复，哪里不重复

要老实讲：
**base alpha 本身并不新。**

此前 digest 已经覆盖过：

- `2026-03-30_1919_perp-perp-funding-diff-nethurdle-alpha.md`
- `2026-04-02_1734_feecoverage-gated-crossvenue-funding-carry-alpha.md`
- `2026-04-12_0830_crossvenue-netcarry-ranking-alpha.md`
- `2026-04-13_0435_cexdex-fundingarb-shell.md`
- `2026-04-15_2326_cexdex-fundingspread-shockreversion-alpha.md`

所以这次**不能**再把主题写成泛泛的“跨所 funding differential 又能套利”。那样就是重复。

这次真正新增的 intake 点是：

1. **`positive-streak admission`**：不是只看当前 spread，而是看它持续了多久；
2. **`negative-hours stop`**：不是刚翻负就砍，也不是一直扛；
3. **`liq-distance auto-close`**：把组合中性的幻想，拆回单腿真实风险；
4. **执行闭环更完整**：信号 → 开仓 → DB → 监控 → 手动/自动平仓。

所以这篇更准确的定位不是“又一个 funding differential 研究”，而是：

> **同一条 raw alpha，在 repo 层终于出现了一个更像 production 的 admission + hold + forced-exit 壳。**

这就足够构成一次新的 intake。

---

## 6. 代码/配置里最该记住的数字

从 repo 直接可见的默认参数：

- `MIN_PAIR_APR = 50`：只报 net APR 至少 `50%` 的 pair
- `SCAN_INTERVAL_SECONDS = 60`
- `POSITION_SIZE_USD = 100`：默认每腿 `100 USD`
- `SIGNAL_COOLDOWN_HOURS = 4`
- `APR_GROWTH_THRESHOLD = 0.5`：若 APR 较上次增长 `50%+` 可再次报信号
- `FUNDING_DIP_TOLERANCE_HOURS = 4.0`
- `NEG_APR_HARD_CLOSE = -50.0`
- `NEG_APR_WAIT_HOURS = 4.0`
- `LIQ_WARN_PCT = 20.0`
- `LIQ_AUTO_CLOSE_PCT = 15.0`
- `PRICE_WARN_PCT = 10.0`
- `PRICE_AUTO_CLOSE_PCT = 15.0`

支持的 venue：

- Backpack
- Lighter
- Hyperliquid
- GRVT
- Aster

README 还写明：**任意交易所都可以两两配对，bot 自动找最优组合。**

---

## 7. 对 1m / 3m / 5m / 15m desk 的真正启发

这条策略虽然收益结算事件还是 funding clock，但它对我们短周期 desk 依然有直接意义，因为它回答的不是“8 小时后收多少钱”这么单一的问题，而是：

### 7.1 `1m / 3m / 5m` 可以做 admission / monitoring 层

短周期分辨率主要用来监控：

- pair 的 net carry 是否还在；
- basis 是否突然炸开；
- 单腿离强平/大滑点是否越来越近；
- 刚刚变负的 carry 是瞬时抖动还是持续恶化。

也就是：

- **1m/3m**：更适合 `monitor / protection / recheck`
- **5m/15m**：更适合 `admission / hold-or-close verdict`

### 7.2 最小实验不该先问“年化多高”，而该先问“streak 有用吗”

当前最值得先验证的不是 long-run APR，而是：

1. **只按当前 `net_apr` 排名开仓**；
2. **按 `net_apr + pair_streak` 联合准入开仓**；
3. **再加 `negative-hours stop`**；
4. **最后才加 liquidation-distance veto / auto-close。**

也就是说，要把这份 repo 的新增价值拆开测，而不是一股脑打包。

---

## 8. 最小可复现实验怎么做

### 8.1 数据源

这条策略的数据需求分两层：

**层 A：最小公开复现实验**
- 同一标的在两到三家公开可抓 funding / mark price / index price 的 perpetual venue；
- funding 更新频率：按各 venue 公布节奏（常见为 `1h` 或 `8h`）；
- 价格监控：`1m` 或更快；
- 公开性：可先用公开 REST/WebSocket funding + mark/index 接口做 proxy。

**层 B：更贴 repo 的实盘化实验**
- 需要真实交易所账户/API；
- 需要拿到持仓、下单、强平价或近似风险指标；
- 才能完整复现 repo 的执行/风控闭环。

### 8.2 最小实验口径

先不要追求 5 家 venue 全上。第一轮建议：

- 标的：`BTC`, `ETH` 先做
- venue：任选 `2~3` 家 funding public path 比较顺的 venue 做 proxy
- 监控频率：`1m`
- 决策频率：`5m`
- 样本期：最近 `30~60d`

### 8.3 A/B 测试设计

#### A. baseline：plain net carry
- 每个决策时点，找 `net_apr` 最高的 same-underlier pair；
- 若 `net_apr >= threshold` 则开；
- 持有到下一次 funding / 固定 `H` 小时 / 或简单 net carry 翻负退出。

#### B. streak admission
- 在 A 的基础上，加：`pair_streak >= {2h, 4h, 8h, 12h}`；
- dip tolerance 先测 `{0h, 2h, 4h}`。

#### C. streak + negative-hours stop
- 若 net carry 翻负但未超过 `grace_hours`，继续持有；
- 超过 `grace_hours` 才退出；
- 同时测 `hard_close = {-25%, -50%, -75%}`。

#### D. streak + negative-hours + risk veto
- 加上单腿爆仓距离/价差爆裂 veto；
- 如果没有真实强平价，就用 `entry-price adverse move` proxy 近似。

### 8.4 最该先看的指标

不要先盯年化收益，第一轮更该看：

- `post-cost pnl / pair`
- `avg holding time`
- `fraction of pairs surviving to next funding event`
- `false-positive rate of fresh spreads`（刚出现就消失的 pair 占比）
- `streak bucket -> realized outcome`
- `orphan risk / one-leg forced close incidents`

---

## 9. 当前 first verdict

**first verdict：值得 intake，而且更像“实盘组件拆解”意义上的强候选。**

但要把话讲清：

- **它不是新 alpha 发明；**
- **它是老 alpha 的更可执行版本；**
- 真正新增价值在于：
  - `streak admission`
  - `negative-hours stop`
  - `single-leg risk honesty`
  - `DB-backed execution loop`

如果你现在让我只从这份 repo 拿走一句最有用的话，那就是：

> **别再把 cross-venue funding carry 写成“谁 net APR 高就做谁”；先测“持续为正多久”再决定要不要上。**

---

## 10. 下一步怎么测

### 10.1 第一优先：做 `streak admission` 的最小回放

先做最小版，不碰真实下单：

1. 每 `1m` 抓 funding / mark；
2. 每 `5m` 计算 all-pair `net_apr`；
3. 维护 `positive_since / dip_since`；
4. 比较：
   - `plain net_apr threshold`
   - `net_apr + streak >= X`
5. 看 post-cost outcome 是否更稳。

### 10.2 第二优先：拆 `negative-hours stop` 是否有边际价值

对同一批 admission 过的 pair，比较：

- `flip-negative immediately exit`
- `wait 1h`
- `wait 2h`
- `wait 4h`
- `hard_close only`

核心问题是：

**短暂负 carry 是可忍噪声，还是恶化前兆？**

### 10.3 第三优先：把风控诚实化

若 public path 拿不到强平价，就先做替代版：

- 单腿 adverse move `> x%` veto；
- venue price divergence `> y bps` veto；
- one-leg liquidity shortfall / quote gap veto。

不要因为没有真实 liquidation price，就假装这部分风险不存在。

---

## 11. 来源

1. **kohtabeloff. (2026). *funding-arb-bot*. GitHub.**  
   - Venue: GitHub repository  
   - Repo URL: <https://github.com/kohtabeloff/funding-arb-bot>  
   - Readable URL: <https://github.com/kohtabeloff/funding-arb-bot>  
   - Raw README: <https://raw.githubusercontent.com/kohtabeloff/funding-arb-bot/main/README.md>

2. **关键源码审计文件**  
   - `config.py`  
   - `main.py`  
   - `core/analyzer.py`  
   - `core/executor.py`  
   - `db/database.py`  
   - `.env.example`

3. **GitHub metadata（API）**  
   - repo: `kohtabeloff/funding-arb-bot`  
   - created: `2026-03-30`  
   - updated: `2026-04-14`  
   - description: `Telegram bot for delta-neutral funding rate arbitrage on crypto perpetual exchanges`

---

## 12. 给自己的落地备注

如果后面真要进复现队列，最值得先写成独立模块的不是 Telegram，不是 DB，而是这 3 个函数层：

1. `calc_net_apr(pair)`
2. `update_positive_streak(pair)`
3. `exit_if_negative_too_long / exit_if_leg_risk_too_high`

也就是说，真正该拿进我们自己代码库的，应该是：

- **raw alpha 层**：cross-venue net carry differential
- **admission 层**：positive streak + dip tolerance
- **risk 层**：negative-hours stop + leg-risk veto

这才是这篇 intake 的核心。