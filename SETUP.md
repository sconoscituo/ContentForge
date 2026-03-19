# ContentForge - 프로젝트 설정 가이드

## 프로젝트 소개

ContentForge는 Google Gemini AI를 활용하여 Instagram, YouTube, 블로그, Twitter 등 다양한 플랫폼에 최적화된 콘텐츠를 자동 생성하는 SaaS 서비스입니다. 크레딧 기반 과금 모델과 PortOne 결제 연동을 지원합니다.

- **기술 스택**: FastAPI, SQLAlchemy, SQLite, Google Gemini AI
- **인증**: JWT (python-jose)
- **결제**: PortOne (포트원)

---

## 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 (필수) | [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 비밀 키 (필수, 임의의 긴 문자열) | 직접 생성 (`openssl rand -hex 32`) |
| `PORTONE_API_KEY` | 포트원 결제 API 키 (선택) | [https://admin.portone.io](https://admin.portone.io) |
| `PORTONE_API_SECRET` | 포트원 결제 API 시크릿 (선택) | [https://admin.portone.io](https://admin.portone.io) |
| `DATABASE_URL` | DB 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 (`true`/`false`, 기본: `false`) | - |
| `MONTHLY_FREE_CREDITS` | 월 무료 크레딧 수 (기본: `10`) | - |

### 크레딧 소모량 (기본값)

| 플랫폼 | 소모 크레딧 |
|---|---|
| Instagram | 1 |
| Twitter | 1 |
| Blog | 2 |
| YouTube | 3 |

---

## GitHub Secrets 설정 방법

GitHub Actions CI/CD를 사용하는 경우, 저장소의 **Settings > Secrets and variables > Actions** 에서 아래 Secrets를 등록합니다.

```
GEMINI_API_KEY        = <Google AI Studio에서 발급한 키>
SECRET_KEY            = <openssl rand -hex 32 으로 생성한 값>
PORTONE_API_KEY       = <포트원 API 키> (선택)
PORTONE_API_SECRET    = <포트원 API 시크릿> (선택)
```

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/ContentForge.git
cd ContentForge
```

### 2. Python 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./contentforge.db
DEBUG=true
MONTHLY_FREE_CREDITS=10
PORTONE_API_KEY=
PORTONE_API_SECRET=
```

---

## 실행 방법

### 로컬 실행 (uvicorn)

```bash
cd ContentForge
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Compose로 실행

```bash
docker-compose up --build
```

### 테스트 실행

```bash
pytest tests/
```
