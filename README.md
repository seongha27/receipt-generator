# 🧾 영수증 자동 생성 웹앱

네이버플레이스 정보를 크롤링하여 영수증을 자동 생성하는 풀스택 웹 애플리케이션입니다.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## ✨ 주요 기능

### 🔍 자동 크롤링
- **네이버플레이스 모바일 URL**에서 메뉴 정보 자동 추출
- **undetected-chromedriver**로 안정적인 크롤링
- **실패 시 수동 입력** 모달 지원

### 📄 다중 포맷 영수증 생성
- **PDF** (텍스트 검색 가능) + **PNG** (300DPI) 동시 생성
- **한글 폰트** 완벽 지원
- **QR 코드** 및 **바코드** 자동 생성
- **세금계산서 형식** 준수

### 🛡️ 보안 & 성능
- **CORS 설정**: `www.adsketch.info` 도메인만 허용
- **Rate Limiting**: 분당 요청 제한
- **입력 검증**: Pydantic 모델 기반 엄격한 데이터 검증
- **한글 오류 메시지** 제공

### 🔗 MCP 연결
- **Claude Code** 와의 안전한 로컬 도구 연결
- 크롤링 및 영수증 생성 도구를 CLI/API로 사용 가능

## 🚀 한줄 복붙 실행 명령

### 로컬 개발 실행
```bash
# 환경설정
cp .env.example .env

# 전체 프로젝트 실행 (Docker Compose)
docker-compose up --build

# 개별 실행
cd app/backend && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
cd app/frontend && npm install && npm run dev
```

### 프로덕션 배포
```bash
# Fly.io 배포 (권장)
fly auth login
fly deploy --config app/infra/fly.toml

# Render 배포 (GitHub 연결 후 자동 배포)
# render.yaml 파일을 사용하여 자동 구성됨
```

## 📁 프로젝트 구조

```
영수증제작/
├── 📁 app/
│   ├── 📁 backend/                # 🐍 FastAPI 백엔드
│   │   ├── main.py               # 메인 애플리케이션
│   │   ├── 📁 models/            # Pydantic 데이터 모델
│   │   │   └── receipt.py
│   │   ├── 📁 routes/            # API 라우터
│   │   │   └── receipt_routes.py
│   │   ├── 📁 services/          # 핵심 서비스
│   │   │   ├── crawler.py        # 네이버플레이스 크롤러
│   │   │   └── receipt_generator.py  # PDF/PNG 생성기
│   │   ├── 📁 utils/             # 유틸리티
│   │   │   ├── user_agents.py    # User-Agent 관리
│   │   │   └── errors.py         # 에러 핸들링
│   │   ├── requirements.txt      # Python 의존성
│   │   └── Dockerfile
│   ├── 📁 frontend/              # ⚛️ React 프론트엔드
│   │   ├── 📁 src/
│   │   │   ├── App.jsx          # 메인 앱
│   │   │   └── 📁 components/   # React 컴포넌트
│   │   │       ├── ReceiptForm.jsx
│   │   │       ├── ManualMenuModal.jsx
│   │   │       ├── ResultDisplay.jsx
│   │   │       ├── LoadingSpinner.jsx
│   │   │       └── ErrorMessage.jsx
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   └── 📁 infra/                 # 🚀 배포 설정
│       ├── fly.toml             # Fly.io 설정
│       └── render.yaml          # Render 설정
├── 📁 config/
│   └── mcp.config.json          # MCP 연결 설정
├── 📁 tools/                    # 🛠️ MCP 도구들
│   ├── receipt_crawler.py       # 크롤링 MCP 도구
│   └── receipt_generator.py     # 생성 MCP 도구
├── docker-compose.yml           # 로컬 개발용
├── .env.example                 # 환경변수 예시
└── README.md
```

## 🛠️ 기술 스택

### 백엔드
- **FastAPI** - 고성능 Python API 프레임워크
- **undetected-chromedriver** - 안전한 Selenium 크롤링
- **ReportLab** - PDF 생성 (텍스트 검색 가능)
- **Pillow** - 고해상도 PNG 생성 (300DPI)
- **SlowAPI** - Rate Limiting
- **Pydantic** - 데이터 검증 및 직렬화

### 프론트엔드
- **React 18** - 최신 React 훅 사용
- **Vite** - 빠른 개발 서버 및 빌드 도구
- **Tailwind CSS** - 유틸리티 기반 스타일링
- **React Hook Form** - 폼 상태 관리
- **Lucide React** - 모던 아이콘 패키지

### 배포 & 인프라
- **Docker** - 컨테이너화
- **Fly.io** - 메인 배포 플랫폼 (2GB RAM, Chrome 최적화)
- **Render** - 대안 배포 플랫폼
- **Nginx** - 프론트엔드 서버

### MCP (Model Context Protocol)
- **Claude Code 연결** - 로컬 도구 안전 연결
- **Python MCP 서버** - 크롤링 및 생성 도구 제공

## 📋 환경 설정

### 1. 환경변수 파일 설정
```bash
cp .env.example .env
```

### 2. 필수 환경변수 편집
```bash
# 백엔드 설정
PORT=8000
ALLOWED_ORIGINS=http://www.adsketch.info,https://www.adsketch.info,http://localhost:3000
LOG_LEVEL=INFO

# 프론트엔드 설정
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Chrome 설정 (Docker 환경)
SELENIUM_HEADLESS=true
```

### 3. Chrome 설치 확인 (로컬 개발시)
- **Windows**: 자동 설치됨
- **macOS**: `brew install --cask google-chrome`
- **Linux**: `apt-get install google-chrome-stable`

## 🔧 개발 가이드

### 로컬 개발 환경 설정

#### 1. 백엔드 개발
```bash
cd app/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 프론트엔드 개발
```bash
cd app/frontend
npm install
npm run dev
```

#### 3. 전체 스택 (Docker)
```bash
docker-compose up --build
```

### API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `POST` | `/api/v1/crawl-menu` | 네이버플레이스 크롤링 |
| `POST` | `/api/v1/generate-receipt` | 영수증 생성 |
| `GET` | `/api/v1/download/pdf/{filename}` | PDF 다운로드 |
| `GET` | `/api/v1/download/png/{filename}` | PNG 다운로드 |
| `POST` | `/api/v1/validate-url` | URL 유효성 검사 |
| `GET` | `/health` | 헬스체크 |

### 네이버플레이스 URL 예시

```
# ✅ 올바른 모바일 URL 형식
https://m.place.naver.com/place/1234567890
https://m.place.naver.com/place/1234567890/menu

# 📋 DOM 셀렉터 후보 (2024년 최신)
상호명: ".Fc1rA", ".GHAhO", "h1.tit"
전화번호: "a[href^='tel:']", ".dry8f", ".xlx7Q"
주소: ".dry8f", ".place_blahblah", ".LDgIH"
메뉴: ".place_section_content .list_menu li", ".menu_list li"
```

## 🚀 배포 가이드

### Fly.io 배포 (권장)

#### 1. Fly CLI 설치
```bash
# macOS
brew install flyctl

# Linux/WSL
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

#### 2. 로그인 및 배포
```bash
fly auth login
fly deploy --config app/infra/fly.toml
```

#### 3. 볼륨 생성 (최초 1회)
```bash
fly volumes create receipt_temp_vol --region nrt --size 1
```

### Render 배포

#### 1. GitHub 연결
- Render 대시보드에서 GitHub 리포지토리 연결

#### 2. 서비스 설정
- **Backend**: `app/infra/render.yaml` 설정 사용 (Docker)
- **Frontend**: 정적 사이트로 배포 (Node.js)

#### 3. 환경변수 설정
```bash
# Backend Service
PYTHON_VERSION=3.11
SECRET_KEY=your-production-secret-key-here
ALLOWED_ORIGINS=https://www.adsketch.info,https://receipt-frontend.onrender.com

# Frontend Service  
NODE_VERSION=18
VITE_API_BASE_URL=https://receipt-backend.onrender.com/api/v1
```

## 🔗 MCP 연결 가이드

### MCP 설정

#### 1. 설정 파일 확인
```bash
cat config/mcp.config.json
```

#### 2. Claude Code 설정에 추가
```json
{
  "mcpServers": {
    "receipt-crawler": {
      "command": "python",
      "args": ["-m", "tools.receipt_crawler"],
      "cwd": "C:/Users/user/Desktop/영수증제작",
      "env": {
        "PYTHONPATH": "./app/backend:."
      }
    },
    "receipt-generator": {
      "command": "python",
      "args": ["-m", "tools.receipt_generator"],
      "cwd": "C:/Users/user/Desktop/영수증제작", 
      "env": {
        "PYTHONPATH": "./app/backend:."
      }
    }
  }
}
```

#### 3. MCP 도구 테스트
```bash
# 크롤링 도구 테스트
python tools/receipt_crawler.py --url "https://m.place.naver.com/place/1234567890"

# 영수증 생성 도구 테스트  
python tools/receipt_generator.py --data sample_receipt.json --output-dir ./output
```

### Claude Code에서 사용

MCP 연결 후 Claude Code에서 다음과 같이 사용 가능:

```
사용자: 이 네이버플레이스 URL에서 메뉴 정보 추출해줘
https://m.place.naver.com/place/1234567890

Claude: MCP 크롤링 도구를 사용하여 메뉴 정보를 추출하겠습니다.
[자동으로 receipt_crawler 도구 호출]
```

## 🔒 보안 및 제한사항

### 보안 설정
- **CORS**: `www.adsketch.info` 도메인만 허용
- **Rate Limiting**: 크롤링 분당 10회, 생성 분당 5회 제한
- **입력 검증**: Pydantic 모델을 통한 엄격한 데이터 검증
- **에러 처리**: 한글 오류 메시지 및 안전한 에러 노출

### 제한사항
- **네이버플레이스 정책**: 정책 변경시 크롤링 실패 가능
- **리소스 사용**: Selenium + Chrome으로 메모리 사용량 높음 (최소 2GB RAM 권장)
- **임시 파일**: 1시간 후 자동 삭제
- **동시 요청**: Rate Limiting으로 제한됨

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 크롤링 실패
```bash
# Chrome 버전 확인
google-chrome --version

# Chrome 업데이트 (Linux)
sudo apt update && sudo apt install --only-upgrade google-chrome-stable

# 수동 ChromeDriver 업데이트
pip install --upgrade undetected-chromedriver
```

#### 2. 한글 폰트 문제
```bash
# Linux에서 한글 폰트 설치
sudo apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra

# Docker에서 폰트 확인
docker exec -it receipt-backend ls -la /usr/share/fonts/truetype/nanum/
```

#### 3. 메모리 부족 (Docker)
```bash
# Docker 메모리 상태 확인
docker stats

# docker-compose 메모리 제한 증가
docker-compose up --build -d --memory=2g
```

#### 4. API 연결 오류
```bash
# 백엔드 서버 상태 확인
curl http://localhost:8000/health

# 환경변수 확인
echo $VITE_API_BASE_URL

# CORS 오류시 환경변수 확인
echo $ALLOWED_ORIGINS
```

### 로그 확인

```bash
# Docker Compose 로그
docker-compose logs backend
docker-compose logs frontend
docker-compose logs -f  # 실시간 로그

# 개별 컨테이너 로그  
docker logs receipt-backend
docker logs receipt-frontend

# 로그 레벨 조정 (.env 파일)
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 디버깅 모드

```bash
# 백엔드 디버깅 모드
cd app/backend
SELENIUM_HEADLESS=false LOG_LEVEL=DEBUG python main.py

# 프론트엔드 개발 모드
cd app/frontend  
npm run dev -- --host 0.0.0.0
```

## 📊 성능 최적화

### 메모리 사용량 최적화
- Chrome 헤드리스 모드 사용
- 크롤링 후 즉시 드라이버 종료
- 임시 파일 자동 정리

### 응답 시간 최적화
- 비동기 처리로 논블로킹 크롤링
- CDN을 통한 정적 자원 캐싱
- 적절한 Rate Limiting 설정

## 📞 지원 및 기여

### 이슈 리포팅
- **GitHub Issues** 사용
- 에러 로그와 환경 정보 첨부 필수

### 기능 요청
- **GitHub Discussions** 사용
- 구체적인 사용 사례와 함께 요청

### 개발 참여
1. Fork 후 feature 브랜치 생성
2. 테스트 코드 작성 및 통과 확인
3. Pull Request 제출

### 문서
- **API 문서**: [http://localhost:8000/docs](http://localhost:8000/docs) (개발시)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🏆 크레딧

### 개발팀
- **AdSketch Team** - 설계 및 개발
- **도메인**: [www.adsketch.info](http://www.adsketch.info)

### 오픈소스 라이브러리
- [FastAPI](https://fastapi.tiangolo.com/) - 백엔드 프레임워크
- [React](https://reactjs.org/) - 프론트엔드 프레임워크  
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - 안전한 크롤링
- [ReportLab](https://www.reportlab.com/) - PDF 생성
- [Tailwind CSS](https://tailwindcss.com/) - 스타일링

### 버전 히스토리
- **v1.0.0** (2024) - 초기 릴리스
  - 네이버플레이스 크롤링
  - PDF/PNG 영수증 생성
  - React 프론트엔드
  - Docker 배포 지원
  - MCP 연결 지원

---

**🎯 목표**: 사업자등록번호와 네이버플레이스 URL만으로 완벽한 영수증을 자동 생성하는 서비스

**📧 문의**: AdSketch 팀 - [www.adsketch.info](http://www.adsketch.info)