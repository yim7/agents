#!/usr/bin/env python3
"""将网易云音乐 .ncm 文件转换为可播放的开放音频文件。"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAGIC = b"CTENFDAM"
CORE_KEY = b"hzHRAmso5kInbaxW"
META_KEY = b"#14ljk_!\\]&0U<'("
KEY_PREFIX = b"neteasecloudmusic"
META_PREFIX_LEN = len(b"163 key(Don't modify):")


@dataclass
class NcmPayload:
    audio: bytes
    audio_format: str
    metadata: dict[str, Any]
    audio_offset: int


@dataclass
class ConvertResult:
    source: Path
    output: Path | None
    status: str
    detail: str


def read_u32(f) -> int:
    raw = f.read(4)
    if len(raw) != 4:
        raise ValueError("文件意外结束，无法读取 4 字节整数")
    return struct.unpack("<I", raw)[0]


def xor_bytes(data: bytes, mask: int) -> bytes:
    return bytes(byte ^ mask for byte in data)


def aes_ecb_decrypt(data: bytes, key: bytes, openssl: str) -> bytes:
    proc = subprocess.run(
        [openssl, "enc", "-d", "-aes-128-ecb", "-K", key.hex(), "-nopad"],
        input=data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()
        raise ValueError(f"openssl AES 解密失败: {err}")

    out = proc.stdout
    if not out:
        return out

    pad = out[-1]
    if 1 <= pad <= 16:
        return out[:-pad]
    return out


def build_key_box(key: bytes) -> bytearray:
    if not key:
        raise ValueError("音频解密 key 为空")

    box = bytearray(range(256))
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = box[i]
        c = (swap + last_byte + key[key_offset]) & 0xFF
        key_offset = (key_offset + 1) % len(key)
        box[i] = box[c]
        box[c] = swap
        last_byte = c
    return box


def decrypt_audio(data: bytes, key_box: bytearray) -> bytes:
    audio = bytearray(data)
    for i in range(len(audio)):
        j = (i + 1) & 0xFF
        audio[i] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xFF]) & 0xFF]
    return bytes(audio)


def parse_metadata(raw: bytes, openssl: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        meta_data = xor_bytes(raw, 0x63)
        decoded = base64.b64decode(meta_data[META_PREFIX_LEN:])
        decrypted = aes_ecb_decrypt(decoded, META_KEY, openssl)
        if decrypted.startswith(b"music:"):
            decrypted = decrypted[len(b"music:") :]
        return json.loads(decrypted.decode("utf-8", "replace").rstrip("\x00"))
    except Exception:
        return {}


def detect_audio_format(audio: bytes, metadata: dict[str, Any]) -> str:
    if audio.startswith(b"ID3") or audio[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}:
        return "mp3"
    if audio.startswith(b"fLaC"):
        return "flac"
    if audio.startswith(b"OggS"):
        return "ogg"
    if len(audio) >= 8 and audio[4:8] == b"ftyp":
        return "m4a"

    meta_format = str(metadata.get("format") or "").lower()
    return meta_format or "bin"


def read_ncm(path: Path, openssl: str) -> NcmPayload:
    with path.open("rb") as f:
        magic = f.read(8)
        if magic != MAGIC:
            raise ValueError(f"不是标准 NCM 文件，文件头为 {magic!r}")

        f.seek(2, 1)

        key_len = read_u32(f)
        encrypted_key = f.read(key_len)
        if len(encrypted_key) != key_len:
            raise ValueError("key data 不完整")

        key_data = aes_ecb_decrypt(xor_bytes(encrypted_key, 0x64), CORE_KEY, openssl)
        if not key_data.startswith(KEY_PREFIX):
            raise ValueError("key data 前缀异常，无法派生音频解密 key")
        audio_key = key_data[len(KEY_PREFIX) :]
        key_box = build_key_box(audio_key)

        meta_len = read_u32(f)
        encrypted_meta = f.read(meta_len)
        if len(encrypted_meta) != meta_len:
            raise ValueError("metadata 不完整")
        metadata = parse_metadata(encrypted_meta, openssl)

        # NCM 在 metadata 后有 CRC32 + image version，然后是封面帧。
        f.seek(5, 1)
        cover_frame_len = read_u32(f)
        cover_data_len = read_u32(f)
        if cover_data_len > cover_frame_len:
            raise ValueError("封面帧长度异常")

        f.seek(cover_data_len, 1)
        f.seek(cover_frame_len - cover_data_len, 1)
        audio_offset = f.tell()
        encrypted_audio = f.read()

    if not encrypted_audio:
        raise ValueError("没有找到加密音频数据")

    audio = decrypt_audio(encrypted_audio, key_box)
    return NcmPayload(
        audio=audio,
        audio_format=detect_audio_format(audio, metadata),
        metadata=metadata,
        audio_offset=audio_offset,
    )


def iter_sources(paths: list[Path]) -> list[Path]:
    sources: list[Path] = []
    for path in paths:
        path = path.expanduser()
        if path.is_dir():
            sources.extend(
                sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() == ".ncm")
            )
        elif path.is_file():
            sources.append(path)
        else:
            raise FileNotFoundError(path)
    return sources


def output_path_for(source: Path, payload: NcmPayload, output_dir: Path | None) -> Path:
    base_dir = output_dir.expanduser() if output_dir else source.parent
    return base_dir / f"{source.stem}.{payload.audio_format}"


def verify_with_ffmpeg(path: Path, ffmpeg: str | None) -> None:
    if not ffmpeg:
        raise ValueError("未找到 ffmpeg；安装后重试，或显式传入 --no-verify")

    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-v", "error", "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or f"ffmpeg exited with {proc.returncode}"
        raise ValueError(f"ffmpeg 完整解码校验失败: {detail}")


def probe_summary(path: Path, ffprobe: str | None) -> str:
    if not ffprobe:
        return ""

    proc = subprocess.run(
        [
            ffprobe,
            "-hide_banner",
            "-v",
            "error",
            "-show_entries",
            "format=duration,bit_rate:stream=codec_name,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return ""

    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    parts = []
    codec = stream.get("codec_name")
    sample_rate = stream.get("sample_rate")
    channels = stream.get("channels")
    duration = fmt.get("duration")
    bit_rate = fmt.get("bit_rate")

    if codec:
        parts.append(str(codec))
    if sample_rate:
        parts.append(f"{int(sample_rate) / 1000:g} kHz")
    if channels:
        parts.append(f"{channels}ch")
    if duration:
        parts.append(format_duration(float(duration)))
    if bit_rate:
        parts.append(f"{round(int(bit_rate) / 1000)} kbps")
    return ", ".join(parts)


def format_duration(seconds: float) -> str:
    total = round(seconds)
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def convert_one(
    source: Path,
    output_dir: Path | None,
    overwrite: bool,
    verify: bool,
    openssl: str,
    ffmpeg: str | None,
    ffprobe: str | None,
) -> ConvertResult:
    payload = read_ncm(source, openssl)
    output = output_path_for(source, payload, output_dir)
    if output.exists() and not overwrite:
        return ConvertResult(source, output, "skip", "输出文件已存在，加 --overwrite 可覆盖")

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(f".{output.name}.tmp")
    tmp.write_bytes(payload.audio)
    try:
        if verify:
            verify_with_ffmpeg(tmp, ffmpeg)
        tmp.replace(output)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

    summary = probe_summary(output, ffprobe)
    detail = summary or f"audio_offset={payload.audio_offset}"
    return ConvertResult(source, output, "ok", detail)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将网易云音乐 .ncm 文件转换为 mp3/flac 等开放音频格式。"
    )
    parser.add_argument("paths", nargs="+", type=Path, help="一个或多个 .ncm 文件或目录。")
    parser.add_argument("-o", "--output-dir", type=Path, help="输出目录；默认写到源文件同目录。")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的输出文件。")
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="跳过 ffmpeg 完整解码校验；默认会校验后才替换输出文件。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    openssl = shutil.which("openssl")
    if not openssl:
        print("错误: 未找到 openssl，无法解密 NCM key。", file=sys.stderr)
        return 2

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    try:
        sources = iter_sources(args.paths)
    except FileNotFoundError as exc:
        print(f"错误: 路径不存在: {exc.filename}", file=sys.stderr)
        return 2

    if not sources:
        print("没有找到 .ncm 文件。")
        return 0

    failed = 0
    skipped = 0
    for source in sources:
        try:
            result = convert_one(
                source=source,
                output_dir=args.output_dir,
                overwrite=args.overwrite,
                verify=not args.no_verify,
                openssl=openssl,
                ffmpeg=ffmpeg,
                ffprobe=ffprobe,
            )
        except Exception as exc:
            failed += 1
            print(f"[失败] {source}: {exc}", file=sys.stderr)
            continue

        if result.status == "skip":
            skipped += 1
            print(f"[跳过] {result.source} -> {result.output}: {result.detail}")
        else:
            print(f"[完成] {result.source} -> {result.output} ({result.detail})")

    if failed:
        print(f"完成，但有 {failed} 个文件失败，{skipped} 个文件跳过。", file=sys.stderr)
        return 1
    if skipped:
        print(f"完成，{skipped} 个文件因输出已存在而跳过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
