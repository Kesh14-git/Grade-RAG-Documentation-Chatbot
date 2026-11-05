import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import Citations from './components/Citations';
import { getDocuments } from './services/api';
import './index.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [activeCitations, setActiveCitations] = useState(null);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [searchScope, setSearchScope] = useState('all'); // 'all' or 'selected'
  const [responseLanguage, setResponseLanguage] = useState('Auto'); // 'Auto', 'English', 'Tamil', 'Hindi'
  
  // Theme state
  const [theme, setTheme] = useState('light');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    }
  }, []);

  const fetchDocs = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  useEffect(() => {
    fetchDocs();
    const interval = setInterval(() => fetchDocs(), 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed);

  return (
    <div className="app-container">
      <Header 
        theme={theme} 
        setTheme={setTheme} 
        toggleSidebar={toggleSidebar}
      />
      
      <div className="main-content">
        <Sidebar 
          documents={documents} 
          fetchDocs={fetchDocs} 
          selectedDocumentIds={selectedDocumentIds}
          setSelectedDocumentIds={setSelectedDocumentIds}
          searchScope={searchScope}
          setSearchScope={setSearchScope}
          isCollapsed={sidebarCollapsed}
        />
        
        <Chat 
          setActiveCitations={setActiveCitations} 
          selectedDocumentIds={selectedDocumentIds}
          searchScope={searchScope}
          responseLanguage={responseLanguage}
          setResponseLanguage={setResponseLanguage}
        />
        
        <Citations 
          activeCitations={activeCitations} 
          setActiveCitations={setActiveCitations} 
        />
      </div>
    </div>
  );
}

export default App;
