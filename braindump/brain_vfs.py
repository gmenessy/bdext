# 🧠 BrainDump (v3) - VFS Kernel Implementation
import os
import json
import sqlite3
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List

@dataclass
class VFSNode:
    path: str
    layer: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_json(self) -> str:
        return json.dumps({
            "path": self.path,
            "layer": self.layer,
            "content": self.content,
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat()
        }, indent=2)

class SQLiteMetadataBackend:
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with open("schema.sql", "r") as f:
            schema = f.read()
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)

    def index_node(self, node: VFSNode):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memory_entries (id, layer, content_path, summary, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (node.path, node.layer, node.path.replace("vfs://", ""), node.metadata.get("summary", ""), node.updated_at.isoformat()))

class FileStorageBackend:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir

    def _resolve_path(self, vfs_path: str) -> str:
        relative_path = vfs_path.replace("vfs://", "")
        return os.path.join(self.root_dir, relative_path)

    def write(self, node: VFSNode):
        full_path = self._resolve_path(node.path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Prefer Markdown for core/wiki/dumps
        if node.path.endswith(".md") or node.layer in ["core", "wiki", "dumps"]:
            ext = ".md" if not full_path.endswith(".md") else ""
            with open(full_path + ext, "w") as f:
                if isinstance(node.content, str):
                    f.write(node.content)
                else:
                    f.write(json.dumps(node.content, indent=2))
        else:
            with open(full_path, "w") as f:
                f.write(json.dumps(node.content, indent=2))

    def read(self, vfs_path: str) -> Optional[VFSNode]:
        full_path = self._resolve_path(vfs_path)
        if not os.path.exists(full_path):
            if os.path.exists(full_path + ".md"):
                full_path += ".md"
            else:
                return None
        
        layer = vfs_path.split("/")[2] if "vfs://" in vfs_path else "unknown"
        with open(full_path, "r") as f:
            content = f.read()
            # Try to parse as JSON if not markdown
            if not full_path.endswith(".md"):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
        
        return VFSNode(path=vfs_path, layer=layer, content=content)

class BrainVFS:
    def __init__(self, root_dir: str = ".", vector_service=None):
        self.storage = FileStorageBackend(root_dir)
        self.metadata = SQLiteMetadataBackend(os.path.join(root_dir, "metadata.db"))
        self.vector_service = vector_service

    def write(self, node: VFSNode):
        """Write a node to physical storage, index metadata, and index vectors."""
        self.storage.write(node)
        self.metadata.index_node(node)
        if self.vector_service:
            # Index vector content (as string)
            content_str = str(node.content) if not isinstance(node.content, str) else node.content
            self.vector_service.index_content(node.path, content_str)

    def read(self, vfs_path: str) -> Optional[VFSNode]:
        """Read a node from storage and update usage stats."""
        with sqlite3.connect(self.metadata.db_path) as conn:
            conn.execute("""
                UPDATE memory_entries 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (vfs_path,))
        return self.storage.read(vfs_path)

    def promote(self, source_vfs_path: str, target_vfs_path: str):
        """Promote a node (e.g., from Dump to Wiki)."""
        node = self.read(source_vfs_path)
        if node:
            promoted_node = VFSNode(
                path=target_vfs_path,
                layer=target_vfs_path.split("/")[2],
                content=node.content,
                metadata=node.metadata.copy()
            )
            self.write(promoted_node)

    def snapshot(self, namespace: str) -> str:
        """Create a timestamped snapshot of a namespace."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = f"snapshots/{namespace}_{timestamp}"
        source_dir = os.path.join(self.storage.root_dir, namespace)
        target_dir = os.path.join(self.storage.root_dir, snapshot_path)
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, target_dir)
            return f"vfs://{snapshot_path}"
        return ""
