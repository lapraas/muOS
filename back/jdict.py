
import abc
import json
from typing import Any, Generic, Type, TypeVar, Union

_OT = TypeVar("_OT", bound="dict")
class JObj(abc.ABC, Generic[_OT]):
    def __init__(self, raw: _OT):
        self.build(raw)

    @abc.abstractmethod
    def build(self, raw: _OT):
        pass
    @abc.abstractmethod
    def serialize(self) -> _OT:
        pass

_K = TypeVar("_K")
_T = TypeVar("_T", bound=JObj)
_Raw = dict[_K, _OT]
class JDict(JObj, Generic[_K, _T]):
    path: str
    jObjClass: Type[_T]
    d: dict[_K, _T]

    @classmethod
    def load(cls):
        try:
            with open(cls.path, "r") as f:
                raw = json.load(f)
        except FileNotFoundError:
            with open(cls.path, "x") as f:
                f.write("{}")
                raw = {}
        return cls(raw)
    
    def dump(self):
        raw = self.serialize()
        with open(self.path, "w") as f:
            json.dump(raw, f)
    
    def build(self, raw: _Raw):
        self.d = {}
        for name in raw:
            objRaw = raw[name]
            self.d[name] = self.jObjClass(objRaw)
    
    def serialize(self):
        raw = {}
        for name in self.d:
            obj = self.d[name]
            raw[name] = obj.serialize()
        return raw