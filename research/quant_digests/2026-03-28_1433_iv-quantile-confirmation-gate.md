# 别把 BTC/ETH implied vol 只当慢频解释变量：这篇 2024 IRFA 更该先落地的是「IV quantile confirmation / veto」短周期共享 gate

- 时间：2026-03-28 14:33 UTC
- 类型：filter
- 主题标签：filter/shared-gate/options/implied-volatility/iv-quantile/confirmation/veto/return-volatility-asymmetry/bitcoin/ethereum/deribit/bitvol/ethvol/5m/15m/1m/3m/paper/external-data/cost
- 证据类型：2024 IRFA accepted manuscript 全文（University of Southampton ePrints 可读）+ Crossref 元数据 + Deribit 公共 IV 数据口径

## 0. 四个先答字段

- 主题类型：filter
- 基础 alpha：**它本身不是独立 raw alpha；它服务于两类已有 base alpha：① `5m/15m` breakout / continuation；② `5m/15m` 冲击后 fade / overreaction。核心假设是：价格冲击若得到 implied vol 变化确认，更像真扩散；若处在高 IV 分位却出现“价动、IV 不确认或反向”的组合，更像过冲，应该 veto 或反打。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么

这次主看的是一篇直接研究 **BTC / ETH 高频收益与 implied vol 非对称关系** 的论文：

- **Authors**：Muhammad Mahmudul Karim, Mohamed Eskandar Shah, Abu Hanifa Md. Noman, Larisa Yarovaya
- **Year**：2024
- **Title**：*Exploring Asymmetries in Cryptocurrency Intraday Returns and Implied Volatility: New Evidence for High-Frequency Traders*
- **Venue**：*International Review of Financial Analysis*
- **DOI**：10.1016/j.irfa.2024.103617
- **Readable URL**：https://doi.org/10.1016/j.irfa.2024.103617
- **Accepted manuscript URL**：https://eprints.soton.ac.uk/495838/1/High_frequency_Bitcoin_and_Ethereum_LY_final.docx
- **Repo URL**：未见作者配套 repo

一句话判断：

> **这篇东西的 base alpha 说不清，所以不该硬包装成主 alpha；它更适合被拆成一个 shared gate：用 BTC/ETH 的 IV 分位和 IV 变动，去给已有短周期方向信号做 confirmation / veto。**

这也正好符合当前 desk intake 的灵活规则：如果材料更像 **filter / regime / overlay**，就明确写成 filter，不冒充 headline raw alpha。

## 2. 为什么这轮值得先补这个 gate，而不是再加一个同类 raw alpha

从 `INDEX.md` 看，最近素材池里的 raw alpha 已经堆了不少：

- intraday momentum / continuation
- short-term reversal / lottery fade
- pairs / relative-value / basis / funding
- order-book / options flow / event-driven

**相对更薄的，是一层能跨策略复用的“短周期 admission / veto”组件。**

这篇 paper 的价值正好在这里：

1. **它不是慢频宏观变量**，而是直接跟着 crypto 自身波动状态走；
2. **它天然服务至少两类 alpha**：
   - trend / breakout：看价格扩散有没有得到 IV 确认；
   - mean reversion / shock fade：看高 IV 状态下的单边 bar 是否已经过冲；
3. 它还回答了一个对我们很实用的问题：
   - `1m/3m` 和 `5m/15m` 不该一视同仁；
   - **IV asymmetry 在高频是存在的，但在极高频低分位更弱，在更慢一点的频率和更高分位更强。**

所以这轮不再继续补一个“又一个 breakout alpha”，而是补一个更像 **shared state layer** 的东西，我认为是合理的。

## 3. 论文里最值得拿走的证据

### 3.1 样本不是小打小闹

论文核心样本有几个数很关键：

- **约 650 万条观测**；
- 同时覆盖 **BTC / ETH** 与其 **model-free implied volatility**（BitVol / EthVol）；
- 频率同时看 **`1m / 5m / 10m / 15m / 60m / daily`**；
- IV 数据起点来自指数 inception，文中明确提到 **2020-04-04** 之后的样本期。

这很重要，因为它不是用日频去硬推高频，而是真的把 **高频 return-volatility 关系** 单独拿出来测。

### 3.2 最关键的 headline：高频下，IV 对收益冲击的响应在所有波动分位都显著；日频不是

论文摘要给出的最重要结论其实已经够 desk 化了：

- **daily 频率**下，估计系数只在 **中高波动 regime** 显著；
- **high-frequency 频率**下，估计系数在 **所有波动 regime** 都高度显著。

这对我们意味着什么？

- 别把 implied vol 当成“只对日频有用、对 `5m/15m` 太慢”的变量；
- 真正应该测的是：**短周期价格冲击是否得到 IV 同步确认**。

换句话说，这篇 paper 更像在告诉我们：

> **IV 不是慢解释变量，而是可以进入短周期信号 admission 的状态变量。**

### 3.3 第二个更实用的结论：弱不弱，取决于“频率 × IV 分位”

作者明确写到：

- **低 quantile + 更高频率**：asymmetry 较弱；
- **高 quantile + 更低频率**：asymmetry 较强。

把它翻成人话：

- 在 **`1m/3m`**，尤其当 IV 本来就不高时，拿 IV 做 bar-by-bar 方向确认，容易太噪；
- 到 **`5m/15m`**，尤其当 IV 已经在高分位时，IV 的确认 / 否决信息更有价值。

这正好给了我们一个很自然的实验分工：

- `1m/3m`：更多拿来执行、风控、盘口 veto；
- `5m/15m`：才是 IV confirmation gate 的主战场。

### 3.4 表格层面的两个定性事实也很有用

从文中的 quantile regression 表可以直接读出两件事：

1. **BTC 和 ETH 都一样，不是单币特例**；
2. 在 `1m` 频率下，正负收益项对 IV 变化在多个 quantile 上都非常显著；但到 **daily**，这种显著性明显收缩到更有限的 regime。

这说明两点：

- 这个结构不是“只在 Bitcoin 上成立”的偶然噪音；
- 也不是“只有高频 HFT 才看得见、我们 5m/15m 用不上”的东西——相反，论文就是在提醒你：**越往中速 intraday（尤其高 IV 状态），越值得纳入 gate。**

## 4. desk 化以后，最合理的读法是什么

我不建议把这篇 paper 解读成“用 IV 单独预测涨跌”。那样会把它读歪。

更合适的 desk 版本是下面这两条：

### 4.1 作为 continuation gate

对已有的 breakout / momentum / lead-lag 信号：

- 若价格上冲（或下砸）同时伴随 **IV 上行确认**，说明这更像 **真扩散 / 真风险重估**；
- 若价格动了，但 **IV 没确认甚至反向**，则这次 price move 更像流动性脉冲或短时 squeeze，信号应降权。

### 4.2 作为 fade veto / fade admit layer

对已有的 reversal / shock-fade 信号：

- 若价格单边极端，但 **IV 已处高分位且继续扩张**，别急着反打，先把它当成“趋势扩散尚未结束”；
- 若高 IV 分位下出现 **price extension + IV 不再确认**，才更像 overreaction，可给 fade 更高优先级。

所以它不是主 alpha，而是：

> **一个把“该追”还是“该等”、以及“该反打”还是“先别碰”区分开的共享 gate。**

## 5. 最小可复现实验怎么做

### 5.1 数据源

- **IV / DVOL 侧**：Deribit 公共 volatility index / options implied vol 数据（BTC, ETH）
  - 可先用 Deribit 公共 IV 指数或等价 proxy（BitVol / EthVol / ATM IV）
  - 参考：`https://docs.deribit.com/`
- **执行侧价格**：Binance 或 Deribit perpetual `1m/5m/15m` K 线
- **公开性**：公开可拉
- **更新频率**：分钟级 / 近实时
- **最小实验口径**：先用 `5m` 与 `15m` 聚合，避免把 `1m` 噪音当发现

### 5.2 先别做复杂模型，先做一个最小 gate

先定义：

- `ret_t`：BTC/ETH perp 当前 bar 收益
- `ivchg_t`：同 bar 的 IV 变化（或 log-diff）
- `iv_q_t`：过去 20~40 个 bar 上 IV 所在分位

然后只测一个很朴素的 admission rule：

- **continuation admit**：
  - `|ret_t|` 进入过去 N bar 前 80%~90% 分位；
  - `sign(ivchg_t) == sign(|ret_t| shock 的方向扩散)`，即大方向上有 IV 确认；
  - `iv_q_t >= 0.6` 或 `0.7`
- **fade admit**：
  - `|ret_t|` 很极端；
  - `iv_q_t >= 0.8`；
  - 但 `ivchg_t` 没继续确认，或出现回落

用这条规则分别去包两套 baseline：

1. **baseline A：5m/15m breakout continuation**
2. **baseline B：5m/15m shock fade**

看 gate 是否提高：

- hit rate
- average markout（1/3/6 bars）
- tail loss
- turnover after veto

### 5.3 成本与风控

这类 gate 最大的风险不是“信号方向错”，而是：

- 过度频繁切换 admission 状态；
- 在 `1m` 上被 IV micro-noise 误导；
- 使用非同源市场（Deribit IV vs Binance perp）时出现时钟错位。

所以最小实验务必先加三条约束：

- **只在 `5m/15m` 做主判定**；
- **同方向确认至少持续 2 个采样点**；
- **执行仍走流动性更好的 perp，IV 只做 gate，不直接做 sizing 主驱动。**

## 6. 我认为这篇东西最该留下来的结论

如果只留一句给后续研究池，我会写：

> **短周期里别把 implied vol 只当“解释涨跌的事后指标”；在 BTC/ETH 上，更值得先测的是“IV quantile × IV change”能不能做 continuation / fade 的 admission-veto layer，尤其优先放在 `5m/15m`，而不是噪音更大的 `1m/3m`。**

这轮它不是来补一个新的 headline raw alpha，而是来补一块当前素材池里更缺的 **shared gate**。

## 7. 下一步怎么测

按优先级我建议直接做 3 步：

1. **BTC perp baseline 对照**：
   - 找一条现成 `5m/15m` breakout alpha，加入 `iv_q × ivchg` admission gate；
   - 比较 gate 前后 trade count、胜率、平均 `3-bar` markout。
2. **ETH perp 平行复现**：
   - 同样口径复现 BTC 与 ETH；
   - 看它是 shared gate 还是只在 BTC 上成立。
3. **fade 版本反向验证**：
   - 只挑 `iv_q >= 0.8` 的极端 bar；
   - 比较“IV 继续扩张”和“IV 不再确认”两组后续 1~6 bar 路径差异。

如果这三步里，gate 对 **至少两类 alpha** 都有稳定帮助，它就值得沉淀成一个正式组件：

- `iv_regime_state`
- `iv_confirmation_gate`
- `iv_nonconfirmation_fade_admit`

## 来源链接

- Paper DOI / landing page：https://doi.org/10.1016/j.irfa.2024.103617
- Accepted manuscript：https://eprints.soton.ac.uk/495838/1/High_frequency_Bitcoin_and_Ethereum_LY_final.docx
- Deribit API docs：首页 https://docs.deribit.com/
