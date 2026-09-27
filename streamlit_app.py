import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="더미데이터 대시보드", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("dummy_sales_data.csv", parse_dates=["날짜"])

df = load_data()

st.title("📊 더미 판매 데이터 대시보드")

# 사이드바 필터
st.sidebar.header("필터")
regions = st.sidebar.multiselect("지역 선택", df["지역"].unique(), default=df["지역"].unique())
categories = st.sidebar.multiselect("카테고리 선택", df["카테고리"].unique(), default=df["카테고리"].unique())

filtered = df[df["지역"].isin(regions) & df["카테고리"].isin(categories)]

# 주요 지표
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 매출", f"{filtered['매출'].sum():,.0f}원")
col2.metric("총 이익", f"{filtered['이익'].sum():,.0f}원")
col3.metric("주문 건수", f"{len(filtered):,}건")
col4.metric("평균 평점", f"{filtered['평점'].mean():.2f}")

st.divider()

# 차트
c1, c2 = st.columns(2)
with c1:
    st.subheader("카테고리별 매출")
    cat_sales = filtered.groupby("카테고리")["매출"].sum().reset_index()
    fig1 = px.bar(cat_sales, x="카테고리", y="매출", color="카테고리")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("지역별 매출 비중")
    region_sales = filtered.groupby("지역")["매출"].sum().reset_index()
    fig2 = px.pie(region_sales, names="지역", values="매출")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("일자별 매출 추이")
daily = filtered.groupby("날짜")["매출"].sum().reset_index()
fig3 = px.line(daily, x="날짜", y="매출")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("데이터 미리보기")
st.dataframe(filtered, use_container_width=True)
