# SystemCode API

시스템 공통 코드(`GroupCode` + 하위 `Code`) 를 조회/추가/수정/삭제합니다.

[← README 로 돌아가기](./README.md)

---

## 데이터 모델 개요

```
GroupCode (groupCode = 식별자)
  ├─ groupCodeNameMap : { ko, en, ... }
  ├─ groupCodeDescMap : { ko, en, ... }
  └─ codeList : [
       { code, color, codeNameMap, codeDescMap }, ...
     ]
```

- 다국어 맵의 빈 값(`""` / `null`) 키는 응답에서 생략됩니다.
- 목록 응답에서 `codeNameMap`/`codeDescMap` 은 `codeName_<locale>`/`codeDesc_<locale>` 로 평탄화됩니다.

---

## `GET /openapi/{projectId}/systemCode` — GroupCode 목록 조회

### 쿼리 파라미터

| 이름 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `groupCode` | string | — | `groupCode` 정확 일치 (예: `PointSavingType`) |
| `use` | `'true'` \| `'false'` | `'true'` | |
| `export` | `'true'` \| `'false'` | `'true'` | |
| `offset`, `limit`, `format` | — | — | 공통 |

### 응답: `OpenApiSystemCodeListResponse`

```json
{
  "items": [
    {
      "groupCode": "PointSavingType",
      "use": true,
      "export": true,
      "updateId": "openapi",
      "updateDate": "2026-05-01T03:12:45.000Z",
      "groupCodeNameMap": { "ko": "포인트 적립 유형", "en": "Point Saving Type" },
      "groupCodeDescMap": { "ko": "포인트 적립 분류 코드" },
      "codeList": [
        {
          "code": "PURCHASE",
          "color": "#00aaff",
          "codeName_ko": "구매적립",
          "codeName_en": "Purchase",
          "codeDesc_ko": null,
          "codeDesc_en": null
        }
      ]
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
  "http://localhost:3000/openapi/myproject/systemCode?groupCode=PointSavingType"
```

---

## `POST /openapi/{projectId}/systemCode` — GroupCode 추가

### 요청 본문: `OpenApiSystemCodeCreateRequest`

| 필드 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `groupCode` | ✅ | — | |
| `groupCodeNameMap` | | `{}` | |
| `groupCodeDescMap` | | `{}` | |
| `codeList[]` | | `[]` | 각 항목은 `code` 필수, `color` 미지정 시 `null` |
| `use` | | `true` | |
| `export` | | `true` | |
| `updateId` | | `'openapi'` | |

### 사용 예시

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/systemCode" \
  -d '{
    "groupCode": "PointSavingType",
    "groupCodeNameMap": { "ko": "포인트 적립 유형", "en": "Point Saving Type" },
    "codeList": [
      { "code": "PURCHASE", "codeNameMap": { "ko": "구매적립" }, "color": "#00aaff" },
      { "code": "EVENT",    "codeNameMap": { "ko": "이벤트적립" } }
    ]
  }'
```

응답: `{ "ok": true, "groupCode": "PointSavingType" }`

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | `groupCode` 누락 |
| `409` | 동일 `groupCode` 존재 |

---

## `PUT /openapi/{projectId}/systemCode/{groupCode}` — GroupCode 수정

`groupCodeNameMap` 만 갱신합니다 (전체 교체).

### 요청 본문: `OpenApiSystemCodeUpdateRequest`

| 필드 | 필수 | 설명 |
|---|---|---|
| `groupCodeNameMap` | ✅ | 새로운 다국어 이름 맵 |
| `updateId` | | 감사 필드. 미지정 시 `'openapi'` |

### 사용 예시

```bash
curl -X PUT -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/systemCode/PointSavingType" \
  -d '{ "groupCodeNameMap": { "ko": "포인트 적립 종류", "en": "Point Saving Kind" } }'
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 해당 `groupCode` 없음 |

---

## `POST /openapi/{projectId}/systemCode/{groupCode}/code` — Code 추가

지정한 `GroupCode.codeList` 에 새 Code 항목을 삽입합니다.

### 요청 본문: `OpenApiCodeAddRequest`

| 필드 | 필수 | 설명 |
|---|---|---|
| `code` | ✅ | |
| `codeNameMap` | | 다국어 이름 맵 |
| `codeDescMap` | | 다국어 설명 맵 |
| `color` | | 미지정/빈 문자열은 `null` 로 저장 |
| `order` | | 삽입 위치 인덱스(0-base). 미지정/범위 밖이면 끝에 append |
| `updateId` | | 감사 필드 |

### 사용 예시

```bash
# GroupCode 의 두 번째 위치에 EVENT 코드 삽입
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/systemCode/PointSavingType/code" \
  -d '{
    "code": "EVENT",
    "codeNameMap": { "ko": "이벤트적립", "en": "Event" },
    "color": "#ff8800",
    "order": 1
  }'
```

응답: `{ "ok": true, "groupCode": "PointSavingType", "code": "EVENT" }`

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | `GroupCode` 없음 |
| `409` | 동일 `code` 가 이미 존재 |

---

## `PUT /openapi/{projectId}/systemCode/{groupCode}/code/{code}` — Code 수정

`codeNameMap`, `codeDescMap`, `color` 중 1개 이상이 필요합니다 (제공된 필드만 갱신).

### 사용 예시

```bash
curl -X PUT -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/systemCode/PointSavingType/code/EVENT" \
  -d '{
    "codeNameMap": { "ko": "이벤트 적립", "en": "Event Saving" },
    "color": "#ff9900"
  }'
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | 갱신 대상 필드 모두 누락 |
| `404` | GroupCode 또는 Code 없음 |

---

## `DELETE /openapi/{projectId}/systemCode/{groupCode}/code/{code}` — Code 삭제

### 사용 예시

```bash
curl -X DELETE -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/systemCode/PointSavingType/code/EVENT"
```

응답: `{ "ok": true, "groupCode": "PointSavingType", "code": "EVENT" }`

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | GroupCode 또는 Code 없음 |
