---
name: bluework-openapi
description: |
  Bluework Tool 의 OpenAPI 를 curl 로 호출할 때 사용합니다. UI 화면 목록, 다국어
  Message, 시스템 공통 코드(SystemCode), 비즈니스 모듈/엔터티/속성, EntityModel
  텍스트, UiModel 트리 등 `/openapi/{projectId}/...` 하위 모든 엔드포인트를 다룹니다.
  Bluework, bluework4, openapi.yaml, doc/api 가 언급되거나, 사용자가 "쿠폰 엔터티
  추가", "메시지 properties 뽑기", "GroupCode 코드 추가", "엔터티 모델 텍스트로
  보여줘", "PartModel 트리 가져와" 같이 위 도메인의 데이터를 조회/변경하려고 할
  때 항상 이 스킬을 사용합니다. 응답은 가능하면 LLM 토큰 효율이 좋은 `text/toon`
  포맷을 사용하고, host 와 API Key 는 환경변수에서 읽어 안전하게 호출합니다.
---

# Bluework OpenAPI (curl) Skill

Bluework Tool 의 외부 OpenAPI 를 `curl` 로 안정적이고 토큰 효율적으로 호출하기 위한 스킬입니다.

## 환경 변수 (필수)

이 스킬은 호스트와 API Key 를 명령줄에 노출하지 않고 환경변수에서 읽습니다.
먼저 두 변수가 셸에 설정되어 있는지 반드시 확인하세요.

| 변수 | 역할 | 예시 |
|---|---|---|
| `BLUEWORK_API_HOST` | API 서버 prefix (스킴 포함, 끝에 `/` 없음) | `http://localhost:3000` |
| `BLUEWORK_API_KEY` | API Key (Bearer 토큰) | `bw_xxx...` |

### Nuxt baseURL 안내 (중요)

이 프로젝트는 Nuxt `baseURL: '/tool/'` 가 적용되어 있어 실제 라우트는 `/tool/openapi/...` 에 마운트됩니다. `BLUEWORK_API_HOST` 를 `http://localhost:3000` 으로 설정하고 `/openapi/...` 경로로 호출하면 서버가 **302 redirect** 를 보냅니다.

→ **이 스킬의 모든 curl 예시는 `-L` (follow redirects) 을 포함**합니다. 사용자가 host 를 어떻게 설정했는지 신경 쓰지 않고 안전하게 동작합니다. `-L` 을 빼면 302 만 받고 끝나므로 절대 빼지 마세요.

(원한다면 호스트를 처음부터 `http://localhost:3000/tool` 로 설정해도 됩니다 — 그래도 `-L` 을 유지하세요.)

### 확인 절차 (호출 전 매번)

```bash
: "${BLUEWORK_API_HOST:?BLUEWORK_API_HOST 가 설정되지 않았습니다. export BLUEWORK_API_HOST=...}"
: "${BLUEWORK_API_KEY:?BLUEWORK_API_KEY 가 설정되지 않았습니다. export BLUEWORK_API_KEY=...}"
```

위 가드 라인을 모든 curl 호출 전에 한 번 실행하세요. 누락되어 있으면 즉시 멈추고 사용자에게 어떤 변수를 설정해야 하는지 알려야 합니다. **API Key 자체를 출력하거나 로그/문서에 남기지 마세요.**

### 401 / "유효하지 않은 API Key" 가 났을 때 (행동 강령)

- **즉시 멈추고 사용자에게 보고**합니다. 어떤 변수가 비어있는지 / 어떤 호스트로 호출했는지를 알려주고 사용자가 해결할 때까지 기다립니다.
- API Key 를 **추측하거나 다른 곳에서 찾으려 시도하지 마세요.** 소스 코드, `.env`, MongoDB, 설정 파일을 뒤지는 것은 이 스킬의 범위 밖이고 보안 정책 위반입니다.
- 사용자가 "테스트 환경이라 placeholder 키를 쓰고 있다" 고 명시한 경우에는 401 자체가 정상 결과입니다. **호출 형태 검증으로 종료**하고 더 진행하지 마세요.

## 응답 포맷: 기본 TOON

이 OpenAPI 는 `application/json` 과 `text/toon` 두 포맷을 지원합니다. **가능하면 항상 `text/toon` 을 사용**하세요. 동일한 데이터 모델을 표 형태로 압축해 LLM 토큰을 크게 절약합니다.

포맷 선택 우선순위는 `?format=...` > `Accept` 헤더 > 기본 `json` 입니다. 이 스킬은 충돌을 피하기 위해 **쿼리 파라미터 `format=toon` 을 명시**합니다.

### TOON 응답을 사용하지 말아야 하는 경우

다음 상황에서는 `format=json` 으로 폴백하세요. 그 외에는 TOON 을 유지합니다.

- **응답 그대로 다른 도구/스크립트에 파이프로 넣어야 할 때** (예: `jq`, 후속 자동화)
- **`{...}` 키-값 구조가 깊거나 동적 키가 많은 응답을 정확히 보존**해야 할 때
  (예: `GET /uiModel/{id}/partModel` 의 PartModel 트리, `GET /entityModel/{id}/entities/{names}` 의 원본 객체)
- **단일 텍스트 필드 응답** (예: `*/text` 엔드포인트의 `TextResponse`) 은 TOON 에서도 거의 동일한 크기이므로 어느 쪽이든 무방합니다. 기본은 TOON 유지.

## 표준 호출 패턴

### GET (목록/조회)

```bash
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  -H "Accept: text/toon" \
  "$BLUEWORK_API_HOST/openapi/<projectId>/<path>?format=toon&<query>"
```

### POST/PUT/DELETE (쓰기)

쓰기 응답은 작고 구조가 단순한 ack 객체이므로 TOON 의 압축 효과가 거의 없습니다. **쓰기에는 일반 JSON 응답**을 사용하면 후속 처리(`jq` 등)가 쉽고 가독성도 좋습니다.

```bash
curl -sS -L -X POST \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  "$BLUEWORK_API_HOST/openapi/<projectId>/<path>" \
  -d '<json-body>'
```

### 상태 코드 확인

응답 본문과 함께 HTTP 상태도 보고 싶다면 `-w` 를 추가합니다. 호출이 실패하는지 진단할 때 유용합니다.

```bash
curl -sS -L -w '\nHTTP %{http_code}\n' \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/<projectId>/<path>?format=toon"
```

## 엔드포인트 빠른 참조

상세 파라미터/응답 스키마는 [`doc/`](./doc/) 의 그룹별 문서를 우선 참고하고, 모호하면 [`doc/openapi.yaml`](./doc/openapi.yaml) 원본을 직접 읽으세요. 아래 표는 자주 쓰는 호출만 모아둔 치트시트입니다.

| 동작 | 메서드 + 경로 | 그룹 문서 |
|---|---|---|
| 화면 목록 | `GET /ui` | [ui.md](./doc/ui.md) |
| 메시지 목록 | `GET /message` | [message.md](./doc/message.md) |
| 메시지 추가 | `POST /message` | message.md |
| 메시지 수정/삭제 | `PUT/DELETE /message/{msgKey}` | message.md |
| Properties 변환 | `GET /message/properties?locale=ko[,en,...]` | message.md |
| GroupCode 목록 | `GET /systemCode` | [systemCode.md](./doc/systemCode.md) |
| GroupCode 추가/수정 | `POST /systemCode`, `PUT /systemCode/{groupCode}` | systemCode.md |
| Code 추가/수정/삭제 | `POST/PUT/DELETE /systemCode/{groupCode}/code[/{code}]` | systemCode.md |
| 비즈니스 모듈 목록 | `GET /bizModule` | [bizModule.md](./doc/bizModule.md) |
| 모듈의 엔터티 목록 | `GET /bizModule/{id}/entities` | bizModule.md |
| 엔터티 추가 | `POST /bizModule/{id}/entities` | bizModule.md |
| 속성 추가 | `POST /bizModule/{id}/entities/{entityName}/attributes` | bizModule.md |
| 속성 삭제 | `DELETE .../attributes/{attributeName}` | bizModule.md |
| 엔터티 모델 텍스트 | `GET /entityModel/{id}/text` | [entityModel.md](./doc/entityModel.md) |
| 엔터티 원본 다중 조회 | `GET /entityModel/{id}/entities/{names}` | entityModel.md |
| UI 모델 텍스트 | `GET /uiModel/{id}/text` | [uiModel.md](./doc/uiModel.md) |
| UI 모델 PartModel | `GET /uiModel/{id}/partModel` | uiModel.md |

`{projectId}` 는 프로젝트(MongoDB DB) 이름, `{id}` 는 비즈니스 모듈/UI 의 MongoDB `_id` 입니다.

## 자주 쓰는 호출 예시

### 1) UI 화면 목록을 LLM 분석용으로 가져오기 (TOON)

```bash
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/ui?uiType=LIST&limit=50&format=toon"
```

### 2) 특정 prefix 메시지를 한국어 properties 로 변환

```bash
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/message/properties?locale=ko&prefix=ecp.&format=toon"
```

### 3) 메시지 한 건 추가 (쓰기 → JSON)

```bash
curl -sS -L -X POST \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  -H "Content-Type: application/json" \
  "$BLUEWORK_API_HOST/openapi/myproject/message" \
  -d '{
    "msgKey": "ecp.user.greeting",
    "msg": { "ko": "안녕하세요", "en": "Hello" },
    "owner": "FrontendApp",
    "appId": "ecp"
  }'
```

### 4) 비즈니스 모듈에 새 엔터티 추가

> ⚠️ **엔터티/속성 쓰기는 `name` 과 `physicalName` 이 모두 필수**입니다.
> 사용자가 `physicalName` 을 명시하지 않았다면 절대 멋대로 생략하지 말고 사용자에게 DB 컬럼명을 물어보세요. 컨벤션상 `physicalName` 은 `lower_snake_case` 입니다 (예: `amountType` → `amount_type`).

```bash
curl -sS -L -X POST \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  -H "Content-Type: application/json" \
  "$BLUEWORK_API_HOST/openapi/myproject/bizModule/$BIZ_MODULE_ID/entities" \
  -d '{
    "name": "Coupon",
    "dbAttrs": { "physicalName": "mkt_coupon", "logicalName": { "ko": "쿠폰" } },
    "groupName": "marketing",
    "columns": [
      { "name": "couponId", "physicalName": "coupon_id",
        "type": "String", "dataType": "VARCHAR", "length": 32,
        "identifier": true, "notNull": true, "attributeGroup": "id" }
    ]
  }'
```

### 5) 엔터티 속성 추가/삭제

```bash
# 추가
curl -sS -L -X POST \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  -H "Content-Type: application/json" \
  "$BLUEWORK_API_HOST/openapi/myproject/bizModule/$BIZ_MODULE_ID/entities/Coupon/attributes" \
  -d '{ "name": "expireDate", "physicalName": "expire_dt",
        "type": "LocalDateTime", "dataType": "DATETIME",
        "attributeGroup": "datetime" }'

# 삭제
curl -sS -L -X DELETE \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/bizModule/$BIZ_MODULE_ID/entities/Coupon/attributes/expireDate"
```

### 6) 엔터티 모델 텍스트로 LLM 컨텍스트 만들기

```bash
# 모듈 전체
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/entityModel/$BIZ_MODULE_ID/text?format=toon"

# 특정 엔터티만 (이름/테이블명 혼용 가능)
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/entityModel/$BIZ_MODULE_ID/text?entity=SalesOrder&entity=Checkout&format=toon"
```

### 7) UI 의 PartModel 트리 (깊은 객체 → JSON 권장)

```bash
curl -sS -L \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/uiModel/USR001/partModel?format=json"
```

## 에러 진단 가이드

응답이 4xx 인 경우 본문은 `{ "statusCode": ..., "message": "..." }` 형태입니다. JSON 으로 받으면 `jq` 로 바로 메시지를 확인할 수 있어 디버깅이 빠릅니다.

```bash
curl -sS -w '\nHTTP %{http_code}\n' \
  -H "Authorization: Bearer $BLUEWORK_API_KEY" \
  "$BLUEWORK_API_HOST/openapi/myproject/bizModule/badId/entities" \
  | jq .
```

| 상태 | 의미 | 자주 보이는 원인 |
|---|---|---|
| 400 | Bad Request | 필수 필드 누락, `offset/limit` 형식 오류 |
| 401 | Unauthorized | `BLUEWORK_API_KEY` 누락/오타/만료 |
| 404 | Not Found | `projectId`, `id`, `entityName`, `groupCode`, `code` 등 잘못 지정 |
| 409 | Conflict | 중복 키(이미 존재하는 `msgKey`/`groupCode`/`code`/엔터티 이름·물리명/속성 이름·물리명), 또는 인덱스가 참조 중인 속성 삭제 시도 |

특히 **속성 삭제 시 409** 가 발생하면 응답 메시지에 차단 원인 인덱스 이름이 포함됩니다. 그 인덱스를 먼저 정리한 뒤 재시도해야 합니다.

## 운영 팁

- **여러 호출이 같은 `projectId`/`id` 를 쓰면** 셸 변수로 잡아두세요.
  ```bash
  PROJECT=myproject
  BIZ_MODULE_ID=65a0...
  ```
- **TOON 응답을 사용자에게 그대로 보여주면 됩니다.** 굳이 JSON 으로 재변환하지 마세요. JSON 변환이 필요한 경우(예: 후속 자동화)에만 `format=json` 으로 다시 호출합니다.
- **PUT/`PATCH 의도`** 의 부분 갱신 동작이 엔드포인트마다 다릅니다 (예: `PUT /systemCode/{groupCode}` 는 `groupCodeNameMap` 만 전체 교체). 수정 전에 해당 그룹 문서의 요청 본문 표를 한 번 더 확인하세요.
- **HTTP 메서드 캐시 주의:** GET 응답을 셸에서 `>file` 로 저장해 재사용해도 무방하지만, 서버 측 데이터가 바뀌었을 가능성이 있으면 다시 호출하세요.

## 처음 호출하기 전 체크리스트

1. `BLUEWORK_API_HOST` 와 `BLUEWORK_API_KEY` 가 셸에 export 되었는가?
2. `projectId` 를 알고 있는가? (모르면 사용자에게 묻기)
3. 모든 curl 에 `-L` 이 포함되어 있는가? (Nuxt baseURL `/tool` 리다이렉트 처리)
4. 쓰기 작업이라면 사용자가 의도/대상을 명시했는가? (특히 `DELETE`)
5. 엔터티/속성 추가라면 `name` + `physicalName` 둘 다 사용자가 명시했는가? 누락된 필수 필드는 추측하지 말고 묻기.
6. 응답을 사람이 보는 용도면 `format=toon`, 후속 자동화에 넣어야 하면 `format=json`.
7. 401 또는 인증 실패가 나면 추가 호출하지 말고 사용자에게 보고하기.
