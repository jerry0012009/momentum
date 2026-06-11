# 2026-03-15 11:31 UTC — breakout future pure-down lead 审计

## 本轮目标
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 主点：继续围绕 `one_more_gate` 的 admission honesty，补一个 deployment-facing 小切片：
  - 不再只从 `down-risk zone` 视角看 coverage；
  - 反过来从 policy 自己“实际打到的小时”出发，检查它们离下一段 pure `down` 还有多远。
- 紧邻子点：把该证据写进 breakout 主报告与 `docs/TODO.md`，避免只留在脚本/CSV。

## 开始前检查（hygiene）
- 已先看 `git status --short` 与最近优化记录（最近主线仍连续在 breakout 的 admission gap）。
- 当前 worktree 存在大量与本轮无关的既有脏改动/未跟踪文件；本轮继续推进，但不混提无关改动。
- `pytrendline_event_validation_v3` 本轮未 reopen，仅作为历史背景，不作为主任务。

## 本轮完成的推进
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增审计函数：
   - `summarize_policy_future_pure_down_lead_audit(...)`
2. 新增三份 artifacts（20bps）：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_future_pure_down_lead_audit_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_future_pure_down_lead_audit_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_future_pure_down_lead_audit_compare_20bps.csv`
3. 在 breakout 主报告新增 deployment-facing 段落（非近义重写）：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新段落标题：`反过来从 policy 自己的受影响小时看：它离下一段 pure down 到底有多远？`
4. 更新 `docs/TODO.md` breakout 主线条目，追加 2026-03-15 11:31 UTC 的 `[x]` 结果记录。

## 关键结果（本轮新增）
来自 `avoid_fluctuating_future_pure_down_lead_audit_compare_20bps.csv`：

### default pair halfsize（对照 gate-only）
- `24h`: `0/44`
- `48h`: `0/44`
- `72h`: `13/44`（约 `29.55%`）
- `96h`: `14/44`（约 `31.82%`）
- 命中来源：`matched_test_hours = 0`，全部来自 `train × flat`。
- 最近 lead 约 `60h`（中位约 `66.5h`）。

### down+flat mixed-tail overlay（对照 default pair）
- `24h`: `0/37`
- `48h`: `0/37`
- `72h`: `5/37`（约 `13.51%`）
- `96h`: `12/37`（约 `32.43%`）
- 命中来源：`matched_test_hours = 0`，全部来自 `train × down+flat`。
- 最近 lead 约 `51h`（中位约 `78.5h`）。

## 对 breakout admission verdict 的影响
- 这轮把 blocker 进一步收紧为结构性读法：
  - 问题不只是 `down-risk zone` 里 `0 coverage`；
  - 更关键是当前 default/mixed policy 的 active hours 自身就离 pure `down` 太远（`24/48h` 仍全 `0/x`）。
- mixed-tail 因此仍不能被诚实地写成 near-down protective conditional gate。
- breakout 正式 verdict 继续维持：`shadow-admission queue / one_more_gate`。

## 最小验证
已运行：
```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
```
结果：成功（exit 0），并确认：
- 新 lead-audit CSV 已生成；
- breakout 主报告已出现对应新段落与数值（`0/44`、`0/37`、`13/44`、`12/37` 等）。

## 本轮相关变更文件
- `scripts/build_support_breakout_v0_reports.py`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_future_pure_down_lead_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_future_pure_down_lead_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_future_pure_down_lead_audit_compare_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `docs/TODO.md`

## 发布与邮件
- 本文件写完后执行：
  - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout未来下跌lead审计" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_1131_breakout-future-pure-down-lead-audit.md`
- 执行结果见本轮终端输出。

## git / 提交说明
- 当前仓库存在大量与本轮无关的既有脏改动与未跟踪文件。
- 本轮未提交，避免把无关改动混入；如需提交，应仅对本轮文件做 selective commit。
