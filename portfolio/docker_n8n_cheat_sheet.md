# 🐳 Docker & n8n 架構師指南：從入門到落地

這份指南不僅是為了面試，更是為了讓你具備「維護一個穩定 AI 自動化系統」的真實能力。
當你從「寫腳本」進階到「管架構」，你需要懂以下這些：

---

## 1. Docker 專業能力 (Containerization)

### 核心觀念：為何要用 Docker？
*   **環境一致性 (Consistency)**：解決 "It works on my machine" 的千古難題。你用 Docker 跑的 n8n，跟在 AWS 上跑的 n8n 環境是一模一樣的。
*   **微服務化 (Microservices)**：你的 AI Agent 系統其實是由 `n8n` (邏輯) + `PostgreSQL` (記憶) + `Python API` (工具) 組成的。Docker 讓這些服務各司其職，互不干擾。

### 必備技能 Checklist
1.  **Docker Compose (編排)**
    *   **認知**：不要再用手打 `docker run -p 5678:5678...` 這種指令了。
    *   **專業做法**：一定要會寫 `docker-compose.yml`。這是一份「建築藍圖」，定義了所有服務怎麼啟動、網路怎麼連、密碼環境代號是什麼。
    *   **面試題**：「你的 n8n 系統重開機後會自動啟動嗎？」-> 回答：「會，我在 Compose 裡設定了 `restart: always`。」

2.  **Volume 持久化與備份**
    *   **認知**：Container 是「隨洗隨丟」的。
    *   **專業做法**：將 `.n8n` 資料夾掛載到 Host (本機) 或是 Docker Volume。
    *   **維運**：備份不只是備份 JSON 檔，還要備份整個 `sqlite` 檔或是定時 `pg_dump` (如果用 Postgres)。

3.  **除錯 (Debugging)**
    *   `docker logs -f n8n`：看 n8n 吐什麼錯誤 (即時 Log)。
    *   `docker exec -it n8n /bin/sh`：像駭客一樣「進入」容器裡面檢查檔案或網路連線。

---

## 2. n8n 自架專業能力 (Self-Hosting Proficiency)

### 資料庫選擇：SQLite vs PostgreSQL
*   **初階 (SQLite)**：n8n 預設值。適合個人、測試。缺點是當 10 個 Webhook 同時進來，因為檔案鎖定 (File Lock)，系統會變慢甚至噴 Error。
*   **進階 (PostgreSQL)**：適合生產環境 (Production)。
*   **專業回答**：「目前 MVP 階段我使用 SQLite，但我的架構考量到了擴展性，未來若流量變大，我會將 Backend DB 遷移至 PostgreSQL 以支援高併發 (High Concurrency)。」

### 環境變數管理 (Result-Oriented Security)
*   **認知**：絕對不要在 n8n 的 UI 節點裡面手打 API Key。
*   **專業做法**：
    1.  建立 `.env` 檔案 (存放 `GOOGLE_API_KEY=AIzA...`)。
    2.  在 Docker Compose 裡引用 `env_file: .env`。
    3.  在 n8n 裡使用 `{{ $env.GOOGLE_API_KEY }}` 讀取。
*   **優點**：當你要換 Key，只要改一個檔案，重啟 Docker，不用進去幾十個 Workflow 一個個改。這叫做**可維護性 (Maintainability)**。

---

## 3. 網路與穿透技術 (Networking & Tunneling)

這裡你提到的 "grok" 應該是指 **ngrok** (或是類似的 Cloudflare Tunnel)。

### 為什麼需要 Tunnel？
*   **現狀**：你的 n8n 跑在私網 (Private IP, e.g., 192.168.x.x)，外部的 LINE Server 找不到你。
*   **功能**：Tunnel 軟體會在你的電腦與公網伺服器之間建立一條加密的「海底隧道」。

### ngrok vs 生產環境方案
| 特性 | ngrok (Free) | Cloudflare Tunnel (Pro) | VPS + Nginx (Expert) |
| :--- | :--- | :--- | :--- |
| **用途** | 開發測試、Demo | 正式上線、家用伺服器 | 企業級自建 |
| **網址** | 隨機亂碼 (每次變) | 固定網域 (YourName.com) | 固定 IP / 網域 |
| **穩定性** | 連線數限制 | 極高 (CDN 加速) | 極高 |

*   **專業認知**：
    *   「我現在用 ngrok 是為了快速開發與驗證 (POC)。」
    *   「如果在正式環境 (Production)，我不建議用 ngrok，可能會因為連線數限制導致掉單。」
    *   「未來我會建議使用 **Cloudflare Tunnel** (Zero Trust)，它不用開防火牆 Port，安全性更高，且有固定網址，LINE Webhook 不用一直改。」

---

## 4. 面試模擬題 (Q&A)

**Q: 你的 n8n 為什麼要自己架，不用雲端版？**
> **A:**
> 1.  **成本控制**：n8n 雲端版是用 Workflow執行次數計費，自架可以用最低成本跑無限次數。
> 2.  **數據隱私**：如果是處理敏感個資或公司內部數據，自架 Docker 可以確保資料完全不流出內網，符合資安規範。
> 3.  **整合強**：我可以直接在 Docker 內呼叫本地的 Python Script (如我的 TTS Server)，這是雲端版做不到的。

**Q: 你怎麼備份你的系統？**
> **A:** 我有用 Docker Volume 將資料掛載出來。我會定期用 Script 備份該資料夾，並且將所有的 Workflow JSON 檔透過 Git 版本控制，推送到 GitHub。即便伺服器爆炸，我也能在一小時內用 `docker-compose up` 在另一台機器滿血復活。
