# Rank 427 / high-volume selloff -> 5m bounce fresh intake keep_P1

- 时间：2026-04-19 22:09 UTC
- 对象：`research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
- 动作：fresh intake first verdict
- 结论：`keep_P1`
- 正式 Rank：`427`

## 本轮只回答的 blocker
`5m hold12` 的正 gross 在统一成本、router-vs-all-signals 与 liquid-major 缩池后，是否仍保住可独立承接的 after-cost panic-bounce pocket。

## 最小复核
基于现成 artifact `reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_panel.csv`，只对 `signal=1` 的 `5m hold12` 做统一 `8bps` round-trip 扣减，并补两类最小诚实切片：

1. **all-signals / 全 8 个 liquid majors**
   - `n=117`
   - `net8 mean ≈ +11.23bps`

2. **all-signals / core4 缩池（BTC/ETH/SOL/BNB）**
   - `n=55`
   - `net8 mean ≈ +7.78bps`
   - `median ≈ +1.70bps`
   - 说明不是只能靠长尾小币才成立。

3. **all-signals / core5 缩池（BTC/ETH/SOL/BNB/DOGE）**
   - `n=70`
   - `net8 mean ≈ +14.03bps`
   - `median ≈ +9.45bps`

4. **router_top1 / strongest-only**
   - 全 8 币 `n=41`，`net8 mean ≈ -3.81bps`
   - core5 `n=35`，`net8 mean ≈ -3.16bps`
   - 说明这条线目前**不该收窄成 top1 shock router**；强行 strongest-only 反而把 edge 压没。

5. **symbol concentration 快看（all-signals / hold12 / net8）**
   - 正贡献：`BNB ≈ +61.85bps (n=5)`、`DOGE ≈ +36.98bps (n=15)`、`BTC ≈ +15.73bps (n=3)`、`SOL ≈ +9.58bps (n=29)`、`LINK ≈ +8.51bps (n=21)`、`ADA ≈ +4.98bps (n=21)`、`XRP ≈ +9.72bps (n=5)`
   - 负贡献：`ETH ≈ -11.48bps (n=18)`
   - 说明 pocket 不是单一币硬撑，但存在明显 side/universe 选择差异，后续 survivor 应优先回答 **是否应剔除 ETH、并把对象收窄成 core bounce sleeve 而非 strongest-only router**。

## 本轮 verdict
`Rank 427`：`high-volume selloff -> 5m bounce` 在统一 `8bps` 成本后，`all-signals` 口径于全 8 币与 core4/core5 缩池内都仍保留正的 after-cost pocket；但 `strongest-only router` 已转负，因此本轮诚实首判为 **保留到 P1**，对象定义应暂时停在 **5m fixed-hold panic-bounce sleeve**，而不是升级成 top1 router。

## 对 runtime 的影响
- 新对象获得正式 `Rank 427`
- Fresh intake 首判完成：`keep_P1`
- `Surviving candidate slot` 切换为 `Rank 427`，保留唯一一次 follow-up 预算
