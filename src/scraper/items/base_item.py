from abc import ABC, abstractmethod

import scrapy


class BaseItem(scrapy.Item, ABC):
    @property
    @abstractmethod
    def model(self):
        """Returns a database model of given item"""
        pass

    @abstractmethod
    def should_save(self) -> bool:
        """Determine whether this item should be saved."""
        pass
