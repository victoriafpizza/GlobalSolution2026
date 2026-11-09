
import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { MapPin, Accessibility, AlertTriangle } from 'lucide-react'

import 'leaflet/dist/leaflet.css'
import './App.css'

// Configuração dos marcadores do mapa
const iconeMapa = new Icon({
  iconUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

function App() {
  // Estados da aplicação
  const [obstaculos, setObstaculos] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)

  // Buscar obstáculos diretamente da API FastAPI
  useEffect(() => {
    const controller = new AbortController()

    async function carregarObstaculos() {
      try {
        setCarregando(true)
        setErro(null)

        const resposta = await fetch('/api/obstacles', {
          signal: controller.signal,
        })

        if (!resposta.ok) {
          throw new Error(`Erro HTTP ${resposta.status}`)
        }

        const dados = await resposta.json()

        if (!Array.isArray(dados.obstaculos)) {
          throw new Error('Formato inválido recebido da API')
        }

        setObstaculos(dados.obstaculos)
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Erro ao carregar obstáculos:', error)
          setErro('Não foi possível carregar os obstáculos.')
        }
      } finally {
        if (!controller.signal.aborted) {
          setCarregando(false)
        }
      }
    }

    carregarObstaculos()

    return () => controller.abort()
  }, [])

  return (
    <div className="app">
      {/* Cabeçalho */}
      <header className="header">
        <div className="brand">
          <Accessibility size={30} aria-hidden="true" />

          <div>
            <h1>ROTA LIVRE</h1>
            <p>Mobilidade e acessibilidade urbana</p>
          </div>
        </div>

        <span className="version">MVP 1.0</span>
      </header>

      {/* Conteúdo principal */}
      <main className="main">
        {/* Painel lateral */}
        <section className="sidebar">
          <h2>Mapa de acessibilidade</h2>

          <p>
            Consulte obstáculos urbanos que podem
            comprometer a mobilidade dos cidadãos.
          </p>

          {/* Resumo de ocorrências */}
          <div className="summary" aria-live="polite">
            <MapPin size={20} aria-hidden="true" />

            <span>
              {carregando
                ? 'Carregando obstáculos...'
                : erro
                  ? 'Dados indisponíveis'
                  : `${obstaculos.length} obstáculos identificados`}
            </span>
          </div>

          {/* Mensagem de erro */}
          {erro && (
            <p role="alert" className="error-message">
              {erro} Verifique se a API está funcionando.
            </p>
          )}

          <h3>Ocorrências registradas</h3>

          {/* Lista de obstáculos */}
          <div className="obstacle-list">
            {!carregando && !erro && obstaculos.length === 0 && (
              <p>Nenhum obstáculo registrado.</p>
            )}

            {obstaculos.map((obstaculo) => (
              <article
                className="obstacle-card"
                key={obstaculo.id}
              >
                <div className="obstacle-title">
                  <AlertTriangle size={18} aria-hidden="true" />

                  <strong>{obstaculo.tipo}</strong>
                </div>

                <p>
                  Latitude: {obstaculo.latitude}
                  <br />
                  Longitude: {obstaculo.longitude}
                </p>

                <span className="status">
                  {obstaculo.status}
                </span>
              </article>
            ))}
          </div>
        </section>

        {/* Mapa interativo */}
        <section
          className="map-section"
          aria-label="Mapa interativo de obstáculos urbanos"
        >
          <MapContainer
            center={[-23.5505, -46.6333]}
            zoom={15}
            scrollWheelZoom={true}
            className="map"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Marcadores recebidos da API */}
            {obstaculos
              .filter(
                (obstaculo) =>
                  Number.isFinite(Number(obstaculo.latitude)) &&
                  Number.isFinite(Number(obstaculo.longitude)) &&
                  Number(obstaculo.latitude) >= -90 &&
                  Number(obstaculo.latitude) <= 90 &&
                  Number(obstaculo.longitude) >= -180 &&
                  Number(obstaculo.longitude) <= 180 &&
                  obstaculo.latitude != null &&
                  obstaculo.longitude != null
              )
              .map((obstaculo) => (
                <Marker
                  key={obstaculo.id}
                  position={[
                    Number(obstaculo.latitude),
                    Number(obstaculo.longitude),
                  ]}
                  icon={iconeMapa}
                >
                  <Popup>
                    <strong>{obstaculo.tipo}</strong>
                    <p>Status: {obstaculo.status}</p>
                  </Popup>
                </Marker>
              ))}
          </MapContainer>
        </section>
      </main>

      {/* Rodapé */}
      <footer className="footer">
        ROTA LIVRE · FIAP Global Solution CitizenTech 2026.2
      </footer>
    </div>
  )
}

export default App
