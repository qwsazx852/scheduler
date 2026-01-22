import { useState, useEffect } from 'react';
import { TrendService } from './services/TrendService';
import type { Trend } from './types';
import { TrendCard } from './components/TrendCard';
import { RefreshCw, Flame } from 'lucide-react';

function App() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("全部");

  const categories = ["全部", "科技", "娛樂", "運動", "生活", "商業"];

  const fetchData = async () => {
    setLoading(true);
    try {
      console.log("App: Fetching data...");
      const data = await TrendService.fetchTrends();
      // Backend now sorts by Growth Rate by default
      setTrends(data);
      setLastUpdated(new Date());
    } catch (e) {
      console.error("App: Fetch failed", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // 5 min
    return () => clearInterval(interval);
  }, []);

  const filteredTrends = activeCategory === "全部" 
    ? trends 
    : trends.filter(t => t.category === activeCategory);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6" style={{ minHeight: '100vh', backgroundColor: '#020617', color: 'white' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 border-b border-slate-800 pb-4 gap-4">
          <div>
            <h1 className="text-3xl font-extrabold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent flex items-center">
              <Flame className="w-8 h-8 text-orange-500 mr-2" />
              TrendPulse 趨勢脈動
            </h1>
            <p className="text-slate-400 mt-1">AI 全網熱度監測 - 捕捉每一個爆紅瞬間</p>
          </div>
          
          <div className="flex flex-col md:items-end gap-2">
            <div className="text-xs text-slate-500">
              {lastUpdated ? `最後更新: ${lastUpdated.toLocaleTimeString()}` : '更新中...'}
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors disabled:opacity-50 text-sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '分析中...' : '立即掃描全網'}
            </button>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mb-6">
            {categories.map(cat => (
                <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                        activeCategory === cat 
                        ? 'bg-white text-slate-900 shadow-lg shadow-white/10 scale-105' 
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                    }`}
                >
                    {cat}
                </button>
            ))}
        </div>

        {/* content */}
        {loading && trends.length === 0 ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <span className="ml-3">正在掃描全網數據...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTrends.map((item, index) => (
              <TrendCard key={item.title + index} item={item} rank={item.rank} />
            ))}
            
            {filteredTrends.length === 0 && (
                <div className="col-span-full text-center py-12 text-slate-500">
                    此分類目前無顯著發燒趨勢。
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
