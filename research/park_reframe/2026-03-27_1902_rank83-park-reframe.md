# 2026-03-27 19:02 UTC — Rank 83 park reframe

- Rank: `83`
- Theme: `Fib trend-strength admission layer`
- Original status: `park`（authoritative verdict 保留）
- This round verdict: `keep_park`

## 为什么这轮看它
- 按 `PARK_REFRAME_QUEUE` 的轮转规则，`50+` 号段今天已连续覆盖多条，本轮切到 `80~110` 段更符合低频轮转。
- `Rank 83` 已在 2026-03-19 完成 `source intake -> minimal clean replication -> cost stability check -> park` 的完整审计链，但最近 `7` 天没有被 `bot6` 单独做 park-reframe 复盘，符合本轮补位条件。
- 它还有一点“可救错觉”：`strong` 桶在低成本下看起来是正的，因此值得明确判断这是不是诚实的窄 reframe，还是只是样本收缩后的残余错觉。

## 原 rank 为什么 park
参考：
- `research/optimization_loop/2026-03-19_0750_rank83-fib-trend-strength-intake.md`
- `research/optimization_loop/2026-03-19_0805_rank83-fib-trend-strength-clean-replication.md`
- `research/optimization_loop/2026-03-19_0826_rank83-cost-stability-park.md`
- `research/quant_digests/2026-03-19_0525_fib-trend-strength-admission-layer.md`

原始故事不是“再发明一条新的 Fib entry”，而是把 `Fib retest_hold` 从二元 `hold/fail` 升级成 `weak / medium / strong` 三档 admission / sizing layer：
- `weak`：只守住 `0.618`，但没收回 `0.5`
- `medium`：收回 `0.5`
- `strong`：在 `medium` 基础上，再收回 `0.382` 或突破 `retest bar high`

minimal clean replication 给出的审计结论其实很明确：
- `base_binary @ 6bps/side`：`mean_total_return ≈ -1.83%`，`positive_asset_ratio = 0/3`
- `strength_filter @ 6bps/side`：`mean_total_return ≈ +1.18%`，`positive_asset_ratio ≈ 66.67%`，`retention ≈ 66.38%`
- `strength_sizing @ 6bps/side`：`mean_total_return ≈ +1.16%`，`positive_asset_ratio = 3/3`
- 但 bucket 细看时，真正有信息的几乎只剩 `strong`：
  - `medium`：`trades=5`，`mean_net_ret≈-0.106%`，`fail_4bars=100%`
  - `strong`：`trades=28`，`mean_net_ret≈+0.146%`，`fail_4bars≈42.86%`

接着 cost stability check 把它压回 park：
- `6bps/side`：`mean_total_return ≈ +1.16%`，`positive_asset_ratio = 3/3`
- `10bps/side`：`mean_total_return ≈ +0.27%`，`positive_asset_ratio = 2/3`
- `15bps/side`：`mean_total_return ≈ -0.83%`，`positive_asset_ratio = 0/3`

也就是说：
**这条线不是完全没信息，而是它留下的残余价值过度集中在“low-cost + strong bucket”这一小块；一旦 friction 提到更诚实的 desk 口径，跨资产结果就一起翻负。**

## 它更像 hard park 还是 soft park
我会把 `Rank 83` 定义为：**soft park，但偏硬**。

原因：
1. 不是 hard park，因为 `Fib 回踩后的强弱分层` 这个想法本身不是胡扯，至少 `strong` 桶确实比 `binary hold` 更像样；
2. 但它又偏硬，因为目前剩下的正 pocket 太依赖低 friction，而且 `medium` 桶基本没有被救活；
3. 原线承诺的是一个可 desk 化的 admission / sizing layer，不是“只在最强那点样本里看起来略正”；按当前证据，它还不到值得重新占位的程度。

## 有没有“可救信号”
有，但很窄：
- `strong` bucket 的后续质量明显好于 `weak/medium`，说明“回踩后确认强度”确实带一点信息；
- 这说明 Fib 主题里，**位置本身不够，确认强度可能比单纯触位更重要**；
- 但现在这个残余更像“别把 weak/medium 和 strong 混在一起”的实现纪律，而不是足够独立的新 queue-facing hypothesis。

换成人话：
**它留下的是“强回收比弱回收更像 continuation”，不是“Rank 83 这条 admission layer 已经值得重开”。**

## 最值得改的唯一一刀是什么
如果一定只保留唯一主修改轴，我会选：

**把三档 `Fib trend-strength admission` 收缩成 `strong-only` 的 Fib-lane sizing / allow 规则。**

trade on：
- 不再保留 `weak / medium / strong` 三档齐上的读法；
- 只在 `strong reclaim` 时对 `Fib retest_hold` 放行或给满仓，其余一律视作不够诚实的弱确认；
- 不改 universe、不加第二层 regime、不顺手改 exit。

trade off：
- trade density 会继续下降；
- 而且这很像把原本就脆弱的改善进一步收缩成“只看最好样本”；
- 如果改善主要来自 retention 大幅下降，而不是更稳的 post-cost expectancy，那它就只是切样本美化。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
1. 这条唯一可改的一刀，本质上只是把 `Rank 83` 原来的强弱分层再继续缩成 `strong-only`；
2. 它没有真正打开一个新的角色层，仍然只是原命题内部的更严版本，容易变成“把样本切到只剩最漂亮那一块”；
3. 而且它和已有的 `Rank 20b`（volume-price interaction admission layer）/ `Fib retest_hold` 既有 admission 审计高度重叠，更像本地实现边界，不像新的 queue-facing 派生假设；
4. 最关键的是：`15bps/side` 下已经 `0/3` 翻负，这说明它当前最缺的不是再起一个 `Rank 83b` 名字，而是承认这块 residual 还不够 desk 级诚实。

## 本轮结论
- 结论类型：`keep_park`
- 原 rank 为什么 park：因为三档 strength layer 虽在低成本下优于 binary hold，但 edge 基本只剩 `strong` 桶；成本提到 `15bps/side` 后跨资产一起翻负
- 更像 hard 还是 soft：`soft park，但偏硬`
- 可救信号：`strong` reclaim 比 `weak/medium` 更像 continuation，说明确认强度有一点信息
- 最值得改的唯一一刀：`把三档强弱分层收缩成 strong-only 的 Fib-lane sizing / allow 规则`
- 是否值得形成新的 derived hypothesis：`否`；这更像原 Rank 83 的实现收缩，而不是值得新起一条 `Rank 83b` 的独立 hypothesis

## 对 queue 的最小写回建议
- `docs/PARK_REFRAME_QUEUE.md`：追加一条 recently reviewed
- `research/park_reframe/INDEX.md`：追加本轮索引
- 不改 `docs/TODO.md`

## Git / 工作区备注
- 当前工作区存在与本轮无关的既有脏文件；本轮只做最小写回，不混做其他 rank 的改动，也不做混合提交。
