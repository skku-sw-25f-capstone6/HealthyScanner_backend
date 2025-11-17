가상환경 생성
python -m venv .venv

가상환경 실행
윈도우: .venv\Scripts\activate
리눅스: source .venv/bin/activate
맥: source .venv/bin/activate

pip install -r requirements.txt로 필요한 것들 설치
현재 설치한 것 : 

pip install cryptography


healthy_scanner_backend/app/routers에서 api 구현하면 됨

(1) 각각의 폴더에 대한 부연 설명

core: 환경 설정 + 공통 기능 묶음
DAL: SQLAlchemy ORM 모델. 데이터 접근 코드
models: 서버 DB 테이블을 정의한 SQLAlchemy ORM 모델들이 모여 있는 곳
routers: FastAPI 라우팅(API 엔드포인트)
schemas: Pydantic 요청/응답 스키마
services: 서비스 계층, 비즈니스 로직
utils : JWT 발급 모듈 처리 폴더.
