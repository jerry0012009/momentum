# 别把 TSMOM 继续写成固定 lookback：这篇 2021 NAJEF 更该先测的是「turning-point formation → continuation」完整 raw alpha，但 5m 只在低成本口袋才值得活
- 时间：2026-03-27 12:44 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：single-asset time-series momentum（先出现一段已确认的同向 formation，再顺着后续 momentum cycles 做 continuation）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/time-series/single-asset/turning-point/dynamic-formation/momentum-cycle/parameter-light/intraday/1m/3m/5m/15m/paper/cost
- 证据类型：开放获取全文 PDF + ScienceDirect 摘要页 + 本地表格抽取（medium evidence）

## 1. 这次看了什么
这次主线看的是 **Oliver Borgards (2021), _Dynamic time series momentum of cryptocurrencies_**, 发表于 **North American Journal of Economics and Finance**。

这篇对我们现在的价值，不是再讲一遍“涨了还会涨”的老话，而是把 **TSMOM 从固定 `N` 根收益排序**，改写成一个更接近交易员直觉的结构：**先确认 formation period，再跟随后续 momentum period，直到 turning-point 结构失效。**

一句话先说：**base alpha 很清楚，就是 own-past continuation；这篇不是 filter，也不是解释型综述，而是一套可以直接拆成 `entry / exit / cost boundary` 的完整 raw alpha 骨架。**

## 2. 核心结论
- **一句话核心结论**：这篇 2021 NAJEF 最值得 desk intake 的，不是“crypto 有 momentum”这个大而化之的 headline，而是 **“用 turning-point 串起来的动态 formation→continuation 规则，可以把单资产 trend alpha 写成不依赖固定 formation/holding 窗口的完整策略。”**
- **一句话它是怎么证明的**：作者对 **20 个加密货币**、`1D / 1h / 5m` 三个频率建模，把 time-series momentum 定义成连续的 momentum cycles；第一段 cycle 是 formation，后续 cycle 组成 momentum period，再直接拿同一规则做交易测试并和 buy-and-hold 对比。

论文里对 desk 最关键的数字，不在“有没有显著性”，而在 **可交易性边界**：
- **1h long momentum**：平均 **gross profit/trade = `0.996%`**，扣掉作者假设的 **`0.2%` 每次交易费**后，仍有 **`0.596%` net profit/trade**；
- **1h short momentum**：平均 **gross profit/trade = `1.002%`**，扣费后仍有 **`0.602%` net profit/trade**；
- **5m long momentum**：平均 **gross profit/trade = `0.093%`**，在论文的高费率下变成 **`-0.307%` net**；
- **5m short momentum**：平均 **gross profit/trade = `0.066%`**，扣费后变成 **`-0.334%` net**；
- 对应地，**5m 的 paper-level breakeven round-trip cost** 大约只有：
  - long 侧 **`9.3 bps`**；
  - short 侧 **`6.6 bps`**。

这几个数非常重要，因为它把这篇东西直接翻译成了 desk 语言：
1. **alpha 本体存在**；
2. **1h 级别 gross 足够厚**；
3. **5m 不是“没有 edge”，而是 edge 太薄，必须过 fee cliff 才有资格进池。**

## 3. 为什么和当前项目有关
这篇和当前 `momentum` 项目直接相关，原因有三层：

- 第一，它补的是我们当前更缺的那一块：**single-asset / own-past / trend continuation raw alpha**。最近 intake 里 `pairs / stat-arb / cross-sectional / carry / basis` 已经很多，但单资产趋势线里，真正写得足够“可交易”的新材料没那么多。
- 第二，它和 backlog 里已经 `REVIEWED + KEEP` 的 `multi_tf_momentum` 不冲突，反而能形成互补：
  - 旧 baseline 更像 **固定窗打分**；
  - 这篇更像 **结构化 event state machine**。
- 第三，它天然适合我们关心的 `1m / 3m / 5m / 15m` 映射：
  - 不是非得照搬论文的 `1D / 1h / 5m`；
  - 更关键的是把 **formation 被确认后才入场**、**continuation 失效就离场** 这套动态骨架搬下来。

所以它不是“再补一篇 trend 论文”，而是在 raw alpha 素材池里补了一个更诚实的命题：
**趋势不一定要靠固定 lookback 和固定 hold 去赌；也可以靠 turning-point 结构，做成一个动态持有、动态出场的 continuation alpha。**

## 3.5 策略拆解（必填）
- 方向属性：`raw alpha`
- 基础 alpha：`single-asset time-series momentum / continuation`
- 是否完整策略：**是**
- 它服务的不是别的主 alpha；它自己就是主 alpha。

### 论文主口径怎么定义
作者把 time-series momentum 拆成两个层级：
1. **formation period**：第一段满足条件的 momentum cycle；
2. **momentum period**：formation 之后，连续仍然满足条件的 cycles。

文中给的直觉很清楚：
- 若 turning points `T1~T4` 已经形成一段正向 momentum cycle；
- 那么在 `T4` 被确认后开多；
- 之后只要后续 cycles 继续满足同方向结构，就继续持有；
- 一旦结构失效，就退出。

也就是说，这不是“过去 32 根涨了就买、再拿 8 根”的静态策略，而是：
- **entry**：formation 被确认；
- **hold**：只在 continuation 结构仍然成立时持有；
- **exit**：turning-point 结构破坏。

### 对 desk 的翻译
把论文语言翻成我们能马上测的实现，大致就是：
- **signal**：最近一段价格 swing 已经从随机波动，演化成可辨认的同向结构；
- **entry**：新 formation 完成后的第一根可交易 bar；
- **exit**：最近一次确认 swing 被跌破 / 突破失败 / 新 turning-point 序列不再同向；
- **sizing**：先从固定 notional 或 ATR-normalized notional 起步；
- **risk**：单笔最大不利 excursion、连续失败次数、日内总止损；
- **cost**：必须单独测 `3 / 5 / 8 / 10 bps` 这条 fee ladder。

## 4. 可复刻的最小实验
### 4.1 论文给我们的最小可复现框架
即使不逐行复刻原文平滑算法，最小实验已经足够明确：
1. 对单资产价格序列做 turning-point / swing 提取；
2. 识别第一段有效同向 cycle，记为 formation；
3. formation 完成后顺势开仓；
4. 只要后续 swing 继续抬高高点低点（多头）/ 压低高点低点（空头），就继续持有；
5. 一旦 swing 结构不再延续，就退出；
6. 分别比较 `1m / 3m / 5m / 15m` 下的 gross、cost 后 net、MDD、trade duration、turnover。

### 4.2 先别误读成“完全无参数”
author 文中会把它描述成 **parameter-less / dynamic momentum strategy**，但对 desk 更诚实的说法是：
- **它不需要预先固定 formation 窗口和 holding 窗口**；
- **但 turning-point 提取本身仍有平滑灵敏度参数**。

文中示例明确用了 **sensitivity parameter `κ = 5`**。所以这篇不是“完全无参数”，而是：
**比固定 lookback/hold 更少依赖硬编码时窗，但仍有 swing 抽取灵敏度需要校准。**

### 4.3 对 `1m / 3m / 5m / 15m` 的最小实验口径
对我们当前 desk，我建议先别上太复杂的滤波器，直接做一个 **paper spirit、desk implementation**：
- **资产**：`BTC`, `ETH`, `SOL` 三个 liquid perp 先跑；
- **bar**：`1m / 3m / 5m / 15m`；
- **turning point 提取**：
  - 版本 A：rolling zigzag / pivot-high-low；
  - 版本 B：ATR-normalized swing filter；
  - 版本 C：论文式 smoothing filter 的近似实现；
- **多头 formation 定义**：最近四个确认 turning points 满足 higher-high + higher-low；
- **空头 formation 定义**：最近四个确认 turning points 满足 lower-high + lower-low；
- **入场**：formation 刚确认后的下一根；
- **离场**：结构失效、或时间止损、或 ATR trailing stop 三者取先；
- **成本口径**：round-trip `3 / 5 / 8 / 10 bps`；
- **输出**：`gross edge / net edge / hit-rate / avg win / avg loss / avg hold bars / turnover / MDD`。

这能最快回答一个最关键的问题：
**dynamic continuation 在我们常用频率里，究竟是“可活的趋势 alpha”，还是“又一个被换手吃掉的好故事”。**

## 5. 可以怎么直接落成完整策略 / 规则
如果要把它写进策略池，我会先用下面这版，而不是死磕论文原版所有细节：

1. **结构识别层**
   - 用 `pivot-confirmed swings` 识别高低点；
   - 至少要求最近两组 highs/lows 同向抬升/下降；
   - 再要求 formation 的绝对幅度超过最小噪声门槛（例如 `x * ATR`）。

2. **入场层**
   - formation 被确认后，下一根 bar 开仓；
   - 不做 anticipatory entry，避免 look-ahead。

3. **持仓层**
   - 只要新确认 swing 仍符合 continuation 结构，就保留仓位；
   - 若出现“高点创新高但低点不抬升”之类的结构劣化，缩半仓而不是硬扛。

4. **离场层**
   - 结构破坏立刻离；
   - 同时配一个最大持有 bars 上限，防止变成慢漂移死拿；
   - 再加 ATR trailing 做灾难保护。

5. **仓位层**
   - 第一版先等权或固定风险；
   - 第二版再试 `ATR target risk`；
   - 暂时不要先叠太多 fancy sizing，先证明 raw alpha 本身是正的。

6. **交易成本层**
   - 这是核心，不是附录。
   - 因为 paper 已经告诉我们：**5m gross edge 本来就薄**，如果 round-trip 成本高于个位数 bps，alpha 很可能直接没了。

## 6. 风险与边界
- **样本边界**：论文样本是 `2014-01-01 ~ 2019-12-31`，这意味着它证明的是早期到中期 crypto 市场的动态 TSMOM，不保证 2026 还原样成立。
- **成本边界非常关键**：论文假设 **每次交易 `0.2%`**，也就是对 5m 这类高频结构非常苛刻；这恰好说明 **5m 是否可活，本质是 fee cliff 问题**。
- **方法不是完全无参数**：虽然 formation/holding 不预设固定长度，但 turning-point 提取仍受 `κ` 或平滑方法影响。
- **单资产 continuation 容易被 regime 影响**：在高噪声、低趋势、资金面来回翻转的阶段，formation 很容易被假突破污染。
- **不要把它误装成 shared gate**：这篇最有价值的是独立 raw alpha，不是给别的 alpha 做过滤层。

## 7. 下一步怎么测
1. **先做最小版 swing continuation，而不是追求论文 full fidelity**
   - 先在 `BTC/ETH/SOL × 5m/15m` 跑一个 pivot-based 近似版；
   - 只回答一个问题：`gross > 0` 吗？`cost 后还有吗？`

2. **专门做 fee cliff 曲线**
   - paper 的关键信息已经非常明确：5m gross 只有 `6.6~9.3 bps/trade` 量级；
   - 所以必须画 `0~12 bps` 的 net decay 曲线，别只报一个固定费率。

3. **把 static lookback TSMOM 和 dynamic swing TSMOM 并排跑**
   - 同一资产、同一频率、同一成本；
   - 比较 `固定 N 根收益排序` vs `formation→continuation`。
   - 如果 dynamic 版只是在换一种方式提高换手，那就不值得继续。

4. **看 15m 是否比 5m 更像 sweet spot**
   - 论文 `1h` 很厚、`5m` 很薄；
   - 对 desk 而言，`15m` 很可能是最该先测的 transfer 点：
     - 比 `5m` 成本压力小；
     - 比 `1h` 反应更快。

5. **只在趋势 pocket 里启用，不要默认 always-on**
   - 先叠最轻的一层 regime：例如 `ADX/ATR expansion` 或 `market-wide trend breadth`；
   - 目标不是把它改造成 filter，而是避免在最噪的 chop 里白白交手续费。

## 8. 来源
- Borgards, Oliver (2021). *Dynamic time series momentum of cryptocurrencies*. **North American Journal of Economics and Finance**, 57, 101428.
- DOI: `10.1016/j.najef.2021.101428`
- DOI URL: https://doi.org/10.1016/j.najef.2021.101428
- Readable URL: https://www.sciencedirect.com/science/article/abs/pii/S1062940821000590
- Elsevier LinkingHub: https://linkinghub.elsevier.com/retrieve/pii/S1062940821000590
- Repo URL：未见官方 repo
- 方法前序：Borgards, O.; Czudaj, R. (2020). *The prevalence of price overreactions in the cryptocurrency market*.

## 9. 本地产物
- 研究笔记：`research/quant_digests/2026-03-27_1244_dynamic-tsmom-turningpoint-continuation-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-27_1244_dynamic-tsmom-turningpoint-continuation-alpha.html`
