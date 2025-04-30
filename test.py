from abc import ABC, abstractmethod


class One(ABC):
    @classmethod
    @abstractmethod
    def poo(self):
        pass


class Two(ABC):
    @classmethod
    @abstractmethod
    def poo(self):
        pass


class Three(Two):
    pass


x = Three()
