# Repeated Mistakes To Avoid

이 문서는 `pykrtourapi`를 만들면서 반복하기 쉬운 실수를 고정해 두는 로그입니다. 같은 문제가 다시 나오면 반드시 테스트와 함께 갱신합니다.

## 서비스키 인코딩

**실수:** URL-encoded 인증키를 `requests`의 `params=`에 넣어 다시 인코딩한다.

**증상:** 정상 키인데도 `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`가 나온다.

**규칙:** 라이브러리 사용 예시는 Decoding 키를 기준으로 한다. 직접 URL 문자열을 만들 때만 Encoding 키를 고려한다.

**가드레일:** HTTP 테스트가 `serviceKey`를 query param으로 그대로 넘기는지 확인한다.

## JSON 요청이어도 XML 오류가 올 수 있음

**실수:** `_type=json`이면 모든 응답이 JSON이라고 가정한다.

**증상:** 인증키 오류에서 JSON 파싱 실패만 보이고 실제 원인을 잃는다.

**규칙:** JSON 파싱 실패 시 XML error envelope를 먼저 파싱하고 typed exception으로 매핑한다.

**가드레일:** `test_non_json_xml_service_key_error_maps_to_auth`.

## `items.item`은 항상 list가 아님

**실수:** 응답을 무조건 `for row in body["items"]["item"]`로 순회한다.

**증상:** 결과가 1건일 때 dict key를 순회하거나 타입 오류가 난다.

**규칙:** missing/blank/single object/list를 모두 정규화한 뒤 모델로 변환한다.

**가드레일:** 클라이언트 테스트가 단일 dict와 빈 응답을 모두 검증한다.

## 하위 코드만 단독으로 보내기

**실수:** `sigunguCode`, `cat2`, `cat3`, `lDongSignguCd`, `lclsSystm2`, `lclsSystm3`를 상위 코드 없이 보낸다.

**증상:** 공공데이터포털 쪽에서 빈 결과 또는 모호한 요청 오류가 난다.

**규칙:** public client에서 의존성 검증을 먼저 수행한다.

**가드레일:** `test_dependent_filter_validation`.

## `detailCommon2`에 구버전 조회 플래그를 계속 보내기

**실수:** `defaultYN`, `firstImageYN`, `overviewYN` 같은 구버전 플래그를 계속 유지한다.

**증상:** 서비스 버전이 바뀐 뒤 문서와 요청 모양이 어긋난다.

**규칙:** `detail_common()`은 `contentId`, pagination만 보낸다. 추가 필드는 공식 문서 또는 실제 응답으로 확인 후 추가한다.

**가드레일:** detail request shape 테스트를 추가할 때 구버전 플래그가 없는지 확인한다.

## 날짜 형식에 하이픈 넣기

**실수:** `2026-04-30` 같은 ISO 날짜 문자열을 그대로 넘긴다.

**증상:** TourAPI가 날짜 파라미터를 인식하지 못한다.

**규칙:** 요청 날짜는 `YYYYMMDD`만 허용한다. Python `date`/`datetime`은 내부에서 변환한다.

**가드레일:** `test_festival_dates_are_normalized`, `test_date_and_yn_conversions`.

## 불안정한 필드를 dataclass에 성급히 고정하기

**실수:** content type별로 달라지는 intro/detail 필드를 모두 public dataclass 필드로 박아 넣는다.

**증상:** 한 content type에서는 맞지만 다른 content type에서 누락/오해가 생긴다.

**규칙:** 공통 필드만 모델에 올리고, 변동 필드는 `raw`로 보존한다.

**가드레일:** `IntroInfo.raw`, `RepeatInfo.raw`를 유지한다.
