import React from 'react';
import ComplianceDashboard from '../components/ComplianceDashboard';
import DeviceList from '../components/DeviceList';

const Home = () => {
    return (
        <div>
            <h1>CompliNet Dashboard</h1>
            <ComplianceDashboard />
            <DeviceList />
        </div>
    );
};

export default Home;