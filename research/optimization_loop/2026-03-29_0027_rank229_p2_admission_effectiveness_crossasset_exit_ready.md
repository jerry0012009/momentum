# Rank 229 / ETH-led abnormal-day continuation (session-defined) — P2 admission 第 1 步：effectiveness / cross-asset 收口

- Time: 2026-03-29 00:27 UTC
- Target: `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- Step type: `P2 admission` / `effectiveness + cross-asset`
- Verdict: `keep_P2 -> exit-ready`

## 本轮要回答的问题
`Rank 229` 已经不再是 `BTC/ETH/LTC` 通用 abnormal-day continuation，而是更诚实的 `ETH-led session-defined` 对象。

当前 admission 第 1 步只回答两件事：
1. ETH 主 pocket 在更诚实的 `next-bar open` 入场口径下，成本后是否仍足够厚；
2. 把对象收缩成 `ETH-led` 之后，跨资产是否还保留最小可接受的旁证，还是已经退化成完全单点偶然 pocket。

## 最小复现口径
公开 `Binance Futures 5m`，最近约 `365d`，标的：`ETHUSDT / BTCUSDT / LTCUSDT`。

统一口径：
1. session offset 扫描 `0 / 4 / 8 / 12 / 16 / 20` 小时；
2. 对每个 session：
   - `ret_from_open_t = close_t / session_open - 1`
   - 用前 `30` 个 session 的 close/open 收益 rolling std 作为 `sigma_session`
   - 当 `|ret_from_open_t| >= k * sigma_session` 首次触发、且剩余 bar 数 `>= M` 时记为信号
3. **诚实执行**：不是在触发 bar 收盘成交，而是 `next-bar open` 同方向入场，持有到 session close；
4. 扫描 `k ∈ {1.0, 1.25, 1.5, 1.75, 2.0}` 与 `M ∈ {4,8,12}`；
5. 核对 gross / net-8 / net-12（round-trip 8/12 bps）。

产出文件：
- `reports/artifacts/rank229_p2_admission_effectiveness_crossasset/grid.csv`
- `reports/artifacts/rank229_p2_admission_effectiveness_crossasset/best_by_symbol.csv`
- `reports/artifacts/rank229_p2_admission_effectiveness_crossasset/summary.json`

## 关键结果
### 1) ETH 主 pocket 在 honest entry 下依然很厚
ETH 最佳 pockets（按 `net-12`）仍明显为正：

- `offset 20h / k=1.25 / M>=8`：`n=91`，gross `+80.2 bps`，net-12 `+68.2 bps`，hit-rate `69.2%`
- `offset 20h / k=1.25 / M>=4`：`n=94`，gross `+79.4 bps`，net-12 `+67.4 bps`，hit-rate `70.2%`
- `offset 0h / k=1.25 / M>=12`：`n=107`，gross `+67.3 bps`，net-12 `+55.3 bps`，hit-rate `56.1%`
- `offset 0h / k=1.25 / M>=8`：`n=111`，gross `+61.5 bps`，net-12 `+49.5 bps`

这说明前一轮 survivor 里看到的 ETH continuation 不是“只要把 entry 诚实化就消失”的脆弱幻觉；即便改成 `next-bar open`，ETH 主 pocket 仍然足够厚，足以继续占据 `Active P2`。

### 2) BTC 只剩薄旁证，不足以把对象重新包装成 cross-asset raw alpha
BTC 最好的组合只到：

- `offset 4h / k=1.25 / M>=12`：`n=116`，gross `+8.64 bps`，net-8 `+0.64 bps`，但 net-12 `-3.36 bps`

也就是说：
- BTC 不是完全反向或完全失真；
- 但它已经不足以支撑“这是一条跨资产都够厚的 abnormal-day continuation alpha”；
- 更诚实的说法仍是：**BTC 只能当薄旁证，不能当主腿。**

### 3) LTC 有稀疏尾部 pocket，但不是稳健的 admission 支柱
LTC 的最优格子表面上有明显正的 `net-12`：

- `offset 4h / k=2.0 / M>=4`：`n=37`，gross `+31.8 bps`，net-12 `+19.8 bps`，但 hit-rate 只有 `43.2%`

这更像：
- 高阈值、低频、尾部驱动的 pocket；
- 可以说明“LTC 并非系统性反向到足以推翻 hypothesis”；
- 但它的稳定性和可固定 spec 性显然弱于 ETH，不能作为 admission 主支撑。

## admission 解释
第 1 步真正改变系统认知的是：

- **ETH 主 pocket 不是假厚度。** 在更诚实的 `next-bar open` 执行下仍然足够厚；
- **cross-asset 不是 0，但也不够强到把对象重新升级成 multi-asset alpha。** BTC 只剩成本边缘旁证，LTC 只有稀疏尾部 pocket；
- 因此这条线最诚实的对象定义仍应保持为：
  - `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
  - 继续留在 `Active P2`
  - **但已经具备进入出口决策轮的厚度**，后续不该再回头重复做“它到底有没有 edge”这种开放式 admission。

## Runtime writeback
- `Active P2 slot` 维持 `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- `latest_result` 更新为：ETH 主 pocket 在 `next-bar open` 口径下仍保留 `~49–68 bps net-12` 的厚度；BTC 只剩薄旁证，LTC 仅有稀疏高阈值尾部 pocket，因此这条线继续维持 `ETH-led` honest scope，但已具备进入 `P2 exit decision` 轮的厚度
- `latest_admission_record` 指向本文
- `p2_rounds_since_level_change`: `1`
- `p2_consecutive_keep_p2`: `1`
- `p2_last_evidence_axis`: `effectiveness_crossasset_honest_entry`

## 一句话结果
`Rank 229` 在更诚实的 `next-bar open` 入场口径下，ETH 主 pocket 仍保留明显厚的成本后 edge（最佳 `net-12` 约 `+68 bps`）；BTC 只剩薄旁证、LTC 仅有稀疏尾部口袋，因此对象维持 `ETH-led` honest scope，但已足够推进到 `P2 exit decision` 轮，而不是继续做开放式 admission。
