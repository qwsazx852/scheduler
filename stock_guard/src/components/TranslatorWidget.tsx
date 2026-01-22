import { useState, useEffect } from 'react';
import { RefreshCw, ArrowRightLeft, BookOpen, X, Play } from 'lucide-react';
import { API_CONFIG } from '../config/api';

export const TranslatorWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [sourceText, setSourceText] = useState('');
    const [targetText, setTargetText] = useState('');
    const [loading, setLoading] = useState(false);

    // Debounce translation
    useEffect(() => {
        const timer = setTimeout(() => {
            if (sourceText.trim()) {
                handleTranslate();
            } else {
                setTargetText('');
            }
        }, 1000);

        return () => clearTimeout(timer);
    }, [sourceText]);

    const handleTranslate = async () => {
        if (!sourceText.trim()) return;
        setLoading(true);

        try {
            const baseUrl = API_CONFIG.getProxyUrl();
            // MyMemory API: q=text, langpair=en|zh-TW
            const text = encodeURIComponent(sourceText);
            const res = await fetch(`${baseUrl}/translate?q=${text}&langpair=en|zh-TW`);
            const data = await res.json();

            if (data && data.responseData) {
                setTargetText(data.responseData.translatedText);
            }
        } catch (e) {
            console.error(e);
            setTargetText('Translation Error');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all hover:scale-105"
                title="即時翻譯"
            >
                <BookOpen className="w-6 h-6" />
            </button>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 z-50 w-80 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl overflow-hidden flex flex-col">
            {/* Header */}
            <div className="bg-slate-800 p-3 flex justify-between items-center border-b border-slate-700">
                <div className="flex items-center space-x-2 text-white font-bold">
                    <ArrowRightLeft className="w-4 h-4 text-blue-400" />
                    <span>即時翻譯 (英 → 中)</span>
                </div>
                <button
                    onClick={() => setIsOpen(false)}
                    className="text-slate-400 hover:text-white transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>
            </div>

            {/* Body */}
            <div className="p-4 space-y-4">
                {/* Source Input */}
                <div>
                    <label className="block text-xs text-slate-400 mb-1">輸入英文</label>
                    <textarea
                        value={sourceText}
                        onChange={(e) => setSourceText(e.target.value)}
                        placeholder="Type English here..."
                        className="w-full h-24 bg-slate-950 text-white p-2 rounded border border-slate-700 focus:border-blue-500 focus:outline-none text-sm resize-none"
                    />
                </div>

                {/* Target Output */}
                <div>
                    <label className="block text-xs text-slate-400 mb-1 flex justify-between">
                        <span>中文翻譯</span>
                        {loading && <RefreshCw className="w-3 h-3 animate-spin text-blue-400" />}
                    </label>
                    <div className="w-full h-24 bg-slate-800/50 text-slate-200 p-2 rounded border border-slate-700/50 text-sm overflow-y-auto">
                        {targetText || <span className="text-slate-600 italic">等待輸入...</span>}
                    </div>
                </div>

                {/* Manual Button (Optional if debounce is slow) */}
                <button
                    onClick={handleTranslate}
                    disabled={loading || !sourceText}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-2"
                >
                    <Play className="w-4 h-4 fill-current" />
                    <span>立即翻譯</span>
                </button>
            </div>

            <div className="bg-slate-950 p-2 text-center">
                <span className="text-[10px] text-slate-600">Powered by MyMemory</span>
            </div>
        </div>
    );
};
