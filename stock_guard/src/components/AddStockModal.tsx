
import { useState } from 'react';
import { X, Plus, Search } from 'lucide-react';

interface AddStockModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAdd: (symbol: string, type: string) => Promise<boolean>;
}

export function AddStockModal({ isOpen, onClose, onAdd }: AddStockModalProps) {
    const [symbol, setSymbol] = useState('');
    const [type] = useState('CRYPTO'); // CRYPTO or STOCK (Business) -> For now only Crypto/Futures supported essentially
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!symbol) return;

        setIsLoading(true);
        setError('');

        try {
            // Basic validation or pre-check if needed, or just let onAdd handle it
            const success = await onAdd(symbol.toUpperCase(), type);
            if (success) {
                setSymbol('');
                onClose();
            } else {
                setError('無法新增：無效的代號或網路錯誤');
            }
        } catch (err) {
            setError('發生未知錯誤');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold text-white flex items-center">
                            <Plus className="w-5 h-5 mr-2 text-blue-500" />
                            新增自選 (Add Stock)
                        </h2>
                        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-2">代號 (Symbol)</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                                <input
                                    type="text"
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    placeholder="e.g. LTC, PEPE, WIF"
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none uppercase"
                                    autoFocus
                                />
                            </div>
                            <p className="text-xs text-slate-500 mt-1">目前僅支援 Binance USDT 交易對 (如 BTC, ETH, PEPE)</p>
                        </div>

                        {error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors text-sm"
                            >
                                取消
                            </button>
                            <button
                                type="submit"
                                disabled={isLoading || !symbol}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg transition-colors text-sm font-bold"
                            >
                                {isLoading ? '驗證中...' : '確認新增'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
