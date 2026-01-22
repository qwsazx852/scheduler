
import React, { useEffect, useState } from 'react';
import { newsService, type NewsItem } from '../services/newsService';

export const NewsFeed: React.FC = () => {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchNews = async () => {
        const items = await newsService.getLatestNews();
        if (items.length > 0) {
            setNews(items);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchNews();
        const interval = setInterval(fetchNews, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    // Format timestamp to HH:mm
    const formatTime = (ts: number) => {
        try {
            if (!ts || isNaN(ts)) return '--:--';
            const date = new Date(ts * 1000);
            if (isNaN(date.getTime())) return '--:--';
            return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit', hour12: false });
        } catch (e) {
            return '--:--';
        }
    };

    return (
        <div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">⚡</span> 7x24 快訊 (WallstreetCN)
            </h2>

            <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar" style={{ maxHeight: '400px' }}>
                {loading && news.length === 0 ? (
                    <div className="text-gray-400 text-center py-4">Loading news...</div>
                ) : (
                    news.map((item, index) => (
                        <div key={item.id || index} className={`p-3 rounded bg-gray-700/50 border-l-4 ${item.score >= 2 ? 'border-red-500' : 'border-blue-400'}`}>
                            <div className="flex justify-between items-start mb-1">
                                <span className="text-xs text-gray-400 font-mono">{formatTime(item.display_time)}</span>
                                {item.score >= 2 && <span className="text-xs bg-red-900 text-red-200 px-1 rounded">重要</span>}
                            </div>
                            <div className="text-sm text-gray-200 leading-relaxed" dangerouslySetInnerHTML={{ __html: item.content || '' }}></div>
                        </div>
                    ))
                )}
            </div>

            <div className="mt-3 text-xs text-center text-gray-500">
                Source: WallstreetCN
            </div>
        </div>
    );
};
