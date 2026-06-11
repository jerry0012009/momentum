# bot3 optimization loop — 2026-04-23 12:01 UTC — polymarket funding-confirmed skewfade → background/P0

## 本轮执行小点
- target: `research/quant_digests/2026-04-23_0942_polymarket-funding-confirmed-skewfade-alpha.md`
- action: fresh intake：对 `retail skew × funding-confirmed fade` 做 first verdict，只补 1 个最小 decisive blocker（它是否已证明存在可独立排队的 after-cost skew-fade pocket，而不是只剩 prediction-market 执行壳 / crowding-confirmation 提示）

## 最小 blocker 检查
本轮只补 1 个最小 decisive blocker：**公开材料是否已经给出可复核的 after-cost pocket 证据，而不只是规则壳。**

我复核了 repo 的公开 README 与 `src/strategies/basis_impl.rs`：
- README 明确把项目定性为：`This project is a learning exercise, not an edge.`
- Basis/funding 策略确实把 `entry/exit/sizing/fee gate/expiry guard` 全写清楚，属于可复刻的执行壳。
- 但公开材料只给了规则说明、参数与单元测试；**没有给出事件级 replay、trade ledger、回测汇总、after-cost hit rate、跨市场/跨时间窗稳定性** 等能证明独立 alpha pocket 的 reader-facing 证据。
- 代码中的测试也只是逻辑单测（例如 skew/funding/velocity/oracle gate 是否触发），不是 PnL 或 after-cost 有效性验证。
- README 自身还强调 Polymarket 里是 `well-funded, low-latency bots`，并把 basis/funding 描述成 thesis/strategy explanation，而不是已验证 edge。

## 结论
- 这条线当前**诚实可保留的价值**是：`crowd skew -> external-market veto/confirm -> skew-fade` 的 research shell / execution template。
- 但它**没有公开证明**自己已经形成至少一个可独立排队、可复核、after-cost 成立的 skew-fade pocket。
- 因此本轮不能给 `keep_P1`；应直接收口 `background/P0`。

## 会改变系统认知的一句话结果
`retail skew × funding-confirmed fade` 已完成 fresh intake first verdict 并收口 `background/P0`：repo 公开材料只证明了 `Polymarket crowd skew + Binance funding/velocity/strike veto` 的可复刻执行壳，README 还明确把项目定性为 `learning exercise, not an edge`，同时没有给出可公开复核的事件级 after-cost 业绩或独立 skew-fade pocket 证据，因此当前不应占用 survivor。

## 参考
- `https://raw.githubusercontent.com/mbordash/RustPolyBot/main/README.md`
- `https://raw.githubusercontent.com/mbordash/RustPolyBot/main/src/strategies/basis_impl.rs`

## 尾部执行状态（非阻断）
- 邮件发送：成功（`send_text_email.py` 返回 code 0）。
- 首页刷新：`publish_homepage_index.sh` 异步进程最终 `SIGKILL` 退出，按 policy 记为非阻断尾部失败；不回滚本轮 `verdict/state/log`。
