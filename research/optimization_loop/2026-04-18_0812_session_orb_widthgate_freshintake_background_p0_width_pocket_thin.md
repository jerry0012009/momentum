# bot3 optimization loop — session ORB width-gate fresh intake收口

- 时间：2026-04-18 08:12 UTC
- 执行对象：`research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
- 执行动作：fresh intake first-verdict
- 结论：`background/P0`

## 本轮最小决定性检查
按 digest 既有 portability artifact 复核 plain ORB 与唯一看起来像有效的 `US session + widest quartile box` pocket，确认这条线是否已经足够支撑新的 intraday breakout front object。

读取文件：
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_session_orb_widthgate_probe_summary.json`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_session_orb_widthgate_probe_trades.csv`

## 复核结果
- plain ORB 整体仍明显为负：`896` 笔，`gross=-5.65bps/笔`，`net8=-13.65bps/笔`。
- 分 session 也都没有独立过线：Tokyo `gross=-12.95bps`，EU `gross=-2.31bps`，US `gross=-1.64bps`。
- 唯一像 pocket 的切片仍是 `US + widest quartile`：`74` 笔，`gross=+10.62bps`，`net8=+2.62bps`；但 timeout rate 高达 `47.3%`，说明很多单不是干净 TP，而是拖到超时平仓。
- 该 pocket 没有跨资产稳定：
  - `BTCUSDT`: `10` 笔，`gross=-11.60bps`，`net8=-19.60bps`
  - `AVAXUSDT`: `19` 笔，`gross=-0.49bps`，`net8=-8.49bps`
  - `ETHUSDT`: `18` 笔，`gross=+19.31bps`，`net8=+11.31bps`
  - `SOLUSDT`: `27` 笔，`gross=+20.88bps`，`net8=+12.88bps`
- 该 pocket 也没有跨月份稳定：
  - `2026-02`: `41` 笔，`net8=-0.95bps`
  - `2026-03`: `20` 笔，`net8=+15.76bps`
  - `2026-04`: `13` 笔，`net8=-6.34bps`

## 决策
`session opening-range breakout × box-width gate` 当前公开可见价值仍停留在 `US + widest quartile` 的薄 pocket，而且该 pocket 既未跨资产稳定（只剩 ETH/SOL 正、BTC/AVAX 负），也未跨月份稳定（2 月与 4 月在 `8bps` 下已转负）；因此这不是一个足够诚实的新 breakout front object，本轮 fresh intake 直接收口 `background/P0`。

## 回写要点
- 不分配 Rank（未达到 `keep_P1`）
- `cycle_plan` item1 标记 `done`
- `Fresh intake slot` 更新 latest result / record

## 尾部执行状态（non-blocking）
- homepage 刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步返回 `signal SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件摘要：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送（code 0）。

