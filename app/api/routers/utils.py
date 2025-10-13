"""Common utility functions for routers"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check X-Forwarded-For header (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Direct connection
    return request.client.host if request.client else "unknown"
