# agents

个人 AI agent 配置：一份全局指令和一组 skills，同步到 Codex 与 Claude Code。

只写模型自己不知道的东西：我的偏好、授权边界、工具用法和产物格式。模型已经会做的工程实践不重复。写作规范见 [writing-for-agents](skills/writing-for-agents/SKILL.md)，修改指令或技能前先读它。

## 安装

在仓库根目录运行，先预览再同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

| 仓库来源 | 安装位置 |
| --- | --- |
| `AGENTS.md` | `~/.codex/AGENTS.md`、`~/.claude/CLAUDE.md` |
| `skills/` | `~/.agents/skills/`、`~/.claude/skills/` |

自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents --claude-home /path/to/claude
```

安装方式是独立复制，覆盖或删除前备份到目标目录的 `.backups/`。每个目标目录的 `.installed-skills.json` 记录本仓库装过的技能；仓库里删掉的技能，下次同步时只在登记过的目录中移除。目标 `skills/` 是符号链接时，脚本在写入前退出。`docs/`、`evals/`、`tests/` 不参与安装。

## 技能

| 技能 | 调用方式 | 用途 |
| --- | --- | --- |
| `grilling` | 自动 | 按设计树逐轮拷问计划或设计 |
| `grill-me` | 手动 | 启动访谈 |
| `grill-with-docs` | 手动 | 访谈，同时用 `domain-modeling` 记录术语和决定 |
| `domain-modeling` | 自动 | 统一语言：维护 `CONTEXT.md` 和 ADR |
| `to-spec` | 手动 | 把对话整理成 spec，存到 `.scratch/<feature>/spec.md` |
| `to-tickets` | 手动 | 拆成带阻塞依赖的 tracer bullet 任务，存到 `.scratch/<feature>/issues/` |
| `handoff` | 手动 | 把对话压缩成交接文档 |
| `git-commit` | 自动 | 提交格式 |
| `project-conventions` | 自动 | 工具链与前端默认值 |
| `writing-for-agents` | 自动 | 编写指令和技能的规范 |
| `ncm-converter` | 自动 | 网易云 `.ncm` 转换 |
| `video-summary` | 自动 | 视频字幕与转写总结 |

“手动”技能只在用户输入 `/name`（Claude Code）或 `$name`（Codex）时加载，同时声明两处：`SKILL.md` frontmatter 中的 `disable-model-invocation: true`，以及 `agents/openai.yaml` 中的 `policy.allow_implicit_invocation: false`。只在用户想要该产物时才用的技能设为手动，省去常驻上下文的 description。

`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`to-spec`、`to-tickets`、`handoff`、`writing-for-agents` 从 [mattpocock/skills](https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7) 忠实翻译成中文，各技能 frontmatter 的 `metadata.upstream` 记录对应原文件。唯一的适配是 `to-spec` 与 `to-tickets` 不依赖上游的 `setup-matt-pocock-skills`，固定使用上游的本地 Markdown 约定（`.scratch/`）作为 issue tracker。个人偏好等行为用例证明需要时再加。

## 验证

安装契约测试只依赖 Python 标准库，在临时目录中运行安装脚本：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

它验证文件安装行为，不验证模型行为。修改指令或技能后，用 [行为用例](evals/prompt-behavior.md) 在真实会话中对照检查。
