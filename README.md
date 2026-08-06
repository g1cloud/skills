# g1cloud skills

## Install

저장소를 받아서 원하는 스킬 디렉토리를 `.claude/skills/` 로 복사합니다.

```sh
# 1. 저장소를 임시 디렉토리에 클론
git clone --depth 1 https://github.com/g1cloud/skills.git /tmp/g1cloud-skills

# 2. 원하는 스킬을 복사
#    - 전역 설치: ~/.claude/skills/
#    - 프로젝트 설치: <프로젝트 루트>/.claude/skills/
mkdir -p ~/.claude/skills
cp -r /tmp/g1cloud-skills/skills/api-gen ~/.claude/skills/

# 3. 임시 디렉토리 정리
rm -rf /tmp/g1cloud-skills
```

설치 가능한 스킬: `api-gen`, `semantic-commit`, `bluework-openapi`, `blue-reno-release`

이미 설치한 스킬을 업데이트할 때도 같은 방식으로 덮어쓰면 됩니다. 복사 후 Claude Code 를 재시작하면 스킬이 로드됩니다.

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

### blue-reno-release

Blue Reno 릴리즈 노트 플랫폼의 Open API(`/api/v1`)로 릴리즈 노트를 등록·수정·게시합니다. 같은 버전의 노트가 있으면 수정하고 없으면 생성한 뒤 `published` 로 전환합니다. 본문을 직접 주지 않으면 직전 태그 이후의 git 로그에서 초안을 만들어 확인을 받은 뒤 올립니다.

**트리거 키워드:** `릴리즈 노트`, `release note`, `bluereno`, `blue reno`, `릴리즈 노트 게시`, `퍼블리시`

**요구사항:** `python3`

**환경 변수:**

| 변수 | 설명 | 필수 | 기본값 |
|---|---|---|---|
| `BLUERENO_API_KEY` | API 키 (`brn_...`) | ✅ | — |
| `BLUERENO_URL` | 서버 오리진 | — | `https://bluereno.g1project.net` |
| `BLUERENO_ARTIFACT_ID` | 게시 대상 Artifact id | — | — |

API 키는 커밋되지 않는 `.claude/settings.local.json` 에 넣습니다.

```json
{
  "env": {
    "BLUERENO_API_KEY": "brn_xxx..."
  }
}
```

나머지는 프로젝트 루트의 `.claude/settings.json` 에 설정합니다.

```json
{
  "env": {
    "BLUERENO_URL": "https://bluereno.g1project.net",
    "BLUERENO_ARTIFACT_ID": "6"
  }
}
```

API 키는 Blue Reno 로그인 후 좌측 하단 프로필 메뉴 → "API 키" 에서 발급하며, 평문은 발급 직후 한 번만 보입니다. 설정 후 Claude Code 를 재시작해야 `env` 가 주입됩니다. 키 소유자가 대상 Artifact 에 **Editor 이상** 권한이어야 합니다.

Artifact id 를 모를 때는 접근 가능한 목록을 조회할 수 있습니다.

```sh
python3 .claude/skills/blue-reno-release/scripts/blue_reno_publish.py --list-artifacts
```

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