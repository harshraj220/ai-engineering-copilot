from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_service
from app.rag.loader import load_document
from app.rag.vector_store import vector_store
from app.services.llm import llm_service


class RAGService:

    def ingest(self, path: str):
        text = load_document(path)
        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("Document contains no text")

        vectors = embedding_service.embed(chunks)

        vector_store.upsert(
            vectors=vectors,
            chunks=chunks,
            document_name=path,
        )

        return {
            "document": path,
            "chunks": len(chunks),
        }

    def retrieve(self, query: str, limit: int = 5):
        vector = embedding_service.embed([query])[0]

        results = vector_store.search(vector, limit=limit)

        return [
            {
                "text": point.payload["text"],
                "document": point.payload["document"],
                "chunk_index": point.payload["chunk_index"],
                "score": point.score,
            }
            for point in results
        ]

    async def answer(self, query: str, limit: int = 5):
        results = self.retrieve(query, limit)

        if not results:
            return {
                "answer": "I couldn't find relevant information.",
                "sources": [],
            }

        context = "\n\n".join(
            f"[Source {index + 1}: {item['document']}]\n"
            f"{item['text']}"
            for index, item in enumerate(results)
        )

        response = await llm_service.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an enterprise knowledge assistant. "
                        "Answer ONLY using the supplied context. "
                        "If the context does not contain the answer, "
                        "say that you don't have enough information. "
                        "Always mention the source documents used."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{query}\n\n"
                        f"Context:\n{context}"
                    ),
                },
            ]
        )

        return {
            "answer": response.choices[0].message.content or "",
            "sources": [
                {
                    "document": item["document"],
                    "chunk_index": item["chunk_index"],
                    "score": item["score"],
                }
                for item in results
            ],
        }


rag_service = RAGService()