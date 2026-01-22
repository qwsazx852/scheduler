import React, { useState } from 'react';
import { X } from 'lucide-react';
import type { Category, TransactionType } from '../types';
import { cn } from '../utils/cn';


interface TransactionFormProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: any) => void;
    categories: Category[];
}

export function TransactionForm({ isOpen, onClose, onSubmit, categories }: TransactionFormProps) {
    const [type, setType] = useState<TransactionType>('expense');
    const [amount, setAmount] = useState('');
    const [categoryId, setCategoryId] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [note, setNote] = useState('');

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            type,
            amount: Number(amount),
            categoryId,
            date,
            note
        });
        onClose();
        // Reset form
        setAmount('');
        setNote('');
    };

    const filteredCategories = categories.filter(c => c.type === type);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm transition-opacity">
            <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl transform transition-all">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-900">新增交易</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Type Toggle */}
                    <div className="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-xl">
                        <button
                            type="button"
                            onClick={() => setType('expense')}
                            className={cn(
                                "py-2 rounded-lg text-sm font-semibold transition-all",
                                type === 'expense'
                                    ? "bg-white text-red-600 shadow-sm"
                                    : "text-slate-500 hover:text-slate-700"
                            )}
                        >
                            支出
                        </button>
                        <button
                            type="button"
                            onClick={() => setType('income')}
                            className={cn(
                                "py-2 rounded-lg text-sm font-semibold transition-all",
                                type === 'income'
                                    ? "bg-white text-green-600 shadow-sm"
                                    : "text-slate-500 hover:text-slate-700"
                            )}
                        >
                            收入
                        </button>
                    </div>

                    {/* Amount */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">金額</label>
                        <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span>
                            <input
                                type="number"
                                required
                                min="0"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                className="w-full pl-8 pr-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all text-lg font-bold text-slate-900"
                                placeholder="0"
                            />
                        </div>
                    </div>

                    {/* Category */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">分類</label>
                        <div className="grid grid-cols-3 gap-2">
                            {filteredCategories.map(cat => (
                                <button
                                    key={cat.id}
                                    type="button"
                                    onClick={() => setCategoryId(cat.id)}
                                    className={cn(
                                        "p-2 rounded-lg text-sm font-medium border transition-all text-center truncate",
                                        categoryId === cat.id
                                            ? "border-indigo-500 bg-indigo-50 text-indigo-700 ring-1 ring-indigo-500"
                                            : "border-slate-200 text-slate-600 hover:border-indigo-300 hover:bg-slate-50"
                                    )}
                                >
                                    {cat.name}
                                </button>
                            ))}
                        </div>
                        {filteredCategories.length === 0 && (
                            <p className="text-xs text-slate-400 mt-2">尚無此分類</p>
                        )}
                    </div>

                    {/* Date */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">日期</label>
                        <input
                            type="date"
                            required
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all text-slate-900"
                        />
                    </div>

                    {/* Note */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">備註</label>
                        <input
                            type="text"
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all text-slate-900"
                            placeholder="早餐、薪水..."
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full py-3 bg-indigo-600 text-white rounded-xl font-bold text-lg hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-lg shadow-indigo-200 mt-4"
                    >
                        儲存交易
                    </button>
                </form>
            </div>
        </div>
    );
}
