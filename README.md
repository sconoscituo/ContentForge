# ContentForge
> SNS 콘텐츠 자동 생성 AI SaaS

## 개요

ContentForge는 Gemini AI를 활용해 인스타그램 캡션, 유튜브 스크립트, 블로그 포스트, 트위터 글을 자동으로 생성하는 서비스입니다.
크레딧 기반 과금 모델로 운영되며, 월 무료 크레딧을 제공합니다.

**수익 구조**: 무료 플랜(월 10 크레딧) / 크레딧 충전 / 프리미엄 구독

## 기술 스택

- **Backend**: FastAPI 0.104, Python 3.11
- **DB**: SQLAlchemy 2.0 (async) + SQLite (aiosqlite)
- **AI**: Google Gemini API (콘텐츠 생성)
- **인증**: JWT (python-jose) + bcrypt
- **배포**: Docker + docker-compose

## 시작하기

### 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값을 설정합니다:

| 변수명 | 설명 |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `DATABASE_URL` | SQLite DB 경로 (기본값 사용 가능) |
| `SECRET_KEY` | JWT 서명용 시크릿 키 |
| `MONTHLY_FREE_CREDITS` | 월 무료 크레딧 수 (기본: 10) |
| `DEBUG` | 개발 환경 여부 (True/False) |

### 실행 방법

#### Docker (권장)

```bash
docker-compose up -d
```

#### 직접 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 API 문서를 확인하세요.

## API 문서

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| GET | `/` | 헬스체크 |
| GET | `/health` | 서버 상태 확인 |
| POST | `/users/register` | 회원가입 |
| POST | `/users/login` | 로그인 (JWT 발급) |
| GET | `/users/me` | 내 정보 조회 (크레딧 포함) |
| POST | `/content/generate` | AI 콘텐츠 생성 (크레딧 소모) |
| GET | `/content/` | 생성된 콘텐츠 목록 |
| GET | `/content/{id}` | 콘텐츠 상세 조회 |
| DELETE | `/content/{id}` | 콘텐츠 삭제 |
| POST | `/content/credits/charge` | 크레딧 충전 |

## 수익 구조

- **무료 플랜**: 월 10 크레딧 (콘텐츠 10개 생성)
- **크레딧 충전**: 100 크레딧 9,900원 / 500 크레딧 39,900원
- **프리미엄 구독** (월 19,900원): 월 500 크레딧 + 고급 템플릿 + 브랜드 톤 커스터마이징

## 라이선스

MIT
