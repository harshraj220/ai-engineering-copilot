from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


class VectorStore:
    COLLECTION_NAME = "enterprise_documents"
    VECTOR_SIZE = 384

    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )

        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections()

        names = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(
        self,
        vectors: list[list[float]],
        chunks: list[str],
        document_name: str,
    ):
        points = []

        for index, (vector, chunk) in enumerate(
            zip(vectors, chunks)
        ):
            points.append(
                PointStruct(
                    id=index,
                    vector=vector,
                    payload={
                        "text": chunk,
                        "document": document_name,
                        "chunk_index": index,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ):
        return self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=limit,
        ).points


vector_store = VectorStore()