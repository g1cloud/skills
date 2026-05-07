# BizModule API

비즈니스 모듈 목록 및 그 하위 엔터티/속성 관리를 제공합니다.
엔터티 모델 텍스트/원본 객체 조회는 [EntityModel 문서](./entityModel.md) 를 참고하세요.

[← README 로 돌아가기](./README.md)

---

## 개념 정리

```
BizModule (id = MongoDB _id)
  └─ Entity Diagram
       ├─ entities[] (그룹 없음, 다이어그램 루트)
       └─ entityGroups[]
            └─ packageName, entities[]

Entity (entity.name = 논리명/클래스명)
  ├─ dbAttrs.physicalName : 테이블 물리명
  └─ attributes[] : 속성 풀
       ├─ name : camelCase 속성명
       └─ dbAttribute.physicalName : DB 컬럼명
```

- 엔터티 검색은 `entity.name` 또는 `entity.dbAttrs.physicalName` 양쪽으로 가능합니다.
- 속성 추가/삭제 시 인덱스 참조 충돌은 409 로 차단됩니다.

---

## `GET /openapi/{projectId}/bizModule` — 비즈니스 모듈 목록

### 쿼리 파라미터

| 이름 | 타입 | 설명 |
|---|---|---|
| `moduleId` | string | LIKE 검색 (대소문자 무시) |
| `moduleName` | string | LIKE 검색 (대소문자 무시) |
| `offset`, `limit`, `sort`, `format` | — | 공통 |

### 응답: `OpenApiBizModuleListResponse`

```json
{
  "items": [
    {
      "moduleId": "SLS",
      "moduleName": "Sales",
      "updateId": "kimos",
      "updateDate": "2026-04-30T..."
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
  "http://localhost:3000/openapi/myproject/bizModule?moduleId=SLS"
```

---

## `GET /openapi/{projectId}/bizModule/{id}/entities` — 모듈의 엔터티 목록

지정한 비즈니스 모듈의 Entity Diagram 모든 엔터티(루트 + 모든 그룹)를 평탄화하여 반환합니다.

### 경로/쿼리 파라미터

| 이름 | 타입 | 설명 |
|---|---|---|
| `id` (path) | string | 비즈니스 모듈 `_id` |
| `entityName` | string | 엔터티명 정규식 (`i` 플래그) |
| `logicalName` | string | 논리명 정규식 |
| `physicalName` | string | 물리명 정규식 |
| `format` | — | 공통 |

### 응답: `OpenApiEntityListResponse`

```json
{
  "items": [
    { "entityName": "SalesOrder",  "logicalName": "판매 주문", "physicalName": "sls_order" },
    { "entityName": "Checkout",    "logicalName": "체크아웃",   "physicalName": "sls_checkout" }
  ],
  "totalCount": 2
}
```

### 사용 예시

```bash
# 'order' 가 포함된 엔터티만
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/bizModule/65a.../entities?entityName=order"
```

---

## `POST /openapi/{projectId}/bizModule/{id}/entities` — 엔터티 추가

지정한 비즈니스 모듈의 Entity Diagram 에 새 엔터티를 추가합니다.

### 동작 규칙

- `name`(클래스명) 과 `dbAttrs.physicalName`(테이블명) 은 필수.
- `groupName` 미지정 → 다이어그램 루트 `entities[]` 에 추가.
- `groupName` 지정 → 해당 `packageName` 의 EntityGroup 에 추가. 그룹이 없으면 404.
- `name` 또는 `physicalName` 이 다이어그램 내 어딘가에 이미 있으면 409.
- `columns[]` 는 단순화된 컬럼 입력으로, 내부적으로 `attribute + dbAttribute(1개)` 쌍으로 변환되어 저장됩니다.
- `attributes` 풀 구조, `indexes`, `associations`, `jpaAttrs` 등은 받지 않으며 모두 기본값으로 채워집니다.

### 요청 본문: `OpenApiEntityCreateRequest`

| 필드 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `name` | ✅ | — | 엔터티 논리명/클래스명 |
| `dbAttrs.physicalName` | ✅ | — | 테이블 물리명 |
| `dbAttrs.logicalName` | | — | 다국어 맵 |
| `description` | | — | 다국어 맵 |
| `groupName` | | — | EntityGroup `packageName` |
| `stereotype` | | `JPA_ENTITY` | `JPA_ENTITY` \| `JPA_EMBEDDABLE` |
| `hasPersonalInfo` | | `false` | |
| `abstractClass` | | `false` | |
| `useMultiLangEntity` | | `false` | |
| `columns[]` | | `[]` | 단순 컬럼 입력 (아래 표) |
| `updateId` | | `'openapi'` | |

#### `columns[]` 항목 (`OpenApiEntityColumnInput`)

| 필드 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `name` | ✅ | — | 속성명 (camelCase) |
| `physicalName` | ✅ | — | DB 컬럼명 |
| `logicalName` | | — | 다국어 맵 |
| `description` | | — | 다국어 맵 |
| `type` | | `String` | Java 타입 등 논리 타입 |
| `dataType` | | `VARCHAR` | DB 데이터타입 |
| `length` | | — | 컬럼 길이 |
| `identifier` | | `false` | PK 여부 |
| `notNull` | | `false` | |
| `unique` | | `false` | |
| `autoIncrement` | | `false` | |
| `updatable` | | `true` | |
| `attributeGroup` | | — | `sn` / `id` / `code` / `amt` / `no` / `datetime` / `val` 등 |

### 응답: `OpenApiEntityWriteAck`

```json
{
  "ok": true,
  "name": "Coupon",
  "physicalName": "mkt_coupon",
  "modelId": "550e8400-e29b-41d4-a716-446655440000"
}
```

`modelId` 는 자동 생성된 엔터티 UUID 로, 인덱스/관계 추가 시 참조에 사용합니다.

### 사용 예시

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/bizModule/65a.../entities" \
  -d '{
    "name": "Coupon",
    "dbAttrs": {
      "physicalName": "mkt_coupon",
      "logicalName": { "ko": "쿠폰", "en": "Coupon" }
    },
    "description": { "ko": "마케팅 쿠폰" },
    "groupName": "marketing",
    "columns": [
      {
        "name": "couponId",
        "physicalName": "coupon_id",
        "logicalName": { "ko": "쿠폰 ID" },
        "type": "String",
        "dataType": "VARCHAR",
        "length": 32,
        "identifier": true,
        "notNull": true,
        "attributeGroup": "id"
      },
      {
        "name": "discountAmount",
        "physicalName": "dscnt_amt",
        "type": "BigDecimal",
        "dataType": "DECIMAL",
        "length": 18,
        "attributeGroup": "amt"
      }
    ]
  }'
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | `name` / `dbAttrs.physicalName` 누락 |
| `404` | 비즈니스 모듈 또는 `groupName` 없음 |
| `409` | 같은 다이어그램에 `name` 또는 `physicalName` 중복 |

---

## `POST /openapi/{projectId}/bizModule/{id}/entities/{entityName}/attributes` — 속성 추가

엔터티의 `attributes` 배열에 새 속성을 추가합니다.

### 동작 규칙

- 엔터티는 다이어그램 루트와 모든 그룹 `entities[]` 에서 `entity.name === entityName` 으로 검색.
- `order` 미지정 시 기존 `attributes` 의 `max(order) + 1` 자동 부여.
- 같은 엔터티 내 `name` 또는 `physicalName` 중복 시 409.

### 요청 본문: `OpenApiAttributeAddRequest`

`OpenApiEntityColumnInput` 의 모든 필드 + 다음:

| 필드 | 필수 | 설명 |
|---|---|---|
| `order` | | 부여할 `order` 값 |
| `updateId` | | 감사 필드 |

### 응답: `OpenApiAttributeWriteAck` (POST)

```json
{
  "ok": true,
  "entityName": "Coupon",
  "attributeName": "expireDate",
  "physicalName": "expire_dt",
  "modelId": "9b2..."
}
```

### 사용 예시

```bash
curl -X POST -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "http://localhost:3000/openapi/myproject/bizModule/65a.../entities/Coupon/attributes" \
  -d '{
    "name": "expireDate",
    "physicalName": "expire_dt",
    "logicalName": { "ko": "만료일시" },
    "type": "LocalDateTime",
    "dataType": "DATETIME",
    "attributeGroup": "datetime"
  }'
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `400` | `name` / `physicalName` 누락 |
| `404` | 엔터티 없음 |
| `409` | 같은 엔터티 내 `name` / `physicalName` 중복 |

---

## `DELETE /openapi/{projectId}/bizModule/{id}/entities/{entityName}/attributes/{attributeName}` — 속성 삭제

엔터티의 `attributes` 배열에서 `attributeName` 항목을 제거합니다.

### 동작 규칙

- 같은 엔터티의 인덱스가 해당 속성의 `dbAttribute` 를 참조하면 409 로 차단됩니다.
  응답 메시지에 차단 원인 인덱스 이름이 포함되며, 해당 인덱스를 먼저 정리해야 합니다.

### 응답: `OpenApiAttributeWriteAck` (DELETE — `physicalName`/`modelId` 미포함)

```json
{ "ok": true, "entityName": "Coupon", "attributeName": "expireDate" }
```

### 사용 예시

```bash
curl -X DELETE -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/bizModule/65a.../entities/Coupon/attributes/expireDate"
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 엔터티 또는 속성 없음 |
| `409` | 인덱스에서 해당 속성 참조 중 |
