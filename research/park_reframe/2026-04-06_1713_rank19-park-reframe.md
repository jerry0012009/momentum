# 2026-04-06 17:13 UTC · Rank 19 park reframe

## 本轮范围与选择
- 本轮只复盘 `1` 条已 `park` 的 rank。
- 按 `docs/PARK_REFRAME_QUEUE.md` 当前轮转，`50+` 与 `80~110` 号段近几天已连续覆盖，因此本轮回到 `1~24`。
- `Rank 19` 上次 park-reframe 是 `2026-03-28 05:21 UTC`，已超过 `7` 天；且它属于“原 rank 已 park、已有既存窄派生 `Rank 19b`”的典型条目，适合做一次低频复看：**最近有没有新证据，值得在 `Rank 19b` 之外再派生新的窄 hypothesis。**
- 保留原 `park` verdict 的审计意义；不改 `docs/TODO.md` 顶部排班。

## 原 rank 为什么 park
原始审计来自：
- `research/optimization_loop/2026-03-17_0320_rank19-box-consolidation-park.md`

原 `Rank 19 = box consolidation / structure breakout` 被 park 的原因没有变：
- 宽版本 `accumulation_ready / narrow_accum_ready` 在 `BTC/ETH/SOL 120d 15m` 上是**高交易数持续亏损**：
  - `mean_total_return` 大约都在 `-20%` 左右；
  - `positive_asset_ratio = 0/3`。
- 更窄的 `box_breakout_ready` 虽然只小幅少亏（约 `-0.77%`），但：
  - `mean_trades ≈ 9.3`
  - `mean_no_trade_ratio ≈ 99.91%`
  - 样本薄到不足以诚实 admission。
- 时间 / 参数 / 跨资产 / 成本四项稳定性也没救回来。

翻成人话：
- 不是“compression / consolidation 主题彻底没信息”；
- 而是**把它直接写成 standalone box-breakout 策略**这件事已经被审计清楚：宽版一直亏，窄版又稀到不够当策略证据。

所以原 `park` verdict 必须保留。

## 它更像 hard park 还是 soft park
**仍然更像 `soft park`，但比 2026-03-28 那次更偏硬。**

原因：
- 对 **原版 standalone `box consolidation breakout`**：已经接近 `hard park`；
- 对 **compression 仍可能保留某种 residual 信息**：还不能完全说死，所以整体仍保留 `soft park`；
- 但这层 residual 现在更像在**外流到新的 raw-alpha compression family**，而不是继续留在旧 `Rank 19` 名下做 shared gate 微调。

## 有没有“可救信号”
**有，但没有超出既有 `Rank 19b`；而且最近新证据反而让它更偏向“主题外流”，不支持再派生 `Rank 19c`。**

这次最相关的新旁证有两条：
1. `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
   - 给出的不是旧 rank 那种 shared gate 读法，而是 **bottom-quartile BB compression breakout 的 standalone raw alpha 候选**；
   - 但公开 proxy 快检结果仍偏负，说明“压缩突破”若要成立，更像要带完整 breakout 壳，而不是回到旧 `Rank 19` 的 box 规则里继续补丁。
2. `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
   - 更进一步把 compression 主题写成 **quality-weighted squeeze release × ATR-defined R shell** 的完整 raw alpha；
   - 这条证据值钱的地方在于：它强调的是 `setup + quality scoring + sizing + risk shell` 一整套，而不是“旧 Rank 19 再改一个更细的 shared gate 就能救活”。

因此这次的新证据并没有给出一条“贴着旧 Rank 19、且不同于既有 `Rank 19b` 的第二条单轴”；相反，它们更像在说：
- compression 主题如果还有活路，
- 更自然的宿主是**新的 standalone raw-alpha family**，
- 而不是在旧 `box consolidation breakout -> shared gate` 这条 residual 上继续细分。

## 最值得改的唯一一刀是什么
**若只保留旧 rank 语境下唯一还诚实的一刀，仍然只是既有 `Rank 19b`：**

> 把 standalone `box consolidation breakout` 降级成 `close-range compression` 的 shared long-admission + short-veto gate。

但要强调：
- 这条一刀**已经被起草过**；
- 本轮没有出现比 `Rank 19b` 更诚实的新一刀；
- 最近新证据也没有支持再往下细切成 `Rank 19c`。

## 是否值得形成新的 derived hypothesis
**不值得。结论：`keep_park`。**

更准确地说：
- 原 `Rank 19` 的 `park` 继续保留；
- `Rank 19b` 仍是它唯一诚实、足够窄、且 bot2 可直接判断是否入板的既存派生表达；
- 最近 `compression / squeeze` 新证据虽然增加了主题热度，但它们把主题推向的是**新的 standalone raw-alpha 宿主**，而不是旧 `Rank 19` 可再诚实派生的一条 queue-facing 单轴；
- 因此本轮不新增 `Rank 19c`，也不把 `Rank 19b` 升级成主循环任务。

## 本轮固定回答
### 原 rank 为什么 park？
因为 standalone box-consolidation breakout 在 `BTC/ETH/SOL 120d 15m` 上表现为：宽版持续亏、窄版极端稀疏，不足以 admission。

### 它更像 hard park 还是 soft park？
`soft park`，但比上次更偏硬；对原 standalone 策略读法已接近 hard park。

### 有没有可救信号？
有，但没有超出既有 `Rank 19b`；最近的新 compression / squeeze 证据更像把主题外流到新的 raw-alpha family，而不是支持再派生 `Rank 19c`。

### 最值得改的唯一一刀是什么？
仍然是既有 `Rank 19b`：**把 standalone box breakout 降级成 `close-range compression` shared long-admission + short-veto gate。**

### 是否值得形成新的 derived hypothesis？
**不值得。** 本轮保持 `keep_park`。

## 最小审计结论
- `source_rank`: `Rank 19`
- `status`: `keep_park`
- `original verdict kept`: `park`
- `park 倾向`: `soft park，但更偏硬`
- `note`: 原 rank 的 residual 仍只到既有 `Rank 19b` 为止；2026-03-30 与 2026-04-06 的新 compression/squeeze 证据把主题继续推向新的 standalone raw-alpha family，不足以在旧 `Rank 19` 名下再诚实派生 `Rank 19c`

## 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Git
- 未 commit。
- 原因：工作区存在大量与本轮无关的既有脏文件；本轮只做最小必要文档改动，不安全混提。
