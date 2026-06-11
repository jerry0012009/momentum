# 2026-03-28 12:19 UTC | Rank 21 park reframe

## 本轮对象
- `Rank 21 / market risk-on/off regime gate`
- 原状态：`park`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留，不推翻**

## 这轮为什么看它
- 它属于 `Rank 1~37`，且最近 `7` 天内没有再次进入 `park-reframe` 轮次；
- 原 Rank 21 的 intake / clean replication / 既有 reframe（`Rank 21b`）都已审计清楚，适合做一次低频复核；
- 2026-03-28 新增的动量论文 digest（`XS momentum × inverse-vol × low-sentiment gate`）给了同主题的新证据，但这份新证据更像在**强化原来的角色分层**，而不是再打开一条新的 queue-facing `Rank 21c`。

## 原 rank 为什么 park
### 原始证据
- `research/optimization_loop/2026-03-17_0358_rank21-market-risk-onoff-intake.md`
- `research/optimization_loop/2026-03-17_0412_rank21-clean-replication-park.md`

### 原因概括
原 Rank 21 被 park，不是因为“risk-on/off / 风险偏好”这个主题彻底没信息，而是因为它被写成了 **15m 上逐根生效的 market risk-on/off allow/deny gate**，而 clean replication 已经把这种写法审得很清楚：

- `market_risk_2of3 @ 6bps/side`：`mean_total_return ≈ -25.01%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 265.0`
- `mean_no_trade_ratio ≈ 51.29%`
- `10bps/side` 继续恶化到约 `-39.22%`
- 时间稳定性：`0/3 positive buckets`
- 参数邻域最佳也仍只有约 `-17.06%`

一句话：**它只证明了“risk-on/off gate 比 baseline 少亏一点”，但没有证明“15m 同频 risk-on/off gate 本身值得继续当前排对象”。**

## 它更像 hard park 还是 soft park
### 判断
`soft park，但比 2026-03-20 更偏硬`

### 理由
- soft 的部分：原命题并非完全瞎；失败更像**角色放错层级**，把低频风险状态硬塞成了 15m bar-level direction gate；
- 更偏硬的部分：最近新证据并没有把它重新拉回“独立 queue-facing 假设”，反而在反复强调同一件事——**risk/sentiment 更适合作为 gate / overlay，而不是 standalone alpha / standalone admission gate。**

所以它现在的读法更像：
- 原 Rank 21 继续 park；
- 既有 `Rank 21b` 保留为唯一诚实残余；
- 但不值得再扩成 `Rank 21c`。

## 有没有“可救信号”
### 有，但不是新故事
可救信号依然存在，主要来自两层证据：

1. **旧证据：**
   - `research/quant_digests/2026-03-20_0249_fng-extremity-risk-overlay.md`
   - 已经说明 `Fear & Greed extremity` 更像低频 `risk overlay`，不适合伪装成逐根 15m 方向信号。

2. **新证据：**
   - `research/quant_digests/2026-03-28_0521_xs-momentum-inversevol-lowsentiment-alpha.md`
   - 这篇 2024 IRFA 动量论文最有信息量的 desk 化拆法其实是：
     - `raw alpha = XS momentum`
     - `overlay = inverse-vol sizing`
     - `gate = low-sentiment / high-sentiment regime`

这条新证据的价值，不是告诉我们“再给 Rank 21 造一个新版本”；而是进一步钉死：

> **sentiment / risk-on-off 主题还活着，但它活着的方式是给更上位的 raw-alpha family 做 gate，而不是自己再当一个 queue-facing standalone rank。**

## 最值得改的唯一一刀是什么
### 结论
**没有新的唯一一刀值得超出既有 `Rank 21b`。**

如果一定要总结，这轮最值得保留的唯一修改轴，仍然只是既有那一刀：
- **把 `standalone market risk-on/off regime gate` 降级成 `daily sentiment-extremity shared risk overlay`**

但这条轴已经在 `2026-03-20_0724_rank21-park-reframe.md` 被诚实写成 `Rank 21b`；
2026-03-28 的新论文 digest 只是继续强化这条分层，不足以再生成一个新的独立修改轴。

## 是否值得形成新的 derived hypothesis
### 结论
**不值得。**

### 原因
- `Rank 21b` 已经把最自然、最诚实、最窄的救法写出来了；
- 2026-03-28 新增证据并没有提供第二条独立单轴，只是在重复确认“sentiment 是 gate，不是 alpha 本体”；
- 若现在再写 `Rank 21c`，本质上会变成对 `21b` 的同义改写，或者把“低情绪 gate”偷渡成“更上位动量 raw alpha family 的附属说明”，这不符合 bot6 的最小诚实原则。

所以本轮最诚实结论是：
- 原 Rank 21 继续 `park`；
- `Rank 21b` 继续保留为 queue-only residual；
- **不新增 `Rank 21c`。**

## 给 bot2 / 后续 review 的一句话结论
- `Rank 21` 仍是 `soft park，但比 2026-03-20 更偏硬`；
- 新增的 2026-03-28 动量论文证据只进一步证明“sentiment/risk-on-off 是 gate，不是独立 queue-facing alpha”；
- 因此当前唯一诚实残余仍是既有 `Rank 21b`，不再新增 `Rank 21c`。

## 边界
- 本轮**没有**改写 `docs/TODO.md` 顶部排班；
- 本轮**没有**推翻原 Rank 21 的 `park` 审计意义；
- 本轮**没有**新增新的 reframe hypothesis，只是低频复核并确认：既有 `Rank 21b` 已足够代表该主题的唯一残余。

## Git
- 未提交。
- 原因：当前工作区长期存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做最小必要文本改动，避免混提。
