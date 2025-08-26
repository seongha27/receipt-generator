from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont
import qrcode
import barcode
from barcode.writer import ImageWriter
import tempfile
import os
import logging
from datetime import datetime
from typing import Tuple

from models.receipt import ReceiptData
from utils.errors import ReceiptGenerationError

logger = logging.getLogger(__name__)

class ReceiptGenerator:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self._register_fonts()
    
    def _register_fonts(self):
        """폰트 등록 (시스템 폰트 사용)"""
        try:
            # 운영체제별 한글 폰트 경로
            font_paths = [
                # Windows
                "C:/Windows/Fonts/malgun.ttf",    # 맑은 고딕
                "C:/Windows/Fonts/malgunbd.ttf",  # 맑은 고딕 Bold
                "C:/Windows/Fonts/gulim.ttc",     # 굴림
                "C:/Windows/Fonts/batang.ttc",    # 바탕
                # macOS
                "/System/Library/Fonts/AppleGothic.ttf",
                "/Library/Fonts/AppleGothic.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                # Linux
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                # Docker 환경에서 추가될 수 있는 경로
                "/fonts/NanumGothic.ttf",
                "/app/fonts/malgun.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Korean', font_path))
                        # Bold 버전도 시도
                        bold_path = font_path.replace('.ttf', 'bd.ttf').replace('Gothic.ttf', 'GothicBold.ttf')
                        if os.path.exists(bold_path):
                            pdfmetrics.registerFont(TTFont('KoreanBold', bold_path))
                        
                        logger.info(f"폰트 등록 성공: {font_path}")
                        return
                    except Exception as e:
                        logger.debug(f"폰트 등록 실패 ({font_path}): {str(e)}")
                        continue
            
            logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
            
        except Exception as e:
            logger.warning(f"폰트 등록 과정에서 오류: {str(e)}")
    
    def _get_png_fonts(self):
        """PNG용 한글 폰트 로드"""
        font_large = font_medium = font_small = None
        
        # 시스템별 한글 폰트 경로 
        font_paths = [
            # Windows
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/gulim.ttc", 
            # macOS
            "/System/Library/Fonts/AppleGothic.ttf",
            # Linux
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/fonts/NanumGothic.ttf",
            "/app/fonts/malgun.ttf"
        ]
        
        korean_font_path = None
        for path in font_paths:
            if os.path.exists(path):
                korean_font_path = path
                break
        
        try:
            if korean_font_path:
                font_large = ImageFont.truetype(korean_font_path, 24)
                font_medium = ImageFont.truetype(korean_font_path, 16)
                font_small = ImageFont.truetype(korean_font_path, 12)
                logger.info(f"PNG 한글 폰트 로드 성공: {korean_font_path}")
            else:
                raise FileNotFoundError("한글 폰트를 찾을 수 없습니다")
        except Exception as e:
            logger.warning(f"PNG 한글 폰트 로드 실패: {str(e)}, 기본 폰트 사용")
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default() 
            font_small = ImageFont.load_default()
        
        return font_large, font_medium, font_small
    
    def generate_receipt(self, receipt_data: ReceiptData) -> Tuple[str, str]:
        """영수증 PDF와 PNG 생성"""
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"receipt_{receipt_data.business_name}_{timestamp}"
            
            pdf_path = os.path.join(self.temp_dir, f"{filename_base}.pdf")
            png_path = os.path.join(self.temp_dir, f"{filename_base}.png")
            
            # PDF 생성
            self._generate_pdf(receipt_data, pdf_path)
            
            # PNG 생성
            self._generate_png(receipt_data, png_path)
            
            logger.info(f"영수증 생성 완료: PDF={pdf_path}, PNG={png_path}")
            return pdf_path, png_path
            
        except Exception as e:
            logger.error(f"영수증 생성 실패: {str(e)}")
            raise ReceiptGenerationError(f"영수증 생성 중 오류가 발생했습니다: {str(e)}")
    
    def _generate_pdf(self, receipt_data: ReceiptData, pdf_path: str):
        """PDF 영수증 생성"""
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # 한글 스타일 설정
            korean_style = ParagraphStyle(
                'Korean',
                parent=styles['Normal'],
                fontName='Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=10,
                leading=12
            )
            
            title_style = ParagraphStyle(
                'KoreanTitle',
                parent=korean_style,
                fontSize=16,
                alignment=1,  # 중앙 정렬
                spaceAfter=12
            )
            
            # 제목
            story.append(Paragraph("영수증", title_style))
            story.append(Spacer(1, 12))
            
            # 사업장 정보
            business_info = [
                f"상호: {receipt_data.business_name}",
                f"사업자등록번호: {receipt_data.business_number}",
                f"대표자: {receipt_data.owner_name}",
            ]
            
            if receipt_data.phone:
                business_info.append(f"전화번호: {receipt_data.phone}")
            if receipt_data.address:
                business_info.append(f"주소: {receipt_data.address}")
            
            for info in business_info:
                story.append(Paragraph(info, korean_style))
            
            story.append(Spacer(1, 12))
            
            # 구분선
            story.append(Paragraph("=" * 50, korean_style))
            story.append(Spacer(1, 6))
            
            # 메뉴 테이블
            table_data = [["메뉴명", "가격"]]
            for item in receipt_data.menu_items:
                table_data.append([item.name, f"{item.price:,}원"])
            
            # 합계 정보
            table_data.extend([
                ["", ""],
                ["소계", f"{receipt_data.subtotal:,}원"],
                ["부가세", f"{receipt_data.vat:,}원"],
                ["총액", f"{receipt_data.total:,}원"]
            ])
            
            table = Table(table_data, colWidths=[3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, -4), (-1, -4), 1, colors.black),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 12))
            
            # 결제 정보
            payment_info = [
                f"결제방법: {receipt_data.payment_method}",
                f"결제일시: {receipt_data.payment_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
                f"승인번호: {receipt_data.approval_number}"
            ]
            
            for info in payment_info:
                story.append(Paragraph(info, korean_style))
            
            story.append(Spacer(1, 12))
            
            # QR 코드 생성
            qr_data = f"{receipt_data.business_name}|{receipt_data.total}|{receipt_data.approval_number}"
            qr_path = self._generate_qr_code(qr_data)
            
            story.append(Paragraph("거래확인용 QR코드:", korean_style))
            story.append(Spacer(1, 6))
            
            # PDF 빌드
            doc.build(story)
            
            # 임시 QR 파일 삭제
            if os.path.exists(qr_path):
                os.remove(qr_path)
                
        except Exception as e:
            logger.error(f"PDF 생성 실패: {str(e)}")
            raise ReceiptGenerationError(f"PDF 생성 실패: {str(e)}")
    
    def _generate_png(self, receipt_data: ReceiptData, png_path: str):
        """PNG 영수증 생성 (300DPI)"""
        try:
            # 영수증 크기 (300DPI 기준)
            width, height = 800, 1200
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # 한글 폰트 로드
            font_large, font_medium, font_small = self._get_png_fonts()
            
            y_pos = 30
            
            # 제목
            title = "영수증"
            title_bbox = draw.textbbox((0, 0), title, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((width - title_width) // 2, y_pos), title, fill='black', font=font_large)
            y_pos += 50
            
            # 사업장 정보
            business_info = [
                f"상호: {receipt_data.business_name}",
                f"사업자등록번호: {receipt_data.business_number}",
                f"대표자: {receipt_data.owner_name}",
            ]
            
            if receipt_data.phone:
                business_info.append(f"전화번호: {receipt_data.phone}")
            if receipt_data.address:
                business_info.append(f"주소: {receipt_data.address}")
            
            for info in business_info:
                draw.text((30, y_pos), info, fill='black', font=font_medium)
                y_pos += 25
            
            y_pos += 20
            
            # 구분선
            draw.line((30, y_pos, width-30, y_pos), fill='black', width=2)
            y_pos += 30
            
            # 메뉴 헤더
            draw.text((30, y_pos), "메뉴명", fill='black', font=font_medium)
            draw.text((width-150, y_pos), "가격", fill='black', font=font_medium)
            y_pos += 30
            
            # 메뉴 항목들
            for item in receipt_data.menu_items:
                draw.text((30, y_pos), item.name, fill='black', font=font_small)
                price_text = f"{item.price:,}원"
                draw.text((width-150, y_pos), price_text, fill='black', font=font_small)
                y_pos += 20
            
            y_pos += 20
            
            # 합계 정보
            draw.line((30, y_pos, width-30, y_pos), fill='black', width=1)
            y_pos += 20
            
            totals = [
                ("소계", receipt_data.subtotal),
                ("부가세", receipt_data.vat),
                ("총액", receipt_data.total)
            ]
            
            for label, amount in totals:
                draw.text((30, y_pos), label, fill='black', font=font_medium)
                amount_text = f"{amount:,}원"
                draw.text((width-150, y_pos), amount_text, fill='black', font=font_medium)
                y_pos += 25
            
            y_pos += 30
            
            # 결제 정보
            payment_info = [
                f"결제방법: {receipt_data.payment_method}",
                f"결제일시: {receipt_data.payment_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
                f"승인번호: {receipt_data.approval_number}"
            ]
            
            for info in payment_info:
                draw.text((30, y_pos), info, fill='black', font=font_small)
                y_pos += 20
            
            y_pos += 30
            
            # QR 코드
            qr_data = f"{receipt_data.business_name}|{receipt_data.total}|{receipt_data.approval_number}"
            qr_path = self._generate_qr_code(qr_data)
            
            try:
                qr_img = Image.open(qr_path)
                qr_img = qr_img.resize((100, 100))
                image.paste(qr_img, ((width - 100) // 2, y_pos))
            except:
                draw.text((30, y_pos), "QR코드 생성 실패", fill='black', font=font_small)
            
            # PNG 저장 (300DPI)
            image.save(png_path, 'PNG', dpi=(300, 300))
            
            # 임시 QR 파일 삭제
            if os.path.exists(qr_path):
                os.remove(qr_path)
                
        except Exception as e:
            logger.error(f"PNG 생성 실패: {str(e)}")
            raise ReceiptGenerationError(f"PNG 생성 실패: {str(e)}")
    
    def _generate_qr_code(self, data: str) -> str:
        """QR 코드 생성"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = os.path.join(self.temp_dir, f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png")
            qr_img.save(qr_path)
            
            return qr_path
            
        except Exception as e:
            logger.warning(f"QR 코드 생성 실패: {str(e)}")
            # 더미 파일 반환
            dummy_path = os.path.join(self.temp_dir, "dummy_qr.png")
            try:
                Image.new('RGB', (100, 100), 'white').save(dummy_path)
            except:
                pass
            return dummy_path
    
    def _generate_barcode(self, data: str) -> str:
        """바코드 생성 (Code128)"""
        try:
            from barcode import Code128
            
            # 승인번호로 바코드 생성
            code = Code128(data[:12], writer=ImageWriter())  # 최대 12자리
            barcode_path = os.path.join(self.temp_dir, f"barcode_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png")
            
            # 바코드 이미지 생성
            code.save(barcode_path.replace('.png', ''))  # save()는 확장자를 자동 추가
            
            return barcode_path
            
        except Exception as e:
            logger.warning(f"바코드 생성 실패: {str(e)}")
            # 더미 파일 반환
            dummy_path = os.path.join(self.temp_dir, "dummy_barcode.png")
            try:
                Image.new('RGB', (200, 50), 'white').save(dummy_path)
            except:
                pass
            return dummy_path