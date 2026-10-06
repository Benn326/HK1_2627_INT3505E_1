from flask import jsonify, request
from uuid import uuid4

ERROR_BASE = "https://api.example.com/probs"


class ApiProblem(Exception):
    def __init__(
        self,
        status,
        title,
        detail=None,
        type_path=None,
        **extra
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type_path = type_path
        self.extra = extra
        super().__init__(detail)


def problem(
    status,
    title,
    detail=None,
    type_path=None,
    **extra
):
    body = {
        "type": (
            f"{ERROR_BASE}/{type_path}"
            if type_path
            else "about:blank"
        ),
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid4())
    }

    if detail is not None:
        body["detail"] = detail

    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"

    return resp