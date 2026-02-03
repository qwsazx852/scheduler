import json
import datetime
import sys

# ==========================================
# 核心價值展示：IE 多目標排程演算法 (模擬)
# Context: 工業工程 (IE) 碩士論文展示
# Logic: 考慮產能限制、換線成本、加班費，計算最佳交期
# ==========================================

def load_input(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Fallback for demo if file not found
        return {
            "quantity": 500,
            "requested_date": "2026-02-28"
        }

def calculate_optimal_schedule(rfq_data):
    """
    模擬多目標決策過程：
    Objective 1: 準時交貨 (Minimize Delay)
    Objective 2: 最小化成本 (Minimize Cost - OT/Setup)
    """
    
    qty = rfq_data.get('quantity', 0)
    req_date_str = rfq_data.get('requested_date', datetime.datetime.now().strftime('%Y-%m-%d'))
    req_date = datetime.datetime.strptime(req_date_str, '%Y-%m-%d').date()
    
    # 1. 讀取目前產能狀態 (Mock Data)
    # 假設目前產線在 2/28 前都滿載
    current_capacity_end_date = datetime.date(2026, 2, 28)
    
    # 2. 計算生產所需時間 (Lead Time Calculation)
    # 假設產能速率: 100 pcs / day
    production_rate = 100 
    days_needed = max(1, qty // production_rate)
    
    # 3. 方案 A: 強制加班趕工 (Meet Deadline)
    # 加班費成本 +30%
    completion_date_A = max(datetime.date.today(), req_date) # 假設硬塞
    cost_A = qty * 10 * 1.3 # Base cost $10 * 1.3
    is_delayed_A = False
    
    # 4. 方案 B: 正常排程 (Optimize Cost)
    # 從目前滿載日之後開始排
    start_date_B = current_capacity_end_date + datetime.timedelta(days=1)
    completion_date_B = start_date_B + datetime.timedelta(days=days_needed)
    cost_B = qty * 10 * 1.0 # Base cost
    
    # 5. 決策邏輯 (The "Algorithm")
    # 如果 方案 B (正常排) 比 客戶要求 晚，但成本省很多，則推薦 B
    # 在此模擬中，我們比較一下
    
    recommendation = {}
    
    if completion_date_B > req_date:
        # 發生延遲，計算延遲天數
        delay_days = (completion_date_B - req_date).days
        
        # IE 決策：如果延遲 < 5天 且 成本省 > 20%，推薦延遲方案
        if delay_days < 5:
            recommendation = {
                "strategy": "COST_OPTIMAL",
                "suggested_date": completion_date_B.strftime('%Y-%m-%d'),
                "original_date": req_date_str,
                "cost_estimate": cost_B,
                "saving": cost_A - cost_B,
                "message": f"建議交期調整為 {completion_date_B}，可避開產能尖峰，節省 {(cost_A - cost_B):.0f} 元成本 (約 {((cost_A-cost_B)/cost_A)*100:.0f}%)。"
            }
        else:
            recommendation = {
                "strategy": "DEADLINE_PRIORITY",
                "suggested_date": req_date_str,
                "cost_estimate": cost_A,
                "message": "為滿足交期，需安排緊急加班產線，成本將增加 30%。"
            }
    else:
        recommendation = {
            "strategy": "STANDARD",
            "suggested_date": req_date_str,
            "cost_estimate": cost_B,
            "message": "產能充足，可如期交貨。"
        }

    return recommendation

if __name__ == "__main__":
    # 若有參數則讀取，否則讀取預設 mock testing
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/Users/jun/.gemini/antigravity/scratch/mock_rfq_input.json'
    
    data = load_input(input_file)
    result = calculate_optimal_schedule(data)
    
    # Output JSON to stdout (for N8n to capture)
    print(json.dumps(result, ensure_ascii=False, indent=2))
