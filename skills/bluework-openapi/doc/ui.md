# UI 화면 API

화면(UI) 메타 목록을 조회합니다. UI 모델 트리/텍스트 조회는 [UiModel 문서](./uiModel.md) 를 참고하세요.

[← README 로 돌아가기](./README.md)

---

## `GET /openapi/{projectId}/ui` — 화면 목록 조회

프로젝트의 화면 목록을 조회합니다. `use: true` 인 화면만 반환됩니다.

### 쿼리 파라미터

| 이름 | 타입 | 설명 |
|---|---|---|
| `uiId` | string | `uiId` LIKE 검색 (대소문자 무시) |
| `uiName` | string | 화면명(`name.ko`) LIKE 검색 (대소문자 무시) |
| `uiType` | string | `uiType` LIKE 검색 (대소문자 무시) |
| `menu1` | string | 1차 메뉴명 LIKE 검색 (페이지네이션 후 필터링) |
| `menu2` | string | 2차 메뉴명 LIKE 검색 (페이지네이션 후 필터링) |
| `offset`, `limit`, `sort`, `format` | — | [공통 파라미터](./README.md#공통-파라미터) 참고 |

> ⚠️ `menu1`, `menu2` 는 DB 쿼리 단계가 아니라 **페이지네이션이 적용된 결과 내**에서 필터링됩니다.
> 메뉴 기준 정확 검색이 필요하면 `limit` 을 충분히 크게 두거나 다른 필터(`uiId` 등) 와 조합하세요.

### 응답: `OpenApiUiListResponse`

```json
{
  "items": [
    {
      "uiId": "USR001",
      "uiName": "사용자 목록",
      "uiType": "LIST",
      "menu1": "사용자관리",
      "menu2": "사용자",
      "updateId": "kimos",
      "updateDate": "2026-05-01T03:12:45.000Z"
    }
  ],
  "totalCount": 42,
  "offset": 0,
  "limit": 100
}
```

### 사용 예시

#### 1) uiId 부분 일치 + 정렬

```bash
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/ui?uiId=USR&sort=-updateDate&limit=20"
```

#### 2) 1차 메뉴 필터 (페이지 내)

```bash
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/ui?menu1=사용자관리&limit=500"
```

#### 3) TOON 포맷으로 LLM 입력 만들기

```bash
curl -H "Authorization: Bearer $API_KEY" \
  -H "Accept: text/toon" \
  "http://localhost:3000/openapi/myproject/ui?uiType=LIST&limit=50"
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | `offset`/`limit` 형식 오류, `sort` 파싱 실패 |
| `401` | API Key 누락/무효 |
