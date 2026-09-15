# agents

个人 AI agents 配置、skills 和同步脚本。提供项目知识、个人取舍与明确的任务要求，不重新规定一整套软件工程方法。

前期需要深入讨论时，用 Grill Me 充分消除模糊，再将结论落到文档。进入开发后，围绕已确认的当前交付目标进行曳光弹式迭代，尽早验证结果；不延续访谈中的等待方式，也不把补充信息自动变成范围扩张。简单明确的任务无需强制经过访谈和文档流程。

## 安装

在完整仓库中预览，再执行同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

默认将 `AGENTS.md` 复制到 `~/.codex/AGENTS.md`，将 `skills/` 复制到 `~/.agents/skills/`。自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents
```

覆盖或移除前，脚本备份到目标目录的 `.backups/`，删除时只清理本仓库安装过的技能。`docs/` 不参与安装。

## 使用

普通任务说明目标、上下文、约束和验收即可；已有信息可引用，不必填表或先选择技能。需要充分访谈时使用 `grill-me`，同时记录领域术语和决定时使用 `grill-with-docs`；多步交付使用 `deliver`；形成或调整软件方案时使用 `software-design`；检查已有方案或实现的结构风险时使用 `design-review`。它们不是每次必经的顺序流程。

`software-design` 交付推荐方案、取舍依据和必要边界；`design-review` 交付有证据的问题与检查结论。按主要产物选择，两者可独立使用，不默认互相触发；同时要求审查与修订时，在原授权内完成，不新增确认步骤。

例如：

> 使用 $deliver，完成文档中已确认的当前交付目标。优先打通可验证的使用路径，沿用兼容要求，不部署。文档中的后续需求不自动纳入本次实现，不新增逐步确认。

`grill-me`、`grill-with-docs` 和 `implement` 配置为 Codex 显式调用入口；两个访谈入口同时保留原 frontmatter 标记。`grilling` 用于充分澄清和思考，不以“足以开工”提前结束；用户转入文档或开发后停止访谈方式，不因新信息自动重启。文档区分已确认决定、本次实现范围、后续需求和未决事项。

## 编写与维护

- [Prompt 系统设计](docs/prompt-design.md)：原则、分层、技能职责及本次取舍。
- [任务描述示例](docs/task-brief.md)：按需表达任务，不是必填模板。
- [项目说明示例](docs/project-instructions.example.md)：记录事实和硬约束，不复制全局偏好。
- [试用与回归案例](docs/prompt-evaluation.md)：包括充分访谈、文档交接、开发范围控制和连续增量任务，尚未进行模型行为实测。
