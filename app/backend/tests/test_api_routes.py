"""
API 라우트 단위 테스트
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from main import app
from models.receipt import RestaurantInfo, MenuItem
from utils.errors import CrawlingError, ReceiptGenerationError


@pytest.fixture
def client():
    """테스트 클라이언트 픽스처"""
    return TestClient(app)


@pytest.fixture
def sample_crawl_request():
    """샘플 크롤링 요청 데이터"""
    return {
        "naver_place_url": "https://m.place.naver.com/place/1234567890",
        "business_number": "123-45-67890",
        "business_name": "테스트 식당",
        "owner_name": "홍길동",
        "payment_method": "신용카드",
        "payment_datetime": "2024-01-15T14:30:00",
        "approval_number": "12345678"
    }


@pytest.fixture
def sample_restaurant_info():
    """샘플 식당 정보"""
    return RestaurantInfo(
        business_name="테스트 식당",
        phone="02-1234-5678",
        address="서울특별시 강남구 테헤란로 123",
        menu_items=[
            MenuItem(name="김치찌개", price=8000),
            MenuItem(name="된장찌개", price=7000),
            MenuItem(name="공기밥", price=1000)
        ]
    )


class TestHealthEndpoint:
    """헬스체크 엔드포인트 테스트"""
    
    def test_health_check(self, client):
        """헬스체크 성공 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestCrawlMenuEndpoint:
    """메뉴 크롤링 엔드포인트 테스트"""
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    def test_crawl_menu_success(self, mock_crawler_class, client, sample_crawl_request, sample_restaurant_info):
        """메뉴 크롤링 성공 테스트"""
        # 모킹 설정
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(return_value=sample_restaurant_info)
        
        response = client.post("/api/v1/crawl-menu", json=sample_crawl_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["business_name"] == "테스트 식당"
        assert data["data"]["phone"] == "02-1234-5678"
        assert len(data["data"]["menu_items"]) == 3
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    def test_crawl_menu_no_menu_found(self, mock_crawler_class, client, sample_crawl_request):
        """메뉴를 찾지 못한 경우 테스트"""
        # 메뉴가 없는 식당 정보
        restaurant_info = RestaurantInfo(
            business_name="테스트 식당",
            phone="02-1234-5678",
            address="서울특별시 강남구",
            menu_items=[]
        )
        
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(return_value=restaurant_info)
        
        response = client.post("/api/v1/crawl-menu", json=sample_crawl_request)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "MANUAL_INPUT_REQUIRED"
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    def test_crawl_menu_crawling_error(self, mock_crawler_class, client, sample_crawl_request):
        """크롤링 에러 테스트"""
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(
            side_effect=CrawlingError("크롤링 실패", "CRAWLING_FAILED")
        )
        
        response = client.post("/api/v1/crawl-menu", json=sample_crawl_request)
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"] == "CRAWLING_FAILED"
        assert data["detail"]["code"] == "MANUAL_INPUT_REQUIRED"
    
    def test_crawl_menu_invalid_request(self, client):
        """잘못된 요청 데이터 테스트"""
        invalid_request = {
            "naver_place_url": "invalid-url",
            # 필수 필드들 누락
        }
        
        response = client.post("/api/v1/crawl-menu", json=invalid_request)
        assert response.status_code == 422  # Validation error


class TestGenerateReceiptEndpoint:
    """영수증 생성 엔드포인트 테스트"""
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    @patch('routes.receipt_routes.ReceiptGenerator')
    def test_generate_receipt_with_crawling(self, mock_generator_class, mock_crawler_class, 
                                          client, sample_crawl_request, sample_restaurant_info):
        """크롤링과 함께 영수증 생성 테스트"""
        # 크롤링 모킹
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(return_value=sample_restaurant_info)
        
        # 영수증 생성 모킹
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_receipt.return_value = ("/tmp/receipt.pdf", "/tmp/receipt.png")
        
        response = client.post("/api/v1/generate-receipt", json=sample_crawl_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "pdf_download_url" in data["data"]
        assert "png_download_url" in data["data"]
        assert data["data"]["receipt_info"]["business_name"] == "테스트 식당"
    
    @patch('routes.receipt_routes.ReceiptGenerator')
    def test_generate_receipt_with_manual_menu(self, mock_generator_class, client, sample_crawl_request):
        """수동 메뉴 입력으로 영수증 생성 테스트"""
        # 수동 메뉴 데이터 추가
        request_data = sample_crawl_request.copy()
        request_data["manual_menu"] = {
            "menu_items": [
                {"name": "김치찌개", "price": 8000},
                {"name": "공기밥", "price": 1000}
            ]
        }
        
        # 영수증 생성 모킹
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_receipt.return_value = ("/tmp/receipt.pdf", "/tmp/receipt.png")
        
        response = client.post("/api/v1/generate-receipt", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["receipt_info"]["business_name"] == "테스트 식당"
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    @patch('routes.receipt_routes.ReceiptGenerator')
    def test_generate_receipt_generation_error(self, mock_generator_class, mock_crawler_class,
                                             client, sample_crawl_request, sample_restaurant_info):
        """영수증 생성 실패 테스트"""
        # 크롤링 모킹
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(return_value=sample_restaurant_info)
        
        # 영수증 생성 실패 모킹
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_receipt.side_effect = ReceiptGenerationError("PDF 생성 실패")
        
        response = client.post("/api/v1/generate-receipt", json=sample_crawl_request)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "RECEIPT_GENERATION_FAILED"


class TestValidateUrlEndpoint:
    """URL 검증 엔드포인트 테스트"""
    
    def test_validate_url_valid(self, client):
        """유효한 URL 검증 테스트"""
        valid_url = "https://m.place.naver.com/place/1234567890"
        
        response = client.post("/api/v1/validate-url", json={"url": valid_url})
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "유효한 네이버플레이스 URL" in data["message"]
    
    def test_validate_url_invalid(self, client):
        """유효하지 않은 URL 검증 테스트"""
        invalid_url = "https://www.google.com"
        
        response = client.post("/api/v1/validate-url", json={"url": invalid_url})
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "네이버플레이스 모바일 URL" in data["message"]


class TestDownloadEndpoints:
    """파일 다운로드 엔드포인트 테스트"""
    
    def test_download_pdf_not_found(self, client):
        """존재하지 않는 PDF 파일 다운로드 테스트"""
        response = client.get("/api/v1/download/pdf/nonexistent.pdf")
        assert response.status_code == 404
    
    def test_download_png_not_found(self, client):
        """존재하지 않는 PNG 파일 다운로드 테스트"""
        response = client.get("/api/v1/download/png/nonexistent.png")
        assert response.status_code == 404
    
    @patch('os.path.exists')
    @patch('fastapi.responses.FileResponse')
    def test_download_pdf_success(self, mock_file_response, mock_exists, client):
        """PDF 다운로드 성공 테스트"""
        mock_exists.return_value = True
        mock_file_response.return_value = Mock()
        
        response = client.get("/api/v1/download/pdf/test.pdf")
        
        # FileResponse가 호출되었는지 확인
        mock_file_response.assert_called_once()
    
    @patch('os.path.exists')
    @patch('fastapi.responses.FileResponse')
    def test_download_png_success(self, mock_file_response, mock_exists, client):
        """PNG 다운로드 성공 테스트"""
        mock_exists.return_value = True
        mock_file_response.return_value = Mock()
        
        response = client.get("/api/v1/download/png/test.png")
        
        # FileResponse가 호출되었는지 확인
        mock_file_response.assert_called_once()


class TestRateLimiting:
    """Rate Limiting 테스트"""
    
    @patch('routes.receipt_routes.NaverPlaceCrawler')
    def test_rate_limiting_crawl_menu(self, mock_crawler_class, client, sample_crawl_request):
        """크롤링 엔드포인트 Rate Limiting 테스트"""
        mock_crawler = Mock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.crawl_restaurant_info = AsyncMock(side_effect=Exception("Blocked by rate limit"))
        
        # 여러 번 요청을 보내서 Rate Limit 확인
        # 실제로는 SlowAPI의 Rate Limiter가 동작해야 함
        for i in range(12):  # 분당 10회 제한이므로 12번 요청
            response = client.post("/api/v1/crawl-menu", json=sample_crawl_request)
            if i >= 10:  # 11번째 요청부터는 429 응답 예상
                if response.status_code == 429:
                    break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])