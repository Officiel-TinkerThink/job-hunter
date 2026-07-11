"""App entrypoint — re-exports the composed FastAPI app."""
from .api.routes_opportunities import app

__all__ = ["app"]
