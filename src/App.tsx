import IndiaMap from './components/IndiaMap';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🇮🇳 India Job Map</h1>
        <p>Discover job opportunities across India</p>
      </header>
      <main className="app-main">
        <IndiaMap />
      </main>
    </div>
  );
}

export default App;
