# 2026-03-26 07:10 UTC — Rank 97 park reframe review

## 本轮对象
- `Rank 97`
- 原主题：`RSRS right-skew shared veto + sizing overlay`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留，不推翻**

## 为什么选它
- 按当前轮转，`50+` 号段这两天已连续覆盖（`50 / 51 / 52 / 76 / 92 / 96 / 101 / 105` 等），本轮切到 `80~110`。
- `Rank 97` 近 7 天未被 `bot6` 单独复盘。
- 它属于典型“看起来像还能救，但很容易重复讲旧故事”的条目，适合做一次低频审计：确认它到底还有没有必要再派生 `Rank 97b`。

## 原 rank 为什么 park
先回看原始 intake 与 clean replication，`Rank 97` 被 park 的原因很直接：

1. **原假设是把 RSRS right-skew 写成 shared veto / sizing overlay**，希望给现有三条 base setup（`breakout_short / ema_psar_long / fib_retest_long`）统一做仓位或否决层。
2. 但最小 clean replication 的结果并不只是“没那么好”，而是 **比 baseline 更差**：
   - `no_overlay` 总体约 `-0.8437`
   - `hard_veto` 约 `-1.1495`
   - `half_size_overlay` 约 `-1.0220`
   - `tiered_sizing_overlay` 约 `-1.1696`
3. **不是靠少做单就能改善**：`hard_veto` 砍掉交易数后仍更差。
4. **也不是轻量 size-down 就能救**：`half_size` / `tiered_sizing` 也没把结果拉回成本门槛之上。
5. **跨资产没有共享改善**：`positive_asset_ratio` 从 baseline 的 `1/3` 变成 `0/3`；BTC/ETH 都被拖差，SOL 只是接近打平。

翻成人话：这条线不是“方向对、执行糙”，而更像**它被放到 shared overlay 这个角色上时，本身就没有足够可兑现的信息量**。

## 它更像 hard park 还是 soft park
我的判断：**`soft park，但偏硬`**。

为什么不是纯 hard park：
- `RSRS / 支撑阻力强度` 这个大主题本身没有死；
- 之前队列里已经有更诚实的同主题收敛版：`Rank 12b`，把 S/R 主题改写成 `volume-weighted zone-persistence shared quality gate`；
- 说明“价格在支撑阻力附近的接受度/持久度”仍可能有信息，只是 **Rank 97 这版“right-skew -> shared sizing/veto”写法不对**。

为什么又说“偏硬”：
- 它已经做过一次很诚实的最小 clean replication，而且四个 arm 没一个把 baseline 推正；
- 当前失败不是小修小补能解释的量级；
- 如果还要继续救，最自然的一刀其实已经非常接近 `Rank 12b`，等于**它自己的残余价值已经被近邻提案消费掉了**。

所以它不是“主题彻底无效”的 hard park，但对 `Rank 97` 自身来说，已经**接近 hard enough**。

## 有没有“可救信号”
有，但很弱，而且不是属于 `Rank 97` 自己的独立可救信号。

### 仅存的可救信号
- `support / resistance strength` 这类信息，仍可能作为 **quality gate** 存在；
- `2026-03-19` 的相关 digest/队列已经把这类残余价值收敛到更窄的表达：
  - 不是“统一 sizing overlay”神谕；
  - 更像“预先冻结 zone 后，判断这个 zone 的持久度/接受度高不高”。

### 但为什么说它不够救 `Rank 97`
- `Rank 97` 的失败点，不是简单阈值没调好；
- 而是 **它把 RSRS right-skew 直接映射成三条 setup 的 shared veto / sizing**，这个职责层本身就站不住；
- 如果继续往“zone persistence / pre-frozen zone quality”方向改，已经不再是 `Rank 97` 的窄修，而是在重复 `Rank 12b` 的角色改写。

所以：**有主题层残余，没有 Rank 97 层残余。**

## 最值得改的唯一一刀是什么
如果硬要说“最值得改的一刀”，那就是：

- **把 `right-skew shared sizing/veto overlay` 改写成 `pre-frozen zone persistence / quality gate`**。

但这刀 **不值得在 Rank 97 名下再派生**，因为：
1. 这已经不是对 Rank 97 的局部修补，而是换职责；
2. 队列里已有近义、且更诚实的承载位：`Rank 12b`；
3. 再起一个 `Rank 97b`，只会制造“同主题重复 draft”。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因很简单：
- 原 `park` 的审计已经足够清楚；
- 现有“可救信号”并不指向 `Rank 97` 自己，而是指向**别的、已经存在的更好容器**；
- 若现在再 draft 一个 `Rank 97b`，大概率只是把 `Rank 12b` 换个说法重写一遍，不符合“每轮只提 1 条唯一主修改轴，且不要重复造轮子”的约束。

## 本轮最终结论
- `verdict = keep_park`
- 原因：`Rank 97` 更像 **soft park，但偏硬**；
- 可救信号：有主题层残余，但已被 `Rank 12b` 这类更诚实的 queue-only 提案吸收；
- 唯一主修改轴：若真要改，也应改成 `zone persistence quality gate`，但这不该再记在 `Rank 97` 名下；
- 因此：**不新增 `Rank 97b`，不写回 TODO，只保留本轮审计记录。**

## 对队列文件的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条 `Recently reviewed`
- `research/park_reframe/INDEX.md`：追加本轮索引
- `docs/TODO.md`：**不改**

## commit / 脏区说明
- 当前 repo 长期存在大量与本轮无关的脏文件。
- 本轮只做最小必要文档改动；**不做 commit**，避免混提。
