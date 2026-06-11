# 2026-03-15 06:14 UTC — breakout strict pure-test tail honesty

## 本轮主点
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 子点：把默认 `ETH+SOL pair-conditioned halfsize` 再压成 **strict pure-test tail honesty**，回答它在最严格的后段 admission 视角下是否仍站得住。

## 为什么选这个
- 按当前 steering，EMA 线若没有新的 forward / holdout / promotion honesty，就不再继续补近义 board。
- breakout 线当前最接近 deployment-facing 的缺口，已经收窄到：
  1. `late-segment / pure-test transferability`
  2. `down regime tail`
- 上两轮已补了 non-overlap `5d / 10d` forward blocks；这轮继续把口径再收紧一刀，避免继续只在“late-segment 大体站得住”这一层绕圈。

## 本轮实际推进
### 1) 新增 strict pure-test tail 指标与产物
在 `scripts/build_support_breakout_v0_reports.py` 新增 `summarize_hourly_pair_tail_snapshot()`，专门汇总：
- 从首个 pure `test` sizing 触发开始
- 到样本末尾为止
- gate-only vs default `ETH+SOL pair halfsize`
- 整段 portfolio tail 的累计收益 / 回撤 / 条件 pocket 改善

新产物：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_20bps.csv`

核心结果：
- strict pure-test tail 起点：`2026-03-06 00:00 UTC`
- 样本末尾：`2026-03-09 03:00 UTC`
- 整段 active hours：`30`
- 实际触发 halfsize 的 hours：`5`
- gate-only tail cumulative net：`-1.02%`
- halfsize tail cumulative net：`-0.25%`
- delta vs gate：`+0.77pp`
- drawdown improve：`+0.21pp`
- 受影响小时 regime 组成：`up=3 / down+flat=2 / pure down=0`

### 2) 把新证据落到 breakout 主报告页
已更新：
- `reports/site/factors/support_breakout_v0_h24/report.html`
- 对应脚本：`scripts/build_support_breakout_v0_reports.py`

新增内容：
- 单独一节解释 strict pure-test tail 的含义
- 明确写出：
  - 这比“只看 5 个被动到的 test 小时条件累计”更硬，因为它看的是整段 tail 的 portfolio path
  - 但它仍只有 `30` 小时，而且 `pure down = 0`
  - 所以它只能说明 pure-test 方向**暂时没翻负**，还**不足以单独清掉 `one_more_gate`**

### 3) 同步 closure / board / TODO
已更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

同步后的项目级读法：
- breakout 默认 candidate 的一般性 late-segment transferability 焦虑继续下降
- strict pure-test tail 也暂时为正
- 但 admission blocker 仍没有变：
  - `pure-test` 证据仍薄
  - `down-tail` 仍几乎没被真正碰到（`pure down = 0`）
- 因此 breakout 当前仍应停在：`needs one more gate / one_more_gate`

## 对当前 deployment / admission 的影响
本轮最重要的不是把 breakout 升格，而是把“为什么还不能升格”压得更硬：

- 现在已经不太像“默认 halfsize 只是 late-segment lucky patch”
  - `5d` non-overlap：`3/4` 改善
  - `10d` non-overlap：`2/2` 改善
  - strict pure-test tail：也仍有 `+0.77pp`
- 但它依然还不是 `shadow paper now`
  - strict pure-test tail 只是一段 `30h` 小尾巴
  - 真正被动到的 pure-test pocket 只有 `5h`
  - `pure down = 0`

所以本轮后的更硬 verdict 是：
- **breakout = shadow-admission candidate, but still `one_more_gate`**
- 下轮若继续 breakout，默认优先补：
  1. `down regime tail honesty`
  2. 更贴近真实 shadow 运行的前瞻观察
- 而不是再补近义 board / wording

## 修改文件
- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`

## 验证
已执行：
```bash
python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py /root/clawd/jerry/momentum/scripts/build_plans_site.py
python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py
python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py
python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py
```

并额外抽查：
- 新 CSV 已生成，数值为 `30h / 5h / -1.02% / -0.25% / +0.77pp`
- `support_breakout_v0_h24/report.html` 已出现 `strict pure-test tail` 新节与 admission 更新
- `TODO.md` 与 `plans/momentum_todo.html` 已同步出现 `2026-03-15 06:05 UTC` 的这条补充

## git / 提交说明
本轮未提交。

原因：当前 `git status --short` 显示工作区存在大量与本轮无关的既有脏改动与未跟踪文件（涵盖 EMA、trendline、site、artifacts、workspace 其他目录等）；按要求，本轮不应把这些无关改动混进同一次提交。若后续需要提交，应只做安全的 selective commit。

## 邮件
- 按要求发送到默认收件箱
- 主题：`[momentum-auto] breakout strict pure-test tail 诚实度`
