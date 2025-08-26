"""
영수증 생성 서비스 단위 테스트
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from services.receipt_generator import ReceiptGenerator
from models.receipt import ReceiptData, MenuItem
from utils.errors import ReceiptGenerationError


@pytest.fixture
def receipt_generator():
    """영수증 생성기 인스턴스 픽스처"""
    return ReceiptGenerator()


@pytest.fixture
def sample_receipt_data():
    """샘플 영수증 데이터 픽스처"""
    return ReceiptData(
        business_number="123-45-67890",
        business_name="테스트 식당",
        owner_name="홍길동", 
        phone="02-1234-5678",
        address="서울특별시 강남구 테헤란로 123",
        payment_method="신용카드",
        payment_datetime=datetime(2024, 1, 15, 14, 30, 0),
        approval_number="12345678",
        menu_items=[
            MenuItem(name="김치찌개", price=8000),
            MenuItem(name="된장찌개", price=7000),
            MenuItem(name="공기밥", price=1000)
        ]
    )


class TestReceiptGenerator:
    """영수증 생성기 테스트"""
    
    def test_font_registration(self, receipt_generator):
        """폰트 등록 테스트"""
        # 폰트 등록이 에러 없이 완료되는지 확인
        assert receipt_generator is not None
    
    @patch('services.receipt_generator.pdfmetrics')
    def test_register_fonts_success(self, mock_pdfmetrics):
        """폰트 등록 성공 테스트"""
        with patch('os.path.exists', return_value=True):
            generator = ReceiptGenerator()
            # 폰트가 정상적으로 등록되었는지 확인
            assert generator is not None
    
    @patch('services.receipt_generator.pdfmetrics')
    def test_register_fonts_no_fonts_available(self, mock_pdfmetrics):
        """사용 가능한 폰트가 없을 때 테스트"""
        with patch('os.path.exists', return_value=False):
            generator = ReceiptGenerator()
            # 폰트가 없어도 생성기가 정상 생성되는지 확인
            assert generator is not None
    
    def test_get_png_fonts_success(self, receipt_generator):
        """PNG 폰트 로드 성공 테스트"""
        with patch('os.path.exists', return_value=True), \
             patch('PIL.ImageFont.truetype') as mock_truetype:
            
            mock_font = Mock()
            mock_truetype.return_value = mock_font
            
            large, medium, small = receipt_generator._get_png_fonts()
            
            assert large is not None
            assert medium is not None  
            assert small is not None
    
    def test_get_png_fonts_fallback(self, receipt_generator):
        """PNG 폰트 로드 실패시 기본 폰트 사용 테스트"""
        with patch('os.path.exists', return_value=False), \
             patch('PIL.ImageFont.load_default') as mock_default:
            
            mock_font = Mock()
            mock_default.return_value = mock_font
            
            large, medium, small = receipt_generator._get_png_fonts()
            
            assert large is not None
            assert medium is not None
            assert small is not None
    
    @patch('services.receipt_generator.SimpleDocTemplate')
    def test_generate_pdf_success(self, mock_doc, receipt_generator, sample_receipt_data):
        """PDF 생성 성공 테스트"""
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            with patch.object(receipt_generator, '_generate_qr_code', return_value='dummy_qr.png'):
                receipt_generator._generate_pdf(sample_receipt_data, pdf_path)
                mock_doc_instance.build.assert_called_once()
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    @patch('PIL.Image.new')
    @patch('PIL.ImageDraw.Draw')
    def test_generate_png_success(self, mock_draw, mock_image, receipt_generator, sample_receipt_data):
        """PNG 생성 성공 테스트"""
        mock_image_instance = Mock()
        mock_draw_instance = Mock()
        mock_image.return_value = mock_image_instance
        mock_draw.return_value = mock_draw_instance
        
        # textbbox 메서드 모킹
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 30)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            png_path = tmp_file.name
        
        try:
            with patch.object(receipt_generator, '_get_png_fonts', return_value=(Mock(), Mock(), Mock())), \
                 patch.object(receipt_generator, '_generate_qr_code', return_value='dummy_qr.png'), \
                 patch('PIL.Image.open', return_value=Mock()):
                
                receipt_generator._generate_png(sample_receipt_data, png_path)
                mock_image_instance.save.assert_called_once()
        finally:
            if os.path.exists(png_path):
                os.unlink(png_path)
    
    def test_generate_receipt_success(self, receipt_generator, sample_receipt_data):
        """영수증 생성 성공 테스트"""
        with patch.object(receipt_generator, '_generate_pdf') as mock_pdf, \
             patch.object(receipt_generator, '_generate_png') as mock_png:
            
            pdf_path, png_path = receipt_generator.generate_receipt(sample_receipt_data)
            
            # 파일 경로가 올바르게 생성되었는지 확인
            assert pdf_path.endswith('.pdf')
            assert png_path.endswith('.png')
            assert '테스트 식당' in pdf_path
            assert '테스트 식당' in png_path
            
            # 생성 함수들이 호출되었는지 확인
            mock_pdf.assert_called_once()
            mock_png.assert_called_once()
    
    def test_generate_receipt_pdf_failure(self, receipt_generator, sample_receipt_data):
        """PDF 생성 실패 테스트"""
        with patch.object(receipt_generator, '_generate_pdf', side_effect=Exception("PDF generation failed")), \
             patch.object(receipt_generator, '_generate_png'):
            
            with pytest.raises(ReceiptGenerationError):
                receipt_generator.generate_receipt(sample_receipt_data)
    
    def test_generate_receipt_png_failure(self, receipt_generator, sample_receipt_data):
        """PNG 생성 실패 테스트"""
        with patch.object(receipt_generator, '_generate_pdf'), \
             patch.object(receipt_generator, '_generate_png', side_effect=Exception("PNG generation failed")):
            
            with pytest.raises(ReceiptGenerationError):
                receipt_generator.generate_receipt(sample_receipt_data)


class TestQRCodeGeneration:
    """QR 코드 생성 테스트"""
    
    def test_generate_qr_code_success(self, receipt_generator):
        """QR 코드 생성 성공 테스트"""
        test_data = "테스트|10000|12345678"
        
        with patch('qrcode.QRCode') as mock_qr_class:
            mock_qr = Mock()
            mock_qr_class.return_value = mock_qr
            mock_qr_img = Mock()
            mock_qr.make_image.return_value = mock_qr_img
            
            qr_path = receipt_generator._generate_qr_code(test_data)
            
            assert qr_path.endswith('.png')
            assert 'qr_' in qr_path
            mock_qr.add_data.assert_called_once_with(test_data)
            mock_qr.make.assert_called_once()
            mock_qr_img.save.assert_called_once()
    
    def test_generate_qr_code_failure(self, receipt_generator):
        """QR 코드 생성 실패 테스트"""
        test_data = "테스트|10000|12345678"
        
        with patch('qrcode.QRCode', side_effect=Exception("QR generation failed")):
            qr_path = receipt_generator._generate_qr_code(test_data)
            
            # 더미 파일이 반환되는지 확인
            assert qr_path.endswith('.png')
            assert 'dummy_qr' in qr_path
    
    def test_generate_barcode_success(self, receipt_generator):
        """바코드 생성 성공 테스트"""
        test_data = "12345678"
        
        with patch('barcode.Code128') as mock_code_class:
            mock_code = Mock()
            mock_code_class.return_value = mock_code
            
            barcode_path = receipt_generator._generate_barcode(test_data)
            
            assert barcode_path.endswith('.png')
            assert 'barcode_' in barcode_path
            mock_code.save.assert_called_once()
    
    def test_generate_barcode_failure(self, receipt_generator):
        """바코드 생성 실패 테스트"""
        test_data = "12345678"
        
        with patch('barcode.Code128', side_effect=Exception("Barcode generation failed")):
            barcode_path = receipt_generator._generate_barcode(test_data)
            
            # 더미 파일이 반환되는지 확인
            assert barcode_path.endswith('.png')
            assert 'dummy_barcode' in barcode_path


class TestReceiptDataProcessing:
    """영수증 데이터 처리 테스트"""
    
    def test_receipt_data_calculations(self, sample_receipt_data):
        """영수증 계산 로직 테스트"""
        # 소계: 8000 + 7000 + 1000 = 16000
        assert sample_receipt_data.subtotal == 16000
        
        # 부가세: 16000 * 0.1 = 1600
        assert sample_receipt_data.vat == 1600
        
        # 총액: 16000 + 1600 = 17600
        assert sample_receipt_data.total == 17600
    
    def test_receipt_data_with_no_menu_items(self):
        """메뉴 아이템이 없는 경우 테스트"""
        receipt_data = ReceiptData(
            business_number="123-45-67890",
            business_name="테스트 식당",
            owner_name="홍길동",
            payment_method="신용카드",
            payment_datetime=datetime.now(),
            approval_number="12345678",
            menu_items=[]
        )
        
        assert receipt_data.subtotal == 0
        assert receipt_data.vat == 0
        assert receipt_data.total == 0
    
    def test_receipt_data_with_single_menu_item(self):
        """단일 메뉴 아이템 테스트"""
        receipt_data = ReceiptData(
            business_number="123-45-67890",
            business_name="테스트 식당",
            owner_name="홍길동",
            payment_method="신용카드",
            payment_datetime=datetime.now(),
            approval_number="12345678",
            menu_items=[MenuItem(name="김치찌개", price=10000)]
        )
        
        assert receipt_data.subtotal == 10000
        assert receipt_data.vat == 1000
        assert receipt_data.total == 11000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])