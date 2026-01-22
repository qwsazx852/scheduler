import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LandingPage } from './components/LandingPage';
import { LessonView } from './components/LessonView';
import './App.css'

function App() {

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<LandingPage />} />
        <Route path="lesson/:lessonId" element={<LessonView />} />
      </Route>
    </Routes>
  );
}

export default App
