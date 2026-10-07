# Code Contrast

같은 요구사항으로 작성된 두 Python 코드의 **구조와 정적 분석 결과**를 나란히 비교하는 학습용 웹 앱입니다. 코드를 평가하거나 실행하지 않습니다. 사용자가 원래 프롬프트와 두 코드를 직접 붙여넣습니다.

## V0.1 기능

- Monaco Editor에서 CODE A와 CODE B 입력, 각 코드의 모델 이름 선택 또는 직접 입력
- Python AST로 줄 수, 함수와 클래스, import, 데코레이터, 예외 처리, async/await, 타입 힌트, 문서 문자열, 함수 길이, 최대 중첩 깊이 계산
- Ruff 정적 검사 결과를 코드별로 표시
- 수치 비교, 규칙 기반 구조 차이 문장, 공통/전용 import 표시
- 문법 오류가 있는 코드를 별도로 표시하고 다른 코드의 분석은 유지
- 선택적으로 Monaco Diff View 열기

두 코드 모두 Python 코드여야 합니다. 모델 이름은 표시용 라벨이며 분석 결과에 영향을 주지 않습니다. 외부 LLM API나 Ollama는 호출하지 않습니다.

## 기술 스택과 구조

- Frontend: React, TypeScript, Vite, Monaco Editor, 일반 CSS
- Backend: Python 3.12 이상, FastAPI, Pydantic, Python `ast`, Ruff, uv

Monaco 파일은 프런트엔드 번들에 포함되므로 편집기를 위해 외부 CDN에 접속하지 않습니다.

```text
gpt_vs_claude/
├─ backend/
│  ├─ app/
│  │  ├─ analyzers/       # AST, 줄 수, Ruff
│  │  ├─ routers/         # POST /api/compare
│  │  ├─ schemas/         # 요청/응답 모델
│  │  ├─ services/        # 비교 및 요약 규칙
│  │  └─ main.py          # FastAPI, CORS, health
│  ├─ tests/
│  └─ pyproject.toml
└─ frontend/
   ├─ src/components/
   ├─ src/pages/
   ├─ src/api/
   ├─ src/types/
   └─ package.json
```

## 설치 및 실행

Python 3.12 이상, [uv](https://docs.astral.sh/uv/), Node.js 20 이상 및 npm이 필요합니다. 저장소를 복제한 뒤 터미널 두 개를 사용합니다.

```bash
git clone https://github.com/EOCHAEEUN/gpt_vs_claude.git
cd gpt_vs_claude
```

백엔드:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

프런트엔드:

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. 백엔드는 `http://localhost:8000`에서 실행됩니다. Vite 개발 서버는 `/api`를 백엔드로 프록시합니다. 별도 배포에서 다른 주소를 사용하려면 `frontend/.env.example`을 참고해 `VITE_API_BASE_URL`을 설정하세요.

## API

`GET /health` → `{"status":"ok"}`

`POST /api/compare`:

```json
{
  "prompt": "FastAPI로 로그인 API를 만들어줘.",
  "code_a": "import os\nprint('A')",
  "code_b": "import sys\nprint('B')",
  "label_a": "GPT",
  "label_b": "Claude"
}
```

응답에는 각 코드의 `valid_python`, `syntax_error`, `metrics`, `ruff_issues`, `ruff_error`, 그리고 `differences`, `import_comparison`, `summary`가 있습니다. 문법 오류가 있으면 그 코드의 `metrics`는 `null`입니다. Ruff를 실행할 수 없는 환경이면 `ruff_error`로 사유를 알립니다. 빈 코드 요청은 HTTP 422를 반환합니다.

### 지표 해석

- `total_lines`는 Python `splitlines()` 기준입니다. `comment_lines`는 주석만 있는 줄을 셉니다. 인라인 주석 줄은 코드 줄로 셉니다.
- `imports`는 import **문**의 개수이고, `import_modules`는 import한 최상위 모듈의 중복 없는 목록입니다.
- `functions`에는 메서드와 중첩 함수도 포함됩니다. 타입 힌트 비율은 전체 함수 중 매개변수 하나 이상에 타입 힌트가 있는 함수, 또는 반환 타입 힌트가 있는 함수의 비율입니다.
- 함수 길이는 AST의 시작 줄부터 끝 줄까지 포함합니다. 최대 중첩 깊이는 `if`, `for`, `while`, `try`, `with`, `match` 계열 노드를 셉니다.
- 수치 차이는 품질 점수가 아니며, 요약 문장은 정해진 규칙으로만 생성됩니다.

## 테스트 및 빌드

```bash
cd backend
uv run pytest -q
uv run ruff check app tests
```

```bash
cd frontend
npm run build
```

사용자 코드는 `eval`, `exec`, Python subprocess로 실행되지 않습니다. Ruff 실행용 임시 파일은 분석 후 삭제됩니다.

## V0.2 계획

Ollama 연결, 정적 분석 데이터 기반의 로컬 LLM 해설, 구현 방식과 trade-off 설명, 학습용 개념 추천, 쉬운 설명 기능을 검토할 예정입니다. V0.1에는 포함되지 않습니다.
