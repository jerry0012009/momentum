# bot3 optimization loop — low-volume upmove fade stale duplicate blocked

- 时间：2026-04-25 19:57 UTC
- 对象：`research/quant_digests/2026-04-24_2250_lowvolume-upmove-fade-alpha.md`
- 执行槽位：`cycle_plan` 第 3 项（fresh intake）
- 本轮动作：核验这条 pending fresh intake 是否仍是合法首判对象，还是已被同日更早轮次完成 first verdict

## 结论
`低成交量上冲 × 次段回吐` 当前 pending 属于 stale duplicate：同一 digest 已在 `2026-04-25 09:30 UTC` 完成 first verdict 并诚实收口 `background/P0`，因此本轮不得重复把它当 fresh intake 重做首判，只能将该小点标记为 `blocked`。

## 本轮依据
- 已存在完成记录：`research/optimization_loop/2026-04-25_0930_lowvolume_upmove_fade_first_verdict_background_p0.md`
- 该记录已经给出明确系统结论：统一 `8bps` 成本下 pooled `15m hold1/hold3` 为 `-4.06 / -4.39 bps`，`5m` 也未救回成本，仅剩 `DOGE hold1` 与 `BTC hold3` 的稀疏单币 pocket，不足以支撑 `keep_P1`
- 根据 policy，bot3 只执行当前最前 pending 的合法小点；若该小点已被前序结果明确完成或前提已失效，应写成 `blocked`，不得自行重排，也不得重复消费同一 fresh intake 预算

## 对 runtime 的影响
- 不分配新 Rank
- 不改动前排槽位层级
- 仅将 `cycle_plan` 第 3 项由 `pending` 改为 `blocked`

## 一句话写回 state
`低成交量上冲 × 次段回吐` 当前 pending 属于 stale duplicate：同一 digest 已在 `2026-04-25 09:30 UTC` 完成 first verdict 并收口 `background/P0`，本轮不得重复把它当 fresh intake 重做首判。

## 尾部执行状态（非阻断）
- homepage 刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终 `SIGKILL` 失败；按 policy 记为非阻断尾部失败，不影响本轮 `state/log/verdict` 生效。
- 中文邮件摘要已成功发送（subject: `[momentum-bot3-auto] 低量上冲条目重复阻断`）。
