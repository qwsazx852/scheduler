import { useState } from 'react';
import type { Trend } from '../types';
import { ExternalLink, TrendingUp, Clock, Zap, Tag, Flame, BarChart2 } from 'lucide-react';
import { TrendChart } from './TrendChart';

interface TrendCardProps {
    item: Trend;
    rank: number;
}

export function TrendCard({ item, rank }: TrendCardProps) {

    const isBreakout = item.status === "Breakout";
    const [showChart, setShowChart] = useState(false);

    return (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-blue-500 transition-all hover:shadow-lg hover:shadow-blue-500/10 group relative overflow-hidden flex flex-col h-full">
            {/* Background Gradient for Breakout items */}
            {isBreakout && (
                <div className="absolute top-0 right-0 p-2 opacity-10">
                    <Flame className="w-24 h-24 text-red-500" />
                </div>
            )}

            <div className="flex justify-between items-start mb-3 relative z-10">
                <div className="flex items-center space-x-3">
                    <span className={`text-2xl font-bold ${rank <= 3 ? 'text-yellow-400' : 'text-slate-500'}`}>
                        #{rank}
                    </span>
                    <div>
                        <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                            {item.title}
                        </h3>
                        <div className="flex flex-wrap gap-2 mt-1">
                            {/* Category Chip */}
                            {item.category && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-700 text-slate-300">
                                    <Tag className="w-3 h-3 mr-1" />
                                    {item.category}
                                </span>
                            )}
                            {/* Growth Rate Chip */}
                            {item.growthRate !== undefined && (
                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${item.growthRate > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                    }`}>
                                    {item.growthRate > 0 ? '+' : ''}{item.growthRate}%
                                </span>
                            )}
                        </div>
                    </div>
                </div>

                {/* Traffic Badge */}
                <div className="flex flex-col items-end gap-1">
                    <div className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        {item.traffic}
                    </div>
                    {isBreakout && (
                        <span className="text-xs font-bold text-red-400 animate-pulse flex items-center">
                            <Zap className="w-3 h-3 mr-1" />
                            暴衝中
                        </span>
                    )}
                </div>
            </div>

            {/* News Snippet */}
            <div className="bg-slate-900/50 rounded p-3 mb-3 relative z-10 flex-grow">
                <p className="text-sm text-slate-300 line-clamp-2 leading-relaxed">
                    {item.newsUrl ? (
                        <a href={item.newsUrl} target="_blank" rel="noreferrer" className="hover:underline">
                            {item.description || '相關新聞報導...'}
                        </a>
                    ) : (
                        item.description
                    )}
                </p>
                <div className="mt-2 flex justify-between items-center text-xs text-slate-500">
                    <span>來源: {item.source}</span>
                    <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {item.pubDate ? new Date(item.pubDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                </div>
            </div>

            {/* Chart Section */}
            {showChart && (
                <div className="mb-3 relative z-10">
                    <p className="text-xs text-slate-400 mb-1">7日熱度趨勢</p>
                    <TrendChart keyword={item.title} color={isBreakout ? "#ef4444" : "#3b82f6"} />
                </div>
            )}

            <div className="grid grid-cols-2 gap-2 relative z-10 mt-auto">
                <button
                    onClick={() => setShowChart(!showChart)}
                    className={`inline-flex items-center justify-center w-full py-2 rounded-lg text-sm transition-colors border ${showChart
                            ? 'bg-blue-600 border-blue-500 text-white'
                            : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700'
                        }`}
                >
                    <BarChart2 className="w-4 h-4 mr-2" />
                    {showChart ? '隱藏分析' : '趨勢分析'}
                </button>
                <a
                    href={`https://www.google.com/search?q=${encodeURIComponent(item.title)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center justify-center w-full py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm transition-colors"
                >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    搜尋相關
                </a>
            </div>
        </div>
    );
}
