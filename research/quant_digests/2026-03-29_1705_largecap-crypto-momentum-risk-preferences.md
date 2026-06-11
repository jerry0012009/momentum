# 大市值币种里的动量才更像可交易 alpha：从风险偏好读 crypto momentum
- 时间：2026-03-29 17:05 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：大市值 / 高成交额子集上的横截面动量（long winners / short losers）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：momentum / cross-sectional / liquidity / universe / limited-attention
- 证据类型：论文证据（当前仅拿到摘要与元数据，属 abstract-only / weak-evidence）

## 1. 这次看了什么
这次看的是 **Juliane Proelss、Denis Schweizer、Bastien Buchwalter (2025)** 发表在 **Finance Research Letters** 的短文 **_Do risk preferences drive momentum in cryptocurrencies?_**。它最值得我们 desk intake 的，不是“crypto 里又有人证明 momentum 可能存在”，而是更具体地说：**动量更像是大市值、较高成交额币种里的可交易 alpha，小币尾部反而会把这个 alpha 稀释掉。**

## 2. 核心结论
- **一句话核心结论：** crypto momentum 不是“全市场通用”，而更像是 **大市值流动性桶里的 raw alpha**。
- 作者用 **survivorship bias-free dataset**，并显式区分 **market capitalization** 与 **trading volume**，去解释为什么旧文献对 crypto momentum 会得出互相打架的结论。
- 论文的直白读法是：**universe selection 本身就是 alpha 定义的一部分**；把太多小币、低成交币塞进来，得到的更可能是噪音、换手和摩擦，不是稳定 edge。
- 从 desk 角度，这篇东西最值钱的不是“再讲一次 momentum”，而是给出一个更实用的 intake 规则：**先在 top-liquidity / top-cap 子集里测动量，再决定是否向尾部扩表。**
- **一句话说明它怎么证明：** 作者靠的是一套去幸存者偏差的币种样本，再按规模与成交分层比较 momentum 策略是否还能成立。

## 3. 为什么和当前项目有关
它直接服务于我们当前最缺的那类东西：**可独立复现的 raw alpha 素材**。而且它不只是告诉你“测动量”，还告诉你 **先在哪个 universe 里测**。对 `1m / 3m / 5m / 15m` desk 来说，这很关键，因为短周期最怕的不是没有信号，而是把 signal、冲击成本和尾部噪音混在一起。若这篇判断成立，我们后续很多 XS momentum / leader-follower / reversal 实验都该先锁在 **高流动性主池**，而不是默认全市场扫一遍。

## 3.5 策略拆解（必填）
- 方向属性：横截面
- 基础 alpha：过去一段窗口的相对强弱延续（winner 继续强，loser 继续弱）
- regime：非必需；主读法先不加 regime
- filter / veto：只在 `top-cap` / `top-ADV` 币池内排序；低成交尾部默认 veto
- risk / sizing / execution overlay：等权或波动率缩放；short leg 单独设更严格的成交额/冲击成本门槛；统一 `next-bar open` 或近似 VWAP 执行

## 4. 可复刻的最小实验
- **研究假设：** 在 `top 20~30` 个高流动性 USDT perp / spot 币种里，横截面动量在短周期上比“全市场混合池”更稳定、更可交易。
- **一个可计算定义：** 每 `15m` 重算一次，按过去 `48` 或 `96` 根 `15m` 收益率排序；只在过去 `24h` 美元成交额最高的 `N` 个币里做 `long top quantile / short bottom quantile`。
- **最小回测切口：** `Binance/Bybit` 主流币，先做 `2023-01` 以来；比较 `top-20 liquid universe` vs `full tradable universe` 两组。
- **最该先看 2 个指标：** `after-cost spread return`、`short leg 是否贡献了大部分 alpha 但同时吃掉大部分成本`。如果第二点成立，就立刻补 `long-only + beta hedge` 对照臂。

## 5. 风险与保留意见
- 当前拿到的是 **摘要 + 元数据**，正文细节（精确 formation/holding、t-stat、分层阈值）还没拿到，所以这篇暂时只能算 **high-potential intake，不算已验证结论**。
- “大市值有效”不等于“越大越好”；真正起作用的可能是 **流动性、可得关注度、机构参与度** 的组合，而不只是 market cap 这一列数字。
- 这类 alpha 很可能出现 **short leg 贡献收益、long leg 承担容量** 的不对称结构；若 short 端 funding / 冲击过高，实盘最优解可能不是完整 L/S，而是 **liquid-winner long-only + hedge**。

## 6. 来源
- **Proelss, J., Schweizer, D., & Buchwalter, B. (2025). _Do risk preferences drive momentum in cryptocurrencies?_ Finance Research Letters, 73, 106531.**
- DOI: `10.1016/j.frl.2024.106531`
- Readable URL: `https://ideas.repec.org/a/eee/finlet/v73y2025ics1544612324015605.html`
- Metadata URL: `https://www.econbiz.de/Record/do-risk-preferences-drive-momentum-in-cryptocurrencies-proelss-juliane/10015211092`
- Publisher URL: `https://www.sciencedirect.com/science/article/pii/S1544612324015605`
