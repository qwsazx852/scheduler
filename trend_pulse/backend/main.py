from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import random
import math
from datetime import datetime, timedelta

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulatedDataEngine:
    def __init__(self):
        # Expanded Keyword Pool (50+ items to simulate a real monitoring system)
        self.dataset = [
            # Tech
            {"title": "iPhone 16 Pro Max", "cat": "科技", "base_vol": 120000},
            {"title": "Sam Altman OpenAI", "cat": "科技", "base_vol": 85000},
            {"title": "RTX 5090", "cat": "科技", "base_vol": 65000},
            {"title": "AI PC 推薦", "cat": "科技", "base_vol": 40000},
            {"title": "iOS 18 功能", "cat": "科技", "base_vol": 95000},
            {"title": "小米汽車 SU7", "cat": "科技", "base_vol": 70000},
            {"title": "Switch 2 爆料", "cat": "科技", "base_vol": 55000},
            {"title": "馬斯克 Starship", "cat": "科技", "base_vol": 60000},
            
            # Entertainment
            {"title": "New Jeans 回歸", "cat": "娛樂", "base_vol": 150000},
            {"title": "周杰倫 大巨蛋", "cat": "娛樂", "base_vol": 250000},
            {"title": "奧本海默 線上看", "cat": "娛樂", "base_vol": 45000},
            {"title": "Netflix 體能之巔2", "cat": "娛樂", "base_vol": 80000},
            {"title": "蔡依林 演唱會", "cat": "娛樂", "base_vol": 110000},
            {"title": "五月天 跨年", "cat": "娛樂", "base_vol": 180000},
            {"title": "韓韶禧 戀情", "cat": "娛樂", "base_vol": 200000},
            {"title": "YOASOBI 台灣", "cat": "娛樂", "base_vol": 130000},
            
            # Sports
            {"title": "大谷翔平 全壘打", "cat": "運動", "base_vol": 300000},
            {"title": "NBA 季後賽", "cat": "運動", "base_vol": 220000},
            {"title": "戴資穎 奧運", "cat": "運動", "base_vol": 280000},
            {"title": "魔獸 台灣籃球", "cat": "運動", "base_vol": 90000},
            {"title": "F1 日本大獎賽", "cat": "運動", "base_vol": 50000},
            {"title": "中信兄弟 大巨蛋", "cat": "運動", "base_vol": 160000},
            {"title": "李多慧 應援", "cat": "運動", "base_vol": 140000},
            
            # Life / News
            {"title": "颱風假 停班停課", "cat": "生活", "base_vol": 500000},
            {"title": "地震 警報", "cat": "生活", "base_vol": 450000},
            {"title": "腸病毒 症狀", "cat": "生活", "base_vol": 60000},
            {"title": "00940 配息", "cat": "生活", "base_vol": 190000},
            {"title": "電價 調漲", "cat": "生活", "base_vol": 110000},
            {"title": "蘇丹紅 名單", "cat": "生活", "base_vol": 130000},
            {"title": "媽祖遶境 直播", "cat": "生活", "base_vol": 100000},
            
            # Business
            {"title": "美國聯準會 降息", "cat": "商業", "base_vol": 550000},
            {"title": "輝達 財報", "cat": "商業", "base_vol": 420000},
            {"title": "台積電 股價", "cat": "商業", "base_vol": 380000},
            {"title": "比特幣 減半", "cat": "商業", "base_vol": 300000},
            {"title": "ETF 00940", "cat": "商業", "base_vol": 450000},
            {"title": "黃仁勳 演講", "cat": "商業", "base_vol": 400000},
            {"title": "房市 管制", "cat": "商業", "base_vol": 150000},
            {"title": "日幣 匯率", "cat": "商業", "base_vol": 250000},
            
            # Potential Breakouts (Low Volume but high interest potential)
            {"title": "某某網紅 翻車", "cat": "娛樂", "base_vol": 20000},
            {"title": "神秘 幾何圖形", "cat": "生活", "base_vol": 5000},
            {"title": "新興 AI 工具", "cat": "科技", "base_vol": 8000},
        ]

    def generate_growth(self):
        # Generate random growth between -10% and +800%
        # More volatility to simulate "Real-time" shifts
        return random.randint(-20, 800)

    def get_daily_trends(self):
        items = []
        
        # Shuffle dataset to simulate changing rankings
        current_data = random.sample(self.dataset, len(self.dataset))
        
        for i, kw in enumerate(current_data):
            # Dynamic Growth Simulation
            # Give some items massive "Breakout" growth regardless of base volume
            growth = self.generate_growth()
            
            # Boost specific "Low Volume" items to simulate "Potential Viral"
            if kw['base_vol'] < 30000 and random.random() > 0.7:
                growth = random.randint(500, 2000) # Massive spike for niche topics
            
            traffic_num = kw["base_vol"] * (1 + growth/100)
            traffic_display = f"{int(traffic_num // 1000)}K+"
            
            # Status Logic
            status = "Normal"
            if growth > 500:
                status = "Breakout" # 暴衝
            elif growth > 150:
                status = "Rising" # 上升中
                
            items.append({
                "rank": 0, # Will sort later
                "title": kw["title"],
                "category": kw["cat"],
                "traffic": traffic_display,
                "trafficNum": int(traffic_num),
                "growthRate": growth,
                "status": status,
                "description": f"AI 監測報告: 「{kw['title']}」在 {kw['cat']} 版面的討論熱度正在{'急速' if growth > 200 else '穩定'}攀升中...",
                "pubDate": datetime.now().isoformat(),
                "newsUrl": f"https://www.google.com/search?q={kw['title']}",
                "source": "TrendPulse Network"
            })
        
        # Sort by Growth Rate (User wants to see "Potential" first)
        items.sort(key=lambda x: x['growthRate'], reverse=True)
        
        # Assign Ranks based on Growth
        for i, item in enumerate(items):
            item['rank'] = i + 1
            
        return items

    def get_interest_over_time(self, keyword: str):
        # Generate 7 days of hourly data (7 * 24 = 168 points)
        data_points = []
        now = datetime.now()
        start_time = now - timedelta(days=7)
        
        # Create a unique-ish curve for each keyword based on hash
        seed = sum(ord(c) for c in keyword)
        random.seed(seed)
        
        base_val = random.randint(20, 50)
        volatility = random.randint(5, 20)
        
        for i in range(168):
            time_point = start_time + timedelta(hours=i)
            # Math magic: Sine wave + Random Noise + Trend
            # Trend: slightly increasing over time
            trend = (i / 168) * 20 
            # Seasonality: Daily cycle (24h)
            seasonality = math.sin((i / 24) * 2 * math.pi) * 15
            
            noise = random.randint(-volatility, volatility)
            
            value = int(base_val + trend + seasonality + noise)
            
            # Clamp between 0 and 100
            value = max(0, min(100, value))
            
            data_points.append({
                "time": time_point.strftime("%Y-%m-%d %H:%M"),
                "value": value
            })
            
        return data_points

engine = SimulatedDataEngine()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "TrendPulse AI Backend (Test Mode) 🚀"}

@app.get("/api/trends/daily")
def get_trends():
    """
    Returns simulated Daily Trends with Analysis Metrics.
    """
    return engine.get_daily_trends()

@app.get("/api/trends/interest/{keyword}")
def get_interest(keyword: str):
    """
    Returns simulated Interest Over Time data for charts.
    """
    return engine.get_interest_over_time(keyword)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
