"""Black Desert Online - AFK Training Dummy EXP Calculator.

Streamlit Community Cloud entrypoint: streamlit_app.py
"""

import math

import streamlit as st


# EXP measured from AFK training dummy (หุ่นไล่กา) in BDO.
REFERENCE_START_EXP = 493_652
REFERENCE_END_EXP = 1_964_238_244
REFERENCE_BONUS = 2125.0
REFERENCE_HOURS = 10
REFERENCE_MINUTES = 14

SLIDER_STEP = 125
PRESET_BONUSES = (1000, 2000, 2125, 3000, 4000)


def estimate_exp_per_minute(
    start_exp: int,
    end_exp: int,
    duration_minutes: int,
    reference_bonus: float,
    target_bonus: float,
) -> float:
    """Estimate EXP/min with the same AFK conditions and proportional bonus."""
    if duration_minutes <= 0 or reference_bonus <= 0:
        raise ValueError("Reference duration and EXP bonus must be positive")
    if end_exp < start_exp or target_bonus < 0:
        raise ValueError("EXP data and target bonus must be non-negative")
    earned_exp = end_exp - start_exp
    return earned_exp / duration_minutes * target_bonus / reference_bonus


def format_exp(value: float) -> str:
    """Show EXP as a rounded, comma-separated whole number."""
    return f"{value:,.0f}"


def nearest_slider_step(value: int) -> int:
    """Snap an arbitrary custom bonus to the nearest slider marker."""
    return int(math.floor(value / SLIDER_STEP + 0.5) * SLIDER_STEP)


def slider_upper_bound(value: int) -> int:
    """Expand the slider for custom bonuses above 5,000%."""
    return max(5000, math.ceil(value / SLIDER_STEP) * SLIDER_STEP)


def set_bonus(value: int) -> None:
    """Source of truth shared by the slider, custom input, and preset buttons."""
    st.session_state.target_bonus = int(value)


def on_slider_change() -> None:
    set_bonus(st.session_state.bonus_slider)


def on_custom_change() -> None:
    set_bonus(st.session_state.bonus_custom)


def hourly_projection(exp_per_minute: float, start_hour: int, end_hour: int) -> list[dict]:
    """Project total EXP gained over each cumulative AFK duration."""
    return [
        {"เวลา AFK": f"{hours} ชั่วโมง", "EXP ที่คาดว่าจะได้รับ": format_exp(exp_per_minute * 60 * hours)}
        for hours in range(start_hour, end_hour + 1)
    ]


st.set_page_config(
    page_title="BDO AFK Training EXP Calculator",
    page_icon="📈",
    layout="wide",
)

st.title("BDO AFK Training EXP Calculator")
st.caption(
    "คำนวณ EXP จากการ AFK ตีหุ่นไล่กา (Training Dummy) ใน Black Desert Online "
    "โดยใช้ผลการทดลองจริงเป็นข้อมูลอ้างอิง"
)

# Section 1: Reference values are shown for transparency but cannot be edited.
st.subheader("1. ข้อมูลอ้างอิง")
reference_left, reference_right = st.columns(2)
with reference_left:
    st.number_input(
        "EXP เริ่มต้น", min_value=0, value=REFERENCE_START_EXP,
        step=1, format="%d", disabled=True,
    )
    st.number_input(
        "EXP สิ้นสุด", min_value=0, value=REFERENCE_END_EXP,
        step=1, format="%d", disabled=True,
    )
    st.number_input(
        "EXP Bonus ตอนที่เก็บข้อมูล (%)", min_value=0.01,
        value=REFERENCE_BONUS, step=125.0, disabled=True,
    )
with reference_right:
    st.number_input(
        "เวลา AFK (ชั่วโมง)", min_value=0, value=REFERENCE_HOURS,
        step=1, disabled=True,
    )
    st.number_input(
        "เวลา AFK (นาที)", min_value=0, max_value=59,
        value=REFERENCE_MINUTES, step=1, disabled=True,
    )
st.caption("ข้อมูลอ้างอิงถูกล็อกไว้ เพื่อให้ทุกการเปรียบเทียบใช้ฐานการทดลองเดียวกัน")

# Section 2: Slider changes by exactly 125%; custom values can be any integer.
st.divider()
st.subheader("2. เลือก EXP Bonus ที่ต้องการคำนวณ")

if "target_bonus" not in st.session_state:
    st.session_state.target_bonus = 3000

selected_bonus = int(st.session_state.target_bonus)
# Synchronize each widget *before* instantiating it in the current run.
st.session_state.bonus_slider = nearest_slider_step(selected_bonus)
st.session_state.bonus_custom = selected_bonus

slider_col, custom_col = st.columns([3, 1], vertical_alignment="bottom")
with slider_col:
    st.slider(
        "EXP Bonus (%)",
        min_value=0,
        max_value=slider_upper_bound(selected_bonus),
        step=SLIDER_STEP,
        key="bonus_slider",
        on_change=on_slider_change,
        help="ลากทีละ 125%",
    )
with custom_col:
    st.number_input(
        "Custom EXP Bonus (%)",
        min_value=0,
        step=1,
        format="%d",
        key="bonus_custom",
        on_change=on_custom_change,
        help="พิมพ์ค่าใดก็ได้ เช่น 999% หรือ 2,250%",
    )

preset_columns = st.columns(len(PRESET_BONUSES))
for column, bonus in zip(preset_columns, PRESET_BONUSES):
    column.button(
        f"{bonus:,}%",
        key=f"preset_{bonus}",
        use_container_width=True,
        type="primary" if selected_bonus == bonus else "secondary",
        on_click=set_bonus,
        args=(bonus,),
    )
st.caption(
    "Slider เพิ่ม/ลดทีละ 125% ส่วนช่อง Custom กรอกได้ทุกจำนวนเต็ม "
    "โดยผลคำนวณใช้ค่า Custom จริง แม้ไม่ตรงกับขีดของ Slider"
)

# Measured reference duration: 03:48 AM to 02:02 PM = 614 minutes.
duration_minutes = REFERENCE_HOURS * 60 + REFERENCE_MINUTES
original_exp = REFERENCE_END_EXP - REFERENCE_START_EXP
target_bonus = int(st.session_state.target_bonus)
exp_per_minute = estimate_exp_per_minute(
    REFERENCE_START_EXP,
    REFERENCE_END_EXP,
    duration_minutes,
    REFERENCE_BONUS,
    target_bonus,
)

# Section 3: Outputs are intentionally EXP only (no LV percentage).
st.divider()
st.subheader("3. ผลการคำนวณ")
st.write(
    f"**EXP ที่ได้รับจริง:** {original_exp:,} EXP ใน "
    f"{REFERENCE_HOURS} ชั่วโมง {REFERENCE_MINUTES} นาที"
)
st.write(f"**EXP Bonus ที่คำนวณ:** {target_bonus:,}%")
metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("EXP / นาที", format_exp(exp_per_minute))
metric_2.metric("EXP / ชั่วโมง", format_exp(exp_per_minute * 60))
metric_3.metric("EXP / 10 ชั่วโมง", format_exp(exp_per_minute * 600))

# Section 4: Compare standard presets with the currently selected bonus.
st.subheader("4. ตารางเปรียบเทียบ EXP Bonus")
bonuses = sorted(set(PRESET_BONUSES) | {target_bonus})
comparison_rows = []
for bonus in bonuses:
    rate = estimate_exp_per_minute(
        REFERENCE_START_EXP,
        REFERENCE_END_EXP,
        duration_minutes,
        REFERENCE_BONUS,
        bonus,
    )
    comparison_rows.append(
        {
            "EXP Bonus": f"{bonus:,}%",
            "EXP / นาที": format_exp(rate),
            "EXP / ชั่วโมง": format_exp(rate * 60),
            "EXP / 10 ชั่วโมง": format_exp(rate * 600),
        }
    )
st.dataframe(comparison_rows, use_container_width=True, hide_index=True)

# Section 5: All 24 cumulative AFK durations update with the bonus controls.
st.subheader("5. EXP ที่ได้รับตามระยะเวลา AFK (1–24 ชั่วโมง)")
st.write(f"**คำนวณจาก EXP Bonus ที่เลือก: {target_bonus:,}%**")
st.caption("จำนวน EXP ที่คาดว่าจะได้รับสะสมเมื่อ AFK ต่อเนื่องเป็นเวลา 1 ถึง 24 ชั่วโมง")
hourly_left, hourly_right = st.columns(2)
with hourly_left:
    st.dataframe(
        hourly_projection(exp_per_minute, 1, 12),
        use_container_width=True,
        hide_index=True,
    )
with hourly_right:
    st.dataframe(
        hourly_projection(exp_per_minute, 13, 24),
        use_container_width=True,
        hide_index=True,
    )

st.info(
    "ตัวเลขเป็นการประมาณโดยสมมติว่า EXP จากการ AFK ตีหุ่นไล่กาเพิ่มตามอัตราส่วน "
    "EXP Bonus โดยตรง และเงื่อนไขการฝึกคงที่ตลอดช่วงเวลา ไม่ใช่การยืนยัน EXP จริงในเกม"
)
st.caption(
    "เมื่อเลเวลเปลี่ยน ค่า EXP ที่ใช้ต่อเลเวลอาจเปลี่ยนไป จึงแสดงผลเป็น EXP เท่านั้น "
    "โดยไม่คำนวณ LV %"
)
