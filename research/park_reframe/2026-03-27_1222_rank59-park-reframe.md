# 2026-03-27 12:22 UTC — Rank 59 park reframe

## 本轮对象
- `Rank 59`
- 原状态：`park`
- 本轮结论：`keep_park`

## 为什么选它
- 近 7 天内未见 `bot6` 复盘 `Rank 59`。
- 当前轮转仍优先看 `50+` 号段；近期已连续覆盖 `50 / 51 / 52 / 54 / 55 / 57 / 58`，因此顺手补看同段、且仍处于 `park` 的 `Rank 59` 更合适。

## 读到的原始审计结论
主要参考：
- `research/optimization_loop/2026-03-18_1537_rank59-source-intake.md`
- `research/optimization_loop/2026-03-18_1557_rank59-clean-replication.md`
- `research/optimization_loop/2026-03-18_1640_rank59-time-stability-park.md`
- 近期相关 digest：`2026-03-22_2339_janis-breakout-ema-role-gate.md`、`2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`

### 1) 原 rank 为什么 park？
原 Rank 59 研究的是 **Ichimoku 的 Kijun + cloud-side continuation gate**，想把它作为 15m continuation 的 shared 结构确认层。

原审计里它没有被直接判成“纯未来函数”，而是被更诚实地判成：
- 在 `ema_psar_long` 上，`cloud_side` / `kijun+cloud_side` 确实有一点“少亏”迹象；
- 但在 `fib_retest_long` 上，改善主要靠 **极端砍样本**（`kijun+cloud_side` retention 只剩约 `6.06%`）；
- 在 `breakout_short` 上几乎没有修好问题；
- 便宜 time-stability check 之后，`ema_psar_long / cloud_side` 也只是 **最后一段转正**，前三桶读法不稳定（大意：`bucket_1` 明显负、`bucket_2` 仍负、`bucket_3` 才转正）。

所以它不是“完全没信号”，而是 **只留下很窄、很晚、很 setup-specific 的残余**，不足以继续占 desk 默认资源位，最终被压回 `park / evidence pool`。

### 2) 它更像 hard park 还是 soft park？
- 我判断：**`soft park`，但已经偏硬。**

原因：
- 它不是 data leakage 型的硬死；
- 但残余价值已经很薄，而且主要集中在 `EMA-PSAR long` 一条 lane；
- 一旦要求跨 setup、跨时间桶更诚实一点，改善就明显塌掉。

## 可救信号有没有？
有，但很有限，只能算 **弱可救信号**：
- `ema_psar_long` 上 `cloud_side` / `kijun+cloud_side` 的确比 base 少亏；
- 说明“更慢的趋势防守线/云外站稳”这类信息，不是完全没用；
- 但它更像 **慢趋势上下文 / avoid-chop 语义**，不像一条还值得单独派生的新 rank。

反过来，否定信号更强：
- `fib_retest_long` 的改善主要来自 retention 崩塌，不够诚实；
- `breakout_short` 基本无效；
- time stability 只剩后段 pocket，说明不是稳定主轴。

## 最值得改的唯一一刀是什么？
如果硬要提一刀，唯一像样的一刀其实是：
- **把 Ichimoku 的云侧 / Kijun 从“continuation gate”进一步降级成更慢、更弱的 HTF context-only long-bias overlay。**

但这刀我不建议再单独派生。

原因很直接：
- 这条修改轴，本质上已经被近期 desk 上更通用、也更诚实的角色改写吸收：
  - `Rank 25c`：把 EMA 从 co-trigger 降级成 HTF context-only gate；
  - `Rank 35b`：保留 higher-tf bias，只删掉过严的 VWAP reclaim；
  - 以及 2026-03-22/23 两篇 EMA role-split digest，本身就在强调“慢趋势线更像 context gate，不像平级触发器”。
- 换句话说，`Rank 59` 留下的那点残余，不够独特；再派生 `Rank 59b`，很大概率只是把 **“慢趋势上下文”** 换个 Ichimoku 壳再讲一遍。

## 是否值得形成新的 derived hypothesis？
- **不值得。**

原因：
1. 原 `park` 审计已经讲清楚：它留下的是 setup-specific late pocket，不是稳定新主轴；
2. 唯一还能写的一刀，本质上已被 `Rank 25c / Rank 35b` 这类现有提案吸收；
3. 若再写 `Rank 59b`，大概率只是重复“慢趋势 context gate”这条旧故事，而不是新的、窄而独立的 hypothesis；
4. 这会削弱原 `park` verdict 的审计意义，不符合 bot6 的职责边界。

## 结论
- 原 rank 为什么 park：因为 Ichimoku Kijun/cloud-side 只在 `EMA-PSAR long` 留下薄弱 residual，在 `Fib` 上主要靠极端砍样本、在 `breakout_short` 上几乎无效，而且时间稳定性不够。
- 更像 hard 还是 soft：**soft park，但偏硬**。
- 有没有可救信号：有，只有一点慢趋势上下文/avoid-chop 残余。
- 最值得改的唯一一刀：若硬改，只能继续降级成 **HTF context-only long-bias overlay**。
- 是否值得形成新的 derived hypothesis：**否，`keep_park`。**

## why not now / 审计备注
- `Rank 59` 的 residual 更像被现有 `EMA context-only / higher-tf bias` 家族吸收，而不是还值得单列一个 `Rank 59b`。
- 因此本轮选择保留原 `park` 的审计意义，不新增派生假设。

## 文件改动
- 新增本轮日志：`research/park_reframe/2026-03-27_1222_rank59-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Git
- 当前 repo 存在大量与本轮无关的既有脏文件；为避免混提，本轮不做 commit。
