# breakout pre-down bridge audit

## 本轮目标
沿 `support_breakout_v0 / breakout-short follow-up` 主候选继续补 deployment-facing admission gap，但只做一个小而完整的切片：

- 不再重复 mixed-tail wording；
- 直接检查默认 `avoid_fluctuating + ETH+SOL pair halfsize` 能不能被解释成“虽然没命中 pure down，但至少会在 pure down 前几小时提前减仓”的 conditional policy。

这一步直接服务于当前 breakout 主问题：`one_more_gate` 到底还能不能被更诚实地放宽。

## 先看当前状态
- 先检查了 `git status --short`、最近 optimization loop 记录、`docs/TODO.md`、以及 `docs/AUTO_OPTIMIZATION_LOOP.md`。
- 当前 repo/worktree 存在大量与本轮无关的脏改动与未跟踪文件；按执行 hygiene，本轮继续推进，但不把这些无关改动混进本轮结论。
- breakout 当前主 blocker 仍是：
  - `pure-test tail` 证据偏薄；
  - `down-tail coverage = 0/100`；
  - mixed-tail 仍只配 `shadow-only`。

## 本轮实际动作
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增 `summarize_pair_predown_bridge_audit(...)`。
2. 新增 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_predown_bridge_audit_20bps.csv`
3. 在 `support_breakout_v0_h24` 主报告新增一节，专门回答：
   - 默认 `ETH+SOL pair halfsize` 是否可以被解释成“anticipatory / pre-down bridge protection”。
4. 更新 `docs/TODO.md`，把这轮结果记为已完成。

## 结果
### 结论
答案是否。

默认 `ETH+SOL pair halfsize` 现在不仅是 `down-tail coverage = 0/100`，而且连未来会滑进 pure `down` 的前置 bridge 小时也没有覆盖，因此**不能**被解释成“虽然没打到 pure down，但至少提前减仓”的 down-tail protection。

### 关键数字
来自 `avoid_fluctuating_eth_sol_pair_halfsize_predown_bridge_audit_20bps.csv`：

- 未来 `6h` 内会滑进 pure `down` 的 bridge 小时：`0/5` 命中
  - `gate-only` 该段累计约 `-2.05%`
- 未来 `12h` 内会滑进 pure `down` 的 bridge 小时：`0/11` 命中
  - `gate-only` 该段累计约 `-3.92%`
- 未来 `24h` 内会滑进 pure `down` 的 bridge 小时：`0/23` 命中
  - `gate-only` 该段累计约 `+1.12%`

### 最关键的 deployment 读法
- 样本里最关键的 pre-down bridge 是一整段 `validate × flat` 前置滑落；
- 在未来 `12h` 内就会接上 pure `down`；
- 这段 bridge 自身累计已经约 `-3.92%`；
- 但默认 pair candidate 对这整段仍是 `0/11` 命中。

所以当前 hard gap 需要写得更直白：

> breakout 默认主候选的缺口不只是“pure down 本身没碰到”，而是连样本里最接近 pure-down 的 anticipatory bridge 也没有 coverage。

## 对 breakout 主 verdict 的影响
- 本轮没有放宽 `one_more_gate`；
- 反而把一个潜在宽松解释关掉了：
  - 不能再把 default pair candidate 说成“提前减仓式”的 down-tail protection；
- breakout 当前更诚实的正式位置继续是：
  - `shadow-admission queue / one_more_gate`

## 修改文件
- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_predown_bridge_audit_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`

## 最小验证
已运行：

```bash
python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py
```

结果：成功（exit code 0），并确认：
- artifact 已生成；
- 报告页已出现 `pre-down bridge` 新段落与表格。

## 发布与邮件
- homepage index publish：已执行成功
  - 命令：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - URL：`https://jp.jerrypsy.top/momentum/`
- email：已发送成功
  - 命令：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout 前置下跌桥接审计" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_1103_breakout-predown-bridge.md`
  - 收件箱：`18810813576@163.com`

## git / 提交情况
本轮**未提交**。

原因：当前 `jerry/momentum` 工作区存在大量与本轮无关的既有脏改动与未跟踪文件，范围覆盖其他 research/docs/site/artifacts 路径；本轮为避免把无关改动混入，不做整仓提交。若后续需要提交，应只做安全的 selective commit，并仅纳入本轮相关文件。 
