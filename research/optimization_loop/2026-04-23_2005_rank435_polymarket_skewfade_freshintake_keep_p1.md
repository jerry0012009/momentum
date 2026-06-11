# bot3 optimization loop — Rank 435 Polymarket funding-confirmed skew fade fresh intake 保留 P1

- 时间：2026-04-23 20:05 UTC
- 执行对象：`research/quant_digests/2026-04-23_0942_polymarket-funding-confirmed-skewfade-alpha.md`
- 执行动作：fresh intake first verdict
- 对应 cycle_plan 槽位：2

## 本轮读取到的关键 runtime
- `Paper launch queue`: `none`（当前无需 P3 wiring）
- `Active P2 slot`: `none`
- `Surviving candidate slot`: `none`
- 因此前排合法主动作就是 cycle_plan 里排在最前的 pending fresh intake：`Polymarket funding-confirmed skew fade`

## 最小 decisive blocker
判断它是否只是在讲“prediction-market sentiment / funding confirmation”的概念提示，还是已经留下一个**可独立排队、可直接复刻、带 after-cost 约束的 event-linked skew-fade pocket**。

## 本轮最小 honesty / execution 检查
直接复核 repo 的可执行规则，而不是只接受 digest 摘要：
- `basis_impl.rs` 明确把 `entry / exit / sizing / fee gate / expiry guard` 全部写成可运行条件；
- 入场不是单独看 funding，而是 `skew > threshold` 为主信号，`funding` 只做 confirm，且有 `velocity flat`、`oracle near strike`、`max taker fee`、`max entry price` 多重现实约束；
- 代码支持 `BTC / ETH / SOL` 三个 crypto filter，并默认面向 hourly event markets，而不是单事件一次性 lucky-run；
- README 明写 basis 策略是 taker、对 fee 敏感、且 funding 只是 confirm，不是独立 alpha，这使对象更像一条可复刻的 event-linked skew-fade shell，而不是只会在文案里成立的情绪故事。

## 结论
给予正式编号 **`Rank 435`**，并把该 fresh intake 首判为 **`keep_P1`**：这条线已经不只是“prediction-market sentiment / funding confirmation router”提示，而是留下了一条可以独立排队的 **event-linked after-cost skew-fade pocket**——`Polymarket YES/NO implied-probability skew` 为主 alpha，`Binance funding` 做方向确认，`flat spot velocity + strike-distance + fee cap + entry-price ceiling + expiry guard` 负责 execution realism。当前仍缺公开样本级 after-cost 业绩，所以还不够直接升 `P2`，但它已经满足保留到 survivor follow-up 的最低门槛。

## 写回 runtime 的最小必要变化
- 分配新正式编号：`Rank 435`
- `Fresh intake slot` 更新为本对象的 `keep_P1` 首判
- `Surviving candidate slot` 切换到 `Rank 435`，并恢复 1 次 follow-up 预算
- `cycle_plan[2]` 写回 result/status=`done`

## 下一步最小 follow-up 方向
唯一值得做的 survivor follow-up 应该是：补一个最便宜的 after-cost honesty check，确认这条 skew-fade 不是只靠单事件/单窗口/单参数写出来的源码故事，而是在至少多个 hourly event window 上留下可重复的净回归痕迹。

## 尾部执行状态（non-blocking）
- 首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 在异步执行中被 SIGKILL 终止，按 policy 记为非阻断尾部失败；不回滚本轮已写出的 verdict/state/log。
- 中文邮件摘要已独立发送成功。
