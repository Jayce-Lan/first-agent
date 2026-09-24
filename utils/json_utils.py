# utils/json_utils.py
import json
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel

class UniversalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump(exclude_none=True)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (set, tuple)):
            return list(obj)
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return str(obj)

def to_json(obj, indent=None):
    """任意对象转 JSON 字符串，一劳永逸。"""
    return json.dumps(obj, cls=UniversalEncoder, ensure_ascii=False, indent=indent)

def log_json(logger, label, obj):
    """直接打印任意对象的 JSON 表示。"""
    logger.info("%s - %s", label, to_json(obj))