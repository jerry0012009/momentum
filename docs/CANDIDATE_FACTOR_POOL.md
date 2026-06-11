# 候选因子池说明（Candidate Factor Pool）

> 目标：把当前 `momentum` 项目里已经做过、正在做、准备做的研究对象，统一整理成一个**可分层、可排序、可复刻**的候选池。
>
> 这份文档回答 3 个问题：
> 1. 为什么现在要做候选因子池；
> 2. 候选池与当前项目结构怎么对应；
> 3. 每个候选因子以后应该按什么格式进入 backlog / 回测 / 报告。

---

## 1. 为什么现在做这件事

当前阶段已经完成了一轮“概念收束 + 最小模板实证”：

- `multi_tf_momentum` 已经落地并完成 cross-market / rolling 视角的初步认识；
- `ema_donchian_breakout` 已经完成单市场、参数扫描、OOS、rolling、crypto vs other；
- `trend_regime_filter` 与 `market_risk_on_off_filter` 已完成 first baseline；
- `price_volume_divergence`、`pullback_recovery_confirmation` 也已有独立研究页。

因此当前最不该做的事，是继续围绕单个 baseline 做无边界调参；
当前最该做的事，是把已有研究对象整理成一个**分层清楚、优先级明确**的候选池，再决定下一轮只复刻 1~2 个高优先级对象。

一句话：

**文献给思想，候选池给研究队列。**

---

## 2. 候选因子池与项目结构如何对应

当前项目里，一个候选因子通常对应下面这些位置：

### 2.1 信号定义层
- 路径：`src/momentum/signals/`
- 作用：定义信号/过滤器/门控本身的规则
- 示例：
  - `multi_tf_momentum.py`
  - `ema_donchian_breakout.py`
  - `trend_regime_filter.py`
  - `market_risk_on_off_filter.py`
  - `price_volume_divergence.py`
  - `pullback_recovery_confirmation.py`

### 2.2 回测/评估层
- 路径：`src/momentum/analytics/`
- 作用：把信号变成可统计的交易结果
- 当前已存在的专用回测模块：
  - `multi_tf_momentum_backtest.py`
  - `ema_donchian_breakout_backtest.py`
- 说明：不是每个候选都必须立刻有独立 analytics 文件；初期也可先由 `scripts/build_*_report.py` 负责实验与统计。

### 2.3 实验脚本与网页报告层
- 路径：`scripts/build_*_report.py`
- 产物：
  - `reports/artifacts/<factor>/`
  - `reports/site/factors/<factor>/report.html`
- 作用：完成一次研究闭环：定义 → 运行 → 汇总 → 图表 → 网页结论

### 2.4 说明文档层
- 路径：`docs/SIGNALS_*.md`
- 作用：记录一个候选因子的定义、参数、解释、风险点

### 2.5 队列与优先级层
- 路径：`docs/FACTOR_BACKLOG.md`
- 作用：统一回答：
  - 这个候选属于哪一层；
  - 当前证据强不强；
  - 是否值得进入下一轮高质量复刻。

---

## 3. 候选池不是“指标列表”，而是“系统分层列表”

以后一个新想法，先不要问“像不像指标”，先问它属于哪一层：

1. **方向过滤**：决定偏多 / 偏空
2. **触发**：决定什么时候开枪
3. **确认增强**：决定这个触发值不值得信
4. **出场**：决定什么时候平仓
5. **风险控制**：决定亏多少、仓位多大
6. **环境门控**：决定今天整套系统要不要开机

这一步非常关键，因为同样叫“信号”的东西，实际在系统里可能扮演完全不同的角色。

---

## 4. 每个候选因子的标准记录卡片

以后一个候选因子进入研究队列，最少要记录下面 8 项：

1. **名字**
2. **所属层级**（方向过滤 / 触发 / 确认增强 / 出场 / 风险控制 / 环境门控）
3. **核心假设**（它为什么可能有效）
4. **可计算定义**（公式/规则/阈值）
5. **适用市场 / 周期**（crypto / 股票；`1m / 3m / 5m / 15m / 1h`）
6. **常见失效方式**
7. **与当前模板如何组合**
8. **复刻优先级**（P0 / P1 / P2）

如果一个候选连这 8 项都说不清，就不应该进入正式复刻队列。

---

## 5. 候选因子的状态定义

建议统一使用下面这些状态：

- `IDEA`：只有概念，还没具体定义
- `SCOPED`：已经能说清定义、层级、失效方式
- `PROTOTYPED`：已经有代码或实验脚本
- `REVIEWED`：已经有报告、图表、结论
- `KEEP`：值得保留在主候选池
- `DROP`：现阶段证据弱，不继续投入
- `PARKED`：不是当前主线，但保留以后再看

说明：
- `PROTOTYPED` / `REVIEWED` 说的是工程/实验完成度；
- `KEEP` / `DROP` / `PARKED` 说的是研究决策。

---

## 6. 当前项目的候选池分层（v0.1）

> 这里只给框架，不替代 `docs/FACTOR_BACKLOG.md` 的优先级表。

### 6.1 方向过滤
- 多周期动量（`multi_tf_momentum`）
- EMA 结构（已在 `ema_donchian_breakout` 中作为方向层出现）
- MA slope（未正式单列实现）

### 6.2 触发
- Donchian breakout
- Pullback recovery confirmation（回踩恢复）
- Endpoint NWE + confirmed extrema foundation（平滑 + 极值确认底层）
- Box consolidation breakout（箱体/窄幅突破，当前偏旁支）

### 6.3 确认增强
- 连续收盘确认（已在 `ema_donchian_breakout` 中出现）
- 缩量回调后恢复
- 放量恢复确认
- 成交量异常确认（`vol_z` 类）
- Price-volume divergence（偏弱证据，当前不宜过度押注）

### 6.4 出场
- ATR stop（已在 `ema_donchian_breakout` 学习模板中使用）
- trailing stop（理论已掌握，尚未独立做实验队列）
- 时间出场（未单列）
- 反向信号出场（未单列）

### 6.5 风险控制
- ATR position sizing（当前高优先级待补）
- 波动率分位过滤 / 高低波动过滤
- 最大单笔风险约束 / 熔断（后续工程层）

### 6.6 环境门控
- Trend/choppy gate（已完成 first baseline）
- Market risk-on / risk-off gate（v1 已完成）
- 高波动停机（可从 vol regime filter 演化）
- 流动性门槛（后续可加）

---

## 7. 当前研究节奏建议

当前建议采用下面的节奏：

### Phase B：文献扫描 + 因子家族归档
- 从经典趋势/动量/风险管理文献抽取“因子家族”，不是抄参数
- 把每个家族翻译成可编码对象

### Phase C：候选池排序
- 只给候选打标签，不急着全做
- 当前优先看：是否适合短周期（默认 `5m/15m`，也接受 `1m/3m`）、是否更偏 crypto、是否已有可组合模块

### Phase D：高质量单因子复刻
- 每次只推进 1~2 个高优先级对象
- 固定口径：净收益、最大回撤、成本后收益、cross-market / OOS / rolling（按阶段补）

### Phase E：组合层验证
- 单因子先证明自己不是纯噪音
- 再考虑组合，不跳步

---

## 8. 当前第一批建议重点关注的候选（适合下一轮）

### P0（最优先）
- EMA 结构（方向过滤）
- Donchian breakout（触发）
- Pullback recovery confirmation（确认增强 / 二次进场）
- ATR position sizing（风险控制）
- Volatility regime filter（环境/风险边界）
- Endpoint NWE + confirmed extrema foundation（结构识别底层 / 非 alpha 成果）

### P1（第二梯队）
- MA slope（方向过滤）
- Volume spike / volume recovery confirmation（确认增强）
- trailing stop 变体（出场）
- market risk-on / risk-off gate 的下一版（环境门控）

### P2（先保留，不急）
- Price-volume divergence 的更复杂变体
- Swing-point divergence
- Box consolidation / up-down wave 等非当前主线对象

---

## 9. 使用方式（以后怎么落地）

以后每发现一个新对象：

1. 先放进 `docs/FACTOR_BACKLOG.md`
2. 明确它属于哪一层
3. 写清核心假设与失效方式
4. 如果值得做，再补：
   - `docs/SIGNALS_<factor>.md`
   - `src/momentum/signals/<factor>.py`
   - `scripts/build_<factor>_report.py`
   - `reports/artifacts/<factor>/`
   - `reports/site/factors/<factor>/report.html`

也就是说，候选池是**研究入口**，不是最终报告本身。

---

## 10. 当前结论（简版）

- 现在做候选因子池，是为了避免继续围绕单个 baseline 炼丹；
- 候选池要按“系统层级”分，而不是按“指标名字”堆；
- 当前 `momentum` 项目已经有足够多的原型与报告，适合进入“候选池排序”阶段；
- 下一轮研究应从 `docs/FACTOR_BACKLOG.md` 里只挑 1~2 个高优先级对象推进。
