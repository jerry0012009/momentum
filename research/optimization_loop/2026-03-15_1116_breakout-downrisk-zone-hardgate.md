# 2026-03-15 11:16 UTC — breakout down-risk-zone hard-gate 审计

## 本轮目标
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 主点：把当前 `one_more_gate` 里最硬的 admission gap（`down-tail coverage`）压成更 deployment-facing 的统一口径，避免继续停在近义 wording。
- 紧邻子点：把 `default pair halfsize` 与 `down+flat mixed-tail overlay` 放到同一口径下对照，回答 mixed-tail 到底能不能算“更诚实的 conditional policy”。

## 开始前检查（hygiene）
- 已先看 `git status --short`、`docs/TODO.md`、最近 breakout 连续轮次记录。
- 工作区存在大量与本轮无关的既有脏改动/未跟踪文件；本轮继续推进，但不混提无关改动。
- `pytrendline_event_validation_v3` 本轮未 reopen，仅作为历史证据背景。

## 本轮完成的推进
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增统一审计函数：
   - `summarize_pair_downrisk_zone_audit(...)`
2. 新增 `down-risk zone` 统一口径（`pure down + pre-down bridge`）并同框输出两条 policy：
   - default：`gate_only -> default_pair_halfsize`
   - mixed：`default_pair_halfsize -> downflat_mixed_tail_overlay`
3. 产出新 artifacts：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`
4. 在主报告新增 deployment-facing 段落（不是近义重写）：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新段落核心：把 blocker 直接压成 `down-risk zone` 后，default 与 mixed-tail 都仍是 `0` coverage。
5. 更新 `docs/TODO.md`：
   - 在 breakout 主线条目下补入本轮结果（2026-03-15 11:16 UTC）。

## 关键结果（本轮新增）
来自 `avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`：

- `default_pair_halfsize`（对照 `gate_only`）
  - `lead=12h`：risk-zone 命中 `0/74`（pure down `0/63`，bridge `0/11`）
  - `lead=24h`：risk-zone 命中 `0/86`（pure down `0/63`，bridge `0/23`）
- `downflat_mixed_tail_overlay`（对照 `default_pair_halfsize`）
  - `lead=12h`：risk-zone 命中 `0/74`（pure down `0/63`，bridge `0/11`）
  - `lead=24h`：risk-zone 命中 `0/86`（pure down `0/63`，bridge `0/23`）

### 本轮 verdict 收紧
- mixed-tail 这轮并没有把 near-down blocker 补成可放行的 conditional gate；
- 更诚实的读法是：mixed-tail 仍只能保留为 strict pure-test mixed pocket 的 shadow 观察项；
- breakout 正式 verdict 继续：`shadow-admission queue / one_more_gate`。

## 最小验证
已运行：
```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
```
结果：成功（exit 0）。

并确认：
- 新 CSV artifact 已生成；
- 主报告已出现 `down-risk zone` 新段落，且数值已落地为 `0/74`、`0/86` 等具体结果。

## 本轮相关变更文件
- `scripts/build_support_breakout_v0_reports.py`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `docs/TODO.md`

## 发布与邮件
- 已执行：
  - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - URL：`https://jp.jerrypsy.top/momentum/`
- 已执行：
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout下行风险区硬门槛审计" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_1116_breakout-downrisk-zone-hardgate.md`
  - 结果：发送成功（`Email sent to: 18810813576@163.com`）

## git / 提交说明
- 当前仓库有大量与本轮无关的脏改动与未跟踪文件；本轮不做提交，避免混入无关改动。
- 若后续需要提交，应仅对本轮文件做 selective commit。
