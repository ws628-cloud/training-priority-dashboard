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

# 비용 대비 효과

# =========================================================

st.subheader(

    "💡 비용 대비 효과 매트릭스"

)


chart_df = fdf.copy()


chart_df["_버블크기"] = (

    chart_df["연간기대절감액(원)"]

    .fillna(0)

    .clip(lower=0)

)


use_bubble = (

    chart_df["_버블크기"].max()

    > 0

)


if use_bubble:


    fig1 = px.scatter(

        chart_df,

        x="예상비용(원)",

        y="예상효과수치(%)",

        size="_버블크기",

        color="시급성",

        hover_name="교육명",

        hover_data={

            "예상기간(일)": True,

            "ROI(배)": True,

            "대상부서": True,

            "_버블크기": False,

        },

        size_max=48,

        color_discrete_map={

            "상": "#e74c3c",

            "중": "#f39c12",

            "하": "#95a5a6",

        },

    )


else:


    fig1 = px.scatter(

        chart_df,

        x="예상비용(원)",

        y="예상효과수치(%)",

        color="시급성",

        hover_name="교육명",

        color_discrete_map={

            "상": "#e74c3c",

            "중": "#f39c12",

            "하": "#95a5a6",

        },

    )


fig1.update_layout(

    xaxis_title="예상 비용(원)",

    yaxis_title="예상 효과(%)",


    # 세로 PDF에 맞게 높이 축소

    height=360,


    autosize=True,


    margin=dict(

        l=45,

        r=15,

        t=15,

        b=45,

    ),


    legend=dict(

        orientation="h",

        yanchor="bottom",

        y=1.02,

        xanchor="left",

        x=0,

    ),

)


fig1.update_xaxes(

    tickformat=","

)


st.plotly_chart(

    fig1,

    use_container_width=True,

    config={

        "displayModeBar": False,

        "responsive": True,

    },

)


# =========================================================

# 우선순위 상위 교육

# =========================================================

st.subheader(

    "🏆 우선순위 상위 교육"

)


max_top_n = len(fdf)


if max_top_n <= 1:


    top_n = 1


else:


    top_n = st.slider(

        "표시할 상위 교육 수",

        min_value=1,

        max_value=max_top_n,

        value=min(

            5,

            max_top_n

        ),

        step=1,

    )


top_df = (

    fdf.sort_values(

        "우선순위점수",

        ascending=False,

    )

    .head(top_n)

    .copy()

)


fig2 = px.bar(

    top_df.sort_values(

        "우선순위점수"

    ),


    x="ROI(배)",

    y="교육명",


    orientation="h",


    color="시급성",


    text="ROI(배)",


    color_discrete_map={

        "상": "#e74c3c",

        "중": "#f39c12",

        "하": "#95a5a6",

    },

)


fig2.update_layout(

    xaxis_title="ROI(배)",

    yaxis_title="",


    height=max(

        280,

        48 * len(top_df),

    ),


    autosize=True,


    margin=dict(

        l=40,

        r=15,

        t=15,

        b=40,

    ),


    legend=dict(

        orientation="h",

        yanchor="bottom",

        y=1.02,

        xanchor="left",

        x=0,

    ),

)


fig2.update_traces(

    textposition="outside"

)


st.plotly_chart(

    fig2,

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

    # 강사 비교 차트

    # -----------------------------------------------------

    instructor_chart_df = idf.copy()


    if "대상인원수" in instructor_chart_df.columns:


        instructor_chart_df[

            "_대상인원버블"

        ] = (

            instructor_chart_df[

                "대상인원수"

            ]

            .fillna(1)

            .clip(lower=1)

        )


        fig3 = px.scatter(

            instructor_chart_df,


            x="사내강사전문성매칭점수",

            y="비용차이(외부-사내, 원)",


            color="추천강사유형",


            size="_대상인원버블",


            hover_name="교육명",


            size_max=40,


            color_discrete_map={

                "사내": "#2ecc71",

                "외부": "#3498db",

                "혼합": "#f1c40f",

                "미정": "#95a5a6",

            },

        )


    else:


        fig3 = px.scatter(

            instructor_chart_df,


            x="사내강사전문성매칭점수",

            y="비용차이(외부-사내, 원)",


            color="추천강사유형",


            hover_name="교육명",


            color_discrete_map={

                "사내": "#2ecc71",

                "외부": "#3498db",

                "혼합": "#f1c40f",

                "미정": "#95a5a6",

            },

        )


    fig3.add_vline(

        x=40,

        line_dash="dash",

        line_color="gray",

    )


    fig3.add_vline(

        x=70,

        line_dash="dash",

        line_color="gray",

    )


    fig3.add_hline(

        y=0,

        line_dash="dot",

        line_color="gray",

    )


    fig3.update_layout(

        xaxis_title="사내강사 전문성 매칭점수",

        yaxis_title="외부비용 - 사내비용",


        height=340,


        autosize=True,


        margin=dict(

            l=50,

            r=15,

            t=15,

            b=45,

        ),


        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="left",

            x=0,

        ),

    )


    fig3.update_yaxes(

        tickformat=","

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


    st.dataframe(

        instructor_table,

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


st.dataframe(

    detail_df,

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
