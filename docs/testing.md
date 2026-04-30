# Testing Guide

## 기본 원칙

- 기본 테스트는 실제 TourAPI를 호출하지 않는다.
- HTTP는 fake session 또는 `responses`로 고정한다.
- 응답 fixture 값은 실제 TourAPI처럼 문자열 중심으로 둔다.
- live test는 별도 marker로 격리한다.

## 실행

```bash
python -m compileall pykrtourapi tests
python -m pytest
python -m pytest --cov=pykrtourapi --cov-fail-under=90
ruff check .
mypy pykrtourapi
```

## 반드시 유지할 테스트 범위

- 공통 요청 파라미터: `serviceKey`, `MobileOS`, `MobileApp`, `_type=json`
- endpoint URL 조합
- HTTP status 및 `resultCode` 예외 매핑
- XML 오류 응답 매핑
- `items.item` 단일 dict/list/empty 정규화
- 날짜 `YYYYMMDD` 변환
- 법정동/분류체계/카테고리 의존성 검증
- 주요 dataclass 변환
- CLI JSON 직렬화

## Live test 규칙

실제 API를 호출하는 테스트를 추가할 때:

```python
import os
import pytest

@pytest.mark.live
def test_live_area_codes():
    key = os.getenv("KTO_SERVICE_KEY")
    if not key:
        pytest.skip("KTO_SERVICE_KEY is not set")
```

live test에서는 관광지 이름, 총 건수, 정렬 순서처럼 변하기 쉬운 값을 단정하지 않는다. 응답 shape, 타입, 필수 공통 필드만 확인한다.
