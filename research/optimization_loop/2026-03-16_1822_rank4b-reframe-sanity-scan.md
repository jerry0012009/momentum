# 2026-03-16 18:22 UTC｜Rank 4b reframe sanity scan：先改 model calibration，再决定要不要扩 pair scope

## 为什么做这轮
Jerry 同意把 `Rank 4` 不是直接复活，而是先开一个更窄的 `Rank 4b` 假设：
- 不推翻原 `Rank 4 = park`；
- 先看负结果到底更像 **pair 选错**，还是 **frozen-beta / spread 定义太粗糙**；
- 目标不是现在就证明 stat-arb 成立，而是找出**最低成本、信息量最高的下一刀**，然后再把它写进 `TODO`。

## 本轮约束
- 只使用本地现成缓存：`BTC/ETH/SOL` 三个 15m、120d price cache；
- 不新拉数据，不引入更大 universe；
- 只做 ad hoc sanity check，不把结果伪装成 formal verdict。

## 看了什么
在原版 `frozen-beta z-score spread` 之外，额外快速扫了三类变体：
1. `rolling-beta / adaptive spread`
2. `ratio spread`
3. 轻量 gate（`vol_calm` / `trend_neutral`）

并对少量参数做窄网格：
- `roll ∈ {48, 96, 192}`
- `entry_z ∈ {1.5, 2.0, 2.5}`
- `exit_z ∈ {0.0, 0.25, 0.5}`
- `max_hold ∈ {16, 32, 64}`

## 最重要的发现
### 1. 第一刀更像该改 `model calibration`，不是直接喊“换币种”
当前本地 cache 只有：
- `BTC/ETH`
- `BTC/SOL`
- `ETH/SOL`

所以现在如果直接说“先换 pair”其实不够诚实，因为**本地还没有足够新的 pair universe 可以判断**。真正的 pair-selection 扩样，要等新 symbols / 数据接进来后才值得做。

### 2. frozen-beta 可能确实过于悲观
在同一批缓存上，`rolling-beta + stricter entry_z` 的 pocket 明显比原版 frozen-beta 更像“值得再给一刀”：

- 原版 frozen-beta first pass：
  - `BTC/ETH ≈ -12.42%`
  - `BTC/SOL ≈ -22.91%`
  - `ETH/SOL ≈ -27.77%`

- ad hoc best pockets（仅作方向感，不是 formal verdict）：
  - `BTC/SOL`：`rolling-beta`, `roll=96`, `entry_z=2.5`, `exit_z=0.0`, `max_hold=32`, `vol_calm` gate
    - `trade_count = 19`
    - `cum ≈ +1.17%`
  - `ETH/SOL`：`rolling-beta`, `roll=192`, `entry_z=2.5`, `exit_z=0.0`, `max_hold=32`, `no gate`
    - `trade_count = 20`
    - `cum ≈ +2.43%`
  - `BTC/ETH`：即使在 best pocket 下也仍偏负，最好大约也只是 `≈ -2.20%`

### 3. regime / vol gate 有帮助，但不像第一主因
- `vol_calm` 对 `BTC/SOL`、`BTC/ETH` 有一定改善；
- 但真正把结果从“明显负”拉到“接近可重看”的，更像是：
  - `rolling beta`
  - 更严格的 `entry_z`
  - 更少、但更挑剔的交易次数

也就是说：**gate 更像 second-order refinement，不像第一主因**。

## 这轮最诚实的结论
- 这还**不够**把 stat-arb 从 `park` 直接拉回 `paper candidate`；
- 但它足够支持一个新的、更窄的假设：
  - **`Rank 4b = crypto stat-arb reframe`**
  - 第一刀不是盲目扩 universe，也不是直接重启大研究；
  - 第一刀应是：**在现有 `BTC/ETH/SOL` 上，把 frozen-beta 改成 `rolling-beta / adaptive spread`，并收紧 `entry_z`，做一次最小 clean replication v2**。

## 因此推荐的动作排序
1. **先落 `Rank 4b` 到 `TODO`**，但明确写成 `reframe hypothesis / opt-in narrow slice`；
2. `Rank 4b` 第一刀固定为：
   - `rolling-beta z-score spread`
   - 优先 `BTC/SOL`、`ETH/SOL`
   - `entry_z` 先看更严格的 `2.5`
3. 若这刀仍不硬：
   - 更诚实地维持 `park`
   - 不再继续为 stat-arb 占默认 Scout 主资源
4. 只有在这刀通过后，才值得进入下一层：
   - 更正式的 stability pack
   - 或真正的 pair-selection 扩样

## 对 TODO 的直接影响
因此本轮不建议：
- 直接撤销 `Rank 4 = park`
- 直接把 stat-arb 写回 active 主线
- 直接先喊 `BTC/COIN / BTC/MSTR` 而不承认本地暂无对应数据

本轮建议：
- 保留原 `Rank 4` verdict；
- 新增一个非常窄的 `Rank 4b` 条目，作为合法重开方式。
