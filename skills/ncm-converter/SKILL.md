---
name: ncm-converter
description: 把网易云音乐的 `.ncm` 文件转成可播放的 MP3 或 FLAC。用户提到 `.ncm` 文件，或网易云下载的音乐无法在外部播放时使用。
---

# NCM 转换器

用本技能目录下的 `scripts/convert_ncm.py` 转换。NCM 的封面帧偏移容易算错，错误输出看起来像 MP3 但完整解码会失败，所以脚本默认用 `ffmpeg` 完整解码校验，通过后才写出最终文件。

```bash
python3 <技能目录>/scripts/convert_ncm.py [-o 输出目录] [--overwrite] <.ncm 文件或目录>...
```

目录递归处理；输出默认在源文件同目录，已存在时跳过；原文件不改动。其余选项见 `--help`。

- 脚本依赖系统 `openssl` 提取 key 和 `ffmpeg` 做校验；有 `ffprobe` 时打印编码、采样率、时长和码率。
- `--no-verify` 只在 `ffmpeg` 不可用且用户明确接受弱校验时用。
- ffmpeg 报 `Header missing` 通常是封面帧偏移解析错了，或者文件不是兼容的 NCM 容器。
