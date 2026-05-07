# Bluework Tool OpenAPI

Bluework Tool 프로젝트의 외부 공개 OpenAPI 사용 가이드입니다.
원본 명세는 [`openapi.yaml`](./openapi.yaml) 을 참고하세요.

## 목차

- [인증](#인증) — API Key 발급/사용 방법
- [응답 포맷](#응답-포맷) — JSON / TOON 선택 방법
- [공통 파라미터](#공통-파라미터) — 페이지네이션, 정렬 등
- [에러 응답](#에러-응답) — 4xx 공통 포맷
- API 그룹별 문서
  - [UI 화면](./ui.md) — 화면 목록 조회
  - [Message](./message.md) — 다국어 메시지 조회/추가/수정/삭제, properties 변환
  - [SystemCode](./systemCode.md) — 시스템 공통 코드(GroupCode/Code) CRUD
  - [BizModule](./bizModule.md) — 비즈니스 모듈, 엔터티, 속성 관리
  - [EntityModel](./entityModel.md) — 엔터티 모델 텍스트/원본 조회
  - [UiModel](./uiModel.md) — UI 모델 텍스트/PartModel 트리 조회

## 베이스 URL

- 로컬 개발 서버: `http://localhost:3000`
- 모든 엔드포인트는 `/openapi/{projectId}/...` 경로 하위에 위치합니다.
- `projectId` 는 MongoDB 데이터베이스 이름과 동일합니다.

## 인증

모든 엔드포인트는 API Key 인증이 필요합니다. 두 가지 방식 중 하나를 선택합니다.

| 방식 | 위치 | 예시 |
|---|---|---|
| Bearer Token | `Authorization` 헤더 | `Authorization: Bearer <api-key>` |
| Query Parameter | URL 쿼리 | `?apiKey=<api-key>` |

> API Key 는 Bluework Tool 의 **설정** 메뉴에서 발급/입력합니다.

### 예시

```bash
# Bearer 헤더 방식 (권장)
curl -H "Authorization: Bearer abc123..." \
  "http://localhost:3000/openapi/myproject/ui?limit=10"

# 쿼리 파라미터 방식 (디버깅 편의용)
curl "http://localhost:3000/openapi/myproject/ui?limit=10&apiKey=abc123..."
```

## 응답 포맷

모든 200 응답은 두 가지 포맷을 지원합니다.

| 포맷 | Content-Type | 설명 |
|---|---|---|
| JSON (기본) | `application/json` | 표준 JSON |
| TOON | `text/toon` | LLM 토큰 효율적 표현 ([스펙](https://github.com/toon-format/spec)) |

포맷 결정 우선순위:

1. `?format=toon` 또는 `?format=json` 쿼리 파라미터
2. `Accept: text/toon` 요청 헤더
3. 기본값 `json`

### TOON 응답 예시

```bash
curl -H "Authorization: Bearer ..." \
  "http://localhost:3000/openapi/myproject/ui?limit=2&format=toon"
```

```
items[2]{uiId,uiName,uiType,menu1,menu2,updateId,updateDate}:
  USR001,사용자 목록,LIST,사용자관리,사용자,kimos,2026-05-01T...
  USR002,사용자 상세,DETAIL,사용자관리,사용자,kimos,2026-05-02T...
totalCount: 2
offset: 0
limit: 2
```

JSON 과 동일한 데이터 모델을 표 형태로 압축한 형식이며, 같은 키 집합을 공유하는 항목들은 헤더 1회 + 데이터 행 N개로 표현됩니다.

## 공통 파라미터

### 경로 파라미터

| 이름 | 위치 | 설명 |
|---|---|---|
| `projectId` | path | 프로젝트 ID (MongoDB 데이터베이스 이름) |

### 페이지네이션 (목록 조회 공통)

| 이름 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `offset` | integer | `0` | 시작 오프셋 (0 이상) |
| `limit` | integer | `100` | 페이지당 개수 (1 이상) |

### 정렬

| 이름 | 타입 | 설명 |
|---|---|---|
| `sort` | string | 쉼표 구분 필드명. `-` 접두어는 내림차순. 예: `updateDate,-uiId` |

### 포맷

| 이름 | 타입 | 설명 |
|---|---|---|
| `format` | `json` \| `toon` | 응답 포맷 강제 지정 |

## 에러 응답

모든 4xx 응답은 동일한 에러 객체 포맷을 사용합니다.

```json
{
  "statusCode": 404,
  "message": "Entity 'NotExist' not found"
}
```

| 상태 코드 | 의미 | 발생 시점 |
|---|---|---|
| `400` | Bad Request | 필수 파라미터 누락, 형식 오류 |
| `401` | Unauthorized | API Key 누락/무효 |
| `404` | Not Found | 대상 리소스 없음 |
| `409` | Conflict | 중복 키로 추가/수정 불가 |

## 쓰기 작업 공통 사항

추가/수정/삭제 엔드포인트는 다음 규칙을 공유합니다.

- `updateId` 미지정 시 `'openapi'` 가 감사 필드(`updateId`)로 기록됩니다.
- `updateDate` 는 서버에서 BSON `Date` 로 자동 갱신됩니다.
- 응답은 `OpenApiWriteAck` 형태(`{ ok: true, ... }`) 또는 엔드포인트별 확장 응답을 반환합니다.
