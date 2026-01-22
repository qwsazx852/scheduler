import React from 'react';
import { LayoutDashboard, PlusCircle, List, PieChart, Wallet } from 'lucide-react';
import { cn } from '../utils/cn';

interface LayoutProps {
    children: React.ReactNode;
    activeTab: 'dashboard' | 'transactions' | 'categories';
    onTabChange: (tab: 'dashboard' | 'transactions' | 'categories') => void;
    onAddTransaction: () => void;
}

export function Layout({ children, activeTab, onTabChange, onAddTransaction }: LayoutProps) {
    const NavItem = ({
        tab,
        icon: Icon,
        label
    }: {
        tab: 'dashboard' | 'transactions' | 'categories',
        icon: React.ElementType,
        label: string
    }) => (
        <button
            onClick={() => onTabChange(tab)}
            className={cn(
                "flex flex-col md:flex-row items-center md:space-x-3 p-3 rounded-xl transition-all duration-200",
                activeTab === tab
                    ? "text-indigo-600 bg-indigo-50"
                    : "text-slate-500 hover:text-indigo-600 hover:bg-indigo-50/50"
            )}
        >
            <Icon className="w-6 h-6" />
            <span className="text-xs md:text-sm font-medium mt-1 md:mt-0">{label}</span>
        </button>
    );

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
            {/* Desktop Sidebar */}
            <aside className="hidden md:flex flex-col w-64 bg-white border-r border-slate-200 p-6 fixed h-full z-10">
                <div className="flex items-center space-x-3 mb-10 px-2">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white">
                        <Wallet className="w-6 h-6" />
                    </div>
                    <h1 className="text-xl font-bold text-slate-900">WealthFlow</h1>
                </div>

                <nav className="space-y-2 flex-1">
                    <NavItem tab="dashboard" icon={LayoutDashboard} label="總覽" />
                    <NavItem tab="transactions" icon={List} label="交易紀錄" />
                    <NavItem tab="categories" icon={PieChart} label="分類管理" />
                </nav>

                <button
                    onClick={onAddTransaction}
                    className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-xl transition-colors shadow-lg shadow-indigo-200"
                >
                    <PlusCircle className="w-5 h-5" />
                    <span className="font-semibold">記一筆</span>
                </button>
            </aside>

            {/* Mobile Header */}
            <header className="md:hidden bg-white border-b border-slate-200 p-4 sticky top-0 z-20 flex justify-between items-center">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
                        <Wallet className="w-5 h-5" />
                    </div>
                    <h1 className="text-lg font-bold text-slate-900">WealthFlow</h1>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 md:ml-64 pb-20 md:pb-0">
                <div className="max-w-5xl mx-auto p-4 md:p-8">
                    {children}
                </div>
            </main>

            {/* Mobile Bottom Navigation */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 px-6 py-2 flex justify-between items-center z-30 pb-safe">
                <NavItem tab="dashboard" icon={LayoutDashboard} label="總覽" />
                <div className="relative -top-5">
                    <button
                        onClick={onAddTransaction}
                        className="w-14 h-14 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-lg shadow-indigo-300 transform transition-transform active:scale-95"
                    >
                        <PlusCircle className="w-7 h-7" />
                    </button>
                </div>
                <NavItem tab="transactions" icon={List} label="紀錄" />
            </nav>
        </div>
    );
}
