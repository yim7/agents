---
name: design-review
description: Reviews specs, plans, PR descriptions, interface docs, comments, code, or diffs for software structure, abstraction quality, module boundaries, information leakage, and complexity risks. Applies to software/code design review, not UI or visual design review.
---

# 设计审查

## 概览

使用这个 skill 审查设计决策，而不只是审查实现细节。任何承载设计意图的 artifact 都可以审查；只有当问题会增加未来复杂度或削弱抽象时，才报告 finding。

核心原则：真正的 finding 应该指出一个会让未来修改更困难、泄漏知识、削弱抽象质量，或增加维护者认知负担的设计决策。

## 适用边界

这是软件/代码结构审查 skill。适用于抽象质量、模块边界、接口形状、信息隐藏和复杂度风险。

不要把它用于 UI、产品或视觉设计审查，除非问题实际来自代码结构。

## 审查对象

这个 skill 适用于：

- `spec`
- `plan`
- PR 描述或变更总结
- 接口文档
- 注释和 docstring
- 代码
- diff

当 artifact 类型会影响审查重点时，加载 `references/review-scope.md`。

## 审查顺序

每次按这个顺序走：

1. 先重建这个问题的最佳整体设计，不要从局部修补开始。
2. 识别 artifact 表达了哪些设计决策。
3. 写下最佳设计隐含的硬约束：ownership、source of truth、层边界、持久化边界、公私接口和任务边界。
4. 用这些约束检查整个 artifact，而不是只看最新 finding 或 diff hunk。
5. 检查 artifact 是否增加：
   - `change amplification`
   - `cognitive load`
   - `unknown unknowns`
6. 检查抽象预算：
   - 每个新抽象是否移除或隐藏了足够复杂度？
   - 删除、缩小可见性或一个聚焦方法是否能用更少概念解决？
   - artifact 是在降低净复杂度，还是只让分层看起来更干净？
   - 每个新名词是职责边界、模块、API 契约、运行时对象，还是持久化事实源？
   - 职责边界是否被不必要地升级成 class、DTO、service、adapter 或 protocol？
   - read model 是否被误当作事实源、领域对象或内部传递对象？
7. 检查下方完整警讯列表，并按当前 artifact 类型筛选适用项。
8. 检查正向设计信号：
   - 深模块
   - 简单接口
   - 不同层代表不同抽象
   - 复杂度被下沉
   - 概念数量减少
   - 公共表面积减少且没有新增多余层
   - 错误或特殊情况被设计掉
   - 结果更容易阅读
9. 最后才考虑命名、注释和一致性，而且只在它们实质影响设计清晰度时提出。

需要详细问题时，加载 `references/review-checklist.md`。

## 整体审查要求

从最佳整体设计出发，而不是从最后一版 patch 出发。

当用户提供已有 review finding 或修订版 artifact 时：

- 把旧 finding 当作线索，不当作审查范围。
- 先判断如果从零实现，干净设计应该是什么。
- 把这个设计转成简短约束图。
- 重新检查所有相关层和任务边界。
- 如果多个 finding 有同一个根因，报告根设计问题，而不是批准一串局部补丁。
- 当某个 finding 被局部修复后，继续检查修复是否造成相邻泄漏。
- 当某个 finding 被修复后，继续检查修复是否通过新增过多概念、对象或 DTO 增加认知负担。
- 不要因为原 finding 消失就认为设计干净；确认底层设计压力也消失了。
- 如果用户提供累积列表，要明确区分 stale finding 和当前 finding。

针对 plan：

- 拒绝需要临时 adapter、双重事实源或半迁移共享接口的任务拆分。
- 共享边界变化必须和所有直接消费者在同一个任务中移动。
- 优先接受曳光弹式业务切片：真实输入、核心逻辑、状态持久化和可观察输出在同一薄闭环里推进。
- 如果 plan 按前端、后端、数据库、API 等技术层拆分，并会导致临时接口、不可验证半成品或后续补丁，应作为 finding。
- public/read-model 层不应接收 private runtime state，除非那正是目标抽象。
- 测试 fixture 也算接口消费者；如果生产代码不该依赖 private state，测试也不应依赖。

## Finding 门槛

只有当问题实质上造成以下风险时才报告 finding：

- 增加未来修改成本
- 增加安全修改所需的背景知识
- 制造隐藏耦合或模糊影响面
- 让同一个设计决策泄漏到多个位置
- 让接口比必要程度更复杂
- 增加抽象成本却没有降低净复杂度
- 鼓励战术补丁，而不是更干净的抽象
- 概念爆炸明显增加维护者认知负担

不要为以下内容报告 finding：

- 纯风格偏好
- 不影响设计的措辞或格式差异
- 命名口味差异，除非名称削弱抽象或隐藏行为
- 不够理想但不误导的注释
- 需要增加更多概念才能换来的“边界更干净”

边界不清楚时，加载 `references/finding-thresholds.md`。

## 输出格式

Findings 放在最前面。每条 finding 要简短，并围绕设计风险。

每条 finding 应包括：

- 设计问题是什么
- 为什么它是复杂度问题
- 未来可能造成什么后果
- 推荐的改进方向
- 推荐方向应包含最小可行修复；不要默认建议新增类、DTO、service 或 adapter

审查 `spec` 或 `plan` 时，要说明问题在实现中可能如何显现。

需要稳定输出结构时，加载 `references/output-format.md`。

## 抽象减法

当审查对象处于早期设计、spec 或 plan 阶段时，除了 findings，还要主动寻找可以降低概念数量的地方。只有当它会实质降低认知负担时才提出。

优先建议：

- 把职责边界保留为文档约束，而不是实现成同名类。
- 把浅对象降级为模块内聚焦函数。
- 把只用于展示的 read model 限定在 API 边界，不持久化、不传入业务核心。
- 压平不必要嵌套的响应 schema。
- 用一条薄但完整的功能闭环替代按层拆出的半成品任务。

好的 review 不只指出边界不清，也要防止边界清楚后概念爆炸。

## 无 Finding 规则

如果没有发现有意义的设计问题，明确说明：

> 在 Design Review 框架下，没有发现明确的设计问题。

不要用泛泛表扬或低信息量观察凑数。

## 和其他审查的关系

这个 skill 只评估设计质量，不替代其他审查视角。

- 设计审查干净，不代表没有 bug、回归或测试缺口。
- 如果还需要其他 review workflow，要一起使用。
- 把这个 skill 当作设计风险 lens，而不是完整 code review。

## 警讯

尤其关注：

- `shallow module`
- `information leakage`
- `temporal decomposition`
- `overexposure`
- `over-abstraction`
- `pass-through method`
- `speculative abstraction`
- `special-general mixture`
- `conjoined methods`
- `nonobvious code`
- `concept explosion`
- `read-model-as-source-of-truth`
- `responsibility-boundary-turned-class`

## 引用资料

按需读取：

- `references/review-scope.md`：不同 artifact 的审查重点
- `references/review-checklist.md`：审查问题清单
- `references/finding-thresholds.md`：finding 门槛
- `references/output-format.md`：稳定输出格式
