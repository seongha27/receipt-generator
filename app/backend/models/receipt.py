from pydantic import BaseModel, validator
from typing import List, Optional, Union
from datetime import datetime

class MenuItem(BaseModel):
    name: str
    price: int
    options: Optional[str] = None

class CrawlRequest(BaseModel):
    naver_place_url: str
    business_number: str
    business_name: str
    owner_name: str
    payment_method: str
    payment_datetime: datetime
    approval_number: str
    
    @validator('business_number')
    def validate_business_number(cls, v):
        # 사업자등록번호 형식 검증 (XXX-XX-XXXXX)
        import re
        if not re.match(r'^\d{3}-\d{2}-\d{5}$', v):
            raise ValueError('사업자등록번호는 XXX-XX-XXXXX 형식이어야 합니다')
        return v

class RestaurantInfo(BaseModel):
    business_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    menu_items: List[MenuItem] = []

class ReceiptData(BaseModel):
    business_number: str
    business_name: str
    owner_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_method: str
    payment_datetime: datetime
    approval_number: str
    menu_items: List[MenuItem]
    
    # 계산된 필드들
    @property
    def subtotal(self) -> int:
        return sum(item.price for item in self.menu_items)
    
    @property
    def vat(self) -> int:
        return int(self.subtotal * 0.1)
    
    @property
    def total(self) -> int:
        return self.subtotal + self.vat

class ManualMenuInput(BaseModel):
    menu_items: List[MenuItem]

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: Optional[str] = None