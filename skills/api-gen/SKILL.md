---
name: api-gen
description: Analyzes Spring MVC RestControllers to automatically generate OpenAPI specs and HTML documentation.
---

# API Documentation Generator

## Trigger

Invoked with the following keywords:
- "api doc", "api 문서", "문서 생성", "generate api doc"

## Environment Variables

- API_GEN_SOURCE_DIR: Source directory. Default: "./"
- API_GEN_API_SOURCE_DIR: Source code directory containing RestControllers. Default: "./"
- API_GEN_FILE: YAML file path. Default: "./doc/api/api.yaml"
- API_GEN_TITLE: API document title. Uses the project name by default.
- API_GEN_VERSION: API document version. Uses the project's version info by default.

## Commands

```bash
# 1. Generate OpenAPI YAML
npx @g1cloud/api-gen \
    --source ${API_GEN_SOURCE_DIR:-./} \
    --api-source ${API_GEN_API_SOURCE_DIR:-./} \
    --output ${API_GEN_FILE:-./doc/api/api.yaml} \
    --title "${API_GEN_TITLE}" \
    --api-version "${API_GEN_VERSION}"
```

## Usage

Run this skill when a RestController or any DTO used by a RestController has been modified, and the documentation will be automatically updated.
