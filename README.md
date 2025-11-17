가상환경 생성
python -m venv .venv

가상환경 실행
윈도우: .venv\Scripts\activate
리눅스: source .venv/bin/activate
맥: source .venv/bin/activate

pip install -r requirements.txt로 필요한 것들 설치
현재 설치한 것 : pip install cryptography


healthy_scanner_backend/app/routers에서 api 구현하면 됨

(1) 각각의 폴더에 대한 부연 설명

utils : JWT 발급 모듈 처리 폴더.
