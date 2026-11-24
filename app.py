# ===== 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px


# ===== 페이지 설정 =====
# [추가] 페이지 제목과 넓은 화면 배치 설정 (가장 먼저 실행되는 st 명령)
st.set_page_config(page_title="Titanic 대시보드", layout="wide")


# ===== 데이터 불러오기 =====
# st.cache_data: 처음 한 번만 파일을 읽고, 그다음부터는 저장해 둔 결과를 재사용
@st.cache_data
def load_data():
    # titanic.csv 파일을 읽어서 반환
    return pd.read_csv("titanic.csv")


# ===== 함수 정의 =====
# 조건에 맞는 승객만 골라내는 함수
def filter_data(df, sexes, classes, age_range):
    # 나이 범위에서 최소값과 최대값 꺼내기
    min_age, max_age = age_range

    # 조건 1: 성별이 sexes 목록에 포함된 행
    cond_sex = df["sex"].isin(sexes)

    # 조건 2: 객실 등급(pclass)이 classes 목록에 포함된 행
    cond_class = df["pclass"].isin(classes)

    # 조건 3: 나이가 최소~최대 범위 안에 있는 행 (양 끝 포함)
    cond_age = df["age"].between(min_age, max_age)

    # 세 조건을 모두 만족하는 행만 반환
    return df[cond_sex & cond_class & cond_age]


# 대시보드 상단 숫자 카드에 쓸 KPI 계산 함수
def kpi(df):
    # 데이터가 비어 있으면 (0, 0, 0) 반환
    if df.empty:
        return (0, 0, 0)

    # 승객 수: 행의 개수
    count = len(df)

    # 생존율(%): survived(0/1)의 평균에 100을 곱하고 소수 첫째 자리로 반올림
    survival_rate = round(df["survived"].mean() * 100, 1)

    # 평균 나이: 결측치를 빼고 평균을 내서 소수 첫째 자리로 반올림
    avg_age = round(df["age"].mean(), 1)

    # 세 값을 함께 반환
    return (count, survival_rate, avg_age)


# 객실 등급별 생존율(%) 막대그래프를 만드는 함수
def class_rate_bar(df):
    # 등급별 생존율을 계산하고 %로 바꿔 소수 첫째 자리로 반올림
    rate = (df.groupby("pclass")["survived"].mean() * 100).round(1).reset_index()

    # 열 이름을 알아보기 쉽게 바꾸기
    rate.columns = ["객실등급", "생존율(%)"]

    # 등급을 문자로 바꿔서 x축이 1, 2, 3 세 칸으로만 나오게 하기
    rate["객실등급"] = rate["객실등급"].astype(str) + "등급"

    # 막대그래프 그리기, 막대 위에 생존율 값 표시
    fig = px.bar(rate, x="객실등급", y="생존율(%)",
                 text="생존율(%)", title="객실 등급별 생존율")

    # 막대 바깥 위쪽에 값 표시
    fig.update_traces(textposition="outside")

    # 완성된 그래프 반환
    return fig


# 생존 여부별 나이 히스토그램을 만드는 함수
def age_hist(df):
    # 원본을 건드리지 않도록 복사본 만들기
    temp = df.copy()

    # 0/1 숫자를 '사망'/'생존' 글자로 바꿔서 색이 두 가지로 나뉘게 하기
    temp["생존여부"] = temp["survived"].map({0: "사망", 1: "생존"})

    # 나이 히스토그램 그리기, 생존 여부로 색 구분, 겹쳐 그리기, 투명도 0.6
    fig = px.histogram(temp, x="age", color="생존여부",
                       barmode="overlay", opacity=0.6,
                       title="생존 여부별 나이 분포")

    # 완성된 그래프 반환
    return fig


# ===== 제목 =====
# 데이터 불러오기 (캐시 덕분에 한 번만 읽음)
df = load_data()

# 대시보드 제목 표시
st.title("타이타닉, 누가 살아남았나?")


# ===== 사이드바 =====
# 사이드바 머리글
st.sidebar.header("필터")

# 성별 선택 (기본값: 모두 선택)
sexes = st.sidebar.multiselect("성별", options=["male", "female"],
                               default=["male", "female"])

# 객실 등급 선택 (기본값: 모두 선택)
classes = st.sidebar.multiselect("객실 등급", options=[1, 2, 3],
                                 default=[1, 2, 3])

# 나이 범위 선택 (0~80세, 기본값: 전체 범위)
age_range = st.sidebar.slider("나이 범위", min_value=0, max_value=80,
                              value=(0, 80))


# ===== 본문: KPI =====
# 사이드바에서 고른 조건으로 데이터 필터하기
filtered = filter_data(df, sexes, classes, age_range)

# 필터된 데이터로 KPI 3개 계산하기
count, survival_rate, avg_age = kpi(filtered)

# 화면을 가로 3칸으로 나누기
col1, col2, col3 = st.columns(3)

# 첫째 칸: 승객 수
col1.metric("승객 수", f"{count}명")

# 둘째 칸: 생존율
col2.metric("생존율", f"{survival_rate}%")

# 셋째 칸: 평균 나이
col3.metric("평균 나이", f"{avg_age}세")


# ===== 본문: 차트 =====
# [추가] KPI 아래를 가로 2칸으로 나누기
left, right = st.columns(2)

# [추가] 왼쪽 칸: 객실 등급별 생존율 막대그래프
left.plotly_chart(class_rate_bar(filtered))

# [추가] 오른쪽 칸: 생존 여부별 나이 히스토그램
right.plotly_chart(age_hist(filtered))


# ===== 본문: 데이터 보기 =====
# [추가] 접었다 펼 수 있는 상자 만들기
with st.expander("데이터 보기"):
    # [추가] 상자 안에 필터된 데이터 표 표시
    st.dataframe(filtered)
