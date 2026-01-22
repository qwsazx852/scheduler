export type TransactionType = 'income' | 'expense';

export interface Category {
    id: string;
    name: string;
    type: TransactionType;
    color: string;
}

export interface Transaction {
    id: string;
    amount: number;
    type: TransactionType;
    categoryId: string;
    date: string; // ISO string
    note?: string;
}

export interface DailySummary {
    date: string;
    income: number;
    expense: number;
}
