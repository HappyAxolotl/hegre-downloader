import json

from datetime import date
from typing import Any


class HegreJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, date):
            return o.isoformat()

        return o.__dict__
