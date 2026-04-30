# TourAPI OpenAPI Catalog

확인 기준일: 2026-04-30

이 카탈로그는 [한국관광콘텐츠랩 OpenAPI 목록](https://api.visitkorea.or.kr/#/useUtilExercises)에서 내려받은 메뉴얼 ZIP 27개를 기준으로 정리했습니다. 원본 목록은 SPA 내부 API `https://api.visitkorea.or.kr/use/useUtilExercises.do`에서 확인했고, 메뉴얼은 `/upload/manual/guide/file/...zip` 경로로 내려받았습니다.

원본 ZIP은 저장소에 커밋하지 않고 `.manuals/`에 내려받아 분석했습니다. 다시 받으려면:

```powershell
.\scripts\download_visitkorea_manuals.ps1
```

## Generic Client

모든 서비스는 `TourApiHubClient`에서 호출할 수 있습니다.

```python
from pykrtourapi import TourApiHubClient

hub = TourApiHubClient.from_env()  # 또는 TourApiHubClient("service-key")

page = hub.call("gocamping", "basedList", facltNm="숲")
page = hub.photo_gallery.gallery_list(galSearchKeyword="서울")
page = hub.pet.detail_pet_tour2(content_id="123")
```

`page_no`, `num_of_rows`, `content_id`, `content_type_id`는 Python식 이름으로 전달하면 각각 `pageNo`, `numOfRows`, `contentId`, `contentTypeId`로 바뀝니다. 그 외 파라미터는 메뉴얼의 원문 이름을 그대로 전달합니다.

## Services

| key | service name | operations | manual |
|---|---|---|---|
| `kor` | `KorService2` | `areaCode2`, `categoryCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `detailPetTour2`, `ldongCode2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596499508.zip) |
| `eng` | `EngService2` | `areaCode2`, `categoryCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `ldongCode2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596531873.zip) |
| `chs` | `ChsService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160495049.zip) |
| `cht` | `ChtService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596423271.zip) |
| `jpn` | `JpnService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596480579.zip) |
| `ger` | `GerService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596457504.zip) |
| `fre` | `FreService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596408255.zip) |
| `spn` | `SpnService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596391866.zip) |
| `rus` | `RusService2` | `areaCode2`, `categoryCode2`, `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `searchFestival2`, `searchStay2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `areaBasedSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596057411.zip) |
| `with` | `KorWithService2` | `areaCode2`, `categoryCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `detailWithTour2`, `areaBasedSyncList2`, `ldongCode2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596514908.zip) |
| `green` | `GreenTourService1` | `areaCode1`, `areaBasedList1`, `areaBasedSyncList1` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160406003.zip) |
| `photo_gallery` | `PhotoGalleryService1` | `galleryList1`, `gallerySearchList1`, `galleryDetailList1`, `gallerySyncDetailList1` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160396374.zip) |
| `gocamping` | `GoCamping` | `basedList`, `locationBasedList`, `searchList`, `imageList`, `basedSyncList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160387374.zip) |
| `odii` | `Odii` | `themeBasedList`, `themeLocationBasedList`, `themeSearchList`, `storyBasedList`, `storyLocationBasedList`, `storySearchList`, `themeBasedSyncList`, `storyBasedSyncList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1720672146251.zip) |
| `datalab` | `DataLabService` | `metcoRegnVisitrDDList`, `locgoRegnVisitrDDList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160370032.zip) |
| `durunubi` | `Durunubi` | `routeList`, `courseList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160359411.zip) |
| `employment` | `tursmService` | `empmnInfoList`, `empmnInfoDetail`, `code`, `syncList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1704160822554.zip) |
| `tats_concentration` | `TatsCnctrRateService` | `tatsCnctrRateList`, `tatsCnctrRatedList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725501618773.zip) |
| `local_hub` | `LocgoHubTarService1` | `areaBasedList1` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725501897980.zip) |
| `related_tour` | `TarRlteTarService1` | `areaBasedList1`, `searchKeyword1` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725502022236.zip) |
| `pet` | `KorPetTourService2` | `ldongCode2`, `areaBasedList2`, `locationBasedList2`, `searchKeyword2`, `detailCommon2`, `detailIntro2`, `detailInfo2`, `detailImage2`, `detailPetTour2`, `petTourSyncList2`, `lclsSystmCode2` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1737596366080.zip) |
| `medical` | `MdclTursmService` | `ldongCode`, `areaBasedList`, `locationBasedList`, `searchKeyword`, `mdclTursmSyncList`, `detailCommon`, `detailIntro`, `detailMdclTursm` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725080563660.zip) |
| `wellness` | `WellnessTursmService` | `ldongCode`, `areaBasedList`, `locationBasedList`, `searchKeyword`, `wellnessTursmSyncList`, `detailCommon`, `detailIntro`, `detailInfo`, `detailImage` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725080513010.zip) |
| `photo_award` | `PhokoAwrdService` | `ldongCode`, `phokoAwrdList`, `phokoAwrdSyncList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/1725092509540.zip) |
| `area_diversity` | `AreaTarDivService` | `areaTouDivList`, `areaExpDivList`, `areaIntlDivList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/manual_areaTarDivService.zip) |
| `area_demand_strength` | `AreaTarDemDsService` | `areaTarSjrnDsList`, `areaTarExpDsList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/manual_areaTarDemDsService.zip) |
| `area_resource_demand` | `AreaTarResDemService` | `areaTarSvcDemList`, `areaCulResDemList` | [download](https://api.visitkorea.or.kr/upload/manual/guide/file/manual_areaTarResDemService.zip) |

## Notes

- `KorService2`처럼 typed high-level 메서드가 있는 서비스도 `TourApiHubClient`에서는 raw record로 반환합니다.
- 메뉴얼마다 구버전 서비스명과 최신 서비스명이 함께 섞여 있는 경우가 있어, 표에는 최신/가장 많이 등장한 서비스명을 기준으로 정리했습니다.
- 일부 메뉴얼의 예제 URL에는 오탈자가 있습니다. 예: Odii 메뉴얼에는 `themeBaseSyncdList`가 보이나 operation 표와 실제 패턴 기준으로 `themeBasedSyncList`를 사용합니다.
