import streamlit as st
import csv
import datetime
import random
from collections import Counter, defaultdict
from supabase import create_client, Client

st.set_page_config(page_title="4D 助手", page_icon="🎰", layout="wide")

# 注入高级 CSS 美化 (深色极简风)
st.markdown("""
<style>
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 整体背景色和字体 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 顶部大标题 */
    h1 {
        text-align: center;
        color: #FFD700;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding-bottom: 20px;
    }
    
    /* 数据概览卡片 */
    .metric-card {
        background-color: #1E232F;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-card h3 {
        color: #A0A5B1;
        font-size: 14px !important;
        margin-bottom: 5px;
    }
    .metric-card p {
        color: #00FF7F;
        font-size: 28px !important;
        font-weight: bold;
        margin: 0;
    }
    
    /* 推荐结果卡片 */
    .result-card {
        background-color: #1E232F;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #444;
    }
    .result-freq { border-left-color: #00BFFF; }
    .result-markov { border-left-color: #FFD700; }
    .result-random { border-left-color: #FF4500; }
    
    /* 按钮样式 */
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 15px;
        font-size: 18px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎰 4D 预测助手 (V6.2 UI版)</h1>", unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    url = "https://tpsthytjwauxnjzhxlot.supabase.co"
    key = "sb_publishable_OlZGJ7WnMLYk51A-j6yw2w_18WUo-ax"
    return create_client(url, key)

supabase = init_connection()

@st.cache_data
def load_history_data():
    prizes = []
    try:
        with open("magnum_draws_cleaned.csv", "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prizes.append(row['prize_1'])
    except Exception:
        pass
    try:
        res = supabase.table("predictions").select("actual_prize").neq("actual_prize", "").execute()
        for r in res.data:
            if r['actual_prize'] and len(r['actual_prize']) == 4:
                prizes.append(r['actual_prize'])
    except Exception:
        pass
    return prizes

# --- 顶部数据概览卡片 ---
try:
    res = supabase.table("predictions").select("*").execute()
    all_data = res.data
    total_pred = len([d for d in all_data if d['model'] != "Manual_Entry"])
    total_hits = sum(1 for d in all_data if d['is_hit'])
    win_rate = (total_hits / total_pred * 100) if total_pred > 0 else 0.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>总预测期数</h3><p>{total_pred}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>累计命中</h3><p>{total_hits}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>当前胜率</h3><p>{win_rate:.2f}%</p></div>', unsafe_allow_html=True)
except Exception:
    pass

tab1, tab2, tab3 = st.tabs(["🔮 预测", "📊 对账", "📥 录入新开奖"])

with tab1:
    st.markdown("<h2>生成下一期预测矩阵</h2>", unsafe_allow_html=True)
    st.write("基于历史数据，同时生成：频率模型、马尔可夫模型、随机对照组。")
    
    if st.button("🚀 生成并冻结三组预测", type="primary", use_container_width=True):
        with st.spinner("AI 正在运算..."):
            prizes = load_history_data()
            if len(prizes) < 10:
                st.error("历史数据太少，无法预测。")
                st.stop()
                
            freq = Counter(prizes)
            top10_freq = [num for num, count in freq.most_common(10)]
            
            all_10000 = [f"{i:04d}" for i in range(10000)]
            top10_random = random.sample(all_10000, 10)
            
            transition = defaultdict(lambda: defaultdict(int))
            for i in range(len(prizes) - 1):
                current_last = prizes[i][-1]
                next_last = prizes[i+1][-1]
                transition[current_last][next_last] += 1
            
            last_prize = prizes[-1]
            predicted_last = max(transition[last_prize[-1]].items(), key=lambda x: x[1])[0] if transition[last_prize[-1]] else "0"
            
            top10_markov = []
            for num, count in freq.most_common(50):
                if num[-1] == predicted_last and num not in top10_markov:
                    top10_markov.append(num)
                if len(top10_markov) >= 10:
                    break
            if len(top10_markov) < 10:
                top10_markov.extend(top10_freq[:10-len(top10_markov)])
            
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                supabase.table("predictions").insert([
                    {"prediction_time": now_str, "model": "Frequency", "top10": ", ".join(top10_freq), "actual_prize": "", "is_hit": False},
                    {"prediction_time": now_str, "model": "Markov", "top10": ", ".join(top10_markov), "actual_prize": "", "is_hit": False},
                    {"prediction_time": now_str, "model": "Random", "top10": ", ".join(top10_random), "actual_prize": "", "is_hit": False}
                ]).execute()
                st.success(f"✅ 三组预测已生成并永久保存至云端！({now_str})")
            except Exception as e:
                st.error(f"❌ 数据库写入失败: {e}")
                
            st.markdown("### 🏆 推荐结果")
            st.markdown(f'<div class="result-card result-freq"><b>🔵 频率模型:</b> {", ".join(top10_freq)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card result-markov"><b>🟡 马尔可夫模型:</b> {", ".join(top10_markov)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card result-random"><b>🔴 随机对照组:</b> {", ".join(top10_random)}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("<h2>录入真实开奖与对账</h2>", unsafe_allow_html=True)
    
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
                        hits_by_model = {"Frequency": 0, "Markov": 0, "Random": 0}
                        for r in pending:
                            is_hit = actual_prize in r['top10'].split(', ')
                            if is_hit:
                                if r['model'] in hits_by_model:
                                    hits_by_model[r['model']] += 1
                            
                            supabase.table("predictions").update({
                                "actual_prize": actual_prize,
                                "is_hit": is_hit
                            }).eq("id", r['id']).execute()
                        
                        st.success(f"✅ 对账完成: {actual_prize}")
                        st.write("**本轮各模型命中情况：**")
                        st.write(f"- 频率模型: {'🎯 命中' if hits_by_model['Frequency'] > 0 else '未中'}")
                        st.write(f"- 马尔可夫模型: {'🎯 命中' if hits_by_model['Markov'] > 0 else '未中'}")
                        st.write(f"- 随机模型: {'🎯 命中' if hits_by_model['Random'] > 0 else '未中'}")
                        
                except Exception as e:
                    st.error(f"❌ 数据库读取/更新失败: {e}")

    st.divider()
    st.markdown("<h2>📜 历史记录 (最近 3 次预测)</h2>", unsafe_allow_html=True)
    
    try:
        res = supabase.table("predictions").select("*").order("id", desc=True).limit(9).execute()
        recent = res.data
        
        if recent:
            for r in recent:
                status_color = "green" if r['is_hit'] else "gray"
                model_color = "red" if r['model'] == "Random" else "blue"
                st.markdown(f"""
                <div style='border: 1px solid #444; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                    <p style='margin: 0; font-size: 0.8rem; color: #aaa;'>预测时间: {r['prediction_time']} | 模型: <span style='color:{model_color};'>{r['model']}</span></p>
                    <p style='margin: 5px 0; font-size: 0.9rem;'><b>Top10:</b> {r['top10']}</p>
                    <p style='margin: 0; font-size: 0.9rem; color: {status_color};'><b>开奖号:</b> {r['actual_prize'] if r['actual_prize'] else '待开奖'} | <b>命中: {r['is_hit']}</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无记录。")
    except Exception as e:
        st.error(f"❌ 历史记录读取失败: {e}")

with tab3:
    st.markdown("<h2>手动录入新开奖结果</h2>", unsafe_allow_html=True)
    st.write("将最新的开奖结果永久写入云端。")
    
    with st.form("new_draw_form"):
        new_prize = st.text_input("输入最新开奖的 4 位头奖号码", max_chars=4)
        submitted_draw = st.form_submit_button("保存至云端", type="primary", use_container_width=True)
        
        if submitted_draw:
            if len(new_prize) != 4 or not new_prize.isdigit():
                st.error("格式错误，请输入 4 位纯数字。")
            else:
                try:
                    data = {
                        "prediction_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "model": "Manual_Entry",
                        "top10": "",
                        "actual_prize": new_prize,
                        "is_hit": False
                    }
                    supabase.table("predictions").insert(data).execute()
                    st.success(f"✅ 新开奖结果 {new_prize} 已成功保存！")
                except Exception as e:
                    st.error(f"❌ 数据库写入失败: {e}")
