import { ArrowUp, ArrowDown, Bell, BarChart2 } from 'lucide-react';
import type { Stock } from '../types';

import { cn } from '../utils/cn';

interface StockCardProps {
    stock: Stock;
    onAlertClick: (id: string) => void;
    onChartClick?: (id: string) => void;
    exchangeRate?: number;
}

export function StockCard({ stock, onAlertClick, onChartClick, exchangeRate = 32.5 }: StockCardProps) {
    const isUp = stock.change >= 0;
    const hasAlert = stock.alertHigh || stock.alertLow;

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'FOREX': return 'bg-emerald-900/50 text-emerald-300';
            case 'CRYPTO': return 'bg-orange-900/50 text-orange-300';
            case 'COMMODITY': return 'bg-yellow-900/50 text-yellow-300';
            default: return 'bg-slate-900 text-slate-400';
        }
    };

    const getSubtitle = () => {
        switch (stock.type) {
            case 'STOCK': return `Vol: ${(stock.volume / 1000).toFixed(1)}K`;
            case 'FOREX': return 'Spot Rate';
            case 'CRYPTO': return 'USDT';
            case 'COMMODITY': return 'USD / oz (盎司)';
            default: return stock.symbol;
        }
    };

    const getTaiwanGoldPrice = () => {
        // 1 oz = 31.1035 g
        // 1 Tael (台兩) = 37.5 g
        // Formula: USD/oz * (37.5 / 31.1035) * USD/TWD
        const conversionFactor = 37.5 / 31.1035;
        const priceTWD = stock.price * conversionFactor * exchangeRate;
        return Math.round(priceTWD).toLocaleString();
    };

    return (
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-600 transition-all group relative overflow-hidden">
            {/* Background Gradient */}
            <div className={cn(
                "absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/5 to-transparent rounded-bl-full pointer-events-none transition-opacity",
                isUp ? "from-red-500/10" : "from-green-500/10" // TW stock color: Red is Up, Green is Down
            )} />

            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="flex items-center space-x-2">
                        <h3 className="font-bold text-lg text-white">{stock.name}</h3>
                        <span className={cn("text-xs font-mono px-1.5 py-0.5 rounded", getTypeColor(stock.type))}>
                            {stock.type === 'STOCK' ? stock.symbol : stock.type}
                        </span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                        {getSubtitle()}
                        {stock.type === 'COMMODITY' && stock.symbol.includes('XAU') && (
                            <span className="block text-yellow-500/80 mt-1 font-mono">
                                ≈ NT$ {getTaiwanGoldPrice()} / 台兩
                            </span>
                        )}
                    </div>
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            // We need a new prop for this, or just reuse onAlertClick for now? 
                            // Actually, let's assume we pass onChartClick
                        }}
                        // Temporary placeholder logic until we update the interface
                        className="hidden"
                    ></button>

                    {/* Check if we have onChartClick passed down */}
                </div>
                <div className="flex">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            // Assuming we are passing a new prop onChartClick
                            if (onChartClick) onChartClick(stock.id);
                        }}
                        className="p-2 rounded-full hover:bg-slate-700 text-slate-400 hover:text-white transition-colors relative"
                        title="查看走勢圖"
                    >
                        <BarChart2 className="w-5 h-5" />
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onAlertClick(stock.id);
                        }}
                        className="p-2 ml-1 rounded-full hover:bg-slate-700 text-slate-400 hover:text-white transition-colors relative"
                        title="設定警示"
                    >
                        <Bell className={cn("w-5 h-5", hasAlert ? "fill-blue-500 text-blue-500" : "")} />
                        {hasAlert && <span className="absolute top-1.5 right-2 w-2 h-2 bg-blue-500 rounded-full animate-pulse" />}
                    </button>
                </div>
            </div>

            <div className="flex items-end justify-between">
                <div className="font-mono text-3xl font-bold text-white">
                    {stock.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={cn(
                    "flex flex-col items-end text-sm font-mono font-medium",
                    isUp ? "text-red-400" : "text-green-400"
                )}>
                    <div className="flex items-center">
                        {isUp ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
                        {stock.change > 0 ? '+' : ''}{stock.change}
                    </div>
                    <div>
                        {stock.changePercent > 0 ? '+' : ''}{stock.changePercent}%
                    </div>
                </div>
            </div>

            {
                hasAlert && (
                    <div className="mt-4 border-t border-slate-700 pt-3 flex gap-2 text-xs text-slate-400 font-mono">
                        {stock.alertHigh && (
                            <span className="flex items-center text-red-300">
                                <span className="mr-1">▲</span> &gt; {stock.alertHigh}
                            </span>
                        )}
                        {stock.alertLow && (
                            <span className="flex items-center text-green-300">
                                <span className="mr-1">▼</span> &lt; {stock.alertLow}
                            </span>
                        )}
                    </div>
                )
            }
        </div >
    );
}
