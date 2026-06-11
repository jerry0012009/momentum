# Rank 437 / pairwise vol-spread lagger continuation survivor follow-up -> background/P0

- 时间：2026-04-25 21:47 UTC
- 对象：`Rank 437 / pairwise vol-spread lagger continuation`
- 执行动作：survivor follow-up（唯一一次 cheap honesty / execution 检查）
- 对应 policy 约束：survivor 只允许 1 次 follow-up；本轮必须直接输出 `promote_P2` 或 `background/P0`

## 本轮要回答的唯一问题
在**公开 rolling pair generation** 下，`1m leader shock -> lagger 1~3 bar follow-through` 是否仍保留足以进入 `P2 admission` 的最小可迁移 alpha；还是一离开作者私有 pair schedule，event markout 与最便宜 friction 就会立刻塌掉。

## 本轮最小 honesty / execution 检查
我只做 state 指定的这一件事：

- 数据：Binance USDⓈ-M public `1m` klines
- universe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`
- lookback：近 `10d`
- rolling pair generation：用前 `5d` 的公开 `leader shock -> next-bar lagger signed return` 评分，选出前 `12` 个 `leader/lagger` 对
- event：`leader 1m return` 超过 `60` 分钟 rolling vol 的 `2.0x`
- 检查目标：`lagger` 的 `1/2/3` bar signed markout 与最便宜 friction ladder（`2/4/6 bps`）

产出 artifacts：
- `reports/artifacts/optimization_loop/rank437_survivor_followup_20260425/selected_pairs.csv`
- `reports/artifacts/optimization_loop/rank437_survivor_followup_20260425/pooled_horizon_summary.csv`
- `reports/artifacts/optimization_loop/rank437_survivor_followup_20260425/pair_horizon_summary.csv`
- `reports/artifacts/optimization_loop/rank437_survivor_followup_20260425/event_detail.csv`
- `reports/artifacts/optimization_loop/rank437_survivor_followup_20260425/meta.json`

## 结果
### pooled horizon summary
- `h=1`：平均 **`+0.615 bps`**，hit rate **`45.4%`**
- `h=2`：平均 **`-0.455 bps`**，hit rate **`41.5%`**
- `h=3`：平均 **`+0.074 bps`**，hit rate **`45.0%`**

### friction 后
- `h=1` 扣最便宜 `2 bps` 后只剩 **`-1.385 bps`**
- `h=2` 扣 `2 bps` 后 **`-2.455 bps`**
- `h=3` 扣 `2 bps` 后 **`-1.926 bps`**
- 扣 `4/6 bps` 更全部为负

## 这次 follow-up 改变了什么系统认知
它直接回答了 survivor 阶段唯一 blocker：

> **公开 rolling pair generation 下，`leader shock -> lagger 1~3 bar follow-through` 并没有留下足够厚、足够单调、也不足以穿过最便宜执行成本的可迁移信号。**

因此此前能保留 `P1 survivor` 的理由——“也许公开版还能留下一个最小 raw alpha 壳”——本轮已被否定。

## 为什么不是 promote_P2
按 policy，升 `P2` 需要这次 follow-up 能把主结论收束成“alpha 还成立，且不存在单一 decisive honesty / execution blocker，值得进入 P2 admission”。

当前恰好相反：
1. `1/2/3` bar markout **不单调**；
2. 最好的 `1-bar` gross 也只有 **`+0.615 bps`**，远低于可交易厚度；
3. 一扣最便宜 `2 bps` friction 就整体转负；
4. 这说明对象一旦离开作者私有 pair schedule，并没有保住 queue-facing 的公开可迁移 alpha。

## 本轮 verdict
- verdict: `background/P0`
- 层级：`Surviving candidate -> Background pool`
- survivor budget：用尽，不再保留前排

## 一句话结果（写回 runtime）
`Rank 437 / pairwise vol-spread lagger continuation` survivor follow-up 已诚实收口到 `background/P0`：公开 rolling pair generation 下的 `1m leader shock -> lagger 1~3 bar follow-through` pooled markout 只有 `h1 +0.62bps / h2 -0.45bps / h3 +0.07bps`，不单调且扣最便宜 `2bps` friction 后全为负，说明离开作者私有 pair schedule 后不存在足够可迁移的 execution-thick alpha，不升 `P2`。

## 尾部执行状态（non-blocking）
- homepage 刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终收到 `SIGKILL` 失败；按 policy 记为**非阻断尾部失败**，不回滚本轮 verdict / state / log。
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 437收口回背景" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-25_2147_rank437_survivor_followup_background_p0.md` 已成功发送。
