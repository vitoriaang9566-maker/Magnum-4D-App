    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 整体背景：深邃的黑蓝色 */
    .stApp {
        background: linear-gradient(135deg, #05080E 0%, #111827 100%);
        color: #E5E7EB;
    }
    
    /* 顶部大标题：土豪金 */
    h1 {
        text-align: center;
        color: #FFD700;
        font-family: 'Georgia', serif;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        padding-bottom: 20px;
    }
    
    h2, h3 {
        color: #FFD700 !important;
        font-family: 'Georgia', serif;
    }
    
    /* 数据概览卡片：黑底金边 */
    .metric-card {
        background-color: rgba(17, 24, 39, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.1);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.3);
    }
    .metric-card h3 {
        color: #A0A5B1 !important;
        font-size: 14px !important;
        margin-bottom: 5px;
    }
    .metric-card p {
        color: #FFD700;
        font-size: 28px !important;
        font-weight: bold;
        margin: 0;
    }
    
    /* 推荐结果卡片：三种颜色的金边 */
    .result-card {
        background-color: rgba(17, 24, 39, 0.9);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    .result-freq { border: 1px solid rgba(0, 191, 255, 0.6); border-left: 5px solid #00BFFF; }
    .result-markov { border: 1px solid rgba(255, 215, 0, 0.6); border-left: 5px solid #FFD700; }
    .result-random { border: 1px solid rgba(255, 69, 0, 0.6); border-left: 5px solid #FF4500; }
    
    /* 按钮：红底金字 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #8B0000 0%, #FF4500 100%);
        color: #FFD700;
        border: 1px solid #FFD700;
        border-radius: 10px;
        padding: 15px;
        font-size: 18px !important;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }
    .stButton>button:hover {
        color: white;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }

    /* ====== 新增：黑金标签页 (Tabs) ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(17, 24, 39, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 8px;
        color: #A0A5B1;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 215, 0, 0.1) !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }

    /* ====== 新增：黑金提示框 (Success/Info) ====== */
    div[data-testid="stNotification"] {
        background-color: rgba(17, 24, 39, 0.95) !important;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.15);
    }
    div[data-testid="stNotification"] p {
        color: #FFD700 !important;
        font-weight: bold;
    }
