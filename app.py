#!/usr/bin/env python
# coding: utf-8

# In[26]:


import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
import os
import re # 결과 파싱을 위해 정규표현식 라이브러리 추가

# ----------------------------------------------------
# 1. Base64 인코딩 함수 및 예시 파일 경로 설정
# ----------------------------------------------------

# 로컬 파일을 Base64로 인코딩하는 함수
def get_base64_from_file(file_path):
    """지정된 파일 경로의 이미지를 Base64 문자열로 인코딩하여 반환합니다."""
    if not os.path.exists(file_path):
        st.error(f"❌ 오류: 예시 이미지 파일 '{file_path}'를 찾을 수 없습니다. Streamlit 파일과 같은 디렉토리에 두세요.")
        st.stop()
        
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ⚠️ 예시 이미지 파일 이름을 지정합니다. (Streamlit 파일과 같은 디렉토리에 있어야 합니다.)
EGEN_FILE_PATH = "egen_example.png" 
TETO_FILE_PATH = "teto_example.png" 

# Base64 문자열을 변수에 할당합니다.
EGEN_BASE64 = get_base64_from_file(EGEN_FILE_PATH) 
TETO_BASE64 = get_base64_from_file(TETO_FILE_PATH) 

# '에겐' 페르소나 분석 예시 출력 텍스트
EGEN_OUTPUT_TEXT = """
**[분류된 페르소나: 에겐 (EGEN)]**

1️⃣ 사진의 느낌, 분위기 묘사:
* **분위기:** 따뜻하고 부드러운 햇살 아래에서 찍은 듯한 아늑하고 편안한 분위기가 느껴집니다. 전반적으로 채광이 좋고 미소가 자연스러워 친근감을 줍니다.
* **느낌:** 활동적이기보다는 사색적이고, 상대방을 배려할 줄 아는 차분한 느낌입니다.

2️⃣ 설문조사 결과 성향 분석 요약:
* 사용자의 설문과 사진 분위기를 종합했을 때, 안정과 편안함을 추구하는 **내향적인 성향(집 선호)**이 강하며, 깊은 관계를 선호하는 타입으로 보입니다. (설문: 집에서 노는 걸 선호해)

3️⃣ 이 사람과 어울릴 것 같은 사람의 페르소나 요약:
* **유형:** 안정감을 주는 '테토' 페르소나와 상호 보완적인 관계가 될 수 있습니다. 에겐의 섬세한 감성을 이해해주고, 가끔은 활동적인 에너지를 불어넣어 줄 수 있는 사람.
* **특징:** 긍정적이고 개방적이며, 즉흥적인 데이트 코스에 언제든 즐겁게 동참할 수 있는 **'내향적인 탐색형(IP)'** 이 적합합니다. (이 부분은 이전 테토와 어울리는 사람 페르소나와 유사하게 수정했습니다. 에겐에게 맞는 상대를 묘사하도록 수정 필요시 알려주세요!)
"""

# '테토' 페르소나 분석 예시 출력 텍스트
TETO_OUTPUT_TEXT = """
**[분류된 페르소나: 테토 (TETO)]**

1️⃣ 사진의 느낌, 분위기 묘사:
* **분위기:** 야외 활동 중 활기차고 역동적인 에너지가 느껴집니다. 웃는 모습이 시원시원하고 생동감이 넘쳐 사교성이 좋아 보입니다.
* **느낌:** 자신감 있고 도전적이면서도, 유머 감각이 있어 주변 사람들에게 즐거움을 주는 쾌활한 느낌입니다.

2️⃣ 설문조사 결과 성향 분석 요약:
* 사용자의 설문과 사진 분위기를 종합했을 때, 새로운 경험을 추구하고 사람들과의 만남에서 에너지를 얻는 **외향적인 성향(밖 선호)**이 강하며, 즉흥적이고 모험적인 탐색형(P) 기질이 돋보입니다. (설문: 밖에서 노는 게 좋아, 즉흥적으로 목적지를 선택하는 게 좋아)

3️⃣ 이 사람과 어울릴 것 같은 사람의 페르소나 요약:
* **유형:** 테토의 활동성을 지지하고 때로는 함께 일탈을 즐길 수 있는 '에겐' 페르소나와 흥미로운 관계가 될 수 있습니다.
* **특징:** 긍정적이고 개방적이며, 즉흥적인 데이트 코스에 언제든 즐겁게 동참할 수 있는 **'내향적인 탐색형(IP)'** 이 적합합니다.
"""

# ----------------------------------------------------
# 2. Streamlit 및 OpenAI API 로직
# ----------------------------------------------------

# 🔑 OpenAI API Key 환경 변수에서 가져오기
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key or api_key.strip() == "":
    st.error("❌ OpenAI API Key를 코드 상단에 입력하세요.")
    st.stop()

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="소개팅 매칭 페이지", layout="centered")

# ✅ 단계 선택 (상단 탭 방식)
step = st.radio(
    "단계를 선택하세요 👇",
    ["1️⃣ 프로필 사진 업로드", "2️⃣ 성향 설문조사", "3️⃣ 데이터 동의", "4️⃣ 결과 보기"],
    horizontal=True
)

# ✅ 세션 상태 초기화
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "survey" not in st.session_state:
    st.session_state["survey"] = {}
if "consent" not in st.session_state:
    st.session_state["consent"] = None
if "matching_persona_image_url" not in st.session_state:
    st.session_state["matching_persona_image_url"] = None


# --- 1️⃣ 프로필 사진 업로드 ---
if step == "1️⃣ 프로필 사진 업로드":
    st.title("💘 소개팅 매칭 웹페이지")
    st.header("1단계: 프로필 사진 업로드")


    uploaded_file = st.file_uploader("프로필 사진을 업로드하세요.", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, width=250, caption="업로드한 사진")
        st.session_state["uploaded_file"] = uploaded_file
        st.success("✅ 사진이 업로드되었습니다!")

    st.info("👉 상단의 단계를 눌러 다음 단계로 이동하세요.")

# --- 2️⃣ 성향 설문조사 ---
elif step == "2️⃣ 성향 설문조사":
    st.title("💬 성향 설문조사")
    st.header("2단계: 나의 취향을 알려주세요")

    q1 = st.radio(
        "Q1. 주로 에너지를 얻는 곳은?",
        ["나는 밖에서 노는 게 좋아.", "나는 집에서 노는 걸 선호해."],
        key="q1_radio"
    )

    q2 = st.radio(
        "Q2. 여행 스타일은?",
        ["나는 여행에서 즉흥적으로 목적지를 선택하는 게 좋아.", "여행은 무조건 계획대로!"],
        key="q2_radio"
    )

    st.session_state["survey"] = {"Q1": q1, "Q2": q2}
    st.success("✅ 설문이 완료되었습니다. 상단의 단계 메뉴에서 다음 단계로 이동하세요.")

# --- 3️⃣ 데이터 동의 ---
elif step == "3️⃣ 데이터 동의":
    st.title("🔒 데이터 활용 동의")
    st.header("3단계: 데이터 제공에 동의해주세요")

    consent = st.radio(
        "Q. 내 데이터를 가져오시겠습니까?",
        ["네", "아니오"],
        key="consent_radio"
    )

    st.session_state["consent"] = consent
    st.info("👉 '4️⃣ 결과 보기' 단계로 이동해 결과를 확인하세요!")

# --- 4️⃣ 결과 보기 ---
elif step == "4️⃣ 결과 보기":
    st.title("💞 AI 매칭 결과")

    # ✅ 입력 데이터 검증
    if not st.session_state["survey"]:
        st.warning("⚠️ 설문조사를 먼저 완료해주세요 (2단계).")
        st.stop()
    if st.session_state["consent"] is None:
        st.warning("⚠️ 데이터 동의 단계를 완료해주세요 (3단계).")
        st.stop()

    q1 = st.session_state["survey"]["Q1"]
    q2 = st.session_state["survey"]["Q2"]
    consent = st.session_state["consent"]
    uploaded_file = st.session_state["uploaded_file"]
    
    # Base64 인코딩 함수 (업로드된 파일용)
    def get_image_base64_data(uploaded_file):
        image_bytes = uploaded_file.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        mime_type = "image/png"
        if uploaded_file.type == "image/jpeg":
            mime_type = "image/jpeg"
        elif uploaded_file.type == "image/webp":
            mime_type = "image/webp"

        return f"data:{mime_type};base64,{image_base64}"


    if st.button("✨ 결과 보기"):
        if uploaded_file is None:
             st.warning("⚠️ 프로필 사진이 업로드되지 않아, 설문 결과 기반으로만 페르소나를 추론하여 분석합니다.")

        with st.spinner("AI가 당신의 사진과 성향을 분석 중입니다..."):
            try:
                # --- Few-Shot Learning Prompt 구성 시작 ---
                
                # 1. System Instruction: 역할 정의 및 Few-Shot 학습 지침
                system_message = {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "당신은 이미지 분류 전문가입니다. 사진을 '에겐' 또는 '테토' 두 가지 예시 이미지와 비교하여 하나의 카테고리로 분류해야 합니다. 출력 형식은 예시와 완전히 동일해야 합니다."
                        }
                    ]
                }
                messages = [system_message]

                # 2. Few-Shot Example 1: EGEN
                user_prompt_egen = f"""
                [예시 1 - 에겐 페르소나]
                이 예시 이미지와 가까운 사진이 들어오면, **'에겐'** 페르소나로 분류하고 아래 Assistant의 응답 형식처럼 결과를 출력해야 합니다.
                """
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt_egen},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{EGEN_BASE64}", "detail": "low"}}
                    ]
                })
                messages.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": EGEN_OUTPUT_TEXT}]
                })

                # 3. Few-Shot Example 2: TETO
                user_prompt_teto = f"""
                [예시 2 - 테토 페르소나]
                이 예시 이미지와 가까운 사진이 들어오면, **'테토'** 페르소나로 분류하고 아래 Assistant의 응답 형식처럼 결과를 출력해야 합니다.
                """
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt_teto},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{TETO_BASE64}", "detail": "low"}}
                    ]
                })
                messages.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": TETO_OUTPUT_TEXT}]
                })

                # 4. Actual User Input (최종 분석 요청)
                actual_user_text_prompt = f"""
                **[실제 사용자 입력 및 묘사 요청]**
                위의 '에겐'과 '테토' 예시를 참고하여, 다음 '사진'을 분류하세요.

                1.  사진 분석을 통해 예시 중 어떤 페르소나(에겐 또는 테토)인지 두 개 카테고리 중 하나로 반드시 분류하세요.
                2.  선택된 페르소나의 분석 형식에 맞춰 설문 정보와 사진을 묘사하세요.

                [사용자 설문 정보]
                - Q1 응답: {q1}
                - Q2 응답: {q2}
                - 데이터 동의: {consent} (분석에 크게 중요하지 않지만 참고만 할 것)
                """

                actual_user_content = [{"type": "text", "text": actual_user_text_prompt}]

                # 사용자 업로드 이미지 Base64를 최종 메시지에 추가
                if uploaded_file is not None:
                    image_url_data = get_image_base64_data(uploaded_file)
                    actual_user_content.append({
                        "type": "image_url",
                        "image_url": {"url": image_url_data, "detail": "high"}
                    })

                messages.append({
                    "role": "user",
                    "content": actual_user_content
                })
                
                # --- Few-Shot Learning Prompt 구성 완료 ---

                # ✅ GPT-4o 모델 호출
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                )

                analysis_result = response.choices[0].message.content
                st.session_state["matching_persona_image_url"] = None # 이전 이미지 URL 초기화

                st.success("✨ 결과가 도출되었습니다!")
                st.markdown("### 💬 AI 분석 결과")
                st.write(analysis_result)

                # --- 이미지 생성 및 표시 로직 추가 ---
                st.markdown("---")
                st.subheader("🎉 이분과 어울릴 것 같아요!")

                # AI 분석 결과에서 '이 사람과 어울릴 것 같은 사람의 페르소나 요약' 부분을 추출
                match_persona_summary_pattern = r"3️⃣ 이 사람과 어울릴 것 같은 사람의 페르소나 요약:\s*(.*?)(?=\n\n|\Z)"
                match_persona_summary = re.search(match_persona_summary_pattern, analysis_result, re.DOTALL)

                image_generation_prompt = "A high-quality, realistic portrait photo of a person who is suitable for online dating. Focus on the overall atmosphere and personality rather than specific facial features. The person should convey a friendly, approachable, and appealing aura suitable for a dating app profile picture. "
                
                if match_persona_summary:
                    extracted_text = match_persona_summary.group(1).strip()
                    # 추출된 텍스트를 이미지 생성 프롬프트에 추가
                    image_generation_prompt += "\n\nBased on the following description: " + extracted_text
                    st.info(f"AI가 어울리는 사람의 특징을 바탕으로 이미지를 생성합니다: \n\n {extracted_text}")
                else:
                    st.warning("⚠️ '어울리는 사람의 페르소나 요약'을 찾을 수 없어 일반적인 소개팅 프로필 이미지를 생성합니다.")
                    image_generation_prompt += " The person should have a friendly, approachable, and appealing aura, suitable for a dating app profile picture."

                with st.spinner("어울리는 프로필 이미지를 생성 중입니다..."):
                    try:
                        # DALL-E 3 호출
                        image_response = client.images.generate(
                            model="dall-e-3",
                            prompt=image_generation_prompt,
                            size="1024x1024",
                            quality="standard",
                            n=1,
                        )
                        generated_image_url = image_response.data[0].url
                        st.session_state["matching_persona_image_url"] = generated_image_url
                        st.image(generated_image_url, caption="AI가 생성한 매칭 페르소나 이미지", use_column_width=True)
                        st.success("✅ 매칭 페르소나 이미지가 성공적으로 생성되었습니다!")
                        st.balloons()

                    except Exception as img_e:
                        st.error(f"이미지 생성 중 오류가 발생했습니다: {img_e}")

            except Exception as e:
                st.error(f"API 호출 중 오류가 발생했습니다:\n\n{e}")


# In[ ]:


