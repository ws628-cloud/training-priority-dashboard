"""
교육 필요성 자동 탐색 & 경영진 의사결정 대시보드
------------------------------------------------
- 데이터 소스: 임직원 설문이 아닌 '현업 데이터'(프로젝트 이슈로그, 헬프데스크 티켓,
  품질 리포트, CS클레임, 감사지적사항, 채용공고/벤치마킹, KPI 미달 텍스트마이닝 등)
  에서 도출된 교육 후보 더미 데이터를 사용합니다.
- 실행 방법: streamlit run training_priority_dashboard.py
- 같은 폴더에 training_needs_dummy_data.csv 가 있어야 합니다.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="교육 필요성 의사결정 대시보드", layout="wide")

# ---------- 데이터 로드 ----------
@st.cache_data
def load_data():
    df = pd.read_csv("training_needs_dummy_data.csv")
    df["ROI(배)"] = (df["연간기대절감액(원)"] / df["예상비용(원)"]).round(1)
    df["투자회수기간(개월)"] = (df["예상비용(원)"] / (df["연간기대절감액(원)"] / 12)).round(1)
    return df

df = load_data()

st.title("📊 현업 데이터 기반 교육 필요성 & 우선순위 대시보드")
st.caption("데이터 출처: 임직원 설문 제외 · 프로젝트 이슈로그 / 헬프데스크 티켓 / 품질리포트 / CS클레임 / 감사지적 / 채용공고벤치마킹 / KPI 텍스트마이닝")

# ---------- 사이드바 필터 ----------
st.sidebar.header("필터")
dept_sel = st.sidebar.multiselect("대상 부서", sorted(df["대상부서"].unique()), default=list(df["대상부서"].unique()))
urgency_sel = st.sidebar.multiselect("시급성", ["상", "중", "하"], default=["상", "중", "하"])
source_sel = st.sidebar.multiselect("데이터 출처유형", sorted(df["데이터출처유형"].unique()), default=list(df["데이터출처유형"].unique()))

fdf = df[
    df["대상부서"].isin(dept_sel)
    & df["시급성"].isin(urgency_sel)
    & df["데이터출처유형"].isin(source_sel)
]

if fdf.empty:
    st.warning("선택한 조건에 해당하는 교육 후보가 없습니다.")
    st.stop()

# ---------- 핵심 지표(경영진 요약) ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("교육 후보 수", f"{len(fdf)}건")
c2.metric("총 소요 예산", f"{fdf['예상비용(원)'].sum()/1e8:.1f}억 원")
c3.metric("연간 기대 절감액 합계", f"{fdf['연간기대절감액(원)'].sum()/1e8:.1f}억 원")
c4.metric("평균 ROI", f"{fdf['ROI(배)'].mean():.1f}배")

st.divider()

# ---------- 버블차트: 비용 vs 효과, 크기=절감액, 색=시급성 ----------
st.subheader("💡 비용 대비 효과 매트릭스 (버블 크기 = 연간 기대 절감액)")
fig1 = px.scatter(
    fdf,
    x="예상비용(원)",
    y="예상효과수치(%)",
    size="연간기대절감액(원)",
    color="시급성",
    hover_name="교육명",
    hover_data={"예상기간(일)": True, "ROI(배)": True, "대상부서": True},
    size_max=60,
    color_discrete_map={"상": "#e74c3c", "중": "#f39c12", "하": "#95a5a6"},
)
fig1.update_layout(xaxis_title="예상 비용(원)", yaxis_title="예상 효과(%)", height=480)
st.plotly_chart(fig1, use_container_width=True)

# ---------- 우선순위 Top N: 비용/기간/효과 비교 ----------
st.subheader("🏆 우선순위 상위 교육 - 비용/기간/효과 비교")
top_n = st.slider("표시할 상위 교육 수", 3, len(fdf), min(5, len(fdf)))
top_df = fdf.sort_values("우선순위점수", ascending=False).head(top_n)

fig2 = px.bar(
    top_df.sort_values("우선순위점수"),
    x="ROI(배)",
    y="교육명",
    orientation="h",
    color="시급성",
    text="ROI(배)",
    color_discrete_map={"상": "#e74c3c", "중": "#f39c12", "하": "#95a5a6"},
    hover_data=["예상비용(원)", "예상기간(일)", "예상효과수치(%)", "투자회수기간(개월)"],
)
fig2.update_layout(xaxis_title="ROI(배) = 연간절감액 ÷ 비용", yaxis_title="", height=400)
st.plotly_chart(fig2, use_container_width=True)

# ---------- 상세 테이블 ----------
st.subheader("📋 교육 후보 상세 데이터")
show_cols = [
    "교육명", "데이터출처유형", "대상부서", "대상인원수", "예상비용(원)",
    "예상기간(일)", "예상효과유형", "예상효과수치(%)", "연간기대절감액(원)",
    "ROI(배)", "투자회수기간(개월)", "시급성", "우선순위점수", "근거요약",
]
st.dataframe(
    fdf[show_cols].sort_values("우선순위점수", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=350,
)

# ---------- 경영진용 자동 요약 ----------
st.subheader("📝 경영진 보고용 자동 요약")
best = fdf.sort_values("우선순위점수", ascending=False).iloc[0]
st.info(
    f"**최우선 추천: {best['교육명']}**  \n"
    f"- 근거: {best['근거요약']}  \n"
    f"- 예상 비용 {best['예상비용(원)']/1e8:.2f}억 원 / 기간 {best['예상기간(일)']}일  \n"
    f"- 기대 효과: {best['예상효과유형']} {best['예상효과수치(%)']}%  \n"
    f"- 연간 기대 절감액 {best['연간기대절감액(원)']/1e8:.2f}억 원 (ROI {best['ROI(배)']}배, "
    f"투자회수 {best['투자회수기간(개월)']}개월)"
)
