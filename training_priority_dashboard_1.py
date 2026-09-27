"""

교육 필요성 자동 탐색 & 경영진 의사결정 대시보드

------------------------------------------------

실행:

    py -m streamlit run training_priority_dashboard_1.py


필요 파일:

    training_needs_dummy_data_1.csv

"""


import pandas as pd

import numpy as np

import plotly.express as px

import streamlit as st


# =========================================================

# Streamlit 기본 설정

# =========================================================

st.set_page_config(

    page_title="교육 필요성 의사결정 대시보드",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)


# =========================================================

# 화면 + A4 세로 PDF 인쇄용 CSS

# =========================================================

st.markdown(

    """

<style>


/* =========================================================

   일반 화면

========================================================= */


html, body, [class*="css"] {

    font-family:

        "Malgun Gothic",

        "Apple SD Gothic Neo",

        "Noto Sans KR",

        Arial,

        sans-serif;

}


.block-container {

    max-width: 1400px !important;

    padding-top: 1.2rem !important;

    padding-left: 2rem !important;

    padding-right: 2rem !important;

    padding-bottom: 3rem !important;

}


h1 {

    margin-bottom: 0.4rem !important;

}


h2, h3 {

    margin-top: 0.8rem !important;

}


[data-testid="stMetric"] {

    padding: 0.2rem 0.2rem !important;

}


/* =========================================================

   A4 세로 PDF / 인쇄

========================================================= */


@media print {


    @page {

        size: A4 portrait;

        margin: 9mm;

    }


    html,

    body {

        width: 100% !important;

        height: auto !important;

        overflow: visible !important;

        background: white !important;

        font-size: 10pt !important;

    }


    /* -----------------------------------------------------

       Streamlit UI 제거

    ----------------------------------------------------- */


    header,

    footer,

    #MainMenu,

    [data-testid="stToolbar"],

    [data-testid="stDecoration"],

    [data-testid="stStatusWidget"],

    [data-testid="stHeader"] {

        display: none !important;

    }


    /* -----------------------------------------------------

       PDF에서는 사이드바 숨김

    ----------------------------------------------------- */


    section[data-testid="stSidebar"],

    [data-testid="stSidebar"] {

        display: none !important;

        width: 0 !important;

        min-width: 0 !important;

        max-width: 0 !important;

    }


    /* -----------------------------------------------------

       메인 화면 전체 폭 사용

    ----------------------------------------------------- */


    [data-testid="stAppViewContainer"],

    [data-testid="stMain"],

    [data-testid="stMainBlockContainer"],

    section.main,

    main {

        width: 100% !important;

        max-width: 100% !important;

        margin: 0 !important;

        padding: 0 !important;

        left: 0 !important;

    }


    .block-container {

        width: 100% !important;

        max-width: 100% !important;

        margin: 0 !important;

        padding: 0 !important;

    }


    /* -----------------------------------------------------

       제목 크기 축소

    ----------------------------------------------------- */


    h1 {

        font-size: 20pt !important;

        line-height: 1.2 !important;

        margin-top: 0 !important;

        margin-bottom: 6px !important;

    }


    h2 {

        font-size: 15pt !important;

        line-height: 1.2 !important;

    }


    h3 {

        font-size: 13pt !important;

        line-height: 1.2 !important;

    }


    p {

        font-size: 9.5pt !important;

    }


    /* -----------------------------------------------------

       KPI 영역

       화면에서는 4열,

       세로 PDF에서는 2열 x 2행

    ----------------------------------------------------- */


    [data-testid="stHorizontalBlock"] {

        display: flex !important;

        flex-wrap: wrap !important;

        width: 100% !important;

        gap: 8px !important;

    }


    [data-testid="column"] {

        min-width: 0 !important;

        width: calc(50% - 6px) !important;

        flex: 0 0 calc(50% - 6px) !important;

    }


    [data-testid="stMetric"] {

        padding: 4px !important;

        margin-bottom: 3px !important;

        break-inside: avoid !important;

        page-break-inside: avoid !important;

    }


    [data-testid="stMetricLabel"] {

        font-size: 9pt !important;

    }


    [data-testid="stMetricValue"] {

        font-size: 18pt !important;

    }


    /* -----------------------------------------------------

       Plotly 차트

    ----------------------------------------------------- */


    [data-testid="stPlotlyChart"],

    [data-testid="stPlotlyChart"] > div {

        width: 100% !important;

        max-width: 100% !important;

        overflow: visible !important;

    }


    [data-testid="stPlotlyChart"] {

        break-inside: avoid !important;

        page-break-inside: avoid !important;

        margin-bottom: 8px !important;

    }


    /* -----------------------------------------------------

       제목과 차트 분리 방지

    ----------------------------------------------------- */


    h1,

    h2,

    h3,

    h4,

    h5 {

        break-after: avoid !important;

        page-break-after: avoid !important;

    }


    /* -----------------------------------------------------

       표

    ----------------------------------------------------- */


    [data-testid="stDataFrame"] {

        width: 100% !important;

        max-width: 100% !important;

        overflow: hidden !important;

        break-inside: avoid !important;

        page-break-inside: avoid !important;

    }


    /* -----------------------------------------------------

       슬라이더 등 조작 UI는 PDF에서 숨김

    ----------------------------------------------------- */


    [data-testid="stSlider"] {

        display: none !important;

    }


    /* -----------------------------------------------------

       구분선 간격 줄임

    ----------------------------------------------------- */


    hr {

        margin-top: 6px !important;

        margin-bottom: 6px !important;

    }


    /* -----------------------------------------------------

       배경색 및 그래프 색상 유지

    ----------------------------------------------------- */


    * {

        -webkit-print-color-adjust: exact !important;

        print-color-adjust: exact !important;

    }

}


</style>

""",

    unsafe_allow_html=True,

)


# =========================================================

# 유틸 함수

# =========================================================

def clean_column_name(col):

    col = str(col)


    replacements = {

        "\ufeff": "",

        "\xa0": " ",

        "\n": "",

        "\r": "",

        "\t": "",

    }


    for old, new in replacements.items():

        col = col.replace(old, new)


    return col.strip()


def compact_column_name(col):

    return clean_column_name(col).replace(" ", "")


def find_column(df, candidates):


    # 정확한 이름 검색

    for candidate in candidates:

        if candidate in df.columns:

            return candidate


    # 공백 제거 후 비교

    compact_map = {

        compact_column_name(col): col

        for col in df.columns

    }


    for candidate in candidates:

        key = compact_column_name(candidate)


        if key in compact_map:

            return compact_map[key]


    return None


def safe_numeric(series):


    if pd.api.types.is_numeric_dtype(series):

        return pd.to_numeric(series, errors="coerce")


    cleaned = (

        series.astype(str)

        .str.replace(",", "", regex=False)

        .str.replace("원", "", regex=False)

        .str.replace("%", "", regex=False)

        .str.strip()

    )


    return pd.to_numeric(cleaned, errors="coerce")


def won_to_eok(value):


    if pd.isna(value):

        return "-"


    return f"{value / 100_000_000:.1f}억 원"


# =========================================================

# 데이터 로드

# =========================================================

@st.cache_data

def load_data():


    csv_path = "training_needs_dummy_data_1.csv"


    try:


        try:

            df = pd.read_csv(

                csv_path,

                encoding="utf-8-sig"

            )


        except UnicodeDecodeError:


            df = pd.read_csv(

                csv_path,

                encoding="cp949"

            )


    except FileNotFoundError:


        st.error(

            f"CSV 파일을 찾을 수 없습니다.\n\n"

            f"`{csv_path}` 파일을 Python 파일과 "

            f"같은 폴더에 넣어주세요."

        )


        st.stop()


    except Exception as e:


        st.error(

            f"CSV 파일을 읽는 중 오류가 발생했습니다.\n\n{e}"

        )


        st.stop()


    # -----------------------------------------------------

    # 컬럼명 정리

    # -----------------------------------------------------

    df.columns = [

        clean_column_name(c)

        for c in df.columns

    ]


    # -----------------------------------------------------

    # 컬럼명 자동 보정

    # -----------------------------------------------------

    aliases = {


        "대상부서": [

            "대상부서",

            "대상 부서",

        ],


        "시급성": [

            "시급성",

            "긴급도",

        ],


        "데이터출처유형": [

            "데이터출처유형",

            "데이터 출처유형",

            "데이터출처 유형",

            "데이터 출처 유형",

        ],


        "교육명": [

            "교육명",

            "교육 명",

            "교육과정명",

            "교육 과정명",

        ],


        "대상인원수": [

            "대상인원수",

            "대상 인원수",

            "대상인원",

            "대상 인원",

        ],


        "예상비용(원)": [

            "예상비용(원)",

            "예상 비용(원)",

            "예상비용",

            "예상 비용",

        ],


        "예상기간(일)": [

            "예상기간(일)",

            "예상 기간(일)",

            "예상기간",

        ],


        "예상효과유형": [

            "예상효과유형",

            "예상 효과유형",

            "예상 효과 유형",

        ],


        "예상효과수치(%)": [

            "예상효과수치(%)",

            "예상 효과수치(%)",

            "예상효과수치",

            "예상 효과 수치",

        ],


        "연간기대절감액(원)": [

            "연간기대절감액(원)",

            "연간 기대절감액(원)",

            "연간 기대 절감액(원)",

            "연간기대절감액",

        ],


        "우선순위점수": [

            "우선순위점수",

            "우선순위 점수",

        ],


        "근거요약": [

            "근거요약",

            "근거 요약",

        ],


        "사내강사보유여부": [

            "사내강사보유여부",

            "사내강사 보유여부",

            "사내 강사 보유 여부",

        ],


        "사내강사전문성매칭점수": [

            "사내강사전문성매칭점수",

            "사내강사 전문성매칭점수",

            "사내 강사 전문성 매칭점수",

        ],


        "사내강사활용시예상비용(원)": [

            "사내강사활용시예상비용(원)",

            "사내강사 활용시 예상비용(원)",

            "사내강사 활용 시 예상비용(원)",

            "사내 강사 활용 시 예상 비용(원)",

        ],


        "외부위탁시예상비용(원)": [

            "외부위탁시예상비용(원)",

            "외부위탁시 예상비용(원)",

            "외부위탁 시 예상비용(원)",

            "외부 위탁 시 예상 비용(원)",

        ],


        "추천강사유형": [

            "추천강사유형",

            "추천 강사유형",

            "추천 강사 유형",

        ],

    }


    rename_map = {}


    for standard_name, candidates in aliases.items():


        actual = find_column(

            df,

            candidates

        )


        if actual is not None and actual != standard_name:

            rename_map[actual] = standard_name


    if rename_map:

        df = df.rename(

            columns=rename_map

        )


    # -----------------------------------------------------

    # 숫자형 컬럼

    # -----------------------------------------------------

    numeric_cols = [

        "대상인원수",

        "예상비용(원)",

        "예상기간(일)",

        "예상효과수치(%)",

        "연간기대절감액(원)",

        "우선순위점수",

        "사내강사전문성매칭점수",

        "사내강사활용시예상비용(원)",

        "외부위탁시예상비용(원)",

    ]


    for col in numeric_cols:


        if col in df.columns:


            df[col] = safe_numeric(

                df[col]

            )


    # -----------------------------------------------------

    # ROI / 투자회수기간

    # -----------------------------------------------------

    if (

        "예상비용(원)" in df.columns

        and

        "연간기대절감액(원)" in df.columns

    ):


        df["ROI(배)"] = np.where(

            df["예상비용(원)"] > 0,


            df["연간기대절감액(원)"]

            /

            df["예상비용(원)"],


            np.nan,

        )


        df["ROI(배)"] = (

            df["ROI(배)"]

            .round(1)

        )


        df["투자회수기간(개월)"] = np.where(

            df["연간기대절감액(원)"] > 0,


            df["예상비용(원)"]

            /

            (

                df["연간기대절감액(원)"]

                /

                12

            ),


            np.nan,

        )


        df["투자회수기간(개월)"] = (

            df["투자회수기간(개월)"]

            .round(1)

        )


    return df


# =========================================================

# 데이터 로드

# =========================================================

df = load_data()


# =========================================================

# 필수 컬럼 검사

# =========================================================

required_cols = [

    "교육명",

    "대상부서",

    "시급성",

    "데이터출처유형",

    "예상비용(원)",

    "예상기간(일)",

    "예상효과수치(%)",

    "연간기대절감액(원)",

    "우선순위점수",

]


missing_required = [

    col

    for col in required_cols

    if col not in df.columns

]


if missing_required:


    st.error(

        "CSV 파일에 필요한 컬럼이 없습니다."

    )


    st.write("### 없는 컬럼")


    for col in missing_required:

        st.write(f"- `{col}`")


    st.write("### 현재 CSV 컬럼")


    st.code(

        "\n".join(

            df.columns.tolist()

        )

    )


    st.stop()


# =========================================================

# 제목

# =========================================================

st.title(

    "📊 현업 데이터 기반 교육 필요성 & 우선순위 대시보드"

)


# =========================================================

# 사이드바 필터

# =========================================================

st.sidebar.header("필터")


# 대상 부서

dept_options = sorted(

    df["대상부서"]

    .dropna()

    .astype(str)

    .unique()

    .tolist()

)


dept_sel = st.sidebar.multiselect(

    "대상 부서",

    dept_options,

    default=dept_options,

)


# 시급성

urgency_order = [

    "상",

    "중",

    "하",

]


actual_urgencies = (

    df["시급성"]

    .dropna()

    .astype(str)

    .unique()

    .tolist()

)


urgency_options = [

    x

    for x in urgency_order

    if x in actual_urgencies

]


for x in actual_urgencies:


    if x not in urgency_options:

        urgency_options.append(x)


urgency_sel = st.sidebar.multiselect(

    "시급성",

    urgency_options,

    default=urgency_options,

)


# 데이터 출처

source_options = sorted(

    df["데이터출처유형"]

    .dropna()

    .astype(str)

    .unique()

    .tolist()

)


source_sel = st.sidebar.multiselect(

    "데이터 출처유형",

    source_options,

    default=source_options,

)


# =========================================================

# 필터 적용

# =========================================================

fdf = df[

    df["대상부서"]

    .astype(str)

    .isin(dept_sel)


    &


    df["시급성"]

    .astype(str)

    .isin(urgency_sel)


    &


    df["데이터출처유형"]

    .astype(str)

    .isin(source_sel)

].copy()


if fdf.empty:


    st.warning(

        "선택한 조건에 해당하는 교육 후보가 없습니다."

    )


    st.stop()


# =========================================================

# 핵심 KPI

# =========================================================

c1, c2, c3, c4 = st.columns(4)


total_budget = (

    fdf["예상비용(원)"]

    .sum()

)


total_savings = (

    fdf["연간기대절감액(원)"]

    .sum()

)


avg_roi = (

    fdf["ROI(배)"].mean()

    if "ROI(배)" in fdf.columns

    else np.nan

)


with c1:


    st.metric(

        "교육 후보 수",

        f"{len(fdf):,}건"

    )


with c2:


    st.metric(

        "총 소요 예산",

        won_to_eok(

            total_budget

        )

    )


with c3:


    st.metric(

        "연간 기대 절감액",

        won_to_eok(

            total_savings

        )

    )


with c4:


    roi_text = (

        f"{avg_roi:.1f}배"

        if pd.notna(avg_roi)

        else "-"

    )


    st.metric(

        "평균 ROI",

        roi_text

    )


st.divider()


# =========================================================

# 비용 대비 효과 분석 (4분면 Pay-Off Matrix)

# =========================================================

st.subheader("💡 비용 대비 효과 분석 (Pay-Off Matrix)")

payoff_df = fdf.copy()

# 4분면 기준선은 현재 필터 결과의 중앙값을 사용합니다.
x_mid = float(payoff_df["예상비용(원)"].median())
y_mid = float(payoff_df["연간기대절감액(원)"].median())

def classify_quadrant(cost, saving):
    if cost <= x_mid and saving >= y_mid:
        return "Quick Win"
    if cost > x_mid and saving >= y_mid:
        return "Major Project"
    if cost <= x_mid and saving < y_mid:
        return "Fill-ins"
    return "재검토 필요"

payoff_df["사분면"] = payoff_df.apply(
    lambda row: classify_quadrant(
        row["예상비용(원)"],
        row["연간기대절감액(원)"],
    ),
    axis=1,
)

fig1 = px.scatter(
    payoff_df,
    x="예상비용(원)",
    y="연간기대절감액(원)",
    color="시급성",
    size="우선순위점수",
    hover_name="교육명",
    hover_data={
        "대상부서": True,
        "예상비용(원)": ":,.0f",
        "연간기대절감액(원)": ":,.0f",
        "ROI(배)": ":.1f",
        "우선순위점수": ":.0f",
        "사분면": True,
    },
    size_max=34,
    color_discrete_map={
        "상": "#e74c3c",
        "중": "#f39c12",
        "하": "#95a5a6",
    },
)

# 중앙값 기준 4분면선
fig1.add_vline(
    x=x_mid,
    line_width=1.5,
    line_dash="dash",
    line_color="gray",
)

fig1.add_hline(
    y=y_mid,
    line_width=1.5,
    line_dash="dash",
    line_color="gray",
)

# 사분면 라벨 배치를 위한 축 범위 계산
x_min = float(payoff_df["예상비용(원)"].min())
x_max = float(payoff_df["예상비용(원)"].max())
y_min = float(payoff_df["연간기대절감액(원)"].min())
y_max = float(payoff_df["연간기대절감액(원)"].max())

x_pad = max((x_max - x_min) * 0.08, 1.0)
y_pad = max((y_max - y_min) * 0.10, 1.0)

plot_x_min = max(0.0, x_min - x_pad)
plot_x_max = x_max + x_pad
plot_y_min = max(0.0, y_min - y_pad)
plot_y_max = y_max + y_pad

x_left_label = plot_x_min + (x_mid - plot_x_min) * 0.07
x_right_label = x_mid + (plot_x_max - x_mid) * 0.07
y_top_label = y_mid + (plot_y_max - y_mid) * 0.86
y_bottom_label = plot_y_min + (y_mid - plot_y_min) * 0.12

quadrant_annotations = [
    (x_left_label, y_top_label, "① Quick Win<br>저비용 · 고효과"),
    (x_right_label, y_top_label, "② Major Project<br>고비용 · 고효과"),
    (x_left_label, y_bottom_label, "③ Fill-ins<br>저비용 · 저효과"),
    (x_right_label, y_bottom_label, "④ 재검토 필요<br>고비용 · 저효과"),
]

for x_pos, y_pos, label in quadrant_annotations:
    fig1.add_annotation(
        x=x_pos,
        y=y_pos,
        text=label,
        showarrow=False,
        align="left",
        xanchor="left",
        font=dict(size=11, color="#34495e"),
        bgcolor="rgba(255,255,255,0.78)",
        bordercolor="rgba(180,180,180,0.35)",
        borderwidth=1,
        borderpad=4,
    )

fig1.update_layout(
    xaxis_title="예상 투자비용 (원)",
    yaxis_title="연간 기대절감액 (원)",
    height=500,
    autosize=True,
    margin=dict(
        l=60,
        r=30,
        t=35,
        b=55,
    ),
    legend=dict(
        title="시급성",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
)

fig1.update_xaxes(
    tickformat=",",
    range=[plot_x_min, plot_x_max],
)

fig1.update_yaxes(
    tickformat=",",
    range=[plot_y_min, plot_y_max],
)

st.plotly_chart(
    fig1,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
    },
)

st.markdown("#### 💡 사분면별 의사결정 가이드")

q1, q2, q3, q4 = st.columns(4)

with q1:
    st.markdown(
        "**① Quick Win**  \n"
        "저비용 · 고효과  \n"
        "→ 우선 검토 및 빠른 실행"
    )

with q2:
    st.markdown(
        "**② Major Project**  \n"
        "고비용 · 고효과  \n"
        "→ 예산 확보 후 전략적 추진"
    )

with q3:
    st.markdown(
        "**③ Fill-ins**  \n"
        "저비용 · 저효과  \n"
        "→ 여유 자원 범위 내 보완"
    )

with q4:
    st.markdown(
        "**④ 재검토 필요**  \n"
        "고비용 · 저효과  \n"
        "→ 대상·방식·범위 재설계"
    )

st.divider()

# =========================================================

# 우선순위 상위 교육

# =========================================================

st.subheader(
    "🏆 우선순위 상위 교육"
)

top_n = min(5, len(fdf))

# 이 영역은 ROI가 아니라 종합 우선순위점수를 사용하여
# 앞의 비용 대비 효과 차트와 역할이 겹치지 않도록 구성
# ---------------------------------------------------------

top_df = (
    fdf.sort_values(
        "우선순위점수",
        ascending=False,
    )
    .head(top_n)
    .copy()
)

fig_priority = px.bar(
    top_df.sort_values(
        "우선순위점수",
        ascending=True,
    ),
    x="우선순위점수",
    y="교육명",
    orientation="h",
    color="시급성",
    text="우선순위점수",
    hover_data={
        "ROI(배)": ":.1f",
        "예상비용(원)": ":,.0f",
        "연간기대절감액(원)": ":,.0f",
    },
    color_discrete_map={
        "상": "#e74c3c",
        "중": "#f39c12",
        "하": "#95a5a6",
    },
)

fig_priority.update_traces(
    texttemplate="%{x:.0f}점",
    textposition="outside",
    cliponaxis=False,
)

fig_priority.update_layout(
    xaxis_title="우선순위점수 (점)",
    yaxis_title="",
    height=max(
        280,
        50 * len(top_df),
    ),
    autosize=True,
    margin=dict(
        l=40,
        r=60,
        t=15,
        b=40,
    ),
    legend=dict(
        title="시급성",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
)

fig_priority.update_xaxes(
    tickformat=".0f",
    rangemode="tozero",
)

st.plotly_chart(
    fig_priority,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
    },
)

st.divider()

# =========================================================

# 사내강사 vs 외부기관

# =========================================================

st.subheader(

    "👩‍🏫 사내강사 vs 외부기관 선별"

)


instructor_cols = [

    "사내강사전문성매칭점수",

    "사내강사활용시예상비용(원)",

    "외부위탁시예상비용(원)",

]


missing_instructor_cols = [

    col

    for col in instructor_cols

    if col not in fdf.columns

]


if missing_instructor_cols:


    st.info(

        "강사 선별 비교에 필요한 컬럼이 없어 "

        "이 영역은 자동으로 생략되었습니다."

    )


else:


    idf = fdf.copy()


    # -----------------------------------------------------

    # 추천 강사유형 자동 생성

    # -----------------------------------------------------

    if "추천강사유형" not in idf.columns:


        def recommend_instructor(score):


            if pd.isna(score):

                return "미정"


            if score >= 70:

                return "사내"


            elif score < 40:

                return "외부"


            else:

                return "혼합"


        idf["추천강사유형"] = (

            idf[

                "사내강사전문성매칭점수"

            ]

            .apply(

                recommend_instructor

            )

        )


    if "사내강사보유여부" not in idf.columns:


        idf[

            "사내강사보유여부"

        ] = "-"


    # -----------------------------------------------------

    # 비용 차이 계산

    # -----------------------------------------------------

    idf[

        "비용차이(외부-사내, 원)"

    ] = (

        idf[

            "외부위탁시예상비용(원)"

        ]

        -

        idf[

            "사내강사활용시예상비용(원)"

        ]

    )


    col_a, col_b = st.columns(2)


    with col_a:


        internal_count = (

            idf[

                "추천강사유형"

            ]

            .astype(str)

            .eq("사내")

            .sum()

        )


        st.metric(

            "사내강사 활용 권장",

            f"{internal_count:,}건"

        )


    with col_b:


        total_internal_saving = (

            idf[

                "비용차이(외부-사내, 원)"

            ]

            .clip(lower=0)

            .sum()

        )


        st.metric(

            "사내 활용 시 절감 예상액",

            won_to_eok(

                total_internal_saving

            )

        )


    # -----------------------------------------------------

    # 사내강사 vs 외부위탁 비용 비교 차트

    # -----------------------------------------------------

    compare_df = idf[

        [

            "교육명",

            "사내강사활용시예상비용(원)",

            "외부위탁시예상비용(원)",

            "추천강사유형",

            "사내강사전문성매칭점수",

        ]

    ].copy()


    # 전문성 매칭점수가 높은 교육부터 정렬

    compare_df = compare_df.sort_values(

        "사내강사전문성매칭점수",

        ascending=False,

    )


    compare_long = compare_df.melt(

        id_vars=[

            "교육명",

            "추천강사유형",

            "사내강사전문성매칭점수",

        ],

        value_vars=[

            "사내강사활용시예상비용(원)",

            "외부위탁시예상비용(원)",

        ],

        var_name="비용유형",

        value_name="비용(원)",

    )


    compare_long["비용유형"] = compare_long["비용유형"].replace(

        {

            "사내강사활용시예상비용(원)": "사내강사",

            "외부위탁시예상비용(원)": "외부위탁",

        }

    )


    fig3 = px.bar(

        compare_long,

        x="비용(원)",

        y="교육명",

        color="비용유형",

        barmode="group",

        orientation="h",

        text="비용(원)",

        hover_data={

            "사내강사전문성매칭점수": True,

            "추천강사유형": True,

            "비용(원)": ":,.0f",

        },

        category_orders={

            "교육명": compare_df["교육명"].tolist(),

            "비용유형": ["사내강사", "외부위탁"],

        },

        color_discrete_map={

            "사내강사": "#2ecc71",

            "외부위탁": "#3498db",

        },

    )


    fig3.update_traces(

        texttemplate="%{x:,.0f}원",

        textposition="outside",

        cliponaxis=False,

    )


    fig3.update_layout(

        xaxis_title="예상 비용 (원)",

        yaxis_title="",

        height=max(

            420,

            52 * compare_df["교육명"].nunique(),

        ),

        autosize=True,

        margin=dict(

            l=40,

            r=110,

            t=20,

            b=40,

        ),

        legend=dict(

            title="비용 구분",

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="left",

            x=0,

        ),

    )


    fig3.update_xaxes(

        tickformat=",",

    )


    st.plotly_chart(

        fig3,

        use_container_width=True,

        config={

            "displayModeBar": False,

            "responsive": True,

        },

    )


    # -----------------------------------------------------

    # 강사 비교 표

    # -----------------------------------------------------

    instructor_table_cols = [

        "교육명",

        "사내강사전문성매칭점수",

        "사내강사활용시예상비용(원)",

        "외부위탁시예상비용(원)",

        "비용차이(외부-사내, 원)",

        "추천강사유형",

    ]


    instructor_table_cols = [

        col

        for col in instructor_table_cols

        if col in idf.columns

    ]


    instructor_table = (

        idf[

            instructor_table_cols

        ]

        .sort_values(

            "사내강사전문성매칭점수",

            ascending=False,

        )

        .reset_index(

            drop=True

        )

    )


    instructor_table_display = instructor_table.copy()


    instructor_money_cols = [

        "사내강사활용시예상비용(원)",

        "외부위탁시예상비용(원)",

        "비용차이(외부-사내, 원)",

    ]


    for col in instructor_money_cols:

        if col in instructor_table_display.columns:

            instructor_table_display[col] = instructor_table_display[col].apply(

                lambda x: f"{x:,.0f}" if pd.notna(x) else "-"

            )


    st.dataframe(

        instructor_table_display,

        use_container_width=True,

        height=240,

        hide_index=True,

    )


st.divider()


# =========================================================

# 교육 후보 상세 데이터

# =========================================================

st.subheader(

    "📋 교육 후보 상세 데이터"

)


desired_show_cols = [

    "교육명",

    "데이터출처유형",

    "대상부서",

    "대상인원수",

    "예상비용(원)",

    "예상기간(일)",

    "예상효과수치(%)",

    "연간기대절감액(원)",

    "ROI(배)",

    "시급성",

    "우선순위점수",

]


show_cols = [

    col

    for col in desired_show_cols

    if col in fdf.columns

]


detail_df = (

    fdf[

        show_cols

    ]

    .sort_values(

        "우선순위점수",

        ascending=False,

    )

    .reset_index(

        drop=True

    )

)


detail_df_display = detail_df.copy()


detail_money_cols = [

    "예상비용(원)",

    "연간기대절감액(원)",

]


for col in detail_money_cols:

    if col in detail_df_display.columns:

        detail_df_display[col] = detail_df_display[col].apply(

            lambda x: f"{x:,.0f}" if pd.notna(x) else "-"

        )


st.dataframe(

    detail_df_display,

    use_container_width=True,

    height=280,

    hide_index=True,

)


# =========================================================

# 경영진 자동 요약

# =========================================================

st.subheader(

    "📝 경영진 보고용 자동 요약"

)


best = (

    fdf.sort_values(

        "우선순위점수",

        ascending=False,

    )

    .iloc[0]

)


education_name = best.get(

    "교육명",

    "-"

)


reason = best.get(

    "근거요약",

    "근거 데이터 확인 필요"

)


cost = best.get(

    "예상비용(원)",

    np.nan

)


days = best.get(

    "예상기간(일)",

    np.nan

)


effect_type = best.get(

    "예상효과유형",

    "예상 효과"

)


effect_value = best.get(

    "예상효과수치(%)",

    np.nan

)


saving = best.get(

    "연간기대절감액(원)",

    np.nan

)


roi = best.get(

    "ROI(배)",

    np.nan

)


payback = best.get(

    "투자회수기간(개월)",

    np.nan

)


cost_text = (

    f"{cost / 100_000_000:.2f}억 원"

    if pd.notna(cost)

    else "-"

)


days_text = (

    f"{days:g}일"

    if pd.notna(days)

    else "-"

)


effect_text = (

    f"{effect_value:g}%"

    if pd.notna(effect_value)

    else "-"

)


saving_text = (

    f"{saving / 100_000_000:.2f}억 원"

    if pd.notna(saving)

    else "-"

)


roi_text = (

    f"{roi:.1f}배"

    if pd.notna(roi)

    else "-"

)


payback_text = (

    f"{payback:.1f}개월"

    if pd.notna(payback)

    else "-"

)


st.info(

    f"""

**최우선 추천: {education_name}**


- **근거:** {reason}

- **예상 비용:** {cost_text}

- **예상 기간:** {days_text}

- **기대 효과:** {effect_type} {effect_text}

- **연간 기대 절감액:** {saving_text}

- **ROI:** {roi_text}

- **투자 회수기간:** {payback_text}

"""

)
