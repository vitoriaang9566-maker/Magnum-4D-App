import os
import requests
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    api_url = "https://4dlivetoday.com/api/v1/operators/magnum?limit=1"
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    result = data["data"]["results"][0]
    draw_date = result["date"]
    first_prize = result["first"]
    
    # 检查是否已存在
    check_res = supabase.table("predictions").select("id").eq("prediction_time", f"Auto_Fetch_{draw_date}").execute()
    
    if len(check_res.data) == 0:
        supabase.table("predictions").insert({
            "prediction_time": f"Auto_Fetch_{draw_date}",
            "model": "Auto_Fetch",
            "top10": "",
            "actual_prize": first_prize,
            "is_hit": False
        }).execute()
        print(f"Successfully inserted {draw_date}: {first_prize}")
    else:
        print(f"Data for {draw_date} already exists.")

except Exception as e:
    print(f"Error: {e}")
