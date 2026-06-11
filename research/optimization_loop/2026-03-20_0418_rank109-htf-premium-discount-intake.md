# 2026-03-20 04:18 UTC — Rank 109 HTF premium-discount long-bias context gate source intake（guard-passed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前无 `due-now / overdue` lane
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`（约 `2.7h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD`，本轮不能空转，主资源必须切到 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1663`
- 最近 optimization logs：
  - `2026-03-20_0358_rank108-clean-replication-park.md`
  - `2026-03-20_0334_rank108-prebreak-intake.md`
  - `2026-03-20_0312_rank107-clean-replication-park.md`
  - `2026-03-20_0254_rank107-mtf-chop-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat` 按 04:10 UTC 顶板顺序应切到 `Rank 109 / HTF premium-discount long-bias context gate`
  - `manual_narrow_paper_last_run_summary.json` 上一轮仍是 `new_closed_trades_appended=0`，因此当前没有新的 `P3 status-changing event` 可以插队

## Active Scout 候选边际比较（先比较后认领）
1. **Rank 109 / HTF premium-discount long-bias context gate**
   - `P0 / fresh repo / source intake next`
   - 直接服务 `Fib retest_hold / EMA continuation` 的 long-side context，且当前只需要最便宜的 `source intake + 两条轻量诚实守门`
2. **Rank 110 / PSAR pre-flip SAR dot reclaim gate**
   - `P0 / fresh repo reserve / source intake reserve`
   - 也有价值，但当前更像 `raw alpha reserve`；在 Rank 109 还没 intake 前不该抢主资源位
3. **fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）**
   - 只有 Rank 109 / Rank 110 这一层都 exhausted 时才回退过去
4. **旧 P1 evidence_pool / P3 continuity / tiny-live plumbing**
   - 当前都不该挤掉这轮 queue-facing Scout 主链

结论：本轮只认领 `Rank 109` 这一条，不并开其他候选。

## 本轮认领
- 主点：`Rank 109 / HTF premium-discount long-bias context gate` 的 `source intake + 两条轻量诚实守门`
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 复核来源：`research/quant_digests/2026-03-20_0323_htf-premium-discount-long-bias-context.md`
- 新增生成脚本：`scripts/build_rank109_htf_premium_discount_source_intake.py`
- 执行生成：`python3 scripts/build_rank109_htf_premium_discount_source_intake.py`
- 生成产物：
  - `reports/artifacts/literature/scout_rank109_htf_premium_discount_long_bias_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank109_htf_premium_discount_long_bias_source_intake.html`
- 回写顶板：`docs/TODO.md`

## 两条轻量诚实守门（本轮冻结）
### 1) trade on / trade off
- **trade on**：只把上一根完整 `4h` K 线的 `prev4h_mid=(high+low)/2` 当 long-side context gate，不单独开仓；默认先服务 `Fib retest_hold / EMA continuation long`，首轮只回答 `entry < prev4h_mid`（discount）是否值得做 long-only allow / size-up
- **trade off**：若 short 侧 `entry > prev4h_mid`（premium）没有一致帮助、甚至更差，就不得镜像成多空对称 shared gate；它不能替代原始 trigger，也不能把 repo 的 Fib 语义偷渡成新的精细 retracement alpha

### 2) lookahead / repaint / leakage
- `prev4h_high / prev4h_low / prev4h_mid` 只能取**上一根完整** `4h` bar
- gate 计算与入场判断都冻结在 `signal 当根及之前数据`
- 下一轮 clean replication 强制 `next-bar open + no-overlap`
- 禁止 future 4h zone 倒灌、禁止事后换更漂亮的 fib/swing anchor、禁止只报 long 侧较好结果再偷渡成 shared gate

## 当前硬结论
**`Rank 109 = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线当前最值得验证的，不是“它是不是新 alpha”，而是“它是不是只配做 `long-side asymmetric context note`”。
- 当前证据最支持的岗位，是给 `Fib retest_hold / EMA continuation` 提供一个便宜的 `HTF discount` 上下文读数；
- 当前**不**支持把它包装成 `breakout-short` 的 shared short gate，也不支持把它写成多空对称 mandatory filter。

## 对顶板的直接影响
- `Paper Seat = EMA / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = Rank 109 / HTF premium-discount long-bias context gate`
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 109 / HTF premium-discount long-bias context gate 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 109 clean replication 直接 hard-fail / exhausted，则切 Rank 110 / PSAR pre-flip SAR dot reclaim gate 的 source intake；若 Rank 110 也 exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank109_htf_premium_discount_source_intake.py`
- artifact：`reports/artifacts/literature/scout_rank109_htf_premium_discount_long_bias_source_intake_card.csv`
- reader-facing 页面：`reports/site/reading/repo_scout/rank109_htf_premium_discount_long_bias_source_intake.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank109_htf_premium_discount_source_intake.py`
- 回读确认：
  - `reports/artifacts/literature/scout_rank109_htf_premium_discount_long_bias_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank109_htf_premium_discount_long_bias_source_intake.html`
  - `docs/TODO.md`

## 备注
- 本轮严格遵守 `1 个主点 + 1 个紧邻子点`：没有并开 Rank 110，也没有回头磨 `Rank 108`
- 当前工作区仍有大量无关脏文件；本轮未尝试混提
- 下一轮若 EMA 仍 waiting_not_due，默认只给 Rank 109 一次最小 clean replication，而不是继续打磨 intake 文案
