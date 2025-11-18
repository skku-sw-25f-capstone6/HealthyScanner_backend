가상환경 생성
python -m venv .venv

가상환경 실행
윈도우: .venv\Scripts\activate
리눅스: source .venv/bin/activate
맥: source .venv/bin/activate

pip install -r requirements.txt로 필요한 것들 설치
현재 설치한 것 : 

<Windows> - 서버 폴더 내에서 powershell, terminal로 실행할 것.
1. pip install cryptography (JWT 토큰 암호화를 위한 패키지)
2. pip install sqlalchemy pymysql (mySQL 동기화를 위한 패키지)
3. pip install fastapi (fastapi 동기화를 위한 패키지)
4. pip install httpx (카카오, 네이버 토큰 검증용 패키지)
5. pip install uvicorn[standard] (uvicorn 패키지 설치)

<MacOS>
1. pip install cryptography
2. pip install sqlalchemy pymysql
3. pip install fastapi
4. pip install httpx
5. pip install uvicorn[standard]
6. xcode-select --install (crytography가 c로 빌드되기 때문에 추가함- pip error 발생 가능성 고려)


<서버 가동 명령어>
uvicorn main:app --reload --host 0.0.0.0 --port 8000



healthy_scanner_backend/app/routers에서 api 구현하면 됨

(1) 각각의 폴더에 대한 부연 설명

utils : JWT 발급 모듈 처리 폴더.
