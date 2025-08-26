"""
영수증 생성기 API - Vercel Serverless Functions
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "🧾 영수증 생성기 API",
        "version": "1.0.2",
        "status": "running",
        "service": "receipt-backend",
        "platform": "Vercel",
        "timestamp": "2025-08-26T07:35:00"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "receipt-backend",
        "platform": "Vercel"
    })

@app.route('/api/test')
def test():
    return jsonify({
        "success": True,
        "message": "API 테스트 성공! 🎉",
        "data": {
            "business_name": "테스트 맛집",
            "menu_items": [
                {"name": "김치찌개", "price": 8000},
                {"name": "된장찌개", "price": 7000},
                {"name": "공기밥", "price": 1000}
            ]
        }
    })

@app.route('/api/crawl-menu', methods=['POST'])
def crawl_menu():
    try:
        data = request.json or {}
        naver_url = data.get('naver_place_url', '')
        business_name = data.get('business_name', '크롤링된 맛집')
        
        return jsonify({
            "success": True,
            "message": "크롤링 성공! (Mock 데이터)",
            "data": {
                "business_name": business_name,
                "phone": "02-1234-5678",
                "address": "서울특별시 강남구 테헤란로 123",
                "menu_items": [
                    {"name": "김치찌개", "price": 8000},
                    {"name": "된장찌개", "price": 7000},
                    {"name": "비빔밥", "price": 9000},
                    {"name": "공기밥", "price": 1000},
                    {"name": "계란말이", "price": 5000}
                ]
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "CRAWLING_FAILED",
            "message": f"크롤링 실패: {str(e)}",
            "code": "MANUAL_INPUT_REQUIRED"
        }), 422

@app.route('/api/generate-receipt', methods=['POST'])
def generate_receipt():
    try:
        data = request.json or {}
        business_name = data.get('business_name', '테스트 식당')
        menu_items = data.get('menu_items', [])
        
        # 메뉴가 없으면 기본 메뉴 사용
        if not menu_items:
            manual_menu = data.get('manual_menu', {})
            menu_items = manual_menu.get('menu_items', [])
        
        # 총액 계산
        total_amount = sum(item.get('price', 0) for item in menu_items)
        
        return jsonify({
            "success": True,
            "message": "영수증 생성 성공! 🧾",
            "data": {
                "pdf_download_url": "/api/download/pdf/receipt_sample.pdf",
                "png_download_url": "/api/download/png/receipt_sample.png",
                "receipt_info": {
                    "business_name": business_name,
                    "total_amount": total_amount,
                    "item_count": len(menu_items)
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "RECEIPT_GENERATION_FAILED",
            "message": f"영수증 생성 실패: {str(e)}"
        }), 500

@app.route('/api/validate-url', methods=['POST'])
def validate_url():
    try:
        data = request.json or {}
        url = data.get('url', '')
        
        if url.startswith('https://m.place.naver.com/'):
            return jsonify({
                "valid": True,
                "message": "유효한 네이버플레이스 URL입니다! ✅"
            })
        else:
            return jsonify({
                "valid": False,
                "message": "네이버플레이스 모바일 URL을 입력해주세요. (예: https://m.place.naver.com/place/...)"
            })
    except Exception as e:
        return jsonify({
            "valid": False,
            "message": f"URL 검증 중 오류가 발생했습니다: {str(e)}"
        }), 400

# Vercel 호환성을 위한 핸들러
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)