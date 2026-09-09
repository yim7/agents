---
name: grill-with-docs
description: 在写 Spec 前逐题澄清需求，同时记录领域术语和设计决定；转入 Spec 整理后结束逐题访谈，继续完成文档。
disable-model-invocation: true
---

使用 `/grilling` 开展当前需求访谈，并使用 `/domain-modeling` 记录术语和设计决定。
遵循 `/grilling` 的生效范围和退出规则；记录文档不延长访谈阶段。
用户要求开始撰写或收敛 Spec 时，结束逐题问答，保留已确认决定并连续完成已授权的文档整理和一致性检查。后续必要问题集中提出，不因历史调用重启访谈，也不把退出访谈视为开发授权。
