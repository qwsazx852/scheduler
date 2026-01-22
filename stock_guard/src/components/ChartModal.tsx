import { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { X } from 'lucide-react';
import { binanceService } from '../services/binanceService';

interface ChartModalProps {
    isOpen: boolean;
    onClose: () => void;
    symbol: string;
}

export function ChartModal({ isOpen, onClose, symbol }: ChartModalProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<any | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!isOpen || !chartContainerRef.current) return;

        setError(null);
        setIsLoading(true);

        // 1. Create Chart
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: '#0f172a' }, // slate-900
                textColor: '#94a3b8', // slate-400
            },
            grid: {
                vertLines: { color: '#1e293b' }, // slate-800
                horzLines: { color: '#1e293b' },
            },
            width: chartContainerRef.current.clientWidth || 600, // Fallback width
            height: 400,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        });

        const candlestickSeries = (chart as any).addCandlestickSeries({
            upColor: '#22c55e', // green-500
            downColor: '#ef4444', // red-500
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        });

        chartRef.current = chart;

        // 2. Fetch Data with Mock Fallback
        const fetchData = async () => {
            try {
                let data = await binanceService.getKlines(symbol);

                // Fallback to Mock Data if API fails (e.g. Proxy issue in Prod)
                if (!data || data.length === 0) {
                    console.warn('Using Mock Data for Chart');
                    setError('⚠️ 使用模擬數據 (Network Error)');

                    // Generate 100 candles
                    const mockData = [];
                    let price = 50000; // Base price
                    let time = Math.floor(Date.now() / 1000) - (100 * 60);

                    for (let i = 0; i < 100; i++) {
                        const move = (Math.random() - 0.5) * 100;
                        const open = price;
                        const close = price + move;
                        const high = Math.max(open, close) + Math.random() * 50;
                        const low = Math.min(open, close) - Math.random() * 50;

                        mockData.push({ time, open, high, low, close });

                        price = close;
                        time += 60;
                    }
                    data = mockData;
                }

                if (data.length > 0) {
                    candlestickSeries.setData(data);
                    chart.timeScale().fitContent();
                    setIsLoading(false); // Success
                    // Don't clear error if it was set to "Simulated" warning
                }
            } catch (err) {
                console.error(err);
                setError('Critical Chart Error');
                setIsLoading(false);
            }
        };

        fetchData();

        // Resize handler
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
            chartRef.current = null;
        };
    }, [isOpen, symbol]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl shadow-2xl flex flex-col overflow-hidden relative">
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-slate-800 bg-slate-900">
                    <div className="flex items-center space-x-2">
                        <h2 className="text-lg font-bold text-white">{symbol} / USDT</h2>
                        <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">1m Interval</span>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Chart Area */}
                <div className="flex-1 w-full bg-slate-950 relative min-h-[400px]">
                    {isLoading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-10 text-white">
                            載入中... (Loading...)
                        </div>
                    )}
                    {error && (
                        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 z-20 text-red-400 flex-col">
                            <p className="font-bold text-lg">⚠️ 發生錯誤</p>
                            <p className="text-sm mt-2 font-mono">{error}</p>
                        </div>
                    )}
                    <div ref={chartContainerRef} className="w-full h-full" />
                </div>
            </div>
        </div>
    );
}
