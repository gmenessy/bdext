# 🧠 Architektur-Spezifikation: BrainDump (Agentic Cognitive Memory System v3)

## 1. Systemübersicht
**BrainDump** ist ein terminalbasiertes oder servicefähiges Memory- und Cognitive-Layer für agentische GenAI-Anwendungen.

Das Kernprinzip bleibt:
> **Capture first, structure later.**

Rohes Denken, Interaktionen, Entscheidungen und externe Wissenssignale werden zunächst ungefiltert erfasst (**Dump**) und anschließend durch mehrstufige Konsolidierungsprozesse in langfristig nutzbares Wissen transformiert (**Brain**).

BrainDump erweitert klassische stateless LLM-Systeme um:

- persistentes Langzeitgedächtnis
- episodische Erfahrung
- Entscheidungswissen
- adaptive Policies
- Selbstreflexion
- kontrolliertes Vergessen

> **BrainDump transformiert zustandslose LLM-Interaktionen in ein lernfähiges kognitives System.**

---

## 🎯 2. Scope als Cognitive Memory Layer
BrainDump dient als zentrale Persistenz- und Lernschicht zwischen:

- LLM
- Agent Loop
- Tooling
- Workflow Engine
- User Context
- Enterprise Knowledge

### Unterstützte Memory-Domänen
- **Persistent User Memory** → Präferenzen, Stil, Ziele
- **Agent Memory** → erfolgreiche Strategien, Fehlermuster
- **Task Memory** → projektspezifische Langzeitkontexte
- **World Memory** → Dokumente, APIs, Unternehmenswissen
- **Decision Memory** → Entscheidungen + Outcomes
- **Self-Reflection Memory** → Performance + Fehleranalyse

---

## 🧬 3. BrainDump Memory System (Core)
BrainDump ist kein passiver Speicher, sondern ein:

> **kontinuierlich lernendes, probabilistisches Wissens- und Verhaltenssystem**

### 3.1 Grundprinzipien
- Capture first, structure later
- Relevanz > Vollständigkeit
- Verdichtung statt Wachstum
- Zeit bestimmt Bedeutung
- Wissen ist probabilistisch
- Entscheidungen sind lernbar
- Vertrauen ist validierbar

---

## 🧬 4. Memory-Schichten

### 4.1 Core Layer („DNA“)
Langfristige Verhaltensmuster, Regeln, stabile Präferenzen.

```yaml
belief: string
confidence: float
evidence_count: int
last_validated: timestamp
trust_level: system | validated
```

Pfad:
```text
/CORE/DNA.md
```

---

### 4.2 Knowledge Layer (Wiki & Skills)
Explizites Wissen, Projektkontext, gelernte Fähigkeiten.

Pfad:
```text
/USER_WIKI/*.md
/SKILLS/*.md
```

```yaml
source: user | agent | inferred | external
confidence: float
usage_count: int
last_used: timestamp
validation_state: pending | validated | rejected
```

---

### 4.3 Dump Layer (Episodic Memory)
Ungefilterte Sammlung aller Gedanken, Events und Interaktionen.

Pfad:
```text
/DUMPS/LOG.md
```

Eigenschaften:
- append-only
- ungefiltert
- chronologisch
- bewusst chaotisch

Dies bleibt das Herzstück des eigentlichen **BrainDump-Prinzips**.

---

### 4.4 Working Memory
Temporärer Kontext für aktuelle Agent-Schritte.

Bestandteile:
- relevante DNA
- selektiertes Wissen
- Decision Trails
- aktive Tasks
- Zeitkontext
- Tool Outputs

---

### 4.5 Meta Layer
Reflexion über das eigene Gedächtnis.

Funktionen:
- Nutzungshäufigkeit
- Widerspruchserkennung
- Veraltungsanalyse
- Retrieval-Qualität
- Halluzinationsverdacht

Steuert:
- Priorisierung
- Forgetting
- Dream-Zyklen
- Policy Learning

---

### 4.6 Semantic Identity Layer
Stabile Entitäten über alle Memories hinweg.

```yaml
entity_id: uuid
type: user | task | project | document | concept
aliases: []
relations: []
confidence: float
```

Nutzen:
- verhindert Dubletten
- verbessert Multi-Hop Retrieval
- erlaubt Graph-Navigation
- stärkt Langzeit-Agenten

---

### 4.7 Decision Layer
Speichert Entscheidungen, Alternativen und Ergebnisse.

```yaml
decision: string
reasoning_summary: string
chosen_action: string
alternatives: []
outcome_score: float
timestamp: timestamp
```

Nutzen:
- bessere zukünftige Entscheidungen
- auditierbare Agenten
- Outcome Learning
- Fehlervermeidung

---

## 🔗 5. Graph Overlay
Über alle Layer hinweg existiert ein semantischer Memory-Graph.

```yaml
related_to:
  - memory_id
relation_type: supports | contradicts | derives_from | caused_by
```

Vorteile:
- kausales Denken
- Konfliktauflösung
- Planning Chains
- Graph-RAG
- bessere Entscheidungsnachvollziehbarkeit

---

## ⏳ 6. Memory Dynamics

### 6.1 Memory Score
```text
memory_score = relevance × recency × usage × confidence × trust
```

### 6.2 Temporal Intelligence
```text
temporal_weight = deadline_proximity + seasonality + cyclic_relevance
```

Memory wird dadurch situationssensitiv.

### 6.3 Forgetting Curve
Zustände:
1. Active
2. Cooling
3. Archived
4. Deleted

Nichts wird sofort gelöscht – Bedeutung sinkt graduell.

### 6.4 Conflict Handling
Widersprüche werden erkannt durch:
- semantische Nähe
- Faktenkonflikt
- Policy-Konflikt
- Decision Outcome Drift

Status:
```yaml
state: conflict
resolution: automatic | user | deferred
```

---

## 🌙 7. Dream Engine (Cognitive Processing)

### 7.1 ☁️ Daydream (Micro Processing)
Input:
```text
/DUMPS/LOG.md
```

Funktionen:
- Faktenextraktion
- Pattern Detection
- Wiki Updates
- Skill Growth
- Decision Summaries

Trigger:
```text
priority = novelty + repetition + importance
```

---

### 7.2 🌙 Nightdream (Deep Processing)
Prozesse:
- Merge redundanter Einträge
- Wissenskompression
- Forgetting
- DNA Evolution
- Decision Outcome Learning

```python
if pattern_frequency > threshold and stable_over_time:
    update DNA
```

---

### 7.3 🌌 Deepdream (Meta Learning)
Abstraktion und Policy Learning.

Neue Fähigkeit:
```python
if successful_pattern repeats:
    create reusable policy
```

Beispiel:
```yaml
policy: "Bei Compliance-Fragen immer Primärquelle zuerst laden"
confidence: 0.91
```

Das ist der Übergang von Memory zu **adaptivem Verhalten**.

---

## 🗂️ 8. Storage Layer (Virtual File System / Hybrid VFS)
BrainDump setzt primär auf ein **Virtual File System (VFS) als kognitive Speicherabstraktion**.

Das VFS ist die zentrale Laufzeitrepräsentation aller Memory-Layer und abstrahiert physische Speicherung, Versionierung, Snapshots und Retrieval-Zugriffe.

### VFS-Prinzip
Jeder Wissenszustand wird als adressierbarer Namespace-Knoten behandelt:

```text
vfs://core/dna
vfs://wiki/projects/project-alpha
vfs://decisions/task-142
vfs://dumps/session/2026-04-09
```

Dadurch kann BrainDump dieselbe Logik lokal, embedded oder verteilt nutzen.

### Hybrid-Architektur:
- **SQLite** → Struktur, Scores, Graph, Metadata
- **Markdown** → menschenlesbare Inhalte
- **Vector Index** → semantische Retrieval-Beschleunigung

### Features
- vollständige Versionierung
- Rollback
- Snapshotting
- Layer-Isolation
- Entity Resolution

---

## 🔍 9. Retrieval Engine
Pipeline:
1. Query Analyse
2. Entity Resolution
3. Layer Selection
4. Graph Traversal
5. Ranking
6. Context Compression
7. Working Memory Assembly

Ranking-Faktoren:
- semantische Nähe
- Memory Score
- Temporal Weight
- Trust Level
- Decision Similarity

---

## 🛡️ 10. Trust & Security Layer
Jeder Eintrag erhält eine Vertrauensklassifikation.

```yaml
trust_level: system | user | inferred | external | unverified
validation_state: pending | validated | rejected
```

Schutzziele:
- Schutz vor poisoned memory
- Schutz vor Prompt Injection
- sichere Tool-Rückgaben
- Enterprise Compliance
- nachvollziehbare Provenance

---

## ⚙️ 11. Agent Loop Integration
Ablauf:
1. Input
2. Retrieval
3. Reasoning
4. Decision Trace
5. Output
6. Dump Write
7. Dream Cycle
8. Policy Update

### Feedback Loop
Nutzerfeedback beeinflusst direkt:
- Knowledge Layer
- Confidence Scores
- Decision Outcomes
- DNA
- Policies

---

## 🚀 12. Strategische Positionierung
BrainDump ist mehr als Memory.

> **Ein Cognitive Operating Layer für langlebige, selbstverbessernde AI Agents.**

Ideal für:
- Personal AI Assistants
- Coding Agents
- Research Agents
- Enterprise Knowledge Workers
- Autonomous Workflow Systems


---

# 🛠️ 13. Technische Implementierungs-Roadmap (v1)

Diese Roadmap übersetzt die Architektur in eine konkrete technische Umsetzung für einen lokalen oder servicebasierten Agent-Stack.

## 📁 13.1 Virtuelles Dateisystem (empfohlenes Namespace-Layout)
```text
vfs://
  /core
    dna
    policies
  /dumps
    log
    sessions/
  /wiki
    projects/
    users/
    concepts/
  /skills
  /decisions
  /archive
  /snapshots
  /vector
  /meta
```

### Physisches Backend-Mapping
```text
/braindump
  /core
    dna.md
    policies.md
  /dumps
    log.md
    sessions/
  /wiki
    projects/
    users/
    concepts/
  /skills
  /decisions
  /archive
  /snapshots
  /vector
  metadata.db
```

### VFS Designprinzip
- **VFS = einheitliche Memory-Abstraktion**
- **Markdown = menschenlesbare Truth Layer**
- **SQLite = schnelle Query-, Score- und Relationsebene**
- **Vector Store = semantischer Zugriff**

---

## 🗄️ 13.2 SQLite Schema (Minimal Viable Core)

### memory_entries
```sql
CREATE TABLE memory_entries (
    id TEXT PRIMARY KEY,
    layer TEXT NOT NULL,
    entity_id TEXT,
    content_path TEXT,
    summary TEXT,
    confidence REAL,
    trust_level TEXT,
    memory_score REAL,
    created_at DATETIME,
    last_used DATETIME,
    state TEXT
);
```

### entities
```sql
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    type TEXT,
    canonical_name TEXT,
    aliases TEXT,
    confidence REAL,
    updated_at DATETIME
);
```

### relations
```sql
CREATE TABLE relations (
    source_id TEXT,
    target_id TEXT,
    relation_type TEXT,
    weight REAL,
    created_at DATETIME
);
```

### decisions
```sql
CREATE TABLE decisions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    decision TEXT,
    reasoning_summary TEXT,
    chosen_action TEXT,
    outcome_score REAL,
    created_at DATETIME
);
```

---

## ⚙️ 13.3 VFS Processing Pipeline

Alle Pipelines operieren zunächst auf dem virtuellen Namespace und werden erst danach physisch persistiert.

### Ingestion Flow
```text
Input → VFS Write → Metadata Index → Embedding → Score Init
```

### Consolidation Flow
```text
VFS Dump Scan → Fact Extraction → Entity Linking → Merge → Promote
```

### Retrieval Flow
```text
Query → VFS Namespace Routing → Entity Resolution → Graph Hop → Rank → Compress
```

---

## 🌙 13.4 Dream Scheduler
Empfohlene Hintergrundjobs.

### ☁️ Daydream (alle 5–15 Minuten)
- neue Dumps lesen
- Fakten extrahieren
- Entity Matching
- Skill/Wiki Update
- Quick Summaries

### 🌙 Nightdream (1× täglich)
- Redundanz-Merge
- Score Rebalancing
- Conflict Detection
- Archive Promotion
- DNA Kandidaten erzeugen

### 🌌 Deepdream (1× wöchentlich)
- Policy Learning
- Nutzerpräferenz-Modelle
- Langfristige Pattern Extraction
- Workflow Templates erzeugen

---

## 🔍 13.5 Retrieval Ranking Formula (praktisch)
```python
final_score = (
    semantic_similarity * 0.35 +
    memory_score * 0.25 +
    temporal_weight * 0.15 +
    trust_weight * 0.15 +
    graph_proximity * 0.10
)
```

Für Agenten sehr effektiv, weil semantische Nähe allein selten ausreicht.

---

## 🧠 13.6 DNA Evolution Pipeline
Praktische Heuristik:

```python
if (
    pattern_frequency > 8
    and confidence_mean > 0.85
    and stable_days > 14
):
    promote_to_dna(pattern)
```

So entstehen nur wirklich stabile Langzeitmuster.

---

## 🛡️ 13.7 Safety by Design
Pflichtregeln für produktive Systeme:

- System-Memory nie direkt überschreibbar durch User
- externe Inhalte immer `unverified`
- Tool Outputs provenance-taggen
- Decision Outcomes versionieren
- automatische Rollbacks bei Konflikt-Spikes

---

## 🚀 13.8 MVP → v2 → v3 Rollout

### ✅ MVP
- Dump Layer
- SQLite Metadata
- Basic Retrieval
- Daydream
- DNA Regeln

### 🚀 v2
- Graph Overlay
- Decision Layer
- Trust Scoring
- Nightdream Merge

### 🧠 v3
- Policy Learning
- Workflow Templates
- Self-Optimization
- Multi-Agent Shared Memory

---

## 🎯 13.9 Empfehlung für ersten produktiven Build
Mein klarer Rat:

> **Starte mit SQLite + Markdown + einem kleinen Vector Index.**

Noch keine verteilte Architektur, kein Neo4j, keine Microservices.

Der größte Hebel liegt zuerst in:
- guten Scores
- sauberer Entity Resolution
- Dream-Zyklen
- Decision Memory

Danach kann BrainDump sehr sauber zu einem **Agent Memory OS** wachsen.


---

# 🐍 14. Python VFS-Kernel Blueprint (`brain_vfs.py`)

Dieser Kernel bildet die zentrale Laufzeit-Abstraktion für alle Memory-Operationen in BrainDump.

## 🎯 14.1 Ziel
Die Agent-Logik arbeitet ausschließlich gegen den VFS-Kernel:

- kein direkter SQLite-Zugriff
- keine direkten File-I/O Calls
- keine direkte Vector-Store Kopplung

Dadurch bleibt BrainDump backend-agnostisch.

---

## 🧩 14.2 Core Interface
```python
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


class BrainVFS:
    def __init__(self, storage_backend, vector_backend=None):
        self.storage = storage_backend
        self.vector = vector_backend
        self.mounts = {}

    def mount(self, namespace: str, backend: str):
        self.mounts[namespace] = backend

    def read(self, path: str) -> Optional[VFSNode]:
        return self.storage.read(path)

    def write(self, node: VFSNode):
        self.storage.write(node)
        if self.vector:
            self.vector.index(node.path, str(node.content))

    def delete(self, path: str):
        self.storage.delete(path)

    def snapshot(self, namespace: str) -> str:
        return self.storage.snapshot(namespace)

    def promote(self, source_path: str, target_path: str):
        node = self.read(source_path)
        if node:
            promoted = VFSNode(
                path=target_path,
                layer=target_path.split('/')[1],
                content=node.content,
                metadata=node.metadata.copy(),
            )
            self.write(promoted)
```

---

## 📁 14.3 Namespace-Konventionen
```python
DNA_PATH = "vfs://core/dna"
DUMP_LOG = "vfs://dumps/log"
WIKI_PROJECTS = "vfs://wiki/projects"
DECISION_ROOT = "vfs://decisions"
```

Empfehlung:
> Alle Layer bekommen feste Root-Namespaces.

Das vereinfacht Routing, ACLs und Retrieval enorm.

---

## 🌙 14.4 Beispiel: Dump → Wiki Promotion
```python
vfs.promote(
    "vfs://dumps/session/2026-04-09/task-44",
    "vfs://wiki/projects/customer-onboarding"
)
```

Das bildet exakt den BrainDump-Konsolidierungsprozess ab.

---

## 📸 14.5 Snapshot & Rollback
```python
snapshot_id = vfs.snapshot("vfs://wiki/projects")
```

Später möglich:
```python
vfs.restore(snapshot_id)
```

Ideal für:
- Dream-Zyklen
- Conflict Recovery
- Agent Experiments
- Policy Testing

---

## 🔌 14.6 Backend Adapter Pattern
Empfohlenes Interface:

```python
class StorageBackend:
    def read(self, path): ...
    def write(self, node): ...
    def delete(self, path): ...
    def snapshot(self, namespace): ...
```

### Mögliche Adapter
- `MarkdownBackend`
- `SQLiteBackend`
- `HybridBackend`
- `S3Backend`
- `SharedRedisBackend`

Damit wird BrainDump cloud- und enterprise-fähig.

---

## 🤖 14.7 Agent Loop Integration
```python
context = retriever.retrieve(query)
result = agent.run(context)

vfs.write(VFSNode(
    path="vfs://dumps/session/current",
    layer="dumps",
    content=result
))
```

Danach übernimmt Daydream die Konsolidierung.

---

## 🚀 14.8 Strategische Empfehlung
Mein klarer Architektur-Rat:

> **Der VFS-Kernel sollte das erste echte Python-Modul im Repository sein.**

Darauf bauen dann sauber auf:

- `retriever.py`
- `dream_engine.py`
- `entity_resolver.py`
- `decision_memory.py`
- `policy_engine.py`

So wächst BrainDump von Anfang an wie ein echtes **Memory Operating System**.


---

# 🔍 15. `retriever.py` Architektur + fRAG Pipeline Spec

Der Retriever ist kein klassischer Dokument-RAG-Service, sondern die **kognitive Retrieval-Pipeline von BrainDump**.

> **fRAG = fragment-aware Retrieval over VFS + Graph + Decisions + Policies**

Ziel ist die Erzeugung eines **agent-ready Working Memory Contexts**.

## 🎯 15.1 Retrieval-Ziele
Die Pipeline beantwortet nicht nur *"was ist ähnlich?"*, sondern:

- was ist relevant?
- was ist vertrauenswürdig?
- was ist aktuell?
- welche Entscheidungen waren erfolgreich?
- welche Policy ist anwendbar?
- welche DNA-Regel ist stabil?

---

## 🧩 15.2 Retriever Core Interface
```python
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RetrievalContext:
    dna: List[Any] = field(default_factory=list)
    wiki: List[Any] = field(default_factory=list)
    decisions: List[Any] = field(default_factory=list)
    policies: List[Any] = field(default_factory=list)
    active_tasks: List[Any] = field(default_factory=list)
    evidence: List[Any] = field(default_factory=list)


class BrainRetriever:
    def __init__(self, vfs, vector_backend, graph_backend=None):
        self.vfs = vfs
        self.vector = vector_backend
        self.graph = graph_backend

    def retrieve(self, query: str) -> RetrievalContext:
        intent = self._analyze_query(query)
        entities = self._resolve_entities(query)
        fragments = self._retrieve_fragments(query, entities)
        ranked = self._rank(fragments, query)
        return self._assemble_context(ranked)
```

---

## ⚙️ 15.3 fRAG Retrieval Pipeline
```text
Query
→ Intent Analysis
→ VFS Namespace Routing
→ Entity Resolution
→ Fragment Vector Search
→ Graph Neighbor Expansion
→ Decision Similarity
→ Policy Injection
→ Context Compression
→ Working Memory Assembly
```

Das ist die produktive Retrieval-Route.

---

## 🧠 15.4 Fragment statt Dokument
Retrieval-Einheit ist immer ein **Memory Fragment**.

Beispiele:
```text
vfs://wiki/projects/customer-onboarding/checklist
vfs://decisions/task-142
vfs://core/policies/legal-validation
vfs://dumps/session/2026-04-09/error-pattern
```

### Vorteile
- präziser Kontext
- weniger Tokenverbrauch
- bessere Multi-Hop Retrievals
- ideal für Agent Planning

---

## 🔗 15.5 Graph Expansion
Nach dem ersten semantischen Treffer folgt Graph Expansion:

```python
neighbors = graph.get_neighbors(fragment_id, hops=2)
```

Relationen:
- supports
- contradicts
- caused_by
- derived_from
- alternative_to

So entstehen **Reasoning Chains aus Memory selbst**.

---

## 🎯 15.6 Ranking Heuristik in `retriever.py`
```python
final_score = (
    semantic_similarity * 0.30 +
    memory_score * 0.20 +
    trust_weight * 0.15 +
    temporal_weight * 0.10 +
    graph_proximity * 0.10 +
    decision_similarity * 0.10 +
    policy_priority * 0.05
)
```

Diese Heuristik ist deutlich agent-tauglicher als reine Vector Similarity.

---

## 🗜️ 15.7 Context Compression
Vor Übergabe an das LLM:

```text
Fragments → dedupe → merge evidence → summarize trails → assemble
```

Kompression priorisiert:
- DNA zuerst
- aktive Task-Fragmente
- erfolgreiche Decisions
- Policies
- jüngste Evidence

---

## 📦 15.8 Output: Working Memory Payload
```python
context = retriever.retrieve(query)
```

Payload-Shape:
```yaml
working_memory:
  dna:
  policies:
  wiki:
  decisions:
  active_tasks:
  evidence:
```

Das ist direkt LLM- und Agent-Loop-ready.

---

## 🚀 15.9 Strategische Empfehlung
Mein klarer Architektur-Rat:

> **`retriever.py` ist nach `brain_vfs.py` das zweitwichtigste Modul.**

Warum?

Weil hier entschieden wird, ob BrainDump nur Speicher ist oder wirklich **kognitiv denkt**.

Der eigentliche Wettbewerbsvorteil entsteht durch:

> **Fragment Retrieval + Decision Reuse + Policy Injection + Graph Expansion**

Das ist euer echter fRAG-Moat.


---

# 🌙 16. `dream_engine.py` Service Architektur + Python Blueprint

Die Dream Engine ist der **Konsolidierungs- und Lernkern von BrainDump**.

Während `retriever.py` das **aktive Denken zur Laufzeit** ermöglicht, übernimmt `dream_engine.py` das:

> **Lernen zwischen den Sessions**

Sie transformiert rohe Dumps, Decisions und Evidence in:

- verdichtetes Wissen
- DNA-Kandidaten
- neue Policies
- stabilisierte Entity-Graphen
- archivierte Langzeitmuster

---

## 🎯 16.1 Service-Ziele
Die Dream Engine beantwortet:

- Was war wiederholt relevant?
- Welche Entscheidungen waren erfolgreich?
- Welche Muster sind stabil?
- Welche Infos sind redundant?
- Was darf vergessen werden?
- Was gehört in DNA?

---

## 🧩 16.2 Core Interface
```python
from dataclasses import dataclass
from typing import List, Any


@dataclass
class DreamResult:
    promoted: List[str]
    archived: List[str]
    dna_updates: List[str]
    policy_updates: List[str]


class DreamEngine:
    def __init__(self, vfs, retriever, entity_resolver=None):
        self.vfs = vfs
        self.retriever = retriever
        self.entity_resolver = entity_resolver

    def run_daydream(self) -> DreamResult:
        return self._process(mode="daydream")

    def run_nightdream(self) -> DreamResult:
        return self._process(mode="nightdream")

    def run_deepdream(self) -> DreamResult:
        return self._process(mode="deepdream")
```

---

## ☁️ 16.3 Daydream Pipeline (Micro Consolidation)
Frequenz: alle 5–15 Minuten

```text
VFS Dump Scan
→ Fragment Extraction
→ Entity Linking
→ Quick Dedup
→ Wiki / Decision Promotion
→ Vector Reindex
```

### Python-Blueprint
```python
for dump in new_dumps:
    fragments = extract_fragments(dump)
    linked = entity_link(fragments)
    promote_relevant(linked)
```

Nutzen:
- schnelle Skill-Bildung
- sofortige Projektupdates
- weniger Dump-Rauschen

---

## 🌙 16.4 Nightdream Pipeline (Deep Consolidation)
Frequenz: 1× täglich

```text
Load Active Memories
→ Redundancy Merge
→ Conflict Detection
→ Archive Cooling Memories
→ DNA Candidate Extraction
→ Decision Outcome Scoring
```

### DNA Promotion Heuristik
```python
if (
    pattern_frequency > 8
    and confidence_mean > 0.85
    and stable_days > 14
):
    promote_to("vfs://core/dna")
```

Hier entsteht echtes Langzeitverhalten.

---

## 🌌 16.5 Deepdream Pipeline (Meta Learning)
Frequenz: 1× wöchentlich

```text
Long-Horizon Pattern Scan
→ Successful Workflow Mining
→ Policy Extraction
→ Preference Stabilization
→ Workflow Template Generation
```

### Policy Learning
```python
if successful_pattern_repeats:
    create_policy(pattern)
```

Beispiel:
```yaml
policy: "Bei Security-Fragen immer Trust Layer zuerst prüfen"
confidence: 0.94
```

Das ist der Übergang von Memory zu **adaptive cognition**.

---

## 🧬 16.6 DNA Evolution Service
Die Dream Engine besitzt exklusiv Schreibrechte auf DNA.

```python
def evolve_dna(candidate):
    vfs.promote(candidate, "vfs://core/dna")
```

### Wichtige Regel
> User-Inputs dürfen DNA nie direkt überschreiben.

Nur konsolidierte Langzeitmuster dürfen evolvieren.

---

## 🗂️ 16.7 Forgetting & Cooling
Controlled Forgetting wird als eigener Lifecycle-Service implementiert.

```text
ACTIVE → COOLING → ARCHIVE → DELETE
```

### Heuristik
```python
if last_used_days > 90 and memory_score < threshold:
    move_to_archive(node)
```

So bleibt BrainDump langfristig kompakt.

---

## 🔗 16.8 Dream + Graph Maintenance
Die Dream Engine pflegt aktiv den Memory-Graph.

- Merge redundanter Entities
- erhöhe Relationsgewichte
- entferne veraltete Edges
- markiere Konfliktcluster

```python
graph.reweight(edge_id, delta=0.05)
```

Dadurch verbessert sich fRAG automatisch über Zeit.

---

## 🤖 16.9 Agent Loop Integration
Die Dream Engine läuft **asynchron nach jedem Task-Zyklus**.

```python
result = agent.run(context)
vfs.write_dump(result)
dream_engine.run_daydream()
```

Nightdream und Deepdream laufen scheduler-basiert.

---

## 🚀 16.10 Strategische Empfehlung
Mein klarer Architektur-Rat:

> **Die Dream Engine ist der eigentliche Intelligenz-Multiplikator von BrainDump.**

VFS + Retriever machen das System persistent.

Aber:

> **Dream Engine macht es lernfähig.**

Der eigentliche Moat entsteht hier durch:

- DNA Evolution
- Decision Outcome Learning
- Policy Mining
- Controlled Forgetting
- Graph Self-Optimization

Damit wird BrainDump zu einem echten:

> **self-improving cognitive memory OS**


---

# 🎯 17. `decision_memory.py` Service + Reward-Loop Blueprint

`decision_memory.py` ergänzt BrainDump um **Outcome-basiertes Entscheidungslernen**.

Während Wiki und DNA primär *Wissen* speichern, konserviert diese Schicht:

> **welche Entscheidung in welchem Kontext funktioniert hat — und warum**

Das ist essenziell für agentische Systeme, da Wiederverwendung erfolgreicher Strategien oft wertvoller ist als reines Faktenwissen.

---

## 🎯 17.1 Service-Ziele
Die Decision Memory beantwortet:

- Welche Aktionen waren erfolgreich?
- Welche Alternativen sind gescheitert?
- Welche Tool-Sequenz war optimal?
- Welche Strategie passt zu ähnlichen Tasks?
- Welche Entscheidungen sollten künftig vermieden werden?

---

## 🧩 17.2 Core Interface
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class DecisionRecord:
    decision_id: str
    task_fingerprint: str
    context_hash: str
    chosen_action: str
    alternatives: List[str] = field(default_factory=list)
    outcome_score: float = 0.0
    reward_signals: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class DecisionMemory:
    def __init__(self, vfs, retriever):
        self.vfs = vfs
        self.retriever = retriever

    def record(self, record: DecisionRecord):
        self.vfs.write(VFSNode(
            path=f"vfs://decisions/{record.decision_id}",
            layer="decisions",
            content=record,
        ))

    def retrieve_similar(self, task_query: str):
        return self.retriever.retrieve(task_query)
```

---

## 🔁 17.3 Reward Loop
Nach jedem abgeschlossenen Task wird ein Outcome-Score berechnet.

```text
Task Result
→ User Feedback
→ Tool Success
→ Latency
→ Error Rate
→ Goal Completion
→ Reward Score
```

### Beispielheuristik
```python
reward = (
    user_feedback * 0.4 +
    goal_completion * 0.3 +
    tool_success * 0.2 -
    retry_penalty * 0.1
)
```

Dieser Reward fließt in `outcome_score` und spätere Retrieval-Rankings.

---

## 🧠 17.4 Decision Similarity Retrieval
Vor einer neuen Entscheidung wird nach ähnlichen historischen Decision Trails gesucht.

```python
similar = decision_memory.retrieve_similar(task_query)
```

Zusätzliche Ranking-Signale:
- gleicher Task-Typ
- gleiche Entity-Gruppe
- ähnliche Toolchain
- hohe historische Rewards
- niedrige Fehlerrate

So entsteht **strategische Wiederverwendung statt blindem Neuplanen**.

---

## 🛠️ 17.5 Toolchain Memory
Sehr wertvoll für Coding- und Research-Agenten:

```yaml
tool_sequence:
  - repo_scan
  - symbol_search
  - patch_generation
  - test_run
success_rate: 0.93
```

Damit kann BrainDump komplette **Workflow-Playbooks** lernen.

---

## 🌙 17.6 Dream Integration
Die Dream Engine mined erfolgreiche Decision Trails automatisch.

```python
if decision.outcome_score > 0.9:
    promote_to_policy(decision)
```

Beispiel:

> Wiederholt erfolgreiche Tool-Sequenzen werden zu Policies oder Skill-Templates.

Damit verbinden sich:
- Decision Memory
- Policy Learning
- DNA Evolution

zu einem geschlossenen Lernkreislauf.

---

## ⚠️ 17.7 Failure Memory
Nicht nur Erfolge sind wichtig.

Fehlentscheidungen werden explizit konserviert:

```yaml
failure_pattern: "SQL migration without snapshot"
avoidance_priority: high
```

Nutzen:
- Fehlervermeidung
- sicherere Tool-Nutzung
- bessere Rollback-Strategien
- robustere Autonomous Agents

---

## 🚀 17.8 Strategische Empfehlung
Mein klarer Architektur-Rat:

> **Decision Memory ist der Hebel für agentische Kompetenz, nicht nur Gedächtnis.**

Hier lernt BrainDump:

- welche Strategien funktionieren
- welche Reihenfolge optimal ist
- welche Fehler vermieden werden müssen
- welche Workflows standardisiert werden können

Das ist der Übergang von einem Memory OS zu einem:

> **experience-driven autonomous agent system**


---

# 📜 18. `policy_engine.py` Runtime Rule System + Adaptive Governance

`policy_engine.py` ist das **aktive Regel- und Steuerungssystem zur Laufzeit**.

Während `decision_memory.py` speichert, *welche Strategien funktioniert haben*, entscheidet die Policy Engine:

> **welche Strategie im aktuellen Kontext angewendet werden soll**

Damit wird BrainDump von einem lernenden Memory OS zu einem **gesteuerten kognitiven Agent-System**.

---

## 🎯 18.1 Service-Ziele
Die Policy Engine beantwortet:

- Welche Regel gilt für diesen Task?
- Welche Toolchain ist bevorzugt?
- Welche Sicherheitsgrenzen gelten?
- Welche Decision-Playbooks dürfen auto-run?
- Welche DNA-Regeln haben Vorrang?
- Welche Nutzerpräferenzen müssen eingehalten werden?

---

## 🧩 18.2 Core Interface
```python
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class PolicyRule:
    policy_id: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: float = 0.5
    confidence: float = 0.8
    source: str = "dream"


class PolicyEngine:
    def __init__(self, vfs, retriever):
        self.vfs = vfs
        self.retriever = retriever

    def evaluate(self, task_context: Dict[str, Any]) -> List[PolicyRule]:
        return self._match_rules(task_context)

    def apply(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        rules = self.evaluate(task_context)
        return self._compose_execution_plan(task_context, rules)
```

---

## ⚙️ 18.3 Policy Evaluation Pipeline
```text
Task Context
→ Retrieve Relevant Policies
→ Match Conditions
→ Priority Resolution
→ Safety Constraints
→ Decision Playbook Injection
→ Execution Plan
```

Die Ausgabe ist ein **agent-ready Plan**, kein bloßer Regeltext.

---

## 🧠 18.4 Policy Sources
Policies können aus mehreren Schichten stammen:

- **DNA Policies** → stabile Langzeitregeln
- **Dream Policies** → aus erfolgreichen Mustern extrahiert
- **User Policies** → explizite Präferenzen
- **System Policies** → Safety / Compliance
- **Task Policies** → projektspezifische Regeln

Priorität:

```text
system > dna > task > dream > user
```

---

## 🛡️ 18.5 Safety Guardrails
Die Policy Engine ist der ideale Ort für Runtime-Governance.

Beispiele:

```yaml
policy: "Vor jeder DB-Migration Snapshot erzwingen"
priority: 0.98
```

```yaml
policy: "Bei externen Datenquellen Trust Layer validieren"
priority: 0.95
```

Damit werden riskante Agent-Aktionen aktiv begrenzt.

---

## 🛠️ 18.6 Toolchain Orchestration Policies
Policies können ganze Tool-Sequenzen definieren.

```yaml
task_type: code_fix
execution_plan:
  - repo_scan
  - symbol_search
  - patch_generation
  - test_run
  - snapshot_commit
```

Nutzen:
- deterministischere Agenten
- wiederverwendbare Workflows
- geringere Fehlerraten

---

## 🌙 18.7 Dream + Decision Integration
Neue Policies entstehen automatisch aus Reward-starken Decision Trails.

```python
if decision.outcome_score > 0.92:
    policy_engine.promote(decision)
```

Das ist die direkte Verbindung zwischen:

- Experience
- Learning
- Governance
- Runtime Behavior

---

## 🔄 18.8 Adaptive Policy Decay
Policies dürfen altern.

```python
if success_rate < 0.6 over 30 days:
    reduce_priority(policy)
```

So verhindert BrainDump veraltete Agent-Gewohnheiten.

Sehr wichtig für:
- API-Änderungen
- Toolchain-Wechsel
- neue User-Workflows

---

## 🚀 18.9 Strategische Empfehlung
Mein klarer Architektur-Rat:

> **Die Policy Engine ist das exekutive Gehirn von BrainDump.**

VFS speichert.
Retriever denkt.
Dream lernt.
Decision bewertet.

> **Policy steuert Verhalten.**

Damit entsteht ein vollständiger Closed Loop:

> **Memory → Retrieval → Decision → Reward → Policy → Action**

Das ist der Schritt zu einem echten:

> **adaptive autonomous cognitive operating system**


---

# 🤖 19. `agent_runtime.py` Orchestrator + Execution Kernel

`agent_runtime.py` ist der **zentrale Hauptprozess von BrainDump**.

Hier werden alle zuvor definierten kognitiven Subsysteme zu einer laufenden Runtime verbunden.

> **Der Runtime Kernel ist das exekutive Nervensystem des Cognitive OS.**

---

## 🎯 19.1 Verantwortlichkeiten
Der Runtime Kernel orchestriert:

- Input Intake
- Working Memory Assembly
- Policy Evaluation
- Toolchain Dispatch
- Decision Recording
- Reward Collection
- Dump Writing
- Dream Triggering

---

## 🧩 19.2 Core Interface
```python
class AgentRuntime:
    def __init__(
        self,
        retriever,
        policy_engine,
        decision_memory,
        dream_engine,
        vfs,
        tool_router,
    ):
        self.retriever = retriever
        self.policy_engine = policy_engine
        self.decision_memory = decision_memory
        self.dream_engine = dream_engine
        self.vfs = vfs
        self.tool_router = tool_router

    def run_task(self, task_input: str):
        context = self.retriever.retrieve(task_input)
        execution_plan = self.policy_engine.apply({"query": task_input, "context": context})
        result = self.tool_router.execute(execution_plan)
        self._post_process(task_input, context, execution_plan, result)
        return result
```

---

## 🔄 19.3 Runtime Execution Loop
```text
Input
→ Retrieve
→ Policy
→ Execution Plan
→ Tool Dispatch
→ Result
→ Decision Record
→ Reward
→ Dump
→ Daydream
```

Nightdream und Deepdream laufen scheduler-basiert parallel.

---

## 🛠️ 19.4 Tool Router Integration
Der Runtime Kernel spricht niemals Tools direkt an, sondern über einen Router.

```python
result = tool_router.execute(plan)
```

Vorteile:
- austauschbare Toolchains
- bessere Testbarkeit
- Retry Policies
- Timeout Governance
- Safety Sandboxing

---

## 🎯 19.5 Decision + Reward Hook
```python
decision_memory.record(
    DecisionRecord(
        decision_id=task_id,
        task_fingerprint=fingerprint(task_input),
        context_hash=hash_context(context),
        chosen_action=str(execution_plan),
        outcome_score=score_result(result),
    )
)
```

Dadurch wird jede Task-Ausführung sofort lernbar.

---

# 🧪 20. Testkonzept + Implementierungsstart

Ja — **die Implementierung kann jetzt sehr gut starten**, weil die Kernmodule sauber separiert sind.

Mein klarer Rat:

> **Jetzt zuerst ein testbares Vertical Slice bauen, nicht sofort Full Feature.**

---

## 🚀 20.1 Empfohlene Implementierungsreihenfolge (Sprint 1–3)

### ✅ Sprint 1 — Kernel Foundations
- `brain_vfs.py`
- `retriever.py`
- `agent_runtime.py`
- `schema.sql`
- einfacher `tool_router.py`

Ziel:
> erster End-to-End Task Loop

---

### 🌙 Sprint 2 — Learning Loop
- `dream_engine.py`
- `decision_memory.py`
- Reward Heuristiken
- Snapshotting
- Archive Lifecycle

Ziel:
> Lernen zwischen Sessions

---

### 📜 Sprint 3 — Adaptive Governance
- `policy_engine.py`
- Playbook Policies
- Safety Guardrails
- Policy Decay
- Workflow Templates

Ziel:
> adaptive Agentensteuerung

---

## 🧪 20.2 Teststrategie (Pflicht)
Ich würde 4 Testebenen definieren.

### 1) Unit Tests
Pro Modul isoliert.

Beispiele:
- VFS write/read
- retrieval ranking
- policy matching
- reward scoring
- DNA promotion heuristics

Ordner:
```text
/tests/unit
```

---

### 2) Integration Tests
Cross-Module Verhalten.

Beispiele:
- Dump → Daydream → Wiki Promotion
- Task → Decision → Reward
- Policy → Toolchain Plan
- Snapshot → Rollback

Ordner:
```text
/tests/integration
```

---

### 3) Simulation / Agent Scenario Tests
Realistische Langläufer.

Beispiele:
- Coding task over 20 iterations
- repeated research workflow
- failure recovery after bad tool output
- preference stabilization over time

Ordner:
```text
/tests/scenarios
```

Das ist extrem wichtig für BrainDump.

---

### 4) Regression + Memory Drift Tests
Spezialtests für Cognitive Systems.

Ziele:
- keine DNA Korruption
- keine Policy Regression
- keine Retrieval Drift
- kein Memory Poisoning

Beispiel:
```python
assert retrieval_quality_t30 >= retrieval_quality_t1
```

Das ist euer wichtigster Qualitäts-Moat.

---

## 📏 20.3 KPI-basierte Testmetriken
Nicht nur funktionale Tests.

Wichtige KPIs:
- Retrieval Precision@k
- Decision Reuse Rate
- Reward Improvement over Time
- Policy Success Rate
- Compression Ratio
- Dream Consolidation Gain
- Drift Score

---

## 🧠 20.4 Golden Test Scenarios
Definiert 5–10 Goldpfade.

Zum Beispiel:

### Coding Agent
```text
repo bug → retrieve history → choose fix playbook → patch → test → reward
```

### Research Agent
```text
topic refinement → source validation → synthesis → preference formatting
```

Diese Szenarien werden über jede Version wiederholt.

---

## 🎯 20.5 Mein klarer Start-Rat
Ja, **jetzt ist der perfekte Zeitpunkt für die Implementierung**.

Aber entscheidend ist:

> **erst den Runtime Vertical Slice stabil bekommen**

Also:

> VFS → Retriever → Runtime → Dump → Daydream

Wenn das läuft, kann BrainDump iterativ sehr schnell wachsen.

Das Testkonzept stellt sicher, dass das System nicht nur Features bekommt, sondern **über Zeit tatsächlich intelligenter wird**.

