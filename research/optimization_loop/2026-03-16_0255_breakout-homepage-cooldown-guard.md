# 2026-03-16 02:55 UTC · breakout homepage cooldown guard

本轮主点：**breakout 的 rerun guard -> 首页 deployment watch 动态冷却守门**。

## 为什么选这刀
- 先看了 `docs/TODO.md`、repo 当前状态、最近 optimization loop 记录。
- `EMA` 主线仍更接近 paper，但这轮用 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 做 fast-precheck 后，当前仍**没有** `due_now / overdue` lane；最靠前的 A 股日频 close 还要约 `4.2h`。
- `breakout` 虽然本地 cache 尾部已继续前推，但 `2026-03-15 23:25 UTC` 刚做过 heavy refresh recheck；当前真正有价值的不是再重复重跑，而是把“现在别误判成该立刻 rerun”这件事压成首页可见的执行守门。

## 本轮执行
1. 重跑 `python3 scripts/build_breakout_revisit_guard.py`
   - 刷新 `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv`。
   - 当前 guard 读法：
     - `last_heavy_recheck_checked_bar_utc = 2026-03-13 13:00:00 UTC`
     - `current_cache_latest_bar_utc = 2026-03-16 02:00:00 UTC`
     - `cache_tail_delta_vs_last_recheck = 61.0h`
     - `hours_since_last_heavy_recheck = 3.5h`
     - `revisit_guard_verdict = cache_advanced_but_recent_recheck_cooldown_hold`
   - 也就是说：**cache 的确更往后了，但 heavy rerun 刚做完不久，当前更诚实动作仍是短冷却 hold，而不是马上再跑一次同类 heavy rerun。**

2. 修改 `scripts/build_site_index.py`
   - 新增 breakout rerun guard 的**动态重算**逻辑，不再只照抄旧 artifact 行。
   - 首页现在会按当前时间重算：
     - guard verdict
     - 距最近 heavy recheck 已过去多久
     - 冷却还剩多久
     - 当前默认动作
   - 这样在 waiting window 里，首页不会继续把 breakout 误写成旧的 `cache_advanced_rerun_worth_checking`。

3. 更新 `docs/TODO.md`
   - 在 breakout freeze verdict 主线下补一条最新补充，明确：
     - 本轮把 breakout 守门继续压成动态 homepage watch；
     - 当前 verdict 已收紧为 `cache_advanced_but_recent_recheck_cooldown_hold`；
     - cooldown 走完前，默认把执行重心切回 EMA 的下一次真实 market-close refresh。

## 结果 / 对 Jerry 现在最有用的判断
- **EMA：** 这轮仍未到真实 close，继续等下一根 completed bar；不要伪造 refresh。
- **Breakout：** 当前更诚实状态不是“该马上 rerun”，而是：
  - cache 已前推，说明后面**值得再查**；
  - 但最近一次 heavy rerun 距今只有约 `3.5h`，因此当前应先 `cooldown hold`；
  - 首页现在会直接显示剩余冷却时间，减少误判。
- **Fibonacci：** 本轮未动，继续 archived / optional filter。

## 验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：fast-precheck 拒绝伪 refresh；当前无 `due_now / overdue` lane。
- `python3 scripts/build_breakout_revisit_guard.py`
- `python3 scripts/build_site_index.py`
- `grep "Breakout rerun guard\|EMA ledger" reports/site/index.html`
  - 已确认首页现在显示：
    - `EMA ledger` 距下次 A 股 close 约 `4.1h`
    - `Breakout rerun guard = cache_advanced_but_recent_recheck_cooldown_hold`
    - 冷却剩余约 `2.5h`

## git / hygiene
- 本轮只改了：
  - `docs/TODO.md`
  - `scripts/build_site_index.py`
  - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv`
  - `reports/site/index.html`
- **未提交 git。** 原因：当前 worktree 已有大量与本轮无关的脏文件 / 未跟踪文件（包括 docs、reports、artifacts、scripts 以及 workspace 上层目录内容），不适合在本轮混提；按要求保持 selective，不把无关改动一起打包。

## 下一刀默认
- 在 breakout 这条线上，等当前 cooldown 走完后，若 cache 仍领先，再做**一次** heavy rerun 检查即可；在那之前默认不要重复跑同类 heavy refresh。
- 在 EMA 这条线上，下一次更值钱的动作仍是等 A 股 next close 到点后，沿同一张 live ledger 真续写 `market-close refresh / week-1 review`。
