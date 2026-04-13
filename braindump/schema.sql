-- BrainDump (v3) - Core SQLite Schema

-- 1. Memory Entries: Index for all VFS nodes
CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    layer TEXT NOT NULL,
    entity_id TEXT,
    content_path TEXT,
    summary TEXT,
    confidence REAL DEFAULT 1.0,
    trust_level TEXT DEFAULT 'unverified',
    memory_score REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    state TEXT DEFAULT 'active'
);

-- 2. Entities: Canonical names and aliases for graph resolution
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    type TEXT, -- user | task | project | document | concept
    canonical_name TEXT,
    aliases TEXT, -- JSON array of aliases
    confidence REAL DEFAULT 1.0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Relations: Semantic graph overlay
CREATE TABLE IF NOT EXISTS relations (
    source_id TEXT,
    target_id TEXT,
    relation_type TEXT, -- supports | contradicts | derives_from | caused_by
    weight REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, target_id, relation_type)
);

-- 4. Decisions: Outcome-based strategy memory
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    decision TEXT,
    reasoning_summary TEXT,
    chosen_action TEXT,
    outcome_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Policies: Behavioral rules (Governance Layer)
CREATE TABLE IF NOT EXISTS policies (
    id TEXT PRIMARY KEY,
    condition TEXT, -- JSON logic/rule
    action TEXT, -- JSON behavioral change
    priority REAL DEFAULT 0.5,
    confidence REAL DEFAULT 0.8,
    source TEXT DEFAULT 'system', -- system | dna | dream | user
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_applied DATETIME
);
