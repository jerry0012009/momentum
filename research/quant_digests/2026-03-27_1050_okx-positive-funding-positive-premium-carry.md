# 别把 funding 套利只看 funding 数字：这份 2025 OKX 新仓库更该先测的是「正 funding × 正 premium」spot-perp carry pocket

- 主题类型：raw alpha
- 基础 alpha：同 venue 下，当永续合约既**资金费率为正**、又**价格高于现货形成正 premium** 时，做 `long spot / short perp`，同时赚 funding carry 与 rich-basis 向现货收敛；若只有 funding 为正、但 perp 并不贵，这条 carry 往往并不值得做。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 为什么这次值得进池
这次主材料不是论文 headline，而是一份很短但方向很对的 2025 新仓库：`R1cK-ChaN/crypto-funding-arbitrage`。

它最值钱的地方，不是“自动化监控 funding”这句废话，而是代码里其实已经写明白了一件对 desk 很重要的判断：

> **base alpha 不是“看到 funding 为正就去 short perp 收租”，而是“只有当 perp 真的比 spot 贵，同时 funding 也站在同一边时，这个 carry 才更像可做 pocket”。**

这条线对当前 desk 有直接价值，因为它属于我们明确要持续补的 `carry / funding / basis` raw alpha 素材池，而且能很快拆成最小实验：
1. funding 本身是 `8h` 节奏的现金流；
2. premium / basis 是 `1m / 5m` 可连续监控的状态；
3. 所以它天然不是“每根 bar 都出手”的主信号，而是**低频 carry 方向 + 高频 timing / veto** 的组合型 raw alpha。

## 2. 这份材料里真正值得抄的那一句
### 2.1 核心来源
**Repo source**
- **Author / Year**: `R1cK-ChaN` / 2025
- **Title**: *crypto-funding-arbitrage*
- **Venue**: GitHub repository
- **Repo URL**: <https://github.com/R1cK-ChaN/crypto-funding-arbitrage>
- **Readable URL**: <https://github.com/R1cK-ChaN/crypto-funding-arbitrage>
- **Raw README**: <https://raw.githubusercontent.com/R1cK-ChaN/crypto-funding-arbitrage/main/README.md>
- **Raw strategy file**: <https://raw.githubusercontent.com/R1cK-ChaN/crypto-funding-arbitrage/main/src/strategies/funding_arbitrage.py>
- **Raw OKX client**: <https://raw.githubusercontent.com/R1cK-ChaN/crypto-funding-arbitrage/main/src/exchange/okx_client.py>

**Paper ground truth**
- **Authors / Year**: Damien Ackerer, Julien Hugonnier, Urban Jermann / 2024
- **Title**: *Perpetual Futures Pricing*
- **Venue**: NBER Working Paper 32936（后续 2025 online 版见 *Mathematical Finance*）
- **DOI**: `10.3386/w32936`
- **Readable URL**: <https://www.nber.org/papers/w32936>
- **Published DOI**: `10.1111/mafi.70018`
- **Published URL**: <https://doi.org/10.1111/mafi.70018>

### 2.2 repo 到底写了什么
这份仓库虽然很短，但 `src/strategies/funding_arbitrage.py` 已经把主判断写得很直白：

```python
if funding_rate > self.funding_threshold:
    price_diff = swap_price - spot_price
    if price_diff > self.spread_threshold:
        return True
```

翻成人话就是：
- 先看 **funding 是否足够正**；
- 再看 **perp 是否真的比 spot 贵**；
- 两个条件都成立，才认为可以考虑去做 `long spot / short perp`。

这跟很多“funding dashboard 式读法”最大的差别在于：
**它不是把 funding 当单变量，而是把 funding + basis 同时当成 alpha 的定义。**

### 2.3 为什么这和理论是对齐的
Ackerer, Hugonnier, Jermann（2024）那篇 *Perpetual Futures Pricing* 的核心提醒是：
- perpetual 的价格锚定，靠的是周期性 funding；
- funding 机制决定了 perp 与 spot 如何被拉回；
- 若想把 perp 当成 carry / basis 交易对象，不能只看“有无 funding”，还要看**价格锚定当前偏在哪边**。

所以，把 repo 里的读法压成一句最有用的话就是：

> **carry 现金流要和 basis 方向站在同一边，才更像可交易的 raw alpha；否则 funding 可能只是表面上为正，但 rich/cheap 关系并不支持同向持仓。**

## 3. desk 化翻译：不要把它伪装成逐根 5m 主信号
这条 alpha 当然属于 `carry / funding / basis`，但它不是“每根 1m/5m bar 都能独立产生新边际信息”的那种 raw alpha。

更诚实的 desk 化口径应该是：
- **alpha 本体**：`long spot / short perp` 收 `正 funding + 正 premium 回归`
- **短周期角色**：`1m / 3m / 5m` 用来做
  - entry timing（避免在 premium 已被吃平后再追）
  - spread monitoring（看 rich basis 是否继续扩张）
  - exit / veto（funding 翻负、premium 消失、盘口塌陷）

也就是说：
**funding 决定“做不做这类 trade”，短周期 bar 决定“什么时候做、什么时候不做”。**

## 4. 我们自己的最小快检（OKX 公共 funding + ticker live snapshot）
### 4.1 数据口径
- **数据源**：OKX public
  - `/api/v5/public/funding-rate`
  - `/api/v5/market/tickers?instType=SWAP`
  - `/api/v5/market/tickers?instType=SPOT`
- **公开性**：公开可得，无需 key
- **频率**：funding 为 `8h` 节奏；premium 可按 `1m / 5m` 连续采样
- **样本**：`2026-03-27 10:55 UTC` 当下全部 `USDT-SWAP` 且有同名 `USDT` spot twin 的币种
- **规模**：共 `199` 个 spot-perp twin
- **实验口径**：只做 live cross-sectional state scan，不做历史回测；先回答“repo 这种双条件筛法，在当前市场到底有多稀疏”。

### 4.2 结果 1：正 funding 很常见，但“正 funding + 正 premium”并不常见
在 `199` 个 OKX `USDT` spot-perp twin 里：
- **`115` 个**当前 funding 为正
- 但其中只有 **`19` 个** 同时满足 `premium > 0`
- 也就是：**只有约 `16.5%` 的正 funding 状态，真的和正 premium 站在同一边**

这条数据很关键，因为它直接说明：
**如果只用 funding 选边，你会把大多数“方向没站对”的 carry 状态也一并收进来。**

### 4.3 结果 2：大币当前并不站在 repo 想要的 pocket 里
截至快检时：
- **BTC**：funding 约 **`+0.229 bps / 8h`**，但 premium 约 **`-5.48 bps`**
- **ETH**：funding 约 **`-0.006 bps / 8h`**，premium 约 **`-3.93 bps`**
- **SOL**：funding 约 **`-2.26 bps / 8h`**，premium 约 **`-7.19 bps`**

也就是说，至少在 majors 上，**你看 funding 面板不一定会看到一个该做的 spot-perp carry**。

### 4.4 结果 3：真正过筛的 pocket 更多出现在小币 rich-basis 状态
当前同侧 pocket 的示例：
- **CVX**：funding **`+0.5 bps / 8h`**，premium **`+30.12 bps`**
- **IOTA**：funding **`+1.0 bps / 8h`**，premium **`+7.15 bps`**
- **FOGO**：funding **`+0.5 bps / 8h`**，premium **`+16.11 bps`**

而 funding 为正但 premium 不支持的反例也很多：
- **SATS**：funding **`+1.0 bps / 8h`**，premium **`-18.73 bps`**
- **FLOKI**：funding **`+1.0 bps / 8h`**，premium **`-14.20 bps`**
- **OP**：funding **`+1.0 bps / 8h`**，premium **`-9.43 bps`**

这说明真正该测的不是“funding 有多大”，而是：
**`funding sign × basis sign × liquidity quality` 三者是不是一起站对。**

相关 artifact：
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/okx_funding_premium_snapshot_20260327_1050/all_usdt_swap_with_spot_snapshot.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/okx_funding_premium_snapshot_20260327_1050/summary.json`

## 5. 为什么我把它定性成“可独立复现，但还不算可直接落地完整策略”
因为 repo 本身还有两块明显没补完：

1. **执行逻辑还只是骨架**
   - `execute_arbitrage()` 里只有 `TODO`
   - `calculate_position_size()` 也只是直接返回 `max_size`

2. **没有把最关键的成本与风控冻结下来**
   - maker / taker 假设没写清
   - funding 预期与实际结算时点没拆开
   - spot/perp 双腿滑点、库存、借贷、交易所风险都没冻结

所以它现在更像：
**一条定义清楚的 raw alpha candidate，而不是已经能放心接实盘的完整执行栈。**

## 6. 但它很容易被 desk 化成完整策略骨架
### entry
对每个 `spot-perp twin` 定义：
- `funding_bps_now`
- `premium_bps = (perp - spot) / spot * 10,000`
- `edge_score = premium_bps + λ * expected_funding_bps - entry_cost_buffer`

最小版本可先用：
- `funding_bps_now > 0`
- `premium_bps > p_open`
- `edge_score > 0`
- 同时过 liquidity / blacklist / event veto

然后执行：
- **long spot**
- **short perp**

### exit
不要只写“拿到 funding 就走”，更诚实的 exit 应该至少有三种：
1. **premium 回到 close band**：例如 `premium_bps < p_close`
2. **funding 翻负或显著走弱**
3. **持仓过 funding boundary 后的固定观察窗**：如 `1~3` 个 funding period 内若 basis 不收敛就撤

### sizing
第一版别复杂：
- 单资产 cap
- 单 cluster cap
- `size ∝ min(edge_score, cap)`
- 再叠一层盘口深度 cap：`size <= x% of top-book / y minutes ADV`

### risk
这类 alpha 的风险不是方向判断，而是 plumbing：
- spot/perp 双腿成交不同步
- funding 窗口前 crowding / 抢跑
- 小币 rich basis 看起来肥，但深度与冲击极差
- 交易所/合约规格/下架/限仓风险
- 极端行情下，basis 可能先继续失真，再谈收敛

### cost
这类 alpha 最容易死在这里：
- 若只看 `+1 bps/8h funding` 就冲进去，**根本不够覆盖双腿进出场成本**
- 更诚实的最小门槛是：
  - `premium_bps + expected_funding_bps`
  - 必须明显大于 `spot leg fee + perp leg fee + 双腿滑点 + 安全 buffer`

所以第一轮别问“有没有 alpha”，先问：
**gross basis+carry 能不能先穿过成本生存线。**

## 7. 我会怎么排“下一步怎么测”
### P0：先做历史 funding boundary event study
对 `OKX BTC/ETH/SOL + 20~50 个有 spot twin 的 liquid alts`：
1. 拉过去 `30~90d` 的 funding history
2. 在每个 funding 时点记录：
   - funding sign / size
   - spot-perp premium
   - 未来 `1m / 5m / 15m / 60m` premium 收敛幅度
3. 比较四组：
   - `funding>0` only
   - `premium>0` only
   - `funding>0 & premium>0`
   - `funding>0 & premium>0 & liquidity gate`

第一问很简单：
**双条件组的后续 basis 收敛，是否显著好于 funding-only。**

### P1：把成本假设正式搬进来
至少分三档：
- maker-spot / taker-perp
- maker/maker
- taker/taker

若一条 pocket 只有在理想 maker/maker 下才活，那它就不能被写成“完整可落地 alpha”。

### P2：分 majors 与 small-caps 看 transfer boundary
因为当前快检已经很清楚：
- majors 很多时候不给 pocket
- 真正的 rich basis 往往在小币

所以必须拆成两条研究问题：
1. majors：edge 小，但流动性好
2. small-caps：gross 看起来大，但可能全被冲击吃掉

### P3：再决定它在 desk 里扮演什么角色
如果历史验证后成立，这条线可走三种落地形态：
1. **独立 carry alpha**：低频事件驱动 book
2. **shared veto**：禁止在 `funding>0 但 premium<=0` 时机械 short perp 收租
3. **sizing overlay**：按 `edge_score` 做强弱分层，不再一刀切

## 8. 一句话结论
这份 2025 repo 真正值得 desk 先拿走的，不是“自动盯 funding”，而是更朴素也更有用的那句：

> **spot-perp carry 不能只看 funding；只有当 perp 确实偏贵、funding 也站在同一边时，它才更像一条可复现的 raw alpha pocket。**
