---
name: domain-modeling
description: 建立并打磨项目的领域模型和统一语言（ubiquitous language）。用于讨论项目术语、编写或修改 CONTEXT.md，或记录、修改 ADR。
metadata:
  upstream: https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/domain-modeling/SKILL.md
---

# 领域建模

在设计过程中主动建立和打磨项目的领域模型：质疑术语、编造边界场景，并在术语和决定确定的当下写下来。只是读取 `CONTEXT.md` 来使用词汇不需要本技能；本技能用于**改变**模型。

## 文件结构

项目已有词汇表、领域文档或 ADR 目录时，沿用它们。否则多数仓库只有一个上下文：

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

根目录有 `CONTEXT-MAP.md` 时，仓库有多个上下文，按它找到当前话题所属的 `CONTEXT.md`；归属不清时问用户。

文件按需创建：第一个术语确定时才创建 `CONTEXT.md`，第一份 ADR 需要时才创建 `docs/adr/`。

## 会话中

### 对照术语表质疑

用户用词与 `CONTEXT.md` 中的定义冲突时，当场指出：“术语表把‘取消’定义为 X，你这里似乎指 Y，以哪个为准？”

### 收敛模糊用词

用户使用含糊或多义的词时，提出一个精确的规范术语：“你说的‘账户’是指客户还是登录用户？这是两个概念。”

### 用具体场景压测

讨论领域关系时，编造具体场景去试探概念之间的边界，迫使定义变精确。

### 与代码交叉核对

用户描述某件事如何运作时，检查代码是否一致。发现矛盾就提出来：“代码会取消整个订单，但你刚说可以部分取消，以哪个为准？”

### 当场更新 CONTEXT.md

术语一确定就写入 `CONTEXT.md`，随讨论逐条记录，格式见 [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md)。

`CONTEXT.md` 只是术语表：只放术语和定义，实现细节、规格和临时记录放到别处。

### 谨慎提议 ADR

三个条件同时成立时才提议写 ADR：

1. **难以逆转**：以后改主意的代价可观
2. **缺少背景会令人意外**：后来的读者会疑惑“为什么这样做”
3. **来自真实取舍**：确实有其他方案，基于具体理由做了选择

格式见 [ADR-FORMAT.md](ADR-FORMAT.md)。
