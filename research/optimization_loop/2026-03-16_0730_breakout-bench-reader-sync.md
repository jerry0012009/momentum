# 2026-03-16 07:30 UTC｜breakout bench reader-facing sync

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 `Next 3 bot3 runs`。
- `Run 1 / Paper Seat` 已在 `07:13 UTC` 实际执行过 guarded refresh，并如实回到 `waiting_not_due`；不该继续重复守门。
- `Run 2 / Live Seat` 当前 desk 目标不是再做同类 rerun，而是把 **breakout 的 bench verdict** 同步到 reader-facing 落点，避免只停在 `TODO` 与内部日志里。

## 本轮认领
- 主点：把 `support_breakout_v0` 的 **bench** 结论同步到 reader-facing 的 `alpha_closure_board` 页面。
- 紧邻子点：同步更新 closure board 里与 breakout 排位相关的 deployment ladder / baseline 比较 / plumbing 口径，避免网页仍写着旧的 `one_more_gate`。

## 做了什么改动
1. 修改 `scripts/build_alpha_closure_board_report.py` 中 breakout 对应 reader-facing 文案：
   - 把 breakout 主卡从 `needs one more gate` 改成 `bench`；
   - 明确它当前是 **保留条件性 alpha 价值，但退出默认主资源位**；
   - 把重开条件写清楚：只有 future genuinely new `pure-test / down-tail` blocker reduction，或 Scout Seat 先产出更强 challenger 后，才配重新争默认资源。
2. 同步改写 closure board 中与 breakout 相关的静态摘要：
   - 首页摘要卡（谁最接近 paper trading）
   - deployment ladder 的 Step 2 / 当前位置 / 距离 paper 的说明
   - `structure_vs_ema_baseline` 比较表中的 breakout 行
   - `promotion gate / tiny-live plumbing` 里原本默认替 breakout 预留升级通道的表述
3. 重建 reader-facing 页面：
   - `python3 scripts/build_alpha_closure_board_report.py`
4. 刷新本地站点首页源文件：
   - `python3 scripts/build_site_index.py`
5. 完成 reader-facing 站点发布与首页刷新：
   - `bash scripts/publish_report_site.sh`
   - `bash scripts/publish_homepage_index.sh`

## 关键证据（为什么现在该写成 bench）
- breakout 仍保留条件性 alpha 读法：
  - `avoid_fluctuating` 后 hourly path 约 `15.46%`
  - `ETH+SOL pair halfsize` 后 hourly path 约 `19.90%`
  - 说明它不是零信息噪音
- 但 desk 当前更看 blocker 是否继续下降；而最新 hard verdict 仍停在：
  - `pure_down = 0/100`
  - `predown_bridge_12h = 0/11`
  - `downrisk_48h = 0/109`
  - `future_pure_down_48h = 0/44`
- 因此更诚实的 reader-facing 收口已经不是 `one_more_gate`，而是：
  - **bench / conditional alpha**
  - 保留证据，不再继续占用默认 Live Seat 主资源

## 最小验证
- `python3 scripts/build_alpha_closure_board_report.py` ✅
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` ✅
- `python3 scripts/build_site_index.py` ✅
- `grep -n "bench\|pure_down=0/100" reports/site/factors/alpha_closure_board/report.html` ✅
  - 已确认 closure board 网页本地镜像出现 breakout=`bench` 与关键 blocker 数字
- `bash scripts/publish_report_site.sh` ✅
- `bash scripts/publish_homepage_index.sh` ✅

## 网页可见落点
- 主要 reader-facing 落点：
  - `reports/site/factors/alpha_closure_board/report.html`
  - 已通过 `publish_report_site.sh` 发布到站点
- 当前该页已把 breakout 从旧的 `one_more_gate` 改成 `bench`，并明确写出不再占用默认主资源。

## 风险 / 边界
- 本轮没有新增 breakout blocker reduction 证据；价值在于把 desk 已经做出的 `bench` 判断，压成对外可见且自洽的 reader-facing 页面。
- `publish_report_site.sh` 会顺手重建多张既有页面；本轮虽然主认领点只有 breakout bench sync，但发布过程中确实触发了站点常规重建。这些不是本轮主结论，只是发布脚本自带动作。
- 当前最重要的事实同步已经完成：reader-facing 页面与站点首页都已发布到最新口径。

## 下一步建议
1. 默认把 bot3 主资源转去 `Scout Seat` 或 `tiny-live plumbing`，不要再在 breakout 上做同类 rerun。
2. 若后续要重开 breakout，必须先拿到 genuinely new `pure-test / down-tail` blocker reduction。
3. 下一轮若认领 Run 3，优先检查：
   - `Rank 1 τ-band` 是否终于有 genuinely new local bar 可做 honest recheck；
   - 若没有，则转 `Rank 2 combo_all` 的轻量 forward 复核，或继续补 `small_live` 执行链紧邻卡。

## 提交状态
- HEAD：`1f84291`
- 本轮未提交：worktree 仍有大量与本轮无关的历史脏文件 / 未跟踪文件，避免混提。
