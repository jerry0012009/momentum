# bot3 自动执行日志：Hyperliquid market-quality shared gate overlay fresh intake

- 时间：2026-04-21 22:12 UTC
- 执行小点：cycle_plan #1
- 对象：`research/quant_digests/2026-04-21_0946_hl-marketquality-shared-gate-overlay.md`
- 动作：fresh intake first verdict；只补一个最小 decisive blocker：把 `premium_tail / amihud_z / roll_spread` shared market-quality gate 接到具体 raw alpha（优先 premium-dislocation fade）上，判断它是否在同一成本口径下真实改善 net expectancy / worst trades。

## 读取证据

- digest 明确承认该对象没有独立 base alpha，只是 `premium-dislocation fade`、`funding/basis carry admission`、`breakout child execution` 的共享准入/size-down overlay。
- 现有 public-data 快检只给出 live snapshot / liquid universe 分层：`n_liquid=54`，abs premium 中位数约 `5.65bps`，P95 约 `19.07bps`；这证明 market-quality 有横截面差异，但不是同窗、事件级的 gate backtest。
- 可用的 Hyperliquid basis-dislocation 90d 事件表显示 raw `asset_p90` premium fade 本身已经很弱：全 8 币 `1/2/4/8 bars` mean 分别约 `+0.28/-13.42/-46.78/-126.13bps`；top1 也为 `-3.73/-16.88/-48.41/-121.41bps`。少数单币如 `HYPE` 的长一点 horizon 为正，但组合与 top1 口径没有形成可交易母体。

## 最小 decisive blocker

本轮没有找到能把 `premium_tail / amihud_z / roll_spread` gate 与 raw alpha 放在同一历史窗口、同一交易事件、同一成本口径下复算的 artifact。现有 market-quality snapshot 只能说明“哪些币此刻 premium/volume/liquidity 不同”，不能证明：

1. gate 后 `premium-dislocation fade` 的 post-cost expectancy 明显改善；
2. worst trades / tail loss 的改善不是事后挑样本；
3. trade count 仍足以交易；
4. overlay 不是泛泛 execution realism 备注。

在母体 raw alpha 还没有稳定 after-cost pocket、且 overlay 证据又缺少同窗事件级 join 的情况下，按 success criterion 不能给 `keep_P1`。

## Verdict

`Hyperliquid market-quality / shared gate overlay` fresh intake first verdict：`background/P0`。

一句话结论：它是有价值的共享执行/准入研究提示，但本轮未能证明 `premium_tail / amihud_z / roll_spread` gate 能在具体 raw alpha 的同窗、同成本事件回放中真实改善 net expectancy / tail loss，因此不作为新的前排 survivor 保留。

## Runtime 更新

- Fresh intake slot：本对象收口为 `background/P0`；按 conditional cycle_plan 切到下一条 fresh intake `research/quant_digests/2026-04-21_2120_pca-eigenportfolio-residual-fade-alpha.md`。
- Surviving candidate / Active P2 / Paper launch queue：无变化。
- cycle_plan #1：`done`。

## Tail steps

- homepage refresh：尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，该尾部步骤在本轮超时/被 SIGKILL，按规则记为非阻断尾部失败，不回滚 verdict / state / log。
- email：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] HL市场质量门控首判收口" --body-file <log>` 已成功发送到配置收件人。
