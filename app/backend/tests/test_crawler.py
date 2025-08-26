"""
크롤링 서비스 단위 테스트
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.crawler import NaverPlaceCrawler
from models.receipt import RestaurantInfo, MenuItem
from utils.errors import CrawlingError


@pytest.fixture
def crawler():
    """크롤러 인스턴스 픽스처"""
    return NaverPlaceCrawler()


@pytest.fixture
def mock_driver():
    """모킹된 WebDriver 픽스처"""
    driver = Mock()
    driver.page_source = '<html><title>테스트 식당 : 네이버</title></html>'
    return driver


class TestNaverPlaceCrawler:
    """네이버플레이스 크롤러 테스트"""
    
    @pytest.mark.asyncio
    async def test_extract_business_name_success(self, crawler):
        """상호명 추출 성공 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            # Mock WebDriver element
            mock_element = Mock()
            mock_element.text = "테스트 식당"
            mock_driver.find_element.return_value = mock_element
            
            result = await crawler._extract_business_name()
            assert result == "테스트 식당"
    
    @pytest.mark.asyncio 
    async def test_extract_business_name_from_title(self, crawler):
        """title에서 상호명 추출 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            # 일반 셀렉터로는 찾지 못하도록 설정
            mock_driver.find_element.side_effect = Exception("Not found")
            
            # BeautifulSoup용 페이지 소스
            mock_driver.page_source = '<html><title>테스트 맛집 : 네이버</title></html>'
            
            result = await crawler._extract_business_name()
            assert result == "테스트 맛집"
    
    @pytest.mark.asyncio
    async def test_extract_phone_success(self, crawler):
        """전화번호 추출 성공 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            mock_elements = [Mock()]
            mock_elements[0].text = "02-1234-5678"
            mock_elements[0].get_attribute.return_value = ""
            mock_driver.find_elements.return_value = mock_elements
            
            result = await crawler._extract_phone()
            assert result == "02-1234-5678"
    
    @pytest.mark.asyncio
    async def test_extract_phone_from_tel_link(self, crawler):
        """tel: 링크에서 전화번호 추출 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            mock_elements = [Mock()]
            mock_elements[0].text = ""
            mock_elements[0].get_attribute.return_value = "tel:02-1234-5678"
            mock_driver.find_elements.return_value = mock_elements
            
            result = await crawler._extract_phone()
            assert result == "02-1234-5678"
    
    @pytest.mark.asyncio
    async def test_extract_address_success(self, crawler):
        """주소 추출 성공 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            mock_elements = [Mock()]
            mock_elements[0].text = "서울특별시 강남구 테헤란로 123"
            mock_driver.find_elements.return_value = mock_elements
            
            result = await crawler._extract_address()
            assert result == "서울특별시 강남구 테헤란로 123"
    
    @pytest.mark.asyncio
    async def test_parse_menu_item_success(self, crawler):
        """메뉴 아이템 파싱 성공 테스트"""
        mock_element = Mock()
        
        # 메뉴명 요소
        mock_name_element = Mock()
        mock_name_element.text = "김치찌개"
        mock_element.find_element.side_effect = [mock_name_element, Mock()]
        
        # 가격 요소  
        mock_price_element = Mock()
        mock_price_element.text = "8,000원"
        mock_element.find_element.side_effect = [mock_name_element, mock_price_element]
        
        result = await crawler._parse_menu_item(mock_element)
        
        assert result is not None
        assert result.name == "김치찌개"
        assert result.price == 8000
    
    @pytest.mark.asyncio
    async def test_parse_menu_item_price_from_text(self, crawler):
        """텍스트에서 가격 추출 테스트"""
        mock_element = Mock()
        mock_element.text = "김치찌개 8,000원\n맛있는 김치찌개입니다"
        mock_element.find_element.side_effect = Exception("Not found")
        
        result = await crawler._parse_menu_item(mock_element)
        
        assert result is not None
        assert result.name == "김치찌개 8,000원"
        assert result.price == 8000
    
    @pytest.mark.asyncio
    async def test_crawl_restaurant_info_success(self, crawler):
        """전체 크롤링 성공 테스트"""
        test_url = "https://m.place.naver.com/place/1234567890"
        
        with patch.object(crawler, '_init_driver'), \
             patch.object(crawler, '_close_driver'), \
             patch.object(crawler, 'driver') as mock_driver, \
             patch.object(crawler, '_extract_business_name', return_value="테스트 식당"), \
             patch.object(crawler, '_extract_phone', return_value="02-1234-5678"), \
             patch.object(crawler, '_extract_address', return_value="서울시 강남구"), \
             patch.object(crawler, '_extract_menu_items', return_value=[
                 MenuItem(name="김치찌개", price=8000),
                 MenuItem(name="된장찌개", price=7000)
             ]):
            
            result = await crawler.crawl_restaurant_info(test_url)
            
            assert isinstance(result, RestaurantInfo)
            assert result.business_name == "테스트 식당"
            assert result.phone == "02-1234-5678"
            assert result.address == "서울시 강남구"
            assert len(result.menu_items) == 2
            assert result.menu_items[0].name == "김치찌개"
            assert result.menu_items[0].price == 8000
    
    @pytest.mark.asyncio
    async def test_crawl_restaurant_info_failure(self, crawler):
        """크롤링 실패 테스트"""
        test_url = "https://m.place.naver.com/place/1234567890"
        
        with patch.object(crawler, '_init_driver'), \
             patch.object(crawler, '_close_driver'), \
             patch.object(crawler, 'driver') as mock_driver:
            
            mock_driver.get.side_effect = Exception("Connection failed")
            
            with pytest.raises(CrawlingError):
                await crawler.crawl_restaurant_info(test_url)


class TestMenuExtraction:
    """메뉴 추출 관련 테스트"""
    
    @pytest.mark.asyncio
    async def test_click_menu_tab_success(self, crawler):
        """메뉴 탭 클릭 성공 테스트"""
        with patch.object(crawler, 'driver') as mock_driver:
            mock_tab = Mock()
            mock_driver.find_element.return_value = mock_tab
            
            # WebDriverWait 모킹
            with patch('services.crawler.WebDriverWait') as mock_wait:
                mock_wait.return_value.until.return_value = mock_tab
                
                await crawler._click_menu_tab()
                mock_tab.click.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_menu_with_bs4_success(self, crawler):
        """BeautifulSoup 메뉴 추출 성공 테스트"""
        html_content = '''
        <div class="place_section_content">
            <ul class="list_menu">
                <li>
                    <span class="name">김치찌개</span>
                    <span class="price">8,000원</span>
                </li>
                <li>
                    <span class="name">된장찌개</span>
                    <span class="price">7,000원</span>
                </li>
            </ul>
        </div>
        '''
        
        with patch.object(crawler, 'driver') as mock_driver:
            mock_driver.page_source = html_content
            
            result = await crawler._extract_menu_with_bs4()
            
            assert len(result) == 2
            assert result[0].name == "김치찌개"
            assert result[0].price == 8000
            assert result[1].name == "된장찌개"
            assert result[1].price == 7000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])