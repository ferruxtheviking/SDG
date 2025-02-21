import os
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__( self, app):
        super().__init__(app)
        self.secretKey = os.getenv('JWT_SECRET_KEY')

    async def dispatch(self, request: Request, call_next):
        try:
            jwtToken = request.headers.get('JWT')
            token = jwt.decode(jwtToken, self.secretKey, algorithms=["HS256"])
            response = await call_next(request)
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail":"Signature has expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail":"Invalid JWT"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail":f"{e}"})

        return response

class CorsMiddleware(BaseHTTPMiddleware):
    def __init__( self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Access-Control-Allow-Origin']      = '*'
        response.headers['Access-Control-Allow-Methods']     = 'GET'
        response.headers['Access-Control-Allow-Headers']     = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response