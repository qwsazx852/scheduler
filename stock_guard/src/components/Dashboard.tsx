
import { useState } from 'react';
import { useStocks } from '../hooks/useStocks';
import { StockCard } from './StockCard';
import { AlertModal } from './AlertModal';
import { ChartModal } from './ChartModal';
import { AddStockModal } from './AddStockModal';
import { SettingsModal } from './SettingsModal';
import { Activity, Bell } from 'lucide-react';
import { NewsFeed } from './NewsFeed';
import { EconomicCalendar } from './EconomicCalendar';
import { TranslatorWidget } from './TranslatorWidget';

export function Dashboard() {
    const { stocks, lastUpdated, toggleAlert, updateSmartAlerts, updateIntervalAlert, telegramToken, telegramChatId, saveTelegramSettings, refreshStats, addStock } = useStocks();
    const [editingStockId, setEditingStockId] = useState<string | null>(null);
    const [viewingChartStockId, setViewingChartStockId] = useState<string | null>(null);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isAddStockOpen, setIsAddStockOpen] = useState(false);
    const [filter, setFilter] = useState<'ALL' | 'CRYPTO' | 'COMMODITY' | 'STOCK' | 'FAVORITES'>('ALL');

    const editingStock = stocks.find(s => s.id === editingStockId);
    const viewingChartStock = stocks.find(s => s.id === viewingChartStockId);

    const filteredStocks = stocks.filter(s => filter === 'ALL' || s.type === filter);

    const handleSaveAlert = (high?: number, low?: number, flags?: any, intervalStep?: number, intervalEnabled?: boolean) => {
        if (editingStockId) {
            // If traditional alerts set
            toggleAlert(editingStockId, high, low);
            // If smart alerts set
            if (flags) {
                updateSmartAlerts(editingStockId, flags);
            }
            // If interval alerts set
            if (intervalStep !== undefined || intervalEnabled !== undefined) {
                updateIntervalAlert(editingStockId, intervalStep || 0, intervalEnabled || false);
            }
            setEditingStockId(null);
        }
    };

    const handleAlertClick = (id: string) => {
        setEditingStockId(id);
    };

    const handleChartClick = (id: string) => {
        setViewingChartStockId(id);
    };

    const tabs = [
        { id: 'ALL', label: '全部' },
        { id: 'CRYPTO', label: '加密貨幣' },
        { id: 'STOCK', label: '商業/股票' },
        { id: 'COMMODITY', label: '原物料' },
    ] as const;

    const usdtwd = 32.5;

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-6 md:p-12">
            <div className="max-w-7xl mx-auto">
                <header className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-3">
                        <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
                            <Activity className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white tracking-tight">StockGuard</h1>
                            <p className="text-xs text-slate-400 font-mono mt-1">
                                最後更新: {lastUpdated.toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => setIsAddStockOpen(true)}
                            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-sm px-4 py-2 rounded-lg transition-colors border border-slate-700 font-bold text-blue-400"
                        >
                            <span>+ 新增</span>
                        </button>
                        <button
                            onClick={() => setIsSettingsOpen(true)}
                            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-sm px-4 py-2 rounded-lg transition-colors border border-slate-700"
                        >
                            <Bell className="w-4 h-4" />
                            <span>通知設定</span>
                            {telegramToken && <div className="w-2 h-2 bg-blue-500 rounded-full" />}
                        </button>
                    </div>
                </header>

                <div className="flex space-x-1 mb-6 bg-slate-900 p-1 rounded-lg w-fit border border-slate-800 overflow-x-auto">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setFilter(tab.id)}
                            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${filter === tab.id
                                ? 'bg-slate-700 text-white shadow-sm'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {filteredStocks.map(stock => (
                        <StockCard
                            key={stock.id}
                            stock={stock}
                            onAlertClick={handleAlertClick}
                            onChartClick={handleChartClick}
                            exchangeRate={usdtwd}
                        />
                    ))}
                </div>

                {/* News & Calendar Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[600px] mb-8">
                    <NewsFeed />
                    <EconomicCalendar />
                </div>

                {/* Modals */}
                {editingStock && (
                    <AlertModal
                        isOpen={!!editingStock}
                        onClose={() => setEditingStockId(null)}
                        stock={editingStock}
                        onSave={(high, low, flags, iStep, iEnabled) => {
                            handleSaveAlert(high, low, flags, iStep, iEnabled);
                        }}
                        onRefresh={refreshStats}
                        telegramToken={telegramToken}
                        telegramChatId={telegramChatId}
                    />
                )}

                {viewingChartStockId && viewingChartStock && (
                    <ChartModal
                        isOpen={!!viewingChartStockId}
                        onClose={() => setViewingChartStockId(null)}
                        symbol={viewingChartStock.symbol}
                    />
                )}

                <AddStockModal
                    isOpen={isAddStockOpen}
                    onClose={() => setIsAddStockOpen(false)}
                    onAdd={addStock}
                />

                <SettingsModal
                    isOpen={isSettingsOpen}
                    onClose={() => setIsSettingsOpen(false)}
                    telegramToken={telegramToken}
                    telegramChatId={telegramChatId}
                    onSave={saveTelegramSettings}
                />

                <TranslatorWidget />
            </div>
        </div>
    );
}
