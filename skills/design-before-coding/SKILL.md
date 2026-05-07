---
name: design-before-coding
description: Guides software design before implementation for coding tasks involving architecture, module boundaries, abstractions, interfaces, problem decomposition, substantial refactoring, or growing code complexity. Triggers before coding when structure or ownership decisions are unclear. Not for UI or visual design unless code structure is the focus.
---

# 编码前设计

## 概览

当任务会改变抽象、模块边界、接口或责任归属时，先使用这个 skill 做软件结构设计，再进入实现。目标不是最快写出能跑的代码，而是通过更好的边界和接口降低后续复杂度。

核心原则：把设计当作复杂度管理。好的设计会隐藏复杂度、降低修改成本，并让未来维护者更容易理解系统。

## 适用边界

这是软件/代码结构设计 skill。适用于架构、模块边界、抽象、接口、责任拆分和复杂度管理。

不要把它用于 UI、产品或视觉设计，除非真正的问题是代码结构。

## 硬性门槛

在开始实现前，必须能比较清楚地说明：

- 正在引入或修改的主要抽象是什么
- 哪个模块拥有哪部分知识
- 哪些信息应该被隐藏
- 调用方应该看到的最简单接口是什么
- 哪些复杂度应该被下沉到模块内部
- 哪些错误或特殊情况可以通过 API 设计消除
- 新设计移除或隐藏了哪些已有复杂度
- 为什么删除、缩小可见性或在现有 owner 上加一个聚焦方法还不够

如果还说不清这些问题，继续读代码、设计或向用户澄清，不要用“先写起来”掩盖不确定性。

## 抽象价值门槛

新抽象不是天然更好。每个抽象都会增加名字、概念、接口和维护成本。

引入新类型、层、服务、DTO、adapter 或 protocol 前，先证明它降低了净复杂度。优先考虑更小的动作：

1. 删除不必要的代码或概念。
2. 缩小可见性，或把行为移动到当前 owner。
3. 在现有抽象上增加一个聚焦方法。
4. 只有当前几种方式无法隐藏正确知识时，才引入新抽象。

只有当新抽象明显满足以下至少一项时才值得引入：

- 删除的复杂度多于新增的复杂度
- 用更小的接口隐藏不稳定的设计决策
- 缩小公共接口或防止信息泄漏
- 移除重复特殊情况或成对协议
- 让一个可能的未来变化影响更少位置

不要因为“边界看起来更干净”、某个概念值得命名，或风格偏好而引入抽象。如果新抽象主要是在包一层并转发状态，要把它当作可疑信号。

## 何时使用

任务涉及以下内容时使用：

- 新抽象
- 新模块、服务或核心组件
- 接口设计
- 模块边界变化
- 架构变化
- 大幅重构
- 把宽泛问题拆成更小的单元
- 代码已经显露增长中的复杂度

## 何时不要使用

不要把这个 skill 强行用于：

- 文案或文本修改
- 常量更新
- 明显局部的一行修复
- 没有设计影响的批量改名
- 不涉及代码结构决策的 UI 或视觉设计选择

## 必需流程

1. 先读足够的现有代码或文档，理解当前抽象、边界和职责。
2. 加载 `references/core-principles.md`。
3. 找出主导的复杂度信号：`change amplification`、`cognitive load` 或 `unknown unknowns`。
4. 加载 `references/design-questions.md`，只回答和当前任务有关的问题。
5. 在备选方案里包含最小基线：删除、缩小可见性，或不引入新抽象。
6. 先比较两到三个合理设计方向，再选定一个。
7. 比较时关注：
   - 接口是否更简单
   - 信息隐藏是否更好
   - 未来修改成本是否更低
   - 特殊情况和错误是否被内部吸收
   - 概念数量是否真的减少
8. 明确写出最终设计决策：
   - 模块归属
   - 接口形状
   - 被隐藏的设计决策
   - 被下沉的复杂度
   - 被设计掉的错误或特殊情况
   - 为什么这个抽象值得新增概念
9. 然后再进入计划或实现。

如果设计仍然难以命名、难以描述，或无法简短解释，加载 `references/design-workflow.md` 继续收敛。

## 最小设计记录

编码前要简短写出设计决策。小任务一段话即可；大任务用短列表覆盖：

- 主导复杂度信号
- 选择的 ownership 边界
- 调用方面对的接口
- 被隐藏或移除的复杂度
- 考虑过的最小基线，以及为什么不够

## 和其他流程的关系

这个 skill 只负责在编码前澄清设计，不替代其他流程。

设计清楚后：

- 继续使用环境要求的计划、实现、测试或验证流程
- 不要把“设计已经清楚”当作跳过测试、调试或验证的理由

## 警讯

看到以下信号时停下来重新考虑设计：

- `shallow module`
- `information leakage`
- `temporal decomposition`
- `overexposure`
- `over-abstraction`
- `pass-through method`
- `speculative abstraction`
- `special-general mixture`
- `nonobvious code`

出现这些信号时加载 `references/red-flags.md`。

## 设计偏好

- 偏好简单接口，而不是简单实现。
- 偏好深模块，而不是许多浅包装。
- 按知识边界分配 owner，而不是按执行顺序拆分。
- 把复杂度吸收到模块内部，而不是推给调用方。
- 在引入 DTO 或新层之前，先考虑删除、私有字段和聚焦方法。
- 在信息隐藏相同的前提下，选择概念更少的设计。
- 偏好容易阅读、解释和扩展的设计。

## 引用资料

按需读取：

- `references/core-principles.md`：核心原则
- `references/design-workflow.md`：设计流程和决策规则
- `references/design-questions.md`：实现前的问题清单
- `references/red-flags.md`：警讯和追问
