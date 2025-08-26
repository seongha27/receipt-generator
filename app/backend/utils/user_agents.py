import random

# 실제 모바일 브라우저 User-Agent 풀
MOBILE_USER_AGENTS = [
    # Samsung Galaxy S21
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    # iPhone 14
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # Galaxy S22
    "Mozilla/5.0 (Linux; Android 12; SM-S906N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    # iPhone 13 Pro
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    # Pixel 7
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
]

def get_random_user_agent() -> str:
    """랜덤 모바일 User-Agent 반환"""
    return random.choice(MOBILE_USER_AGENTS)

def get_chrome_options():
    """크롤링용 Chrome 옵션 설정"""
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--window-size=375,667')  # iPhone 크기
    
    # 모바일 에뮬레이션
    mobile_emulation = {
        "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
        "userAgent": get_random_user_agent()
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    return options