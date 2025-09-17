import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';

function App() {
    const [portfolioSummary, setPortfolioSummary] = useState(null);
    const [assetDetails, setAssetDetails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchPortfolioData();
    }, []);

    const fetchPortfolioData = async () => {
        setLoading(true);
        setError(null);
        try {
            // In a real application, this would be an API call to your backend
            // For now, we'll simulate data or load from a static JSON if available
            const response = await fetch('/api/portfolio_data'); // Placeholder API endpoint
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setPortfolioSummary(data.summary);
            setAssetDetails(data.asset_details);
        } catch (e) {
            console.error("Failed to fetch portfolio data:", e);
            setError("Failed to load portfolio data. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="container">Loading portfolio data...</div>;
    }

    if (error) {
        return <div className="container error-message">Error: {error}</div>;
    }

    return (
        <div className="container">
            <h1>PortfolioPulse Dashboard</h1>

            <div className="section">
                <h2>Resumo da Carteira</h2>
                {portfolioSummary ? (
                    <div className="metric-card">
                        <h3>Visão Geral</h3>
                        <p><strong>Valor Total Atual:</strong> R$ {portfolioSummary.ValorTotalAtual?.toFixed(2) || 'N/A'}</p>
                        <p><strong>Total Investido:</strong> R$ {portfolioSummary.TotalInvestido?.toFixed(2) || 'N/A'}</p>
                        <p><strong>Lucro/Prejuízo:</strong> R$ {portfolioSummary.LucroPrejuizo?.toFixed(2) || 'N/A'}</p>
                        <p><strong>ROI Percentual:</strong> {portfolioSummary.ROI_Percentual?.toFixed(2) || 'N/A'}%</p>
                    </div>
                ) : (
                    <p>Nenhum resumo de carteira disponível.</p>
                )}
            </div>

            <div className="section">
                <h2>Detalhes por Ativo</h2>
                {assetDetails.length > 0 ? (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Ativo</th>
                                <th>Quantidade</th>
                                <th>Preço Médio</th>
                                <th>Preço Atual</th>
                                <th>Valor Atual</th>
                                <th>Lucro/Prejuízo</th>
                                <th>ROI (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {assetDetails.map((asset, index) => (
                                <tr key={index}>
                                    <td>{asset.Ativo}</td>
                                    <td>{asset.Quantidade}</td>
                                    <td>R$ {asset.PrecoMedio?.toFixed(2)}</td>
                                    <td>R$ {asset.PrecoAtual?.toFixed(2)}</td>
                                    <td>R$ {asset.ValorAtual?.toFixed(2)}</td>
                                    <td>R$ {asset.LucroPrejuizo?.toFixed(2)}</td>
                                    <td>{asset.ROI_Percentual?.toFixed(2)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>Nenhum detalhe de ativo disponível.</p>
                )}
            </div>

            <button onClick={fetchPortfolioData} className="button">
                Atualizar Dados
            </button>
        </div>
    );
}

// Render the React application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);

