# 把 EMA / PSAR 成本结论补回 closure board

## 为什么这次选这个

这轮没有继续去开新验证，而是沿着上一轮刚补好的 `EMA / PSAR` 成本页，再往前走半步：把那份结论正式补回 `alpha_closure_board` 总览页。

原因很简单：
1. 上一轮虽然已经把成本段挂回了 `EMA / PSAR Raw Alpha Focus` 主报告，但 Jerry 如果只看 closure 入口页，还看不到这条新结论；
2. 当前自动化被要求“尽量把结果落实到网页主入口/closure 入口”，所以这轮最小而高价值的动作，就是把成本信息补回总览口径；
3. 这也是一个足够小、不会重跑重型数据、但会直接影响“接下来先做什么”的 framing 更新。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 把 `EMA / PSAR raw alpha focus` 卡片里的“当前最强证据”改成包含成本页结论；
   - 明确写入：
     - `EMA` 的 positive-only median breakeven round-trip cost 约 `383.2bps`
     - `PSAR` 约 `300.9bps`
     - 到 `60m`，`EMA` 扣 `20bps` 后仍约 `4/9` 组合存活，`PSAR` 只剩约 `2/9`
   - 相应把“当前不能过度解读什么 / 下一步最值得做什么”收紧为：
     - 现在真正缺的是 `rolling / OOS honesty`
     - 以及 `EMA + PSAR` 最小组合验证
2. 重建 `reports/site/factors/alpha_closure_board/report.html`
   - closure board 现在不再只是复述旧 gross 结果，而是会直接把成本层读法带进总览排序；
3. 更新 `docs/TODO.md`
   - 在 `comparison / decision board` 这条未完成任务下补一条最新进度说明，明确当前更稳的项目级排序：
     - `EMA` 继续作为 `raw alpha baseline candidate`
     - `PSAR` 更适合作为 `fast reaction / protective layer`

## 验证 / 证据

### 1) closure board 已正式接入成本结论

`reports/site/factors/alpha_closure_board/report.html` 中，`EMA / PSAR raw alpha focus` 卡片现在已明确写入：
- `EMA` 成本缓冲约 `383.2bps`
- `PSAR` 成本缓冲约 `300.9bps`
- `60m` 下 `EMA @20bps` 约 `4/9` 存活，`PSAR @20bps` 约 `2/9`

### 2) 这让 closure 页的“下一步”更具体了

现在 closure board 上对这条线的默认 next step 已从泛泛的“补更多完整回测”收紧为：
1. 先补 `EMA` 的 `rolling / OOS honesty`
2. 再做 `EMA + PSAR` 最小组合页

这比之前更有利于 bot2 / Jerry 直接判断下轮该把时间投到哪一刀。

### 3) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`

结果：
- 成功生成 closure board 页面；
- 页面内容已能检索到新的成本描述与更新后的 next-step framing。

## 风险 / 边界

1. 这轮没有新增回测或新数据，只是把上一轮已经得到的成本结论补回上位总览页；
2. 因此它属于 **closure framing 推进**，不是新的实证验证；
3. 成本结论本身仍是基于上一轮 first-pass 线性近似，不应误读成正式逐笔 net 回放已经完成。

## 下一步建议

若继续沿这条线推进，下一小步最值得做的是：
1. `EMA rolling / OOS honesty` 页；
2. `EMA + PSAR` 最小组合页；
而不是再重复补 gross 层解释。

## Commit

本轮**未提交**。

原因：当前 repo worktree 在本轮涉及路径上已存在早于本轮的未提交改动（尤其 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html` 本身就是 dirty），此时做 selective commit 仍无法确保只打包本轮单独变更。