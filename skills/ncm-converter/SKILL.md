---
name: ncm-converter
description: 将网易云音乐、NetEase Cloud Music 的 `.ncm` 文件转换为可播放的开放音频格式，例如 MP3 或 FLAC。用户提供或提到 `.ncm` 文件、网易云下载音乐无法在外部播放、需要转换 NCM 文件、或需要批量转换本地 NCM 并用 ffmpeg 校验时使用。
---

# NCM 转换器

## 概览

使用这个 skill 将本地网易云音乐 `.ncm` 文件转换成可播放的音频文件。优先使用内置脚本，因为 NCM 解析对封面帧偏移很敏感，错误输出有时看起来像 MP3，但完整解码会失败。

## 工作流

1. 确认输入路径存在，并且是 `.ncm` 文件，或包含 `.ncm` 文件的目录。
2. 从这个 skill 目录运行 `scripts/convert_ncm.py`。
3. 默认保留完整解码校验；只有用户明确接受弱校验时才使用 `--no-verify`。
4. 向用户报告输出路径和 `ffprobe` 摘要。

## 命令

转换单个文件，默认输出到源文件同目录：

```bash
python3 /path/to/ncm-converter/scripts/convert_ncm.py "/path/to/song.ncm"
```

输出到指定目录：

```bash
python3 /path/to/ncm-converter/scripts/convert_ncm.py -o "/path/to/output" "/path/to/song.ncm"
```

递归批量转换目录：

```bash
python3 /path/to/ncm-converter/scripts/convert_ncm.py "/path/to/网易云音乐"
```

覆盖已有输出：

```bash
python3 /path/to/ncm-converter/scripts/convert_ncm.py --overwrite "/path/to/song.ncm"
```

## 校验

- 脚本依赖系统 `openssl` 提取 NCM key。
- 默认依赖 `ffmpeg`，会先对临时产物执行 `ffmpeg -v error -i <file> -f null -`，完整解码通过后才替换最终输出。
- 如果存在 `ffprobe`，脚本会打印 codec、采样率、声道数、时长和码率。
- 只有在 `ffmpeg` 不可用且用户明确接受弱校验时，才使用 `--no-verify`。

## 注意

- 原始 `.ncm` 文件不会被修改。
- 如果输出文件已经存在，脚本默认跳过；需要重新生成时加 `--overwrite`。
- 常见坏输出症状是 ffmpeg 报 `Header missing`；这通常意味着 NCM 封面帧偏移解析错了，或者文件不是兼容的 NCM 容器。
