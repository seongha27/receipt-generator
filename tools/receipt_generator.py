"""
MCP 연동용 영수증 생성 도구
Claude Code와 연동하여 로컬에서 안전하게 영수증 생성
"""

import json
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# 백엔드 모듈 임포트 (경로 조정 필요)
sys.path.append('../app/backend')
from services.receipt_generator import ReceiptGenerator
from models.receipt import ReceiptData, MenuItem
from utils.errors import ReceiptGenerationError

logger = logging.getLogger(__name__)

class MCPReceiptGenerator:
    """MCP 연동용 영수증 생성 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.output_dir.mkdir(exist_ok=True)
        self.generator = ReceiptGenerator()
    
    async def generate_receipt(self, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        영수증 PDF/PNG 생성
        
        Args:
            receipt_data: 영수증 데이터 딕셔너리
            
        Returns:
            생성 결과 딕셔너리
        """
        try:
            logger.info("영수증 생성 시작")
            
            # 데이터 검증 및 변환
            receipt = self._validate_and_convert_data(receipt_data)
            
            # 영수증 생성
            pdf_path, png_path = self.generator.generate_receipt(receipt)
            
            # 파일을 설정된 출력 디렉토리로 이동
            final_pdf_path = self.output_dir / Path(pdf_path).name
            final_png_path = self.output_dir / Path(png_path).name
            
            # 파일 이동
            import shutil
            shutil.move(pdf_path, final_pdf_path)
            shutil.move(png_path, final_png_path)
            
            result = {
                "success": True,
                "data": {
                    "pdf_path": str(final_pdf_path),
                    "png_path": str(final_png_path),
                    "business_name": receipt.business_name,
                    "total_amount": receipt.total,
                    "menu_count": len(receipt.menu_items)
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "format": "PDF + PNG",
                    "dpi": self.config.get('image_dpi', 300)
                }
            }
            
            logger.info(f"영수증 생성 완료: {final_pdf_path}, {final_png_path}")
            return result
            
        except ReceiptGenerationError as e:
            logger.error(f"영수증 생성 오류: {e.message}")
            return {
                "success": False,
                "error": {
                    "type": e.error_type,
                    "message": e.message,
                    "code": "GENERATION_FAILED"
                }
            }
            
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)}")
            return {
                "success": False,
                "error": {
                    "type": "UNEXPECTED_ERROR",
                    "message": f"영수증 생성 중 오류가 발생했습니다: {str(e)}",
                    "code": "INTERNAL_ERROR"
                }
            }
    
    def _validate_and_convert_data(self, data: Dict[str, Any]) -> ReceiptData:
        """데이터 검증 및 ReceiptData 객체로 변환"""
        required_fields = [
            'business_number', 'business_name', 'owner_name',
            'payment_method', 'payment_datetime', 'approval_number'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")
        
        # 메뉴 항목 변환
        menu_items = []
        for item_data in data.get('menu_items', []):
            if isinstance(item_data, dict):
                menu_items.append(MenuItem(
                    name=item_data['name'],
                    price=item_data['price'],
                    options=item_data.get('options')
                ))
        
        if not menu_items:
            raise ValueError("최소 1개의 메뉴 항목이 필요합니다")
        
        # 날짜 변환
        payment_datetime = data['payment_datetime']
        if isinstance(payment_datetime, str):
            payment_datetime = datetime.fromisoformat(payment_datetime.replace('Z', '+00:00'))
        
        return ReceiptData(
            business_number=data['business_number'],
            business_name=data['business_name'],
            owner_name=data['owner_name'],
            phone=data.get('phone'),
            address=data.get('address'),
            payment_method=data['payment_method'],
            payment_datetime=payment_datetime,
            approval_number=data['approval_number'],
            menu_items=menu_items
        )

# MCP 도구 인터페이스 함수들
async def mcp_generate_receipt(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP에서 호출되는 영수증 생성 함수"""
    generator = MCPReceiptGenerator()
    
    receipt_data = params.get('receipt_data')
    if not receipt_data:
        return {
            "success": False,
            "error": {
                "type": "INVALID_PARAMS",
                "message": "receipt_data 파라미터가 필요합니다",
                "code": "MISSING_DATA"
            }
        }
    
    return await generator.generate_receipt(receipt_data)

def mcp_get_tool_info() -> Dict[str, Any]:
    """도구 정보 반환"""
    return {
        "name": "receipt_generator",
        "description": "영수증 PDF와 PNG 파일을 생성합니다",
        "version": "1.0.0",
        "functions": [
            {
                "name": "generate_receipt",
                "description": "영수증 데이터로부터 PDF/PNG 파일 생성",
                "parameters": {
                    "receipt_data": {
                        "type": "object",
                        "description": "영수증 생성에 필요한 데이터",
                        "required": True,
                        "properties": {
                            "business_number": {"type": "string"},
                            "business_name": {"type": "string"},
                            "owner_name": {"type": "string"},
                            "payment_method": {"type": "string"},
                            "payment_datetime": {"type": "string"},
                            "approval_number": {"type": "string"},
                            "menu_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price": {"type": "integer"},
                                        "options": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
    }

# CLI 실행 지원
if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="영수증 생성기 MCP 도구")
    parser.add_argument("--data", required=True, help="영수증 데이터 JSON 파일")
    parser.add_argument("--output-dir", help="출력 디렉토리")
    
    args = parser.parse_args()
    
    async def main():
        config = {}
        if args.output_dir:
            config['output_dir'] = args.output_dir
            
        generator = MCPReceiptGenerator(config)
        
        with open(args.data, 'r', encoding='utf-8') as f:
            receipt_data = json.load(f)
        
        result = await generator.generate_receipt(receipt_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(main())