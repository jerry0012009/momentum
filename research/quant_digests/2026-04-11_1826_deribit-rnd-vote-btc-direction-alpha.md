# 别把这份 2026 options signal repo 只读成 PDF 可视化：对 short-cycle desk，更该先测的是「nearest-expiry RND unanimous vote × BTC perp direction」这条 raw alpha

- 时间：2026-04-11 18:26 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `app.py`）+ 2022/2023 BTC options 论文元数据 grounding + Deribit BTC options public live probe
- 主题类型：raw alpha
- 基础 alpha：**BTC 近到期期权隐含出的 risk-neutral density（RND）若在 `skew / tails / peak / band` 这几层上朝同一方向倾斜，短周期 BTC perp 更值得沿该方向做；本质不是“IV 高低”，而是“期权分布形状已经把偏向哪边写出来了”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/external-data/risk-neutral-density/skew/tails/peak/band/directional/btc/perpetual/deribit/binance/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + BTC options 文献 grounding + 交易所公共 live 数据

## 1. 先回答一句：base alpha 是什么？

**base alpha = 近到期期权隐含分布形状对 BTC 短周期方向有信息。**

翻成人话：
不是单纯看 ATM IV 升了还是降了，
而是看 **整个近到期 strike surface 拼出来的概率分布，到底更偏向上侧、下侧、肥尾、还是 mode 已经整体偏移**。

如果这些 shape signal 朝同一边站队，
那它就不是 shared gate，也不是纯解释层；
它本身就是一条可以单独拿来交易 `BTC 1m/3m/5m/15m perp` 的 **external-data directional raw alpha**。

---

## 2. 为什么这轮值得写，而不是继续补又一条纯价量形态

因为当前素材池里已经有不少：
- spot/perp basis
- pairs / stat-arb
- OFI / microstructure
- prediction-market parity / continuation

但 **“公开 BTC options surface → 短周期方向”** 这条线还没有被单独展开成一条 clean raw alpha。

而且这次挑的不是“期权市场解释一切”这种大词，
而是一份 2026 repo 已经写成可运行信号机的旁支：

> **用 Deribit 公开期权链直接重建 risk-neutral PDF，然后把 PDF 的形状翻成 LONG / SHORT / NO TRADE。**

这比再写一篇纯 filter / overlay 更能扩充 raw alpha 素材池。

---

## 3. 这份 repo 真正给了什么

主材料是 **mario-badea (2026), `iv-signal-scanner`**。
它最值得拿走的，不是 GUI，而是 `app.py` 里这条非常明确的骨架：

### 3.1 数据输入
- 从 **Deribit public API** 拉指定 expiry 的 BTC options 链；
- 读取每个 strike 的 `mark_iv`；
- 不需要私钥，不需要私有数据库。

### 3.2 中间层：从 IV surface 重建 risk-neutral PDF
repo 用的是：
1. spline 平滑 IV surface；
2. 用 Black-Scholes 重定价 call；
3. 再用 **Breeden-Litzenberger** 二阶导近似恢复 risk-neutral density。

也就是说，它不是“用几个 strike 的 eyeballing”，而是试图把 **整条 surface 的形状** 压成可计算的分布。

### 3.3 最关键：四票表决，不是一条孤立指标
`compute_signals()` 里有 4 个独立投票层：

1. **skew**
   - 比较 spot 上下两侧的概率质量；
   - `p_up - p_dn` 足够大则给 LONG，反之给 SHORT。

2. **tails**
   - 比较远离 spot 两侧尾部的概率质量；
   - 判断 fat-tail 风险偏向哪边。

3. **peak**
   - 看 PDF 的 mode 是否整体偏离当前 spot；
   - mode 明显在 spot 上方给 LONG，在下方给 SHORT。

4. **band**
   - 看概率是否大量跑出 `±3%` band；
   - 若 outside-band 很高，则把它当“市场在 pricing big move”，并沿 skew 方向给票。

最终规则非常朴素：

> **只有当活跃投票全都指向同一边，才输出 final LONG / SHORT；否则 NO TRADE。**

这点对 desk 很重要，因为它天然自带一个“没一致就别做”的 admission 机制。

---

## 4. 文献 grounding：为什么这不是纯拍脑袋 repo

### 4.1 2022 *Journal of Financial Markets*
**Alexander, Deng, Feng, Wan (2022), _Net buying pressure and the information in bitcoin option trades_**。

OpenAlex abstract 给出的核心点很值钱：
- Deribit **tick-level option prices** 里确实有信息；
- OTM 期权价格不仅受 vol trader 影响，也受 **directional trader** 影响；
- 这种方向性在 2021 bubble 期尤其明显。

翻成人话：
**BTC options 不是一层被动贴现壳；链上的方向预期、尾部对冲需求、order imbalance 会真实写进曲面里。**

### 4.2 2021 *Digital Finance*
**Woebbeking (2021), _Cryptocurrency volatility markets_**。

Crossref abstract 明确说：
- 用 granular intraday crypto options data 可以稳定抽出 implied volatility index；
- 不同计算法得到的指数序列 cointegrated；
- 对应 ECM 还能当成 **market-implied tail-risk indicator**。

翻成人话：
**期权面不是只对“未来波动大小”有信息，对尾部风险结构本身也有信息。**
这正好给 repo 的 `tails / band / shape` 读法做地基。

### 4.3 2023 *Risks*
**Winkel, Härdle (2023), _Pricing Kernels and Risk Premia implied in Bitcoin Options_**。

这篇进一步说明：
- 比特币 options 的 pricing kernel 会随期限变化；
- short-dated 与 long-dated 的 risk premium shape 不一样；
- 投资者愿意为短期价格波动保险支付显著 premium。

对我们 desk 的翻译不是“去研究宏大风险偏好”，而是：

> **front expiry 的分布形状，往往比远月更像短周期交易者的实时偏向。**

所以第一轮最该测的是 **nearest-expiry directional vote**，不是把所有期限一锅炖。

---

## 5. live honesty check：当前 Deribit 公共快照到底长什么样？

我按 repo 的核心逻辑，直接对 **Deribit BTC options 当前 11 个活跃 expiry** 做了一次 live probe（见 artifact）。结果不算花，但很有用：

- **11 个 expiry** 里：
  - `LONG = 6`
  - `SHORT = 2`
  - `NO TRADE = 3`
- **前 6 个近到期（1d / 2d / 3d / 4d / 6d / 13d）全部给 LONG 或偏 LONG**。
- 最远的 `25SEP26`、`25DEC26` 则转成 **SHORT**。
- 中间期限如 `26JUN26`、`26MAR27` 出现 **投票冲突**，所以 repo 规则会老实输出 `NO TRADE`。

### 5.1 前端期限的具体数字
当前快照里，前 5 个最近 expiry 大致是这样：

- `12APR26`（1d）：`p_up - p_dn ≈ +7.48%`，final = **LONG**
- `13APR26`（2d）：`p_up - p_dn ≈ +3.25%`，final = **LONG**
- `14APR26`（3d）：`p_up - p_dn ≈ +4.02%`，final = **LONG**
- `15APR26`（4d）：`skew=LONG`，`tails=LONG`，final = **LONG**
- `17APR26`（6d）：`skew=LONG`，`peak=LONG`，final = **LONG**
- `24APR26`（13d）：`tails=LONG`，`peak=LONG`，虽 `skew` 不再强，但 final 仍是 **LONG**

### 5.2 远端期限给了什么提醒
- `25SEP26`（167d）：`skew=SHORT`、`peak=SHORT`、`band=SHORT`，final = **SHORT**
- `25DEC26`（258d）：主要由 `peak` 下移给出 **SHORT**
- `26JUN26`（76d）：`skew/peak/band` 偏 LONG，但 `tails` 偏 SHORT，最终 **NO TRADE**

这对 desk 的启发很直接：

> **front expiry 更像短周期交易信号；中远期更像 risk-premium / macro-vol 视角。**

所以别把所有期限混成一个总分。

---

## 6. 为什么我把它归类成 raw alpha，而不是 filter / overlay

因为这条线可以单独闭环：

- **交易对象**：BTC perp（Binance / Bybit / Deribit 都可）
- **方向**：front-expiry RND final signal 的 LONG / SHORT
- **入场**：统一投票后入场
- **不做的时候**：投票冲突就 NO TRADE
- **退出**：固定 horizon / sign flip / time-stop
- **成本**：按 perp taker 或 maker-taker 混合口径扣

它不是“给别的 alpha 打补丁”才成立。

当然，它也可以顺手给别的东西做 overlay：
- 给 breakout / continuation 做 confirm；
- 给 MR fade 做 veto；
- 给 OI / funding / top-trader 等外部信号做多源一致性过滤。

但那是二次用途。

**第一性分类，仍然应该是 raw alpha。**

---

## 7. 最小可复现实验，应该怎么搭

### 7.1 研究假设
若最近到期 BTC options surface 重建出的 RND 在 `skew / tails / peak / band` 上一致偏多或偏空，则未来 `BTC perp 5m/15m` 更容易沿该方向漂移。

### 7.2 最小信号定义
每 `1m` 抓一次最近到期（先试 `1d~7d`）的期权链：
- 算 `final_signal ∈ {LONG, SHORT, NO TRADE}`；
- first lane 先只交易 `LONG/SHORT`；
- `NO TRADE` 直接空仓。

### 7.3 最小交易壳
先别搞复杂：
- **标的**：`BTCUSDT perp`
- **entry**：`final_signal` 连续两帧一致才进
- **exit A**：持有 `1 / 3 / 5` 根 `5m` bar
- **exit B**：或 `15m × 1 / 2 / 4` 根
- **exit C**：中途 signal 反向则提前走
- **size**：先固定 notional；第二轮再按 `|p_up - p_dn|` 或 active-vote count 分层

### 7.4 成本口径
至少显式跑三档：
- `4 bps` round-trip（maker-ish）
- `8 bps` round-trip（保守 taker）
- `12 bps` round-trip（更严口径）

### 7.5 必做 A/B
1. **front-only**：只看最近到期
2. **front-agree-2of3**：最近 3 个 expiry 至少 2 个同向
3. **front-minus-far conflict veto**：若 front LONG 但 far SHORT，是否 size-down 或直接 veto

真正该先回答的问题不是“回测曲线美不美”，而是：

> **front-expiry RND vote 到底有没有稳定的 5m/15m sign edge。**

---

## 8. 当前最诚实的 verdict

**Verdict：值得进研究池，而且优先级不低。**

原因不是 repo 自带了一个漂亮 GUI，
而是它同时满足：

1. **base alpha 清楚**：options-implied distribution shape → BTC short-horizon direction
2. **公开可复现**：Deribit public API 即可拉链
3. **最小实验快**：`1m` 采样 + `BTC perp 5m/15m` 就能开测
4. **live snapshot 不空**：不是所有 expiry 都在喊同一句话，front / mid / far 的差异反而说明这里真有结构信息

但也要老实说两点：
- repo 自带 backtest 主要是 **synthetic IV surface**，不能拿来当 live 证据；
- Breeden-Litzenberger 对 surface 平滑很敏感，近到期 / 缺口 strike / 稀疏报价时可能会抖。

所以这轮最对的推进方式不是“立刻信它”，而是：

> **先把它做成 front-expiry 方向信号，再看 BTC perp 上 `5m/15m` 成本后能不能活。**

---

## 9. 下一步怎么测

1. **先做 14 天 front-expiry replay**
   - 每 `1m` 拉最近到期 BTC options 链
   - 重建 RND
   - 存 `skew/tails/peak/band/final`
   - 同步对齐 `BTCUSDT perp 1m/5m/15m`

2. **先跑最简单的 sign test**
   - `final=LONG` 后看未来 `5m/15m/30m/60m` sign hit-rate 与 mean bps
   - `final=SHORT` 同理
   - `NO TRADE` 作为基准组

3. **再跑 cost-aware trade shell**
   - `2-frame confirm`
   - `time-stop`
   - `sign-flip exit`
   - `4/8/12bps` 三档成本

4. **最后才做结构增强**
   - front-only vs front+2of3
   - front-far conflict veto
   - active-vote-count sizing

如果这四步里，`5m` 成本后还能留下明显正期望，
这张卡就该升到 replication queue；
如果只在极少数时段有效，那也至少能留下一个高信息量的 **options-sidecar admission layer**。

---

## 10. 来源

1. **mario-badea (2026). _iv-signal-scanner_. GitHub Repository.**  
   - Repo URL: `https://github.com/mario-badea/iv-signal-scanner`  
   - Readable URL: `https://github.com/mario-badea/iv-signal-scanner`  
   - Raw README: `https://raw.githubusercontent.com/mario-badea/iv-signal-scanner/main/README.md`  
   - Raw source: `https://raw.githubusercontent.com/mario-badea/iv-signal-scanner/main/app.py`

2. **Alexander, C., Deng, J., Feng, D., & Wan, C. (2022). _Net buying pressure and the information in bitcoin option trades_. Journal of Financial Markets.**  
   - DOI: `10.1016/j.finmar.2022.100764`  
   - Readable URL: `https://doi.org/10.1016/j.finmar.2022.100764`

3. **Woebbeking, M. (2021). _Cryptocurrency volatility markets_. Digital Finance.**  
   - DOI: `10.1007/s42521-021-00037-3`  
   - Readable URL: `https://doi.org/10.1007/s42521-021-00037-3`

4. **Winkel, B., & Härdle, W. K. (2023). _Pricing Kernels and Risk Premia implied in Bitcoin Options_. Risks.**  
   - DOI: `10.3390/risks11050085`  
   - Readable URL: `https://doi.org/10.3390/risks11050085`

5. **本地 live probe artifact**  
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/deribit_rnd_signal_probe_2026-04-11.csv`
