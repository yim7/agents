# agents

个人 AI agents 配置、skills 和同步脚本。

这个仓库只保存自己维护、可同步的内容，不保存 token、缓存、会话记录或机器相关的临时状态。

## 目录结构

```text
agents/
  AGENTS.md
  skills/
  scripts/
    install.py
  README.md
  .gitignore
```

## 使用方式

先预览同步动作：

```bash
uv run python scripts/install.py --dry-run
```

确认后执行：

```bash
uv run python scripts/install.py
```

默认同步到：

```text
~/.codex/AGENTS.md
~/.agents/skills/
```

如果要安装到其他目录：

```bash
uv run python scripts/install.py --codex-home /path/to/codex --agents-home /path/to/agents
```

## 同步到新电脑

```bash
git clone git@github.com:<your-name>/agents.git
cd agents
uv run python scripts/install.py --dry-run
uv run python scripts/install.py
```

## 同步行为

脚本会保持目标目录和仓库一致：

目标 `skills/` 使用独立目录，通过复制同步，不使用指向仓库的软链接。脚本检测到目标目录是软链接时会停止，避免全局安装反向写入仓库。未定制的第三方 skills 直接安装到 `~/.agents/skills/`；需要自行维护的定制版及其必要依赖纳入本仓库。

- 仓库中新增的 skill → 安装到目标目录
- 仓库中已有的 skill → 内容有变化时更新
- 仓库中删除的 skill → 从目标目录移除（仅限本仓库安装过的）

每个目标目录维护一个 `.installed-skills.json` manifest，记录本仓库安装过的内容。用户自己添加的 skill 不会被触碰。

## 注意事项

- 提交前检查不要包含密钥、token、缓存和本地会话。
- `skills/` 只放自己维护的 skill。
- 覆盖或移除前会备份到目标目录的 `.backups/`。

## 自维护的需求访谈 skills

以下技能接管自本机已安装的 Matt 技能副本；本仓库保存当前维护版本，更新上游时先比较差异，不直接覆盖。原始上游版本号未记录。

- `grilling`：核心需求访谈，包含我们调整的阶段范围和退出规则。
- `grill-me`：调用 `grilling` 的快捷入口。
- `grill-with-docs`：调用 `grilling` 和 `domain-modeling`，在访谈中记录术语和设计决定。
- `domain-modeling`：随附依赖，包含 `CONTEXT-FORMAT.md` 和 `ADR-FORMAT.md` 两份模板。

这四个目录随现有安装命令一并复制到新电脑，无需另装 Matt 技能包。定制访谈结束后，文档记录不应重新启动逐题问答。

## 技能迭代

- 根据实际误触发、重复确认、职责冲突或遗漏改进技能；单次输出不满意先区分任务表达、执行偏差和技能规则问题。
- description 以调用条件和用途为主；只有容易与相邻技能混淆时才加排除条件。流程、退出条件和授权边界放在正文。
- 优先修改已有规则，避免不断追加例外。修改后检查典型适用场景和相邻不适用场景，再同步全局副本；实际效果由后续任务验证。
