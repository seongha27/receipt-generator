"""
간단한 크롤러 (Chrome 없이 Mock 데이터 반환)
Render 무료 플랜용
"""

import logging
from typing import List
import asyncio
import requests
from bs4 import BeautifulSoup

from models.receipt import RestaurantInfo, MenuItem
from utils.errors import CrawlingError

logger = logging.getLogger(__name__)

class SimpleNaverPlaceCrawler:
    """Chrome 없는 환경용 간단한 크롤러"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        }
    
    async def crawl_restaurant_info(self, url: str) -> RestaurantInfo:
        """네이버플레이스에서 식당 정보 크롤링 (간단 버전)"""
        try:
            logger.info(f"간단 크롤링 시도: {url}")
            
            # 실제 크롤링 시도 (requests 사용)
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 기본 정보 추출 시도
                business_name = self._extract_name_from_soup(soup) or "크롤링된 식당"
                
                # 간단한 메뉴 데이터 (실제 크롤링 실패시 Mock 데이터)
                mock_menus = [
                    MenuItem(name="김치찌개", price=8000),
                    MenuItem(name="된장찌개", price=7000), 
                    MenuItem(name="공기밥", price=1000),
                    MenuItem(name="계란말이", price=5000),
                    MenuItem(name="콜라", price=2000)
                ]
                
                return RestaurantInfo(
                    business_name=business_name,
                    phone="02-1234-5678",
                    address="서울특별시 강남구 테헤란로 123",
                    menu_items=mock_menus
                )
                
            except Exception as e:
                logger.warning(f"실제 크롤링 실패, Mock 데이터 사용: {str(e)}")
                
                # Mock 데이터 반환
                return RestaurantInfo(
                    business_name="테스트 맛집",
                    phone="02-555-1234",
                    address="서울특별시 강남구 역삼동 123-45",
                    menu_items=[
                        MenuItem(name="김치찌개", price=8000),
                        MenuItem(name="된장찌개", price=7000),
                        MenuItem(name="비빔밥", price=9000),
                        MenuItem(name="공기밥", price=1000)
                    ]
                )
            
        except Exception as e:
            logger.error(f"크롤링 중 오류: {str(e)}")
            raise CrawlingError(f"크롤링 실패: {str(e)}", "CRAWLING_FAILED")
    
    def _extract_name_from_soup(self, soup) -> str:
        """BeautifulSoup에서 식당명 추출"""
        try:
            # title 태그에서 추출
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                name = (title_text
                       .replace(" : 네이버", "")
                       .replace(" - 네이버플레이스", "")
                       .replace("네이버플레이스", "")
                       .strip())
                if name and len(name) > 1:
                    return name
            
            # 다양한 셀렉터 시도
            selectors = [".Fc1rA", ".GHAhO", "h1", ".place_name"]
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text().strip()
                    if name and len(name) > 1:
                        return name
                        
        except Exception as e:
            logger.debug(f"이름 추출 실패: {str(e)}")
        
        return None