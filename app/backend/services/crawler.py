import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import List, Optional
import asyncio

from models.receipt import RestaurantInfo, MenuItem
from utils.user_agents import get_chrome_options
from utils.errors import CrawlingError

logger = logging.getLogger(__name__)

class NaverPlaceCrawler:
    def __init__(self):
        self.driver = None
    
    def _init_driver(self):
        """Selenium WebDriver 초기화"""
        if self.driver is None:
            try:
                options = get_chrome_options()
                # 헤드리스 모드 (서버 환경)
                options.add_argument('--headless')
                
                self.driver = uc.Chrome(options=options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
            except Exception as e:
                logger.error(f"WebDriver 초기화 실패: {str(e)}")
                raise CrawlingError("브라우저 초기화에 실패했습니다.", "DRIVER_INIT_FAILED")
    
    def _close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.warning(f"WebDriver 종료 중 오류: {str(e)}")
    
    async def crawl_restaurant_info(self, url: str) -> RestaurantInfo:
        """네이버플레이스에서 식당 정보 크롤링"""
        try:
            self._init_driver()
            
            # 페이지 로드
            logger.info(f"네이버플레이스 크롤링 시작: {url}")
            self.driver.get(url)
            
            # 페이지 로딩 대기
            await asyncio.sleep(3)
            
            # 기본 정보 추출
            business_name = await self._extract_business_name()
            phone = await self._extract_phone()
            address = await self._extract_address()
            
            # 메뉴 탭으로 이동
            menu_items = await self._extract_menu_items()
            
            return RestaurantInfo(
                business_name=business_name or "정보 없음",
                phone=phone,
                address=address,
                menu_items=menu_items
            )
            
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {str(e)}")
            raise CrawlingError(f"크롤링 실패: {str(e)}", "CRAWLING_FAILED")
        
        finally:
            self._close_driver()
    
    async def _extract_business_name(self) -> Optional[str]:
        """상호명 추출"""
        try:
            # 다양한 셀렉터 시도 (2024년 최신 네이버플레이스 구조)
            selectors = [
                ".Fc1rA",           # 2024년 새로운 네이버플레이스
                ".GHAhO",           # 이전 버전
                ".place_blahblah",  # 모바일 버전
                "h1.tit",           # 기존 네이버플레이스
                ".place_name",      # 백업 셀렉터
                "h1",               # 최후 수단
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name = element.text.strip()
                    if name and name != "네이버" and len(name) > 1:
                        logger.info(f"상호명 추출 성공 ({selector}): {name}")
                        return name
                except:
                    continue
            
            # BeautifulSoup로 재시도
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # title 태그에서 추출
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.text
                # "네이버플레이스" 및 관련 문자열 제거
                name = (title_text
                       .replace(" : 네이버", "")
                       .replace(" - 네이버플레이스", "")
                       .replace(" | 네이버플레이스", "")
                       .replace("네이버플레이스", "")
                       .strip())
                if name and name != "네이버" and len(name) > 1:
                    logger.info(f"상호명 추출 성공 (title): {name}")
                    return name
            
            # 최후 수단: 메타 태그 시도
            meta_tags = soup.find_all('meta', {'property': ['og:title', 'twitter:title']})
            for meta in meta_tags:
                content = meta.get('content', '')
                if content and content != "네이버플레이스":
                    name = content.replace(" : 네이버", "").replace(" - 네이버플레이스", "").strip()
                    if name and len(name) > 1:
                        logger.info(f"상호명 추출 성공 (meta): {name}")
                        return name
                    
        except Exception as e:
            logger.warning(f"상호명 추출 실패: {str(e)}")
        
        return None
    
    async def _extract_phone(self) -> Optional[str]:
        """전화번호 추출"""
        try:
            # 2024년 최신 전화번호 셀렉터들
            selectors = [
                "a[href^='tel:']",     # 전화 링크
                ".dry8f",              # 새로운 네이버플레이스 2024
                ".LDgIH",              # 이전 버전
                ".xlx7Q",              # 모바일 버전
                ".tel",                # 기존
                ".phone_number",       # 백업
                ".contact_tel"         # 최후 수단
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        phone = element.text.strip()
                        if not phone:
                            phone = element.get_attribute('href', '').replace('tel:', '')
                        
                        # 전화번호 형식 정규화
                        phone = re.sub(r'[^\d-]', '', phone)
                        
                        # 전화번호 형식 검증 (한국 전화번호)
                        if re.match(r'^[\d-]+$', phone) and len(phone.replace('-', '')) >= 9:
                            # 일반 전화번호나 휴대폰 번호 형식 확인
                            digits_only = phone.replace('-', '')
                            if (digits_only.startswith('02') or 
                                digits_only.startswith('0') and len(digits_only) in [10, 11]):
                                logger.info(f"전화번호 추출 성공 ({selector}): {phone}")
                                return phone
                except:
                    continue
            
            # BeautifulSoup로 재시도
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # href에서 tel: 링크 찾기
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            for link in tel_links:
                phone = link.get('href', '').replace('tel:', '')
                if phone and len(phone.replace('-', '')) >= 9:
                    logger.info(f"전화번호 추출 성공 (tel link): {phone}")
                    return phone
            
            # 텍스트에서 전화번호 패턴 찾기
            phone_patterns = [
                r'\b0\d{1,2}-\d{3,4}-\d{4}\b',  # 02-1234-5678
                r'\b0\d{2,3}\d{3,4}\d{4}\b'     # 0212345678
            ]
            
            page_text = soup.get_text()
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    if len(match.replace('-', '')) >= 9:
                        logger.info(f"전화번호 추출 성공 (pattern): {match}")
                        return match
                    
        except Exception as e:
            logger.warning(f"전화번호 추출 실패: {str(e)}")
        
        return None
    
    async def _extract_address(self) -> Optional[str]:
        """주소 추출"""
        try:
            # 2024년 최신 주소 셀렉터들
            selectors = [
                ".dry8f",              # 새로운 네이버플레이스 2024 (전화번호와 함께)
                ".place_blahblah",     # 모바일 버전
                ".LDgIH",              # 이전 버전
                ".addr",               # 기존
                ".address",            # 백업
                ".location_addr",      # 최후 수단
                ".place_address"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        address = element.text.strip()
                        
                        # 주소인지 확인 (한국 주소 키워드 포함)
                        address_keywords = [
                            '시', '도', '구', '군', '동', '로', '길', '면', '읍',
                            '번지', '호', '층', '번길', '대로'
                        ]
                        
                        # 전화번호가 아니고 주소 키워드가 포함된 경우
                        if (address and 
                            not re.match(r'^[\d-\s()]+$', address) and  # 전화번호 형식이 아님
                            any(keyword in address for keyword in address_keywords) and
                            len(address) > 5):  # 최소 길이
                            
                            logger.info(f"주소 추출 성공 ({selector}): {address}")
                            return address
                except:
                    continue
            
            # BeautifulSoup로 재시도
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 메타 태그에서 주소 찾기
            meta_tags = soup.find_all('meta', {'name': ['description', 'og:description']})
            for meta in meta_tags:
                content = meta.get('content', '')
                # 주소 패턴 찾기
                address_match = re.search(r'([가-힣]+[시도][\s가-힣\d-]+[구군][\s가-힣\d-]+)', content)
                if address_match:
                    address = address_match.group(1).strip()
                    logger.info(f"주소 추출 성공 (meta): {address}")
                    return address
            
            # 페이지 텍스트에서 한국 주소 패턴 찾기
            page_text = soup.get_text()
            address_patterns = [
                r'([가-힣]+시[\s가-힣\d-]+구[\s가-힣\d-]+)',  # 서울시 강남구 ...
                r'([가-힣]+도[\s가-힣\d-]+시[\s가-힣\d-]+)',  # 경기도 성남시 ...
                r'([가-힣]+구[\s가-힣\d-]+동[\s가-힣\d-]+)'   # 강남구 역삼동 ...
            ]
            
            for pattern in address_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    if len(match) > 8:  # 적절한 길이의 주소
                        logger.info(f"주소 추출 성공 (pattern): {match}")
                        return match
                    
        except Exception as e:
            logger.warning(f"주소 추출 실패: {str(e)}")
        
        return None
    
    async def _extract_menu_items(self) -> List[MenuItem]:
        """메뉴 아이템 추출"""
        menu_items = []
        
        try:
            # 1단계: 메뉴 탭으로 이동 (URL 직접 변경 또는 탭 클릭)
            current_url = self.driver.current_url
            
            # 메뉴 URL로 직접 이동 시도
            if '/menu' not in current_url:
                menu_url = current_url.rstrip('/') + '/menu'
                try:
                    logger.info(f"메뉴 페이지로 이동: {menu_url}")
                    self.driver.get(menu_url)
                    await asyncio.sleep(3)
                except:
                    # URL 변경 실패시 탭 클릭 시도
                    await self._click_menu_tab()
            
            # 2단계: 메뉴 항목 추출
            menu_selectors = [
                # 2024년 최신 네이버플레이스 메뉴 셀렉터
                ".place_section_content .list_menu li",
                ".place_section_content .menu_list li",
                ".menu_list_wrap li",
                ".restaurant_menu .menu_item",
                ".menu_wrap .menu_item",
                ".menu-list .menu-item",
                ".list_menu li",
                ".menu_list li"
            ]
            
            for selector in menu_selectors:
                try:
                    menu_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"셀렉터 {selector}로 {len(menu_elements)}개 요소 발견")
                    
                    if menu_elements:
                        for i, element in enumerate(menu_elements[:25]):  # 최대 25개
                            try:
                                menu_item = await self._parse_menu_item(element)
                                if menu_item:
                                    menu_items.append(menu_item)
                                    logger.debug(f"메뉴 {i+1}: {menu_item.name} - {menu_item.price}원")
                            except Exception as e:
                                logger.debug(f"메뉴 파싱 실패 {i+1}: {str(e)}")
                                continue
                        
                        if menu_items:  # 메뉴가 하나라도 추출되면 성공
                            break
                except Exception as e:
                    logger.debug(f"셀렉터 {selector} 실패: {str(e)}")
                    continue
            
            # 3단계: BeautifulSoup으로 재시도 (Selenium 실패시)
            if not menu_items:
                logger.info("BeautifulSoup으로 메뉴 추출 재시도")
                menu_items = await self._extract_menu_with_bs4()
            
            logger.info(f"메뉴 추출 완료: {len(menu_items)}개")
            return menu_items[:20]  # 최대 20개로 제한
            
        except Exception as e:
            logger.error(f"메뉴 추출 실패: {str(e)}")
            return []
    
    async def _click_menu_tab(self):
        """메뉴 탭 클릭 시도"""
        menu_tab_selectors = [
            "a[href*='menu']",
            ".tab_menu",
            ".menu_tab", 
            "button[data-tab='menu']",
            "[data-value='menu']",
            "a[data-tab='menu']"
        ]
        
        for selector in menu_tab_selectors:
            try:
                menu_tab = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                menu_tab.click()
                await asyncio.sleep(2)
                logger.info(f"메뉴 탭 클릭 성공: {selector}")
                return
            except:
                continue
        
        logger.warning("메뉴 탭 클릭 실패")
    
    async def _extract_menu_with_bs4(self) -> List[MenuItem]:
        """BeautifulSoup을 사용한 메뉴 추출"""
        menu_items = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 다양한 메뉴 패턴 시도
            menu_containers = soup.select('.place_section_content, .menu_list_wrap, .restaurant_menu')
            
            for container in menu_containers:
                # 메뉴 아이템들 찾기
                menu_elements = container.find_all(['li', 'div'], class_=re.compile(r'menu|item'))
                
                for element in menu_elements:
                    try:
                        # 메뉴명 찾기
                        name_element = element.find(['span', 'div', 'strong'], class_=re.compile(r'name|title|menu'))
                        if not name_element:
                            name_element = element.find(['span', 'div', 'strong'])
                        
                        # 가격 찾기  
                        price_element = element.find(['span', 'div'], class_=re.compile(r'price|cost|won'))
                        if not price_element:
                            # 텍스트에서 가격 패턴 찾기
                            text = element.get_text()
                            price_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', text)
                            if price_match:
                                price_text = price_match.group(1)
                            else:
                                continue
                        else:
                            price_text = price_element.get_text()
                        
                        if name_element:
                            name = name_element.get_text().strip()
                            price = int(re.sub(r'[^\d]', '', price_text)) if price_text else 0
                            
                            if name and price > 0:
                                menu_items.append(MenuItem(name=name, price=price))
                    except:
                        continue
                
                if menu_items:  # 메뉴를 찾으면 중단
                    break
            
            return menu_items[:20]
            
        except Exception as e:
            logger.warning(f"BeautifulSoup 메뉴 추출 실패: {str(e)}")
            return []
    
    async def _parse_menu_item(self, element) -> Optional[MenuItem]:
        """개별 메뉴 아이템 파싱"""
        try:
            # 메뉴명 추출
            name_selectors = [".name", ".menu_name", ".title", "strong", "h3", "h4"]
            name = ""
            
            for selector in name_selectors:
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_element.text.strip()
                    if name:
                        break
                except:
                    continue
            
            if not name:
                name = element.text.split('\n')[0].strip()
            
            # 가격 추출
            price_selectors = [".price", ".cost", ".won", ".menu_price"]
            price_text = ""
            
            for selector in price_selectors:
                try:
                    price_element = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    if price_text:
                        break
                except:
                    continue
            
            if not price_text:
                # 텍스트에서 가격 패턴 찾기
                text = element.text
                price_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', text)
                if price_match:
                    price_text = price_match.group(1)
            
            # 가격 숫자로 변환
            price = 0
            if price_text:
                price_numbers = re.findall(r'\d+', price_text.replace(',', ''))
                if price_numbers:
                    price = int(''.join(price_numbers))
            
            if name and price > 0:
                return MenuItem(name=name, price=price)
                
        except Exception as e:
            logger.warning(f"메뉴 아이템 파싱 실패: {str(e)}")
        
        return None