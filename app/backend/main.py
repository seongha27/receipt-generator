from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
import sys

# 환경변수 로드 (dotenv가 없어도 동작하도록)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from routes import receipt_routes
from utils.errors import handle_crawling_error, handle_receipt_error

# (환경변수는 위에서 이미 로드됨)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)

# FastAPI 앱 생성
app = FastAPI(
    title="영수증 생성기 API",
    description="네이버플레이스 크롤링 기반 영수증 자동 생성 API",
    version="1.0.0"
)

# Rate Limit 에러 핸들러
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정 - adsketch.info 도메인만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://www.adsketch.info",
        "https://www.adsketch.info",
        "http://localhost:3000",  # 개발용
        "http://127.0.0.1:3000"   # 개발용
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(receipt_routes.router, prefix="/api/v1", tags=["receipts"])

@app.get("/")
async def root():
    return {"message": "영수증 생성기 API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "receipt-backend"}

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"전역 예외 발생: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다."
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )