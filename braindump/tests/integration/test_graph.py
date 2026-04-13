# 🧠 BrainDump (v3) - Knowledge Graph Integration Test
import os
import sqlite3
from brain_vfs import BrainVFS
from retriever import BrainRetriever
from entity_resolver import EntityResolver

def test_knowledge_graph_retrieval():
    """
    Test: Entity Resolution -> Graph Relation -> Expanded Retrieval.
    """
    # 1. Setup
    root_dir = "test_data_graph"
    os.makedirs(root_dir, exist_ok=True)
    vfs = BrainVFS(root_dir)
    db_path = os.path.join(root_dir, "metadata.db")
    
    resolver = EntityResolver(db_path=db_path)
    retriever = BrainRetriever(vfs, db_path=db_path, entity_resolver=resolver)
    
    # 2. Create Knowledge Graph
    # Project Alpha depends on Python
    alpha_id = resolver.resolve_entity("ProjectAlpha", entity_type="project")
    python_id = resolver.resolve_entity("Python", entity_type="concept")
    
    resolver.create_relation(alpha_id, python_id, rel_type="uses", weight=0.9)
    
    # 3. Retrieve for "ProjectAlpha"
    query = "Tell me about ProjectAlpha"
    context = retriever.retrieve(query)
    
    # 4. Assertions
    # Evidence should contain the related "Python" entity ID
    found_evidence = [e["id"] for e in context.evidence]
    assert python_id in found_evidence
    
    print("Knowledge Graph Integration Test: PASSED ✅")

if __name__ == "__main__":
    try:
        test_knowledge_graph_retrieval()
    finally:
        # Cleanup
        # shutil.rmtree("test_data_graph")
        pass
