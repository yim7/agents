# agents

个人 AI agent 配置：一份全局指令和一组 skills，同步到 Claude Code、DeepSeek Harness 与 Codex。

只写模型自己不知道的东西：我的偏好、授权边界、工具用法和产物格式。模型已经会做的工程实践不重复。写作规范见 [writing-for-agents](skills/writing-for-agents/SKILL.md)，修改指令或技能前先读它。

## 安装

在仓库根目录运行，先预览再同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

| 仓库来源 | 安装位置 |
| --- | --- |
| `AGENTS.md` | `~/.claude/CLAUDE.md`、`~/.dsh/AGENTS.md`（`$DSH_HOME` 优先）、`~/.codex/AGENTS.md` |
| `skills/` | `~/.claude/skills/`、`~/.agents/skills/`（DeepSeek Harness 和 Codex 都读这里） |

自定义目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents --claude-home /path/to/claude --dsh-home /path/to/dsh
```

安装方式是独立复制，覆盖或删除前备份到目标目录的 `.backups/`。每个目标目录的 `.installed-skills.json` 记录本仓库装过的技能；仓库里删掉的技能，下次同步时只在登记过的目录中移除。目标 `skills/` 是符号链接时，脚本在写入前退出。`tests/` 不参与安装。

## 技能

| 技能 | 调用方式 | 用途 |
| --- | --- | --- |
| `improve-codebase-architecture` | 手动 | 架构体检：找出改起来、测起来最费劲的地方，出 HTML 报告，再逐项讨论 |
| `project-conventions` | 自动 | 工具链与前端默认值 |
| `writing-for-agents` | 自动 | 写或改 AGENTS.md、CLAUDE.md、技能时的写法 |
| `ncm-converter` | 自动 | 网易云 `.ncm` 转换 |
| `video-summary` | 自动 | 视频字幕与转写总结 |

“手动”技能只在用户输入 `/name`（Claude Code）或 `$name`（Codex）时加载，同时声明两处：`SKILL.md` frontmatter 中的 `disable-model-invocation: true`，以及 `agents/openai.yaml` 中的 `policy.allow_implicit_invocation: false`。只在用户想要该产物时才用的技能设为手动，省去常驻上下文的 description。

提交信息格式写在 `AGENTS.md`，不单独设技能。

## 验证

安装契约测试只依赖 Python 标准库，在临时目录中运行安装脚本：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

它验证文件安装行为，不验证模型行为。修改指令或技能后，在真实会话里按实际任务检查效果。
