# 警讯

## 目录

- `shallow module`
- `information leakage`
- `temporal decomposition`
- `overexposure`
- `pass-through method`
- `special-general mixture`
- `conjoined methods`
- `nonobvious code`
- `concept explosion`
- `read-model-as-source-of-truth`
- `responsibility-boundary-turned-class`

## `shallow module`

定义：

- 接口几乎和实现一样复杂。

常见伪装：

- 很小的 wrapper，却暴露很多选项或方法。

下一步追问：

- 它应该合并进更深的模块，还是围绕更高层接口重新设计？

## `information leakage`

定义：

- 同一个设计决策出现在多个模块里。

常见伪装：

- 重复解析逻辑、重复策略检查、重复假设同一种数据形状。

下一步追问：

- 哪个模块应该拥有这份知识，让其他模块不再需要知道它？

## `temporal decomposition`

定义：

- 结构按执行顺序拆开，而不是按隐藏知识拆开。

常见伪装：

- 一个类读取，一个类解析，一个类验证，但它们都必须知道同一种结构。

下一步追问：

- 这些步骤真的是不同抽象，还是同一个责任被按时间切开了？

## `overexposure`

定义：

- 接口把罕见行为暴露给了所有调用方。

常见伪装：

- 大量参数、flag 或开关，而大多数调用方其实不该关心它们。

下一步追问：

- 常见情况能不能成为默认行为，罕见情况能不能下沉？

## `pass-through method`

定义：

- 方法主要把参数原样转发给另一个同抽象层的方法。

常见伪装：

- 薄 wrapper 几乎没有增加知识、策略或简化。

下一步追问：

- 这一层创造了新抽象吗？还是调用方应该直接使用下层？

## `special-general mixture`

定义：

- 特殊场景行为混进了通用抽象。

常见伪装：

- 条件很多的代码，把当前某个 workflow 硬编码进 reusable module。

下一步追问：

- 什么属于通用抽象？什么应该留在特殊场景代码里？

## `conjoined methods`

定义：

- 两个方法依赖过紧，理解一个必须同时理解另一个。

常见伪装：

- 共享隐藏状态、强顺序耦合、一个方法为另一个方法设置隐形条件。

下一步追问：

- 这些责任应该合并，还是围绕更清楚的抽象重新设计？

## `nonobvious code`

定义：

- 快速阅读不足以理解代码含义或为什么能工作。

常见伪装：

- 泛型容器、模糊命名、意外行为、隐藏约定。

下一步追问：

- 不明显是因为抽象弱、命名弱，还是缺少关键说明？

## `concept explosion`

定义：

- 一个设计为了表达边界而引入大量新名词、类型、DTO、service 或事件。

常见伪装：

- 每个职责边界都被实现成同名对象，读模型被拆成许多小 schema。

下一步追问：

- 哪些只是职责边界？哪些必须存在于代码？能否压平、合并或延后？

## `read-model-as-source-of-truth`

定义：

- API 或 UI 读模型被误当作持久化事实源、领域对象或业务模块之间的内部传递对象。

常见伪装：

- 把 response snapshot 存进数据库，或让核心逻辑依赖展示字段。

下一步追问：

- 真正的事实状态在哪里？读模型能否只在 API 边界临时组装？

## `responsibility-boundary-turned-class`

定义：

- 为了说明 owner 而命名的职责边界，被过早实现成 class、DTO、service 或 adapter。

常见伪装：

- 某个对象只有一个转发方法，或只保存调用方已经知道的状态。

下一步追问：

- 模块内函数、私有方法或现有 owner 上的聚焦方法是否足够？
