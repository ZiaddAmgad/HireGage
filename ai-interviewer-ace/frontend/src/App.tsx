import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import StartPage from './pages/StartPage';
import InterviewPage from './pages/InterviewPage';
import FeedbackPage from './pages/FeedbackPage';
import Layout from './components/layout/Layout';
import { InterviewProvider } from './context/InterviewContext';

function App() {
  return (
    <InterviewProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<StartPage />} />
            <Route path="/interview" element={<InterviewPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
          </Routes>
        </Layout>
      </Router>
    </InterviewProvider>
  );
}

export default App;