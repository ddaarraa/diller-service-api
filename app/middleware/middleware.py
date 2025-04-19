from fastapi import Header, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

SECRET_KEY = "w_RZQ0Gj1hMlEjUtAHXk3GnHRspRm8zKzPzE0xxm-Zs"

class SecretKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/docs", "/openapi.json", "/redoc", "/all-raw-logs"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        key = request.headers.get("X-Secret-Key")
        if key != SECRET_KEY:
            raise HTTPException(status_code=403, detail="Forbidden: Invalid Secret Key")
        return await call_next(request)
    
def verify_secret_key(x_secret_key: str = Header(...)):
    # Optional: move this check into the middleware if you're using both
    if x_secret_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid Secret Key")