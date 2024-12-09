# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import datetime
import logging

import chromadb
from chromadb import Settings
from langchain_huggingface import HuggingFaceEmbeddings

from app import app
from models import db
from src.scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToChromaPipeline:
    def __init__(self, host="chatbot-chromadb-container", port=8000):
        """Initialize ChromaDB client and embeddings."""
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(allow_reset=True, anonymized_telemetry=False),
        )
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def process_item(self, item: SiteItem, spider):
        if not isinstance(item, SiteItem):
            return item
        if item is None:
            logger.error("Received None item, skipping...")
            return item

        with app.app_context():
            if not item.should_save:
                return item
        collection_name = "colection_W2A"
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        collection = self.client.get_or_create_collection(collection_name)
        existing_docs = collection.get()
        existing_hashes = {metadata["hash"] for metadata in existing_docs["metadatas"]}
        current_hash = item.get("page_hash")
        if current_hash in existing_hashes:
            logger.info(
                f"Item with hash {current_hash} already exists in ChromaDB, skipping..."
            )
            return item
        logger.info(f"Adding new item to ChromaDB with hash {current_hash}")
        collection.add(
            ids=[f"{item.get('url').replace('/','')}-{timestamp}"],
            embeddings=self.embedding_function.embed_documents(item.get("html")),
            documents=[item.get("html")],
            metadatas=[{"hash": current_hash}],
        )
        return item
