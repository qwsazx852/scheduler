import { useState, useEffect } from 'react';
import type { Transaction, Category } from '../types';
import { v4 as uuidv4 } from 'uuid';


const DEFAULT_CATEGORIES: Category[] = [
    { id: '1', name: '薪資', type: 'income', color: 'bg-green-500' },
    { id: '2', name: '投資', type: 'income', color: 'bg-blue-500' },
    { id: '3', name: '飲食', type: 'expense', color: 'bg-orange-500' },
    { id: '4', name: '交通', type: 'expense', color: 'bg-yellow-500' },
    { id: '5', name: '購物', type: 'expense', color: 'bg-pink-500' },
    { id: '6', name: '娛樂', type: 'expense', color: 'bg-purple-500' },
    { id: '7', name: '居住', type: 'expense', color: 'bg-indigo-500' },
];

const STORAGE_KEYS = {
    TRANSACTIONS: 'wealthflow_transactions',
    CATEGORIES: 'wealthflow_categories',
};

export function useFinance() {
    const [transactions, setTransactions] = useState<Transaction[]>(() => {
        const stored = localStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
        return stored ? JSON.parse(stored) : [];
    });

    const [categories, setCategories] = useState<Category[]>(() => {
        const stored = localStorage.getItem(STORAGE_KEYS.CATEGORIES);
        return stored ? JSON.parse(stored) : DEFAULT_CATEGORIES;
    });

    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.TRANSACTIONS, JSON.stringify(transactions));
    }, [transactions]);

    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.CATEGORIES, JSON.stringify(categories));
    }, [categories]);

    const addTransaction = (transaction: Omit<Transaction, 'id'>) => {
        const newTransaction = { ...transaction, id: uuidv4() };
        setTransactions(prev => [newTransaction, ...prev]);
    };

    const deleteTransaction = (id: string) => {
        setTransactions(prev => prev.filter(t => t.id !== id));
    };

    const addCategory = (category: Omit<Category, 'id'>) => {
        const newCategory = { ...category, id: uuidv4() };
        setCategories(prev => [...prev, newCategory]);
    };

    const deleteCategory = (id: string) => {
        setCategories(prev => prev.filter(c => c.id !== id));
    };

    const getBalance = () => {
        return transactions.reduce((acc, curr) => {
            return curr.type === 'income' ? acc + curr.amount : acc - curr.amount;
        }, 0);
    };

    const getMonthlyStats = () => {
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();

        const currentMonthTransactions = transactions.filter(t => {
            const date = new Date(t.date);
            return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
        });

        const income = currentMonthTransactions
            .filter(t => t.type === 'income')
            .reduce((acc, t) => acc + t.amount, 0);

        const expense = currentMonthTransactions
            .filter(t => t.type === 'expense')
            .reduce((acc, t) => acc + t.amount, 0);

        return { income, expense };
    };

    return {
        transactions,
        categories,
        addTransaction,
        deleteTransaction,
        addCategory,
        deleteCategory,
        getBalance,
        getMonthlyStats,
    };
}

