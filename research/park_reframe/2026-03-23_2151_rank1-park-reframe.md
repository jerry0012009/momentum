# 2026-03-23 21:51 UTC | Rank 1 park reframe

## 本轮对象
- `Rank 1 / τ-band / no-trade breakout filter`
- 原状态：`park`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留，不推翻**

## 为什么这轮又看 Rank 1
- 按 `Rank 1~37` 的低频队列轮转，当前低号段里可复看的 parked rank 基本都已在最近 7 天扫过；
- 但 `Rank 1` 在 2026-03-20 上次 reframe 之后，新增了更贴 breakout 本体的新证据：
  - `research/quant_digests/2026-03-23_2140_cta-breakout-fullstack-cost-survival-check.md`
- 这条新证据虽然不是原版 `τ-band`，但它直接回答了一个相关问题：**“单靠 breakout + 一点确认是否够，还是必须把 exit/risk/cost 一起看？”**

## 原 rank 为什么 park
原始审计来自：
- `research/optimization_loop/2026-03-16_0355_tau-band-first-verdict.md`
- `research/optimization_loop/2026-03-16_0912_scout-rank1-honest-recheck.md`

原 Rank 1 被 park 的核心原因没变：
1. `τ-band` 相对 raw breakout **更不差**，能压一点假突破；
2. 但在 `BTC/ETH/SOL 120d 15m` 最小 clean-room 上，**绝对 post-cost return 仍为负**；
3. honest recheck 拿到真新 bar 之后，结论也没有翻正；
4. 所以它更诚实的位置一直只是 `execution guard / evidence pool`，不是可独立升级的 alpha。

一句话：**原 Rank 1 证明了“裸 break 不够”，但没证明“静态 τ-band 本身足够救活 breakout”。**

## 它更像 hard park 还是 soft park
### 判断
`soft park`

### 理由
- `hard` 的部分：把 `static τ-band` 当 standalone rescue，这条路已经基本审计完；
- `soft` 的部分：breakout 之后需要额外确认这件事本身没死，只是原来的实现太薄。

所以它不是“主题彻底作废”，而是“**原角色与原写法已经不值得继续磨**”。

## 这次有没有新的可救信号
### 有，但不足以再派生新一条 Rank 1c
本轮唯一新增证据来自：
- `2026-03-23_2140_cta-breakout-fullstack-cost-survival-check.md`

这条 digest 给出的关键信息是：
1. Donchian breakout 主题本身仍能组成**完整 raw alpha 骨架**；
2. 但一旦把 `ATR stop / slow exit / volume / cost` 放回完整链路，**默认参数在近 90 天 5m 公共数据上仍未过成本生存线**；
3. 也就是说，问题并不是“再给 breakout 加一个更花的微确认就自然活”，而是**breakout 家族本身要想活，往往得靠完整 risk/exit/cost 治理**。

这对 Rank 1 的意义更像：
- 它继续支持“别把第一根 break 直接当正式票”；
- 但它**不支持**再从 Rank 1 上额外切出一条新的微确认分支；
- 相反，它更像在提醒：`Rank 1b` 已经是足够诚实的残余表达，再往下切很容易沦为“继续给 breakout 加小滤镜”。

## 最值得改的唯一一刀是什么
### 结论
**仍然是既有 `Rank 1b` 的那一刀：把 static τ-band 改写成 two-stage outside-persistence continuation gate。**

本轮没有出现比 `Rank 1b` 更值得保留的新单轴。

为什么不是新一刀：
- 新 digest 强调的是 **完整 breakout skeleton 的成本治理**；
- 这已经超出 Rank 1 这种“单薄确认层”该承担的角色；
- 若硬从这里再派生 `Rank 1c`，大概率会滑向多轴改写：`entry + exit + ATR + cost + volume` 一起上，违反 bot6 的单轴纪律。

## 是否值得形成新的 derived hypothesis
### 结论
**不值得。**

更准确地说：
- `Rank 1` 原 park 结论不变；
- `Rank 1b` 仍是它最诚实、最窄、且已足够清楚的派生表达；
- 2026-03-23 这条 CTA breakout 新证据，**只够强化“breakout 要看完整成本生存线，不该继续在 Rank 1 上切更多微确认故事”**；
- 因此本轮不新增 `Rank 1c`。

## 本轮固定回答
### 1. 原 rank 为什么 park？
因为静态 `τ-band` 虽比 raw breakout 更不差，但成本后仍负，且 honest recheck 没翻案。

### 2. 它更像 hard park 还是 soft park？
`soft park` —— breakout 需要确认这个主题还在，但 `static τ-band standalone rescue` 这条具体写法已基本走完。

### 3. 有没有“可救信号”？
有，且仍然只落在既有 `Rank 1b / outside-persistence` 这一条上；本轮新 digest 没再给出第二条更诚实的单轴。

### 4. 最值得改的唯一一刀是什么？
仍是：**`static τ-band -> two-stage outside-persistence gate`**。

### 5. 是否值得形成新的 derived hypothesis？
**不值得。** 现有 `Rank 1b` 已经把残余信息表达得够窄；再派生新分支会滑向多轴 breakout full-stack 重写。

## 结论
- 本轮状态：`keep_park`
- 原 rank：保留 `park`
- 派生状态：维持既有 `Rank 1b`，不新增 `Rank 1c`

## 给队列的最短写法
- `2026-03-23 21:51 UTC | Rank 1 | verdict=keep_park | original verdict kept=park | note=soft park；2026-03-23 的 CTA breakout fullstack 新证据只进一步说明 breakout 家族若要活更依赖完整 risk/exit/cost 骨架，不足以在既有 Rank 1b（two-stage outside-persistence）之外再诚实派生 Rank 1c`

## Git
- 未提交。
- 原因：本轮只做最小必要文本改动；且当前 worktree 存在无关脏文件，避免混提。
