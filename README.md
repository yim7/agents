# agents

个人 AI agents 配置、skills 和同步脚本。提供项目知识、个人取舍与明确的任务要求，不重新规定一整套软件工程方法。

前期需要深入讨论时，用 Grill Me 充分消除模糊，再将结论落到文档。进入开发后，围绕已确认的当前交付目标迭代；具体阶段边界见 [AGENTS.md](AGENTS.md)。简单明确的任务无需强制经过访谈和文档流程。

## 安装

从包含 `AGENTS.md`、`scripts/install.py` 和全部待同步 `skills/` 的仓库根目录运行。不要求带 `.git/` 才能安装；但不能只复制安装脚本或部分技能，因为脚本把源 `skills/` 当作本仓库的完整安装集合，可能清理其余已登记技能。

先预览，再执行同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

默认将 `AGENTS.md` 复制到 `~/.codex/AGENTS.md`，将 `skills/` 复制到 `~/.agents/skills/`。采用独立目录复制，不使用指向仓库的软链接；目标 `<agents-home>/skills` 如果是符号链接，脚本会退出，须先核对并迁移其中内容。

自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents
```

覆盖或移除前，备份到目标目录的 `.backups/`。过期技能清理仅依据各目标目录的 `.installed-skills.json`；安装脚本不会按名称猜测未登记技能的来源。`docs/` 和 `tests/` 不参与安装。

### 旧设计技能更名

本 PR 将 `design-before-coding` 替换为 `software-design`，不提供旧名入口。

若目标目录的 manifest 已登记旧名，同步会备份并删除旧技能、安装新技能。若 manifest 缺失或未登记旧名，旧目录会保留；安装新技能不代表旧技能已经禁用。先核对旧副本的路径、来源和本地修改，再通过对应安装方式清理，不要按同名批量删除。其他项目目录或第三方安装位置也不在本脚本的清理范围。

## 使用与调用策略

普通任务说明目标、上下文、约束和验收即可，已有信息可引用。需要充分访谈时选择 `grill-me`，同时记录领域术语和决定时选择 `grill-with-docs`；需要任务清单时选择 `to-tickets`；多步交付使用 `deliver`。这些不是每次必经的顺序流程。

`software-design` 交付推荐方案、取舍依据和必要边界；`design-review` 交付有证据的问题与检查结论。按主要产物选择，两者可独立使用，不默认互相触发。同时要求审查与修订时，在原授权内完成，不新增确认步骤。

例如：

> 使用 $deliver，完成文档中已确认的当前交付目标，提供使用入口和验证结果，不部署。

Codex 显式调用入口共有四个：`grill-me`、`grill-with-docs`、`implement`、`to-tickets`，各自的 `agents/openai.yaml` 设置了 `allow_implicit_invocation: false`。本 PR 为两个 grill 入口新增这份 YAML；`implement` 和 `to-tickets` 的配置在基线已存在。调用策略限制自动选择，不是权限隔离。

两个 grill 入口保留 `disable-model-invocation: true` frontmatter，供 Claude Code 等识别该字段的宿主使用；Codex 使用上述 YAML。两处声明面向不同宿主，并非同一解析器的重复配置，后续更改显式调用意图时应一起核对。当前安装脚本不配置 Claude Code 的安装目录。

## 验证与维护

安装契约测试仅依赖 Python 标准库，在临时目录运行安装脚本，不修改本机 agent 配置：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

这些测试验证 manifest 清理范围、预览无写入和符号链接拒绝，不验证模型行为。

- [Prompt 系统设计](docs/prompt-design.md)：原则、规则归属及相对基线的变更。
- [任务描述示例](docs/task-brief.md)：按需表达任务，不是必填模板。
- [项目说明示例](docs/project-instructions.example.md)：记录事实和硬约束。
- [试用与回归案例](docs/prompt-evaluation.md)：访谈、文档、开发和设计审查的行为场景，仍待实测。
