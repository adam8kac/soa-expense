from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from services.request_statistics_service import RequestStatisticsService


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.statistics_service = RequestStatisticsService()

    async def dispatch(self, request: Request, call_next):
        # Log the request path
        path = request.url.path
        method = request.method

        # Skip logging for statistics endpoints themselves to avoid recursion
        if "/statistics" not in path and path != "/docs" and path != "/openapi.json":
            try:
                # Save the call to statistics
                self.statistics_service.save_call(path)
            except Exception as e:
                print(f"Error logging request: {e}")

        response = await call_next(request)
        return response
