# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from datetime import date

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app import app
from scraper.items.site_item import SiteItem

logger = logging.getLogger()


class SaveToChromaPipeline:
    def process_item(self, item, spider):
        if not isinstance(item, SiteItem):
            return item

        with app.app_context():
            if not item.should_save:
                return item

            collection_name = "collection_W2A"
            client: chromadb.ClientAPI = app.chromadb_client
            collection = client.get_or_create_collection(collection_name)
            existing_doc = collection.get(where={"url": item.get("url")})
            existing_hashes = {
                metadata["hash"] for metadata in existing_doc["metadatas"]
            }
            current_hash = item.get("page_hash")
            if current_hash in existing_hashes:
                logger.debug(
                    f"Item with hash {current_hash} already exists in ChromaDB, skipping..."
                )
                return item
            logger.debug(f"Adding new item to ChromaDB with hash {current_hash}")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )
            splits_to_add = text_splitter.split_text(" ".join(item.get("json")))
            if splits_to_add:
                collection.add(
                    ids=[
                        f"split_{collection_name}_{current_hash}_{i}"
                        for i, _ in enumerate(splits_to_add)
                    ],
                    embeddings=app.embedding_function.embed_documents(splits_to_add),
                    documents=splits_to_add,
                    metadatas=[
                        {
                            "hash": current_hash,
                            "url": item.get("url"),
                            "add_date": str(date.today()),
                        }
                        for _ in enumerate(splits_to_add)
                    ],
                )
        return item
