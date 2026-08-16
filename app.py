import streamlit as st
import urllib.request
import io
from pypdf import PdfReader
import pandas as pd

st.set_page_config(page_title="診所藥品庫存比對", page_icon="💊", layout="centered")

# 1. 診所常用藥品清單
COMMON_DRUGS = [
    # 單味藥
    "黃水茄", "藕節", "半枝蓮", "綿茵陳", "仙鶴草", "香附", "板藍根", "白鮮皮", "桑寄生", "麥芽", 
    "合歡皮", "大黃", "蒲公英", "茯神", "益母草", "夏枯草", "夜交藤", "連翹", "葶苶子", "丹參", 
    "菟絲子", "紫蘇葉", "玉竹", "山藥", "葛根", "黃精", "杜仲", "魚腥草", "皂角刺", "續斷", 
    "蒼耳子", "鉤藤", "女貞子", "天花粉", "川芎", "旱蓮草", "枳實", "地膚子", "蒼朮", "海螵蛸", 
    "土茯苓", "黃芩", "梔子", "決明子", "雞血藤", "牡蠣", "牡丹皮", "紫草根", "巴戟天", "淫羊藿", 
    "石膏", "艾葉", "薄荷", "路路通", "小茴香", "雞內金", "覆盆子", "銀豆", "澤瀉", "三七", 
    "梗米", "白芨",
    # 複方藥
    "消風散", "當歸芍藥散", "加味逍遙散", "清燥救肺湯", "八味帶下方", "當歸拈痛湯", "柴胡加龍骨牡蠣湯", 
    "桂枝加龍骨牡蠣湯", "半夏厚朴湯", "炙甘草湯", "辛夷清肺湯", "三黃瀉心湯", "百合固金湯", "天王補心丹", 
    "濟生腎氣丸", "當歸四逆湯", "補中益氣湯", "天麻鉤藤飲", "清暑益氣湯", "五苓散", "加胃平胃散", 
    "止嗽散", "代赭旋覆湯", "六君子湯", "平胃散", "麥門冬湯", "小青龍湯", "蒼耳散", "豬苓湯", 
    "普濟消毒飲", "龍膽瀉肝湯", "通竅活血湯", "人蔘養榮湯", "血府逐瘀湯", "木香檳榔丸", "桂枝茯苓丸", 
    "川芎茶調散", "知柏地黃丸", "連翹敗毒散", "麻子仁丸", "甘麥大棗湯", "柴胡疏肝湯", "溫膽湯", 
    "溫清湯", "柴胡清肝湯", "少腹逐瘀湯", "身痛逐瘀湯", "完帶湯", "防風通聖散", "杞菊地黃丸", 
    "芍藥甘草湯", "歸脾湯", "大承氣湯", "藿香正氣散", "疏經活血湯", "甘露飲", "玉女煎", 
    "半夏瀉心湯", "桑螵蛸散", "生脈飲", "七寶美髯丹", "黃耆五物湯", "荊芥連翹湯", "金鎖固精丸", 
    "八正散", "柴葛解肌湯", "葛根黃芩黃連湯", "四逆湯", "補陽還五湯", "桃核承氣湯", "大青龍湯", 
    "越婢加朮湯", "當歸飲子", "保和丸", "胃舒寧", "紫草根牡蠣湯", "地黃飲子", "溫經湯", 
    "清上防風湯", "竹葉石膏湯"
]

st.title("💊 診所藥品庫存自動比對")

# 分頁籤：支援「貼上網址」與「檔案上傳」兩種模式
tab1, tab2 = st.tabs(["🔗 貼上 PDF 網址", "📤 上傳 PDF 檔案"])

pdf_stream = None

# ---- 模式 1：貼上網址 ----
with tab1:
    url_input = st.text_input("請貼上複製的 PDF 網址：", placeholder="https://... 或 http://...")
    if url_input:
        try:
            req = urllib.request.Request(url_input, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                pdf_bytes = response.read()
                pdf_stream = io.BytesIO(pdf_bytes)
                st.success("成功讀取網路 PDF 檔案！")
        except Exception as e:
            st.error("無法讀取該網址的 PDF，請確認網址是否為公開可下載的連結，或改用上傳檔案。")

# ---- 模式 2：檔案上傳 ----
with tab2:
    uploaded_file = st.file_uploader("選擇手機內的 PDF 檔案", type=["pdf"])
    if uploaded_file is not None:
        pdf_stream = uploaded_file

# ---- 比對與顯示邏輯 ----
if pdf_stream is not None:
    try:
        reader = PdfReader(pdf_stream)
        pdf_text_lines = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text_lines.extend(text.split('\n'))

        matched_data = []

        for drug in COMMON_DRUGS:
            for line in pdf_text_lines:
                if drug in line:
                    parts = line.split()
                    qty = parts[-1] if parts else "0"
                    matched_data.append({
                        "診所常用藥": drug,
                        "廠商標示品名": parts[1] if len(parts) > 1 else drug,
                        "庫存數量": qty
                    })
                    break

        st.divider()
        st.subheader(f"✅ 符合項目（共 {len(matched_data)} 項）")

        if matched_data:
            for idx, item in enumerate(matched_data, 1):
                st.markdown(
                    f"""
                    <div style="background-color:#F0F2F6; padding:12px; border-radius:10px; margin-bottom:8px;">
                        <span style="font-size:16px; font-weight:bold; color:#1E88E5;">{idx}. {item['診所常用藥']}</span><br/>
                        <span style="font-size:14px; color:#555;">廠商品名：{item['廠商標示品名']}</span><br/>
                        <span style="font-size:15px; font-weight:bold; color:#D32F2F;">📦 廠商庫存：{item['庫存數量']}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.warning("⚠️ 未找到任何符合「診所常用藥」且「廠商有庫存」的項目。")
    except Exception as e:
        st.error("解析 PDF 失敗，請確認檔案格式是否正確。")
