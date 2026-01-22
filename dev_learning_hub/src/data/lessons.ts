export interface Lesson {
    id: string;
    title: string;
    moduleId: string;
    content: string; // Markdown content
}

export interface Module {
    id: string;
    title: string;
    description: string;
    lessons: Lesson[];
}

export const MODULES: Module[] = [
    {
        id: 'tools',
        title: '第一章：環境準備 (Setup)',
        description: '在開始寫程式之前，我們需要先把電腦變成一個強大的開發工具。',
        lessons: [
            {
                id: 'vscode-setup',
                title: '1-1. 安裝編輯器 VS Code',
                moduleId: 'tools',
                content: `
# 為什麼需要 VS Code？

寫程式就像寫文章，我們需要一個好用的「記事本」。Visual Studio Code (VS Code) 是目前全球工程師最愛用的工具，因為它免費、擴充性強，而且微軟維護得很好。

![VS Code 介面概覽](/images/vscode.png)

## 步驟一：下載與安裝
1. 前往官網 [code.visualstudio.com](https://code.visualstudio.com)
2. 點擊 "Download" 下載適合你電腦的版本 (Windows/Mac)。
3. 安裝並開啟程式。

## 步驟二：安裝中文介面 (選用)
如果不習慣英文，可以安裝中文包：
1. 點擊左側最後一個圖示 (Extensions)。
2. 搜尋 "Chinese"。
3. 點擊 "Install" 並重啟軟體。

## 步驟三：認識介面
- **左側欄**：檔案總管 (Explorer)、搜尋 (Search)、擴充套件 (Extensions)。
- **中間**：編輯區，寫程式的地方。
- **下方**：終端機 (Terminal)，我們下指令的地方。
        `
            },
            {
                id: 'nodejs-setup',
                title: '1-2. 安裝 Node.js 環境',
                moduleId: 'tools',
                content: `
# 什麼是 Node.js？

JavaScript 原本只能在瀏覽器裡面跑。Node.js 讓 JavaScript 可以直接在你的電腦系統上運作，這樣我們才能建立伺服器、打包檔案。簡單說，它是**讓你的電腦看懂程式碼的引擎**。

## 安裝步驟
1. 前往 [nodejs.org](https://nodejs.org)
2. 下載左邊的 **LTS 版本** (穩定版)。
3. 一路點擊 "Next" 安裝到底。

## 驗證安裝
安裝好後，我們要檢查是否成功：
1. 打開 VS Code。
2. 按 \`Ctrl + \` (反引號，Esc 下面那顆) 打開終端機。
3. 輸入以下指令並按 Enter：

\`\`\`bash
node -v
\`\`\`

如果有出現類似 \`v18.x.x\` 或 \`v20.x.x\` 的數字，恭喜你，你的電腦已經準備好可以寫程式了！
        `
            }
        ]
    },
    {
        id: 'frontend-basics',
        title: '第二章：網頁基礎 (HTML/CSS)',
        description: '網頁就像積木，HTML 是結構，CSS 是外觀。',
        lessons: [
            {
                id: 'html-structure',
                title: '2-1. HTML 骨架拆解',
                moduleId: 'frontend-basics',
                content: `
# HTML 就像是網頁的骨骼

任何網頁 (包括你現在看的這個) 都是由 HTML 組成的。它告訴瀏覽器：哪裡是標題、哪裡是圖片、哪裡是按鈕。

![HTML 結構示意圖](/images/html_structure.png)

## 常見標籤
- \`<div>\`: 盒子。用來分區塊。
- \`<h1>\` ~ \`<h6>\`:標題。字體大小不同。
- \`<p>\`: 段落文字。
- \`<button>\`: 按鈕。

## 實作練習
試著在你的 VS Code 建立一個 \`index.html\`，貼上以下內容：

\`\`\`html
<div class="card">
  <h1>我的職缺監控器</h1>
  <p>目前狀態：執行中</p>
  <button>開始監控</button>
</div>
\`\`\`

直接把檔案拖到瀏覽器打開，你就會看到一個超醜的網頁——因為我們還沒加 CSS！
        `
            },
            {
                id: 'css-styling',
                title: '2-2. CSS 美化與 Flexbox',
                moduleId: 'frontend-basics',
                content: `
# CSS 賦予網頁靈魂

如果 HTML 是骨骼，CSS 就是皮膚與衣服。

![Flexbox 排版原理](/images/flexbox.png)

## Flexbox 排版神技
新手最頭痛的就是「怎麼把東西置中」、「怎麼排成一列」。**Flexbox** 就是救星。

\`\`\`css
.card {
  display: flex;         /* 開啟 Flex 模式 */
  flex-direction: column; /* 由上往下排 (或是 row 由左往右) */
  align-items: center;    /* 水平置中 */
  justify-content: center;/* 垂直置中 */
}
\`\`\`

這個概念非常重要，因為我們之後做儀表板時，為了讓按鈕跟輸入框排在同一排，全都是靠 Flexbox。
        `
            }
        ]
    },
    {
        id: 'workshop',
        title: '第三章：零基礎開發實戰',
        description: '從一行程式碼都沒有，到完成整個監控專案。請跟著我一步一步做。',
        lessons: [
            {
                id: 'create-project',
                title: '3-1. 建立專案與檔案',
                moduleId: 'workshop',
                content: `
# 第一步：建立你的 React 專案

我們不用從零開始造輪子，使用 **Vite** 可以快速幫我們產生一個標準的網站骨架。

## 1. 執行指令
打開 VS Code 終端機，輸入：
\`\`\`bash
npm create vite@latest my-monitor-app -- --template react-ts
\`\`\`

這行指令的意思是：
- \`create vite\`: 呼叫 Vite 工具
- \`my-monitor-app\`: 你的專案名稱
- \`--template react-ts\`: 使用 React + TypeScript 樣板

## 2. 進入專案並安裝
\`\`\`bash
cd my-monitor-app
npm install
npm install lucide-react clsx tailwind-merge
\`\`\`
我們順便安裝了 \`lucide-react\` (圖示庫) 和一些樣式工具。

## 3. 建立組件檔案
在 \`src\` 資料夾內，建立一個新檔案叫 \`JobMonitor.tsx\`。這就是我們要寫程式的地方。
        `
            },
            {
                id: 'build-ui',
                title: '3-2. 刻出使用者介面 (UI)',
                moduleId: 'workshop',
                content: `
# 第二步：設計畫面

我們要把畫面分成三個區塊：標題、控制列、結果顯示。

## JobMonitor.tsx (部分程式碼)

\`\`\`tsx
import { Play, Square, Bell, Loader2 } from 'lucide-react';

export function JobMonitor() {
  return (
    <div className="bg-slate-900 text-white p-6 rounded-xl max-w-2xl mx-auto">
      
      {/* 1. 標題區 */}
      <div className="flex items-center space-x-2 mb-6">
        <div className="w-3 h-3 bg-green-500 rounded-full"/>
        <h1 className="font-bold">Web Monitor v1.0</h1>
      </div>

      {/* 2. 控制區 */}
      <div className="flex gap-2 mb-6">
        <input 
          type="text" 
          placeholder="輸入監控網址..."
          className="flex-1 bg-slate-800 rounded px-4 py-2"
        />
        <button className="bg-green-600 px-6 py-2 rounded flex items-center">
          <Play className="w-4 h-4 mr-2" /> 開始
        </button>
      </div>

      {/* 3. 結果區 */}
      <div className="bg-slate-950 p-4 rounded h-64 overflow-auto">
        <p className="text-slate-500">// 監控日誌顯示於此...</p>
      </div>

    </div>
  );
}
\`\`\`
把這段程式碼貼進除去，你的畫面雛形就出來了！
        `
            },
            {
                id: 'add-state',
                title: '3-3. 賦予生命 (State)',
                moduleId: 'workshop',
                content: `
# 第三步：加入狀態管理

現在的畫面是「死」的，我們需要用 React 的 \`useState\` 讓它活起來。

## 什麼是 State？
就像遊戲裡的「血條」或「金幣」，數據變了，畫面就會跟著變。

## 修改程式碼
在 \`JobMonitor\` 函式裡面，第一行加入這些變數：

\`\`\`tsx
import { useState } from 'react'; // 記得匯入

export function JobMonitor() {
  // 1. 控制是否正在執行
  const [isRunning, setIsRunning] = useState(false);
  
  // 2. 儲存使用者輸入的網址
  const [url, setUrl] = useState('');
  
  // 3. 儲存監控日誌 (字串陣列)
  const [logs, setLogs] = useState<string[]>([]);

  // ... (下面的 return 程式碼跟剛剛一樣)
}
\`\`\`

接著，把按鈕的 \`OnClick\` 事件綁定上去：
\`\`\`tsx
<button 
  onClick={() => setIsRunning(!isRunning)} 
  className={isRunning ? "bg-red-600" : "bg-green-600"}
>
  {isRunning ? "停止" : "開始"}
</button>
\`\`\`
現在點擊按鈕，顏色就會變了！
        `
            },
            {
                id: 'add-logic',
                title: '3-4. 核心邏輯實現',
                moduleId: 'workshop',
                content: `
# 第四步：自動化邏輯

這是最關鍵的一步。我們要用 \`useEffect\` 和 \`setInterval\` 來製造「每隔幾秒做一次檢查」的效果。

## 邏輯實作
在 \`useState\` 下方加入這段程式碼：

\`\`\`tsx
import { useEffect } from 'react';

useEffect(() => {
  let timer: any;

  if (isRunning) {
    // 如果是「執行中」，設定定時器
    timer = setInterval(() => {
      
      // 1. 新增一條 Log
      const time = new Date().toLocaleTimeString();
      setLogs(prev => [\`[\${time}] 正在掃描 \${url}...\`, ...prev]);

      // 2. 模擬請求 (只有 30% 機率會發現新職缺)
      const foundNew = Math.random() > 0.7;
      
      if (foundNew) {
         setLogs(prev => ['🎉 發現新職缺！', ...prev]);
         // 這裡未來可以加入發送 Email 或 Line 通知的功能
      }

    }, 3000); // 每 3000 毫秒 (3秒) 執行一次
  }

  // 很重要：當組件關閉或停止時，要清除定時器，不然電腦會當機
  return () => clearInterval(timer);

}, [isRunning, url]); // 當 isRunning 或 url 改變時，重新設定
\`\`\`
        `
            },
            {
                id: 'full-code',
                title: '3-5. 完整程式碼對照',
                moduleId: 'workshop',
                content: `
# 恭喜！你完成了

將所有片段組合起來，這就是你現在在「實戰演練」中看到的完整功能程式碼。你可以直接複製這份程式碼到你的專案中執行。

\`\`\`tsx
import { useState, useEffect } from 'react';
import { Play, Square, Loader2, Bell, AlertTriangle, ExternalLink } from 'lucide-react';

// 定義職缺的資料格式 (TypeScript 優勢)
interface Job {
  id: string;
  title: string;
  company: string;
  salary: string;
  url: string;
  new: boolean;
}

// ... (由於篇幅，這裡展示核心邏輯，完整程式碼請參考本平台的 JobMonitorDemo.tsx)
\`\`\`

## 下一步挑戰
試著修改這個程式：
1. **縮短時間**：把 3000 改成 1000 (1秒)。
2. **改變機率**：把 \`> 0.7\` 改成 \`> 0.2\` (更容易發現職缺)。
3. **客製化內容**：把「發現新職缺」的文字改成你想要的文字。
        `
            }
        ]
    },
    {
        id: 'final-project',
        title: '第四章：成果驗收',
        description: '使用我們剛剛寫出的模擬器進行演練。',
        lessons: [
            {
                id: 'implementation',
                title: '4-1. 啟動模擬器',
                moduleId: 'final-project',
                content: `
# 實戰演練

下方就是使用上述程式碼執行出來的結果。
試著想像你就是電腦，每 3 秒鐘執行一次 \`setInterval\` 裡面的任務：**發送請求 -> 等待回應 -> 判斷結果**。
        `
            }
        ]
    }
];
