"""
영수증 계산 로직 단위 테스트
"""

import pytest
from datetime import datetime
from models.receipt import ReceiptData, MenuItem

def test_receipt_subtotal_calculation():
    """소계 계산 테스트"""
    menu_items = [
        MenuItem(name="김치찌개", price=8000),
        MenuItem(name="된장찌개", price=7000),
        MenuItem(name="공기밥", price=1000)
    ]
    
    receipt = ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 식당",
        owner_name="홍길동",
        payment_method="신용카드",
        payment_datetime=datetime.now(),
        approval_number="12345678",
        menu_items=menu_items
    )
    
    assert receipt.subtotal == 16000

def test_receipt_vat_calculation():
    """부가세 계산 테스트"""
    menu_items = [
        MenuItem(name="김치찌개", price=10000)
    ]
    
    receipt = ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 식당",
        owner_name="홍길동",
        payment_method="신용카드",
        payment_datetime=datetime.now(),
        approval_number="12345678",
        menu_items=menu_items
    )
    
    assert receipt.vat == 1000  # 10% VAT

def test_receipt_total_calculation():
    """총액 계산 테스트"""
    menu_items = [
        MenuItem(name="김치찌개", price=10000),
        MenuItem(name="공기밥", price=1000)
    ]
    
    receipt = ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 식당",
        owner_name="홍길동",
        payment_method="신용카드",
        payment_datetime=datetime.now(),
        approval_number="12345678",
        menu_items=menu_items
    )
    
    assert receipt.subtotal == 11000
    assert receipt.vat == 1100
    assert receipt.total == 12100

def test_empty_menu_items():
    """빈 메뉴 리스트 테스트"""
    receipt = ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 식당",
        owner_name="홍길동",
        payment_method="신용카드",
        payment_datetime=datetime.now(),
        approval_number="12345678",
        menu_items=[]
    )
    
    assert receipt.subtotal == 0
    assert receipt.vat == 0
    assert receipt.total == 0

if __name__ == "__main__":
    pytest.main([__file__])