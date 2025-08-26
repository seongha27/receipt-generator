"""
간단한 영수증 생성 서버 (Render.com 호환)
"""
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "영수증 생성기 API",
        "version": "1.0.1",
        "status": "running",
        "service": "receipt-backend",
        "timestamp": "2025-08-26T07:30:00"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "receipt-backend"
    })

@app.route('/api/v1/test')
def test():
    return jsonify({
        "success": True,
        "message": "API 테스트 성공",
        "data": {
            "business_name": "테스트 맛집",
            "menu_items": [
                {"name": "김치찌개", "price": 8000},
                {"name": "된장찌개", "price": 7000},
                {"name": "공기밥", "price": 1000}
            ]
        }
    })

@app.route('/api/v1/crawl-menu', methods=['POST'])
def crawl_menu():
    try:
        data = request.json
        naver_url = data.get('naver_place_url', '')
        
        # Mock 데이터 반환
        return jsonify({
            "success": True,
            "message": "크롤링 성공 (Mock 데이터)",
            "data": {
                "business_name": "크롤링된 맛집",
                "phone": "02-1234-5678",
                "address": "서울특별시 강남구 테헤란로 123",
                "menu_items": [
                    {"name": "김치찌개", "price": 8000},
                    {"name": "된장찌개", "price": 7000},
                    {"name": "비빔밥", "price": 9000},
                    {"name": "공기밥", "price": 1000}
                ]
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "CRAWLING_FAILED",
            "message": f"크롤링 실패: {str(e)}"
        }), 422

@app.route('/api/v1/generate-receipt', methods=['POST'])
def generate_receipt():
    try:
        data = request.json
        
        return jsonify({
            "success": True,
            "message": "영수증 생성 성공 (Mock)",
            "data": {
                "pdf_download_url": "/api/v1/download/pdf/receipt_sample.pdf",
                "png_download_url": "/api/v1/download/png/receipt_sample.png",
                "receipt_info": {
                    "business_name": data.get('business_name', '테스트 식당'),
                    "total_amount": 16000,
                    "item_count": 4
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "RECEIPT_GENERATION_FAILED",
            "message": f"영수증 생성 실패: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)