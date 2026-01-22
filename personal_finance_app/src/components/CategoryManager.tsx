import { useState } from 'react';
import type { Category, TransactionType } from '../types';
import { Plus, X, Trash2 } from 'lucide-react';
import { cn } from '../utils/cn';

interface CategoryManagerProps {
    categories: Category[];
    onAdd: (category: Omit<Category, 'id'>) => void;
    onDelete: (id: string) => void;
}

const PRESET_COLORS = [
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500',
    'bg-lime-500', 'bg-green-500', 'bg-emerald-500', 'bg-teal-500',
    'bg-cyan-500', 'bg-sky-500', 'bg-blue-500', 'bg-indigo-500',
    'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500', 'bg-pink-500',
    'bg-rose-500', 'bg-slate-500'
];

export function CategoryManager({ categories, onAdd, onDelete }: CategoryManagerProps) {
    const [isAdding, setIsAdding] = useState(false);
    const [newName, setNewName] = useState('');
    const [newType, setNewType] = useState<TransactionType>('expense');
    const [newColor, setNewColor] = useState(PRESET_COLORS[0]);

    const handleAdd = (e: React.FormEvent) => {
        e.preventDefault();
        if (!newName.trim()) return;

        onAdd({
            name: newName,
            type: newType,
            color: newColor
        });

        setNewName('');
        setIsAdding(false);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900">分類管理</h2>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-50 text-indigo-600 rounded-xl hover:bg-indigo-100 transition-colors font-medium"
                >
                    {isAdding ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                    <span>{isAdding ? '取消' : '新增分類'}</span>
                </button>
            </div>

            {/* Add Category Form */}
            <div className={cn(
                "bg-white rounded-2xl shadow-sm border border-slate-100 p-6 transition-all duration-300 overflow-hidden",
                isAdding ? "max-h-96 opacity-100 mb-6" : "max-h-0 opacity-0 p-0 border-0 m-0"
            )}>
                <form onSubmit={handleAdd} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">類型</label>
                        <div className="flex space-x-2">
                            <button
                                type="button"
                                onClick={() => setNewType('expense')}
                                className={cn(
                                    "flex-1 py-2 rounded-lg text-sm font-medium border transition-colors",
                                    newType === 'expense'
                                        ? "border-red-500 bg-red-50 text-red-600"
                                        : "border-slate-200 text-slate-500 hover:bg-slate-50"
                                )}
                            >
                                支出
                            </button>
                            <button
                                type="button"
                                onClick={() => setNewType('income')}
                                className={cn(
                                    "flex-1 py-2 rounded-lg text-sm font-medium border transition-colors",
                                    newType === 'income'
                                        ? "border-green-500 bg-green-50 text-green-600"
                                        : "border-slate-200 text-slate-500 hover:bg-slate-50"
                                )}
                            >
                                收入
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">名稱</label>
                        <input
                            type="text"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            placeholder="例如：健身、Netflix..."
                            className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">顏色</label>
                        <div className="flex flex-wrap gap-2">
                            {PRESET_COLORS.map(color => (
                                <button
                                    key={color}
                                    type="button"
                                    onClick={() => setNewColor(color)}
                                    className={cn(
                                        "w-8 h-8 rounded-full transition-transform hover:scale-110",
                                        color,
                                        newColor === color ? "ring-2 ring-offset-2 ring-slate-400 scale-110" : ""
                                    )}
                                />
                            ))}
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-colors"
                    >
                        確認新增
                    </button>
                </form>
            </div>

            {/* Categories List */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {categories.map(category => (
                    <div key={category.id} className="bg-white p-4 rounded-xl border border-slate-100 flex items-center justify-between group hover:shadow-md transition-all">
                        <div className="flex items-center space-x-3">
                            <div className={cn("w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg", category.color)}>
                                {category.name[0]}
                            </div>
                            <div>
                                <h3 className="font-bold text-slate-900">{category.name}</h3>
                                <span className={cn(
                                    "text-xs px-2 py-0.5 rounded-full",
                                    category.type === 'income' ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                                )}>
                                    {category.type === 'income' ? '收入' : '支出'}
                                </span>
                            </div>
                        </div>
                        <button
                            onClick={() => onDelete(category.id)}
                            className="text-slate-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 p-2"
                            title="刪除"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
