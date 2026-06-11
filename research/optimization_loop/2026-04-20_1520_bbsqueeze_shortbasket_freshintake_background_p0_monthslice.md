# Rankless fresh intake — bbsqueeze release short basket → background/P0

- Time: 2026-04-20 15:20 UTC
- Target: `research/quant_digests/2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`
- Action: fresh intake first verdict
- Scope: 只补当前 cycle 小点要求的最小 blocker——检查 `15m` `ETH/XRP/LINK` short basket / top1 router 在统一 `8bps`、资产贡献、腿数压缩与月份切片后，是否仍保留可承接的 after-cost downside drift。

## 结论
`BB squeeze release breakdown × alt short basket` 不保留 survivor，fresh intake first verdict 直接收口 `background/P0`。

## 改变系统认知的一句话
虽然 `15m` `ETH/XRP/LINK` short basket 与 top1 router 在全样本上仍有 `net8` 正值，但该 pocket 没能通过月份切片的最小稳健性要求：最近 `2026-04` 已明显转负，因此它更像阶段性 short-regime pocket，而不是当前值得保留到 `P1` 的可承接 front object。

## 最小 blocker 检查
数据源：`reports/artifacts/quant_digests/2026-04-19_bbsqueeze_release_events.csv`

### 1) 原 digest 中最强 pocket 复核
- `15m` `ETH/XRP/LINK` short basket：`n=110`，`gross≈+21.26bps/trade`，`net8≈+13.26bps`
- `15m` 同刻 `top1 short router`：`n=100`，`gross≈+26.54bps/trade`，`net8≈+18.54bps`

### 2) 资产贡献不是单币硬撑
- `ETHUSDT short`: `n=37`, `net8≈+15.11bps`
- `LINKUSDT short`: `n=38`, `net8≈+13.25bps`
- `XRPUSDT short`: `n=35`, `net8≈+11.31bps`

=> 这一步说明它不是“只靠一枚币 lucky hit”的假阳性。

### 3) 但月份切片没有通过最小稳健性门槛
`ETH/XRP/LINK short basket` 月份切片：
- `2025-12`: `n=11`, `net8≈-6.49bps`
- `2026-01`: `n=29`, `net8≈+13.92bps`
- `2026-02`: `n=29`, `net8≈+43.21bps`
- `2026-03`: `n=24`, `net8≈+21.09bps`
- `2026-04`: `n=17`, `net8≈-37.24bps`

`top1 short router` 月份切片：
- `2025-12`: `n=10`, `net8≈+1.65bps`
- `2026-01`: `n=27`, `net8≈+18.41bps`
- `2026-02`: `n=27`, `net8≈+60.40bps`
- `2026-03`: `n=21`, `net8≈+7.77bps`
- `2026-04`: `n=15`, `net8≈-30.25bps`

=> 最近月已经反向，且不是轻微掉到成本线附近，而是明显转负；这不满足当前 cycle 对“月份切片后仍保留可复制 after-cost drift”的要求。

### 4) 腿数压缩也没解决 recent decay
进一步压成 `ETH/XRP` 两腿后：
- short basket：`n=72`, `net8≈+13.26bps`
- top1 router：`n=71`, `net8≈+11.89bps`
- 但 `2026-04` 仍约 `-28.80bps`

=> 不是“腿太多导致稀释”的问题，核心问题仍是 recent regime decay。

## Verdict
按本轮 success criterion，只有当该 short-window reversal / breakdown pocket 在统一成本、资产贡献、月份切片与执行 realism 下仍保留可承接的正 `net`，才应 `keep_P1`。

本次最小 blocker 检查已经说明：
- 资产贡献层面：合格；
- 月份切片层面：不合格，最近 `2026-04` 已显著转负；
- 因此不保留 `survivor`，直接收口 `background/P0`。

## Runtime writeback
- `cycle_plan` item 1 → `done`
- `Fresh intake slot` latest result → `background/P0`
- `Background pool` 补记本条收口

## Tail step status
- homepage publish: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮触发 `SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- email notify: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] BB squeeze 短篮子收口 P0" --body-file <本文件>` 已成功发送。
