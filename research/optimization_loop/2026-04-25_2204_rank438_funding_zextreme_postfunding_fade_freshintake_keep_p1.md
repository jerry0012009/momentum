# Rank 438 / funding z-score extreme × post-funding fade fresh intake -> keep_P1

- 时间：2026-04-25 22:04 UTC
- 对象：`research/quant_digests/2026-04-25_2020_funding-zextreme-postfunding-fade.md`
- 执行动作：fresh intake first verdict
- 对应 policy 约束：只补 1 个最小 decisive blocker，直接判断 `keep_P1` 或 `background/P0`

## 本轮要回答的唯一问题
这条 `funding z-score extreme -> post-funding 1h~4h fade`，在当前公开证据下，是否已经足够保留一个不漂移的 survivor 主语；还是仍只是 funding crowding 叙事 / 稀疏样本演示，不值得继续占前排资源。

## 本轮最小 decisive blocker 检查
我只检查一件事：**公开 Binance 事件快检里的短窗 fade，在最便宜统一 friction 扣减后，是否仍保留一个清楚、可继续跟进的 event alpha 主语。**

直接读取本轮现成 probe summary：
- `|funding z| >= 1.5` pooled 事件数：`35`
- mean-reversion / plain / `1h`：`+22.24 bps/笔`，胜率 `77.4%`
- mean-reversion / plain / `4h`：`+14.41 bps/笔`，胜率 `67.4%`
- mean-reversion / plain / `8h`：`-10.83 bps/笔`

对最便宜统一 friction 做诚实扣减后：
- `1h net @ 2bps = +20.24 bps/笔`
- `4h net @ 2bps = +12.41 bps/笔`
- `8h net @ 2bps = -12.83 bps/笔`

## 结论
结论：**可以保留 survivor。**

原因不是因为 repo 已经给出完整 production 壳，而是因为最小主语已经够清楚，且没有被 cheapest friction 当场打穿：
1. 主语不是抽象的“funding 有信息”，而是明确的 `8h funding extreme event -> 后续 1h~4h 价格反向回吐`；
2. 公开数据快检里，这个主语在 pooled 层面已出现稳定正号，且 `1h/4h` 明显优于 `8h`，说明它更像短窗 fade 事件而不是长 hold carry；
3. 扣掉最便宜 `2bps` friction 后，`1h/4h` 仍为正，说明当前还不存在“唯一 decisive execution blocker = 一上成本就全灭”；
4. 这一步已经足够形成一个不漂移的 survivor follow-up 主语：下一轮不该再泛讲 funding crowding 故事，而该直接检查跨资产稳定性 / child execution 是否还保留厚度。

## 为什么这轮不是 background/P0
把它直接打回 `background/P0`，需要满足“除了 funding 拥挤叙事外，没有剩余可迁移、可继续验证的 event alpha 主语”。当前并非如此。

虽然样本只有 `35` 笔、且 symbol 细分上并不完全整齐，但 pooled `1h~4h` fade 在 cheapest friction 后仍为正，而且 `8h` 已经翻负，这恰恰把主语收束得更明确：

> **Rank 438 / `funding z-score extreme -> 1h~4h post-funding fade` 值得保留到 P1 survivor；下一步只需要做一次 cheap follow-up，确认它不是被少数币种偶然支撑，而是在最小 cross-asset / child-execution 口径下仍有可迁移厚度。**

## 当前未解决、但允许留到 survivor follow-up 的唯一 blocker
**唯一值得继续检查的 blocker**：

> 在不漂移主题的前提下，把 pooled fade 拆到最小跨资产/执行口径后，这个 `funding extreme -> short-window fade` 是否仍然有足够厚的、可迁移的 event edge；还是主要被少数 symbol 或单一退出时钟支撑。

这正好符合一次 cheap survivor follow-up 的范畴，因此本轮应 `keep_P1`，而不是直接升 `P2`。

## 本轮 verdict
- verdict: `keep_P1`
- 新 Rank：`438`
- 层级：fresh intake -> surviving candidate

## 一句话结果（写回 runtime）
`Rank 438 / funding z-score extreme × post-funding fade` fresh intake 首判为 `keep_P1`：公开 Binance `|funding z|>=1.5` 事件快检已把主语收束到 `8h funding extreme -> 1h~4h price fade`，且 pooled `1h/4h` 在最便宜 `2bps` friction 后仍保留正向厚度（约 `+20.24 / +12.41 bps`），足以保留一个不漂移 survivor；下一步只需做一次 cheap follow-up，确认这不是由少数 symbol / 单一退出时钟偶然支撑的伪厚度。

## 尾部执行状态（non-blocking）
- homepage 刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终被 `SIGKILL` 终止，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 438首判保留P1" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-25_2204_rank438_funding_zextreme_postfunding_fade_freshintake_keep_p1.md` 已成功发送。
