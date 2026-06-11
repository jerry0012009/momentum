# Rank 438 / funding z-score extreme × post-funding fade survivor follow-up -> background/P0

- 时间：2026-04-25 23:28 UTC
- 对象：`Rank 438 / funding z-score extreme × post-funding fade`
- 执行动作：survivor 唯一 follow-up
- 对应 policy 约束：这一步必须只围绕唯一 decisive blocker 做最小诚实检查，并直接输出 `promote_P2` 或 `background/P0`

## 本轮要回答的唯一问题
`8h funding extreme -> 1h~4h fade` 这条主语，在最小 cross-asset split 与 child-execution / exit-clock 口径下，是否仍保留足够可迁移厚度，值得升到 `P2 admission`；还是主要由少数 symbol / 单一退出时钟支撑，应该用完 survivor 预算并收口到 `background/P0`。

## 本轮只做的最小检查
我没有扩成新的 funding crowding 研究，只复核现成公开 probe artifacts：
- `reports/artifacts/quant_digests/2026-04-25_funding_zextreme_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_funding_zextreme_probe_detail.csv`

已知 pooled 事件层结果仍成立：
- plain mean-reversion / `1h`：`35` 笔，`+22.24 bps/笔`
- plain mean-reversion / `4h`：`35` 笔，`+14.41 bps/笔`
- plain mean-reversion / `8h`：`-10.83 bps/笔`

所以这次 survivor follow-up 不再重复“有没有 pooled fade”这个维度，而是直接看**拆到 symbol 后，最小 breadth 是否还诚实**。

## cross-asset / child-execution 最小拆分结果
按 detail artifact 的 symbol-level plain mean-reversion 汇总，`1h` / `4h` 的正号主要集中在少数币种：

### 1h
- `BNBUSDT`：约 `+32.10 bps`
- `ETHUSDT`：约 `+43.32 bps`
- `XRPUSDT`：约 `+25.75 bps`
- `DOGEUSDT`：约 `+49.15 bps`，但仅 `1` 笔
- `SOLUSDT`：约 `+0.46 bps`，扣最便宜 `2bps` friction 后近乎转负
- `BTCUSDT`：约 `-17.35 bps`

### 4h
- `BNBUSDT`：约 `+43.80 bps`
- `ETHUSDT`：约 `+50.09 bps`
- `XRPUSDT`：约 `+42.99 bps`
- `DOGEUSDT`：约 `+4.27 bps`，但仍仅 `1` 笔
- `SOLUSDT`：约 `-12.51 bps`
- `BTCUSDT`：约 `-42.17 bps`

### 读法
- child exit-clock 上，`1h~4h fade` 这个方向本身没漂移，`8h` 继续 hold 反而恶化，这一点与 fresh-intake 结论一致；
- 但 **cross-asset breadth 不够诚实**：`BTC` 在 `1h` 与 `4h` 都明显反号，`SOL` 也没有保留足够净厚度；
- 当前存活的“正号”主要由 `ETH/BNB/XRP` 支撑，`DOGE` 只有单笔，不能当 admission 证据。

## 结论
结论：**本轮不能升 `P2`，应收口到 `background/P0`。**

原因不是 pooled edge 消失，也不是单纯成本把它打穿；真正的 decisive blocker 是：

> 当 survivor follow-up 把它拆到最小 cross-asset 口径后，这条 `funding extreme -> short-window fade` 还没有展示出足够可迁移的 breadth，当前更像 `ETH/BNB/XRP` 主导的局部 crowding 现象，而不是可以直接进入 `P2 admission` 的通用 raw alpha。

按 policy，这一步的出口必须是 `promote_P2` 或 `background/P0`。由于 blocker 已经明确，而且不是一句“再补一点稳定性”就能收掉，因此不能继续保留 survivor，也不能开放式拖进 `P2`。

## 为什么不是 promote_P2
要升 `P2`，至少要能说：主语成立，且当前不存在单一 decisive honesty / execution blocker，值得进入五维 admission。现在并不满足：
- `execution` 不是主问题，`1h/4h` pooled gross 仍够厚；
- **真正的问题是 breadth**：`BTC` 反号且幅度大，`SOL` 近乎无厚度，说明这条线尚未证明自己能跨最核心 majors 迁移；
- 在这种情况下直接升 `P2`，等于把 survivor 唯一 follow-up 本该解决的问题继续往后拖。

## 本轮 verdict
- verdict: `background/P0`
- survivor budget：已用完
- 层级：`Surviving candidate -> Background pool`

## 一句话结果（写回 runtime）
`Rank 438 / funding z-score extreme × post-funding fade` survivor 唯一 follow-up 收口为 `background/P0`：虽然 pooled `1h~4h` post-funding fade 仍为正，但最小 cross-asset 拆分显示厚度主要集中在 `ETH/BNB/XRP`，`BTC` 在 `1h/4h` 都明显反号、`SOL` 近乎无净厚度，因此它尚未证明自己具备足够可迁移 breadth，不诚实升 `P2`。

## 尾部执行状态（non-blocking）
- homepage 刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 已独立执行，但在本轮等待窗口内未正常返回，随后中止；按 policy 记为非阻断尾部失败，不回滚本轮 verdict / state / log。
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 438 survivor收口回背景" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-25_2328_rank438_survivor_followup_background_p0.md` 已成功发送。
