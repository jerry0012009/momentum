# breakout mixed-tail episode honesty

## 为什么这次选这个
- 这轮继续遵循当前 breakout 主线优先级：不再平均推进三条线，默认先补最接近 `admission / shadow paper` 判断的缺口。
- 上两轮已经把默认 `ETH+SOL pair halfsize` 说明白：pure-test 前半段只有 very thin edge，最后两小时 `down+flat mixed-tail` 才补出更多增量。
- 因此这轮最小但完整的一刀，应该继续回答：`mixed-tail overlay` 自己到底能不能被更诚实地写成 conditional gate，还是仍主要靠训练段 carry + 单段 test pocket 撑着。

## 做了什么改动
1. 在 `scripts/build_support_breakout_v0_reports.py` 里，把 `pair + down+flat mixed-tail overlay` 的受影响小时接入现成的 `episode decomposition` 汇总，新增 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_episode_summary_20bps.csv`
2. 在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增一段 deployment-facing 解释：
   - 把 mixed-tail overlay 的 `37` 个受影响小时按真实时间顺序压成 `3` 段 episode；
   - 明确区分 `train × down+flat` 与 `test × down+flat` 的贡献占比；
   - 直接回答这刀目前更像 `shadow-only mixed gate`，还不是可晋级的 admission patch。
3. 在 `docs/TODO.md` 里补了一条已完成记录，避免下一轮重复做近义 wording。
4. 重新生成：
   - `support_breakout_v0_h24` 主报告
   - `plans` 站点页（让 TODO 更新可见）

## 验证 / 证据
- 运行通过：
  - `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
  - `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 新 artifact 结果显示，mixed-tail overlay 当前只会塌成 3 段：
  - `train × down+flat`：5h，条件改善约 `+0.03pp`
  - `train × down+flat`：7h，条件改善约 `+0.53pp`
  - `test × down+flat`：25h，条件改善约 `+0.26pp`
- 加总后，当前 mixed-tail overlay 的总 conditional delta 约 `+0.81pp`：
  - `train` 两段合计约 `+0.55pp`，约占 `68.22%`
  - `test` 那一段约 `+0.26pp`，约占 `31.78%`
- 这说明 mixed-tail 不是完全没有 forward 方向，但目前仍不是“多段 pure-test honesty 已成立”的状态；更诚实的表述仍应是：`shadow-only mixed gate`。

## 风险 / 边界
- 这轮没有把 breakout verdict 往前推进到 `shadow paper now`；结论反而更收紧：mixed-tail 现在仍主要靠训练段 carry 支撑。
- `down-tail coverage = 0/100` 这个 hard gap 没有被这轮修掉；因此它仍不能替代默认 `pair halfsize` 主候选，也不能解除 `one_more_gate`。
- 本轮只补了 `mixed-tail overlay` 的 episode honesty，不等于补齐更长的真实 forward / live-like admission 证据。

## 下一步建议
- 若下一轮继续 breakout，优先顺序仍应是：
  1. 继续沿 `default pair halfsize` 主候选补更硬的 `pure-test / down-tail honesty`
  2. 或继续回答 mixed-tail 是否能在更长、更多段的 forward 条件下复现，而不是继续堆 wording
- 若 breakout 暂时没有更硬的新 slice，可切回 EMA 的 `paper-trading runbook`，但不要再新增近义 board 页面。

## Commit hash
- 未提交。

## 为什么未提交
- 当前 `jerry/momentum` 工作区存在大量与本轮无关的脏文件与未跟踪产物；本轮虽然完成了自己的最小切片，但不适合把无关改动一起打包提交。
- 这轮已明确只改动并刷新了与 breakout mixed-tail episode honesty 直接相关的脚本 / 报告 / TODO / 站点页，未混提其它主题改动。
