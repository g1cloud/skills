# Message API

다국어 메시지(`Message` 컬렉션) 의 조회/추가/수정/삭제 및 Java `properties` 변환을 제공합니다.

[← README 로 돌아가기](./README.md)

---

## 공통 사항

- `msg` 는 언어 코드(`ko`, `en`, `ja`, `zh`, `fr`, `th` 등) 를 키로 한 다국어 맵입니다.
- 빈 문자열 값은 저장 시 자동 제거되어 GET 응답과 일관됩니다.
- 목록 응답은 `msg.<locale>` 을 `msg_<locale>` 로 평탄화하여 반환합니다 (TOON 테이블 압축 가능).
- 응답 페이지에 등장한 모든 locale 키는 모든 item 에 동일하게 포함되며, 값이 없으면 `null` 입니다.

---

## `GET /openapi/{projectId}/message` — 메시지 원본 목록 조회

`Message` 컬렉션 데이터를 그대로(`locale` 변환 없이) 반환합니다.

### 쿼리 파라미터

| 이름 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `owner` | `BackendApp` \| `FrontendApp` | — | 소유 애플리케이션 종류 |
| `appId` | string | — | FrontendApp 의 `appId` 필터 |
| `use` | `'true'` \| `'false'` | `'true'` | 사용 여부 |
| `export` | `'true'` \| `'false'` | `'true'` | export 여부 |
| `prefix` | string | — | `msgKey` prefix 필터 (예: `ecp.`) |
| `offset`, `limit`, `format` | — | — | 공통 |

### 응답: `OpenApiMessageListResponse`

```json
{
  "items": [
    {
      "msgKey": "ecp.user.greeting",
      "owner": "FrontendApp",
      "appId": "ecp",
      "use": true,
      "export": true,
      "updateId": "openapi",
      "updateDate": "2026-05-01T01:00:00.000Z",
      "msg_ko": "안녕하세요",
      "msg_en": "Hello",
      "msg_ja": null
    }
  ],
  "totalCount": 1,
  "offset": 0,
  "limit": 100
}
```

### 사용 예시

```bash
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/message?prefix=ecp.user.&limit=50"
```

---

## `POST /openapi/{projectId}/message` — 메시지 추가

새 메시지를 추가합니다.

### 요청 본문: `OpenApiMessageCreateRequest`

| 필드 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `msgKey` | ✅ | — | 메시지 키 |
| `msg` | ✅ | — | 언어별 메시지 맵 |
| `owner` | | `null` | `BackendApp` \| `FrontendApp` |
| `appId` | | `null` | FrontendApp `appId` |
| `use` | | `true` | |
| `export` | | `true` | |
| `updateId` | | `'openapi'` | 감사 필드 |

### 응답: `OpenApiWriteAck`

```json
{ "ok": true, "msgKey": "ecp.user.greeting" }
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | `msgKey`/`msg` 누락 |
| `409` | 동일 `msgKey` 가 이미 존재 |

### 사용 예시

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/message" \
  -d '{
    "msgKey": "ecp.user.greeting",
    "msg": { "ko": "안녕하세요", "en": "Hello" },
    "owner": "FrontendApp",
    "appId": "ecp"
  }'
```

---

## `PUT /openapi/{projectId}/message/{msgKey}` — 메시지 수정

지정한 `msgKey` 의 `msg` (언어별 메시지 맵) 을 갱신합니다.

### 요청 본문: `OpenApiMessageUpdateRequest`

| 필드 | 필수 | 설명 |
|---|---|---|
| `msg` | ✅ | 새로운 언어별 메시지 맵 |
| `updateId` | | 감사 필드. 미지정 시 `'openapi'` |

### 사용 예시

```bash
curl -X PUT -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/message/ecp.user.greeting" \
  -d '{ "msg": { "ko": "안녕!", "en": "Hi!" } }'
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 매칭되는 `msgKey` 없음 |

---

## `DELETE /openapi/{projectId}/message/{msgKey}` — 메시지 삭제

지정한 `msgKey` 의 메시지를 삭제합니다.

### 사용 예시

```bash
curl -X DELETE -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/message/ecp.user.greeting"
```

응답:

```json
{ "ok": true, "msgKey": "ecp.user.greeting" }
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 매칭되는 `msgKey` 없음 |

---

## `GET /openapi/{projectId}/message/properties` — 메시지 properties 조회

메시지를 Java `properties` 파일 형식 텍스트로 변환하여 반환합니다.

### 쿼리 파라미터

| 이름 | 필수 | 설명 |
|---|---|---|
| `locale` | ✅ | 단일(`ko`) 또는 쉼표 구분 복수(`ko,en,ja`) |
| `owner`, `appId`, `use`, `export`, `prefix` | | 목록 API 와 동일 |

지원 로케일: `ko`, `en`, `ja`, `zh`, `fr`

### 응답

#### locale 단일 → `SingleLocaleResponse`

```json
{
  "text": "ecp.user.greeting=안녕하세요\necp.user.bye=안녕히 가세요\n",
  "filename": "messages_ko.properties",
  "totalCount": 2
}
```

#### locale 복수 → `MultiLocaleResponse`

```json
{
  "files": {
    "ko": { "text": "ecp.user.greeting=안녕하세요\n", "count": 1 },
    "en": { "text": "ecp.user.greeting=Hello\n", "count": 1 }
  },
  "totalCount": 1
}
```

### 사용 예시

```bash
# 단일 로케일
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/message/properties?locale=ko&prefix=ecp."

# 복수 로케일
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/message/properties?locale=ko,en,ja"
```
