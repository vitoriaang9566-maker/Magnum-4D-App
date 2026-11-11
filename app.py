    # ================= 这里开始画图 (累计柱状图) =================
    st.markdown("<h2>📊 模型累计命中对比</h2>", unsafe_allow_html=True)
    
    try:
        res = supabase.table("predictions").select("*").neq("actual_prize", "").execute()
        all_data = res.data
        
        df = pd.DataFrame(all_data)
        df = df[df['model'].isin(['Frequency', 'Markov', 'Random'])]
        
        if not df.empty:
            stats = df.groupby('model')['is_hit'].sum().reset_index()
            
            # 确保三个模型都有数据，没有的默认为 0
            models = ['Frequency', 'Markov', 'Random']
            for m in models:
                if m not in stats['model'].values:
                    stats = pd.concat([stats, pd.DataFrame({'model': [m], 'is_hit': [0]})], ignore_index=True)
            
            colors = {'Frequency': '#00BFFF', 'Markov': '#FFD700', 'Random': '#FF4500'}
            
            fig = go.Figure()
            for model in models:
                model_stat = stats[stats['model'] == model]
                if not model_stat.empty:
                    val = model_stat['is_hit'].values[0]
                    fig.add_trace(go.Bar(
                        x=[model],
                        y=[val],
                        name=model,
                        marker_color=colors[model],
                        text=[val],
                        textposition='auto',
                    ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E5E7EB'),
                yaxis=dict(title='累计命中次数', showgrid=True, gridcolor='rgba(255,255,255,0.1)', rangemode='tozero'),
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("还没有对账数据，先去对账吧！")
    except Exception as e:
        st.error(f"读取图表数据失败: {e}")
