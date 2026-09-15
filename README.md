# agents

个人 AI agents 配置、skills 和同步脚本。提供项目知识、个人取舍与明确的任务要求，不重新规定一整套软件工程方法。

默认工作方式：围绕当前交付目标，优先曳光弹式迭代，尽早得到可运行、可验证的结果；在授权内连续推进，不把新设想自动加入当前范围。

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

普通任务说明目标、上下文、约束和验收即可；已有信息可引用，不必填表或先选择技能。需要逐题访谈时使用 `grill-me`；多步交付使用 `deliver`；有未决结构选择时使用 `design-before-coding`；专项结构审查使用 `design-review`。它们不是固定的顺序流程。

例如：

> 使用 $deliver，完成已确认的当前交付目标。优先打通可验证的使用路径，沿用兼容要求，不部署。未来设想留到后续，不新增逐步确认。

`grill-me`、`grill-with-docs` 和 `implement` 配置为 Codex 显式调用入口；两个访谈入口同时保留原 frontmatter 标记。`grilling` 只匹配用户要求的访谈，信息足够或切换阶段后退出，不因执行中出现新信息自动重启。

## 编写与维护

- [Prompt 系统设计](docs/prompt-design.md)：原则、分层、技能职责及本次取舍。
- [任务描述示例](docs/task-brief.md)：按需表达任务，不是必填模板。
- [项目说明示例](docs/project-instructions.example.md)：记录事实和硬约束，不复制全局偏好。
- [试用与回归案例](docs/prompt-evaluation.md)：包括访谈退出、范围控制和连续增量任务，尚未进行模型行为实测。
- [历史设计资料](docs/archive/README.md)：原文归档，不是当前执行规范。
