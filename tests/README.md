# Tests

- `unit/`：纯函数与规则测试（factors/signals/risk）
- `integration/`：模块协作测试（data -> strategy -> engine）
- `regression/`：固定数据集回测结果回归（防止收益曲线意外漂移）

## 维护建议
- 每新增一个核心策略参数，都补至少 1 条单元或回归测试。
