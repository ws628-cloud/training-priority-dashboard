# -*- coding: utf-8 -*-
"""
동아ST 경영관리부문 HRD 포트폴리오
경영진 보고용 교육 투자 의사결정 대시보드

실행 방법:
    pip install -r requirements.txt
    streamlit run app.py

데이터 출처: training_candidates.csv (더미데이터 - 임직원 설문 미포함,
GMP/규제감사, MR·CRM, R&D 이슈로그, QC/QA 리포트, 컴플라이언스 이수율,
신제품 역량갭, 경쟁사 벤치마킹 등 현업 데이터 기반으로 구성)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------------
st.set_page_config(
    page_title="동아ST HRD 교육투자 의사결정 대시보드",
    page_icon="📊",
    layout="wide",
)

URGENCY_W, ROI_W, RISK_W = 0.4, 0.3, 0.3  # 시급성 40% + ROI 30% + 규제·컴플라이언스 리스크 30%


@st.cache_data
def load_data(path: str = "training_candidates.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["우선순위점수"] = (
        df["시급성점수"] * URGENCY_W + df["ROI점수"] * ROI_W + df["리스크점수"] * RISK_W
    ).round(2)
    df["투자회수기간_개월"] = (df["예상비용_원"] / (df["연간기대절감액_원"] / 12)).round(1)
    df["연간ROI_퍼센트"] = (
        (df["연간기대절감액_원"] - df["예상비용_원"]) / df["예상비용_원"] * 100
    ).round(0)
    df["운영형태"] = df["강사구분"].apply(
        lambda x: "사내강사 운영 가능" if str(x).startswith("내부") else "외부기관 위탁 필요"
    )
    df = df.sort_values("우선순위점수", ascending=False).reset_index(drop=True)
    df.insert(0, "우선순위", df.index + 1)
    return df


df_all = load_data()

# ------------------------------------------------------------------
# 헤더
# ------------------------------------------------------------------
st.title("📊 동아ST 경영관리부문 교육(HRD) 투자 의사결정 대시보드")
st.caption(
    "우선순위 산정 공식 : 시급성 40% + ROI 30% + 규제·컴플라이언스 리스크 30% · "
    "데이터 출처 : GMP/규제감사, MR·CRM, R&D 이슈로그, QC/QA 리포트, 컴플라이언스 이수율, "
    "신제품 역량갭, 경쟁사 벤치마킹 (임직원 설문 미포함)"
)

# ------------------------------------------------------------------
# 사이드바 필터
# ------------------------------------------------------------------
st.sidebar.header("🔎 필터")

dept_options = sorted(df_all["대상부서"].unique())
selected_depts = st.sidebar.multiselect("대상부서", dept_options, default=dept_options)

op_options = sorted(df_all["운영형태"].unique())
selected_op = st.sidebar.multiselect("운영형태", op_options, default=op_options)

urgency_min, urgency_max = st.sidebar.slider(
    "시급성 점수 범위", 0.0, 10.0, (0.0, 10.0), 0.5
)

df = df_all[
    df_all["대상부서"].isin(selected_depts)
    & df_all["운영형태"].isin(selected_op)
    & df_all["시급성점수"].between(urgency_min, urgency_max)
].copy()

if df.empty:
    st.warning("선택한 조건에 해당하는 교육 후보가 없습니다. 필터를 조정해주세요.")
    st.stop()

# ------------------------------------------------------------------
# 상단 KPI
# ------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("검토 대상 교육 수", f"{len(df)}건")
col2.metric("총 예상비용", f"{df['예상비용_원'].sum()/1e8:,.1f}억원")
col3.metric("총 연간기대절감액", f"{df['연간기대절감액_원'].sum()/1e8:,.1f}억원")
avg_payback = df["투자회수기간_개월"].mean()
col4.metric("평균 투자회수기간", f"{avg_payback:,.1f}개월")

st.divider()

# ------------------------------------------------------------------
# 비용 x 효과 버블차트
# ------------------------------------------------------------------
st.subheader("💰 비용 × 효과 버블차트")
st.caption("버블 크기 = 연간기대절감액 · 색상 = 운영형태")

fig_bubble = px.scatter(
    df,
    x="예상비용_원",
    y="연간ROI_퍼센트",
    size="연간기대절감액_원",
    color="운영형태",
    text="교육명",
    hover_data={
        "교육명": True,
        "대상부서": True,
        "예상비용_원": ":,.0f",
        "연간기대절감액_원": ":,.0f",
        "투자회수기간_개월": ":.1f",
        "우선순위점수": True,
    },
    color_discrete_map={
        "사내강사 운영 가능": "#2E86AB",
        "외부기관 위탁 필요": "#E07A5F",
    },
    size_max=55,
)
fig_bubble.update_traces(textposition="top center")
fig_bubble.update_layout(
    xaxis_title="예상비용 (원)",
    yaxis_title="연간 ROI (%)",
    height=520,
)
st.plotly_chart(fig_bubble, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# 우선순위 랭킹
# ------------------------------------------------------------------
left, right = st.columns([1.3, 1])

with left:
    st.subheader("🏆 우선순위 랭킹")
    fig_rank = px.bar(
        df.sort_values("우선순위점수"),
        x="우선순위점수",
        y="교육명",
        orientation="h",
        color="운영형태",
        color_discrete_map={
            "사내강사 운영 가능": "#2E86AB",
            "외부기관 위탁 필요": "#E07A5F",
        },
        text="우선순위점수",
    )
    fig_rank.update_layout(height=450, yaxis_title="", xaxis_title="우선순위 점수(10점 만점)")
    st.plotly_chart(fig_rank, use_container_width=True)

with right:
    st.subheader("⚖️ 운영형태 비중")
    fig_pie = px.pie(
        df,
        names="운영형태",
        values="대상인원",
        color="운영형태",
        color_discrete_map={
            "사내강사 운영 가능": "#2E86AB",
            "외부기관 위탁 필요": "#E07A5F",
        },
        hole=0.45,
    )
    fig_pie.update_layout(height=450, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# ROI / 투자회수기간 상세 테이블
# ------------------------------------------------------------------
st.subheader("📋 교육 후보 상세 (ROI · 투자회수기간)")

display_cols = [
    "우선순위",
    "교육명",
    "데이터출처유형",
    "대상부서",
    "대상인원",
    "예상비용_원",
    "예상기간_주",
    "연간기대절감액_원",
    "연간ROI_퍼센트",
    "투자회수기간_개월",
    "운영형태",
    "우선순위점수",
]
st.dataframe(
    df[display_cols].style.format(
        {
            "예상비용_원": "{:,.0f}",
            "연간기대절감액_원": "{:,.0f}",
            "연간ROI_퍼센트": "{:.0f}%",
            "투자회수기간_개월": "{:.1f}개월",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

with st.expander("📌 근거 데이터(수치) 및 기대효과 상세 보기"):
    st.dataframe(
        df[["교육명", "근거수치", "기대효과유형", "기대효과수치", "강사구분"]],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "⚠ 본 대시보드의 수치는 지원 포트폴리오 목적의 더미데이터이며, "
    "실제 동아ST의 경영 데이터가 아닙니다."
)
