# 用 split-specific excess 重新排 breakout short 顺序：raw 升到第一，confirm_1 第二，confirm_2 第三

## 为什么这次选这个

这轮继续沿同一条 `pytrendline_event_validation_v3` 主线推进，而且只补一个很小但很关键的缺口：

**前几轮对 breakout short 的内部排序，主要还是建立在 raw mean / split-honesty 上；现在需要用更诚实的 split-specific excess 再排一次。**

原因很直接：
- raw return 为负，不代表它真的比同段无条件基线更差；
- 如果后续正式 OOS 要只先做 1 条，排序不能停留在 raw mean；
- 这一步可以直接决定谁先占用第一顺位 OOS 资源。

这轮最值得复用/借鉴的点是：**候选排序如果不经过“相对同段基线”的二次修正，很容易把“市场本来就弱”误判成“事件真的更有 alpha”。**

## 核心结论（中文摘要）

核心结论：**在把 `h24` 升级成 split-specific excess 之后，当前 breakout short 更诚实的顺序应修正为：`support_breakout_raw` → `support_breakout_confirm_1` → `support_breakout_confirm_2`。**

证据如何支持这个结论：**按 `validate / test` 的 `h24` 相对同段基线表现看，`support_breakout_raw` 的 `avg_excess_ret` 最负（约 `-1.79% / -1.31%`），而且两段都是 `4/4` 资产同向负 excess；`support_breakout_confirm_1` 次之（约 `-1.52% / -0.95%`，同样 `4/4` 负 excess）；`support_breakout_confirm_2` 虽然 validate 也很负（约 `-1.68%`），但 test 只剩约 `-0.73%`，且 `1/4` 资产转为正 excess。说明在 relative edge 视角下，`raw` 比 `confirm_1` 更像当前第一顺位候选。**

## 本轮做了什么改动

本轮只做一个主点：**用 split-specific excess 重新排 breakout short 顺序。**

具体动作：

1. 继续使用现有样本与缓存
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
   - `reports/artifacts/pytrendline_event_validation_v3/cache/*.csv`

2. 沿用现有全局 `60/20/20` 切分
   - `train / validate / test`

3. 只比较 breakout short 三档的 `h24`
   - `support_breakout_raw`
   - `support_breakout_confirm_1`
   - `support_breakout_confirm_2`

4. 重新为每个 split 计算 baseline，并输出相对 excess
   - `reports/artifacts/pytrendline_event_validation_v3_variant_excess_rank_v1/variant_h24_split_excess_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_variant_excess_rank_v1/variant_h24_split_excess_by_asset.csv`

5. 更新 `docs/TODO.md`
   - 把 breakout short 的第一顺位从 `confirm_1` 修正成 `raw`；
   - 并同步重建 `plans/momentum_todo.html`。

## 验证 / 证据

### 1) validate 段（h24）

- `support_breakout_raw`
  - `avg_excess_ret ≈ -1.79%`
  - `4/4` 资产负 excess
- `support_breakout_confirm_2`
  - `avg_excess_ret ≈ -1.68%`
  - `4/4` 资产负 excess
- `support_breakout_confirm_1`
  - `avg_excess_ret ≈ -1.52%`
  - `4/4` 资产负 excess

### 2) test 段（h24）

- `support_breakout_raw`
  - `avg_excess_ret ≈ -1.31%`
  - `4/4` 资产负 excess
- `support_breakout_confirm_1`
  - `avg_excess_ret ≈ -0.95%`
  - `4/4` 资产负 excess
- `support_breakout_confirm_2`
  - `avg_excess_ret ≈ -0.73%`
  - `3/4` 资产负 excess，`1/4` 转正

### 3) train 段提醒

- `support_breakout_raw`：`avg_excess_ret ≈ +0.07%`
- `support_breakout_confirm_1`：`avg_excess_ret ≈ +0.07%`
- `support_breakout_confirm_2`：`avg_excess_ret ≈ -0.11%`

这说明：
- train 段并没有给出“raw 明显更强”的干净证据；
- 当前排序更像是：**在 validate / test 这两个更重要的 OOS 段里，raw 的 relative edge 最强。**

## 风险 / 边界

- 这轮没有新增事件生成，只是把排序标准从 raw mean 升级成 split-specific excess；
- 样本仍小，所以排序仍应看作 first-pass priority，而不是最终 verdict；
- `raw` 升到第一，也不代表它最终一定优于 `confirm_1`，只是说明目前在 OOS relative edge 上更值得先验证。

## 下一步建议

1. 如果下一步只做一个正式 OOS 主对象，当前最合理的是：
   - `support_breakout_raw @ h24`
2. 第二顺位：
   - `support_breakout_confirm_1 @ h24`
3. 第三顺位：
   - `support_breakout_confirm_2 @ h24`
4. 当前不建议再沿用“confirm_1 第一”的旧排序，而不经过 split-specific excess 复核。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。