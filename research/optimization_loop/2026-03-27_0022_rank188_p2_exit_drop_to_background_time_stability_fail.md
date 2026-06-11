# Rank 188 / extreme-only sparse top-k shock reversal skeleton — P2 exit decision drop_to_background

- 时间：2026-03-27 00:22 UTC
- 对象：`Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- 轮次角色：bot3 P2 exit decision
- 结论：`drop_to_background`

## 本轮只回答一个问题
只围绕上一轮留下的唯一 blocker：

> `extreme-only + top-k + 16-bar sparse + BTC veto` 这条窄 pocket 的 `time stability`，是否已经足以支持它进入 `P3 / paper trade / paper launch`。

不重开 effectiveness / cross-asset / parameter / honesty 旧轴；只用最小新增时间切片，把出口三选一收口。

## 沿用的 runtime truth（不重复证明）
在进入这一轮之前，系统已知：
1. `Rank 188` 不是 dense 版本那种“高换手直接杀死”的明显负 edge；
2. 但它当前只剩 **很薄的 net pocket**，不是厚 edge；
3. cross-asset broadness 不够，主要更像少数币硬撑的窄 pocket；
4. `8-bar` 回到负值，说明 cadence 轴存在明确脆点；
5. honesty / execution realism 没看到新的 fatal flaw。

因此，这轮唯一合法的新问题就是：
- **这条窄 pocket 是否至少在时间维上不是“只活在最近一小段”。**

## 本轮新增证据：120d 三分桶 time stability（只看当前合法对象）
我按当前已压缩后的对象口径，补了最小时间切片 proxy：
- universe：沿 admission 阶段保留的主流 perp 横截面（`ETH/BNB/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/DOT/SUI`；`BTC` 只作 gate）
- signal family：同一条 `adaptive shock-threshold` 横截面反转骨架
- lookbacks：`8/16/32/64`
- shock trigger：rolling `30d` 的 `|return|` `90%` 分位
- gate：`BTC 4h SMA > 24h SMA`
- 只检查当前合法对象的两个近邻：`top-k=2` / `top-k=4`
- cadence：`16-bar sparse rebalance`
- 执行：`next bar`
- 将最近 `120d` 等分成 3 个时间桶，直接看这条 pocket 是否三段都站得住

### 结果读法
#### `top-k=2`
- 全样本：gross 约 `+0.099 bps/bar`；net（按单边 `2bps` 估算）约 `+0.088 bps/bar`
- 但三分桶表现是：
  - **前 1/3：gross `-0.008 bps/bar`；net `-0.015 bps/bar`**
  - 中 1/3：gross `+0.147 bps/bar`；net `+0.133 bps/bar`
  - 后 1/3：gross `+0.158 bps/bar`；net `+0.144 bps/bar`

#### `top-k=4`
- 全样本：gross 约 `+0.109 bps/bar`；net 约 `+0.092 bps/bar`
- 但三分桶表现是：
  - **前 1/3：gross `-0.051 bps/bar`；net `-0.060 bps/bar`**
  - 中 1/3：gross `+0.094 bps/bar`；net `+0.072 bps/bar`
  - 后 1/3：gross `+0.283 bps/bar`；net `+0.263 bps/bar`

## 这组 time stability 证据改变了什么
它回答得很直接：

- 这条 pocket **不是“三段都能守住”的稳定对象**；
- `top-k=2` 与 `top-k=4` 都在前 1/3 失守，说明问题不是某个单一 `top-k` 设定偶发翻车；
- 后两段显著更强，尤其最后 1/3 明显抬高全样本结果，说明 **当前 pocket 主要是近段 regime 贡献，不是跨时间都站得住的持续 edge**。

翻成人话：
> 它不是“薄，但稳定”；而是“薄，而且明显更像最近窗口 pocket”。

而在 `Rank 188` 已经同时具备：
- net edge 薄、
- cross-asset 不宽、
- cadence 脆、

这三个已知约束的前提下，只要 `time stability` 还显示“前 1/3 不守正、收益集中在后 2/3”，就已经足够构成最终出口的决定性负面回答：
- **不够诚实进 `P3`**；
- 也不再适合继续挂在 `Active P2` 等下一轮救火。

## 为什么结论是 `drop_to_background`
### 为什么不是 `promote_P3`
不成立。
`P3` 需要的是“即便对象窄，也至少有足够像样的时间稳定性，值得进入 paper trade / paper launch”。

但现在看到的是：
- 三分桶里前 1/3 对 `top-k=2/4` 都不守正；
- 组合总成绩主要靠后两段、尤其最近段抬起来；
- 这和之前已经知道的“薄 edge + 窄 broadness + cadence 脆点”叠在一起后，读法只能更保守，而不是更激进。

### 为什么不是 `one-time P2->P1 re-scope`
也不成立。
当前并没有出现新的、单一且明确的更窄 spec 可以合法重写：
- `extreme-only`
- `top-k`
- `16-bar sparse`
- `BTC veto`

这条线已经被压缩得足够窄；此时再退回 `P1`，并不会得到新对象，只会变成把已经回答掉的出口问题重新伪装成“再看看”。

### 为什么是 `drop_to_background`
因为这次终于补齐了唯一剩余 blocker，而且答案是否定的：
- **time stability 没能给出支持 `P3` 的读法；**
- 在薄 edge / 窄 broadness / cadence 脆点 已经成立的前提下，这已经足以把它收口为当前不值得继续前排占位的对象。

## 本轮唯一改变系统认知的话
**`Rank 188` 的 `extreme-only + top-k + 16-bar sparse + BTC veto` pocket 在最近 `120d` 三分桶里，对 `top-k=2/4` 都出现“前 1/3 不守正、后 2/3 才转强”的时间集中度，因此它更像近期 regime pocket，而不是足够稳定、值得进入 `P3` 的 paper-trade 候选；在既有薄 edge、窄 broadness、cadence 脆点前提下，本轮应直接 `drop_to_background`。**

## 系统影响
- `Rank 188` 退出 `Active P2 slot`；
- 不进入 `Paper launch queue`；
- 不触发新的 `P2->P1` re-scope；
- 回到 `Background pool`，默认不自动重开。
