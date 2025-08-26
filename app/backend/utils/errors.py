from fastapi import HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CrawlingError(Exception):
    """크롤링 관련 에러"""
    def __init__(self, message: str, error_type: str = "CRAWLING_ERROR"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

class ValidationError(Exception):
    """데이터 검증 에러"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ReceiptGenerationError(Exception):
    """영수증 생성 에러"""
    def __init__(self, message: str, error_type: str = "RECEIPT_ERROR"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

def handle_crawling_error(error: Exception) -> HTTPException:
    """크롤링 에러를 HTTP 응답으로 변환"""
    if isinstance(error, CrawlingError):
        logger.error(f"크롤링 오류: {error.message}")
        return HTTPException(
            status_code=422,
            detail={
                "error": error.error_type,
                "message": error.message,
                "code": "MANUAL_INPUT_REQUIRED"
            }
        )
    else:
        logger.error(f"예상치 못한 크롤링 오류: {str(error)}")
        return HTTPException(
            status_code=500,
            detail={
                "error": "CRAWLING_FAILED",
                "message": "메뉴 정보를 가져오는 중 오류가 발생했습니다. 수동으로 입력해주세요.",
                "code": "MANUAL_INPUT_REQUIRED"
            }
        )

def handle_receipt_error(error: Exception) -> HTTPException:
    """영수증 생성 에러를 HTTP 응답으로 변환"""
    if isinstance(error, ReceiptGenerationError):
        logger.error(f"영수증 생성 오류: {error.message}")
        return HTTPException(
            status_code=500,
            detail={
                "error": error.error_type,
                "message": error.message
            }
        )
    else:
        logger.error(f"예상치 못한 영수증 생성 오류: {str(error)}")
        return HTTPException(
            status_code=500,
            detail={
                "error": "RECEIPT_GENERATION_FAILED",
                "message": "영수증 생성 중 오류가 발생했습니다."
            }
        )