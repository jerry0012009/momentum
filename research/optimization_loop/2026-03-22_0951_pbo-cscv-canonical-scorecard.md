# 2026-03-22 09:51 UTC · bot3 auto · Run3 / pbo-cscv honesty gate canonical-ish 离线实现

## 本轮按板执行
- 顶板要求：`Run 3 = 只选 1 个（当前：pbo-cscv honesty gate）`
- 本轮遵守“最多 1 个主点 + 1 个紧邻子点”：
  - **主点**：把前一轮 `proxy demo` 升成 **canonical-ish CSCV/PBO + DSR 离线 scorecard**。
  - **紧邻子点**：只在 `Rank 139 / thr=0.8` 这一个固定对象上跑 1 次，读它当前的 honesty 口径，不打开其他 Scout 候选。

## 本轮新增产物
- 脚本：`scripts/build_pbo_cscv_dsr_scorecard.py`
- 结果表：`reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_scorecard.csv`
- 元数据：`reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_meta.json`

## 这次实现了什么
相对上一轮只看 `half split + sharpe proxy` 的最小 demo，这轮补成了更像样的离线 honesty gate：
1. **CSCV / PBO**
   - 把 `Rank 139 trade_log.csv` 按时间切成 `8` 段；
   - 枚举 `8 选 4` 的对称 train/test 组合（共 `70` 组）；
   - 每组在 IS 上按 `Sharpe@6bps` 选赢家，再看它在 OOS 上的排名；
   - 由此得到 `PBO`（赢家掉进 OOS 下半区的比例）。
2. **DSR（离线近似）**
   - 对 `baseline / veto_opp_dir / confirm_same_dir_only` 三臂，输出：
     - `mean_net_6bps`
     - `sharpe_6bps`
     - `dsr_probability`
     - `skewness / kurtosis`
3. **工程口径**
   - 全程使用含 `12bps` roundtrip 成本后的净收益；
   - 仍明确标注为 **offline canonical-ish approximation**，不是库级严格统计包，但已比 proxy demo 更接近真正可复用的 honesty gate。

## 结果（只读 Rank 139 这一条）
### 1) hard read
- **PBO = 0.1714**
- **lambda_median = 0.75**
- **verdict = guard_passed**

按当前 desk 的朴素分层：
- `PBO < 0.2`：可以先视作 **honesty guard passed**；
- 这说明 `Rank 139 / thr=0.8` 当前不是那种“IS 挑赢家、OOS 经常直接掉进下半区”的典型过拟合爆雷对象。

### 2) 三臂对比（当前固定对象）
- `baseline`
  - `mean_net_6bps = -0.1549%`
  - `sharpe_6bps = -0.113`
  - `dsr_probability ≈ 0.004`
- `veto_opp_dir`
  - `mean_net_6bps = +0.3428%`
  - `sharpe_6bps = +0.268`
  - `dsr_probability ≈ 0.839`
- `confirm_same_dir_only`
  - `mean_net_6bps = +0.5370%`
  - `sharpe_6bps = +0.365`
  - `dsr_probability ≈ 0.881`
  - `cscv_selected_count = 64 / 70`
  - `avg_oos_rank_when_selected ≈ 1.09`

### 3) 人话结论
- 这轮更像把上一轮的“它看起来不像立刻爆雷”推进成了**有明确数字支撑的 honesty 读法**：
  - `confirm_same_dir_only @ 0.8` 不只是全样本均值最好；
  - 在大多数 CSCV 切法里，它在 IS 被选中后，OOS 排名通常仍靠前；
  - 所以当前至少可以说：**这条 gate 并不是靠一次样本好运才显得强。**
- 但也别过度解读：
  - 这里只对 **单一 family / 单一阈值 / 单一对象（Rank 139）** 做了离线检查；
  - 还没上升到“对整个 scout 候选池统一做 pooled honesty discount”的层级。

## 对 desk 的意义
- **主点**：`pbo-cscv honesty gate` 已经从“概念/source/proxy”推进到 **可复跑的 canonical-ish offline scorecard**。
- **紧邻子点**：在当前唯一测试对象 `Rank 139 / thr=0.8` 上，hard read 是 **guard_passed，不是明显 selection-bias 爆雷**。

## 下一步（留给后续，不在本轮展开）
若后续继续这条线，只建议做下面二选一中的一个：
1. 把这套 CSCV/PBO/DSR scorecard 接到更通用的 `family scorecard` 输出；
2. 或做 pooled multi-family 版本，避免只盯单一对象。

本轮不再打开第二个 Scout 候选，不再回头扩写 Rank139 近义研究。
