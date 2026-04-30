# pykrtourapi

한국관광공사(KTO) TourAPI를 Python에서 쓰기 좋게 감싼 비공식 클라이언트입니다.

기본 대상은 공공데이터포털의 **한국관광공사_국문 관광정보서비스_GW**이며, 현재 기본 서비스 URL은 `http://apis.data.go.kr/B551011/KorService2`입니다. 공식 문서 기준으로 지역/위치/키워드/행사/숙박/상세/이미지/동기화/코드 조회 계열을 우선 지원합니다.

> 확인 기준일: 2026-04-30  
> 공식 근거: [공공데이터포털 국문 관광정보서비스_GW](https://www.data.go.kr/en/data/15101578/openapi.do), [2026-01-09 TourAPI URL/입출력 변경 공지](https://www.data.go.kr/bbs/ntc/selectNotice.do?originId=NOTICE_0000000004471)

## 특징

- `KorService2` 기본 지원: `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, 상세/이미지/코드 조회
- `Page[T]`와 frozen dataclass 모델 반환
- `items.item`이 단일 object 또는 list로 오는 차이를 내부에서 정규화
- `resultCode`, HTTP status, XML 형태 서비스키 오류를 typed exception으로 매핑
- 법정동 코드(`lDong*`)와 분류체계 코드(`lclsSystm*`) 의존성 검증
- 기본 테스트는 실제 API를 호출하지 않는 offline mock 방식

## 설치

개발 중인 로컬 저장소에서는:

```bash
pip install -e ".[dev]"
```

## 인증키

공공데이터포털에서 한국관광공사 국문 관광정보서비스 활용 신청 후 **Decoding 인증키**를 환경변수에 넣는 방식을 권장합니다. 이 라이브러리는 `requests.get(..., params=...)`를 사용하므로 이미 인코딩된 키를 다시 인코딩하지 않도록 주의하세요.

```bash
export KTO_SERVICE_KEY="발급받은_decoding_인증키"
```

PowerShell:

```powershell
$env:KTO_SERVICE_KEY="발급받은_decoding_인증키"
```

대체 환경변수로 `KRTOURAPI_SERVICE_KEY`, `TOURAPI_SERVICE_KEY`도 읽습니다.

## 사용 예시

```python
from pykrtourapi import ContentType, KrTourApiClient

client = KrTourApiClient.from_env(mobile_app="my-travel-app")

page = client.search_keyword(
    "경복궁",
    content_type_id=ContentType.TOURIST_ATTRACTION,
    l_dong_regn_cd="11",
)

for item in page.items:
    print(item.content_id, item.title, item.addr1, item.map_x, item.map_y)

detail = client.detail_common(page.items[0].content_id)
print(detail.overview)
```

위치 기반 조회:

```python
nearby = client.location_based_list(
    map_x=126.9769,
    map_y=37.5796,
    radius=1000,
    content_type_id=ContentType.RESTAURANT,
)
```

코드 조회:

```python
for code in client.area_codes().items:
    print(code.code, code.name)

for code in client.legal_dong_codes(list_yn=True).items:
    print(code.raw)

for code in client.classification_system_codes(list_yn=True).items:
    print(code.raw)
```

## 제공 메서드

| 메서드 | TourAPI endpoint | 반환 |
|---|---|---|
| `area_based_list()` | `areaBasedList2` | `Page[TourItem]` |
| `location_based_list()` | `locationBasedList2` | `Page[TourItem]` |
| `search_keyword()` | `searchKeyword2` | `Page[TourItem]` |
| `search_festival()` | `searchFestival2` | `Page[TourItem]` |
| `search_stay()` | `searchStay2` | `Page[TourItem]` |
| `detail_common()` | `detailCommon2` | `TourDetail` |
| `detail_intro()` | `detailIntro2` | `Page[IntroInfo]` |
| `detail_info()` | `detailInfo2` | `Page[RepeatInfo]` |
| `detail_images()` | `detailImage2` | `Page[ImageInfo]` |
| `area_based_sync_list()` | `areaBasedSyncList2` | `Page[TourItem]` |
| `area_codes()` | `areaCode2` | `Page[CodeItem]` |
| `category_codes()` | `categoryCode2` | `Page[CodeItem]` |
| `legal_dong_codes()` | `ldongCode2` | `Page[CodeItem]` |
| `classification_system_codes()` | `lclsSystmCode2` | `Page[CodeItem]` |
| `raw_endpoint()` | 임의 endpoint | `Page[Mapping]` |

## 다른 언어 서비스

동일한 endpoint 이름을 쓰는 다국어 서비스는 `language=`로 선택할 수 있습니다.

```python
client = KrTourApiClient.from_env(language="en")  # EngService2
```

지원 매핑: `ko`, `en`, `ja`/`jp`, `zh-cn`/`zh`, `zh-tw`, `de`, `fr`, `es`, `ru`

## CLI

```bash
pykrtourapi keyword 경복궁 --content-type-id 12
pykrtourapi location --map-x 126.9769 --map-y 37.5796 --radius 1000
pykrtourapi detail 126508
pykrtourapi area-codes
```

## 개발

```bash
python -m compileall pykrtourapi tests
python -m pytest
python -m pytest --cov=pykrtourapi --cov-fail-under=90
ruff check .
mypy pykrtourapi
```

기본 테스트는 실제 TourAPI를 호출하지 않습니다. live test를 추가할 때는 `@pytest.mark.live`를 붙이고 `KTO_SERVICE_KEY`가 없으면 skip 해야 합니다.

자세한 구현 규칙은 [krtourapi-api.md](krtourapi-api.md), 반복 실수 방지 문서는 [docs/repeated-mistakes.md](docs/repeated-mistakes.md), 테스트 정책은 [docs/testing.md](docs/testing.md)를 참고하세요.

## 라이선스

GPL-3.0-or-later.
