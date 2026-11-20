import logging
import os
from datetime import datetime, timezone
from flask import Flask
from sunset import deprecate_at

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = Flask(__name__)
app.json.ensure_ascii = False


def get_sunset_date():
    raw = os.getenv("V1_SUNSET")
    if not raw:
        return datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    dt = datetime.fromisoformat(raw)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


V1_SUNSET = get_sunset_date()


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


if __name__ == "__main__":
    app.run(debug=True)
