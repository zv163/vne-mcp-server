# VPak Binary Format Specification

## Header (16 bytes)

| Offset | Size | Type | Field |
|--------|------|------|-------|
| 0 | 4 | bytes | Magic: `VPAK` |
| 4 | 4 | uint32 LE | Version (currently 1) |
| 8 | 4 | uint32 LE | Flags: bit0=encrypted, bit1=compressed |
| 12 | 4 | uint32 LE | File count |

## File Table (file_count × 32 bytes)

Per entry:

| Offset | Size | Type | Field |
|--------|------|------|-------|
| 0 | 8 | uint64 LE | Name hash |
| 8 | 8 | uint64 LE | Data offset from file start |
| 16 | 8 | uint64 LE | Packed size in archive |
| 24 | 8 | uint64 LE | Original size (before compression) |

## Data Section

Concatenated file data. Each file's data starts at `HEADER_SIZE + file_count * ENTRY_SIZE + entry.data_offset`.

## Name Hash Algorithm

```
hash = struct.unpack('<Q', hashlib.sha256(relative_path.encode('utf-8')).digest()[:8])[0]
```

Where `relative_path` uses forward slashes (e.g. `texture/icon.png`), relative to the resources root.

## Encryption (Flag bit0)

XOR cipher with 256-byte rotating key:

```python
def derive_key(seed: str) -> bytes:
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    key = bytearray(256)
    for i in range(256):
        key[i] = h[i % 32] ^ ((i * 0x9D) & 0xFF)
    return bytes(key)

def xor_crypt(data: bytearray, key: bytes) -> bytearray:
    for i in range(len(data)):
        data[i] ^= key[i % 256]
    return data
```

## Compression (Flag bit1)

zlib deflate (level 6). Applied BEFORE encryption if both flags are set.

Decompression order: decrypt first, then decompress.

## Packable Extensions

```
texture:  .png .jpg .jpeg .tif .tiff .webp .avif
audio:    .wav .mp3 .ogg .flac
video:    .mp4 .m4v .avi .mkv .flv .mov .webm
font:     .ttf .otf
shader:   .fs .glsl
```

## Unpackable (always kept on disk)

```
.meta .flow .vns .style .ui .saveprofile .md
```

## Lua Implementation Notes

**The Python SHA256 hash is NOT used by the Lua packer/loader.** The pure-Lua VPak implementation (`vpak_pack_step.lua` and `vpak_loader.lua`) uses FNV-1a 32-bit as a replacement because `util.HashString` does not exist in VNE's `Engine.Util`:

```lua
local function _hash_string(s)
    if type(s) ~= "string" then s = tostring(s) end
    local hash = 2166136261
    for i = 1, #s do
        hash = hash ~ string.byte(s, i)
        hash = (hash * 16777619) % 4294967296
    end
    return hash
end
```

Key points:
- **Both packer and loader** must contain the identical `_hash_string` function
- **VNE paths are userdata**, not Lua strings — the `tostring()` guard is mandatory
- FNV-1a hash fits in a Lua float (32-bit, well under 2^53) so no precision issues
- The 32-bit hash is sufficient for visual novel resource counts (typically < 1000 files); collision probability is negligible
- Python packager (`vpak.py`) and Lua packer produce DIFFERENT hashes for the same path — archives are not interchangeable between packers
