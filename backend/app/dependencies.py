async def require_admin() -> bool:
    """No-op today. Swap in a real check (API key, session, etc.) to protect admin routes
    without needing to touch any router — every admin route already depends on this."""
    return True
