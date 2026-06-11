# 2026-03-29 09:29 UTC — Rank 234 / multiday MAX lottery XS continuation fresh intake → keep_P1

## 本轮执行对象
- target: `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md`
- action: 对 `multiday MAX / lottery rich-vs-cheap continuation` 做最小 fresh intake 首判，只回答它是否足够独立、是否值得进入前排 survivor。

## 读到的硬信息
1. 这篇 2021 Financial Innovation 论文给的是一条**独立的横截面 raw alpha**，不是 filter：`long high-MAX / short low-MAX`。
2. 原论文 headline 足够硬：`28d formation -> 1w holding` 的 `High MAX - Low MAX` 在 crypto 样本里有显著正 spread（文内给到 `3.03%/week` raw、`1.99%/week` alpha）。
3. 它与已入池的 `past-hour MAX rich-vs-cheap fade` 不是同义重复：后者是**短 formation / 短 holding / 反转**，这条是**更长 formation / 更长 holding / continuation**。
4. 但当前证据仍停在**论文层**，且作者样本明确更偏小币、低价币、低流动性币；迁移到 desk 关心的 liquid perp / 15m/5m 后，最先可能死在容量、成本与“只是 plain return-rank 换名”这三个问题上。

## 最小 distinctness 判断
这条线不该直接按“已有 MAX/lottery 家族所以算旧东西”处理。真正应保留的是：
- `MAX` 不是单一方向因子；
- 更合理的对象定义是 **formation-horizon-conditioned MAX family**；
- 当前这篇补的是其中的 **longer-formation continuation branch**，与 `past-hour MAX fade` 形成可证伪的符号翻转对照。

所以它**值得保留为独立对象**，但还不够诚实地直接进 `P2`：
- 还没有 desk 口径的 clean replication；
- 还没有回答 `MAX score` 是否优于 plain return-rank；
- 还没有回答 liquid majors / perp universe 下成本后是否还活。

## 正式结论
- 分配新正式编号：`Rank 234`
- first verdict: **`keep_P1`**
- runtime 语义：进入 `Fresh intake slot` 并锁定为当前唯一 `Surviving candidate`，保留 1 次最小 decisive follow-up 预算。

## 推荐的唯一 survivor follow-up 方向
若下一轮由 bot3 执行它的唯一 follow-up，最便宜且最 decisive 的动作应是：
- 在 liquid USDT perp universe 上做 `MAX horizon ladder` 最小快检；
- 至少比较 `1h / 24h / 72h formation` × `1h / 4h / 8h holding`；
- 并把 `MAX rank` 与 `plain return-rank` 并排；
- 只回答：**更长 formation 是否真的从 fade 翻成 continuation，且不是 plain momentum 换名。**

## 本轮会改变系统认知的话
`Rank 234 / multiday MAX lottery XS continuation` 与已存在的 `past-hour MAX fade` 构成同一家族里的 formation-horizon 符号翻转分支，因 distinctness 明确且论文证据够硬，本轮正式 `keep_P1` 并进入 survivor；但在回答 liquid perp 下是否真有 continuation、且是否优于 plain return-rank 之前，不升 `P2`。
