import React from 'react';
import type { Transaction, TransactionType } from '../types';
import { ArrowUpRight, ArrowDownRight, Wallet, PieChart as PieChartIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { cn } from '../utils/cn';

interface DashboardProps {
    balance: number;
    monthlyStats: {
        income: number;
        expense: number;
    };
    recentTransactions: Transaction[];
}

export function Dashboard({ balance, monthlyStats, recentTransactions }: DashboardProps) {
    // Prepare data for the chart (Expense breakdown by category logic would go here)
    // For MVP, we'll visualize Income vs Expense
    const chartData = [
        { name: '收入', value: monthlyStats.income, color: '#10b981' }, // emerald-500
        { name: '支出', value: monthlyStats.expense, color: '#ef4444' }, // red-500
    ];

    // If no data, show empty state in chart
    const hasData = monthlyStats.income > 0 || monthlyStats.expense > 0;

    const StatCard = ({
        label,
        amount,
        type,
        icon: Icon
    }: {
        label: string,
        amount: number,
        type?: TransactionType,
        icon: React.ElementType
    }) => (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between h-32">
            <div className="flex items-center justify-between">
                <span className="text-slate-500 text-sm font-medium">{label}</span>
                <div className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center",
                    type === 'income' ? "bg-green-50 text-green-600" :
                        type === 'expense' ? "bg-red-50 text-red-600" :
                            "bg-indigo-50 text-indigo-600"
                )}>
                    <Icon className="w-5 h-5" />
                </div>
            </div>
            <div>
                <h3 className="text-2xl font-bold text-slate-900">
                    ${amount.toLocaleString()}
                </h3>
                {type && (
                    <p className={cn(
                        "text-xs font-medium mt-1 flex items-center",
                        type === 'income' ? "text-green-600" : "text-red-600"
                    )}>
                        {type === 'income' ? '+' : '-'}{type === 'income' ? '本月收入' : '本月支出'}
                    </p>
                )}
            </div>
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard
                    label="總資產"
                    amount={balance}
                    icon={Wallet}
                />
                <StatCard
                    label="本月收入"
                    amount={monthlyStats.income}
                    type="income"
                    icon={ArrowUpRight}
                />
                <StatCard
                    label="本月支出"
                    amount={monthlyStats.expense}
                    type="expense"
                    icon={ArrowDownRight}
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Chart Section */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col items-center justify-center min-h-[300px]">
                    <h3 className="text-lg font-bold text-slate-900 mb-4 w-full flex items-center gap-2">
                        <PieChartIcon className="w-5 h-5 text-indigo-500" />
                        收支概況
                    </h3>
                    <div className="w-full h-[200px]">
                        {hasData ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={chartData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {chartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-slate-400">
                                <PieChartIcon className="w-12 h-12 mb-2 opacity-50" />
                                <p>尚無數據</p>
                            </div>
                        )}
                    </div>
                    {hasData && (
                        <div className="flex justify-center gap-4 mt-4 text-sm font-medium">
                            <div className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded-full bg-[#10b981]" />
                                <span>收入</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded-full bg-[#ef4444]" />
                                <span>支出</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Transactions List Section */}
                <div className="md:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-slate-900">近期交易</h3>
                    </div>

                    <div className="space-y-4">
                        {recentTransactions.length === 0 ? (
                            <p className="text-slate-500 text-center py-8">尚無交易紀錄</p>
                        ) : (
                            recentTransactions.map(t => (
                                <div key={t.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className={cn(
                                            "w-10 h-10 rounded-full flex items-center justify-center text-white",
                                            t.type === 'income' ? "bg-green-500" : "bg-red-500" // Simplified for dashboard
                                        )}>
                                            {t.type === 'income' ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-slate-900">{t.note || '未分類'}</p>
                                            <p className="text-xs text-slate-500">{new Date(t.date).toLocaleDateString()}</p>
                                        </div>
                                    </div>
                                    <span className={cn(
                                        "font-bold",
                                        t.type === 'income' ? "text-green-600" : "text-slate-900"
                                    )}>
                                        {t.type === 'income' ? '+' : '-'}${t.amount.toLocaleString()}
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
