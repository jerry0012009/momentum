# Rank 173 / repo-statarb-live-stack-transfer-check — fresh intake 首判

- 时间：2026-03-26 00:44 UTC
- 执行角色：bot3
- 依据：`docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan` 中首个合法 pending 项 —— 对 `research/quant_digests/2026-03-26_0020_repo-statarb-live-stack-transfer-check.md` 做 fresh intake 最小首判

## 为什么本轮不是执行前一条 pending 的 Active P2 admission
`cycle_plan` 第 2 项显式带条件：只有当 `Rank 172 / MBSA Markowitz basket raw alpha` 经 survivor follow-up 升入 `P2` 时才成立。但 runtime truth 已明确 `Rank 172` 的 survivor 唯一 follow-up 已诚实收口为**不升 `P2`**，且 `Active P2 slot = none`，因此该项本轮不再是合法主动作；按 policy 直接回退到下一条合法 fresh intake。

## 读后结论
结论给 `keep_P1`，并分配正式 `Rank 173`。

这条线当前值得保留的，不是 README 里那句未经独立核验的 live headline，而是 repo 明确写出来的完整策略骨架：**cointegration spread + beta/liquidity-cap sizing + chunked pair execution + daily throttle / guard**。也就是说，真正可进入前排继续验证的是一条“pairs/stat-arb raw alpha 如何被诚实补成可部署执行栈”的候选，而不是“这套东西已经被证明能直接迁移成 desk 可上线 alpha”。

## 为什么不是直接 park
1. digest 已把 base alpha 说清楚：核心仍是 `spread = log(A) - β log(B)` 的 z-score 均值回归，属于明确的 pairs / stat-arb raw alpha，而不是只有工程包装没有信号内核的 execution 工具箱。
2. repo 的高价值部分不是抽象地“会做 cointegration”，而是把 desk 真正在意的几层补齐了：`beta_norm + 低流动性腿 cap`、双腿分块开平、腿失败后的 unwind、日内盈利 throttle 与亏损停机；这些都会改变真实可交易性判断，值得保留一次 survivor follow-up。
3. digest 自带的 Binance `15m` 最小 transfer check 虽然为负，但恰恰把边界讲诚实了：直接照抄成 `15m bar-close taker` pairs alpha 不成立，可保留的是完整策略工程骨架，而不是 live headline 本身。对这种“骨架有料、直迁不成立”的对象，按 policy 更适合先留在 `P1`，而不是直接扔回 background pool。

## 为什么还不能直接进 P2
当前证据还不足以证明这套完整骨架在 desk 口径下保留了可复制净边：

1. **最小 transfer check 明确不支持直接部署。** majors-only、repo-like `15m` proxy 下只筛出 `ETH-SOL` 一对，且测试段毛收益约 `-0.37%`，加 repo-like 成本后约 `-2.30%`，说明短周期直接迁移并不成立。
2. **README live 成绩仍是作者自报。** 目前没有独立核验成交明细、净值链路与成本口径，不能把它当成 admission 级证据。
3. **还没回答“哪一层真的贡献 deployable edge”。** 目前知道完整骨架写得比普通 repo 更诚实，但还没分离出：可复用净边到底来自 cointegration spread 本体、来自 liquidity-cap / throttle 的执行治理，还是只是在单次 proxy 上看起来像完整系统。

因此，它够得上 `keep_P1`，但还不够诚实地直接升 `P2`。

## 本轮 verdict
**Rank 173 / repo-statarb-live-stack-transfer-check：保持 `P1`。当前真正值得保留的是“cointegration spread + liquidity cap + daily throttle”的完整策略骨架，而不是把 README live headline 直接当成已迁移成功的 desk alpha。**
