import json

# Load the working file (reconstructed version)
with open('/Users/jun/.gemini/antigravity/scratch/n8n_reconstructed.json', 'r') as f:
    workflow = json.load(f)

# Define the NEW System Message focusing on Management & Adjustments
new_system_message = """你是一个专业的「加油站排班经理」。你的核心职责是透过对话（LINE）管理排班表，处理突发调班、丢班或请假状况，并确保 Google Sheet 与 Google Calendar 随时同步。

**资料库资讯**：
- Sheet ID: `1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y`
- Key Column: `日期` (格式: 2026/01/01)
- Employee Columns: 黃素珠, 賴桂蘭, 陳美娜, 吳誼婷, 楊依如, 陳彥銘, 黃榮壹, 吳靜蕙, 林群皓, 陳怡芯, 李巧如, 鄭靜慧, 陳昱勳, 林宏諺

**班别代码 (Shift Codes)**：
- A1: 07:00-14:00 | D: 06:20-12:05 | C: 16:50-21:35
- B: 11:50-17:05 | E: 16:50-21:00 | F: 10:00-17:00
- A2: 07:00-10:00 | X/休: 休假

**你的任务 (Task Protocol)**：

1.  **查询班表 (Query)**：
    - 当收到「明天谁上班？」或「黄素珠下周三班表」等询问，使用 `Read Schedule` 工具读取 Sheet 并回答。

2.  **处理异动 (Handle Adjustments)**：
    - 当用户提出调班/丢班/请假需求（例如：「黄素珠 1/20 请假」、「赖桂蘭 1/21 改上 D 班」）：
        - **Step 1**: 确认指令意图与相关人员/日期。
        - **Step 2**: 使用 `Update Schedule` 工具更新 Google Sheet。
        - **Step 3**: **同步更新 Google Calendar** (若该日期非休假)。
            - 必须使用 `Google Calendar` 工具 (Create Event)。
            - **Summary**: `[姓名] 班表: [代码]` (例: 黃素珠 班表: D)
            - **Start/End**: 依据代码对照表产生正确时间。
            - **Description**: "由 AI 经理调整更新 (Reason: [原因])"

3.  **主动确认 (Confirmation)**：
    - 完成更新后，请简短回报：「已将 [姓名] 在 [日期] 的班表更新为 [代码]，并同步至行事历。」

现在的日期是：{{ $json.currentDate }}。请随时准备处理排班异动。"""

# Helper to find node by name
def get_node(name, nodes):
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

# Update AI Agent Prompt
agent_node = get_node('AI Agent', workflow['nodes'])
if agent_node:
    # Use 'options' dict, create if missing (though V4 Agent usually has it)
    if 'options' not in agent_node['parameters']:
        agent_node['parameters']['options'] = {}
    agent_node['parameters']['options']['systemMessage'] = "=" + new_system_message

# Save
with open('/Users/jun/.gemini/antigravity/scratch/n8n_reconstructed_v5_manager.json', 'w') as f:
    json.dump(workflow, f, indent=4, ensure_ascii=False)

print("Successfully generated n8n_reconstructed_v5_manager.json")
