#!/usr/bin/env python3
"""
VoidNovelEngine MCP Server

A Model Context Protocol server that provides tools for AI assistants
to interact with VoidNovelEngine projects. Supports stdio transport.

Provides tools for:
- Reading project configuration (.vne files)
- Listing and querying resources
- Reading/writing project files
- Running VPak resource packaging
- Searching project content
- Getting export configuration

Usage:
    python vne_mcp_server.py [--project-path /path/to/project]
    # If no project path given, discovers from current directory
"""

import os
import sys
import json
import struct
import re
import glob
import time
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# MCP Protocol Implementation (stdlib only, no external deps)
# ---------------------------------------------------------------------------

class MCPServer:
    """Minimal MCP JSON-RPC server over stdio."""

    def __init__(self, name: str = "vne-mcp-server", version: str = "1.1.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Dict] = {}
        self._request_id = 0

    def register_tool(self, name: str, description: str, input_schema: Dict,
                      handler, annotations: Dict = None):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler,
            "annotations": annotations,
        }

    def _send_response(self, id, result):
        self._write({"jsonrpc": "2.0", "id": id, "result": result})

    def _send_error(self, id, code: int, message: str):
        self._write({"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}})

    def _write(self, obj):
        data = json.dumps(obj, ensure_ascii=False)
        sys.stderr.write(f"[MCP OUT] {data[:200]}...\n")
        sys.stderr.flush()
        sys.stdout.write(data + "\n")
        sys.stdout.flush()

    def _read_message(self) -> Optional[Dict]:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            return None
        try:
            msg = json.loads(line)
            sys.stderr.write(f"[MCP IN] {json.dumps(msg, ensure_ascii=False)[:200]}...\n")
            sys.stderr.flush()
            return msg
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[MCP ERR] JSON parse error: {e}\n")
            return None

    def _handle_initialize(self, msg):
        result = {
            "protocolVersion": "2025-11-25",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": self.name, "version": self.version},
            "instructions": "VNE MCP Server — provides 15 tools for VoidNovelEngine projects. Use vne_project_info first to get an overview, vne_list_node_types to see available flow nodes, vne_validate_flow before opening generated .flow files, vne_refresh_assets after creating files externally.",
        }
        self._send_response(msg.get("id"), result)

    def _handle_tools_list(self, msg):
        tools_list = []
        for t in self.tools.values():
            tools_list.append({
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            })
        self._send_response(msg.get("id"), {"tools": tools_list})

    def _handle_tools_call(self, msg):
        params = msg.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        tool = self.tools.get(tool_name)
        if not tool:
            self._send_error(msg.get("id"), -32601, f"Tool not found: {tool_name}")
            return

        try:
            result = tool["handler"](arguments)
            # Result must be list of content blocks
            if isinstance(result, list):
                content = result
            elif isinstance(result, dict) and "content" in result:
                content = result["content"]
            else:
                content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
            self._send_response(msg.get("id"), {"content": content})
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self._send_error(msg.get("id"), -32000, f"Tool error: {e}\n{tb}")

    def run(self):
        """Main server loop over stdio."""
        sys.stderr.write(f"[MCP] {self.name} v{self.version} starting...\n")
        sys.stderr.flush()

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            method = msg.get("method", "")

            if method == "initialize":
                self._handle_initialize(msg)
            elif method == "notifications/initialized":
                pass  # No response needed
            elif method == "tools/list":
                self._handle_tools_list(msg)
            elif method == "tools/call":
                self._handle_tools_call(msg)
            elif method == "ping":
                self._send_response(msg.get("id"), {})
            else:
                self._send_error(msg.get("id"), -32601, f"Unknown method: {method}")


# ---------------------------------------------------------------------------
# VoidNovelEngine Project Tools
# ---------------------------------------------------------------------------

class VNEProject:
    """Represents a VoidNovelEngine project."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self._vne_path = None
        self._vne_data = None
        self._resources_path = None
        self._application_path = None

    def _find_vne(self) -> Optional[Path]:
        """Find project.vne in or above the given path."""
        current = self.project_path
        for _ in range(10):
            vne_file = current / "project.vne"
            if vne_file.exists():
                return vne_file
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _ensure_loaded(self):
        if self._vne_path is None:
            self._vne_path = self._find_vne()
        if self._vne_path and self._vne_data is None:
            with open(self._vne_path, 'r', encoding='utf-8-sig') as f:
                self._vne_data = json.load(f)
            self._application_path = self._vne_path.parent / "application"
            self._resources_path = self._application_path / "resources"

    def is_valid(self) -> bool:
        self._ensure_loaded()
        return self._vne_path is not None

    def get_info(self) -> Dict:
        self._ensure_loaded()
        if not self._vne_data:
            return {"error": "No project.vne found"}

        asset_registry = self._vne_data.get("asset_registry", {})
        assets = asset_registry.get("assets", [])

        resource_counts = {}
        for asset in assets:
            t = asset.get("type", "unknown")
            resource_counts[t] = resource_counts.get(t, 0) + 1

        return {
            "project_path": str(self._vne_path.parent),
            "project_version": self._vne_data.get("project_version", "unknown"),
            "total_assets": len(assets),
            "resource_counts": resource_counts,
            "application_path": str(self._application_path) if self._application_path else None,
            "resources_path": str(self._resources_path) if self._resources_path else None,
        }

    def list_resources(self, resource_type: str = None) -> List[Dict]:
        self._ensure_loaded()
        if not self._vne_data:
            return []

        asset_registry = self._vne_data.get("asset_registry", {})
        assets = asset_registry.get("assets", [])

        result = []
        for asset in assets:
            if resource_type and asset.get("type") != resource_type:
                continue
            result.append({
                "guid": asset.get("guid", ""),
                "type": asset.get("type", "unknown"),
                "relative_path": asset.get("last_known_relative_path", ""),
                "meta_path": asset.get("last_known_meta_path", ""),
                "size": asset.get("file_signature", {}).get("size", 0),
            })

        result.sort(key=lambda x: (x["type"], x["relative_path"]))
        return result

    def read_file(self, relative_path: str) -> Optional[str]:
        self._ensure_loaded()
        if not self._vne_path:
            return None

        full_path = self._vne_path.parent / relative_path
        try:
            full_path = full_path.resolve()
            # Safety: don't allow reading outside project
            if not str(full_path).startswith(str(self._vne_path.parent)):
                return None
            if not full_path.exists():
                return None
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except Exception:
            return None

    def list_directory(self, relative_path: str = ".") -> List[Dict]:
        self._ensure_loaded()
        base = self._vne_path.parent if self._vne_path else self.project_path
        full_path = (base / relative_path).resolve()

        if not str(full_path).startswith(str(base)):
            return []

        if not full_path.exists():
            return []

        result = []
        try:
            for entry in sorted(full_path.iterdir()):
                result.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None,
                })
        except PermissionError:
            pass
        return result

    def search(self, query: str, file_pattern: str = "*.lua") -> List[Dict]:
        self._ensure_loaded()
        base = self._vne_path.parent if self._vne_path else self.project_path
        app_path = base / "application"

        results = []
        if app_path.exists():
            for path in app_path.rglob(file_pattern):
                try:
                    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                rel = str(path.relative_to(base))
                                results.append({
                                    "file": rel,
                                    "line": i,
                                    "content": line.strip()[:200],
                                })
                except Exception:
                    continue

        return results[:50]  # Limit results

    def get_resource_detail(self, guid: str) -> Optional[Dict]:
        self._ensure_loaded()
        if not self._vne_data:
            return None

        asset_registry = self._vne_data.get("asset_registry", {})
        for asset in asset_registry.get("assets", []):
            if asset.get("guid") == guid:
                meta_path = asset.get("last_known_meta_path")
                meta_content = None
                if meta_path:
                    meta_full = self._vne_path.parent / meta_path
                    if meta_full.exists():
                        with open(meta_full, 'r', encoding='utf-8-sig') as f:
                            meta_content = json.load(f)

                return {
                    "asset": asset,
                    "meta_content": meta_content,
                }
        return None

    def get_lua_api(self) -> Dict:
        """Describe the engine's Lua API for AI assistance."""
        return {
            "engine_modules": {
                "Engine.SDL": "SDL2 bindings (window, renderer, audio, input)",
                "Engine.Raylib": "Raylib bindings (textures, shapes, audio streaming)",
                "Engine.ImGUI": "Dear ImGui bindings (editor UI)",
                "Engine.Util": "Utility: file I/O, processes, strings",
                "Engine.JSON": "JSON parse/serialize",
            },
            "key_modules": {
                "application.framework.global_context": "Global state",
                "application.framework.resource_index": "Asset registry and indexing",
                "application.framework.resources_manager": "Runtime resource loading/caching",
                "application.framework.flow_manager": "Flow graph / story scripts",
                "application.framework.scene_manager": "Scene lifecycle",
                "application.framework.settings_manager": "Project settings (project.vne)",
                "application.framework.native_io": "File system operations",
                "application.framework.vpak_loader": "VPak archive resource loader",
            },
            "project_structure": {
                "project.vne": "Project configuration and asset registry (JSON)",
                "main.lua": "Entry point",
                "application/application.lua": "Engine initialization",
                "application/framework/": "Core engine modules (Lua)",
                "application/node/": "Flow node definitions (builtin + custom)",
                "application/pin/": "Data type pin definitions",
                "application/resources/": "Game assets (texture, audio, font, etc.)",
                "application/scene/": "Scenes (editor, released, etc.)",
                "application/external/": "External tools (luac, ffmpeg, etc.)",
                "plugins/": "Plugin packages",
            },
            "resource_types": {
                "texture": [".png", ".jpg", ".webp", ".tif", ".avif"],
                "audio": [".wav", ".mp3", ".ogg", ".flac"],
                "video": [".mp4", ".avi", ".mkv", ".webm"],
                "font": [".ttf", ".otf"],
                "shader": [".fs", ".glsl"],
                "flow": [".flow", ".vns"],
                "style": [".style"],
                "ui": [".ui"],
                "save_profile": [".saveprofile"],
            },
        }

    def get_export_config(self) -> Dict:
        """Get export-related configuration."""
        self._ensure_loaded()
        if not self._vne_data:
            return {"error": "No project loaded"}

        # Read settings from the .vne file's parent
        settings = {}
        settings_path = self._vne_path.parent
        settings_vne = settings_path / "project.vne"
        if settings_vne.exists():
            with open(settings_vne, 'r', encoding='utf-8-sig') as f:
                settings = json.load(f)

        # Extract export-relevant keys
        export_keys = [
            "title", "entry_flow_guid", "default_fullscreen",
            "single_file", "developer", "file_description",
            "release_version", "release_mode", "window_icon_guid",
        ]
        export_config = {}
        for key in export_keys:
            if key in settings:
                export_config[key] = settings[key]

        # Check VPak status
        resources_vpak = settings_path / "application" / "resources.vpak"
        export_config["has_vpak"] = resources_vpak.exists()
        if resources_vpak.exists():
            export_config["vpak_size"] = resources_vpak.stat().st_size

        return export_config

    def refresh(self):
        """Clear cached data to force re-reading project.vne on next access.
        Use this after creating/modifying files externally so the server
        picks up new assets without needing an engine restart."""
        self._vne_data = None
        self._vne_path = None

    def register_asset(self, relative_path: str, asset_type: str,
                       guid: str = None, size: int = None, mtime: int = None,
                       add_to_open_flows: bool = False) -> Dict:
        """Atomically register a new asset: creates .meta file, adds to project.vne registry.
        
        Args:
            relative_path: e.g. 'flow/校园恋爱.flow'
            asset_type: e.g. 'flow', 'texture', 'audio'
            guid: auto-generated if None
            size: file size in bytes (auto-detected if None)
            mtime: modification time (auto-detected if None)
            add_to_open_flows: if True, prepends to open_flow_guid_list
        Returns:
            Dict with guid, meta_path, and registration status
        """
        import uuid as _uuid
        
        self._ensure_loaded()
        if not self._vne_path:
            return {"error": "No project.vne found"}
        
        base = self._vne_path.parent
        
        # Determine file path
        file_path = base / relative_path
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # Auto-detect size and mtime
        if size is None:
            size = file_path.stat().st_size
        if mtime is None:
            mtime = int(file_path.stat().st_mtime)
        
        # Generate GUID
        if guid is None:
            guid = str(_uuid.uuid4())
        
        # Create .meta file
        meta_path = file_path.parent / (file_path.name + ".meta")
        meta_rel = str(meta_path.relative_to(base)).replace("\\", "/")
        meta_content = {"version": 1, "importer": [], "guid": guid}
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_content, f, ensure_ascii=False)
        
        # Add to project.vne asset_registry
        new_asset = {
            "guid": guid,
            "last_known_relative_path": relative_path.replace("\\", "/"),
            "type": asset_type,
            "last_known_meta_path": meta_rel,
            "file_signature": {"size": size, "mtime": mtime},
        }
        
        assets = self._vne_data.setdefault("asset_registry", {}).setdefault("assets", [])
        assets.append(new_asset)
        
        # Optionally add to open flows
        if add_to_open_flows and asset_type == "flow":
            open_flows = self._vne_data.setdefault("open_flow_guid_list", [])
            if guid not in open_flows:
                open_flows.insert(0, guid)
        
        # Write back project.vne
        with open(self._vne_path, 'w', encoding='utf-8') as f:
            json.dump(self._vne_data, f, ensure_ascii=False, separators=(',', ':'))
        
        return {
            "status": "registered",
            "guid": guid,
            "relative_path": relative_path,
            "type": asset_type,
            "meta_path": meta_rel,
            "size": size,
            "mtime": mtime,
        }

    def validate_flow(self, flow_path: str) -> Dict:
        """Validate a .flow file for structural correctness.
        
        Checks:
        - Valid JSON
        - All nodes have valid type_ids
        - All input pins (except entry) have 'key' fields
        - show_choice_button uses correct output keys (choice_1..5 not route_1..5)
        - merge_flow inputs have explicit keys
        - All links reference existing pin IDs
        Returns validation result with errors/warnings list.
        """
        self._ensure_loaded()
        base = self._vne_path.parent if self._vne_path else Path(".")
        full_path = base / flow_path
        
        if not full_path.exists():
            return {"valid": False, "errors": [f"File not found: {full_path}"]}
        
        try:
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                flow = json.load(f)
        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Invalid JSON: {e}"]}
        
        errors = []
        warnings = []
        
        nodes = flow.get("node_pool", [])
        links = flow.get("link_pool", [])
        
        # Collect all pin IDs
        all_pin_ids = set()
        node_by_id = {}
        for node in nodes:
            nid = node.get("id")
            node_by_id[nid] = node
            for p in node.get("input_pin_list", []):
                all_pin_ids.add(p["id"])
            for p in node.get("output_pin_list", []):
                all_pin_ids.add(p["id"])
        
        # Known valid type_ids (from application/node/builtin/)
        known_types = self._discover_node_types()
        
        for node in nodes:
            nid = node.get("id", "?")
            tid = node.get("type_id", "")
            
            if not tid:
                errors.append(f"Node {nid}: missing type_id")
                continue
            
            if known_types and tid not in known_types:
                warnings.append(f"Node {nid}: unknown type_id '{tid}' (may be custom)")
            
            # Check input pins for keys
            for p in node.get("input_pin_list", []):
                if "key" not in p:
                    if tid == "merge_flow":
                        errors.append(
                            f"Node {nid} (merge_flow): input pin {p['id']} missing 'key'. "
                            "merge_flow inputs require explicit keys — this causes crashes!"
                        )
                    else:
                        errors.append(f"Node {nid} ({tid}): input pin {p['id']} missing 'key'")
            
            # Check output pins for keys (entry is exception)
            for p in node.get("output_pin_list", []):
                if "key" not in p and tid != "entry":
                    errors.append(f"Node {nid} ({tid}): output pin {p['id']} missing 'key'")
            
            # Check show_choice_button output keys
            if tid == "show_choice_button":
                out_keys = [p.get("key", "") for p in node.get("output_pin_list", [])]
                for i, k in enumerate(out_keys):
                    expected = f"choice_{i+1}"
                    if k and k != expected and k.startswith("route_"):
                        errors.append(
                            f"Node {nid} (show_choice_button): output key '{k}' should be '{expected}'. "
                            "Using 'route_N' causes crashes! VNE expects 'choice_N'."
                        )
        
        # Validate links — also detect non-integer pin IDs (common bug)
        for link in links:
            lid = link.get("id", "?")
            out_pin = link.get("output_pin_id")
            in_pin = link.get("input_pin_id")
            
            if not isinstance(out_pin, int):
                errors.append(
                    f"Link {lid}: output_pin_id is {type(out_pin).__name__}, expected int. "
                    "Did you pass a dict (e.g. output_map) instead of a pin ID (e.g. output_map['out'])?"
                )
            elif out_pin not in all_pin_ids:
                errors.append(f"Link {lid}: output_pin_id {out_pin} not found in any node")
            
            if not isinstance(in_pin, int):
                errors.append(
                    f"Link {lid}: input_pin_id is {type(in_pin).__name__}, expected int. "
                    "Did you pass a dict (e.g. input_map) instead of a pin ID (e.g. input_map['in'])?"
                )
            elif in_pin not in all_pin_ids:
                errors.append(f"Link {lid}: input_pin_id {in_pin} not found in any node")
        
        # Performance warning: VNE editor struggles with >80 nodes
        if len(nodes) > 80:
            warnings.append(
                f"Flow has {len(nodes)} nodes — VNE editor may crash or freeze when opening. "
                "Limit: 80 nodes per .flow file. Split into multiple smaller scenes using switch_scene."
            )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "node_count": len(nodes),
            "link_count": len(links),
            "known_node_types": len(known_types) if known_types else 0,
        }

    def list_node_types(self) -> List[Dict]:
        """Discover all available flow node type_ids and their pin schemas
        by scanning application/node/builtin/."""
        self._ensure_loaded()
        return self._discover_node_types_detailed()

    def _discover_node_types(self) -> set:
        """Quick scan: return set of known type_ids."""
        types = set()
        self._ensure_loaded()
        base = self._vne_path.parent if self._vne_path else Path(".")
        node_dir = base / "application" / "node" / "builtin"
        if not node_dir.exists():
            return types
        
        for lua_file in node_dir.rglob("*.lua"):
            try:
                content = lua_file.read_text(encoding='utf-8-sig', errors='ignore')
                # Extract type_id from Lua node definition
                m = re.search(r'type_id\s*=\s*"([^"]+)"', content)
                if m:
                    types.add(m.group(1))
            except Exception:
                pass
        return types

    def _discover_node_types_detailed(self) -> List[Dict]:
        """Detailed scan: return type_id, name, category, inputs, outputs."""
        result = []
        self._ensure_loaded()
        base = self._vne_path.parent if self._vne_path else Path(".")
        node_dir = base / "application" / "node" / "builtin"
        if not node_dir.exists():
            return result
        
        for lua_file in sorted(node_dir.rglob("*.lua")):
            try:
                content = lua_file.read_text(encoding='utf-8-sig', errors='ignore')
                
                # Extract type_id
                m_type = re.search(r'type_id\s*=\s*"([^"]+)"', content)
                if not m_type:
                    continue
                type_id = m_type.group(1)
                
                # Extract name (Chinese display name)
                m_name = re.search(r'name\s*=\s*"([^"]+)"', content)
                name = m_name.group(1) if m_name else type_id
                
                # Extract category
                m_cat = re.search(r'category\s*=\s*"([^"]+)"', content)
                category = m_cat.group(1) if m_cat else ""
                
                # Extract inputs (add_input calls)
                inputs = []
                for m in re.finditer(r'add_input\(\s*\{([^}]+)\}', content):
                    pin_def = m.group(1)
                    m_k = re.search(r'key\s*=\s*"([^"]+)"', pin_def)
                    m_t = re.search(r'type_id\s*=\s*"([^"]+)"', pin_def)
                    m_n = re.search(r'name\s*=\s*"([^"]+)"', pin_def)
                    inputs.append({
                        "key": m_k.group(1) if m_k else "(auto)",
                        "type_id": m_t.group(1) if m_t else "?",
                        "name": m_n.group(1) if m_n else "",
                    })
                
                # Extract outputs (add_output calls)
                outputs = []
                for m in re.finditer(r'add_output\(\s*\{([^}]+)\}', content):
                    pin_def = m.group(1)
                    m_k = re.search(r'key\s*=\s*"([^"]+)"', pin_def)
                    m_t = re.search(r'type_id\s*=\s*"([^"]+)"', pin_def)
                    m_n = re.search(r'name\s*=\s*"([^"]+)"', pin_def)
                    outputs.append({
                        "key": m_k.group(1) if m_k else "(auto)",
                        "type_id": m_t.group(1) if m_t else "?",
                        "name": m_n.group(1) if m_n else "",
                    })
                
                result.append({
                    "type_id": type_id,
                    "name": name,
                    "category": category,
                    "inputs": inputs,
                    "outputs": outputs,
                })
            except Exception:
                pass
        
        return result


# ---------------------------------------------------------------------------
# MCP HTTP/SSE Transport (TCP mode)
# ---------------------------------------------------------------------------

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP over SSE transport."""

    server_state: 'MCPHTTPServer' = None

    def log_message(self, format, *args):
        """Log to stderr for VNE console capture."""
        msg = f"[MCP HTTP] {self.client_address[0]}: {format % args}"
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
        # Also write to server log
        if self.server_state:
            self.server_state.log(msg)

    def do_GET(self):
        if self.path == '/sse':
            self._handle_sse()
        elif self.path == '/health':
            self._handle_health()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/message':
            self._handle_message()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _handle_health(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "name": self.server_state.name}).encode())

    def _handle_sse(self):
        """SSE endpoint: server → client messages."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        client_id = f"{self.client_address[0]}:{self.client_address[1]}"
        self.server_state.register_sse(client_id, self)

        try:
            # Send initial endpoint event
            self.wfile.write(f"event: endpoint\ndata: /message\n\n".encode())
            self.wfile.flush()

            # Keep connection alive, check for messages
            while self.server_state.running:
                msg = self.server_state.get_sse_message(client_id)
                if msg:
                    try:
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                    except BrokenPipeError:
                        break
                else:
                    time.sleep(0.1)
        except Exception:
            pass
        finally:
            self.server_state.unregister_sse(client_id)

    def _handle_message(self):
        """POST endpoint: client → server messages."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            msg = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        # Process through the MCP server
        response = self.server_state.process_message(msg)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if response:
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())


class MCPHTTPServer:
    """MCP Server over HTTP (SSE transport)."""

    def __init__(self, mcp_server: MCPServer, host: str = "127.0.0.1", port: int = 8765):
        self.mcp = mcp_server
        self.host = host
        self.port = port
        self.name = mcp_server.name
        self.running = False
        self._httpd: Optional[HTTPServer] = None
        self._sse_clients: Dict[str, MCPHTTPHandler] = {}
        self._sse_queues: Dict[str, list] = {}
        self._lock = threading.Lock()
        self._log_lines: List[str] = []

    def log(self, msg: str):
        self._log_lines.append(msg)
        # Print to stdout for VNE Lua host to capture
        print(msg, flush=True)

    def register_sse(self, client_id: str, handler: MCPHTTPHandler):
        with self._lock:
            self._sse_clients[client_id] = handler
            self._sse_queues[client_id] = []
        self.log(f"[VNE_MCP] Client connected: {client_id}")

    def unregister_sse(self, client_id: str):
        with self._lock:
            self._sse_clients.pop(client_id, None)
            self._sse_queues.pop(client_id, None)
        self.log(f"[VNE_MCP] Client disconnected: {client_id}")

    def get_sse_message(self, client_id: str) -> Optional[str]:
        with self._lock:
            queue = self._sse_queues.get(client_id)
            if queue:
                return queue.pop(0)
        return None

    def send_to_client(self, client_id: str, msg: str):
        with self._lock:
            queue = self._sse_queues.get(client_id)
            if queue is not None:
                queue.append(msg)

    def broadcast(self, msg: str):
        with self._lock:
            for client_id in self._sse_queues:
                self._sse_queues[client_id].append(msg)

    def process_message(self, msg: Dict) -> Optional[Dict]:
        """Process an incoming MCP message, return response if applicable."""
        method = msg.get("method", "")

        # We need to intercept the write and response sending
        # For TCP mode, we collect the response manually
        if method == "initialize":
            result = {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.mcp.name, "version": self.mcp.version},
                "instructions": "VNE MCP Server — provides 15 tools for VoidNovelEngine projects. Use vne_project_info first to get an overview, vne_list_node_types to see available flow nodes, vne_validate_flow before opening generated .flow files, vne_refresh_assets after creating files externally.",
            }
            msg_id = msg.get("id")
            return {"jsonrpc": "2.0", "id": msg_id, "result": result} if msg_id is not None else None

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            tools_list = []
            for t in self.mcp.tools.values():
                tools_list.append({
                    "name": t["name"],
                    "description": t["description"],
                    "inputSchema": t["inputSchema"],
                })
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"tools": tools_list}}

        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            tool = self.mcp.tools.get(tool_name)
            if not tool:
                return {"jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}

            try:
                result = tool["handler"](arguments)
                if isinstance(result, list):
                    content = result
                elif isinstance(result, dict) and "content" in result:
                    content = result["content"]
                else:
                    content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"content": content}}
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                return {"jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32000, "message": f"Tool error: {e}"}}

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}}

        else:
            return {"jsonrpc": "2.0", "id": msg.get("id"),
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}}

    def start(self):
        """Start the HTTP server in a background thread."""
        # Create handler class with reference to this server
        handler = type('Handler', (MCPHTTPHandler,), {'server_state': self})

        self._httpd = HTTPServer((self.host, self.port), handler)
        self.running = True

        # Ready signal - VNE Lua host watches for this
        ready_msg = f"VNE_MCP_READY host={self.host} port={self.port}"
        print(ready_msg, flush=True)
        sys.stderr.write(ready_msg + "\n")
        sys.stderr.flush()

        self.log(f"[VNE_MCP] Server started on http://{self.host}:{self.port}")
        self.log(f"[VNE_MCP] SSE endpoint: http://{self.host}:{self.port}/sse")
        self.log(f"[VNE_MCP] Message endpoint: http://{self.host}:{self.port}/message")

        try:
            self._httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            self._httpd.server_close()
            self.log("[VNE_MCP] Server stopped")

    def stop(self):
        self.running = False
        if self._httpd:
            self._httpd.shutdown()

    def get_logs(self) -> List[str]:
        return list(self._log_lines)


# ---------------------------------------------------------------------------\n# Server Setup\n# ---------------------------------------------------------------------------

def create_server(project_path: str = None) -> MCPServer:
    """Create and configure the VNE MCP server with all tools."""

    if project_path is None:
        project_path = os.getcwd()

    project = VNEProject(project_path)

    server = MCPServer(name="vne-mcp-server", version="1.2.1")

    # --- Tool: vne_project_info ---
    server.register_tool(
        name="vne_project_info",
        description="Get VoidNovelEngine project information: project version, asset counts, paths, and resource type breakdown.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(project.get_info(), ensure_ascii=False, indent=2)}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_list_resources ---
    server.register_tool(
        name="vne_list_resources",
        description="List all resources in the VNE project from the asset registry. Filter by type: texture, audio, video, font, shader, flow, style, ui, save_profile.",
        input_schema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Filter by resource type (e.g. texture, audio, flow, style)"
                }
            },
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.list_resources(args.get("type")),
                ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_read_file ---
    server.register_tool(
        name="vne_read_file",
        description="Read a file from the VNE project by its relative path (e.g., 'main.lua', 'application/framework/flow_manager.lua').",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file within the project"
                }
            },
            "required": ["path"],
        },
        handler=lambda args: [
            {"type": "text", "text": project.read_file(args["path"]) or f"File not found: {args['path']}"}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_list_directory ---
    server.register_tool(
        name="vne_list_directory",
        description="List contents of a directory within the VNE project.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to directory (default: project root)"
                }
            },
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.list_directory(args.get("path", ".")),
                ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_search ---
    server.register_tool(
        name="vne_search",
        description="Search for text in VNE project files. Searches Lua scripts by default.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for (case-insensitive)"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File glob pattern (default: *.lua)"
                }
            },
            "required": ["query"],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.search(args["query"], args.get("file_pattern", "*.lua")),
                ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_get_resource ---
    server.register_tool(
        name="vne_get_resource",
        description="Get detailed information about a specific resource by its GUID, including .meta file content.",
        input_schema={
            "type": "object",
            "properties": {
                "guid": {
                    "type": "string",
                    "description": "Resource GUID (UUID format)"
                }
            },
            "required": ["guid"],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.get_resource_detail(args["guid"]) or {"error": "Resource not found"},
                ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_lua_api ---
    server.register_tool(
        name="vne_lua_api",
        description="Get the VoidNovelEngine Lua API reference, including engine modules, framework modules, project structure, and resource type mappings. Use this to understand how to write code for VNE.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(project.get_lua_api(), ensure_ascii=False, indent=2)}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_export_config ---
    server.register_tool(
        name="vne_export_config",
        description="Get the current VNE project export configuration (title, entry flow, settings, VPak status).",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(project.get_export_config(), ensure_ascii=False, indent=2)}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_pack_resources ---
    server.register_tool(
        name="vne_pack_resources",
        description="Run VPak resource packaging for the VNE project. Bundles loose resource files into encrypted .vpak archives for release distribution.",
        input_schema={
            "type": "object",
            "properties": {
                "source_dir": {
                    "type": "string",
                    "description": "Path to resources directory (default: application/resources)"
                },
                "output": {
                    "type": "string",
                    "description": "Output .vpak file path (default: application/resources.vpak)"
                },
                "key": {
                    "type": "string",
                    "description": "Encryption key for XOR cipher (default: built-in key)"
                },
                "compress": {
                    "type": "boolean",
                    "description": "Enable zlib compression (requires Python zlib)"
                },
            },
            "required": [],
        },
        handler=lambda args: _handle_pack(project, args),
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )

    # --- Tool: vne_read_vpak ---
    server.register_tool(
        name="vne_read_vpak",
        description="List or extract files from a VPak archive.",
        input_schema={
            "type": "object",
            "properties": {
                "archive": {
                    "type": "string",
                    "description": "Path to .vpak file"
                },
                "action": {
                    "type": "string",
                    "enum": ["list", "extract"],
                    "description": "Action: list contents or extract a file"
                },
                "file_path": {
                    "type": "string",
                    "description": "Relative path of file to extract (for extract action)"
                },
                "key": {
                    "type": "string",
                    "description": "Decryption key (required for encrypted archives)"
                },
            },
            "required": ["archive", "action"],
        },
        handler=lambda args: _handle_vpak(args),
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_console_log ---
    server.register_tool(
        name="vne_console_log",
        description="Get the VNE editor console log. Reads the real-time console output captured by the MCP runtime bridge (mcp_host.lua). Returns log entries as JSON lines with timestamp, level, and message. Use this to see editor errors, warnings, and status messages.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recent entries to return (default: 50, max: 500)",
                    "default": 50,
                },
                "level": {
                    "type": "string",
                    "enum": ["info", "warning", "error", "success", "debug"],
                    "description": "Filter by log level (default: all)",
                },
                "since": {
                    "type": "integer",
                    "description": "Return only entries with index >= since. Use 0 for all. (default: 0)",
                },
            },
        },
        handler=lambda args: _handle_console_log(project, args),
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_refresh_assets (NEW in 1.2.0) ---
    server.register_tool(
        name="vne_refresh_assets",
        description="Refresh the asset cache so newly created or modified files are visible without restarting the VNE editor. Call this after creating .vns, .flow, .meta files or modifying project.vne externally.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                _handle_refresh(project), ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )

    # --- Tool: vne_register_asset (NEW in 1.2.0) ---
    server.register_tool(
        name="vne_register_asset",
        description="Register a new asset file in the VNE project atomically: creates the .meta file, adds it to project.vne's asset registry, and optionally adds to open_flow_guid_list. Use this instead of manually editing project.vne.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the asset file (e.g. 'flow/校园恋爱.flow')"
                },
                "type": {
                    "type": "string",
                    "description": "Asset type: flow, texture, audio, video, font, shader, style, ui, save_profile"
                },
                "guid": {
                    "type": "string",
                    "description": "Optional GUID. Auto-generated UUID if omitted."
                },
                "add_to_open_flows": {
                    "type": "boolean",
                    "description": "If true, also prepend to open_flow_guid_list (for flow type assets)"
                },
            },
            "required": ["path", "type"],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.register_asset(
                    relative_path=args["path"],
                    asset_type=args["type"],
                    guid=args.get("guid"),
                    add_to_open_flows=args.get("add_to_open_flows", False),
                ), ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": False, "destructiveHint": True},
    )

    # --- Tool: vne_validate_flow (NEW in 1.2.0) ---
    server.register_tool(
        name="vne_validate_flow",
        description="Validate a .flow file before opening it in the VNE editor. Checks for: valid JSON, correct pin keys (especially choice_N for show_choice_button), merge_flow input keys, missing pin keys, and broken link references. Use this after generating .flow files to prevent crashes.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the .flow file (e.g. 'application/resources/flow/校园恋爱.flow')"
                },
            },
            "required": ["path"],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.validate_flow(args["path"]), ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    # --- Tool: vne_list_node_types (NEW in 1.2.0) ---
    server.register_tool(
        name="vne_list_node_types",
        description="List all available flow node type_ids with their pin schemas (inputs/outputs). Use this before generating .flow files to ensure correct pin keys and avoid crashes from wrong pin names.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda args: [
            {"type": "text", "text": json.dumps(
                project.list_node_types(), ensure_ascii=False, indent=2
            )}
        ],
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )

    return server


def _handle_pack(project: VNEProject, args: Dict) -> List[Dict]:
    """Handle the vne_pack_resources tool."""
    import subprocess

    project._ensure_loaded()
    base = project._vne_path.parent if project._vne_path else Path(os.getcwd())

    source_dir = args.get("source_dir", "application/resources")
    output = args.get("output", "application/resources.vpak")
    key = args.get("key")
    compress = args.get("compress", False)

    source_full = base / source_dir
    output_full = base / output

    if not source_full.exists():
        return [{"type": "text", "text": f"Source directory not found: {source_full}"}]

    # Try Python packager first
    packager_path = base / "tools" / "vne-packager" / "vpak.py"
    cmd = [sys.executable, str(packager_path), "pack", str(source_full), str(output_full)]
    if key:
        cmd.extend(["--key", key])
    if not compress:
        cmd.append("--no-compress")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return [{"type": "text", "text": result.stdout + "\n" + result.stderr}]
    except FileNotFoundError:
        # Fall back to pure-Lua style packing via the engine
        # For now, just report the command that would be run
        return [{"type": "text", "text": json.dumps({
            "status": "packager_not_found",
            "command": " ".join(cmd),
            "hint": "Run this command directly or use the Lua export pipeline (window_exporter.lua) which has a built-in pure-Lua packer.",
            "source_dir": str(source_full),
            "output": str(output_full),
        }, ensure_ascii=False, indent=2)}]
    except Exception as e:
        return [{"type": "text", "text": f"Packaging failed: {e}"}]


def _handle_vpak(args: Dict) -> List[Dict]:
    """Handle the vne_read_vpak tool."""
    archive = args["archive"]
    action = args["action"]

    if not os.path.exists(archive):
        return [{"type": "text", "text": f"Archive not found: {archive}"}]

    # Use the Python packager module
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    parent_tools = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vne-packager")
    sys.path.insert(0, parent_tools)

    try:
        import vpak
        if action == "list":
            entries = vpak.list_contents(archive)
            return [{"type": "text", "text": json.dumps({
                "archive": archive,
                "file_count": len(entries),
                "entries": entries,
            }, ensure_ascii=False, indent=2)}]
        elif action == "extract":
            file_path = args.get("file_path", "")
            key = args.get("key")
            data = vpak.read_file_by_path(archive, key, file_path)
            if data is None:
                return [{"type": "text", "text": f"File not found: {file_path}"}]
            # Return as text if it looks like text, otherwise base64
            try:
                text = data.decode('utf-8')
                return [{"type": "text", "text": text}]
            except UnicodeDecodeError:
                import base64
                b64 = base64.b64encode(data).decode('ascii')
                return [{"type": "text", "text": f"[Binary data, {len(data)} bytes, base64]\n{b64}"}]
    except ImportError:
        return [{"type": "text", "text": "VPak module not available. Ensure tools/vne-packager/vpak.py exists."}]
    except Exception as e:
        return [{"type": "text", "text": f"VPak operation failed: {e}"}]


def _handle_console_log(project: 'VNEProject', args: Dict) -> List[Dict]:
    """Handle the vne_console_log tool — read editor console log file."""
    base = project._vne_path.parent if project._vne_path else Path(os.getcwd())
    log_file = base / "save" / "diagnostics" / "mcp_console.jsonl"

    if not log_file.exists():
        return [{"type": "text", "text": json.dumps({
            "status": "no_log_file",
            "hint": "Console log file not found. The VNE editor must be running with the MCP Console Bridge (mcp_host.lua). Restart the VNE editor after updating mcp_host.lua.",
            "expected_path": str(log_file),
        }, ensure_ascii=False, indent=2)}]

    limit = min(args.get("limit", 50), 500)
    level_filter = args.get("level")
    since = args.get("since", 0)

    try:
        raw = log_file.read_text(encoding="utf-8")
    except Exception as e:
        return [{"type": "text", "text": json.dumps({
            "status": "read_error",
            "error": str(e),
        }, ensure_ascii=False)}]

    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    entries = []
    parse_errors = 0

    for i, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            parse_errors += 1
            continue

        if since > 0 and i < since:
            continue
        if level_filter and entry.get("level") != level_filter:
            continue
        entries.append(entry)

    # Apply limit (most recent entries)
    if len(entries) > limit:
        entries = entries[-limit:]

    return [{"type": "text", "text": json.dumps({
        "status": "ok",
        "total_lines": len(lines),
        "returned": len(entries),
        "parse_errors": parse_errors,
        "log_file": str(log_file),
        "file_size": log_file.stat().st_size if log_file.exists() else 0,
        "entries": entries,
    }, ensure_ascii=False, indent=2)}]


def _handle_refresh(project: 'VNEProject') -> Dict:
    """Handle the vne_refresh_assets tool — clear cache for re-reading."""
    project.refresh()
    # Force re-read to confirm
    info = project.get_info()
    return {
        "status": "refreshed",
        "message": "Asset cache cleared. Project re-loaded.",
        "total_assets": info.get("total_assets", 0),
        "resource_counts": info.get("resource_counts", {}),
    }


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="VoidNovelEngine MCP Server")
    parser.add_argument("--project-path", "-p", help="Path to VNE project directory")
    parser.add_argument("--port", type=int, default=0, help="Run in TCP/HTTP mode on given port (default: 8765 if --port specified without value)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind in TCP mode (default: 127.0.0.1)")
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode (default if --port not set)")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    parser.add_argument("--info", action="store_true", help="Show project info and exit")
    parser.add_argument("--resources", help="List resources of given type and exit")
    args = parser.parse_args()

    project_path = args.project_path or os.getcwd()
    project = VNEProject(project_path)

    if args.list_tools:
        server = create_server(project_path)
        print("Available VNE MCP Tools:")
        for name, tool in server.tools.items():
            print(f"  {name}: {tool['description'][:100]}")
        return

    if args.info:
        print(json.dumps(project.get_info(), ensure_ascii=False, indent=2))
        return

    if args.resources is not None:
        resource_type = args.resources if args.resources else None
        print(json.dumps(project.list_resources(resource_type), ensure_ascii=False, indent=2))
        return

    # Run MCP server
    mcp = create_server(project_path)

    if args.port > 0:
        # TCP/HTTP mode
        port = args.port if args.port else 8765
        host = args.host or "127.0.0.1"
        http_server = MCPHTTPServer(mcp, host=host, port=port)
        sys.stderr.write(f"[VNE_MCP] Starting TCP/HTTP mode...\n")
        sys.stderr.write(f"[VNE_MCP] Binding to {host}:{port}\n")
        sys.stderr.flush()
        http_server.start()
    else:
        # Stdio mode (default for MCP clients like Claude Desktop)
        sys.stderr.write("[VNE_MCP] Starting stdio mode...\n")
        sys.stderr.flush()
        mcp.run()


if __name__ == "__main__":
    main()
