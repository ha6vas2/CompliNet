import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ComplianceDashboard = () => {
    const [complianceData, setComplianceData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchComplianceData = async () => {
            try {
                const response = await axios.get('/api/compliance');
                setComplianceData(response.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchComplianceData();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <h1>Compliance Dashboard</h1>
            <ul>
                {complianceData.map((item) => (
                    <li key={item.id}>
                        <h2>{item.name}</h2>
                        <p>Status: {item.status}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ComplianceDashboard;