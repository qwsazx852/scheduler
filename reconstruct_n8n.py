import json

# Load the working file
with open('/Users/jun/.gemini/antigravity/scratch/n8n_fixed_active.json', 'r') as f:
    working_workflow = json.load(f)

# Define my System Message
my_system_message = """你是一个专业的「加油站排班经理」。你的职责是管理一份包含14位员工的 Google Sheet 班表，并协助将班表同步到 Google Calendar。

**资料库资讯**：
- Sheet ID: `1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y`
- Key Column: `日期` (格式如 2026/01/01)
- Employee Columns: 黃素珠, 賴桂蘭, 陳美娜, 吳誼婷, 楊依如, 陳彥銘, 黃榮壹, 吳靜蕙, 林群皓, 陳怡芯, 李巧如, 鄭靜慧, 陳昱勳, 林宏諺

**班别代码与时间对照 (Shift Codes)**：
- A1: 07:00 - 14:00
- D: 06:20 - 12:05
- D1: 06:20 - 12:05
- A2: 07:00 - 10:00
- C: 16:50 - 21:35
- B: 11:50 - 17:05
- B1: 11:50 - 17:05
- E: 16:50 - 21:00
- F: 10:00 - 17:00
- A2c: 07:00-10:00, 12:50-21:35
- B-: 11:50 - 18:00
- X / 休: 休假 (Leave)

**任务处理原则**：
1.  **查询 (Query)**：当用户问「某人那天上什么班」或「明天谁上班」，请使用 `Read Schedule` 工具。读取后请用自然的语言回答。
2.  **修改与同步 (Update & Sync)**：当用户要求「Request Update」或修改班表时：
    -   修改必须使用 `Update Schedule` 工具。
    -   **同步行事历**：如果修改的班别是「有效班别」(即非 X/休)，请**同时**使用 `Google Calendar` 工具(如果有連接)在当天建立事件。
        -   Summary: `[姓名] 班表: [班别代码]` (例如: 黃素珠 班表: D)
        -   Start/End Time: 根据上方的对照表，结合日期产生完整的 ISO 时间 (例如: 2026-01-20T06:20:00)。
        -   若代码不在对照表中，请仅更新 Sheet，并备注提醒用户未知班别。

现在的日期是：{{ $json.currentDate }}。请根据用户指令灵活操作。"""

# Define my Tools (Read Schedule, Update Schedule, Gemini Vision, Switch, etc.)
# Note: I'll start by just adding the Sheets tools and Webhook modifications to match the V4 logic but kept in valid structure.

# Helper to find node by name
def get_node(name, nodes):
    for node in nodes:
        if node.get('name') == name:
            return node
    return None

# 1. Update AI Agent Prompt
agent_node = get_node('AI Agent', working_workflow['nodes'])
if agent_node:
    agent_node['parameters']['options']['systemMessage'] = "=" + my_system_message

# 2. Define my Sheet Tools (Read and Update)
read_schedule_tool = {
    "parameters": {
        "toolDescription": "Read the schedule to find out who is working.",
        "operation": "getMany",
        "documentId": {
            "__rl": True,
            "value": "1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y",
            "mode": "list",
            "cachedResultName": "WorkSchedule",
            "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y/edit"
        },
        "sheetName": {
            "__rl": True,
            "value": "gid=0",
            "mode": "list",
            "cachedResultName": "Sheet1",
            "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y/edit#gid=0"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.googleSheetsTool",
    "typeVersion": 4.7,
    "position": [1340, 40],
    "id": "read-schedule-tool",
    "name": "Read Schedule",
    "credentials": {
        "googleSheetsOAuth2Api": {
            "id": "MNr7Hns0arjkklic",
            "name": "Google Sheets account"
        }
    }
}

update_schedule_tool = {
    "parameters": {
        "toolDescription": "Update the schedule. Use this to change shifts, mark leave, or swap duties.",
        "operation": "update",
        "documentId": {
            "__rl": True,
            "value": "1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y",
            "mode": "list",
            "cachedResultName": "WorkSchedule",
            "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y/edit"
        },
        "sheetName": {
            "__rl": True,
            "value": "gid=0",
            "mode": "list",
            "cachedResultName": "Sheet1",
            "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1eNkWVipmFheU-IzzbnflFlY5scRq07HPFt8ZzrTWI2Y/edit#gid=0"
        },
        "columns": {
            "mappingMode": "autoMapInputData",
            "matchingColumns": ["日期"],
            "schema": [
                {"id": "日期", "displayName": "日期", "required": False, "defaultMatch": True, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "黃素珠", "displayName": "黃素珠", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": False},
                {"id": "賴桂蘭", "displayName": "賴桂蘭", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": False},
                {"id": "陳美娜", "displayName": "陳美娜", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": False}
            ],
            "attemptToConvertTypes": False,
            "convertFieldsToString": False
        },
        "options": {}
    },
    "type": "n8n-nodes-base.googleSheetsTool",
    "typeVersion": 4.7,
    "position": [1500, 40],
    "id": "update-schedule-tool",
    "name": "Update Schedule",
    "credentials": {
        "googleSheetsOAuth2Api": {
            "id": "MNr7Hns0arjkklic",
            "name": "Google Sheets account"
        }
    }
}

# 3. Filter nodes (remove old tools)
nodes_to_keep = ['When chat message received', 'Google Gemini Chat Model', 'Simple Memory', 'AI Agent', 'Date & Time', 'Webhook', 'Edit Fields', 'HTTP Request']
filtered_nodes = [n for n in working_workflow['nodes'] if n['name'] in nodes_to_keep]

# 4. Add my tools
filtered_nodes.append(read_schedule_tool)
filtered_nodes.append(update_schedule_tool)

# 5. Rebuild Connections
# Start with existing connections but filter out removed nodes
new_connections = {}
# Copy existing connections if they relate to kept nodes
for node_name, conns in working_workflow['connections'].items():
    if node_name in nodes_to_keep:
        new_connections[node_name] = conns

# Connect new tools to AI Agent
# Note: In n8n JSON, the connections object defines "outputs" from a node.
# Since Read/Update Schedule are TOOLS, they connect TO the AI Agent's "ai_tool" input.
# BUT in the JSON structure, the TOOL node has the connection entry pointing to the Agent.
# Let's check n8n_fixed_active.json structure.
# "Wikipedia": { "ai_tool": [ [ { "node": "AI Agent", ... } ] ] }
new_connections['Read Schedule'] = {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
}
new_connections['Update Schedule'] = {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
}

# Update Workflow
working_workflow['nodes'] = filtered_nodes
working_workflow['connections'] = new_connections
working_workflow['name'] = "Dynamic Schedule Agent (Reconstructed)"

# Save
with open('/Users/jun/.gemini/antigravity/scratch/n8n_reconstructed.json', 'w') as f:
    json.dump(working_workflow, f, indent=4, ensure_ascii=False)

print("Successfully generated n8n_reconstructed.json")
