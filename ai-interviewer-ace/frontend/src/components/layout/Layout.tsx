import React from 'react';
import { Briefcase } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-7xl mx-auto flex items-center">
          <div className="flex items-center space-x-2">
            <Briefcase className="h-8 w-8 text-blue-800" />
            <h1 className="text-xl font-bold text-gray-900">AI Interviewer Ace</h1>
          </div>
        </div>
      </header>
      <main className="flex-1 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {children}
      </main>
      <footer className="bg-white py-4 px-6 border-t border-gray-100">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} AI Interviewer Ace. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Layout;