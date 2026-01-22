import { useState, useEffect } from 'react';
import { X, Bell } from 'lucide-react';
import { notificationService } from '../services/notificationService';

interface AlertModalProps {
    isOpen: boolean;
    onClose: () => void;
    stock: any;
    onSave: (high?: number, low?: number, flags?: any, intervalStep?: number, intervalEnabled?: boolean) => void;
    onRefresh?: () => void;
    telegramToken?: string;
    telegramChatId?: string;
}

export function AlertModal({ isOpen, onClose, stock, onSave, onRefresh, telegramToken, telegramChatId }: AlertModalProps) {
    const [priceHigh, setPriceHigh] = useState<string>('');
    const [priceLow, setPriceLow] = useState<string>('');

    // Interval Alert State
    const [intervalStep, setIntervalStep] = useState<string>('');
    const [intervalEnabled, setIntervalEnabled] = useState(false);

    // Smart Alerts State
    const [touchHigh, setTouchHigh] = useState(false);
    const [touchLow, setTouchLow] = useState(false);
    const [touchClose, setTouchClose] = useState(false);
    const [touchOpen, setTouchOpen] = useState(false);
    const [touchFib618, setTouchFib618] = useState(false);
    const [touchFib786, setTouchFib786] = useState(false);

    // Sync with existing settings when opening
    useEffect(() => {
        if (isOpen && stock) {
            setPriceHigh(stock.alertHigh?.toString() || '');
            setPriceLow(stock.alertLow?.toString() || '');

            // Sync interval settings
            setIntervalStep(stock.intervalStep?.toString() || '');
            setIntervalEnabled(stock.intervalAlertEnabled || false);

            // Sync flags if they exist
            if (stock.alertFlags) {
                setTouchHigh(stock.alertFlags.touchHigh);
                setTouchLow(stock.alertFlags.touchLow);
                setTouchClose(stock.alertFlags.touchClose);
                setTouchOpen(stock.alertFlags.touchOpen);
                setTouchFib618(stock.alertFlags.touchFib618 || false);
                setTouchFib786(stock.alertFlags.touchFib786 || false);
            } else {
                setTouchHigh(false); setTouchLow(false); setTouchClose(false); setTouchOpen(false);
                setTouchFib618(false); setTouchFib786(false);
            }
        }
    }, [isOpen, stock.id]);

    const handleSave = () => {
        const high = priceHigh ? parseFloat(priceHigh) : undefined;
        const low = priceLow ? parseFloat(priceLow) : undefined;
        const iStep = intervalStep ? parseFloat(intervalStep) : undefined;

        const flags = {
            touchHigh,
            touchLow,
            touchClose,
            touchOpen,
            touchFib618,
            touchFib786
        };

        onSave(high, low, flags, iStep, intervalEnabled);
    };

    if (!isOpen || !stock) return null;

    const currentPrice = stock.price;
    const { keyLevels } = stock;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-in p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold text-white flex items-center">
                            <Bell className="w-5 h-5 mr-2 text-blue-500" />
                            設定警示 - {stock.name}
                        </h2>
                        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    <div className="flex justify-center mb-8">
                        <div className="text-center">
                            <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Current Price</div>
                            <div className="text-3xl font-mono font-bold text-white">
                                {currentPrice.toLocaleString()}
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {/* 1. Price Level Alerts */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-2">上限價格 (High)</label>
                                <input
                                    type="number"
                                    value={priceHigh}
                                    onChange={(e) => setPriceHigh(e.target.value)}
                                    placeholder="無設定"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-2">下限價格 (Low)</label>
                                <input
                                    type="number"
                                    value={priceLow}
                                    onChange={(e) => setPriceLow(e.target.value)}
                                    placeholder="無設定"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                        </div>

                        {/* 2. Smart Alerts (Key Levels) */}
                        {keyLevels && (
                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                                <div className="flex justify-between items-center mb-3">
                                    <h3 className="text-sm font-bold text-white flex items-center">
                                        <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                                        智慧關鍵點位 (Smart Levels)
                                    </h3>
                                    <button
                                        onClick={() => {
                                            // Find all enabled smart alerts to simulate
                                            const msgs: string[] = [];
                                            if (touchHigh) msgs.push(`🚀 ${stock.name} 突破昨日最高價 ${keyLevels.yesterdayHigh}`);
                                            if (touchLow) msgs.push(`🔻 ${stock.name} 跌破昨日最低價 ${keyLevels.yesterdayLow}`);
                                            if (touchClose) msgs.push(`🔵 ${stock.name} 穿越昨日收盤價 ${keyLevels.yesterdayClose}`);
                                            if (touchOpen) msgs.push(`🟡 ${stock.name} 回到今日開盤價 ${keyLevels.todayOpen}`);
                                            if (touchFib618) msgs.push(`📉 ${stock.name} 抵達 0.618 黃金分割位 ${Math.round(keyLevels.fib618 || 0)}`);
                                            if (touchFib786) msgs.push(`📉 ${stock.name} 抵達 0.786 關鍵支撐 ${Math.round(keyLevels.fib786 || 0)}`);

                                            if (msgs.length === 0) {
                                                alert('請先勾選至少一個智慧警示選項，才能進行模擬測試。');
                                                return;
                                            }

                                            const fullMsg = `[測試] 模擬觸發 ${msgs.length} 個警示：\n${msgs.join('\n')}\n(Simulated Trigger)`;
                                            notificationService.sendBrowserNotification('StockGuard 測試', fullMsg);
                                            if (telegramToken && telegramChatId) {
                                                notificationService.sendTelegramNotification(telegramToken, telegramChatId, fullMsg);
                                                alert(`已發送模擬測試通知 (Telegram)\n共包含 ${msgs.length} 個警示`);
                                            } else {
                                                alert('已發送瀏覽器通知 (Telegram 未設定)');
                                            }
                                        }}
                                        className="text-xs bg-slate-700 hover:bg-slate-600 text-blue-300 px-2 py-1 rounded transition-colors"
                                    >
                                        ⚡ 模擬觸發
                                    </button>
                                </div>
                                <div className="space-y-2">
                                    <label className="flex items-center justify-between group cursor-pointer">
                                        <span className="text-sm text-slate-400 group-hover:text-slate-200">触及昨日最高 ({keyLevels.yesterdayHigh})</span>
                                        <input type="checkbox" checked={touchHigh} onChange={e => setTouchHigh(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                    </label>
                                    <label className="flex items-center justify-between group cursor-pointer">
                                        <span className="text-sm text-slate-400 group-hover:text-slate-200">触及昨日最低 ({keyLevels.yesterdayLow})</span>
                                        <input type="checkbox" checked={touchLow} onChange={e => setTouchLow(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                    </label>
                                    <label className="flex items-center justify-between group cursor-pointer">
                                        <span className="text-sm text-slate-400 group-hover:text-slate-200">触及昨日收盘 ({keyLevels.yesterdayClose})</span>
                                        <input type="checkbox" checked={touchClose} onChange={e => setTouchClose(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                    </label>
                                    <label className="flex items-center justify-between group cursor-pointer">
                                        <span className="text-sm text-slate-400 group-hover:text-slate-200">回到今日开盘 ({keyLevels.todayOpen})</span>
                                        <input type="checkbox" checked={touchOpen} onChange={e => setTouchOpen(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                    </label>

                                    {keyLevels.fib618 && (
                                        <>
                                            <div className="border-t border-slate-700/50 my-2"></div>
                                            <div className="text-xs font-bold text-yellow-500 mb-1">斐波那契回撤 (Fibonacci)</div>
                                            <label className="flex items-center justify-between group cursor-pointer">
                                                <span className="text-sm text-slate-400 group-hover:text-slate-200">回測 0.618 ({Math.round(keyLevels.fib618)})</span>
                                                <input type="checkbox" checked={touchFib618} onChange={e => setTouchFib618(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                            </label>
                                            <label className="flex items-center justify-between group cursor-pointer">
                                                <span className="text-sm text-slate-400 group-hover:text-slate-200">回測 0.786 ({Math.round(keyLevels.fib786 || 0)})</span>
                                                <input type="checkbox" checked={touchFib786} onChange={e => setTouchFib786(e.target.checked)} className="accent-blue-500 w-4 h-4" />
                                            </label>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                        {!keyLevels && (
                            <div className="text-center py-4 bg-slate-800/30 rounded-lg border border-slate-700/50 border-dashed">
                                <div className="text-xs text-slate-500 mb-2">
                                    (目前無法取得關鍵點位數據，請稍後再試)
                                </div>
                                <button
                                    onClick={() => onRefresh?.()}
                                    className="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs rounded-full transition-colors flex items-center justify-center mx-auto"
                                >
                                    🔄 重新嘗試載入
                                </button>
                            </div>
                        )}

                        {/* 3. Interval Alerts */}
                        <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/30">
                            <div className="flex justify-between items-center mb-3">
                                <h3 className="text-sm font-bold text-blue-200 flex items-center">
                                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                    波動追蹤警示 (Interval Alert)
                                </h3>
                            </div>
                            <div className="flex items-center space-x-4">
                                <div className="flex-1">
                                    <label className="block text-xs font-medium text-slate-400 mb-1">每波動 (點/美元)</label>
                                    <input
                                        type="number"
                                        value={intervalStep}
                                        onChange={(e) => setIntervalStep(e.target.value)}
                                        placeholder="例如: 10"
                                        disabled={!intervalEnabled}
                                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none disabled:opacity-50"
                                    />
                                </div>
                                <div className="flex items-center pt-5">
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={intervalEnabled}
                                            onChange={(e) => setIntervalEnabled(e.target.checked)}
                                            className="accent-blue-500 w-5 h-5"
                                        />
                                        <span className="text-sm text-white">啟用</span>
                                    </label>
                                </div>
                            </div>
                            <p className="text-[10px] text-slate-400 mt-2">
                                * 啟用後，價格每變動設定的幅度，就會發送一次通知。
                            </p>
                        </div>

                        <button
                            onClick={handleSave}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-colors mt-2"
                        >
                            儲存設定
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
