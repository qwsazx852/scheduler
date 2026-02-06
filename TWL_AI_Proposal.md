# 企業 AI 系統架構整合與自動化執行計畫書 (Proposal)

**提案人**: [您的名字/團隊]
**日期**: 2026/02/05
**提交對象**: TWL HR & 技術審核團隊

---

## 1. 執行摘要 (Executive Summary)

本計畫旨在為貴公司導入先進的 **Agentic AI (代理人人工智慧)** 技術，構建一個能跨越 **Legacy ERP (API/GUI)** 與 **通訊協作平台 (DingTalk/Google)** 的智慧混合自動化架構。

我們採用 **「效率優先 (Efficiency First)」** 的混合架構，以 API 串接為主，視覺操作為輔。本計畫考核期將 **聚焦於「智慧訂單自動化」單一場景** 進行深度驗證，確保交付具備量化效益的 POC 成果。

### 1.1 預期效益與 KPI (Key Performance Indicators)
| 指標項目 | 當前現狀 (As-Is) | 預期目標 (To-Be) |
| :--- | :--- | :--- |
| **訂單處理時間** | 人工輸入約 5~10 分鐘/張 | **標準單 < 30 秒/張** (異常單除外) |
| **資料正確率** | 人工打字錯誤率約 1~3% | **100%** (AI 預填 + 異常時人工介入) |
| **系統覆蓋率** | 僅支援標準單，特殊單需全人工 | **100%** (API 處理標準單 + Copilot 處理客製欄位) |

---

## 2. 系統架構設計 (System Architecture)

針對貴公司複雜的軟體生態，我們將 **Citrix Workspace** 定義為核心操作場域，涵蓋所有研發與生產工具 (**SolidWorks / Office / MPLab IDE / Bartender / 鼎新 ERP / Altium / 智能物流**)。本架構將整合 **DingTalk** 與 **Google Enterprise**，形成三層式自動化體系：

```mermaid
graph TD
    %% Define Styles
    classDef brain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef trigger fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef action fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef legacy fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,stroke-dasharray: 5 5;

    subgraph "Trigger Layer (感知觸發)"
        User[🤵 業務人員 (Uncle)]:::trigger
        Email[📧 Google Mail (PDF訂單)]:::trigger
        Ding[💬 DingTalk (手機指令)]:::trigger
        User -->|轉寄訂單| Email
        User -->|發送指令| Ding
    end

    subgraph "Reasoning Layer (AI 決策核心)"
        Brain[🧠 Enterprise AI Core]:::brain
        Parser[📄 Visual RAG 解析引擎]:::brain
        Router[🔀 意圖路由 (Router)]:::brain
        
        Email --> Parser
        Ding --> Brain
        Parser --> Brain
        Brain --> Router
    end

        graph TD
            %% Styles
            classDef trigger fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
            classDef brain fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
            classDef action fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
            classDef output fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;

            %% 1. Input Layer
            subgraph Input["1. Trigger (需求觸發)"]
                User["🤵 業務人員 / 郵件"]:::trigger
            end

            %% 2. Intelligence Layer
            subgraph Core["2. AI Analysis (決策大腦)"]
                Sherry["🧠 Enterprise AI Core"]:::brain
                Parser["📄 PDF 識別引擎"]:::brain
                Input --> Sherry
                Sherry --> Parser
                Parser --> Sherry
            end

            %% 3. Execution Layer (Hybrid)
            subgraph Exec["3. Hybrid Action (分流執行)"]
                direction TB
                
                %% Path A
                subgraph PathA["路徑 A: 標準 API (快)"]
                    API["🔌 標準 ERP API"]:::action
                end

                %% Path B
                subgraph PathB["路徑 B: Citrix 虛擬桌面 (全能)"]
                    Copilot["🤖 Desktop Copilot"]:::action
                    
                    subgraph Apps["受控軟體 (Citrix Apps)"]
                        ERP["鼎新 ERP / 物流"]
                        Design["SolidWorks / Altium"]
                    end
                    
                    Copilot -->|操作/讀取| Apps
                end
            end

            %% 4. Result Layer
            subgraph Outcome["4. Outcome (結果歸檔)"]
                DB[("🗄️ 公司資料庫")]:::output
                Sheet["📊 Google Sheet 週報"]:::output
                Ding["📱 釘釘完工通知"]:::output
            end

            %% Connections (Main Flow)
            Sherry -->|規則分流| API
            Sherry -->|例外處理| Copilot
            
            API --> DB
            Apps --> DB

            %% The "Then What?" Answer
            API -->|成功日誌| Sheet
            Copilot -->|執行截圖| Sheet
            Sheet -->|摘要推播| Ding
```

### 2.1 核心大腦層 (AI Brain Integration)
*   **決策中樞**: 部署企業級 LLM 作為邏輯核心，負責意圖識別與任務調度。
*   **通訊整合**:
    *   **Google Workspace**: 深度整合 Mail/Drive (API)。
    *   **釘釘 (DingTalk)**: 透過 Webhook 串接通知，負責「異常回報」與「人工審核」。

> **範疇聲明**: 下列 SolidWorks/Altium/Bartender 等外圍系統整合為 **第二階段 (Phase 2) 架構願景**，本次考核期將保留其擴充接口，不列入本次 POC 交付範圍。

### 2.2 混合整合層 (Hybrid Integration Layer) - **Efficiency First**
針對 Citrix 與 ERP 環境，我們採取「效率優先」的分級整合策略，避免非必要的視覺操作：
*   **Tier 1 (優先): 標準 API / 資料庫對接**
    *   針對 T100/E10 等新版模組，優先使用 Web API 進行資料交換，確保速度與準確度 ( < 1s 延遲)。
*   **Tier 2 (補位): Visual Desktop Copilot (桌面助手)**
    *   **啟動方式**: **人機協作 (Attended)**。由使用者開啟 ERP 視窗，AI 透過 **Local Python Agent** 接手模擬滑鼠鍵盤輸入。
    *   **定位**: 作為 API 無法覆蓋時的「備援機制」，避免開發高風險的底層 Hook 腳本。

### 2.3 領域知識與自動化層 (Domain Knowledge & Automation)
針對特定軟體特性，建立專屬的 **AI 處理模組**：
*   **SolidWorks (RAG 知識庫)**: 建立「設計規範知識庫」，AI 自動檢索 ISO/CNS 標準與公司內部設計守則，輔助工程師決策。
*   **Altium / MPLab (BOM 智慧稽核)**: 導入「BOM 結構化比對」，由 Python 解析電路圖 BOM 並與 ERP 料號進行 **欄位級 (Field-level) 一致性稽核**，精準預防備料錯誤。
*   **Bartender (AI 列印自動化)**: 導入「AI 標籤驅動」，AI 讀取訂單後自動生成 **Commander Script (列印指令腳本)**，直接驅動 Bartender 套表列印，取代人工開啟檔案。
*   **鼎新 ERP / 智能物流 (Copilot)**: 建立操作手冊索引，讓 AI 成為 24hr 的 ERP 小幫手。

### 2.4 技術完備性驗證 (Capability Proof)
雖然 API 為首選，但我們已驗證最具挑戰性的 **「視覺備援方案」**，確保在 API 失效時系統仍能運作：
*   **Legacy 支援能力**: 已驗證可透過 AI 識別老舊 Conductor ERP 介面結構。
*   **極端情境對應**: 即使面對無 API 的封閉環境 (Citrix)，仍具備托底 (Fallback) 的自動化執行能力。

---

## 3. 考核期執行目標：智慧訂單自動化 (Smart Order Processing)

驗證場景：**非標準訂單 (PDF/Image) -> Hybrid ERP 自動建單 (API/Copilot)**

> **註**：考量考核初期環境連線權限與軟體授權限制，本 POC 將採用 **「數位雙生 (Digital Twin) 模擬驗證」** 策略。我們將建置 **Mock ERP** 與 **Mock CAD** 環境，在不影響正式區的前提下，驗證 AI 的「邏輯判斷」與「自動化路徑」是否正確。

### 自動化流程 (POC 模擬定義)
1.  **觸發**: AI 監聽 Google Mail，識別訂單。
2.  **讀取**: Visual RAG 萃取料號、數量、交期。
3.  **操作 (模擬對接)**:
    *   **ERP API**: 呼叫自建的 **Mock API Server** (模擬 T100 回傳成功/失敗訊號)。
    *   **Desktop Copilot**: 操作本機 **模擬視窗 (Dummy APP)**，驗證 AI 的滑鼠控制與截圖防護機制 (證明 Windowguard 有效)。
4.  **填寫與驗證 (Human-in-the-loop)**:
    *   AI 模擬輸入資料。
    *   **[關鍵檢核 (例外處理)]**: 僅在 AI 信心度 < 95% 或 API 回傳錯誤時觸發：
        *   系統暫停輸入。
        *   **API 模式**: 發送 **「資料預覽卡片 (JSON Card)」** 至釘釘 (顯示萃取的料號/數量)。
        *   **視覺模式**: 發送 **「ERP 畫面截圖」** 至釘釘 (顯示錯誤視窗)。
        *   人工點擊「確認」後，AI 繼續執行；點擊「修正」則由人工接手。
5.  **回報**: 完成後，發送 ERP 單號至釘釘。
6.  **歸檔 (Auditing)**:
    *   系統自動將「訂單資訊、處理結果(成功/失敗)、ERP單號」寫入 **Google Sheets**。
    *   作為週報表數據來源，並供後續稽核 (Audit Trail) 使用。

---

## 4. 資料隱私與資安承諾 (Security & Compliance)

鑑於貴公司產業特性，我們將「資料安全」視為最高指導原則：

1.  **數據不落地 (Data Privacy)**:
    *   所有敏感數據 (SolidWorks 圖檔、ERP 成本、Altium 設計圖) 僅在 **公司內網/Citrix 環境** 中進行處理，不流出企業邊界。
    *   我們承諾：**絕不將貴公司之任何核心文件用於外部 AI 模型之公開訓練** (採用 Enterprise API 標準，如 Google Vertex AI / Azure OpenAI)。所有 API 呼叫皆簽署「Zero Data Retention (零資料留存)」協議。
2.  **加密傳輸**:
    *   所有通訊節點 (n8n, Python Agent, DingTalk) 皆強制採用 **TLS 1.3** 加密協定，防止中間人攻擊。
3.  **權限控管與視窗鎖定**:
    *   AI Agent 操作權限嚴格比照員工帳號。
    *   **Windowguard 機制**: 透過 **Win32 API (Handle Lock)** 技術，視覺辨識僅針對「ERP 特定應用程式視窗」，絕不截取桌面背景或其他通訊軟體畫面，確保隱私合規。

---

## 5. 執行時程規劃 (4-Week Roadmap)

| 階段 | 重點任務 | 交付成果 |
| :--- | :--- | :--- |
| **Week 1** | **架構與資安** | 環境搭建、**API 欄位映射分析 (Gap Analysis)**、資安加密通道設置。 | 環境安檢 / API 規格報告 |
| **Week 2** | **混合技能開發** | 優先串接 ERP API，並針對無 API 模組開發 **Visual Agent** 備援機制。 | API 串接/視覺識別 Prototype |
| **Week 3** | **整合與人機協作** | 串聯全流程，並實作 **「釘釘人工審核 (Human-in-the-loop)」** 機制。 | 整合測試報告 |
| **Week 4** | **驗收交付** | 壓力測試、操作手冊撰寫、災難復原演練 (Citrix 斷線處置)。 | **正式驗收報告** |

---

## 6. 實地驗證資源需求 (On-site POC Requirements)
若考核通過，進入第二階段 **真實環境測試 (Real-world Pilot)** 時，需請貴司 IT 部門協助提供以下資源，以確保系統能順利對接：

1.  **測試帳號 (Service Account)**:
    *   一組僅具備 **「建立訂單」** 與 **「查詢庫存」** 權限的 ERP / Citrix 測試帳號 (建議非管理員權限)，以驗證最小權限原則 (Least Privilege)。
2.  **網路白名單 (Firewall Allowlist)**:
    *   開放 POC 執行主機 (或指定 IP) 對內網 ERP API 的連線權限。
3.  **API 規格文件 (Interface Specs)**:
    *   若需測試 Tier 1 API 整合，需提供 T100/E10 訂單模組之 Swagger / WSDL 定義檔。
4.  **執行環境 (Runtime Environment)**:
    *   若需進行長時間壓力測試 (72hr+)，建議提供一台 **虛擬機 (VM)** 或獨立 PC 部署 Agent，避免占用個人開發電腦資源。

---

**結論**:
本計畫將透過導入「API 效率優先 + AI 視覺備援」的混合架構，在確保資安無虞與系統穩定的前提下，靈活解決 Legacy ERP 的自動化難題，為貴公司建立可持續發展的智慧製造體系。
