from fastapi import HTTPException


def api_error(code: str, status_code: int = 400, meta: dict = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "meta": meta or {}},
    )


def auth_error(code: str, meta: dict = None) -> HTTPException:
    return api_error(code, status_code=401, meta=meta)


def not_found_error(entity: str) -> HTTPException:
    return api_error(f"{entity.upper()}_NOT_FOUND", status_code=404)


def forbidden_error(code: str = "FORBIDDEN") -> HTTPException:
    return api_error(code, status_code=403)
