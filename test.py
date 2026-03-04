import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# --- 解決 Matplotlib 中文顯示問題 ---
mpl.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS'] 
mpl.rcParams['axes.unicode_minus'] = False

# --- 網頁設定 ---
st.set_page_config(page_title="清大光學實驗助教幫手", layout="wide")
st.title("🔬 實驗 2：組合透鏡成像模擬 (範圍：0-1200mm)")
st.markdown("此模擬器專為 1.2 公尺光學桌設計，幫助你理解「虛物成實像」的座標扣除邏輯。")

# --- 側邊欄：四個主要測量座標 ---
st.sidebar.header("📏 光學桌刻度輸入 (0-1200 mm)")
mode = st.sidebar.radio("實驗模式：", ["測量凹透鏡焦距", "測量凸面鏡焦距"])

# 已知焦距微調
f1 = st.sidebar.number_input("凸透鏡 L1 已知焦距 (mm)", value=100.0)

# 1. 物體位置
x_obj = st.sidebar.slider("1. 物體/光源座標 (x_obj)", 0.0, 1200.0, 50.0)

# 2. 凸透鏡 L1 位置 (必須在物體後面)
x_L1 = st.sidebar.slider("2. 凸透鏡 L1 座標 (x_L1)", x_obj + 10.0, 1200.0, 200.0)

# 自動計算 I1 (虛物) 座標
so1 = x_L1 - x_obj
if so1 != f1:
    si1 = 1 / (1/f1 - 1/so1)
    x_I1 = x_L1 + si1
else:
    si1 = 9999.0
    x_I1 = 9999.0

# 3. 待測物 L2 位置 (通常放在 L1 與 I1 之間)
x_L2 = st.sidebar.slider("3. 待測元件 L2 座標 (x_L2)", x_L1 + 10.0, 1200.0, 350.0)

# 4. 最終成像平面位置
if mode == "測量凹透鏡焦距":
    # 凹透鏡成像在後方
    x_I2 = st.sidebar.slider("4. 最終成像 I2 座標 (x_I2)", x_L2 + 10.0, 1200.0, 600.0)
else:
    # 凸面鏡成像是反射，在前方
    x_I2 = st.sidebar.slider("4. 最終成像 I2 座標 (x_I2)", x_L1 + 5.0, x_L2 - 5.0, 250.0)

# --- 計算邏輯展示 ---
st.header("📐 座標轉換與高斯公式應用")

c1, c2 = st.columns(2)

with c1:
    st.subheader("第一階段：產生虛物 (I1)")
    st.markdown(f"""
    1. **求物距 $s_{{o1}}$**：$x_{{L1}} - x_{{obj}} = {x_L1} - {x_obj} = {so1:.1f}$ mm
    2. **求像距 $s_{{i1}}$**：$(1/{f1} - 1/{so1:.1f})^{{-1}} = {si1:.1f}$ mm
    3. **求初次成像位置 $x_{{I1}}$**：$x_{{L1}} + s_{{i1}} = {x_L1} + {si1:.1f} = {x_I1:.1f}$ mm
    """)
    if x_I1 > x_L2:
        st.success(f"✅ I1 ({x_I1:.1f}) 在 L2 ({x_L2}) 後方，成功建立「虛物」！")
    else:
        st.error(f"❌ I1 在 L2 前方，這不符合虛物成實像的實驗條件，請調整滑桿。")

with c2:
    st.subheader(f"第二階段：計算 {mode}")
    # 關鍵：虛物距 so2 的定義
    so2 = -(x_I1 - x_L2)
    
    if mode == "測量凹透鏡焦距":
        si2 = x_I2 - x_L2 # 穿透，後減前
        f2 = 1 / (1/so2 + 1/si2)
        st.markdown(f"""
        1. **求虛物距 $s_{{o2}}$**：$-(x_{{I1}} - x_{{L2}}) = -({x_I1:.1f} - {x_L2}) = **{so2:.1f}** mm
        2. **求實像距 $s_{{i2}}$**：$x_{{I2}} - x_{{L2}} = {x_I2} - {x_L2} = **{si2:.1f}** mm
        3. **計算結果 $f_2$**：$(1/s_{{o2}} + 1/s_{{i2}})^{{-1}} = **{f2:.2f}** mm
        """)
    else:
        si2 = x_L2 - x_I2 # 反射，前減後 (相對於光行進方向)
        f2 = 1 / (1/so2 + 1/si2)
        st.markdown(f"""
        1. **求虛物距 $s_{{o2}}$**：$-(x_{{I1}} - x_{{L2}}) = -({x_I1:.1f} - {x_L2}) = **{so2:.1f}** mm
        2. **求實像距 $s_{{i2}}$**：$x_{{L2}} - x_{{I2}} = {x_L2} - {x_I2} = **{si2:.1f}** mm
        3. **計算結果 $f_2$**：$(1/s_{{o2}} + 1/s_{{i2}})^{{-1}} = **{f2:.2f}** mm
        """)

# --- 繪圖 ---
st.header("🖼️ 光學桌座標示意圖 (0-1200mm)")

fig, ax = plt.subplots(figsize=(12, 4))
ax.axhline(0, color='black', lw=1)

# 畫元件
ax.vlines([x_obj, x_L1, x_L2, x_I2], -10, 10, colors=['black', 'blue', 'purple', 'red'], lw=2)
ax.vlines(x_I1, -10, 10, colors='green', linestyles='--', lw=1)

# 標籤
ax.text(x_obj, 12, "物(obj)", ha='center')
ax.text(x_L1, 12, "L1", ha='center', color='blue')
ax.text(x_L2, 12, "L2", ha='center', color='purple')
ax.text(x_I2, 12, "像(I2)", ha='center', color='red')
ax.text(x_I1, -15, "虛物(I1)", ha='center', color='green')

# 設定軸範圍
ax.set_xlim(0, 1200)
ax.set_ylim(-20, 20)
ax.set_xlabel("光學桌刻度 (mm)")
ax.grid(True, alpha=0.3)
st.pyplot(fig)