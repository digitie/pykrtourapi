from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st
from pydantic import BaseModel

from visitkorea import (
    SERVICE_BY_KEY,
    SERVICE_DEFINITIONS,
    TourApiError,
    TourApiHubClient,
    get_api_catalog,
    normalize_service_key,
    resolve_service_key,
    service_key_env_names,
    service_key_sources,
)


def jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def catalog_rows_for_service(service_id: str) -> list[dict[str, Any]]:
    return [row for row in get_api_catalog() if row["service_id"] == service_id]


def dataframe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "service_key_env_names": ", ".join(row["service_key_env_names"]),
        }
        for row in rows
    ]


def parse_params(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        return {}
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Parameters JSON must be an object.")
    return value


st.set_page_config(page_title="VisitKorea TourAPI Debug UI", layout="wide")
st.title("VisitKorea TourAPI Debug UI")

catalog = get_api_catalog()
service_options = {
    f"{service.dataset_name} ({service.key})": service.key for service in SERVICE_DEFINITIONS
}

with st.sidebar:
    st.header("API")
    selected_service_label = st.selectbox("Dataset", list(service_options))
    selected_service_id = service_options[selected_service_label]
    selected_service = SERVICE_BY_KEY[selected_service_id]
    selected_rows = catalog_rows_for_service(selected_service_id)

    operation_options = [str(row["operation"]) for row in selected_rows if row["operation"]]
    selected_operation = st.selectbox("Operation", operation_options)

    st.link_button("서비스키 신청/발급", selected_service.apply_url)
    st.caption(f"Manual: {selected_service.manual_url}")

    key_sources = {source.label: source.key for source in service_key_sources()}
    selected_key_source_label = st.selectbox("Service key source", list(key_sources))
    selected_key_source = key_sources[selected_key_source_label]
    default_key = resolve_service_key(source=selected_key_source) or ""
    service_key_input = st.text_input(
        "Service key",
        value=default_key,
        type="password",
        help=".env 또는 환경변수의 키를 기본값으로 읽고, 복붙 공백은 실행 전에 제거합니다.",
    )
    normalized_key = normalize_service_key(service_key_input)
    if service_key_input and normalized_key != service_key_input:
        st.caption("입력된 서비스키의 공백은 요청 전에 자동 제거됩니다.")

    timeout = st.number_input("Timeout seconds", min_value=1.0, max_value=120.0, value=10.0)
    num_of_rows = st.number_input("numOfRows", min_value=1, max_value=1000, value=10)
    page_no = st.number_input("pageNo", min_value=1, value=1)

selected_catalog_row = next(
    row
    for row in selected_rows
    if row["operation"] == selected_operation
)

st.subheader(selected_catalog_row["dataset_name"])
st.caption(selected_catalog_row["description"])

params_text = st.text_area(
    "Additional parameters as JSON",
    value="{}",
    height=140,
    help='예: {"keyword": "궁", "areaCode": "1"}',
)

run_clicked = st.button("Run", type="primary")
debug_trace: list[str] = [
    f"dataset={selected_catalog_row['dataset_name']}",
    f"service_id={selected_service_id}",
    f"service_name={selected_catalog_row['service_name']}",
    f"operation={selected_operation}",
    f"data_source={selected_catalog_row['data_source']}",
    f"service_key_source={selected_key_source}",
    f"service_key_apply_url={selected_catalog_row['service_key_apply_url']}",
]

result: Any = None
error: dict[str, Any] | None = None
request_params: dict[str, Any] = {}

if run_clicked:
    try:
        if not normalized_key:
            raise ValueError("Service key is required.")
        request_params = parse_params(params_text)
        hub = TourApiHubClient(
            normalized_key,
            timeout=float(timeout),
            service_key_source=selected_key_source,
        )
        result = hub.call(
            selected_service_id,
            selected_operation,
            params=request_params,
            page_no=int(page_no),
            num_of_rows=int(num_of_rows),
        )
        debug_trace.append(f"items={len(result.items)}")
        debug_trace.append(f"total_count={result.total_count}")
    except TourApiError as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "metadata": exc.metadata}
        debug_trace.append(f"error={type(exc).__name__}")
    except Exception as exc:  # noqa: BLE001 - debug UI must surface any input/runtime issue.
        error = {"type": type(exc).__name__, "message": str(exc)}
        debug_trace.append(f"error={type(exc).__name__}")

raw_tab, parsed_tab, processed_tab, error_tab, trace_tab, fixture_tab = st.tabs(
    [
        "Raw Response",
        "Pydantic Model",
        "Processed Result",
        "Validation Errors",
        "Debug Trace",
        "Fixture / Testcase",
    ]
)

with raw_tab:
    if result is not None:
        st.json(jsonable(result.raw))
    else:
        st.info("Run an API call to see the raw response.")

with parsed_tab:
    if result is not None:
        st.json(jsonable(result))
    else:
        st.info("Run an API call to see the parsed Pydantic result.")

with processed_tab:
    if result is not None:
        rows = [jsonable(item) for item in result.items]
        if rows:
            st.dataframe(pd.json_normalize(rows, sep="."))
        else:
            st.info("No items returned.")
    else:
        st.info("Run an API call to see processed rows.")

with error_tab:
    if error is not None:
        st.json(error)
    else:
        st.success("No error for the latest run.")

with trace_tab:
    st.write("Selected catalog item")
    st.json(selected_catalog_row)
    st.write("Service-key lookup")
    st.json(
        {
            "selected_source": selected_key_source,
            "env_names": service_key_env_names(selected_key_source),
            "loaded_from_env_or_dotenv": bool(default_key),
            "normalized": bool(normalized_key),
        }
    )
    st.write("Debug trace")
    st.code("\n".join(debug_trace), language="text")
    st.write("Catalog rows for selected dataset")
    st.dataframe(pd.DataFrame(dataframe_rows(selected_rows)))
    with st.expander("Full catalog"):
        st.dataframe(pd.DataFrame(dataframe_rows(list(catalog))))

with fixture_tab:
    st.info(
        "Fixture 저장은 후속 단계에서 연결합니다. "
        "현재 탭은 실행 결과를 확인한 뒤 저장 경계를 붙이기 위한 자리입니다."
    )
