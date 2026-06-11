# PSAR anchor + EMA confirm：两条轻量诚实守门通过，下一步只保留 1 次最小 clean replication

- 时间：2026-03-18 03:39 UTC
- 轮次：bot3 auto optimization / Trading Desk / Run 2 / Scout Seat
- 当前 seat 状态：`Paper Seat / EMA = running paper / waiting_not_due`
- 本轮主点：完成 `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` 的 source intake 与两条轻量诚实守门
- 紧邻子点：把当前 verdict 回写到 `docs/TODO.md` 顶板，并落一张可复用的 source-intake artifact

## 1. 为什么这轮选这个
先读了 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与当前 `Next 3 bot3 runs`。

本轮最诚实的排班判断很直接：
- `Run 1 / EMA` 仍处于真实 `waiting_not_due`，最新 due guardrail 显示 A 股下一次 close 还在 `2026-03-18 07:00 UTC`；
- `Rank 17 / Rank 2 / Rank 29 / Rank 32b` 都已属于 `P3 narrow paper lane`，当前没有新的 `append/review` 事件；
- `Rank 43` 与 `Rank 40` 已在最近两轮完成各自唯一 fast-lane budget，并都压回 `park / evidence pool`；
- 因此这轮默认应落到 `Run 2 / Scout Seat`，而且要优先认领当前边际价值最高的 fresh repo source：`Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`。

## 2. 本轮先核对了什么
### Paper Seat due-check（Run 1 只做核对，不空转）
读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：
- A 股三条 lane：`next_expected_close_utc = 2026-03-18 07:00 UTC`
- 美股：`2026-03-18 20:00 UTC`
- Crypto：`2026-03-19 00:00 UTC`
- 当前全 desk 没有 `due-now / overdue` lane

结论：`EMA` 这一轮确实只是 `waiting_not_due`，所以本轮不能把 paper refresh 硬做成主点。

### fresh source 证据读取
本轮只读 source-level 证据，不做 replication：
- `README.md`
- `psar_scalper/src/trend.py`
- `psar_scalper/src/score_utils.py`
- `psar_scalper/src/risk_utils.py`
- `SISTEMA_30M_5M_1M.md`

## 3. 两条轻量诚实守门结果
### 守门 1：`trade on / trade off` 能不能清楚冻结？
**通过。**

当前能冻结成一个足够清楚的 clean-room intake 口径：
- `trade on`：高一级 `PSAR anchor`（30m 或 1h）先给方向许可；15m `EMA direction + slope` 做 continuation 确认；低一级 micro layer 只做 veto，不单独充当 alpha；执行默认 `next-bar open + no-overlap + fixed hold 6~12 bars`。
- `trade off`：PSAR anchor 未给方向许可、或 15m EMA direction/slope 未确认、或 micro veto 明确逆向时不交易；若最终必须依赖 `ALWAYS_IN_MARKET`、多对择优、或超厚 1m execution layer 才能讲通，则直接视为当前 desk 不适配。

更直白地说：这条 source 现在已经能回答一个当前 desk 真正在乎的问题——**PSAR 更像结构锚 / flip veto，而不是和 EMA 并列的原始入场 alpha。**

### 守门 2：有没有明显 `lookahead / repaint / data leakage`？
**通过，但带保留意见。**

source-level 证据：
- `trend.py` 里的 `compute_trend_score` / `build_trend_signal` 只基于当前 indicator snapshot 的 `psar_30_dir / ema_30_dir / ema_30_slope_deg / ema_1_fast / ema_1_slow / atr_pct_30m` 组合分数；
- `score_utils.py` 的 `compute_atr_health / compute_macro_alignment / compute_micro_alignment` 也都是用当前 regime、ATR%、micro slope、bandwidth 做过滤与打分；
- `risk_utils.py` 则只是把当前 ATR regime 映射到 `SL/TP / max_bars / trailing`。

当前没看到一眼可判死刑的前视、重绘或未来数据穿越。

但保留意见同样明确：
- 原仓库自带 `ALWAYS_IN_MARKET`；
- 有多对交易与 priority/planner 逻辑；
- 原始结构更偏 `30m / 5m / 1m` 联动，而不是我们当前要的轻量 `15m` desk template。

所以这条线虽然过了诚实守门，但**不能直接被误读成“alpha 已成立”**；它目前只是拿到了那 **1 次最小 clean replication** 的执行资格。

## 4. 本轮 hard verdict
**`Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` -> `guard-passed / admit_to_clean_replication_queue`**

一句话原因：
- 它已经能把 `trade on / trade off` 说清楚；
- 当前也未见明显 `lookahead / repaint / leakage`；
- 同时它直接服务 `EMA / PSAR raw alpha focus`，比回头磨已 park 的 `Rank 40 / 43` 或过早回退 `Run 3` 更贴当前 desk 主线。

## 5. 本轮产物
1. `reports/artifacts/literature/scout_repo_psar_anchor_ema_confirm_source_intake_card.csv`
   - 记录了 source 类型、trade on/off、honesty gate、最小 replication 设计与当前 verdict
2. `docs/TODO.md`
   - 顶部 `Scout Seat` authoritative note 已从 `source intake next` 更新为 `guard-passed / admit_to_clean_replication_queue`
   - `Next 3 bot3 runs` 已同步改成：下一轮若 `EMA` 仍是 waiting-window，就继续这同一条线的 **1 次最小 clean replication**
3. reader-facing 落点
   - 继续复用已有 digest 页面：`reports/site/reading/quant_digests/2026-03-18_0255_psar-anchor-ema-confirmation-gate.html`
   - 同时通过重建 `momentum_todo.html`，把当前 authoritative 排班对外可见

## 6. 最小 clean replication 该怎么做（仅作为下一轮预算）
若下一轮继续同一条线，只允许做：
- 资产：`BTC / ETH / SOL`
- 样本：本地 `180~365d 15m cache`
- 三臂对照：`EMA_raw` vs `PSAR_raw` vs `PSAR_anchor + EMA_confirm`
- 统一执行：`next-bar open`、`no-overlap`、`fixed hold 6~12 bars`
- 成本：至少 `6 / 10 / 15 bps per side`
- 先回答 4 个问题：
  1. `post-cost return`
  2. `positive_asset_ratio`
  3. `trade_count`
  4. `flip-to-fail rate`

## 7. 风险 / 边界
- 这轮还不是 replication，更不是 paper candidate verdict。
- 目前最容易犯的错误，是把“工程模板看起来合理”误读成“alpha 已被验证”。
- 如果下一轮发现 edge 只存在于原仓库那套厚 execution layer / 多对择优，而不是高层 PSAR anchor 本身，就应快速压回 `park / evidence pool`。

## 8. 下一步建议
按当前 `TRADING DESK BOARD`：
1. 若下一轮 `EMA` 仍是 `waiting_not_due`，默认继续同一条线，只做 **1 次最小 clean replication**；
2. 若这一步 clean replication 失败，再回退比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`；
3. 默认不要回头磨 `Rank 40 / Rank 43`，也不要挤占当前没有状态变化的 `P3 continuity`。

## 9. commit / 邮件
- commit：未提交
- 原因：repo 当前仍有大量与本轮无关的脏文件 / 未跟踪产物，安全 selective commit 成本过高，避免混提
- 邮件：本轮完成后按要求发送中文摘要
- 当前 commit hash：`5331292`
