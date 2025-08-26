"""
MCP 연동용 영수증 크롤러 도구
Claude Code와 연동하여 로컬에서 안전하게 크롤링 수행
"""

import json
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 백엔드 모듈 임포트 (경로 조정 필요)
sys.path.append('../app/backend')
from services.crawler import NaverPlaceCrawler
from models.receipt import RestaurantInfo
from utils.errors import CrawlingError

logger = logging.getLogger(__name__)

class MCPReceiptCrawler:
    """MCP 연동용 크롤러 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.crawler = NaverPlaceCrawler()
    
    async def crawl_restaurant(self, url: str) -> Dict[str, Any]:
        """
        네이버플레이스 URL에서 식당 정보 크롤링
        
        Args:
            url: 네이버플레이스 모바일 URL
            
        Returns:
            크롤링 결과 딕셔너리
        """
        try:
            # URL 유효성 검증
            if not url.startswith('https://m.place.naver.com/'):
                raise ValueError("올바른 네이버플레이스 모바일 URL이 아닙니다")
            
            logger.info(f"크롤링 시작: {url}")
            
            # 크롤링 실행
            restaurant_info = await self.crawler.crawl_restaurant_info(url)
            
            # 결과 변환
            result = {
                "success": True,
                "data": {
                    "business_name": restaurant_info.business_name,
                    "phone": restaurant_info.phone,
                    "address": restaurant_info.address,
                    "menu_items": [
                        {
                            "name": item.name,
                            "price": item.price,
                            "options": item.options
                        }
                        for item in restaurant_info.menu_items
                    ]
                },
                "metadata": {
                    "crawled_at": datetime.now().isoformat(),
                    "url": url,
                    "menu_count": len(restaurant_info.menu_items)
                }
            }
            
            logger.info(f"크롤링 성공: {len(restaurant_info.menu_items)}개 메뉴 추출")
            return result
            
        except CrawlingError as e:
            logger.error(f"크롤링 오류: {e.message}")
            return {
                "success": False,
                "error": {
                    "type": e.error_type,
                    "message": e.message,
                    "code": "CRAWLING_FAILED"
                }
            }
            
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)}")
            return {
                "success": False,
                "error": {
                    "type": "UNEXPECTED_ERROR",
                    "message": f"크롤링 중 오류가 발생했습니다: {str(e)}",
                    "code": "INTERNAL_ERROR"
                }
            }

# MCP 도구 인터페이스 함수들
async def mcp_crawl_restaurant(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP에서 호출되는 크롤링 함수"""
    crawler = MCPReceiptCrawler()
    url = params.get('url')
    
    if not url:
        return {
            "success": False,
            "error": {
                "type": "INVALID_PARAMS",
                "message": "URL 파라미터가 필요합니다",
                "code": "MISSING_URL"
            }
        }
    
    return await crawler.crawl_restaurant(url)

def mcp_get_tool_info() -> Dict[str, Any]:
    """도구 정보 반환"""
    return {
        "name": "receipt_crawler",
        "description": "네이버플레이스에서 식당 정보와 메뉴를 크롤링합니다",
        "version": "1.0.0",
        "functions": [
            {
                "name": "crawl_restaurant",
                "description": "네이버플레이스 URL에서 식당 정보 크롤링",
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "네이버플레이스 모바일 URL",
                        "required": True,
                        "example": "https://m.place.naver.com/place/1234567890"
                    }
                }
            }
        ]
    }

# CLI 실행 지원
if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="영수증 크롤러 MCP 도구")
    parser.add_argument("--url", required=True, help="네이버플레이스 모바일 URL")
    parser.add_argument("--output", help="결과 저장 파일 (JSON)")
    
    args = parser.parse_args()
    
    async def main():
        crawler = MCPReceiptCrawler()
        result = await crawler.crawl_restaurant(args.url)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(main())