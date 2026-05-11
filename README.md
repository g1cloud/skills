# g1cloud skills

## Install

```sh
npx skills add g1cloud/skills --skill api-gen

npx skills add g1cloud/skills --skill semantic-commit

npx skills add g1cloud/skills --skill bluework-openapi
```

## Skills

### api-gen

Spring MVC RestController를 분석하여 OpenAPI 스펙과 HTML 문서를 자동 생성합니다.

**트리거 키워드:** `api doc`, `api 문서`, `문서 생성`, `generate api doc`

**필수 환경 변수:**

| 변수 | 설명 | 기본값 |
|---|---|---|
| `API_GEN_SOURCE_DIR` | 소스 루트 디렉토리 | `./` |
| `API_GEN_API_SOURCE_DIR` | RestController가 포함된 소스 디렉토리 | `./` |
| `API_GEN_FILE` | 출력 YAML 파일 경로 | `./doc/api/api.yaml` |
| `API_GEN_TITLE` | API 문서 제목 | 프로젝트명 |
| `API_GEN_VERSION` | API 문서 버전 | 프로젝트 버전 |

환경 변수는 프로젝트 루트의 `.claude/settings.json`에 설정합니다.

```json
{
  "env": {
    "API_GEN_SOURCE_DIR": "./",
    "API_GEN_API_SOURCE_DIR": "./src/main/java",
    "API_GEN_FILE": "./doc/api/api.yaml",
    "API_GEN_TITLE": "My API",
    "API_GEN_VERSION": "1.0.0"
  }
}
```

### semantic-commit

Conventional Commits v1.0.0 스펙에 따라 git 커밋 메시지를 생성합니다.

**트리거 키워드:** `commit`, `semantic commit`, `conventional commit`, `/semantic-commit`

### bluework-openapi

Bluework Tool 의 OpenAPI(`/openapi/{projectId}/...`)를 `curl` 로 호출합니다. UI 화면 목록, 다국어 Message, 시스템 공통 코드(SystemCode), 비즈니스 모듈/엔터티/속성, EntityModel 텍스트, UiModel 트리 등을 조회/변경합니다. 응답은 토큰 효율이 좋은 `text/toon` 포맷을 기본으로 사용합니다.

**트리거 키워드:** `bluework`, `bluework4`, `openapi.yaml`, `엔터티 추가`, `메시지 properties`, `GroupCode`, `EntityModel`, `UiModel`, `PartModel`

**필수 환경 변수:**

| 변수 | 설명 | 예시 |
|---|---|---|
| `BLUEWORK_API_HOST` | API 서버 prefix (스킴 포함, 끝에 `/` 없음) | `http://localhost:3000` |
| `BLUEWORK_API_KEY` | API Key (Bearer 토큰) | `bw_xxx...` |

쉘에 export 하거나 프로젝트 루트의 `.claude/settings.json` 에 설정합니다.

```json
{
  "env": {
    "BLUEWORK_API_HOST": "http://localhost:3000",
    "BLUEWORK_API_KEY": "bw_xxx..."
  }
}
```

> Nuxt `baseURL: '/tool/'` 가 적용된 환경에서는 `/openapi/...` 호출이 302 redirect 됩니다. 스킬의 모든 curl 예시는 `-L` 옵션을 포함합니다.

## Statusline

### etc/statusline.sh

Claude Code 의 HUD(상태표시줄)에 사용할 수 있는 statusline 스크립트입니다. [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) HUD 디자인에서 영감을 받았습니다.

**표시 항목:**

```
Model | 5h:NN%(Hh Mm) | wk:NN%(Dd Hh) | ctx:NN% | cwd | repo:NAME | branch:BR | +S !M ?U ⇡A ⇣B
```

- **Model**: 사용 중인 모델(Opus/Sonnet/Haiku)과 버전 (티어별 색상)
- **5h / wk**: 5시간 / 주간 rate limit 사용률과 리셋까지 남은 시간 (70%/90% 임계값으로 색상)
- **ctx**: 컨텍스트 윈도우 사용률 (70%/85% 임계값, 85% 이상 시 CRITICAL 표시)
- **cwd**: 현재 작업 디렉토리 (basename)
- **branch**: 현재 git 브랜치 (worktree 인 경우 `(wt:NAME)` 표시)
- **상태 카운트**: `+`staged `!`modified `?`untracked `⇡`ahead `⇣`behind

**요구사항:** `jq`, `bash`, `git`

**적용 방법 (간편):**

Claude Code 에 파일 URL 을 주고 적용해달라고 하면 됩니다.

```
https://raw.githubusercontent.com/g1cloud/skills/refs/heads/main/etc/statusline.sh 를 claude code 의 statusline 으로 적용해줘
```

또는 슬래시 커맨드로:

```
/statusline https://raw.githubusercontent.com/g1cloud/skills/refs/heads/main/etc/statusline.sh 를 적용해줘
```

**적용 방법 (수동):**

1. 스크립트를 다운로드하고 실행 권한을 부여합니다.

   ```sh
   mkdir -p ~/.claude
   curl -fsSL https://raw.githubusercontent.com/g1cloud/skills/refs/heads/main/etc/statusline.sh -o ~/.claude/statusline.sh
   chmod +x ~/.claude/statusline.sh
   ```

2. `~/.claude/settings.json` (또는 프로젝트의 `.claude/settings.json`) 에 statusLine 을 등록합니다.

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.sh",
       "padding": 0
     }
   }
   ```

3. Claude Code 를 재시작하면 하단에 HUD 가 표시됩니다.