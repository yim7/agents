# agents

个人 AI agents 配置、skills 和同步脚本，只保存自己维护、可同步的内容。每个技能的用途与流程见各自的 `SKILL.md`。

## 安装

在仓库目录先预览，再执行同步：

```bash
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

默认同步位置：

- `AGENTS.md` → `~/.codex/AGENTS.md`
- `skills/` → `~/.agents/skills/`

如需安装到其他目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents
```

## 同步行为

- 使用独立目录，通过复制同步，不使用指向仓库的软链接。
- 新增或更新仓库中的技能；删除时只清理本仓库安装过的技能。
- 覆盖或移除前，备份到目标目录的 `.backups/`。

## 使用示例

按名称使用技能，例如：

> 使用 deliver，完成当前已确认的下一条可运行切片，交付使用入口和验收结果。
