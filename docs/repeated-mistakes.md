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

## 국문 `KorService2`만 구현하고 전체 OpenAPI라고 말하기

**실수:** `api.visitkorea.or.kr/#/useUtilExercises`에는 27개 서비스가 있는데, 자주 쓰는 국문 관광정보서비스만 보고 “전체 구현”으로 착각한다.

**증상:** 고캠핑, 관광사진, 오디, 데이터랩, 반려동물, 의료/웰니스, 지역 수요 계열 서비스를 호출할 방법이 없다.

**규칙:** typed wrapper는 `KorService2`에 집중하되, 전체 OpenAPI 지원은 `SERVICE_DEFINITIONS`와 `TourApiHubClient`가 책임진다. 메뉴얼 목록이 바뀌면 카탈로그 테스트를 먼저 갱신한다.

**가드레일:** `test_catalog_contains_all_manual_services`, `test_hub_call_by_service_key_and_operation_alias`.

## 메뉴얼 ZIP 원본을 저장소에 커밋하기

**실수:** 공식 메뉴얼 ZIP/DOCX를 분석용으로 내려받은 뒤 그대로 git에 올린다.

**증상:** 저장소가 불필요하게 커지고, 외부 원문 파일의 라이선스/갱신 이력을 패키지 릴리스와 섞어 버린다.

**규칙:** 원본은 `.manuals/`에만 내려받고 `.gitignore`로 제외한다. 재현이 필요하면 `scripts/download_visitkorea_manuals.ps1`를 사용한다.

**가드레일:** `.manuals/`는 gitignore에 유지하고, 문서에는 원본 URL과 다운로드 절차만 남긴다.

## 인증키를 테스트 코드나 커밋에 남기기

**실수:** 실 서버 테스트를 빠르게 돌리려고 인증키를 테스트 파일, README 예시, shell script 기본값에 직접 넣는다.

**증상:** 키가 git history에 남고, 원격 저장소나 패키지 배포본에 노출된다.

**규칙:** 인증키는 `.env.local` 또는 현재 shell 환경변수에만 둔다. `.env*`는 gitignore에 유지하고, 커밋 전 `git status --ignored .env.local`로 추적되지 않는지 확인한다.

**가드레일:** `scripts/run_live_tests.ps1`는 `.env.local`을 읽기만 하며, live test는 `KTO_SERVICE_KEY`가 없으면 skip한다.

## 실 서버 응답 코드를 문서 예시 `00`만 정상으로 보기

**실수:** 정상 응답을 `resultCode=00`만 허용한다.

**증상:** 실제 국문 `areaCode2` 응답처럼 `resultCode=0000`이 오면 성공인데도 오류로 처리한다.

**규칙:** `00`, `0000`, `0`, `NORMAL_CODE`는 모두 정상 코드로 본다.

**가드레일:** `test_result_code_0000_is_treated_as_success`, `test_live_korean_area_codes_returns_tourapi_shape`.
