import sys, traceback
sys.path.append(r'c:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking')
try:
    from evidence_service.app.pipeline.extractor import extract
    from evidence_service.app.pipeline.resolver import resolve_entities
    from evidence_service.app.pipeline.relationship_builder import build_relationships
    from evidence_service.app.repo.inmemory import InMemoryGraphRepo
    print('IMPORTS_OK')
except Exception:
    traceback.print_exc()
