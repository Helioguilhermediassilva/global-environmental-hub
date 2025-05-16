import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import './MapComponent.css';

// Tipos para os hotspots
interface Hotspot {
  id: string;
  latitude: number;
  longitude: number;
  acquisition_date: string;
  confidence: number;
  source: string;
  brightness?: number;
  frp?: number;
  biome?: string;
  land_use?: string;
}

// Props para o componente
interface MapComponentProps {
  apiUrl?: string;
  initialCenter?: [number, number];
  initialZoom?: number;
}

const MapComponent: React.FC<MapComponentProps> = ({
  apiUrl = 'http://localhost:8000/hotspots',
  initialCenter = [-3.4653, -62.2159], // Centro da Amazônia
  initialZoom = 5
}) => {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    dateRange: '7',
    source: 'all',
    minConfidence: '0'
  });

  // Função para buscar dados da API
  const fetchHotspots = async () => {
    setLoading(true);
    setError(null);

    try {
      // Construir URL com filtros
      let url = apiUrl;
      const params = new URLSearchParams();
      
      // Adicionar filtros à URL
      if (filters.dateRange !== 'all') {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(filters.dateRange));
        
        params.append('start_date', startDate.toISOString());
        params.append('end_date', endDate.toISOString());
      }
      
      if (filters.source !== 'all') {
        params.append('source', filters.source);
      }
      
      if (filters.minConfidence !== '0') {
        params.append('min_confidence', filters.minConfidence);
      }
      
      // Adicionar parâmetros à URL se houver algum
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      // Fazer requisição à API
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      
      const data = await response.json();
      setHotspots(data);
    } catch (err) {
      console.error('Erro ao buscar dados:', err);
      setError('Falha ao carregar dados de hotspots. Por favor, tente novamente mais tarde.');
      
      // Dados simulados para desenvolvimento
      setHotspots([
        {
          id: '1',
          latitude: -9.45678,
          longitude: -56.78901,
          acquisition_date: '2025-05-15T14:30:00',
          confidence: 85,
          source: 'VIIRS',
          brightness: 325.7,
          frp: 45.2,
          biome: 'Amazon Rainforest',
          land_use: 'Forest'
        },
        {
          id: '2',
          latitude: -8.12345,
          longitude: -55.54321,
          acquisition_date: '2025-05-15T15:45:00',
          confidence: 90,
          source: 'MODIS',
          brightness: 310.5,
          frp: 38.7,
          biome: 'Amazon Rainforest',
          land_use: 'Forest'
        },
        {
          id: '3',
          latitude: -10.98765,
          longitude: -57.12345,
          acquisition_date: '2025-05-15T16:15:00',
          confidence: 75,
          source: 'VIIRS',
          brightness: 330.2,
          frp: 52.1,
          biome: 'Amazon Rainforest',
          land_use: 'Forest'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Buscar dados quando o componente montar ou os filtros mudarem
  useEffect(() => {
    fetchHotspots();
  }, [filters]);

  // Função para lidar com mudanças nos filtros
  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Função para determinar a cor do marcador com base na confiança
  const getMarkerColor = (confidence: number) => {
    if (confidence >= 90) return '#e74c3c'; // Vermelho para alta confiança
    if (confidence >= 70) return '#f39c12'; // Laranja para média confiança
    return '#f1c40f'; // Amarelo para baixa confiança
  };

  return (
    <div className="map-component">
      <div className="map-filters">
        <div className="filter-group">
          <label htmlFor="dateRange">Período:</label>
          <select 
            id="dateRange" 
            name="dateRange" 
            value={filters.dateRange} 
            onChange={handleFilterChange}
          >
            <option value="1">Últimas 24 horas</option>
            <option value="7">Últimos 7 dias</option>
            <option value="30">Últimos 30 dias</option>
            <option value="all">Todos os dados</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="source">Fonte:</label>
          <select 
            id="source" 
            name="source" 
            value={filters.source} 
            onChange={handleFilterChange}
          >
            <option value="all">Todas as fontes</option>
            <option value="MODIS">MODIS</option>
            <option value="VIIRS">VIIRS</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="minConfidence">Confiança mínima:</label>
          <select 
            id="minConfidence" 
            name="minConfidence" 
            value={filters.minConfidence} 
            onChange={handleFilterChange}
          >
            <option value="0">Todas</option>
            <option value="50">50%</option>
            <option value="75">75%</option>
            <option value="90">90%</option>
          </select>
        </div>
        
        <button 
          className="refresh-button" 
          onClick={() => fetchHotspots()} 
          disabled={loading}
        >
          {loading ? 'Carregando...' : 'Atualizar'}
        </button>
      </div>
      
      <div className="map-container">
        {loading && <div className="loading-overlay">Carregando dados do mapa...</div>}
        
        {error && <div className="error-message">{error}</div>}
        
        <MapContainer 
          center={initialCenter} 
          zoom={initialZoom} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {hotspots.map((hotspot) => (
            <CircleMarker
              key={hotspot.id}
              center={[hotspot.latitude, hotspot.longitude]}
              radius={5 + (hotspot.confidence / 20)} // Tamanho baseado na confiança
              pathOptions={{ 
                fillColor: getMarkerColor(hotspot.confidence),
                color: '#000',
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.6
              }}
            >
              <Popup>
                <div className="hotspot-popup">
                  <h3>Foco de Calor {hotspot.id}</h3>
                  <p><strong>Fonte:</strong> {hotspot.source}</p>
                  <p><strong>Confiança:</strong> {hotspot.confidence}%</p>
                  <p><strong>Data:</strong> {new Date(hotspot.acquisition_date).toLocaleString()}</p>
                  <p>
                    <strong>Localização:</strong> {hotspot.latitude.toFixed(5)}, {hotspot.longitude.toFixed(5)}
                  </p>
                  {hotspot.brightness && (
                    <p><strong>Temperatura:</strong> {hotspot.brightness.toFixed(1)} K</p>
                  )}
                  {hotspot.frp && (
                    <p><strong>Potência Radiativa:</strong> {hotspot.frp.toFixed(1)} MW</p>
                  )}
                  {hotspot.biome && (
                    <p><strong>Bioma:</strong> {hotspot.biome}</p>
                  )}
                  {hotspot.land_use && (
                    <p><strong>Uso do Solo:</strong> {hotspot.land_use}</p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      
      <div className="map-stats">
        <div className="stat-item">
          <span className="stat-value">{hotspots.length}</span>
          <span className="stat-label">Focos de calor</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">
            {hotspots.filter(h => h.confidence >= 90).length}
          </span>
          <span className="stat-label">Alta confiança</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">
            {Object.keys(hotspots.reduce((acc, h) => {
              acc[h.source] = true;
              return acc;
            }, {} as Record<string, boolean>)).length}
          </span>
          <span className="stat-label">Fontes</span>
        </div>
      </div>
    </div>
  );
};

export default MapComponent;
