import { useState, useEffect } from 'react';
import { Play, Square, Loader2, Bell, AlertTriangle, ExternalLink } from 'lucide-react';
import { cn } from '../utils/cn';

interface Job {
    id: string;
    title: string;
    company: string;
    salary: string;
    url: string;
    new: boolean;
}

export function JobMonitorDemo() {
    const [isRunning, setIsRunning] = useState(false);
    const [url, setUrl] = useState('https://www.104.com.tw/jobs/search/?keyword=frontend');
    const [logs, setLogs] = useState<string[]>([]);
    const [jobs, setJobs] = useState<Job[]>([]);
    const [scanCount, setScanCount] = useState(0);

    const addLog = (msg: string) => {
        setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 10));
    };

    useEffect(() => {
        let interval: any;

        if (isRunning) {
            addLog('啟動監控排程... 每 3 秒掃描一次');

            interval = setInterval(() => {
                setScanCount(c => c + 1);
                addLog(`正在請求: ${url}...`);

                // Simulate network delay and finding result
                setTimeout(() => {
                    const success = Math.random() > 0.3; // 70% success rate
                    if (success) {
                        const foundNew = Math.random() > 0.7; // 30% chance to find new
                        if (foundNew) {
                            addLog('🎉 發現新職缺！觸發通知！');
                            const newJob: Job = {
                                id: Math.random().toString(),
                                title: ['Frontend Engineer', 'React Developer', 'Web Dev'][Math.floor(Math.random() * 3)],
                                company: ['Tech Corp', 'StartUp Inc', 'Global Ltd'][Math.floor(Math.random() * 3)],
                                salary: ['60k-80k', '70k-90k', '80k-100k'][Math.floor(Math.random() * 3)],
                                url: url, // Use the monitored URL or a mock
                                new: true
                            };
                            setJobs(prev => [newJob, ...prev]);
                        } else {
                            addLog('掃描完成，無新資料。');
                        }
                    } else {
                        addLog('⚠️ 請求被阻擋 (403 Forbidden) - 模擬反爬蟲機制');
                    }
                }, 800);

            }, 3000);
        } else {
            if (scanCount > 0) addLog('監控已停止。');
        }

        return () => clearInterval(interval);
    }, [isRunning, url]);

    return (
        <div className="bg-slate-900 rounded-xl overflow-hidden border border-slate-700 shadow-2xl my-8">
            {/* Header */}
            <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-slate-400 text-sm font-mono ml-4">Web Monitor v1.0</span>
                </div>
                <div className="text-xs text-slate-500 font-mono">Status: {isRunning ? 'ACTIVE' : 'IDLE'}</div>
            </div>

            <div className="p-6 space-y-6">
                {/* Controls */}
                <div className="flex gap-4">
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-300 font-mono text-sm focus:border-blue-500 outline-none transition-colors"
                        placeholder="輸入目標網址..."
                    />
                    <button
                        onClick={() => setIsRunning(!isRunning)}
                        className={cn(
                            "px-6 py-3 rounded-lg font-bold flex items-center space-x-2 transition-all active:scale-95",
                            isRunning
                                ? "bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/50"
                                : "bg-green-500 text-white hover:bg-green-600 shadow-lg shadow-green-500/20"
                        )}
                    >
                        {isRunning ? (
                            <>
                                <Square className="w-4 h-4 fill-current" />
                                <span>停止監控</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4 fill-current" />
                                <span>開始執行</span>
                            </>
                        )}
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Logs Console */}
                    <div className="bg-slate-950 rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs space-y-2 border border-slate-800">
                        {logs.length === 0 && <span className="text-slate-600 italic">// 等待指令中...</span>}
                        {logs.map((log, i) => (
                            <div key={i} className={cn(
                                "border-l-2 pl-2",
                                log.includes('發現新職缺') ? "border-green-500 text-green-400 bg-green-500/5" :
                                    log.includes('阻擋') ? "border-red-500 text-red-400" :
                                        "border-slate-700 text-slate-400"
                            )}>
                                {log}
                            </div>
                        ))}
                        {isRunning && (
                            <div className="flex items-center space-x-2 text-blue-400 animate-pulse">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                <span>Scanning...</span>
                            </div>
                        )}
                    </div>

                    {/* Results Panel */}
                    <div className="bg-slate-800 rounded-lg p-4 h-64 overflow-y-auto border border-slate-700">
                        <h3 className="text-slate-400 text-xs font-bold uppercase mb-4 flex items-center">
                            <Bell className="w-3 h-3 mr-2" />
                            監控結果 ({jobs.length})
                        </h3>
                        <div className="space-y-3">
                            {jobs.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-40 text-slate-600 text-sm">
                                    <AlertTriangle className="w-8 h-8 mb-2 opacity-50" />
                                    <p>尚無符合條件的項目</p>
                                </div>
                            ) : (
                                jobs.map(job => (
                                    <a
                                        key={job.id}
                                        href={job.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="bg-slate-700 p-3 rounded-lg border border-slate-600 flex justify-between items-start animate-fade-in hover:bg-slate-600 transition-colors cursor-pointer group"
                                    >
                                        <div>
                                            <div className="font-bold text-white text-sm group-hover:text-blue-300 transition-colors flex items-center">
                                                {job.title}
                                                <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </div>
                                            <div className="text-slate-400 text-xs mt-1">{job.company}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-green-400 font-mono text-sm">{job.salary}</div>
                                            <div className="text-[10px] text-blue-300 bg-blue-500/10 px-1 py-0.5 rounded mt-1 inline-block">New</div>
                                        </div>
                                    </a>
                                ))

                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
