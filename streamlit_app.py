import streamlit as st


def estimate_exp_per_minute(
    start_exp: int,
    end_exp: int,
    duration_minutes: int,
    reference_bonus: float,
    target_bonus: float,
) -> float:
    """Estimate EXP per minute assuming EXP scales with the total bonus."""
    earned_exp = end_exp - start_exp
    return earned_exp / duration_minutes * (target_bonus / reference_bonus)


def format_exp(value: float) -> str:
    return f"{value:,.0f}"


st.set_page_config(
    page_title="BDO Training EXP Calculator",
    page_icon="📈",
    layout="wide",
)

st.title("BDO Training EXP Calculator")
st.caption("คำนวณ EXP ต่อนาทีและต่อชั่วโมงจากผลฟาร์มจริง โดยไม่อิง LV %")

st.subheader("1. ข้อมูลการฟาร์มอ้างอิง")
left, right = st.columns(2)
with left:
    start_exp = st.number_input(
        "EXP เริ่มต้น", min_value=0, value=493_652, step=1, format="%d"
    )
    end_exp = st.number_input(
        "EXP สิ้นสุด", min_value=0, value=1_964_238_244, step=1, format="%d"
    )
    reference_bonus = st.number_input(
        "EXP Bonus ตอนที่เก็บข้อมูล (%)",
        min_value=0.01,
        value=2125.0,
        step=25.0,
    )
with right:
    hours = st.number_input("เวลาฟาร์ม (ชั่วโมง)", min_value=0, value=10, step=1)
    minutes = st.number_input(
        "เวลาฟาร์ม (นาที)", min_value=0, max_value=59, value=14, step=1
    )
    target_bonus = st.number_input(
        "EXP Bonus ที่ต้องการทดลอง (%)",
        min_value=0.0,
        value=3000.0,
        step=100.0,
    )

duration_minutes = hours * 60 + minutes

if end_exp < start_exp:
    st.error("EXP สิ้นสุดต้องมากกว่าหรือเท่ากับ EXP เริ่มต้น")
    st.stop()
if duration_minutes <= 0:
    st.error("ระยะเวลาฟาร์มต้องมากกว่า 0 นาที")
    st.stop()

original_exp = end_exp - start_exp
exp_minute = estimate_exp_per_minute(
    start_exp, end_exp, duration_minutes, reference_bonus, target_bonus
)

st.divider()
st.subheader("2. ผลการคำนวณ")
st.write(f"**EXP ที่ได้รับจริง:** {original_exp:,} EXP ใน {hours} ชั่วโมง {minutes} นาที")
st.write(f"**EXP Bonus ที่คำนวณ:** {target_bonus:,.2f}%")

col1, col2, col3 = st.columns(3)
col1.metric("EXP / นาที", format_exp(exp_minute))
col2.metric("EXP / ชั่วโมง", format_exp(exp_minute * 60))
col3.metric("EXP / 10 ชั่วโมง", format_exp(exp_minute * 600))

st.subheader("3. ตารางเปรียบเทียบ EXP Bonus")
bonuses = sorted({1000.0, 2000.0, 2125.0, 3000.0, 4000.0, target_bonus})
rows = []
for bonus in bonuses:
    per_min = estimate_exp_per_minute(
        start_exp, end_exp, duration_minutes, reference_bonus, bonus
    )
    rows.append(
        {
            "EXP Bonus": f"{bonus:,.2f}%",
            "EXP / นาที": format_exp(per_min),
            "EXP / ชั่วโมง": format_exp(per_min * 60),
            "EXP / 10 ชั่วโมง": format_exp(per_min * 600),
        }
    )
st.dataframe(rows, use_container_width=True, hide_index=True)

st.info(
    "การประมาณนี้สมมติว่า EXP เปลี่ยนแปลงตามอัตราส่วนของ EXP Bonus โดยตรง "
    "และความเร็วในการกำจัดมอนสเตอร์คงที่"
)
st.caption(
    "ข้อมูล EXP เริ่มต้น/สิ้นสุดต้องเป็นค่าที่หักลบกันได้โดยตรง "
    "หากเลเวลอัปกลางช่วงฟาร์ม ต้องนำ EXP ของแต่ละเลเวลมารวมก่อน"
)
