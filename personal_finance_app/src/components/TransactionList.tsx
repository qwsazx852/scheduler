import { useState } from 'react';
import type { Transaction, Category } from '../types';
import { format } from 'date-fns';

import { zhTW } from 'date-fns/locale';
import { Search, Filter, ArrowUpRight, ArrowDownRight, Trash2 } from 'lucide-react';
import { cn } from '../utils/cn';

interface TransactionListProps {
    transactions: Transaction[];
    categories: Category[];
    onDeleteCallback: (id: string) => void;
}

export function TransactionList({ transactions, categories, onDeleteCallback }: TransactionListProps) {
    const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');
    const [search, setSearch] = useState('');

    const filteredTransactions = transactions.filter(t => {
        const matchesType = filterType === 'all' || t.type === filterType;
        const matchesSearch = t.note?.toLowerCase().includes(search.toLowerCase()) || false;
        return matchesType && matchesSearch;
    });

    const getCategoryName = (id: string) => {
        return categories.find(c => c.id === id)?.name || '未分類';
    };

    const getCategoryColor = (id: string) => {
        // Simply returning utility classes or hex based on category could be enhanced.
        // For now, we use a basic mapping or the stored color class.
        return categories.find(c => c.id === id)?.color || 'bg-slate-500';
    };

    return (
        <div className="space-y-6">
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 justify-between bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                <div className="flex items-center space-x-2 bg-slate-50 px-3 py-2 rounded-xl w-full md:w-64">
                    <Search className="w-5 h-5 text-slate-400" />
                    <input
                        type="text"
                        placeholder="搜尋交易備註..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="bg-transparent outline-none w-full text-sm text-slate-900 placeholder:text-slate-400"
                    />
                </div>

                <div className="flex items-center space-x-2">
                    <div className="p-2 bg-slate-50 rounded-xl text-slate-500">
                        <Filter className="w-5 h-5" />
                    </div>
                    <select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value as any)}
                        className="bg-slate-50 px-4 py-2 rounded-xl text-sm font-medium text-slate-700 outline-none border-r-8 border-transparent cursor-pointer"
                    >
                        <option value="all">全部類型</option>
                        <option value="income">只看收入</option>
                        <option value="expense">只看支出</option>
                    </select>
                </div>
            </div>

            {/* List */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                {filteredTransactions.length === 0 ? (
                    <div className="p-10 text-center text-slate-500">
                        沒有符合條件的交易紀錄
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100">
                        {filteredTransactions.map(t => (
                            <div key={t.id} className="p-4 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                <div className="flex items-center space-x-4">
                                    <div className={cn(
                                        "w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-sm",
                                        getCategoryColor(t.categoryId)
                                    )}>
                                        {t.type === 'income' ? <ArrowUpRight className="w-6 h-6" /> : <ArrowDownRight className="w-6 h-6" />}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900">{t.note || getCategoryName(t.categoryId)}</h4>
                                        <div className="flex items-center space-x-2 text-xs text-slate-500 mt-1">
                                            <span className="bg-slate-100 px-2 py-0.5 rounded-full">{getCategoryName(t.categoryId)}</span>
                                            <span>•</span>
                                            <span>{format(new Date(t.date), 'yyyy/MM/dd', { locale: zhTW })}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-4">
                                    <span className={cn(
                                        "font-bold text-lg",
                                        t.type === 'income' ? "text-green-600" : "text-slate-900"
                                    )}>
                                        {t.type === 'income' ? '+' : '-'}${t.amount.toLocaleString()}
                                    </span>
                                    <button
                                        onClick={() => onDeleteCallback(t.id)}
                                        className="text-slate-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 p-2"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
