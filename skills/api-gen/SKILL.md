# API Documentation Generator

Spring MVC 의 RestController 를 분석해, OpenAPI 스펙과 HTML 문서를 자동으로 생성합니다.

## Trigger

다음 키워드로 호출:
- "api doc", "api 문서", "문서 생성", "generate api doc"

## 환경변수

- API_GEN_SOURCE_DIR : 소스 디렉토리. 디폴트: "./"
- API_GEN_API_SOURCE_DIR : RestController 가 포함된 소스코드 디렉토리. 디폴트: "./"
- API_GEN_FILE : yaml 파일. 디폴트: "./doc/api/api.yaml"
- API_GEN_TITLE : API 문서 제목. 디폴트로 프로젝트 이름을 사용함.
- API_GEN_VERSION : API 문서 버전. 디폴트로 프로젝트의 version 정보를 사용함.

## Commands

```bash
# 1. OpenAPI YAML 생성
npx @g1cloud/api-gen \
    --source ${API_GEN_SOURCE_DIR:-./} \
    --api-source ${API_GEN_API_SOURCE_DIR:-./} \
    --output ${API_GEN_FILE:-./doc/api/api.yaml} \
    --title "${API_GEN_TITLE}" \
    --api-version "${API_GEN_VERSION}"

```

## Usage

RestController 나 RestController 에서 사용하는 DTO 가 변경된 경우, 이 스킬을 실행하면 문서가 자동으로 업데이트됩니다.
