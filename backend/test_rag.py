from app.rag.service import rag_service


result = rag_service.ingest(
    "test_documents/security.txt"
)

print("INGESTION:")
print(result)

results = rag_service.retrieve(
    "What actions require human approval?"
)

print("\nRETRIEVAL:")

for result in results:
    print("\nScore:", result["score"])
    print("Document:", result["document"])
    print("Text:", result["text"])