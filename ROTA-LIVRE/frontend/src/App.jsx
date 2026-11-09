
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { MapPin, Accessibility, AlertTriangle } from 'lucide-react'
import 'leaflet/dist/leaflet.css'
import './App.css'

const obstaculos = [
  {
    id: 1,
    tipo: 'Calçada danificada',
    latitude: -23.5505,
    longitude: -46.6333,
    status: 'Pendente',
  },
  {
    id: 2,
    tipo: 'Rampa bloqueada',
    latitude: -23.551,
    longitude: -46.634,
    status: 'Em análise',
  },
]

const iconeMapa = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <Accessibility size={30} />
          <div>
            <h1>ROTA LIVRE</h1>
            <p>Mobilidade e acessibilidade urbana</p>
          </div>
        </div>
        <span className="version">MVP 1.0</span>
      </header>

      <main className="main">
        <section className="sidebar">
          <h2>Mapa de acessibilidade</h2>
          <p>
            Consulte obstáculos urbanos que podem
            comprometer a mobilidade dos cidadãos.
          </p>

          <div className="summary">
            <MapPin size={20} />
            <span>
              {obstaculos.length} obstáculos identificados
            </span>
          </div>

          <h3>Ocorrências registradas</h3>

          <div className="obstacle-list">
            {obstaculos.map((obstaculo) => (
              <article className="obstacle-card" key={obstaculo.id}>
                <div className="obstacle-title">
                  <AlertTriangle size={18} />
                  <strong>{obstaculo.tipo}</strong>
                </div>

                <p>
                  Latitude: {obstaculo.latitude}
                  <br />
                  Longitude: {obstaculo.longitude}
                </p>

                <span className="status">{obstaculo.status}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="map-section" aria-label="Mapa de obstáculos urbanos">
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

            {obstaculos.map((obstaculo) => (
              <Marker
                key={obstaculo.id}
                position={[
                  obstaculo.latitude,
                  obstaculo.longitude,
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

      <footer className="footer">
        ROTA LIVRE · FIAP Global Solution CitizenTech 2026.2
      </footer>
    </div>
  )
}

export default App
