"""
pytest 설정 및 공통 픽스처
"""

import pytest
import asyncio
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock

from models.receipt import ReceiptData, MenuItem, RestaurantInfo


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처 (비동기 테스트용)"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_directory():
    """임시 디렉토리 픽스처"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_menu_items():
    """샘플 메뉴 아이템들"""
    return [
        MenuItem(name="김치찌개", price=8000, options="매운맛"),
        MenuItem(name="된장찌개", price=7000, options="보통맛"),
        MenuItem(name="공기밥", price=1000),
        MenuItem(name="계란말이", price=5000),
        MenuItem(name="콜라", price=2000)
    ]


@pytest.fixture
def sample_receipt_data(sample_menu_items):
    """샘플 영수증 데이터"""
    return ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 맛집",
        owner_name="홍길동",
        phone="02-1234-5678",
        address="서울특별시 강남구 테헤란로 123, 1층",
        payment_method="신용카드",
        payment_datetime=datetime(2024, 1, 15, 14, 30, 0),
        approval_number="12345678",
        menu_items=sample_menu_items
    )


@pytest.fixture
def sample_restaurant_info(sample_menu_items):
    """샘플 식당 정보"""
    return RestaurantInfo(
        business_name="테스트 맛집",
        phone="02-1234-5678", 
        address="서울특별시 강남구 테헤란로 123, 1층",
        menu_items=sample_menu_items
    )


@pytest.fixture
def mock_webdriver():
    """모킹된 WebDriver"""
    driver = Mock()
    driver.page_source = """
    <html>
        <head><title>테스트 맛집 : 네이버</title></head>
        <body>
            <h1 class="Fc1rA">테스트 맛집</h1>
            <div class="dry8f">
                <span>02-1234-5678</span>
                <span>서울특별시 강남구 테헤란로 123</span>
            </div>
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
        </body>
    </html>
    """
    return driver


@pytest.fixture
def sample_api_request():
    """샘플 API 요청 데이터"""
    return {
        "naver_place_url": "https://m.place.naver.com/place/1234567890",
        "business_number": "123-45-67890",
        "business_name": "테스트 맛집",
        "owner_name": "홍길동",
        "payment_method": "신용카드",
        "payment_datetime": "2024-01-15T14:30:00Z",
        "approval_number": "12345678"
    }


@pytest.fixture
def sample_manual_menu():
    """샘플 수동 입력 메뉴"""
    return {
        "menu_items": [
            {"name": "김치찌개", "price": 8000, "options": "매운맛"},
            {"name": "된장찌개", "price": 7000, "options": "보통맛"},
            {"name": "공기밥", "price": 1000}
        ]
    }


@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch):
    """환경변수 모킹 (모든 테스트에 자동 적용)"""
    monkeypatch.setenv("SELENIUM_HEADLESS", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "100")  # 테스트시 높은 제한
    monkeypatch.setenv("RATE_LIMIT_PERIOD", "60")


@pytest.fixture
def mock_chrome_driver():
    """Chrome 드라이버 모킹"""
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_file:
        chrome_driver_path = tmp_file.name
    
    yield chrome_driver_path
    
    # 정리
    if os.path.exists(chrome_driver_path):
        os.unlink(chrome_driver_path)


@pytest.fixture
def mock_font_files(temp_directory):
    """폰트 파일 모킹"""
    font_files = {}
    
    # 다양한 폰트 파일 생성
    font_names = ['malgun.ttf', 'gulim.ttc', 'NanumGothic.ttf']
    for font_name in font_names:
        font_path = os.path.join(temp_directory, font_name)
        with open(font_path, 'wb') as f:
            f.write(b'fake font data')  # 가짜 폰트 데이터
        font_files[font_name] = font_path
    
    return font_files


# pytest 마커 정의
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "slow: 느린 테스트 (실제 네트워크 요청 포함)"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "unit: 단위 테스트"
    )
    config.addinivalue_line(
        "markers", "crawler: 크롤링 관련 테스트"
    )
    config.addinivalue_line(
        "markers", "generator: 영수증 생성 관련 테스트"
    )


# 테스트 실행 전/후 훅
def pytest_sessionstart(session):
    """테스트 세션 시작시 실행"""
    print("\n🧪 영수증 생성기 테스트 시작")


def pytest_sessionfinish(session, exitstatus):
    """테스트 세션 종료시 실행"""
    if exitstatus == 0:
        print("\n✅ 모든 테스트 통과!")
    else:
        print(f"\n❌ 테스트 실패 (종료 코드: {exitstatus})")


# 테스트 결과 수집
@pytest.fixture(scope="session", autouse=True)
def test_results():
    """테스트 결과 수집용 픽스처"""
    results = {"passed": 0, "failed": 0, "errors": 0}
    return results


# 비동기 테스트 지원
@pytest.fixture
def async_client():
    """비동기 테스트 클라이언트"""
    from httpx import AsyncClient
    from main import app
    return AsyncClient(app=app, base_url="http://test")