#!/usr/bin/env python3
"""
VoidNovelEngine VPak Resource Packager

Creates .vpak archives that bundle game resources with optional
encryption and compression for release distribution.

VPak Format:
  [4 bytes]  Magic: "VPAK"
  [4 bytes]  Version (uint32 LE)
  [4 bytes]  Flags (uint32 LE): bit0=encrypted, bit1=compressed
  [4 bytes]  File count (uint32 LE)
  [N bytes]  File table (file_count entries):
    [8 bytes]  Name hash (xxh64 of relative path)
    [8 bytes]  Data offset from file start (uint64 LE)
    [8 bytes]  Data size in archive (uint64 LE)
    [8 bytes]  Original size before compression (uint64 LE)
  [N bytes]  Data section (concatenated file data)

Encryption: XOR cipher with 256-byte rotating key (derived from seed)
Compression: zlib (deflate)
"""

import struct
import zlib
import hashlib
import os
import json
import sys
from typing import Dict, List, Tuple, Optional

MAGIC = b"VPAK"
VERSION = 1
FLAG_ENCRYPTED = 0x01
FLAG_COMPRESSED = 0x02

HEADER_SIZE = 16  # magic(4) + version(4) + flags(4) + count(4)
ENTRY_SIZE = 32   # hash(8) + offset(8) + size(8) + original_size(8)


def _derive_key(seed: str) -> bytes:
    """Derive a 256-byte XOR key from a seed string."""
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    key = bytearray(256)
    for i in range(256):
        key[i] = h[i % len(h)] ^ ((i * 0x9D) & 0xFF)
    return bytes(key)


def _xor_crypt(data: bytearray, key: bytes) -> bytearray:
    """Apply XOR encryption in-place using rotating key."""
    key_len = len(key)
    for i in range(len(data)):
        data[i] ^= key[i % key_len]
    return data


def _name_hash(relative_path: str) -> int:
    """Compute 64-bit hash of a relative path for the file table."""
    h = hashlib.sha256(relative_path.encode('utf-8')).digest()
    return struct.unpack('<Q', h[:8])[0]


def pack(
    source_dir: str,
    output_path: str,
    encryption_key: Optional[str] = None,
    compress: bool = True,
    file_list: Optional[List[str]] = None,
    progress_callback=None,
) -> Dict:
    """
    Pack files from source_dir into a .vpak archive.

    Args:
        source_dir: Root directory containing files to pack
        output_path: Path to output .vpak file
        encryption_key: If provided, encrypt with derived XOR key
        compress: Whether to zlib-compress file data
        file_list: Specific file paths (relative to source_dir) to pack.
                   If None, pack all files recursively.
        progress_callback: Optional callback(step, current, total)

    Returns:
        Dict with stats: file_count, total_original_size, total_packed_size, etc.
    """
    if file_list is None:
        file_list = []
        for root, dirs, files in os.walk(source_dir):
            for fname in files:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, source_dir).replace('\\', '/')
                file_list.append(rel)

    file_list = sorted(set(file_list))

    flags = 0
    key = None
    if encryption_key:
        flags |= FLAG_ENCRYPTED
        key = _derive_key(encryption_key)
    if compress:
        flags |= FLAG_COMPRESSED

    # Read all file data and compute hashes
    entries: List[Tuple[int, bytes, bytes]] = []  # (hash, original_data, packed_data)
    total_original = 0

    for i, rel_path in enumerate(file_list):
        full_path = os.path.join(source_dir, rel_path)
        if not os.path.isfile(full_path):
            continue

        with open(full_path, 'rb') as f:
            original_data = f.read()

        total_original += len(original_data)
        packed_data = original_data

        if compress:
            packed_data = zlib.compress(original_data, 6)

        if key:
            packed_data = _xor_crypt(bytearray(packed_data), key)

        entries.append((_name_hash(rel_path), original_data, bytes(packed_data)))

        if progress_callback:
            progress_callback('packing', i + 1, len(file_list))

    # Build file table and data section
    file_table = bytearray()
    data_section = bytearray()
    current_offset = 0

    for name_hash, original_data, packed_data in entries:
        file_table.extend(struct.pack('<Q', name_hash))
        file_table.extend(struct.pack('<Q', current_offset))
        file_table.extend(struct.pack('<Q', len(packed_data)))
        file_table.extend(struct.pack('<Q', len(original_data)))
        data_section.extend(packed_data)
        current_offset += len(packed_data)

    # Write header
    with open(output_path, 'wb') as f:
        f.write(MAGIC)
        f.write(struct.pack('<I', VERSION))
        f.write(struct.pack('<I', flags))
        f.write(struct.pack('<I', len(entries)))
        f.write(bytes(file_table))
        f.write(bytes(data_section))

    stats = {
        'file_count': len(entries),
        'total_original_size': total_original,
        'total_packed_size': output_size(output_path),
        'flags': flags,
        'encrypted': bool(flags & FLAG_ENCRYPTED),
        'compressed': bool(flags & FLAG_COMPRESSED),
    }
    return stats


def output_size(path: str) -> int:
    """Get size of a .vpak file."""
    return os.path.getsize(path)


def list_contents(path: str) -> List[Dict]:
    """List contents of a .vpak archive."""
    with open(path, 'rb') as f:
        header = f.read(HEADER_SIZE)
        if header[:4] != MAGIC:
            raise ValueError("Not a valid VPAK file")

        version, flags, file_count = struct.unpack('<III', header[4:])
        if version != VERSION:
            raise ValueError(f"Unsupported VPAK version: {version}")

        entries = []
        for _ in range(file_count):
            entry_data = f.read(ENTRY_SIZE)
            name_hash, offset, size, original_size = struct.unpack('<QQQQ', entry_data)
            entries.append({
                'name_hash': name_hash,
                'offset': offset,
                'size': size,
                'original_size': original_size,
            })

    return entries


def read_file(archive_path: str, encryption_key: Optional[str], hash_or_index: int) -> Optional[bytes]:
    """Read a single file from a .vpak archive by its name hash or index."""
    with open(archive_path, 'rb') as f:
        header = f.read(HEADER_SIZE)
        if header[:4] != MAGIC:
            raise ValueError("Not a valid VPAK file")

        version, flags, file_count = struct.unpack('<III', header[4:])
        compressed = bool(flags & FLAG_COMPRESSED)
        encrypted = bool(flags & FLAG_ENCRYPTED)

        key = None
        if encrypted:
            if not encryption_key:
                raise ValueError("Archive is encrypted but no key provided")
            key = _derive_key(encryption_key)

        table_start = HEADER_SIZE
        data_start = table_start + file_count * ENTRY_SIZE

        for i in range(file_count):
            f.seek(table_start + i * ENTRY_SIZE)
            name_hash, offset, size, original_size = struct.unpack('<QQQQ', f.read(ENTRY_SIZE))

            if hash_or_index in (name_hash, i):
                f.seek(data_start + offset)
                data = bytearray(f.read(size))

                if encrypted and key:
                    data = _xor_crypt(data, key)

                if compressed and original_size != size:
                    data = zlib.decompress(bytes(data))

                return bytes(data)

    return None


def read_file_by_path(archive_path: str, encryption_key: Optional[str], relative_path: str) -> Optional[bytes]:
    """Read a file from .vpak by its relative path."""
    target_hash = _name_hash(relative_path)
    return read_file(archive_path, encryption_key, target_hash)


# CLI interface
def main():
    import argparse

    parser = argparse.ArgumentParser(description='VoidNovelEngine VPak Resource Packager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # pack command
    pack_parser = subparsers.add_parser('pack', help='Pack resources into .vpak')
    pack_parser.add_argument('source_dir', help='Source directory with resources')
    pack_parser.add_argument('output', help='Output .vpak file path')
    pack_parser.add_argument('--key', '-k', help='Encryption key (XOR cipher)')
    pack_parser.add_argument('--no-compress', action='store_true', help='Disable zlib compression')
    pack_parser.add_argument('--manifest', '-m', help='JSON manifest with file list')

    # list command
    list_parser = subparsers.add_parser('list', help='List contents of .vpak')
    list_parser.add_argument('archive', help='Path to .vpak file')

    # extract command
    extract_parser = subparsers.add_parser('extract', help='Extract file from .vpak')
    extract_parser.add_argument('archive', help='Path to .vpak file')
    extract_parser.add_argument('path', help='Relative path of file to extract')
    extract_parser.add_argument('--key', '-k', help='Decryption key')
    extract_parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    if args.command == 'pack':
        file_list = None
        if args.manifest:
            with open(args.manifest, 'r', encoding='utf-8') as f:
                file_list = json.load(f)

        stats = pack(
            args.source_dir,
            args.output,
            encryption_key=args.key,
            compress=not args.no_compress,
            file_list=file_list,
        )
        print(f"Packed {stats['file_count']} files")
        print(f"  Original: {stats['total_original_size']:,} bytes")
        print(f"  Packed:   {stats['total_packed_size']:,} bytes")
        if stats['total_original_size'] > 0:
            ratio = (1 - stats['total_packed_size'] / stats['total_original_size']) * 100
            print(f"  Ratio:    {ratio:.1f}%")
        print(f"  Encrypted: {stats['encrypted']}")
        print(f"  Compressed: {stats['compressed']}")

    elif args.command == 'list':
        entries = list_contents(args.archive)
        print(f"VPAK archive: {args.archive}")
        print(f"Files: {len(entries)}")
        for i, entry in enumerate(entries):
            print(f"  [{i}] hash=0x{entry['name_hash']:016x} "
                  f"size={entry['size']:,} "
                  f"original={entry['original_size']:,}")

    elif args.command == 'extract':
        data = read_file_by_path(args.archive, args.key, args.path)
        if data is None:
            print(f"File not found: {args.path}", file=sys.stderr)
            sys.exit(1)
        if args.output:
            os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
            with open(args.output, 'wb') as f:
                f.write(data)
            print(f"Extracted to: {args.output}")
        else:
            sys.stdout.buffer.write(data)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
