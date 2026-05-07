# EntityModel API

비즈니스 모듈의 Entity Diagram 을 텍스트 또는 원본 JSON 으로 조회합니다.
엔터티 추가/속성 변경은 [BizModule 문서](./bizModule.md) 를 참고하세요.

[← README 로 돌아가기](./README.md)

---

## `GET /openapi/{projectId}/entityModel/{id}/text` — 엔터티 모델 텍스트 조회

지정한 비즈니스 모듈의 Entity Diagram 을 사람/LLM 친화적 텍스트로 변환합니다.

### 경로/쿼리 파라미터

| 이름 | 타입 | 설명 |
|---|---|---|
| `id` (path) | string | 비즈니스 모듈 `_id` |
| `entity` | string \| string[] | 엔터티명 필터 (단일 또는 배열) |
| `table` | string \| string[] | 테이블명 필터 (단일 또는 배열) |
| `package` | string \| string[] | 패키지명 필터 (단일 또는 배열) |
| `format` | — | 공통 |

배열 파라미터는 `?entity=A&entity=B` 또는 `?entity=A,B` 형태 모두 사용 가능합니다.

### 응답: `TextResponse`

```json
{ "text": "package marketing\n\nEntity Coupon (mkt_coupon) ..." }
```

### 사용 예시

```bash
# 모듈 전체 텍스트
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/entityModel/65a.../text"

# 특정 엔터티 두 개만
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/entityModel/65a.../text?entity=SalesOrder&entity=Checkout"

# 패키지 단위
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/entityModel/65a.../text?package=marketing"
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 필터 조건에 맞는 Entity 없음 |

---

## `GET /openapi/{projectId}/entityModel/{id}/entities/{names}` — 다중 엔터티 원본 조회

`names` 로 지정한 엔터티들의 **원본 객체(JSON)** 를 한 번에 반환합니다.
텍스트 변환 없이 `attributes`, `indexes`, `associations` 등 모든 메타를 그대로 받을 때 사용합니다.

### 경로 파라미터

| 이름 | 설명 |
|---|---|
| `names` | 콤마 구분된 이름 목록. `entity.name` 또는 `entity.dbAttrs.physicalName`(테이블명) 양쪽으로 매칭 |

예: `SalesOrder,Checkout` 또는 `sls_order,sls_checkout` (혼용 가능)

### 응답: `OpenApiEntityModelEntitiesResponse`

```json
{
  "items": [
    { "name": "SalesOrder", "dbAttrs": { "physicalName": "sls_order" }, "attributes": [/*...*/] },
    { "name": "Checkout",   "dbAttrs": { "physicalName": "sls_checkout" }, "attributes": [/*...*/] }
  ],
  "missing": ["Unknown"],
  "totalCount": 2
}
```

- `items` 는 매칭된 엔터티의 원본 객체 배열입니다 (`additionalProperties: true` — 모든 필드 그대로 전달).
- `missing` 은 요청 중 매칭되지 않은 이름 목록입니다.
- `totalCount` 는 `items.length` 입니다.

### 사용 예시

```bash
# 엔터티명으로
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/entityModel/65a.../entities/SalesOrder,Checkout"

# 테이블명으로 (혼용 가능)
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:3000/openapi/myproject/entityModel/65a.../entities/sls_order,Checkout"
```

### 에러

| 상태 | 발생 시점 |
|---|---|
| `404` | 비즈니스 모듈 또는 Entity Diagram 자체가 없음 |

> 일부 이름이 매칭되지 않은 경우는 200 응답의 `missing` 에 담깁니다 (404 아님).
