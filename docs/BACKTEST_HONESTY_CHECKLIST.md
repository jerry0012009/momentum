# Backtest Honesty Checklist

这份清单不是只给 `Rank29` 用的。

它是给后续所有 `Rank` 系列策略的一个**防自欺最小检查表**：

> 在讨论“这个策略能不能升格”之前，先确认我们看的不是事后重写过的漂亮历史图。

---

## 0. 什么时候必须触发 honesty audit

只要策略里出现下列任意一种，就默认要做：

- pivot confirmation
- trendline / support-resistance line
- HH / LL / structure switch
- segment lifecycle
- state machine 会在后面 bar 才确认前面状态
- regime 标签会回填到历史 bars
- label 依赖未来窗口（如 future bucket / later confirmation / delayed pattern close）

一句话：

> **凡是“后面多看几根 bar，前面状态会变得更清楚”的地方，都不能直接默认可交易。**

---

## 1. 先把两种口径分开

每个策略都尽量保留两套结果：

### A. hindsight / explanatory
用途：
- 看结构
- 画图
- 做解释
- 帮人理解“后来为什么长成这样”

### B. strict-causal / tradable
用途：
- 回测基准
- 策略晋级
- paper / live admission
- 成本与稳定性评估

规则：

- **可以保留 hindsight 图**
- **不能用 hindsight 结果证明策略已验证有效**

---

## 2. 每个关键点至少要有两个时间字段

如果策略里有 pivot / swing / segment / breakout anchor，尽量显式记录：

- `origin_time`
- `confirmed_at`

或者至少要能从数据里推出：

- 这个点落在哪根 bar
- 我是在哪根 bar 才真的知道它成立

如果页面只展示 `origin_time`，但不展示 `confirmed_at`，就非常容易误导人。

---

## 3. 对任何 baseline，先跑一次“污染比例”

最小做法：

- 旧口径结果 = `old_signals`
- causal 结果 = `causal_signals`
- 差集 = `hindsight_only`
- 计算：

```text
misleading_pct = hindsight_only / old_signals
```

经验上：

- `0% ~ 5%`：通常还能继续往下看
- `5% ~ 20%`：需要明确披露，谨慎读
- `20% ~ 50%`：已经不能直接把旧回测当基准
- `>50%`：应优先停下来重做 baseline
- `≈100%`：旧结论基本失效

---

## 4. 检查顺序不要反

正确顺序：

1. **baseline honesty**
2. **no-overlap / hold logic honesty**
3. **cost sensitivity**
4. **time stability**
5. **regime / overlay / gate**
6. **paper / live admission**

不要先做：
- 很复杂的 regime gate
- 漂亮的 monthly panel
- 多层 shadow
- live debug

然后最后才发现 baseline 本身不诚实。

---

## 5. 常见危险信号

如果你看到下面这些现象，要立刻怀疑 future leak：

- 历史信号很多，实盘几乎接不到
- 图上星号很密，但真实 runner 经常判成 expired / stale
- 某些线总是“事后看非常完美”
- 第二个点总在 signal 后面才长出来
- 时间稳定性很好，但真实样本数量非常少
- 加了很多 overlay 之后看起来越来越强，但 baseline 本身解释不清

---

## 6. 页面上应该怎么标

如果页面既展示结构，又展示信号，建议显式区分：

- `causal signal`
- `hindsight-only signal`

并尽量把：
- `line_value`
- `close`
- `anchor / pivot`
- `confirmed_at`

分开画或分开列。

目标不是把图画得更漂亮，目标是：

> **让人一眼看出“这个点是当时就能交易”，还是“事后才知道”。**

---

## 7. 晋级门槛建议

一个策略要讨论从 research → paper / live，至少满足：

### 最低门槛
- causal baseline 为正
- 不是靠极少数样本撑起来
- misleading ratio 足够低
- 关键资产 / 时间切片不是全面塌陷

### 若不满足
建议：
- 降级为 research
- 标记 archived / needs redesign
- 不要继续用旧 headline 对外或对内背书

---

## 8. 一句最重要的话

以后任何人拿来一张很好看的策略图，先别急着问：

- 收益多少？
- 夏普多少？
- 要不要上 paper？

先问：

> **这条信号，在当时那根 bar 上，真的是当时就能知道的吗？**

如果这句答不稳，后面所有数字都得打折。 
