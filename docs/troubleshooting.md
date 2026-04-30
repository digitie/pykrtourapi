# Troubleshooting

## `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`

가능한 원인:

- 인증키를 잘못 복사했다.
- Encoding 키를 `params=`에 넣어 이중 인코딩됐다.
- 해당 API 활용 신청이 아직 승인되지 않았다.
- 기존 서비스 URL에서 `KorService2`로 재신청이 필요하다.

해결:

1. 공공데이터포털 마이페이지에서 Decoding 키를 확인한다.
2. `KTO_SERVICE_KEY`에 Decoding 키를 넣는다.
3. 국문 관광정보서비스_GW 활용 신청 상태를 확인한다.

## 결과가 비어 있음

가능한 원인:

- `resultCode=03`인 정상적인 데이터 없음 응답
- `eventStartDate`, `modifiedtime` 날짜 범위가 너무 좁음
- `sigunguCode`만 보내고 `areaCode`를 누락
- `lDongSignguCd`만 보내고 `lDongRegnCd`를 누락
- 분류체계 하위 코드만 단독 전달

해결:

- 필터를 하나씩 줄여가며 확인한다.
- 코드 조회 메서드로 실제 코드 값을 먼저 가져온다.
- 라이브러리 validation 오류가 나면 상위 코드를 함께 전달한다.

## JSON 파싱 실패

TourAPI는 `_type=json` 요청에도 인증키/권한 오류를 XML로 돌려줄 수 있다. `pykrtourapi`는 알려진 XML 오류 envelope를 파싱해 `TourApiAuthError` 등으로 바꾼다. 그래도 `TourApiParseError`가 난다면 응답 본문 일부를 확인하고 새 envelope 형태를 테스트로 추가한다.

## HTTP 403 Forbidden

가능한 원인:

- 해당 서비스 활용신청이 되어 있지 않다. 예를 들어 국문만 신청한 키로 `EngService2`를 호출하면 403이 날 수 있다.
- TourAPI 게이트웨이가 기본 `python-requests` User-Agent를 차단한다.
- 인증키가 잘못되었거나 승인 전이다.

해결:

- 신청된 서비스 URL인지 먼저 확인한다.
- `pykrtourapi` 기본 세션은 브라우저 호환 User-Agent를 설정한다. 커스텀 session을 넘길 때도 User-Agent를 지정한다.
- live test에서는 미신청 서비스의 403을 `TourApiAuthError` 매핑 검증에 사용한다.

## `radius must be between 1 and 20000 meters`

`locationBasedList2`의 반경은 공식 문서 기준 최대 20km다. 더 넓은 검색이 필요하면 행정구역 기반 조회와 후처리를 사용한다.

## 한글이 터미널에서 깨져 보임

Windows PowerShell의 출력 인코딩 문제일 수 있다. 파일이 깨졌다고 가정하기 전에 Python에서 UTF-8로 읽거나 테스트 문자열 비교로 확인한다.
