import streamlit as st
import csv
import datetime
from pathlib import Path
from collections import Counter

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

clean_file = Path("02_CLEAN_DATA/magnum_draws_cleaned.csv")
forward_dir = Path("07_FORWARD_TEST")
ledger_file = forward_dir / "forward_test_ledger.csv"

tab1, tab2 = st.tabs(["🔮 预测", "📊 对账"])

with tab1:
    st.markdown("<h2>生成下一期 Top 10</h2>", unsafe_allow_html=True)
    st.write("基于历史频率模型（Frequency）。")
    
    if st.button("🚀 立即生成并冻结", type="primary", use_container_width=True):
        with st.spinner("计算中..."):
            prizes = []
            if clean_file.exists():
                with clean_file.open("r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        prizes.append(row['prize_1'])
            
            freq = Counter(prizes)
            top10 = [num for num, count in freq.most_common(10)]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            forward_dir.mkdir(exist_ok=True)
            if not ledger_file.exists():
                with ledger_file.open("w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["预测日期", "开奖日期", "预测模型", "推荐Top10", "实际头奖", "是否命中Top10", "备注"])
            
            with ledger_file.open("a", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([now_str, "待开奖", "Frequency_Top10", ", ".join(top10), "", "", "等待开奖"])
            
            st.success(f"✅ 记录已生成 ({now_str})")
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
                if not ledger_file.exists():
                    st.error("找不到台账文件。")
                else:
                    rows = []
                    with ledger_file.open("r", encoding="utf-8-sig", newline="") as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                    
                    pending = [r for r in rows if r['实际头奖'] == ""]
                    
                    if not pending:
                        st.warning("没有待对账的预测。")
                    else:
                        hits = 0
                        for r in pending:
                            r['开奖日期'] = datetime.date.today().strftime("%Y-%m-%d")
                            r['实际头奖'] = actual_prize
                            if actual_prize in r['推荐Top10'].split(', '):
                                r['是否命中Top10'] = "是"
                                r['备注'] = "🎯 命中！"
                                hits += 1
                            else:
                                r['是否命中Top10'] = "否"
                                r['备注'] = "未命中"
                        
                        with ledger_file.open("w", encoding="utf-8-sig", newline="") as f:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
                        
                        total_predictions = len(rows)
                        total_hits = sum(1 for r in rows if r['是否命中Top10'] == "是")
                        hit_rate = (total_hits / total_predictions) * 100 if total_predictions else 0
                        
                        st.success(f"✅ 对账完成: {actual_prize}")
                        st.metric(label="累计命中率", value=f"{hit_rate:.2f}%")
                        st.write(f"总期数: {total_predictions} | 命中: {total_hits}")

    st.divider()
    st.markdown("<h2>📜 历史记录 (最近3期)</h2>", unsafe_allow_html=True)
    if ledger_file.exists():
        with ledger_file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            if len(data) > 0:
                # 倒序取最近 3 条
                recent = data[-3:][::-1]
                for r in recent:
                    status_color = "green" if r['是否命中Top10'] == "是" else "gray"
                    st.markdown(f"""
                    <div style='border: 1px solid #444; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                        <p style='margin: 0; font-size: 0.8rem; color: #aaa;'>预测时间: {r['预测日期']}</p>
                        <p style='margin: 5px 0; font-size: 1rem;'><b>预测号:</b> {r['推荐Top10']}</p>
                        <p style='margin: 0; font-size: 0.9rem; color: {status_color};'><b>开奖号:</b> {r['实际头奖']} | <b>{r['备注']}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("暂无记录。")
    else:
        st.info("尚未生成预测。")
