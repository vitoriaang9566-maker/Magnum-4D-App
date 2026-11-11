import streamlit as st
import csv
import datetime
from collections import Counter
from supabase import create_client, Client

st.set_page_config(page_title="4D 助手", page_icon="🎰", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    h1 {font-size: 1.5rem !important;}
    h2 {font-size: 1.2rem !important;}
    p {font-size: 0.9rem !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🎰 4D 预测助手</h1>", unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

tab1, tab2 = st.tabs(["🔮 预测", "📊 对账"])

with tab1:
    st.markdown("<h2>生成下一期 Top 10</h2>", unsafe_allow_html=True)
    st.write("基于历史频率模型（Frequency）。")
    
    if st.button("🚀 立即生成并冻结", type="primary", use_container_width=True):
        with st.spinner("计算中..."):
            prizes = []
            with open("magnum_draws_cleaned.csv", "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prizes.append(row['prize_1'])
            
            freq = Counter(prizes)
            top10 = [num for num, count in freq.most_common(10)]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                data = {
                    "prediction_time": now_str,
                    "model": "Frequency_Top10",
                    "top10": ", ".join(top10),
                    "actual_prize": "",
                    "is_hit": False
                }
                supabase.table("predictions").insert(data).execute()
                st.success(f"✅ 记录已生成并永久保存至云端！({now_str})")
            except Exception as e:
                st.error(f"❌ 数据库写入失败: {e}")
                
            st.info(f"**推荐号码：**\n\n{', '.join(top10)}")

with tab2:
    st.markdown("<h2>录入真实开奖</h2>", unsafe_allow_html=True)
    
    with st.form("input_form"):
        actual_prize = st.text_input("输入 4 位头奖号码", max_chars=4)
        submitted = st.form_submit_button("提交对账", type="primary", use_container_width=True)
        
        if submitted:
            if len(actual_prize) != 4 or not actual_prize.isdigit():
                st.error("格式错误，请输入 4 位纯数字。")
            else:
                try:
                    response = supabase.table("predictions").select("*").eq("actual_prize", "").execute()
                    pending = response.data
                    
                    if not pending:
                        st.warning("没有待对账的预测。")
                    else:
                        hits = 0
                        for r in pending:
                            is_hit = actual_prize in r['top10'].split(', ')
                            if is_hit:
                                hits += 1
                            
                            supabase.table("predictions").update({
                                "actual_prize": actual_prize,
                                "is_hit": is_hit
                            }).eq("id", r['id']).execute()
                        
                        total_resp = supabase.table("predictions").select("*").execute()
                        all_rows = total_resp.data
                        total_predictions = len(all_rows)
                        total_hits = sum(1 for r in all_rows if r['is_hit'])
                        hit_rate = (total_hits / total_predictions) * 100 if total_predictions else 0
                        
                        st.success(f"✅ 对账完成: {actual_prize}")
                        st.metric(label="累计命中率", value=f"{hit_rate:.2f}%")
                        st.write(f"总期数: {total_predictions} | 命中: {total_hits}")
                except Exception as e:
                    st.error(f"❌ 数据库读取/更新失败: {e}")

    st.divider()
    st.markdown("<h2>📜 历史记录 (最近3期)</h2>", unsafe_allow_html=True)
    
    try:
        res = supabase.table("predictions").select("*").order("id", desc=True).limit(3).execute()
        recent = res.data
        
        if recent:
            for r in recent:
                status_color = "green" if r['is_hit'] else "gray"
                st.markdown(f"""
                <div style='border: 1px solid #444; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                    <p style='margin: 0; font-size: 0.8rem; color: #aaa;'>预测时间: {r['prediction_time']}</p>
                    <p style='margin: 5px 0; font-size: 1rem;'><b>预测号:</b> {r['top10']}</p>
                    <p style='margin: 0; font-size: 0.9rem; color: {status_color};'><b>开奖号:</b> {r['actual_prize']} | <b>命中: {r['is_hit']}</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无记录。")
    except Exception as e:
        st.error(f"❌ 历史记录读取失败: {e}")
