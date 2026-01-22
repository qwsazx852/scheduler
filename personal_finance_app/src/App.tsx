import { useState } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { TransactionForm } from './components/TransactionForm';
import { TransactionList } from './components/TransactionList';
import { CategoryManager } from './components/CategoryManager';
import { useFinance } from './hooks/useFinance';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'transactions' | 'categories'>('dashboard');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {
    transactions,
    categories,
    getBalance,
    getMonthlyStats,
    addTransaction,
    deleteTransaction,
    addCategory,
    deleteCategory
  } = useFinance();

  const handleAddTransaction = (data: any) => {
    addTransaction(data);
  };

  return (
    <>
      <Layout
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onAddTransaction={() => setIsModalOpen(true)}
      >
        {activeTab === 'dashboard' && (
          <Dashboard
            balance={getBalance()}
            monthlyStats={getMonthlyStats()}
            recentTransactions={transactions.slice(0, 5)}
          />
        )}
        {activeTab === 'transactions' && (
          <TransactionList
            transactions={transactions}
            categories={categories}
            onDeleteCallback={deleteTransaction}
          />
        )}
        {activeTab === 'categories' && (
          <CategoryManager
            categories={categories}
            onAdd={addCategory}
            onDelete={deleteCategory}
          />
        )}
      </Layout>


      <TransactionForm
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddTransaction}
        categories={categories}
      />
    </>
  );
}

export default App;

