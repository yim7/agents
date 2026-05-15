---
name: git-commit
description: 编写、检查、整理或准备 Git 提交信息时使用。要求提交信息用英文，并遵循 Conventional Commits 规范。
---

# Git Commit

编写、检查、整理或准备 Git 提交信息时使用这个 skill。

## 规则

- 提交信息使用英文。
- 遵循 Conventional Commits 规范。
- 一个提交只描述一件逻辑完整的事。
- 不要把不相关的改动混进同一个提交。
- 提交或推送前必须先得到用户确认。
- 写提交信息前先查看相关 diff。

```text
<type>[optional scope][optional !]: <description>
```

## 常用类型

常用 `feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert`。

有明确影响范围时可以加 scope：

## 示例

```text
feat(auth): add password reset flow
fix(cli): handle empty commit messages
docs: add Git commit guidelines
refactor(config): simplify default loading
chore: update agent instructions
feat(api)!: require authorization header
```

破坏性变更可以使用 `!`，必要时补充 `BREAKING CHANGE:` footer。

## 参考

- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
