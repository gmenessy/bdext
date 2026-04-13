# 🧠 Demo 4: Intelligente Akte - "Living Case File"
import sys
import os
import sqlite3
import uuid
import json
from datetime import datetime, timedelta
from demo_utils import setup_demo_env
from brain_vfs import VFSNode
from decision_memory import DecisionRecord

class CaseManager:
    def __init__(self, env):
        self.env = env
        self.db_path = env["db_path"]
        self.vfs = env["vfs"]

    def create_case(self, case_id, title, deadline_days=30):
        opened_at = datetime.now()
        deadline = opened_at + timedelta(days=deadline_days)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO cases (case_id, title, status, opened_at, deadline) VALUES (?, ?, ?, ?, ?)",
                         (case_id, title, "open", opened_at.isoformat(), deadline.isoformat()))
        return deadline

    def link_entity(self, case_id, entity_id, role):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO case_links (case_id, entity_id, role) VALUES (?, ?, ?)",
                         (case_id, entity_id, role))

def run_demo():
    print("🧠 BrainDump Demo 4: Intelligente Akte (Living Case File)")
    print("-------------------------------------------------------")
    env = setup_demo_env("living_case_file")
    agent = env["agent"]
    vfs = env["vfs"]
    entity_resolver = env["entity_resolver"]
    case_mgr = CaseManager(env)

    case_id = "CASE-FR-2026-001"
    print(f"\n[Tag 1] Eröffnung Bauantrag: '{case_id}' (Stadt Freiburg)")
    deadline = case_mgr.create_case(case_id, "Bauantrag Müller - Freiburg", deadline_days=30)
    
    # --- TAG 1: Eingang ---
    print("\n[Tag 1] Dokumenteneingang: E-Mail vom Architekt + Notiz Sachbearbeiter")
    
    # 1. E-Mail vom Architekt
    email_content = "Anhang: PDF_Plan_V1.pdf. Wir beantragen die Baugenehmigung für das Grundstück 42."
    agent.run_task(f"INGEST (Case {case_id}): {email_content}")
    
    # 2. Notiz Sachbearbeiter
    note_content = "Erstsichtung: Statiknachweis fehlt im PDF-Plan."
    agent.run_task(f"INGEST (Case {case_id}): {note_content}")

    # Entity Extraction (Simuliert durch Resolver)
    g_id = entity_resolver.resolve_entity("Grundstück 42", "property")
    case_mgr.link_entity(case_id, g_id, "subject_property")
    
    print(f" ✅ Entitäten extrahiert: {g_id} (Rolle: subject_property)")

    # --- TAG 5: Widerspruch ---
    print("\n[Tag 5] Neues Dokument: Gutachten_Statik_Final.pdf")
    gutachten_content = "Gutachten: Die Statik für Grundstück 42 ist gemäß LBauO §17 vollständig und ausreichend."
    
    # Wir fügen dies direkt in den Knowledge Layer ein, um den Konflikt zu simulieren
    fact_path = f"vfs://wiki/concepts/statik_{uuid.uuid4().hex[:8]}"
    vfs.write(VFSNode(
        path=fact_path,
        layer="wiki",
        content={"assertion": "Statik ausreichend", "source": "Gutachten_Final", "confidence": 0.9, "alpha": 1, "beta": 0},
        metadata={"summary": "Statik-Check Grundstück 42"}
    ))
    
    # Simulieren des vorherigen Widerspruchs (aus der Notiz)
    original_path = f"vfs://wiki/concepts/statik_{uuid.uuid4().hex[:8]}"
    vfs.write(VFSNode(
        path=original_path,
        layer="wiki",
        content={"assertion": "Statik fehlt", "source": "Notiz_Sachbearbeiter", "confidence": 0.8, "alpha": 0, "beta": 1},
        metadata={"summary": "Mangel: Statik fehlt"}
    ))

    print(" ⚠️ Konflikt erkannt: 'Statik fehlt' vs 'Statik ausreichend'")
    # Relation contradictions anlegen
    with sqlite3.connect(env["db_path"]) as conn:
        conn.execute("INSERT INTO relations (source_id, target_id, relation_type, weight) VALUES (?, ?, ?, ?)",
                     (fact_path, original_path, "contradicts", 1.0))
        # Bayesian Belief Update Simulation: alpha=1, beta=1 -> Confidence 0.5
        conn.execute("UPDATE memory_entries SET confidence = 0.5, state = 'conflict' WHERE id IN (?, ?)", (fact_path, original_path))

    # --- TAG 12: Entscheidung ---
    print("\n[Tag 12] Sachbearbeiter prüft Akte und entscheidet...")
    
    decision_reasoning = "Widersprüchliche Angaben zur Statik. Da das Sicherheitsrisiko hoch ist (Vorsichtsprinzip), wird eine Nachforderung gestellt."
    decision = DecisionRecord(
        id=uuid.uuid4().hex[:8],
        task_id=case_id,
        decision="Nachforderung Statik",
        reasoning_summary=decision_reasoning,
        chosen_action="REQUEST_INFO",
        outcome_score=1.0 # Erfolgreich deeskaliert
    )
    env["decision_memory"].record(decision)
    print(f" 🤖 Entscheidung protokolliert: {decision.decision}")
    print(f" 🔧 Begründung: {decision_reasoning}")

    # --- TAG 30: Fristprüfung ---
    print("\n[Tag 30] System-Check: Fristen und Priorisierung")
    current_time = datetime.now() + timedelta(days=28) # Wir springen in die Zukunft
    
    # Proximity Check
    days_left = (deadline - current_time).days
    proximity = 1.0 - (days_left / 30.0)
    print(f" ⏳ Akte '{case_id}' hat noch {days_left} Tage bis zur Frist ({deadline.strftime('%Y-%m-%d')}).")
    print(f" 🚨 Temporal Proximity Weight: {proximity:.2f}")

    # --- RETRIEVAL: Warum wurde Nachforderung gestellt? ---
    print("\n[Retrieval] Frage: 'Warum wurde für den Fall Müller eine Nachforderung gestellt?'")
    
    # Simulation des fRAG Agenten, der die Kette verfolgt
    context = env["retriever"].retrieve("Nachforderung Statik Müller")
    
    print("\n📊 Akteneinsicht (Audit-Log):")
    # 1. Entscheidung finden
    with sqlite3.connect(env["db_path"]) as conn:
        conn.row_factory = sqlite3.Row
        dec = conn.execute("SELECT * FROM decisions WHERE task_id = ?", (case_id,)).fetchone()
        print(f"  Decision: {dec['decision']} (Datum: {dec['created_at']})")
        print(f"  Begründung: {dec['reasoning_summary']}")
        
    # 2. Widersprüche finden
    with sqlite3.connect(env["db_path"]) as conn:
        conn.row_factory = sqlite3.Row
        conflicts = conn.execute("SELECT * FROM memory_entries WHERE state = 'conflict'").fetchall()
        print(f"  Gefundene Widersprüche: {len(conflicts)}")
        for c in conflicts:
            print(f"    - [{c['id']}] {c['summary']} (Confidence: {c['confidence']})")

    print("\n✨ Demo 4 Complete: BrainDump verwaltet die 'Living Case File' auditierbar und intelligent.")

if __name__ == "__main__":
    run_demo()
