# `rolling-OLS residual z-score fade × cost-aware sizing` — fresh intake first verdict `background/P0`

- 时间：2026-04-23 00:35 UTC
- target: `research/quant_digests/2026-04-22_0204_rollols-costaware-pairfade-shell.md`
- action: conditional fresh intake：对 `rolling-OLS residual z-score fade × cost-aware sizing` 做 first verdict，只补 1 个最小 decisive blocker（它是否相对已 live `Rank 424 / 431` 留下独立新增的 pairs shell 价值，而不是又一个 pair-MR deployment repeat）
- success_criterion: 必须直接输出 `keep_P1` 或 `background/P0`；只有当它在 distinctness、最小双腿成本与 sparse-timeout realism 检查后仍保留独立新增价值，才 `keep_P1`

## 本轮最小 blocker
只回答一件事：这条线有没有证明自己相对已 live 的 pairs family（尤其 `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade` 与 `Rank 431 / cointegration maker-first + hard time-stop pairs`）留下新的、值得单独排队的 after-cost shell 价值。

## 现成证据回读
目标 digest 自己已经把最关键的 portability 结果写得很清楚：

- Binance USDⓈ-M `AVAXUSDT / ICPUSDT` 最近约 `120d`
- `15m`：仅 `5` 笔，`avg gross ≈ +190.50bps/笔`，但 `timeout rate = 100%`
- `5m`：`43` 笔，`avg gross ≈ +10.57bps/笔`，`median gross ≈ -3.61bps/笔`，`timeout rate ≈ 97.7%`

这说明：
1. `15m` 的所谓厚 pocket 几乎完全建立在极稀疏样本上；
2. `5m` 虽有更多交易，但 gross 厚度本身就已经接近最小双腿成本线；
3. 两个周期都没有表现出“自然 center-reclaim 主导”的干净 spread 回归，绝大多数交易仍靠 hard timeout 收口。

## 与已 live pairs family 的 distinctness 对比
### 相对 Rank 424
`Rank 424` 已经把 pairs family 收口成：
- `cointegration-first pair admission`
- `strongest residual z-score spread fade`
- `SOL/LTC core + LINK/AVAX watch`
- 至少一个 core pair 在多月份/前后半样本下保住 after-cost 边际

也就是说，`Rank 424` 已经覆盖了“pair admission + residual spread fade”的核心主语。当前这条 `rolling-OLS residual z-score fade` 并没有拿出新的 durable pair set，也没有展示比 `Rank 424` 更厚、更稳、或更可迁移的 after-cost pocket；它新增的主要是 `cost-aware sizing / split-local state machine / cost rerun hygiene` 这些研究部署层组件。

### 相对 Rank 431
`Rank 431` 已经把同一家族进一步收口成：
- `rolling pair admission + maker-first + hard time-stop`
- recent public scan 至少两对同向 after-cost pocket
- 后续 admission 还继续围绕 `cross-pair durability` 做过收口

当前对象在 execution realism 上并没有超出 `Rank 431`：
- 它没有证明 maker-first / sparse deployment 后仍能产生新宿主；
- 反而现成 probe 已经显示策略高度依赖 timeout，说明它更像 `Rank 431` 这类 hard-time-stop pair shell 的研究卫生/size 组件，而不是新的 queue-facing alpha 主语。

## 为什么不能给 keep_P1
如果要给 `keep_P1`，至少要满足下面之一：
1. 留下不同于 `Rank 424 / 431` 的 durable pair pocket；
2. 证明 `cost-aware sizing` 不只是“缩小亏损/稀释噪音”，而是能把薄 gross 可靠抬成可迁移的 after-cost shell；
3. 在 sparse-timeout realism 下，证明中心回归质量本身足够好，而不是几乎全靠超长 timeout 收尾。

当前都没有做到：
- `5m` 的 gross 只有 `≈ +10.57bps/笔`，对双腿成本明显不保险；
- `15m` 只有 `5` 笔，不能支撑一个新的 front object；
- 高 timeout-rate 说明它在短周期迁移后并没有形成新的 clean mean-reversion pocket；
- 最终新增价值主要停留在 `pairs family 的 deployment / hygiene 提示`，而不是独立 alpha。

## 结论
`rolling-OLS residual z-score fade × cost-aware sizing` 的 fresh intake first verdict 已诚实收口 `background/P0`：当前 Binance perp portability 里，`15m` 只剩 `5` 笔且 `timeout=100%` 的稀疏 pocket，`5m` 虽有 `43` 笔但 `gross≈+10.57bps/笔`、`median gross<0`、`timeout≈97.7%`，没有证明自然回中枢质量足以覆盖最小双腿成本；同时它相对已 live 的 `Rank 424 / 431` 没有拿出新的 durable pair set 或独立 after-cost shell，新增价值主要退化为 `cost-aware sizing / split-local state hygiene / cost-rerun` 的 pairs deployment 组件提示，因此不进入 survivor，直接转入 `background/P0`。

## runtime follow-up
- 当前 conditional fresh intake 已诚实收口 `background/P0`
- Fresh intake front-slot 自然切到下一条 pending：`research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`

## tail-step execution note
- homepage publish（`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`）在本轮执行中超时并被 SIGKILL；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知已独立执行成功：`[momentum-bot3-auto] pairs 壳重复收口 P0`。
