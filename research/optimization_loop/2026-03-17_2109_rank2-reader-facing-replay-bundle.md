# 2026-03-17 21:09 UTC · Rank 2 reader-facing replay bundle

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 reader-facing replay bundle`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍是 `running paper / waiting_not_due`
  - `Scout Seat` 顶板 authoritative 读法仍是本地 fast-lane `exhaustion state`
  - `Live Seat` 默认空席；本轮没有 bot2 新的 promoted candidate
  - 因此本轮继续诚实落到 `Run 3 / tiny-live plumbing fallback`

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 最近 runs：
  - `19:37 UTC`：写回 `Scout fast-lane exhaustion`
  - `20:59 UTC`：生成 `small_live_rank2_next_replay_bundle_v1.csv`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = waiting_not_due`
  - `Scout Seat`：当前没有新的合格 `paper / repo based 5m / 15m crypto` intake
  - `Run 3`：当前最值钱的是把已存在的 Rank 2 replay / preflight artifact 真正挂到 reader-facing 页面，而不是继续只留在 CSV

## active 路径边际价值比较
### Run 1 / EMA
- 当前 due guardrail 已回到全 desk 无 `due-now / overdue` lane
- 继续认领只会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板 authoritative override 已明确：当前本地 `paper / repo based 5m / 15m crypto` fast lane 暂时 exhaustion
- 本轮没有新的合格 source，也没有新的 promoted candidate

### Run 3 / tiny-live plumbing
- `small_live_rank2_next_replay_bundle_v1.csv` 与 `small_live_rank2_replay_preflight_snapshot_v1.csv` 已经存在，但 `alpha_closure_board/report.html` 还没把这两张更贴近当前允许动作的表真正 reader-facing 化
- 相比继续追加新的 packet / starter / wording，这一刀更接近 deployable artifact：让页面直接回答“现在唯一允许的一腿是什么、为什么是这条腿、数字上怎么读”

## 本轮主点 + 紧邻子点
- **主点**：把 `Rank 2 next replay bundle` 正式挂进 `alpha_closure_board/report.html`
- **紧邻子点**：顺手把 `Rank 2 replay preflight snapshot` 也挂进同页，补齐最小 precision / rounding 数字读法

## 本轮做了什么
### 1) 扩展 builder，把两张现有 artifact 真正 reader-facing 化
文件：`scripts/build_alpha_closure_board_report.py`

本轮新增：
- 读取 `small_live_rank2_replay_preflight_snapshot_v1.csv`
- 新增 HTML rows 渲染：
  - `rank2_next_replay_bundle_rows_html`
  - `rank2_replay_preflight_snapshot_rows_html`
- 在 `Rank 2 next status-changing gate` 后插入两个新卡片：
  - `Rank 2 next replay bundle（v1）`
  - `Rank 2 replay preflight snapshot（v1）`

页面现在会直接回答：
- 当前唯一允许的一腿是什么
- 样例名义金额怎么读
- 必须抓哪三段 refs
- 通过后最多推进到哪一步
- 白名单三条腿在当前 precision / rounding 口径下为什么是这个优先顺序

### 2) 做最小验证并重建 reader-facing 页面
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

结果：
- builder 编译通过
- `reports/site/factors/alpha_closure_board/report.html` 已重建
- 页面里已确认出现：
  - `Rank 2 next replay bundle（v1）`
  - `Rank 2 replay preflight snapshot（v1）`

### 3) 刷新站点首页
执行：
- `bash scripts/publish_homepage_index.sh`

结果：
- 首页 index 已刷新
- 对外入口已发布到：`https://jp.jerrypsy.top/momentum/`

## 当前 hard verdict
**当前 `Run 3` 不该再只把 Rank 2 的下一步埋在 artifact 目录里。更诚实的 reader-facing 状态应该直接写清：当前唯一允许动作仍是一次 whitelist-bound `test/no-fill` replay，而更适合作为第一腿的是 `SOL-USD / SOLUSDT`；即使通过，也只推进到 `eligible_for_shadow_parity_review`，绝不是 tiny-live 放行。**

更具体地说：
- `next replay bundle` 负责把当前唯一允许动作压成单行执行包
- `replay preflight snapshot` 负责给这个顺序补最小数字解释，避免只靠文案偏好决定先后
- 这两张卡挂上页面后，后续如果 Jerry / bot2 只看网页，不必再去 artifact 目录里自己拼出当前允许动作

## reader-facing / deployable 落点
- 页面：`reports/site/factors/alpha_closure_board/report.html`
- 站点首页已刷新：`reports/site/index.html`
- 对外可见入口：`https://jp.jerrypsy.top/momentum/`

## 验证 / 证据
已验证：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` 成功
- builder 成功重建 `alpha_closure_board/report.html`
- 页面文本检索已确认包含：
  - `Rank 2 next replay bundle（v1）`
  - `Rank 2 replay preflight snapshot（v1）`
- `publish_homepage_index.sh` 成功发布首页

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有重新占用 `Live Seat`
- 本轮没有新增 Scout candidate
- 本轮没有再继续补新的 Rank 2 packet / starter row artifact，而是把已有最值钱的两张表公开成 reader-facing 页面
- 这轮改变的是可见性与执行清晰度，不是策略状态本身

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
