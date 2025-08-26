# Node.js 18 베이스 이미지
FROM node:18-alpine as build

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 파일들 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# Nginx를 사용한 프로덕션 이미지
FROM nginx:alpine

# 빌드된 파일을 nginx 디렉토리로 복사
COPY --from=build /app/dist /usr/share/nginx/html

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]