# 2026-03-17 05:24 UTC · Rank 7 cheap honesty recheck → 压回 park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD`：
  - `Paper Seat = EMA waiting_not_due`，不能在 waiting-window 空转；
  - `Live Seat` 仍无 bot2 新 promoted candidate；
  - 因此本轮默认落到 `Run 2 / Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17`：刚补完 `P3 weekly review queue`，当前没有新的真实 `append/review need`；
  - `Rank 2`：已有 `narrow paper pilot` 的 refresh / review / history 最小接线，当前也没有新的真实 append 口；
  - `Rank 7`：按板子仍保留 **唯一允许的一次 cheap honesty recheck**，本轮正好应该把它做完，然后给出 `升格 / park`。
- 因此本轮主点固定为：**只围绕 Rank 7 的 `fixed_priority` 做 1 次便宜诚实检查**，回答：
  - 能否在**不破坏成本 / 跨标的存活**的前提下，
  - 把极端 `no_trade_ratio≈98.6%` 压回更可用范围？

## 本轮主点 + 紧邻子点
- 主点：新增 Rank 7 的 cheap honesty recheck artifact + reader-facing 页面。
- 紧邻子点：把 `docs/TODO.md` 顶板与 Rank 7 条目同步成最新 hard verdict，避免它继续占用 `P1 weak candidate` 身份。

## 本轮做了什么
### 1) 新增脚本
- `scripts/build_adaptive_trend_combo_honesty_recheck.py`

作用：
- 复用现有 `Binance 120d / 15m / BTC+ETH+SOL` 历史样本与已有 clean replication 逻辑；
- 不追新 bar，不扩新大框架；
- 只围绕原本最不差的 `fixed_priority`，测试 3 个“只放松 1 条门”的邻近版本：
  1. `EMA+combo`
  2. `EMA+retest`
  3. `EMA+任一门`

### 2) 新增 artifacts / 网页落点
新增：
- `reports/artifacts/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck_summary.csv`
- `reports/artifacts/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck_asset_summary.csv`
- `reports/artifacts/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck_meta.csv`
- `reports/site/factors/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck.html`

并同步：
- `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
  - 新增指向 honesty recheck 的 reader-facing 链接与一句话结论。

### 3) 同步交易台指挥板
更新：
- `docs/TODO.md`

更新点：
- `Next 3 bot3 runs` 顶部 authoritative override：
  - 把 `Rank 7` 从 `P1 weak candidate / evidence pool` 压回 `park / evidence pool`；
  - 明确本轮之后，若 `Rank 17 / Rank 2` 都无真实 P3 append/review need，就直接回到新的 fresh intake / clean replication。
- `Run 2 / 2a`：
  - 写明唯一允许的 cheap honesty recheck 已完成；
  - 写明两类结果：
    - `EMA+combo` 几乎不改善交易密度；
    - `EMA+retest / EMA+任一门` 虽把 `no_trade_ratio` 压到约 `21.1%`，但 `6~20bps` 下跨资产回报全部转负。
- Rank 7 主条目：
  - 从 `P1 weak candidate` 改回 `park / evidence pool`。

## 关键结果
6bps/side 下：
- `fixed_priority_baseline`：
  - `mean_total_return ≈ +2.33%`
  - `positive_asset_ratio = 2/3`
  - `mean_no_trade_ratio ≈ 98.60%`
- `ema_plus_combo`：
  - 与 baseline 几乎同一组样本，结果基本重合；
  - 说明单纯去掉 retest 门并没有真正改善交易密度。
- `ema_plus_one`：
  - `mean_no_trade_ratio ≈ 21.10%`
  - 但 `mean_total_return ≈ -33.68%`
  - `positive_asset_ratio = 0/3`
- `ema_plus_retest`：
  - `mean_no_trade_ratio ≈ 21.10%`
  - 但 `mean_total_return ≈ -34.42%`
  - `positive_asset_ratio = 0/3`

成本梯度 `10/15/20bps` 下结论不变：
- 只要把交易密度从极端稀疏状态压下来，跨资产回报就一起塌掉；
- 没有出现“更可用交易密度 + 仍保留成本/跨标的存活”的中间地带。

## hard verdict
- Rank 7 当前应 **压回 `park / evidence pool`**。
- 这轮 cheap honesty recheck 已经完成了它被允许的唯一一次“便宜续命机会”；
- 更诚实的 desk 读法是：
  - 这条线并非完全没 edge；
  - 但**没有证据证明它能在不破坏成本 / 跨标的读法的前提下，把极端稀疏度压回可部署区间**；
  - 因此不应继续保留 `P1 weak candidate` 身份。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_adaptive_trend_combo_honesty_recheck.py`
2. `python3 scripts/build_adaptive_trend_combo_honesty_recheck.py`
3. `grep -n "Rank 7 adaptive trend combo\|fixed_priority_honesty_recheck\|05:24 UTC" docs/TODO.md`
4. `grep -n "fixed-priority honesty recheck\|park / evidence pool" reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
5. `sed -n '1,40p' reports/artifacts/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck_summary.csv`

## 对 desk 主线的意义
- 这轮没有继续在 `Rank 7` 上做 wording / closeout 磨皮，而是把那唯一允许的 cheap check 真做完了；
- 做完之后，Scout Seat 的 active 高优先 backlog 更干净：
  - `Rank 17 / Rank 2` 继续只在真实 `P3 append/review need` 出现时才认领；
  - 否则默认直接切回新的 `paper / repo based 5m / 15m crypto` intake / clean replication。

## 网页可见落点
- `reports/site/factors/scout_adaptive_trend_combo_15m/fixed_priority_honesty_recheck.html`
- `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
- 首页索引将在本轮结尾刷新。

## Git / 提交
- 本轮未提交。
- 原因：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
