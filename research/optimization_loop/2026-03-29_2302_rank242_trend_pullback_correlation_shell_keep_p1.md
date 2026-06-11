# Rank 242 / trend continuation × pullback re-entry × correlation-budget shell — fresh intake keep_P1

- Time: 2026-03-29 23:02 UTC
- Target: `trend continuation × pullback re-entry × correlation-budget shell`
- Source digest: `research/quant_digests/2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `Rank 242`

## 本轮只回答一件事
这条对象是否足够独立，值得从 digest 升成新的 queue-facing fresh intake。

## 结论
结论是 **值得**，并正式记为 `Rank 242 / trend continuation × pullback re-entry × correlation-budget shell`，当前层级为 `keep_P1`。

它之所以成立，不是因为“又来一个 4h trend repo”，而是因为主语已经收敛得足够清楚：

1. **基础 alpha 清楚**：主体是 `bull-regime breakout continuation`，不是泛泛 momentum。
2. **pullback 不是第二条 alpha**：它只是同一条趋势 alpha 的再进场层，所以对象边界不是“trend + unrelated pullback 拼装”，而是单一 alpha 的 state-machine 扩写。
3. **portfolio shell 有独立信息量**：`trend-only`、`trend+pullback`、`trend+pullback+correlation-budget shell` 三层可以直接做 honest A/B，对照边界明确；这里的相关性闸门、gross exposure、sleeve budget、drawdown scalar 不是装饰，而是 repo 已显式工程化的组合外壳。
4. **可以单轮证伪**：下一轮只要按 digest 已写清的 desk 版 spec，去做 `trend-only vs +pullback vs +shell` 的最小 clean-room 对照，就能知道这条对象到底是独立增量，还是旧 trend family 的一次过度包装。

## 为什么现在只到 keep_P1，不直接升 P2
还不能直接升 `P2`，因为目前证据主要来自 source audit 与 repo 内置结果，尚未完成我们自己的最小 clean-room admission。尤其要先回答两件事：

- `pullback sleeve` 到底是在提升 entry quality，还是只是把同一段趋势重复交易、提高换手；
- `correlation-budget shell` 到底是在减少组合拥挤尾损，还是只是在砍信号密度、把漂亮回测留给少数窗口。

所以这一步的诚实结论应是：**对象边界已足够独立，值得正式 intake；但还没有到 P2 admission。**

## 会改变系统认知的一句话
`Rank 242` 不是旧 trend/momentum family 的泛实现拼装，而是一条可独立复现、可直接做 `trend-only` vs `trend+pullback` vs `trend+pullback+correlation-budget shell` 三层 honest 对照的新 fresh intake，因此本轮记为 `keep_P1`。
