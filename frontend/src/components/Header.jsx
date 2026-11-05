import React from 'react';
import { Sun, Moon, Menu, Settings, FileText } from 'lucide-react';

export default function Header({ 
  theme, 
  setTheme, 
  toggleSidebar
}) {
  
  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <button className="icon-btn mobile-only" onClick={toggleSidebar} aria-label="Toggle Menu" style={{display: "none"}}>
          <Menu size={20} />
        </button>
        <div className="brand">
          <FileText size={24} className="brand-icon" style={{color: 'var(--accent)'}} />
          <span>NPN AI Workspace</span>
        </div>
      </div>
      
      <div className="header-right">
        {/* Status Indicator */}
        <div style={{display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--success)'}}>
          <span style={{width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success)'}}></span>
          <span className="hide-mobile">RAG Ready</span>
        </div>

        {/* Theme Toggle */}
        <button 
          className="icon-btn" 
          onClick={handleThemeToggle}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>
        
        {/* Settings (Placeholder) */}
        <button className="icon-btn" title="Settings">
          <Settings size={18} />
        </button>
      </div>
    </header>
  );
}
