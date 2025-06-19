import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import 'antd/dist/reset.css';
import './App.css';

import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ConfigPage from './pages/ConfigPage';
import SimulationPage from './pages/SimulationPage';
import ResultsPage from './pages/ResultsPage';
import ReportsPage from './pages/ReportsPage';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/config" element={<ConfigPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Routes>
          </Layout>
        </div>
      </Router>
    </ConfigProvider>
  );
}

export default App;
