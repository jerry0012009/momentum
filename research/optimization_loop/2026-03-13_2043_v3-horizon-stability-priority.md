# 用现有 v3 artifacts 做 horizon stability 小审计：先给 breakout short 做 OOS，rebound long 暂降一级

## 为什么这次选这个

这轮没有再重跑大样本，也没有继续补外部来源，而是回到当前更像真实 alpha 主线的 `pytrendline_event_validation_v3`，用现成 artifacts 做一个很小但有决策价值的动作：**horizon stability 小审计**。

原因很简单：
- v3 现在已经有一批候选，但还没正式进入 OOS；
- 如果不先回答“谁更稳定、谁更值得先吃 OOS 资源”，下一步就容易同时开太多支线；
- 当前用现有 `event_excess_summary.csv / family_excess_summary.csv` 就能完成这个判断，成本低、信息量高。

这轮最值得复用/借鉴的点是：**在 OOS 之前，先用已有 horizons（h6/h24/h48/h72）做 sign / excess 稳定性筛一遍，比直接把所有 shortlist 一起推进 OOS 更能节省研究资源。**

## 核心结论（中文摘要）

核心结论：**基于当前 `pytrendline_event_validation_v3` 的 horizon stability 小审计，下一步应优先把 OOS 资源给 breakout short 这条线（尤其 `support_breakout_confirm_2` / broader support_breakout family），而不是先给 `support_rebound_confirm_1`。**

证据如何支持这个结论：**`support_breakout_confirm_2` 在 `h6 / h24 / h48 / h72` 的 `avg_excess_ret` 全部为负（约 `-0.62% / -0.61% / -1.30% / -1.37%`），且 `consistency` 保持在 `0.75~1.0`；`support_breakout_raw` 甚至在四个 horizons 都保持 `consistency = 1.0` 的负向 excess。相比之下，`support_rebound_confirm_1` 只有 `h24` 出现微弱正 excess（约 `+0.015%`），而 `h6 / h48 / h72` 仍为负，不够稳定。说明当前更像“该先过 OOS honesty”的，是 breakout short，而不是 rebound long。**

## 本轮做了什么改动

本轮只做一个主点：**用现有 v3 artifacts 做 horizon stability priority audit。**

具体动作：

1. 读取现有 artifacts
   - `reports/artifacts/pytrendline_event_validation_v3/event_excess_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3/family_excess_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3/alpha_shortlist_h24.csv`
   - `reports/artifacts/pytrendline_event_validation_v3/summary.json`

2. 重点对比三类对象
   - `support_breakout_confirm_2`
   - broader `breakout_short` family（至少看 `support_breakout_raw` / `support_breakout_confirm_2`）
   - `support_rebound_confirm_1`

3. 将结论写回 `docs/TODO.md`
   - 在 `V3X-E. OOS / 防过拟合验证` 下补进度说明：
     - breakout family 单独 OOS 现在应优先；
     - `support_rebound_confirm_1` 下调为 second-pass OOS。

4. 最小重建镜像页
   - 重建：`reports/site/plans/momentum_todo.html`
   - 同步到：`/var/www/momentum-report/plans/momentum_todo.html`

## 验证 / 证据

### 1) breakout short 候选的 horizon stability

#### `support_breakout_confirm_2`
- `h6`：`avg_excess_ret ≈ -0.625%`，`consistency = 1.0`
- `h24`：`avg_excess_ret ≈ -0.610%`，`consistency = 0.75`
- `h48`：`avg_excess_ret ≈ -1.296%`，`consistency = 0.75`
- `h72`：`avg_excess_ret ≈ -1.373%`，`consistency = 1.0`

#### `support_breakout_raw`
- `h6`：`avg_excess_ret ≈ -0.485%`，`consistency = 1.0`
- `h24`：`avg_excess_ret ≈ -0.621%`，`consistency = 1.0`
- `h48`：`avg_excess_ret ≈ -0.954%`，`consistency = 1.0`
- `h72`：`avg_excess_ret ≈ -0.721%`，`consistency = 1.0`

这说明：
- breakout short 这条线不只是 `h24` 好看；
- 它在多个 horizons 上都维持了同号的负 excess；
- 因而更像值得先过 OOS honesty 的真实候选。

### 2) support rebound long 候选的 horizon stability

#### `support_rebound_confirm_1`
- `h6`：`avg_excess_ret ≈ -0.456%`
- `h24`：`avg_excess_ret ≈ +0.015%`
- `h48`：`avg_excess_ret ≈ -0.665%`
- `h72`：`avg_excess_ret ≈ -0.351%`
- `consistency`：`1.0 / 0.75 / 1.0 / 0.5`

这说明：
- 它当前只有 `h24` 给出微弱正 excess；
- 一旦拉到其他 horizons，方向并不稳定；
- 所以它更像保留观察位，而不是当前第一顺位的 OOS 对象。

### 3) 一个容易误判的对象：`resistance_breakout_confirm_1`

- 它在 `h24` 上相对基线很亮眼：`avg_excess_ret ≈ +0.834%`，`consistency = 1.0`；
- 但到 `h48 / h72`，绝对收益已经转负，只剩 relative excess 仍为正；
- 说明它可能更像“相对抗跌/少跌”而不是稳定 continuation alpha。

因此当前更合理的资源顺序不是“先追 h24 最亮的点”，而是“先追跨 horizon 更稳定的一条线”。

## 风险 / 边界

- 这轮没有新跑实验，只是基于现有 artifacts 做 priority audit；
- horizon stability 不是 OOS 的替代品，只是 OOS 之前的筛选器；
- breakout short 现在优先级更高，不等于它已经通过了 honesty validation；
- rebound long 现在优先级下调，也不等于永久放弃，只是当前证据还不够稳定。

## 下一步建议

1. 下一小步最值得做的是：
   - 按当前结论，先给 `support_breakout_confirm_2 / breakout short family` 做单独 OOS；
2. `support_rebound_confirm_1` 则放到 second-pass OOS：
   - 若 breakout short 过不了 OOS，再回头重新评估它；
3. 当前不建议把 OOS 资源先花在“只有某个单一 horizon 看起来好”的对象上。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件与 TODO 镜像同步，不做提交。