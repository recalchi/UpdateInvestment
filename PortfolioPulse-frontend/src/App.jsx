import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Progress } from '@/components/ui/progress.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Settings, 
  BarChart3, 
  PieChart, 
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import './App.css';

function App() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [logs, setLogs] = useState([]);

  // Simular dados da carteira
  useEffect(() => {
    setPortfolioData({
      totalValue: 125430.50,
      monthlyReturn: 3.2,
      categories: [
        { name: 'Ações LP', value: 35.2, change: 2.1, color: '#10b981' },
        { name: 'Ações DY', value: 28.5, change: 1.8, color: '#3b82f6' },
        { name: 'STOCKS', value: 18.3, change: 4.2, color: '#8b5cf6' },
        { name: 'FII', value: 12.0, change: 0.9, color: '#f59e0b' },
        { name: 'Cripto', value: 4.5, change: -2.1, color: '#ef4444' },
        { name: 'Renda Fixa', value: 1.5, change: 0.5, color: '#6b7280' }
      ],
      recentUpdates: [
        { asset: 'PRIO3', action: 'Atualizado', time: '2 min', status: 'success' },
        { asset: 'BBSE3', action: 'Rebalanceado', time: '5 min', status: 'warning' },
        { asset: 'META', action: 'Novo preço', time: '8 min', status: 'info' }
      ]
    });
    setLastUpdate(new Date());
  }, []);

  const handleUpdate = async () => {
    setIsUpdating(true);
    setLogs([]);
    
    const updateSteps = [
      'Conectando com Nord Research...',
      'Extraindo dados de Ações DY...',
      'Processando FIIs...',
      'Atualizando Stocks US...',
      'Calculando rentabilidades...',
      'Sincronizando com planilha...',
      'Atualização concluída!'
    ];

    for (let i = 0; i < updateSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLogs(prev => [...prev, { 
        message: updateSteps[i], 
        time: new Date().toLocaleTimeString(),
        type: i === updateSteps.length - 1 ? 'success' : 'info'
      }]);
    }
    
    setIsUpdating(false);
    setLastUpdate(new Date());
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                PortfolioPulse
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-gray-300 border-gray-600">
                {lastUpdate ? `Última atualização: ${lastUpdate.toLocaleTimeString()}` : 'Nunca atualizado'}
              </Badge>
              <Button 
                onClick={handleUpdate} 
                disabled={isUpdating}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isUpdating ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Atualizando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Atualizar Carteira
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Valor Total */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Valor Total da Carteira</CardDescription>
              <CardTitle className="text-3xl font-bold text-white">
                R$ {portfolioData?.totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                {portfolioData?.monthlyReturn > 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ${
                  portfolioData?.monthlyReturn > 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {portfolioData?.monthlyReturn > 0 ? '+' : ''}{portfolioData?.monthlyReturn}% no mês
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Status da Automação */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Status da Automação</CardDescription>
              <CardTitle className="text-xl text-white">
                {isUpdating ? 'Executando...' : 'Pronto'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                {isUpdating ? (
                  <Clock className="w-4 h-4 text-yellow-500" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                <span className="text-sm text-gray-300">
                  {isUpdating ? 'Processando dados...' : 'Todos os sistemas operacionais'}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Próxima Execução */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardDescription className="text-gray-400">Próxima Execução Automática</CardDescription>
              <CardTitle className="text-xl text-white">Em 18 dias</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-300">Agendado para 1º do próximo mês</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-gray-800 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-gray-700">Visão Geral</TabsTrigger>
            <TabsTrigger value="categories" className="data-[state=active]:bg-gray-700">Categorias</TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-gray-700">Logs</TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-gray-700">Configurações</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Distribuição da Carteira */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <PieChart className="w-5 h-5 mr-2" />
                    Distribuição da Carteira
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {portfolioData?.categories.map((category, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-300">{category.name}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-400">{category.value}%</span>
                          <span className={`text-xs ${
                            category.change > 0 ? 'text-green-500' : 'text-red-500'
                          }`}>
                            {category.change > 0 ? '+' : ''}{category.change}%
                          </span>
                        </div>
                      </div>
                      <Progress 
                        value={category.value} 
                        className="h-2"
                        style={{ '--progress-background': category.color }}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Atualizações Recentes */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Atualizações Recentes</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {portfolioData?.recentUpdates.map((update, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          update.status === 'success' ? 'bg-green-500' :
                          update.status === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                        }`} />
                        <div>
                          <p className="text-sm font-medium text-white">{update.asset}</p>
                          <p className="text-xs text-gray-400">{update.action}</p>
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">{update.time}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="categories" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {portfolioData?.categories.map((category, index) => (
                <Card key={index} className="bg-gray-800 border-gray-700">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg text-white">{category.name}</CardTitle>
                    <CardDescription className="text-2xl font-bold text-white">
                      {category.value}%
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      {category.change > 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`text-sm ${
                        category.change > 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {category.change > 0 ? '+' : ''}{category.change}% no período
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Terminal de Logs</CardTitle>
                <CardDescription className="text-gray-400">
                  Acompanhe o progresso da automação em tempo real
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                  {logs.length === 0 ? (
                    <p className="text-gray-500">Nenhum log disponível. Execute uma atualização para ver os logs.</p>
                  ) : (
                    logs.map((log, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <span className="text-gray-500">[{log.time}]</span>
                        <span className={
                          log.type === 'success' ? 'text-green-400' :
                          log.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                        }>
                          {log.message}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  Configurações da Automação
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Frequência de Atualização</label>
                  <select className="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                    <option>Mensal (Recomendado)</option>
                    <option>Quinzenal</option>
                    <option>Semanal</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Caminho da Planilha Local</label>
                  <input 
                    type="text" 
                    className="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    placeholder="C:\Users\Renan\OneDrive\Documentos\planilhas\Carteira_Investimento_test\"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="notifications" className="rounded" />
                  <label htmlFor="notifications" className="text-sm text-gray-300">
                    Enviar notificações por email após atualizações
                  </label>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Salvar Configurações
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;

