# bot3 optimization loop — BTC vs alt basket relative-strength rotation fresh intake -> background/P0

- 时间：2026-04-23 10:00 UTC
- target: `research/quant_digests/2026-04-23_0725_btc-dominance-alt-rotation-alpha.md`
- action: fresh intake first verdict（`BTC vs alt basket 相对强弱切换 / dominance rotation`）
- success criterion: 必须直接输出 `keep_P1` 或 `background/P0`；只有当至少一个非单 alt、非单窗 lucky-run 的 BTC-vs-alt rotation after-cost pocket 成立，才 `keep_P1`

## 本轮只补的最小 decisive blocker
这条线是否已经证明存在**独立于现有 xs / rotation / router family 的 after-cost relative-strength alpha**，而不是只剩一个可复用的 `BTC-vs-alt regime router` 叙事。

## 使用证据
1. digest：`research/quant_digests/2026-04-23_0725_btc-dominance-alt-rotation-alpha.md`
2. 既有 portability artifact：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_meta.json`
3. 既有 selected-config 明细：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_detail.csv`
4. 对照 family：已 live `Rank 389 / cross-venue net-carry ranking alpha`、以及近轮多个已收口的 router / rotation 类 fresh-intake verdict

## 关键观察
### 1) 当前最好结果仍是 gross / near-continuous exposure，不是已过成本关的新 pocket
artifact 给出的最好连续配置为：
- `top_alts=4, rebars=4`
- `mean_bps ≈ +0.1136 bps/bar`
- `Sharpe ≈ 2.16`
- `cumret ≈ +22.37%`
- `avg_turnover_x ≈ 0.178/bar`
- `active_ratio ≈ 99.8%`

这说明它更多像一条**几乎持续在场、频繁换腿的 gross relative-strength shell**。但 fresh intake 的门槛不是“gross 看起来可追”，而是要看到现实费滑下仍有独立 after-cost pocket。当前 digest 与 artifact 都没有给出统一 `8/12bps` 级别、或同等诚实成本下仍为正的证据。

### 2) selected-config 细节只证明“方向切换骨架存在”，没有证明净边可存活
`selected_config_detail.csv` 里主要记录的是：
- `btc_weight` 在 `-0.5 / 0 / +0.5` 间切换；
- `trend_direction` 决定站到 BTC 侧还是 alt 侧；
- 仅附了 `0/1/2bp` 的轻成本列。

也就是说，现有最细颗粒证据仍停留在：
- `BTC-ret - alt-basket-ret` 这条相对强弱信号确实可形成 router；
- 但现实 desk 更关心的 `多腿 short-cycle perp` 成本、child execution、持续换仓磨损，并没有被这份证据真正回答。

### 3) 新增价值主要退化为 router / regime layer，而不是独立 front raw alpha
这条对象最有价值的地方，是：
- 先判 `BTC 主导` 还是 `alt 主导`；
- 再把 strongest / weakest basket 路由到对应一侧。

但这更像一种：
- `cross-asset relative-strength state -> basket routing` 骨架，
- 可以给现有 xs / rotation / basket-family 当 regime / router 提示层，
- 而不是已经形成一个值得单独占用 survivor 槽位的新 front object。

### 4) 按当前 success criterion，不足以给 keep_P1
本轮要求的是：
- 至少看到**非单 alt、非单窗**支撑的 after-cost pocket；
- 且它要足够独立，不只是“BTC dominance 叙事能帮助别的策略做路由”。

现有证据没有完成这一步：
- 核心最好结果仍是 gross；
- 换手和 active ratio 显示其对现实费滑高度脆弱；
- 也没有证明它相对现有 rotation/router family 留下新的、可独立排队的 after-cost edge。

## 结论
`BTC vs alt basket 相对强弱切换 / dominance rotation` 的 fresh intake first verdict 应直接收口 `background/P0`：现有 portability probe 只证明 `BTC-ret - alt-basket-ret` 可以作为 cross-asset relative-strength regime/router 骨架使用，但最佳结果仍建立在近乎连续暴露与高换腿的 gross 口径上，尚未证明在现实 short-cycle perp 成本下存在非单 alt、非单窗口支撑的独立 after-cost alpha；因此它当前更适合作为 `BTC-vs-alt parent router / regime layer` 提示，而不是新的 survivor/front raw alpha。

## 尾部执行记录（non-blocking）
- publish：首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 在本轮无输出长时间挂起，已按非阻断尾部异常处理并终止，不回滚本轮 verdict/state/log。
- email：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] BTC主导轮动首判收口P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-23_1000_btc_dominance_alt_rotation_freshintake_background_p0.md` 已成功发送。
