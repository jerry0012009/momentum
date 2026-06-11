# Rank 267 P2 admission：cross-asset stability 显示 majors 不成立，当前更像 alt-basket 驱动

- 时间：2026-03-31 10:44 UTC
- 对象：Rank 267 / crypto factor momentum × size/vol rotation
- 任务类型：P2 admission / cross-asset stability
- 结论：`done`（但结论为 `cross-asset blocker`）

## 本轮只执行这一个小点
按 `BOT2_BOT3_STATE.md` 的第 1 个 pending 小点，只检查同一套已知最强骨架在不同资产子集上的稳定性；不扩表、不新增 sleeves、不把题目偷换回泛 effectiveness。

固定口径：
- universe：沿用上一轮 Rank 267 replication 的 24 个 Binance USDT perp 高流动标的
- bar：`4h`
- ranking：`7d`
- holding：`24h`
- rotation：`1d` sleeve-level winner rotation
- sleeves：`momentum / size / low-vol`
- 成本：统一按单边 `10bps`，用横截面参与率近似 round-trip 成本
- 对比：`full universe`、`BTC/ETH/SOL majors`、`ex-majors alt basket`、以及 `leave-one-asset-out`

原始 artifact：
- `reports/artifacts/rank267_cross_asset_20260331/rank267_cross_asset_summary.json`

## 关键结果
### 1) full universe 仍为正，但强度明显低于上一轮 survivor follow-up 写法
- full-universe static mean net:
  - `momentum`: `+55.96 bps/period`
  - `size`: `+5.35 bps/period`
  - `low-vol`: `-74.39 bps/period`
- full-universe best-known rotation（同一骨架）:
  - `+80.05 bps/period`
  - hit rate `59.28%`
  - picks：`momentum 250 / size 222 / lowvol 223`

这说明：
- 这条线**没有塌成单一币幻觉**；
- 但一旦按 cross-asset admission 重新严看，最稳的并不是“majors 也跟着一起赚钱”，而是“全市场里主要靠 alt basket 维持净边”。

### 2) majors 单独拆开后，并不支持直接朝 P3 走
`BTC / ETH / SOL` 单独成 basket 后：
- static mean net:
  - `momentum`: `-22.52 bps/period`
  - `size`: `-21.36 bps/period`
  - `low-vol`: `-13.70 bps/period`
- rotation：`+11.17 bps/period`
- hit rate：`50.07%`

这不符合“cross-asset admission passed”的口径。也就是说，**把高流动 majors 单独拎出来后，这条线几乎只剩手续费边缘，不能证明它在更干净、更可承载的币上仍成立。**

### 3) alt basket 才是主要利润来源
`ex-majors` alt basket：
- static mean net:
  - `momentum`: `+66.61 bps/period`
  - `size`: `+15.97 bps/period`
  - `low-vol`: `-83.54 bps/period`
- rotation：`+117.44 bps/period`
- hit rate：`58.85%`

因此目前更准确的描述不是“Rank 267 在 cross-asset 上 broadly 成立”，而是：

> **Rank 267 当前看到的净边，主要来自 majors 以外的高流动 alt basket；majors 自身并未给出足够像样的成本后支持。**

### 4) leave-one-asset-out 没有暴露“单一币拯救全局”
最差几组 leave-one-out rotation mean net：
- drop `NOMUSDT`: `+88.09 bps/period`
- drop `SOLUSDT`: `+88.69 bps/period`
- drop `LINKUSDT`: `+89.66 bps/period`
- drop `ZECUSDT`: `+89.72 bps/period`
- drop `ETHUSDT`: `+89.92 bps/period`

最好几组：
- drop `ONTUSDT`: `+104.00 bps/period`
- drop `DOTUSDT`: `+109.53 bps/period`

所以 blocker **不是**“只靠某一个币抬出来”；更像是**一整个 alt pocket / alt basket** 在抬结果，而 majors 并没有同步跟上。

## admission 结论
这一步该改变的系统认知是：

> `Rank 267：cross-asset blocker 明确；leave-one-out 仍为正，说明不是单一币幻觉，但 BTC/ETH/SOL majors 单独拆开几乎不赚钱，当前净边主要由 ex-majors alt basket 支撑，因此本对象不再适合按“broad cross-asset passed、继续直接冲 P3”来理解，而应进入出口决策。`

## 为什么这不是 promote_P3 证据
按 policy，这一步要回答的是“净边是否在 majors 与 leave-one-out 下仍成立”。现在答案是：
- `leave-one-out`：成立
- `majors`：**不成立**

因此它没有通过这轮 `cross-asset stability` admission，不能再把当前 P2 叙事写成“只差一点点就能放心 paper”。

## 对 runtime 的直接影响
- 当前 `cycle_plan` 第 1 项应写为 `done`
- 当前小点 `result` 应写为 `Rank 267：cross-asset blocker 明确，转入出口决策`
- `Active P2` 的最新结论应更新为：
  - 不是单一币依赖；
  - 但 majors 不过关、净边主要由 ex-majors alt basket 驱动；
  - 因而当前更接近“带 blocker 的出口判断”，而不是无条件继续朝 `promote_P3` 倾斜。
