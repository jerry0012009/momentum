# 2026-03-28 05:21 UTC｜bot6 park-reframe｜Rank 19

## 0) 本轮选择（为什么是 Rank 19）
- 本轮仍只处理 `1` 条已 `park` 的旧 rank，不改 `docs/TODO.md` 顶部排班，不替 `bot2 / bot3` 分配任务。
- 轮转上，近期 `50~79` 与 `80~110` 号段已连续覆盖；`Rank 1~24` 中又要优先避开最近 `7` 天刚复盘过、且没有新证据的条目。
- `Rank 19` 上次 park-reframe 在 `2026-03-19 11:11 UTC`，距今已超过 `7` 天；它属于已 `park` 且已有一条既存窄派生（`Rank 19b`）的条目，适合做一次低频复看：**最近有没有足够新证据，值得在 `Rank 19b` 之外再派生新的窄假设。**

## 1) 原 Rank 为什么 park？
原始审计来自：
- `research/optimization_loop/2026-03-17_0320_rank19-box-consolidation-park.md`

原 Rank 19 被 park 的核心原因很集中：它把 `box consolidation / structure breakout` 写成了 **standalone entry family**，但结果呈现出典型的“两头都不诚实”失败：

- 宽版本 `accumulation_ready` / `narrow_accum_ready`：
  - `mean_total_return` 大约都在 `-20%` 左右；
  - `positive_asset_ratio = 0/3`；
  - 交易数不少，但持续亏。
- 更窄的 `box_breakout_ready`：
  - 虽然只小幅少亏（约 `-0.77%`）；
  - 但 `mean_trades≈9.3`、`mean_no_trade_ratio≈99.91%`，样本薄到不足以拿来 admission。
- Light Stability Pack 也没有救：
  - 时间稳定性 `0/3` bucket 为正；
  - 参数邻域最不差仍为负；
  - `BTC/ETH/SOL` 三条腿全负；
  - friction 从 `6 -> 20bps/side` 持续恶化。

翻成人话：
- 不是“压缩后释放”这个主题完全没信息；
- 而是 **把它直接写成独立 box-breakout 策略** 这件事已经被审计消费：
  - 宽版一直亏；
  - 窄版又薄到不够当策略证据。

所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`，但已经比 2026-03-19 那次更偏硬。**

原因：
- 作为 standalone `box consolidation breakout` 策略，它已经该停，这一点没有变化；
- 但它留下过一条可解释的残余：`compression` 更像 shared context，而不像独立开仓键；
- 只是这条残余在 2026-03-19 已经被很诚实地收敛成了既有 `Rank 19b`，所以今天再看时，soft 的空间已经变窄。

## 3) 有没有“可救信号”？
**有，但仍然只是既有 `Rank 19b` 那一级的可救信号；最近没有足够新的证据支持再派生一条 `Rank 19c`。**

可救信号本身没变：
- 原 Rank 19 说明了宽版 structure breakout 不行；
- 最窄版又提示 `compression` 可能更像环境筛子，而不是 alpha 本体；
- 因而“把 compression 降级成 shared long-admission + short-veto gate”这条角色改写仍然成立。

但这次复看后，更重要的判断是：
- 最近 `docs/RECENT_PAPER_SEEDS.md` 与 `research/quant_digests/INDEX.md` 并没有出现一条新的、同样贴着 `compression / box / consolidation` 主题、且能形成**第二条不同于 Rank 19b 的单轴**的新证据；
- 现有可讲的残余，仍然就是 2026-03-19 那次已经起草过的 `Rank 19b`；
- 再往下切，很容易滑成：
  - 继续细调压缩阈值；
  - 或顺手叠第二层 regime / exit / bounce-quality；
  - 这都会违反 bot6 的“每轮最多 1 条唯一主修改轴”纪律。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得保留的一刀，仍然是既有 `Rank 19b`：把 standalone `box consolidation breakout` 降级成 `close-range compression` shared long-admission + short-veto gate。**

也就是说：
- 不再根据 box breakout 本身直接开仓；
- 只把过去 `N` 根 close 是否处在窄区间，当成现有 `Fib retest_hold / EMA-PSAR continuation / breakout-short` 的 shared allow/deny 层；
- long 侧优先当 admission；
- short 侧优先当 veto / sizing，而不是加码器。

本轮没有出现比 `Rank 19b` 更值得保留的新一刀。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原 Rank 19 的 `park` 继续保留；
- 既有 `Rank 19b` 仍是它唯一诚实、足够窄、且 bot2 可直接判断是否入板的派生表达；
- 最近没有出现足够新的同主题证据，支持再从 Rank 19 身上切出第二条窄派生；
- 因此本轮不新增 `Rank 19c`，也不把 `Rank 19b` 升级成主循环任务。

## 6) trade on / trade off（本轮只做审计，不新起草）
### trade on
- 保留既有 `Rank 19b` 的读法：`compression` 只当 shared context，不再当 standalone box-breakout entry。

### trade off
- 放弃继续从 Rank 19 衍生第二条近义候选；
- 避免为了显得有产出而重复包装同一残余信息；
- 若未来没有新的同主题外部证据，Rank 19 更应继续停留在“原 park 保留 + 既有 19b 备查”状态。

## 7) 本轮固定回答（简版）
### 原 rank 为什么 park？
因为 standalone box-consolidation breakout 在 `BTC/ETH/SOL 120d 15m` 上表现为：宽版持续亏、窄版又极端稀疏，不足以 admission。

### 它更像 hard park 还是 soft park？
`soft park`，但比 2026-03-19 更偏硬；作为 standalone 策略已审计完，残余信息只剩既有 `Rank 19b` 那一级。

### 有没有“可救信号”？
有，但没有超出既有 `Rank 19b`；最近没有新证据支持再派生 `Rank 19c`。

### 最值得改的唯一一刀是什么？
仍是：**把 standalone box breakout 降级成 `close-range compression` shared long-admission + short-veto gate**。

### 是否值得形成新的 derived hypothesis？
**不值得。** 本轮保持 `keep_park`。

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 19` 读法 = `soft park`，但偏硬；
- 可救残余仍只收敛到既有 `Rank 19b`；
- 本轮不新增 `Rank 19c`，也不改 `TODO`。

## 9) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) Git
- 未 commit。
- 原因：workspace 存在无关脏文件 / 未跟踪文件；本轮只做最小必要文档改动，不安全混提。
