---
name: domain-modeling
description: 建立并打磨项目的领域模型。用于讨论代码库术语、编写或修改 CONTEXT.md，或记录、修改 ADR 时。
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/domain-modeling/SKILL.md
---

# 领域建模

在设计过程中主动建立并打磨项目的领域模型。这是一项**主动**的工作：质疑术语、编造边界场景，并在术语表条目和决定成形的那一刻把它们写下来。（仅仅**读取** `CONTEXT.md` 来使用词汇不属于本技能：那是任何技能都能顺手做的一行习惯。本技能用于你在**改变**模型，而不只是使用它的时候。）

## 文件结构

大多数仓库只有一个上下文：

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

如果根目录存在 `CONTEXT-MAP.md`，说明仓库有多个上下文。这份地图指向每个上下文所在的位置：

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← 系统级决定
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← 上下文内的决定
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

文件按需创建：只在有内容可写时才创建。如果还没有 `CONTEXT.md`，在第一个术语确定时创建。如果还没有 `docs/adr/`，在需要第一份 ADR 时创建。

## 会话中

### 对照术语表提出质疑

当用户使用的术语与 `CONTEXT.md` 中已有的语言冲突时，立即指出。“你的术语表把‘取消’定义为 X，但你似乎指的是 Y。到底是哪个？”

### 让模糊的语言变精确

当用户使用含糊或多义的术语时，提出一个精确的规范术语。“你说的‘账户’是指客户（Customer）还是用户（User）？这是两个不同的东西。”

### 讨论具体场景

讨论领域关系时，用具体场景做压力测试。编造能探到边界情况的场景，迫使用户把概念之间的边界说清楚。

### 与代码交叉核对

当用户陈述某件事如何运作时，检查代码是否一致。如果发现矛盾，把它摆出来：“你的代码会取消整个订单，但你刚才说可以部分取消。哪个是对的？”

### 当场更新 CONTEXT.md

术语一确定，就在当下更新 `CONTEXT.md`。不要攒着一起写：随时发生随时记录。格式见 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)。

`CONTEXT.md` 应该完全不含实现细节。不要把 `CONTEXT.md` 当作规格、草稿本或存放实现决定的地方。它是术语表，仅此而已。

### 谨慎提议 ADR

只有以下三条同时成立时，才提议创建 ADR：

1. **难以逆转**：以后改变主意的代价可观
2. **缺少背景会令人意外**：未来的读者会疑惑“为什么要这样做？”
3. **真实取舍的结果**：确实存在其他方案，而你出于具体理由选择了其中一个

缺少任意一条，就跳过 ADR。格式见 [ADR-FORMAT.md](./ADR-FORMAT.md)。
