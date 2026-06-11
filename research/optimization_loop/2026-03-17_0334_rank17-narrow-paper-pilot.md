# 2026-03-17 03:34 UTC · Rank 17 pullback recovery confirmation 升格为 narrow paper pilot（ETH+SOL only）

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat / EMA` 当前仍是 `waiting_not_due`，因此本轮默认主资源继续落到 `Scout Seat`。
- 先比较 active Scout 候选的当前边际价值：
  - `Rank 2 combo_all` 已是 `narrow paper pilot approved`，但当前没有新的 `append/review need`，继续认领只会重复低边际值接线。
  - `Rank 7~16 / 18~20` 已完成 `clean replication + Light Stability Pack` 且都在 `park / evidence pool`，本轮没有比 `Rank 17` 更接近减少真实 gate 的动作。
  - `Rank 17 pullback recovery confirmation` 刚完成 `paper candidate wiring`，按 board 规则正处在最适合做 **1 次 genuinely verdict-changing 最小检查** 的位置。
- 因此本轮主点固定为：**对 Rank 17 做 1 次真正会改变 verdict 的最小诚实检查，而不是继续补近义 wiring 或直接转 fresh intake。**

## 开始前检查
- `git status --short` 显示 repo 工作区存在大量与本轮无关的历史脏文件 / 未跟踪产物；本轮只做 selective 写入，不混提。
- 最近 optimization logs：
  - `2026-03-17_0229_rank17-pullback-paper-candidate.md`
  - `2026-03-17_0233_rank17-paper-candidate-wiring.md`
  - `2026-03-17_0320_rank19-box-consolidation-park.md`
  - `2026-03-17_0326_rank20-price-volume-divergence-park.md`
- 当前 desk 状态：
  - `Paper Seat = EMA / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = 默认主资源`

## 本轮主点 + 紧邻子点
- 主点：对 `Rank 17 pullback recovery confirmation` 做最小 scope-honesty check，判断是否能从 `paper candidate pool` 升到 `narrow paper pilot`。
- 紧邻子点：把 verdict 同步写回 `docs/TODO.md` 与 reader-facing factor 页，并补最小 `narrow paper pilot` 接线 artifact。

## 做了什么
### 1) 新增脚本
- `scripts/build_pullback_recovery_narrow_pilot_scope.py`

脚本逻辑：
- 只复用既有产物：
  - `clean_replication_summary.csv`
  - `clean_replication_asset_summary.csv`
  - `clean_replication_trades.csv`
  - `time_stability.csv`
  - `cost_trade_stability.csv`
  - `paper_candidate_admission_memo.csv`
- **不改信号规则，不追新 bar，不下载新数据**。
- 只做一个 genuinely verdict-changing 的最小检查：
  - 把当前最明显的 blocker `BTC weak leg` 从运行 scope 里诚实剥离；
  - 用同一批历史 trades 重算 `ETH+SOL-only` 在 `6 / 10 / 15 / 20 bps per side` 下的 aggregate friction ladder；
  - 若缩 scope 后 `15bps` 仍为正，则允许它从 `paper candidate pool` 升到 **更窄范围的 `narrow paper pilot approved`**；
  - `BTC` 不偷升格，单列留在 `park / excluded red-watch leg`。

### 2) 新增 deployable / paper plumbing artifacts
新增：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_friction_check.csv`
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_monitoring_board.csv`
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_seed_rows.csv`
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_refresh_history.csv`

这些产物的作用：
- 把 Rank 17 从 `paper candidate only` 继续压成一个可继续 refresh / review 的 **ETH+SOL 窄范围 paper pilot**；
- 同时保留 `BTC` 的排除与红灯，不让 aggregate headline 偷偷掩盖弱腿。

### 3) reader-facing 页面同步
更新：
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`

新页面不再只停在“paper candidate wiring”，而是直接给出：
- 为什么原始 full scope 只能停在 `paper candidate pool`
- 为什么这轮最小 honest narrowing 足以改变 verdict
- 新的 `ETH+SOL narrow paper pilot` friction / monitoring / seed rows
- `BTC` 继续 `park / excluded red-watch leg`

### 4) TODO / desk board 写回
更新：
- `docs/TODO.md`

已同步写回：
- `Rank 17` 从 `paper candidate pool` 升级为 **`narrow paper pilot approved（ETH+SOL only）`**
- `BTC` 保持 `park / excluded red-watch leg`
- `Next 3 bot3 runs` 当前窗口顺序调整为：
  - 先 fresh scout intake
  - 只有在 `Rank 17 / Rank 2` 出现真实 `append/review need` 或新的 verdict-changing check 时，才回补现有 P3

## 核心证据 / 最小诚实检查结果
### 原始 full scope（BTC+ETH+SOL）
- 主变体：`pullback2_vol1.0_break1`
- `6bps/side ≈ +10.21%`
- `10bps/side ≈ +4.07%`
- `15bps/side ≈ -3.13%`
- `20bps/side ≈ -9.81%`
- 这就是为什么它此前只能停在 `paper candidate pool`。

### 本轮新检查：ETH+SOL-only 窄范围 friction ladder
- `6bps/side ≈ +24.12%`
- `10bps/side ≈ +16.66%`
- `15bps/side ≈ +7.95%`
- `20bps/side ≈ -0.12%`
- `15bps/side` 下 `positive_asset_ratio = 2/2`
- `ETH 15bps ≈ +7.49%`
- `SOL 15bps ≈ +8.40%`

### 诚实边界
- 这不是说 `Rank 17` 全 scope 都通过了。
- 这只说明：
  - `ETH+SOL` 这两条腿已经足够进入 **`paper-only narrow pilot`**；
  - `BTC` 这条腿仍然没有过关，应继续单列 `park / excluded red-watch`。
- 同时 `20bps/side` 已接近零 / 微负，因此这条线仍然只适合 `paper-only narrow pilot`，**绝不应偷升 tiny-live**。

## 本轮 hard verdict
- `Rank 17 pullback recovery confirmation`：**升格为 `narrow paper pilot approved（ETH+SOL only）`**。
- `BTC-USD`：**继续 `park / excluded red-watch leg`**。

## 对 desk 的意义
- 这轮不是继续写 docs，而是把一条 `P2 paper candidate` 真正推进到了 `P3 narrow paper pilot`。
- 它减少的是 **scope / execution honesty** 上的真实 gate：
  - 不再把 BTC 弱腿混在同一个 pilot headline 里；
  - 也不再让 Rank 17 长期卡在 `paper candidate` 位置追求更漂亮证据。
- 这也符合当前 board 7.6 / 7.7：
  - 一旦候选进入 `paper candidate pool` 且 1~2 轮最小诚实检查没爆雷，就默认推进到 `narrow paper pilot`；
  - 到了 `P3` 之后，后续若继续认领它，只应补最小 `paper ledger / monitoring / refresh / review` 接线。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_pullback_recovery_narrow_pilot_scope.py`
2. `python3 scripts/build_pullback_recovery_narrow_pilot_scope.py`
3. Python 字符串校验：
   - `docs/TODO.md` 已写入 `narrow paper pilot approved（ETH+SOL only）`
   - `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html` 已写入 `ETH+SOL-only 在 15bps/side 仍约 7.95%`
4. 检查新增 artifacts：
   - `narrow_paper_pilot_ethsol_monitoring_board.csv`
   - `narrow_paper_pilot_ethsol_refresh_history.csv`

## 过程异常与 fallback 记录（按 8.1）
- 在更新 `docs/TODO.md` 时，第一次尝试用脚本做整段精确替换没有命中，且我自己临时拼的正则脚本还因引号没闭合报了 `SyntaxError`。
- 已按规则立刻 fallback：先 `read` 重新定位最新片段，再改用更稳的逐段 `edit` 精确替换，最终成功写回 `Rank 17` 状态、`当前窗口排班`、`2k` 执行口径。
- 另外有一条中间验证命令因 shell 里误用了反引号导致 `15bps/side: No such file or directory`，随后已立即改成 Python 字符串校验并通过；不影响最终产物与 verdict。

## 下一步建议
1. 默认把 Scout 主资源切回 **fresh paper / repo based 5m / 15m crypto intake**。
2. 若后续继续认领 `Rank 17`，只允许：
   - `ETH+SOL narrow paper pilot` 的最小 `refresh / review / ledger` 续写；或
   - 一个真正会改变 paper verdict 的最小检查。
3. `BTC` 不要因为这轮升格被顺带洗白；除非拿到新的 honest evidence，否则继续 `park / excluded red-watch`。

## 网页可见落点
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`
- 首页索引待本轮结尾统一刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## Git / 提交
- 本轮未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
