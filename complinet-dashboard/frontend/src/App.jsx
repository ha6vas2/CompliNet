import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import Settings from './pages/Settings';
import ComplianceDashboard from './components/ComplianceDashboard';
import DeviceList from './components/DeviceList';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/compliance" element={<ComplianceDashboard />} />
                <Route path="/devices" element={<DeviceList />} />
            </Routes>
        </Router>
    );
};

export default App;