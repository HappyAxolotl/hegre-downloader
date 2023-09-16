from json import JSONEncoder
from datetime import date
from typing import Any

from model.object_type import ObjectType


class HegreJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, ObjectType):
            return str(o)

        return o.__dict__
