# Code Contrast

같은 요구사항으로 작성된 두 Python 코드의 **구조와 정적 분석 결과**를 나란히 비교하고, 선택적으로 로컬 AI 튜터에게 차이를 설명받는 학습용 웹 앱입니다. 코드를 실행하거나 모델의 승패를 평가하지 않습니다. 사용자가 원래 프롬프트와 두 코드를 직접 붙여넣습니다.

## V0.1 기능

- Monaco Editor에서 CODE A와 CODE B 입력, 각 코드의 모델 이름 선택 또는 직접 입력
- Python AST로 줄 수, 함수와 클래스, import, 데코레이터, 예외 처리, async/await, 타입 힌트, 문서 문자열, 함수 길이, 최대 중첩 깊이 계산
- Ruff 정적 검사 결과를 코드별로 표시
- 수치 비교, 규칙 기반 구조 차이 문장, 공통/전용 import 표시
- 문법 오류가 있는 코드를 별도로 표시하고 다른 코드의 분석은 유지
- 선택적으로 Monaco Diff View 열기

두 코드 모두 Python 코드여야 합니다. 모델 이름은 표시용 라벨이며 분석 결과에 영향을 주지 않습니다. V0.1 정적 비교는 Ollama 없이 작동합니다.

## V0.2 기능

- 로컬 Ollama 연결 및 설치된 모델 상태 확인
- 실제 코드와 V0.1 정적 분석 결과를 바탕으로 구조 차이와 trade-off 해설
- 최대 3개의 관련 학습 개념 추천, 각 개념의 `쉽게 설명해줘` 기능
- JSON Schema 기반 Ollama 응답과 Pydantic 검증, 연결 실패·모델 없음·시간 초과·잘못된 응답 처리
- AI 기능은 선택 사항이며, Ollama가 꺼져 있어도 정적 비교는 유지

GPT, Claude, Gemini 등 외부 유료 LLM API는 사용하지 않습니다. AI 해설은 확률적인 모델 출력이므로 코드 및 정적 분석 지표와 함께 확인하세요.

## 기술 스택과 구조

- Frontend: React, TypeScript, Vite, Monaco Editor, 일반 CSS
- Backend: Python 3.12 이상, FastAPI, Pydantic, Python `ast`, Ruff, httpx, uv
- AI: 로컬 Ollama (선택 사항)

Monaco 파일은 프런트엔드 번들에 포함되므로 편집기를 위해 외부 CDN에 접속하지 않습니다.

```text
gpt_vs_claude/
├─ backend/
│  ├─ app/
│  │  ├─ analyzers/       # AST, 줄 수, Ruff
│  │  ├─ ai/              # Ollama 호출, 프롬프트, 응답 검증
│  │  ├─ routers/         # compare, AI tutor API
│  │  ├─ schemas/         # 요청/응답 모델
│  │  ├─ services/        # 비교, 요약, AI 해설
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

PowerShell에서 `npm.ps1` 실행이 차단되면 실행 정책을 변경할 필요 없이 `npm.cmd install`, `npm.cmd run dev`, `npm.cmd run build`를 사용하세요. Node.js가 PATH에 있어야 합니다. 개발 서버가 다른 포트를 표시하면 터미널의 `Local:` 주소를 여세요.

### Ollama 설정 (AI Tutor 사용 시)

1. [Ollama](https://ollama.com/)를 설치하고 서버를 실행합니다. Ollama 앱이 서버를 이미 시작했다면 별도의 `ollama serve` 명령은 필요하지 않습니다.
2. `ollama list`로 설치된 모델 이름을 확인합니다. CLI가 PATH에 없다면 PowerShell에서 `(Invoke-RestMethod http://localhost:11434/api/tags).models.name`으로 확인할 수 있습니다. 모델이 없다면 원하는 로컬 모델을 `ollama pull <모델명>`으로 설치합니다. 예시인 `qwen2.5-coder:7b`가 모든 PC에 설치되어 있는 것은 아닙니다.
3. `backend/.env.example`을 `backend/.env`로 복사하고 `OLLAMA_MODEL`을 **내 PC에 설치된 정확한 모델명**으로 바꿉니다. 기본 URL은 `http://localhost:11434`이며 필요하면 `OLLAMA_BASE_URL`을 변경합니다.
4. 백엔드를 재시작하고 `GET /api/ai/status` 또는 화면의 연결 상태를 확인합니다.

Windows PowerShell 예:

```powershell
cd backend
Copy-Item .env.example .env
# .env의 OLLAMA_MODEL=YOUR_INSTALLED_MODEL_NAME을 실제 설치된 모델명으로 수정
ollama list
uv run uvicorn app.main:app --reload
```

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

V0.2 API:

- `GET /api/ai/status`: Ollama 연결 및 설정 모델 설치 여부. `available`, `model`, `message` 반환.
- `POST /api/explain`: `/api/compare`와 같은 `prompt`, `code_a`, `code_b`, `label_a`, `label_b`를 받습니다. 백엔드에서 정적 분석을 다시 사용하고 `summary`, `architecture`, `tradeoffs`, `learning_points`, `recommendation_context`를 반환합니다.
- `POST /api/explain/concept`: `concept`, `prompt`, `code_a`, `code_b`, `context`를 받아 한 줄 설명, 비유, 현재 코드 관련성, 짧은 예제, 사용 시점, 현재 필요성을 반환합니다.

AI 해설은 코드당 최대 12,000자, 원래 프롬프트는 최대 2,000자입니다. 더 긴 코드는 V0.1 정적 비교로 계속 분석할 수 있습니다. AI 오류는 해당 요청에만 표시됩니다. API 명세는 백엔드 실행 후 `http://localhost:8000/docs`에서 볼 수 있습니다.

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

## 향후 확장

V0.3 이후에는 여러 단계의 질문 흐름, 학습 기록, 응답 근거의 자동 검증 등을 검토할 수 있습니다. 현재 버전에는 데이터베이스, 로그인, 코드 실행, 여러 Agent가 없습니다.
