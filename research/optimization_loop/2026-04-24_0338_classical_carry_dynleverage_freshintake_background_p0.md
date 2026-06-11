# classical carry × dynamic leverage shell — fresh intake first verdict（background/P0）

- 时间：2026-04-24 03:38 UTC
- 对象：`research/quant_digests/2026-04-24_0140_classical-carry-dynleverage-shell.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只回答一个最小 decisive blocker
这条 `classical carry × dynamic leverage shell` 是否留下了一个**相对现有 funding/carry 家族仍可独立排队的 after-cost carry pocket**，还是它的新增价值只剩 leverage / product-shell / risk-budget 提示？

## 最小证据
1. digest 自身的 base alpha 仍是最朴素的 **single-venue positive funding carry（long spot + short perp）**；dynamic leverage 只是 sizing / drawdown 管理层，不是新的 raw alpha 主语。
2. 外部 README 的关键证据仍停留在课程项目级 summary：`BTC/ETH funding positive over 85% of time`、`staking-enhanced carry +3.9%`、`dynamic leverage reduces drawdowns`；它没有给出一个可直接复核的、跨多币 / 多 funding windows 的 recent **after-cost net-carry ledger**，也没有证明 dynamic leverage 在当前 Binance recent regime 下能把薄 carry 重新抬成独立 alpha。
3. 现有 runtime 已有更接近实盘的 funding/carry 宿主：已 live `Rank 389 / cross-venue net-carry ranking alpha`，且近轮已经把多个 carry/scanner/router 壳诚实收口为 `background/P0`。这份材料相对它没有拿出新的 distinct pocket；新增信息主要退化为：
   - `dynamic leverage as risk-budget knob`
   - `carry shell complete with entry/exit/risk framing`
   - `staking / Pendle` 作为收益增强或产品化旁支
4. 按本轮 success criterion，需要看到“至少一个非单 funding-window、非单 regime lucky-run 的 after-cost carry pocket，且相对现有 funding/carry 家族仍有独立新增价值”；当前证据没有闭合这一点。

## 为什么直接收口 background/P0
- **distinctness 不成立**：alpha 主语没有脱离 desk 已 live 的 `Rank 389` / 既有 funding-carry family。
- **after-cost 证据不够**：repo/README 提供的是长期课程项目结论，不是当前 regime 下可复核的 recent net ledger。
- **dynamic leverage 不是新的 raw alpha**：它更像 carry 宿主上的 risk-sizing 组件提示，而不是值得单独占用 front slot 的对象。

## 本轮结果句
`classical carry × dynamic leverage shell` 的 fresh intake first verdict 已诚实收口 `background/P0`：它没有证明相对已 live `Rank 389 / cross-venue net-carry ranking alpha` 留下新的独立 after-cost carry pocket，新增价值主要退化为 `dynamic leverage / risk-budget / product-shell` 提示，而不是新的前排 raw alpha。

## 尾部执行状态（non-blocking）
- 首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 在异步会话中被 `SIGKILL` 终止（非阻断尾部失败，不回滚本轮 verdict/state/log）。
- 邮件发送命令已成功执行。
