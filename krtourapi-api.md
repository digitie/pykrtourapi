# TourAPI 구현 메모

확인 기준일: 2026-04-30

## 공식 근거

- [공공데이터포털 한국관광공사_국문 관광정보서비스_GW](https://www.data.go.kr/en/data/15101578/openapi.do)
- [공공데이터포털 2026-01-09 TourAPI 오퍼레이션 URL/입출력 변경 공지](https://www.data.go.kr/bbs/ntc/selectNotice.do?originId=NOTICE_0000000004471)
- [TourAPI 관광데이터 Hub](https://api.visitkorea.or.kr)

공공데이터포털 문서에는 국문 관광정보서비스가 JSON+XML REST API이며, 약 26만 건의 국내 관광정보를 15종 범주로 제공한다고 안내되어 있다. 기본 요청 링크는 `http://apis.data.go.kr/B551011/KorService2/{operation}` 형식이다.

## 공통 요청

| 파라미터 | 규칙 |
|---|---|
| `serviceKey` | 공공데이터포털 인증키. `params=`를 쓰므로 Decoding 키 권장 |
| `MobileOS` | `IOS`, `AND`, `WEB`, `WIN`, `ETC`; 기본 `ETC` |
| `MobileApp` | 서비스/앱 이름; 기본 `pykrtourapi` |
| `_type` | 항상 `json` |
| `pageNo` | 1 이상 |
| `numOfRows` | 1~1000 |

## 구현 endpoint

| 메서드 | endpoint | 핵심 요청 |
|---|---|---|
| `area_based_list` | `areaBasedList2` | `contentTypeId`, 지역/법정동/분류체계 필터 |
| `location_based_list` | `locationBasedList2` | `mapX`, `mapY`, `radius` 필수. `radius <= 20000` |
| `search_keyword` | `searchKeyword2` | `keyword` 필수 |
| `search_festival` | `searchFestival2` | `eventStartDate` 필수, `eventEndDate` 선택 |
| `search_stay` | `searchStay2` | 숙박 정보 목록 |
| `detail_common` | `detailCommon2` | `contentId` |
| `detail_intro` | `detailIntro2` | `contentId`, `contentTypeId` |
| `detail_info` | `detailInfo2` | `contentId`, `contentTypeId` |
| `detail_images` | `detailImage2` | `contentId`, `imageYN`, `subImageYN` |
| `area_based_sync_list` | `areaBasedSyncList2` | 동기화 목록, `showFlag` 선택 |
| `area_codes` | `areaCode2` | `areaCode` 선택 |
| `category_codes` | `categoryCode2` | `contentTypeId`, `cat1`, `cat2`, `cat3` |
| `legal_dong_codes` | `ldongCode2` | `lDongRegnCd`, `lDongListYn` |
| `classification_system_codes` | `lclsSystmCode2` | `lclsSystm1/2/3`, `lclsSystmListYn` |

## 코드 체계

### 국문 contentTypeId

| 값 | 의미 |
|---|---|
| `12` | 관광지 |
| `14` | 문화시설 |
| `15` | 축제/공연/행사 |
| `25` | 여행코스 |
| `28` | 레포츠 |
| `32` | 숙박 |
| `38` | 쇼핑 |
| `39` | 음식점 |

### 정렬 arrange

| 값 | 의미 |
|---|---|
| `A` | 제목순 |
| `C` | 수정일순 |
| `D` | 생성일순 |
| `E` | 거리순 |
| `O` | 대표 이미지 있는 항목 제목순 |
| `Q` | 대표 이미지 있는 항목 수정일순 |
| `R` | 대표 이미지 있는 항목 생성일순 |
| `S` | 대표 이미지 있는 항목 거리순 |

## 의존성 검증

기존 `areaCode`, `sigunguCode`, `cat1/2/3`는 공식 문서에서 삭제 예정 또는 대체 예정으로 표시되는 항목이 있다. 하지만 운영 호환성을 위해 여전히 전달할 수 있게 두되, 하위 코드만 단독으로 들어가는 실수는 막는다.

- `sigunguCode`는 `areaCode` 필요
- `cat2`는 `cat1` 필요
- `cat3`는 `cat1`, `cat2` 필요
- `lDongSignguCd`는 `lDongRegnCd` 필요
- `lclsSystm2`는 `lclsSystm1` 필요
- `lclsSystm3`는 `lclsSystm1`, `lclsSystm2` 필요

## 응답 정규화

TourAPI 응답은 보통 아래 형태다.

```json
{
  "response": {
    "header": {"resultCode": "00", "resultMsg": "OK"},
    "body": {
      "items": {"item": []},
      "numOfRows": 10,
      "pageNo": 1,
      "totalCount": 0
    }
  }
}
```

주의할 점:

- `items`가 빈 문자열일 수 있다.
- `items.item`이 단일 object일 수 있다.
- `items.item`이 list일 수 있다.
- 서비스키 오류는 `_type=json` 요청이어도 XML로 돌아올 수 있다.
- `resultCode=03`은 목록에서는 빈 `Page`로 처리하고, 단건 상세에서는 `TourApiNoDataError`로 올린다.

## 예외 매핑

```text
TourApiError
├── TourApiAuthError       # 인증키/활용신청/권한 문제
├── TourApiRateLimitError  # 호출 한도/트래픽 제한
├── TourApiRequestError    # 잘못된 파라미터 또는 4xx 계열
├── TourApiNoDataError     # 단건 상세에서 결과 없음
├── TourApiServerError     # 5xx, resultCode 99/04 계열
└── TourApiParseError      # JSON/XML 구조 또는 타입 변환 실패
```

## 확장 원칙

1. 공식 문서 또는 실제 응답 fixture로 endpoint와 필드를 확인한다.
2. 공개 메서드는 snake_case, 요청 파라미터는 내부에서 TourAPI 원문 이름으로 변환한다.
3. 새 필드가 불안정하면 dataclass 필드 추가보다 `raw` 보존을 우선한다.
4. 일반 테스트는 네트워크를 사용하지 않는다.
5. 반복되는 실수를 발견하면 `docs/repeated-mistakes.md`와 guardrail test를 함께 갱신한다.
