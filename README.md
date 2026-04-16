# g1cloud skills

## Install

```sh
npx skills add g1cloud/skills --skill api-gen

npx skills add g1cloud/skills --skill semantic-commit
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