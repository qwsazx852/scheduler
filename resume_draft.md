# 張晉嘉 (Jin-Jia Zhang / Jimmy)
**AI 落地應用工程師 (AI Implementation Engineer)**
📞 0981-527-023 | ✉️ qwsazx852@gmail.com | 📍 屏東/遠端/台南/高雄/台中

## 👨‍💻 個人簡介 (Professional Summary)

具備深厚的**演算法工程背景**與兩年國家科學委員會計畫實作經驗。專注於 **AI 應用落地**，擅長結合 Low-Code (n8n) 與 Python 技術，將複雜的業務邏輯轉化為由 AI 驅動的自動化解決方案。

精通 **RAG (檢索增強生成)** 知識庫建構、**Multi-LLM 策略調度** 與 **API 逆向工程**。擁有工業工程碩士學位，具備將數學理論轉化為工程應用的能力，能將 **多目標最佳化演算法 (NSGA-II/GA/PSO)** 與現代 LLM Agent 結合，解決具備實務限制條件的複雜決策問題。

## 🚀 核心技能 (Key Skills)

### 🤖 AI Agent & RAG 架構
*   **Agent 編排**: n8n, LangChain, **Multi-LLM 策略** (Gemini 3.0 Pro + Groq LPU 混合調度)
*   **私有知識庫**: **Pinecone**, Gemini Embeddings, 語義檢索流程設計

### ⚙️ 自動化與系統集成
*   **內容管線**: RSS -> AI 摘要 -> 自建 Python TTS Server -> LINE 多模態推播
*   **基礎設施 (DevOps)**: **Docker 自架 (Self-hosted n8n)**, **ngrok** (本地服務穿透與 Webhook 測試), 容器化部署管理
*   **逆向工程**: 分析非公開 API (如人力銀行數據) 實現高效數據採集
*   **API 串接**: Notion API, LINE Messaging API, Google Workspace

### 🧮 演算法決策與最佳化
*   **啟發式演算法**: **NSGA-II** (多目標優化), **Genetic Algorithm (GA)**, **PSO** (粒子群), **Ant Colony (ACO)**, 蒙地卡羅模擬
*   **工業應用場景**:
    *   **線平衡 (Line Balance)**: 型II/型III問題算法優化，提升設備生產率
    *   **非同步平行拆裝 (ASDP)**: 工作站排程設計與機械手臂路徑優化
    *   **永續製造決策**: 運用 **3R1T** 原則 (Reuse/Recycle/Remanufacture/Trash) 設定懲罰值，計算最佳拆裝終止點，權衡「最小碳足跡」與「最佳企業盈利」。

### 💻 後端開發
*   **語言與框架**: Python (FastAPI/Flask), MATLAB
*   **系統設計**: RESTful API 設計, 多目標決策系統模擬與分析

## 💼 專業專案經歷 (Selected AI Projects)

### 1. Sherry: 多模態 AI 個人助理系統 (n8n + RAG + Multi-Modal)
*核心技術：n8n, Python, Gemini 1.5, Pinecone, Line API, Azure TTS*

*   **RAG 知識庫實作**: 利用 **Pinecone** 與 **Gemini Embeddings** 建構個人私有知識庫，導入 Recursive Character Text Splitter 優化檢索精準度，有效解決長文本上下文限制，將 Agent 幻覺率大幅降低。
*   **全自動新聞廣播系統**: 整合 RSS 訂閱源，透過 JavaScript (n8n Code Node) 進行即時數據清洗，串接自建 **Python TTS Server** 發送語音訊息，實現端到端 (E2E) 的資訊減量解決方案。
*   **智慧求職代理人 (Career Agent)**:
    *   **API 逆向工程**: 成功分析並串接求職平台非公開 API，繞過網頁爬蟲限制，效率提升 **300%**。
    *   **決策管線**: 實作「職缺篩選 -> AI 評分 (Scorer) -> 客製化應徵信 (Tailor)」的完整自動化流程，並自動寫入 Notion 進行追蹤。

### 2. 工業級智慧排班決策系統 (Algorithm + Streamlit + Python)
*核心技術：Python, Streamlit, Heuristic Algorithms (GA/PSO)*

*   **啟發式演算落地**: 將碩士研究之 **GA/PSO 演算法** 應用於餐飲/零售排班場景，成功處理排班中的複雜人力限制條件（Hard Constraints）與公平性指標（Soft Constraints）。
*   **可視化決策工具**: 使用 **Streamlit** 開發互動式 UI，設計獨創的「逐步除錯模式 (Step-by-Step Debug Mode)」，實現演算法決策黑盒子的透明化，大幅縮短人工調整時間。

### 3. 多目標 ESG 永續製造模型 (MATLAB)
*核心技術：MATLAB, NSGA-II, Mathematical Modeling*

*   **數學建模**: 建立「企業利潤最大化 × 碳足跡最小化」之**雙目標優化模型**。
*   **效能評估**: 使用 **NSGA-II 演算法** 求得 Pareto 最優解集，並以 Hypervolume 指標驗證在降低碳排的前提下，仍能維持企業獲利之實務潛力。

## 🛠 工作經驗 (Professional Experience)

**國家科學委員會 (NSTC) | 研究助理**
*2022/6 – 2024/7*
*   負責計畫書撰寫與演算法原型開發，將複雜的 ESG 永續製造問題轉化為可執行之 Python/MATLAB 程式。
*   實作多種啟發式演算法，建立 Benchmark 評估流程，優化收斂速度並降低運算成本。

**鼎新電腦 (Digiwin) | ERP 實習顧問**
*2021/9 – 2022/2*
*   協助企業導入與維護 ERP 系統，負責將客戶的**業務需求 (Business Requirements)** 轉化為精確的**系統邏輯與流程設定**。
*   累積企業級軟體導入經驗，熟悉 B2B 系統落地流程與異常排除。

## 🎓 學歷 (Education)

**國立勤益科技大學 | 工業工程與管理系 碩士**
*2022/7 – 2024/7*
*   研究領域: 多目標最佳化、決策模型設計、演算法效能權衡

## 🏆 專業證照 (Certifications)

*   **澳洲 FTMO 操盤手認證 (2024)**: 具備嚴格的風險控管、資金管理與量化策略回測能力。
*   **品質管理技術師證照 (CIIE)**: 熟悉品質管理流程與數據分析工具。
*   **SolidWorks 研習證明**

---

## 📖 自傳 (Autobiography)

### 【解決問題，享受挑戰：我是工程師張晉嘉】
樂觀與積極，是我面對挑戰時的一貫態度。在求學生涯中，我發現自己最大的熱情在於「解決問題」，並享受尋找最佳解的過程。碩士期間，我鑽研「啟發式演算法 (Heuristic Algorithms)」，不僅是為了完成論文，更是為了探索如何利用數學與邏輯，將產線生產效能推向極致。為了提升求解效率，我養成閱讀國際期刊的習慣，不僅重現前輩的方法，更嘗試改良算法結構，這種「知其然，更知其所以然」的研發精神，奠定了我紮實的技術底蘊。

### 【擁抱 AI ：從學習者到駕馭者】
在這個 AI 快速迭代的時代，我保持著強烈的危機感與求知慾。除了正規的程式訓練，我積極進修類神經網路架構，並將 ChatGPT 與各類 AI Agent 工具視為提升效率的「副駕駛」。我深信，唯有懂得駕馭 AI，才能保持「今天比昨天更進步一點」的競爭力。這種持續進化的心態，使我能迅速掌握 n8n、RAG 等新技術，並將其應用於實際專案中。

### 【投資心法與工程思維的交匯】
程式開發之外，我對投資領域同樣充滿熱情。投資市場反映著複雜的人性與高度的不確定性，這與解決工程難題有著異曲同工之妙——都沒有唯一的「標準答案」，只有當下的「最佳決策」。
憑藉著對技術分析與基本面的鑽研，我通過了嚴格的 **澳洲自營商 (FTMO) 二階段考試**，獲得操作資金。這段經歷不僅證明了我的邏輯分析能力，更鍛鍊出我**「堅定信念」**與**「復盤調整」**的強大心理素質。面對程式 Bug 或專案瓶頸時，我同樣以此心態面對：失敗就分析原因、調整參數，直至找到成功路徑。

---

## 📖 Autobiography

### [Problem Solver: Embracing Challenges with Optimism]
Optimism and proactivity define my approach to every challenge. Throughout my academic career, I discovered that my true passion lies in "problem-solving" and enjoying the journey of finding the optimal solution. During my Master’s studies, I specialized in **Heuristic Algorithms**, focusing on applying mathematical logic to maximize production efficiency. To improve solution quality, I habitually studied international journals, not only to reproduce existing methods but to refine and optimize them. This research-driven mindset—seeking not just *how* but *why*—laid a solid technical foundation for my engineering career.

### [AI-Native Mindset: From Learner to Driver]
In this era of rapid AI iteration, I maintain a strong sense of urgency and curiosity. Beyond traditional programming, I actively study Neural Network architectures and leverage tools like ChatGPT and AI Agents as my efficient "co-pilots." I believe that only by mastering AI can one stay competitive, striving to be "better today than yesterday." This continuous evolution has enabled me to quickly master **n8n**, **RAG**, and **Agent Orchestration**, translating cutting-edge tech into practical, deployed projects.

### [The Intersection of Investment Discipline & Engineering Logic]
Beyond coding, I am deeply passionate about financial markets. The complexity and uncertainty of the market mirror engineering challenges—there is rarely a single "correct answer," only the "optimal decision" for the current context.
Through rigorous study of technical and fundamental analysis, I passed the **FTMO Challenge & Verification**, becoming a funded trader. This achievement is not just financial; it proves my ability in **Risk Management**, **Data-Driven Decision Making**, and **Psychological Resilience**. Whether facing a market drawdown or a critical software bug, my philosophy remains the same: analyze the failure, adjust the parameters, and execute the solution with conviction.
