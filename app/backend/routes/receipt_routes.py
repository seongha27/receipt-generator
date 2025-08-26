from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import tempfile
import os
import logging

from models.receipt import CrawlRequest, ManualMenuInput, ReceiptData, ErrorResponse
from services.crawler import NaverPlaceCrawler
from services.receipt_generator import ReceiptGenerator
from utils.errors import handle_crawling_error, handle_receipt_error, CrawlingError

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

@router.post("/crawl-menu")
@limiter.limit("10/minute")
async def crawl_menu(request: CrawlRequest, remote_addr: str = Depends(get_remote_address)):
    """네이버플레이스에서 메뉴 정보 크롤링"""
    try:
        crawler = NaverPlaceCrawler()
        restaurant_info = await crawler.crawl_restaurant_info(request.naver_place_url)
        
        if not restaurant_info.menu_items:
            raise CrawlingError(
                "메뉴 정보를 찾을 수 없습니다. 수동으로 메뉴를 입력해주세요.",
                "NO_MENU_FOUND"
            )
        
        return {
            "success": True,
            "data": restaurant_info.dict(),
            "message": f"{len(restaurant_info.menu_items)}개의 메뉴를 찾았습니다."
        }
    
    except CrawlingError as e:
        raise handle_crawling_error(e)
    except Exception as e:
        raise handle_crawling_error(e)

@router.post("/generate-receipt")
@limiter.limit("5/minute")
async def generate_receipt(
    crawl_data: CrawlRequest,
    manual_menu: ManualMenuInput = None,
    remote_addr: str = Depends(get_remote_address)
):
    """영수증 PDF/PNG 생성"""
    try:
        # 크롤링 데이터가 있으면 사용, 없으면 수동 입력 데이터 사용
        if manual_menu and manual_menu.menu_items:
            menu_items = manual_menu.menu_items
            # 크롤링 없이 기본 정보만 사용
            receipt_data = ReceiptData(
                business_number=crawl_data.business_number,
                business_name=crawl_data.business_name,
                owner_name=crawl_data.owner_name,
                payment_method=crawl_data.payment_method,
                payment_datetime=crawl_data.payment_datetime,
                approval_number=crawl_data.approval_number,
                menu_items=menu_items
            )
        else:
            # 크롤링 시도
            crawler = NaverPlaceCrawler()
            restaurant_info = await crawler.crawl_restaurant_info(crawl_data.naver_place_url)
            
            receipt_data = ReceiptData(
                business_number=crawl_data.business_number,
                business_name=crawl_data.business_name,
                owner_name=crawl_data.owner_name,
                phone=restaurant_info.phone,
                address=restaurant_info.address,
                payment_method=crawl_data.payment_method,
                payment_datetime=crawl_data.payment_datetime,
                approval_number=crawl_data.approval_number,
                menu_items=restaurant_info.menu_items
            )
        
        # 영수증 생성
        generator = ReceiptGenerator()
        pdf_path, png_path = generator.generate_receipt(receipt_data)
        
        return {
            "success": True,
            "data": {
                "pdf_download_url": f"/api/v1/download/pdf/{os.path.basename(pdf_path)}",
                "png_download_url": f"/api/v1/download/png/{os.path.basename(png_path)}",
                "receipt_info": {
                    "business_name": receipt_data.business_name,
                    "total_amount": receipt_data.total,
                    "item_count": len(receipt_data.menu_items)
                }
            },
            "message": "영수증이 성공적으로 생성되었습니다."
        }
        
    except Exception as e:
        raise handle_receipt_error(e)

@router.get("/download/pdf/{filename}")
async def download_pdf(filename: str):
    """PDF 파일 다운로드"""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )

@router.get("/download/png/{filename}")
async def download_png(filename: str):
    """PNG 파일 다운로드"""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="image/png"
    )

@router.post("/validate-url")
@limiter.limit("20/minute")
async def validate_naver_place_url(url: str, remote_addr: str = Depends(get_remote_address)):
    """네이버플레이스 URL 유효성 검사"""
    if not url.startswith("https://m.place.naver.com/"):
        return {
            "valid": False,
            "message": "네이버플레이스 모바일 URL을 입력해주세요. (예: https://m.place.naver.com/place/...)"
        }
    
    return {
        "valid": True,
        "message": "유효한 네이버플레이스 URL입니다."
    }