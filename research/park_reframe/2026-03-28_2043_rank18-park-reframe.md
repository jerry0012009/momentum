# 2026-03-28 20:43 UTC · Rank 18 park reframe review

## 本轮结论（先给人看的短版）
- source_rank：`Rank 18 / EMA neighborhood consensus / plateau vote`
- 本轮 verdict：`keep_park`
- 原 `park` verdict：**保留，不推翻**
- 我对它的当前读法：**soft park，但比 2026-03-21 更偏硬**
- 本轮唯一判断：`Rank 18` 的残余信息，当前仍只诚实收敛到既有 `Rank 18b`（把 standalone entry 降级成 shared abstain / trend-readiness veto gate）；最近新增证据不足以再派生 `Rank 18c`

## 为什么这轮轮到 Rank 18
- 按 `bot6` 轮转规则，近期 `50+` 与 `80~110` 已连续覆盖；本轮回到 `1~24` 号段。
- `Rank 18` 上次 park-reframe 是 `2026-03-21 18:15 UTC`，已略超 7 天窗口；且最近新增了两条与“高阈值 abstain / 只做高置信度段”直接相关的新证据，值得低频复看一次。
- 同时，`Rank 18` 仍是 queue-facing 的已 park rank，但目前没有被写回 `TODO` 前排，不会抢 `bot2 / bot3` 主循环。

## 本轮读到的关键证据
1. 原 clean replication：`research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
2. 上次 reframe 结论：`research/park_reframe/2026-03-21_1815_rank18-park-reframe.md`
3. 新旁证 A：`research/quant_digests/2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md`
4. 新旁证 B：`research/quant_digests/2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`

---

## 1) 原 rank 为什么 park？
原始 clean replication 的失败并不含糊：
- `plateau_vote_5of9_spread_guard` 在 `BTC/ETH/SOL 120d 15m` 上，`mean_total_return ≈ -19.89%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 157`，并非靠“样本太少无法判断”
- 成本梯度 `10/15/20bps` 下继续恶化到约 `-29.36% / -39.63% / -48.42%`
- 参数邻域没有出现“由负翻正”的稳定平台

翻成人话：
- **EMA 邻域平台共识** 这件事，放在 `15m crypto` 上当 **standalone entry alpha**，已经被审得很清楚：会少亏一点，但还是负，而且不是临门一脚型失败。
- 所以原 `park` 结论仍有完整审计意义，不能因为“最近又看到 abstain / high-confidence 论文”就翻案。

## 2) 它更像 hard park 还是 soft park？
我这轮仍把它读成：**`soft park`，但比 2026-03-21 更偏硬。**

为什么不是 hard park：
- 它相对 `anchor_10_40` 的确少亏（约 `-30.21% -> -19.89%`）；
- 而且天然伴随高 `no_trade_ratio`，说明“EMA 邻域一致性”并非完全没信息。

为什么又比上次更偏硬：
- 最近新增两条证据都在强化同一个方向：**高阈值 abstain / 只交易高置信度段** 更像一条上位 raw-alpha / intrabar trigger family 的语言，不是 Rank 18 自己还能继续分叉出新 queue-facing 假设的证据；
- 换句话说，新增证据支持的是“把它降级成 gate 的职责更合理”，而不是“原主题还有第二条、第三条窄救法”。

## 3) 有没有“可救信号”？
有，但信号还是老那一类，而且更像被既有 `Rank 18b` 吸收：

### 可救信号
1. **少亏而不是转正**
   - plateau 共识版明显比 anchor 少亏，说明“EMA 邻域是否一致”仍有一点交易质量信息。

2. **天然像 abstain 机制**
   - 这条线自带高 no-trade ratio，本来就更像“别在没走出来的时候乱开仓”。

3. **最新旁证只在强化 high-confidence / abstain 语义**
   - `2026-03-20 α/β abstain`：强调小位移不做、极端冲击不追。
   - `2026-03-27 BTC SI lagged-tech`：minute score 只有在高阈值、短延续口袋里才勉强像交易触发器。
   - 这两条都在说：**先分辨什么时候不做/只做高置信度段**，而不是继续把原指标当 standalone alpha。

### 但为什么这些还不够派生新假设
- 它们都没有提供一个**不同于 `Rank 18b` 的新单轴**；
- 相反，它们只是把 `Rank 18b` 的语言进一步坐实：**该主题更适合做 abstain / readiness gate，而不是 entry engine。**

## 4) 最值得改的唯一一刀是什么？
**仍然只有既有那一刀最诚实：把 Rank 18 从 standalone entry 降级成 shared abstain / trend-readiness veto gate。**

也就是：
- 不让 Rank 18 自己触发开仓；
- 只在已有 setup 触发时，用 plateau consensus 去决定 `allow / abstain`；
- 第一刀仍该是 `baseline vs abstain-only gate` 的 strict A/B。

本轮没有看到比这更自然、也更诚实的新切法。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因很简单：
- 值得保留的残余已经在 `Rank 18b` 里被表达了；
- 新证据没有给出新的唯一主修改轴；
- 如果这时再写 `Rank 18c`，大概率只是把“high-confidence abstain / minute trigger”换个说法重复包装，属于不诚实扩写队列。

## 6) trade on / trade off（本轮只作为复核，不新起草）
既有 `Rank 18b` 的取舍仍成立：
- **trade on**：用 EMA 邻域一致性去少做低质量段；
- **trade off**：trade density 下降，而且很容易落入“砍单美化”而非真实 edge；所以只能做 strict A/B，不能顺手偷带第二轴。

本轮没有出现值得改写这组 trade on / trade off 的新证据。

---

## 最终结论（bot6 标准口径）
- `verdict`: `keep_park`
- `original_park_verdict_kept`: `yes`
- `park_type_read`: `soft park, but more hard-leaning than 2026-03-21`
- `salvage_signal`: `有，但只进一步收敛到既有 Rank 18b；不足以新增 Rank 18c`
- `single best cut`: `仍是既有 Rank 18b：standalone entry -> shared abstain / trend-readiness veto gate`
- `new derived hypothesis this round`: `none`

## 对 queue 的实际动作
- 不新增 active reframe candidate
- 只在 `docs/PARK_REFRAME_QUEUE.md` 的 `Recently reviewed` 追加一条本轮记录
- 只在 `research/park_reframe/INDEX.md` 追加本轮索引
- 默认不改 `docs/TODO.md`

## Git / 工作区说明
- 本轮只做最小必要文档写入。
- 当前工作区长期存在大量共享脏文件；为避免混入无关改动，本轮**不做 selective commit**。
