# 2026-03-17 06:23 UTC · Rank 25 time red-watch honest recheck → park

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`；
  - `Live Seat` 仍空；
  - 因此按默认顺序落到 `Run 2 / Scout Seat`。
- 再比较所有 active Scout 候选边际价值：
  - `Rank 17 / Rank 2` 都是 `P3 narrow paper pilot`，当前未看到新的真实 `append/review need`；
  - `Rank 25` 刚在上一轮升到临时 `P2 / time-stability red-watch`，并且 board 已明确：下一轮只允许做 **1 次 genuinely verdict-changing 的最小诚实检查**，回答“升 P3 / 压回 park”。
- 所以本轮只认领这一件事：**验证 Rank 25 的时间不稳到底是不是单点热像素**。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 25` 的那 1 次最小诚实检查，并给出 `升 P3 / 压回 park` 的硬结论。
- 紧邻子点：把结论同步到 `docs/TODO.md` 与 factor 页，形成 reader-facing 网页落点。

## 做了什么
### 1) 新增独立 recheck 脚本与 artifact
新增脚本：
- `scripts/build_ema_donchian_time_redwatch_recheck.py`

基于现有 `BTC / ETH / SOL 120d 15m` cache（不追新 bar、不新增下载）生成：
- `reports/artifacts/scout_ema_donchian_breakout_15m/time_redwatch_recheck.csv`
- `reports/artifacts/scout_ema_donchian_breakout_15m/time_redwatch_scope_check.csv`
- `reports/artifacts/scout_ema_donchian_breakout_15m/time_redwatch_verdict.csv`
- `reports/site/factors/scout_ema_donchian_breakout_15m/time_redwatch_recheck.html`

### 2) 这次 honest recheck 具体问了什么
只问一个问题，不扩新框架：
- 原主变体 `l30_c3` 的时间稳定性 red-watch，
- 到底只是单点参数热像素，
- 还是连唯一仍为正 pocket 的邻近变体 `l40_c3` 也同样不稳。

为避免只靠参数邻域绕过去，又补了一个最小 scope honesty check：
- 不改规则；
- 只把资产 scope 诚实缩到更强的 `ETH+SOL-only`；
- 看它是否至少把时间 bucket 结构拉平。

### 3) 检查结果
#### 邻近正 pocket 重检查（`l30_c3` vs `l40_c3`）
- 两个变体都重复出现完全同样的时间结构：
  - `bucket_1 负`
  - `bucket_2 正`
  - `bucket_3 负`
- 两者时间正收益 bucket 都只有 `3/9`。

#### ETH+SOL-only 窄范围检查
- 即使去掉最弱腿 `BTC`，只看 `ETH+SOL-only`：
  - `bucket_1 ≈ -10.48% ~ -14.77%`
  - `bucket_2 ≈ +39.26% ~ +40.00%`
  - `bucket_3 ≈ -11.22% ~ -10.25%`
- 也就是说，窄范围之后仍然只有中段 bucket 为正，时间正收益 bucket 仍只有 `1/3`。

## 本轮 hard verdict
- `Rank 25 EMA + Donchian breakout`：**从临时 `P2` 如实压回 `park / evidence pool`**。
- 核心原因不是成本、跨标的或参数邻域先崩；
- 而是这 1 次 genuinely verdict-changing 的最小诚实检查已经说明：
  - 时间稳定性问题不是单点像素；
  - 在正邻域和窄范围 scope 下都没有被修复；
  - 因此当前不支持升到 `P3 narrow paper pilot`。

## 同步更新
### Desk / TODO
已更新 `docs/TODO.md`：
- `Rank 25` 阶段表从 `P2 / time-stability red-watch` 改为 `park / evidence pool`；
- `Next 3 bot3 runs` authoritative override 已改写为：
  - 先看 `Rank 17 / Rank 2` 是否有真实 `P3 need`；
  - 若无，下一轮默认直接切 fresh paper/repo intake。
- `Run 2 -> 2r Rank 25` 条目已同步 recheck 后的 hard verdict。

### Reader-facing 网页落点
已更新：
- `reports/site/factors/scout_ema_donchian_breakout_15m/report.html`

新增：
- `reports/site/factors/scout_ema_donchian_breakout_15m/time_redwatch_recheck.html`

网页上现在能直接看到：
- 为什么它先前能进 P2；
- 为什么这次最小诚实检查后又被压回 park。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_ema_donchian_time_redwatch_recheck.py`
2. `python3 scripts/build_ema_donchian_time_redwatch_recheck.py`
3. `sed -n '1,20p' reports/artifacts/scout_ema_donchian_breakout_15m/time_redwatch_verdict.csv`
4. `grep -n "park / evidence pool\|ETH+SOL-only narrow-scope" reports/site/factors/scout_ema_donchian_breakout_15m/time_redwatch_recheck.html`
5. 回读 `docs/TODO.md` 顶部 `Rank 25` 与 `Next 3 bot3 runs` 片段

## 风险 / 边界
- 本轮没有追最新 bar；
- 没有改信号规则；
- 没有把 `Rank 25` 继续人为续命成“再看一次”；
- 没有打开新候选；
- 只做了 board 明确允许的那 1 次最小诚实检查。

## 下一步建议
1. 下轮先看 `Rank 17 / Rank 2` 是否出现真实 `P3 append/review need`。
2. 若没有，按 desk 规则直接切回新的 `paper / repo based 5m / 15m crypto` fresh intake。
3. `Rank 25` 后续除非 bot2 明确点名或出现新的 genuinely verdict-changing 证据，否则不再默认占主资源。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
