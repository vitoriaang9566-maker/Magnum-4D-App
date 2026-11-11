import streamlit as st
import csv
import datetime
import random
import requests
import pandas as pd
import plotly.graph_objects as go
from collections import Counter, defaultdict
from supabase import create_client, Client

st.set_page_config(page_title="4D 助手", page_icon="👑", layout="wide")

# ================= 黑金奢华风格 CSS =================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #05080E 0%, #111827 100%); color: #E5E7EB; }
    h1 { text-align: center; color: #FFD700; font-family: 'Georgia', serif; font-weight: bold; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); padding-bottom: 20px; }
    h2, h3 { color: #FFD700 !important; font-family: 'Georgia', serif; }
    .metric-card { background-color: rgba(17, 24, 39, 0.8); border: 1px solid rgba(255, 215, 0, 0.5); border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 0 15px rgba(255, 215, 0, 0.1); margin-bottom: 20px; transition: all 0.3s ease; }
    .metric-card:hover { box-shadow: 0 0 25px rgba(255, 215, 0, 0.3); }
    .metric-card h3 { color: #A0A5B1 !important; font-size: 14px !important; margin-bottom: 5px; }
    .metric-card p { color: #FFD700; font-size: 28px !important; font-weight: bold; margin: 0; }
    .result-card { background-color: rgba(17, 24, 39, 0.9); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
    .result-freq { border: 1px solid rgba(0, 191, 255, 0.6); border-left: 5px solid #00BFFF; }
    .result-markov { border: 1px solid rgba(255, 215, 0, 0.6); border-left: 5px solid #FFD700; }
    .result-random { border: 1px solid rgba(255, 69, 0, 0.6); border-left: 5px solid #FF4500; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #8B0000 0%, #FF4500 100%); color: #FFD700; border: 1px solid #FFD700; border-radius: 10px; padding: 15px; font-size: 18px !important; font-weight: bold; box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
    .stButton>button:hover { color: white; box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
    div[data-testid="stRadio"] > div[role="radiogroup"] { display: flex; justify-content: center; gap: 20px; padding: 20px 0; }
    div[data-testid="stRadio"] > div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] label { background-color: rgba(17, 24, 39, 0.8); border: 1px solid rgba(255, 215, 0, 0.4); border-radius: 12px; padding: 15px 40px; cursor: pointer; transition: all 0.3s ease; text-align: center; box-shadow: 0 0 10px rgba(0,0,0,0.5); }
    div[data-testid="stRadio"] > div[role="radiogroup"] label:hover { border-color: #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
    div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] { background-color: rgba(255, 215, 0, 0.15) !important; border: 2px solid #FFD700 !important; box-shadow: 0 0 25px rgba(255, 215, 0, 0.6) !important; transform: scale(1.05); }
    div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] p { color: #FFD700 !important; font-weight: bold; font-size: 1.2rem !important; text-shadow: 0 0 5px rgba(255, 215, 0, 0.5); }
    div[data-testid="stRadio"] > div[role="radiogroup"] label p { color: #E5E7EB; font-size: 1.1rem; margin: 0; }
    div[data-testid="stNotification"] { background-color: rgba(17, 24, 39, 0.95) !important; border: 1px solid rgba(255, 215, 0, 0.5) !important; border-radius: 10px; box-shadow: 0 0 15px rgba(255, 215, 0, 0.15); }
    div[data-testid="stNotification"] p { color: #FFD700 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>👑 4D 预测助手 (黑金 VIP 版) 👑</h1>", unsafe_allow_html=True)

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
    total_pred = len([d for d in all_data if d['model'] not in ["Manual_Entry", "Auto_Fetch"]])
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

# ================= 自定义导航菜单 =================
menu = st.radio(
    "导航",
    ["预测", "对账与图表", "全自动抓取"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# ================= 内容区域 =================
if menu == "预测":
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
            st.markdown(f'<div class="result-card result-freq"><b style="color:#00BFFF;">💎 频率模型:</b> {", ".join(top10_freq)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card result-markov"><b style="color:#FFD700;">👑 马尔可夫模型:</b> {", ".join(top10_markov)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card result-random"><b style="color:#FF4500;">🎲 随机对照组:</b> {", ".join(top10_random)}</div>', unsafe_allow_html=True)

elif menu == "对账与图表":
    st.markdown("<h2>录入真实开奖与命中率走势</h2>", unsafe_allow_html=True)
    
    with st.form("input_form"):
        actual_prize = st.text_input("输入 4 位头奖号码", max_chars=4)
        submitted = st.form_submit_button("提交对账", type="primary", use_container_width=True)
        
        if submitted:
            if len(actual_prize) != 4 or not actual_prize.isdigit():
                st.error("格式错误，请输入 4 位纯数字。")
            else:
                try:
                    # 找所有待对账预测 (包括之前没开奖的)
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
                        st.write("**本轮命中情况：** 频率: " + ("🎯" if hits_by_model['Frequency'] else "未中") + " | 马尔可夫: " + ("🎯" if hits_by_model['Markov'] else "未中") + " | 随机: " + ("🎯" if hits_by_model['Random'] else "未中"))
                except Exception as e:
                    st.error(f"❌ 对账失败: {e}")

    st.divider()
    
    # ================= 这里开始画图 =================
    st.markdown("<h2>📈 最近 30 期命中率走势</h2>", unsafe_allow_html=True)
    
    try:
        # 取最近 90 条记录（约 30 期 * 3 个模型）
        res = supabase.table("predictions").select("*").neq("actual_prize", "").order("id", desc=False).execute()
        all_data = res.data
        
        # 用 Pandas 来整理数据
        df = pd.DataFrame(all_data)
        df = df[df['model'].isin(['Frequency', 'Markov', 'Random'])].tail(90)
        
        if not df.empty:
            # 为了让 x 轴好看，我们只用时间
            df['time'] = df['prediction_time'].apply(lambda x: x.split(' ')[1][:5])
            
            fig = go.Figure()
            # 定义颜色
            colors = {'Frequency': '#00BFFF', 'Markov': '#FFD700', 'Random': '#FF4500'}
            
            for model in ['Frequency', 'Markov', 'Random']:
                model_df = df[df['model'] == model]
                if not model_df.empty:
                    fig.add_trace(go.Scatter(
                        x=model_df['time'], 
                        y=model_df['is_hit'].astype(int), 
                        mode='lines+markers',
                        name=model,
                        line=dict(color=colors[model], width=3),
                        marker=dict(size=8, line=dict(width=2, color='#111827'))
                    ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E5E7EB'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickvals=[0, 1], ticktext=['未中', '命中']),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("还没有对账数据，先去对账吧！")
    except Exception as e:
        st.error(f"读取图表数据失败: {e}")

    st.divider()
    st.markdown("<h2>📜 历史记录 (最近 10 条)</h2>", unsafe_allow_html=True)
    try:
        res = supabase.table("predictions").select("*").order("id", desc=True).limit(10).execute()
        recent = res.data
        if recent:
            for r in recent:
                status_color = "#FFD700" if r['is_hit'] else "#6B7280"
                model_color = "#FF4500" if r['model'] == "Random" else "#00BFFF"
                if r['model'] == "Auto_Fetch": model_color = "#00FF7F"
                st.markdown(f"""
                <div style='border: 1px solid rgba(255,215,0,0.2); background-color: rgba(17, 24, 39, 0.6); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <p style='margin: 0; font-size: 0.8rem; color: #A0A5B1;'>预测时间: {r['prediction_time']} | 模型: <span style='color:{model_color};'>{r['model']}</span></p>
                    <p style='margin: 5px 0; font-size: 1rem; color: #E5E7EB;'><b>Top10:</b> {r['top10']}</p>
                    <p style='margin: 0; font-size: 0.9rem; color: {status_color};'><b>开奖号:</b> {r['actual_prize'] if r['actual_prize'] else '待开奖'} | <b>命中: {r['is_hit']}</b></p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ 历史记录读取失败: {e}")

elif menu == "全自动抓取":
    st.markdown("<h2>自动抓取最新开奖结果</h2>", unsafe_allow_html=True)
    st.write("点击下方按钮，系统将自动从 4dlivetoday 抓取最新一期 Magnum 头奖，并存入数据库。")
    
    if st.button("🤖 立即联网抓取最新结果", type="primary", use_container_width=True):
        with st.spinner("正在连接 4dlivetoday 接口..."):
            try:
                url = "https://4dlivetoday.com/api/v1/operators/magnum?limit=1"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                result = data["data"]["results"][0]
                draw_date = result["date"]
                first_prize = result["first"]
                
                st.success(f"✅ 抓取成功！日期: {draw_date}, 头奖: {first_prize}")
                
                check_res = supabase.table("predictions").select("id").eq("prediction_time", f"Auto_Fetch_{draw_date}").execute()
                
                if len(check_res.data) > 0:
                    st.warning(f"⚠️ {draw_date} 的数据已经存在于数据库中，无需重复插入。")
                else:
                    supabase.table("predictions").insert({
                        "prediction_time": f"Auto_Fetch_{draw_date}",
                        "model": "Auto_Fetch",
                        "top10": "",
                        "actual_prize": first_prize,
                        "is_hit": False
                    }).execute()
                    st.success(f"✅ 已将 {draw_date} 的头奖 {first_prize} 永久保存至云端！")
                    
            except Exception as e:
                st.error(f"❌ 抓取或保存失败: {e}")
