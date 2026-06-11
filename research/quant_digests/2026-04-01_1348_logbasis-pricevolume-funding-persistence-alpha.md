# 别把这篇 2026 永续收益论文 + 新 repo 只读成 funding 套壳：对 short-cycle desk，更该先测的是「log-basis × price-volume admission × funding persistence」这条 perp carry raw alpha

- 时间：2026-04-01 13:48 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-venue/perpetual/log-basis/price-volume/funding-persistence/hedged/market-neutral/binance/bybit/okx/15m/5m/3m/1m/paper/repo/public-data/cost
- 证据类型：2026 SSRN 论文摘要/元数据（Crossref，abstract-only）+ 2026 GitHub repo source audit（`README.md` + `strategies/spot_perp.py` + `config/main.yaml`）+ 2018 SSRN 背景论文元数据

- 主题类型：raw alpha
- 基础 alpha：**当 perp 相对 spot 挂着可收的 carry（正/负 funding + log-basis 提示的持有回报）且该 carry 不是瞬时噪声，而是有持续性时，做 `long cheap leg / short rich leg` 的 delta-neutral 持有，赚 funding + basis 收敛 + 预期总回报；price-volume 只负责 admission / sizing，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
### 一句话核心结论
**这轮最值得 intake 的，不是“funding 大于 0 就去收租”，而是把 `log-basis carry` 当作 alpha 本体，再用 `price-volume` 因子做短周期 admission，最后用 funding persistence + cost hurdle 决定是否真的开仓。**

### 一句话它是怎么证明的
- **论文侧**：2026 新论文先从 perpetual futures 的 cost-of-carry 框架出发，再在 `170` 个候选 predictor 上做截面检验，结果得到 `63` 个显著 total-return 策略，并称一个由 **log-basis + price-volume relevant factor** 构成的两因子模型可以解释这 `63` 条策略。
- **工程侧**：2026 新 repo 直接把 carry 落成可交易规则：只有当 funding 过阈值、同向持续、预计 funding 收益能覆盖 round-trip 费用和 inventory 风险时，才让 spot-perp 对冲仓位进场。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这次 **base alpha 很清楚**，不是 filter 伪装成 alpha。

alpha 本体是：
1. **perp 相对 spot 的 carry / basis 信号**：谁更贵、谁更便宜；
2. **这个 carry 在接下来一段持有期里还能不能继续兑现**：看 funding 是否持续、basis 是否没有夸张到容易先继续恶化；
3. **用对冲结构把大盘方向剥掉**：尽量赚 funding + basis 收敛，而不是赌单边。

所以它属于：
- `raw alpha`
- 更具体地说是：`carry / funding / basis` 家族里的 **完整 spot-perp market-neutral 策略**。

`price-volume` 在这里的角色很重要，但它**默认是 admission / sizing / ranking 增强层**，不是 alpha 本体。

## 3. 为什么这轮值得写，而不是继续堆一个泛 carry 摘要
虽然 desk 最近已经 intake 过几条 funding / basis 线，但这轮仍然值得写，原因是它补的是**一条更完整的“可直接落地策略骨架”**：

1. **论文给了最新学术支撑。**
   不是老生常谈地说“funding 可能有预测力”，而是明确说 perpetual returns 里，**log-basis + price-volume** 是系统性驱动。
2. **repo 给了能直接复现的 entry / exit / sizing / risk / cost 规则。**
   这对当前 desk 比纯理论更有用。
3. **很适合和短周期执行层解耦。**
   carry 本体本来就不该伪装成逐根 1m 主信号；更诚实的做法是：
   - `carry` 负责“值不值得拿”；
   - `15m / 5m` 的 `price-volume` 负责“什么时候拿、拿多大”；
   - `1m / 3m` 负责执行与减冲击。

这比再写一篇“低频数据硬装成 1m alpha”的 digest 更干净。

## 4. 这次看了什么来源
### 4.1 主 supporting paper（最新学术线索）
- **Authors**：Yi Cao, Pengfei Luo, Yuhan Cheng, Yizhe Dong
- **Year**：2026
- **Title**：*Anatomy of Cryptocurrency Perpetual Futures Returns*
- **Venue**：SSRN preprint
- **DOI**：<https://doi.org/10.2139/ssrn.6365329>
- **Readable URL**：<https://www.ssrn.com/abstract=6365329>
- **证据级别说明**：当前可稳定拿到的是 Crossref 元数据与摘要，**属于 abstract-only supporting evidence**，不把它当唯一主证据。

### 4.2 主工程来源（本轮真正可落地的主证据）
- **Author / Repo owner**：gencersarp
- **Year**：2026
- **Title / Repo**：*cryptoarb*
- **Repo URL**：<https://github.com/gencersarp/cryptoarb>
- **Readable URL**：<https://github.com/gencersarp/cryptoarb>
- **关键文件**：
  - `README.md`
  - `strategies/spot_perp.py`
  - `config/main.yaml`

### 4.3 背景地基
- **Authors**：Igor Makarov, Antoinette Schoar
- **Year**：2018（SSRN metadata）
- **Title**：*Trading and Arbitrage in Cryptocurrency Markets*
- **Venue**：SSRN working paper / journal version later exists, but here引用可稳定取到的 SSRN DOI 元数据
- **DOI**：<https://doi.org/10.2139/ssrn.3171204>
- **Readable URL**：<https://doi.org/10.2139/ssrn.3171204>

## 5. 2026 新论文真正给了 desk 什么
### 5.1 不是一句“funding 很重要”，而是把 perpetual returns 写回 cost-of-carry
Crossref 摘要里最重要的不是漂亮术语，而是这句意思：

**持有 perpetual futures 的预期回报，来自当前 log-basis、对未来 spot 的预期误差，以及持有期内 futures-spot spread 的变化。**

翻成人话：
- perp 并不是“永远贴着 spot”自动定价；
- 当前 basis 里本身就含着未来回报信息；
- 你赚不赚钱，不只看下一次 funding，而是看一整个持有窗口的 total return。

这很关键，因为它把 short-cycle desk 常做的东西拆清楚了：
- **alpha 本体**：carry / basis
- **兑现路径**：funding + convergence + total-return drift
- **短周期执行层**：只负责减少拿得太早、太挤、太贵

### 5.2 论文给出的 3 个硬数据点
根据当前可得的 Crossref 摘要：

1. 论文评估了 **170** 个 perpetual return predictors；
2. 其中得到 **63** 条统计显著的 total-return 策略；
3. 一个由 **log-basis + price-volume relevant factor** 构成的两因子模型，声称可以解释这 **63** 条策略。

对 desk 的含义非常直接：
- `log-basis` 值得当成 carry 主轴；
- `price-volume` 不需要神化成另一条独立 alpha，更自然的用法是先做 admission / ranking / sizing；
- 也就是说，**论文更像在告诉我们：perp carry 不该裸奔，而该配一个 flow-sensitive 的增强层。**

### 5.3 但要诚实：论文当前仍是 abstract-only supporting
这轮不能把 paper 讲得太满。

我们**还没拿到稳定可读的全文**，所以以下内容不能假装已经确认：
- paper 里 `price-volume relevant factor` 的精确定义；
- 样本频率、换仓节奏、成本口径；
- 63 条策略的具体分组方法与稳健性表。

所以这轮更合理的做法是：
- 把 paper 当成**高信号学术线索**；
- 真正落地时，先靠 repo 和公开数据做最小实验。

## 6. repo 是怎么把这条 alpha 落成完整策略的
这份 2026 `cryptoarb` repo 在 `strategies/spot_perp.py` 里给出的逻辑，其实非常适合作为 desk 的第一版骨架。

### 6.1 Entry：不是 funding 为正就进
代码核心逻辑：

1. 读取当前 funding rate；
2. 只有当 `abs(funding_rate) >= entry_threshold` 才继续；
3. 再把 funding 近似年化：`fr * 3 * 365`；
4. 只有年化 carry 也过最小门槛，才继续；
5. 再要求 funding 在最近若干 bar **同号持续**；
6. 再看 projected funding edge 是否大于 round-trip fee + slippage + inventory risk。

这比“正 funding 就收租”高明的地方在于：
**它先判断 carry 是否真实、是否持续、是否足够厚，最后才问要不要做。**

### 6.2 Basis filter：basis 不是主信号，但能 veto 极端错误时点
源码里还有一层 `basis z-score` 过滤：
- 如果 basis 已经拉得太极端，就跳过；
- 原因不是否定 carry，而是承认“过度拥挤的 basis 可能先继续扩，再回归”，这会把对冲腿拖进 hidden cost。

这对短周期 desk 非常重要。
因为 carry 交易真正亏钱的常见方式，不是 funding 本身没给钱，而是：
- 你进得太挤；
- 你在 basis 最 stretched 的时点开仓；
- 然后被 leg divergence 和冲击成本先狠狠干一轮。

### 6.3 Exit：先别神化动态优化，简单规则就够
repo 的退出规则其实很朴素：
- 如果 funding 回落到 `exit_threshold` 下方，就平；
- 或者超过 `max_hold_bars` 就平。

这很对。
当前 desk 更需要先回答：
**carry 本体 after-cost 能不能活**，而不是一开始就把出场做成复杂 RL。

### 6.4 repo 给出的几个可直接拿走的配置数字
`config/main.yaml` 里，SpotPerpFunding 当前启用参数包括：

- 交易资产：`BTC, ETH, SOL, AVAX, LINK, DOGE`
- venue：`binance`
- `entry_funding_threshold = 0.0000528762`
- `exit_funding_threshold = 0.0000118355`
- `expected_hold_bars = 13`
- `max_hold_bars = 53`
- `position_size_pct = 0.7178`
- `max_open_positions = 5`
- `min_expected_edge_bps = 0.4247`
- `inventory_risk_bps = 0.6046`

换算一下更直观：
- `entry_funding_threshold` 大约是 **0.53 bps / 8h**；
- `exit_funding_threshold` 大约是 **0.12 bps / 8h**；
- `expected_hold_bars = 13`，对应大约 **104 小时**；
- `max_hold_bars = 53`，对应大约 **17.7 天**。

这再次说明：
**carry 本体不是 1m scalping。**
它天然是一个更慢的 alpha，但完全可以用短周期数据去做 admission、减仓、执行与 veto。

## 7. 对 `1m / 3m / 5m / 15m` 的 desk 化读法
### 7.1 别把低频 carry 硬装成逐根主信号
更诚实的分层应该是：

- **raw alpha 层**：funding + log-basis carry
- **admission / sizing 层**：`15m / 5m` 的 price-volume proxy
- **execution 层**：`1m / 3m` 的微观结构与冲击控制

也就是说：
- 这条线完全服务当前短周期 desk；
- 但服务方式不是“它每根 1m 都给方向”；
- 而是“它决定这笔 delta-neutral carry 值不值得拿，以及拿的时候怎样更像人而不是铁头”。

### 7.2 一个 desk 可执行的 `price-volume` proxy
因为论文全文未得，`price-volume relevant factor` 的精确定义当前还不能硬抄。
所以 first-pass 应该老实用 **proxy**：

- `rv_short = ret_15m × rel_quote_volume_15m`
- `rel_quote_volume_15m = quote_volume / rolling_median(quote_volume, 96)`
- `pv_proxy = zscore(rv_short, 96)`

含义：
- 如果 carry 看起来值得拿，
- 但最近 `15m` 的价格/量能流向完全反着你、而且还在加速，
- 那就别急着进，或者至少降仓。

### 7.3 `15m` first-pass 比 `1m` 更对
建议第一刀这样落：

- carry 信号每 `15m` 重算一次；
- funding / basis 用最新可得 mark、index、spot、next funding 更新；
- 只有当：
  - carry 为正；
  - funding 同号持续；
  - `pv_proxy` 没有强烈反向；
  - 预期收益覆盖费用壳；
  才允许进场。

这样更符合这条 alpha 的真实节奏。

### 7.4 `5m` 可以拿来加快 admission，不建议先上 `1m`
如果 `15m` first verdict 正常，再下钻到：
- `5m` 的 volume / impact proxy；
- `1m / 3m` 的 execution scheduling。

但**不要反过来**。
先卷 `1m` 往往只是让你更早遇到滑点，而不是更早看见 alpha。

## 8. 可以怎样把它落成完整策略
### 8.1 Entry
对每个候选资产 `i`：

1. 计算 `basis_i,t = ln(mark_perp_i,t / spot_i,t)`
2. 读取 `next_funding_i,t` 或最近 funding carry proxy
3. 形成原始 carry 分数，例如：
   - `carry_score_i,t = z(basis_i,t) + z(expected_funding_i,t)`
4. 做 persistence 检查：
   - 最近 `k` 个 funding observation 同号
   - 或最近 `n` 个 `15m` 更新里 carry_score 未跌破 admission threshold
5. 加 `pv_proxy` 作为 admission：
   - 若 `pv_proxy` 明显顺着 carry 有利方向，允许正常仓位
   - 若 `pv_proxy` 中性，允许小仓位
   - 若 `pv_proxy` 强烈逆向，延迟或 veto
6. `next bar` 再执行，避免同 bar 幻觉

### 8.2 Exit
第一轮别复杂化，先测三种：

1. `carry_score < exit_threshold`
2. `next funding` 明显塌掉
3. `max_hold` 到期

如果想加第四种，再加：
4. `pv_proxy` 由支持转为强烈反向时，提前减半或平仓

### 8.3 Sizing
建议先用三层：

1. **signal layer**：按 `carry_score` 分层（小/中/大仓）
2. **portfolio layer**：单资产、单 venue、总 gross 上限
3. **execution layer**：参与率上限，避免 spot/perp 两腿把自己打穿

### 8.4 Risk
必须至少有：
- basis stretch veto
- funding flip veto
- leg divergence stop
- venue exposure cap
- 单币名义价值上限
- 事件日程 veto（上币、下币、重大公告）

### 8.5 Cost
至少做三档：
- maker-ish
- mixed
- taker-heavy

并且把成本拆开看：
- perp 开平手续费
- spot 开平手续费
- slippage / impact
- borrow / inventory risk
- funding 实际兑现偏差

## 9. 最小可复现实验（直接面向当前 desk）
### 实验 A：`15m` same-venue spot-perp carry with price-volume admission
- **标的池**：BTC, ETH, SOL, LINK, AVAX, DOGE
- **venue**：先 Binance，再扩 Bybit / OKX
- **bar**：`15m`
- **base signal**：`z(log_basis) + z(next_funding)`
- **persistence**：最近 `2~3` 次 funding observation 同号，或最近 `8~16` 个 `15m` carry_score 未翻负
- **admission**：`pv_proxy` 不得强烈逆向
- **执行**：spot-perp 对冲同步开仓
- **持有**：到下一次 / 两次 funding，或 `carry_score` 跌破 exit
- **回答问题**：`price-volume` admission 能不能让同一条 carry 在 after-cost 下更稳，而不是只减少交易次数？

### 实验 B：ablation ladder
在相同 universe、相同执行与相同成本口径下，只比较：

1. **funding only**
2. **funding + log-basis**
3. **funding + log-basis + price-volume proxy**
4. **funding + log-basis + price-volume proxy + persistence gate**

这是这条线最值得先跑的实验，因为它直接回答：
**真正给你增量的，到底是 carry 本体，还是 admission 壳。**

### 实验 C：`5m` admission / `1m` execution transfer
- carry 本体仍按慢频更新
- 用 `5m` 重新算 `pv_proxy`
- 用 `1m` 做 TWAP / participation scheduling

目的不是把 alpha 变成 `1m alpha`，而是测试：
**更细执行，能否降低冲击而不稀释 carry。**

## 10. 下一步怎么测
建议顺序别花：

1. **先做实验 B**：先确认增量来自哪里
2. 如果 `funding + log-basis` 本体就不行，先停，不要继续给 admission 壳贴金
3. 如果 `funding + log-basis` 可活，再看 `price-volume proxy` 是否提高：
   - after-cost Sharpe
   - MDD
   - positive trade ratio
   - average leg divergence
4. 如果 `15m` 可活，再把 admission 压到 `5m`
5. 最后才讨论 `1m / 3m` 执行层

最重要的一句：
**先验证 carry 本体，再优化 admission；先验证 admission，再优化 execution。**

## 11. 这条线最容易错在哪
### 11.1 把 funding 当成唯一收益来源
很多时候你实际赚/亏的，更多来自：
- basis 变化
- 进出场冲击
- 两腿不同时成交造成的 divergence

所以评价一定要看 **total return**，不是只看 funding 到账。

### 11.2 把 `price-volume` 说成新 alpha
这轮不该这么写。
更诚实的说法是：
- alpha 本体是 carry / basis
- `price-volume` 是 admission / sizing / veto 增强层

### 11.3 直接把 repo 的 8h 参数抄到 15m
源码里的 `13`、`53`、`0.53 bps/8h` 都有参考价值，
但应该拿去当**量级感**，不是直接按数字照搬。

### 11.4 只在理想 maker 成本下成立
如果一条 carry 策略只有在完美 maker 成本下才活，
那它不是 ready，只能算候选。

## 12. 对当前 `momentum` 项目的直接意义
这条线和现有 backlog 的关系很清楚：

- 它**不是**继续围绕 breakout / pullback 内循环；
- 它补的是一条 **carry / funding / basis raw alpha**；
- 同时给了一个很好的模块化拆法：
  - raw alpha：carry
  - filter / admission：price-volume
  - risk：basis stretch / funding flip / leg divergence
  - execution：`1m / 3m` scheduling

对当前 desk，这条线最有价值的地方就是：
**可以很快做 first verdict，而且 verdict 非常干净。**

## 13. Sources
1. Cao, Y., Luo, P., Cheng, Y., & Dong, Y. (2026). *Anatomy of Cryptocurrency Perpetual Futures Returns*. SSRN. DOI: <https://doi.org/10.2139/ssrn.6365329>. Readable URL: <https://www.ssrn.com/abstract=6365329>
2. gencersarp. (2026). *cryptoarb* [GitHub repository]. <https://github.com/gencersarp/cryptoarb>
3. Key repo files used in this digest:
   - <https://raw.githubusercontent.com/gencersarp/cryptoarb/main/README.md>
   - <https://raw.githubusercontent.com/gencersarp/cryptoarb/main/strategies/spot_perp.py>
   - <https://raw.githubusercontent.com/gencersarp/cryptoarb/main/config/main.yaml>
4. Makarov, I., & Schoar, A. (2018). *Trading and Arbitrage in Cryptocurrency Markets*. SSRN. DOI: <https://doi.org/10.2139/ssrn.3171204>
