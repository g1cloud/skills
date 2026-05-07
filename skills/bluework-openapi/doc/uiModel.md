# UiModel API

화면(UI) 의 모델을 텍스트 또는 PartModel 트리 구조로 조회합니다.
화면 메타 목록은 [UI 문서](./ui.md) 를 참고하세요.

[← README 로 돌아가기](./README.md)

---

## `GET /openapi/{projectId}/uiModel/{id}/text` — UI 모델 텍스트 조회

지정한 화면(UI)의 모델을 사람/LLM 친화적 텍스트로 변환합니다.

### 경로 파라미터

| 이름 | 설명 |
|---|---|
| `id` | UI ID (MongoDB `_id`) |

### 응답: `TextResponse`

```json
{ "text": "UI USR001 (사용자 목록)\n  Container ...\n    Grid ..." }
```

### 사용 예시

```bash
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/uiModel/65b.../text"
```

---

## `GET /openapi/{projectId}/uiModel/{id}/partModel` — PartModel 트리 조회

화면의 PartModel 트리 구조를 화면 정보(`uiInfo`) 와 함께 반환합니다.
텍스트 변환 없이 원시 트리 구조가 필요할 때 사용합니다.

### 경로 파라미터

| 이름 | 설명 |
|---|---|
| `id` | UI ID — MongoDB `_id` 또는 `uiId` 모두 허용 |

### 응답: `OpenApiUiModelPartModelResponse`

```json
{
  "uiInfo": {
    "uiId": "USR001",
    "name": "사용자 목록",
    "menu1": { "id": "MENU_USER",  "name": "사용자관리" },
    "menu2": { "id": "MENU_USERS", "name": "사용자" }
  },
  "partModel": {
    "partId": "root",
    "partType": "Container",
    "partInfo": { /* ... */ },
    "attrMap": {
      "title": { "type": "S", "val": "사용자 목록" }
    },
    "comment": { "ko": "메인 컨테이너" },
    "caseMsgList": [
      { "msgText": "저장되었습니다." }
    ],
    "children": [
      {
        "partId": "grid01",
        "partType": "BSGrid",
        "attrMap": {
          "rowCount": { "type": "I", "val": "100" },
          "useFilter": { "type": "B", "val": "true" }
        },
        "children": []
      }
    ],
    "layoutAttrMap": { /* 레이아웃 속성 (선택) */ },
    "extraAttrMap": { /* 추가 속성 (선택) */ }
  }
}
```

### `attrMap` / `layoutAttrMap` 의 값 타입

| `type` | 의미 |
|---|---|
| `S` | 문자열 |
| `I` | 정수 |
| `B` | 불리언 |
| `M` | 메시지 |
| `DS` | DataSource |
| `DM` | DataMapping |
| `*_REF` | 참조 인덱스 (변환 후에는 노출되지 않음) |
| `ETC` | 기타 |

### 사용 예시

```bash
# MongoDB _id 로 조회
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/uiModel/65b.../partModel"

# uiId 로 조회
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/uiModel/USR001/partModel"
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 해당 UI 모델 없음 |
