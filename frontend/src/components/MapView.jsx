import React, { useEffect, useRef } from 'react';
import Map, { Source, Layer, Marker, NavigationControl } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import Legend from './Legend';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

// 1. Curved Great-Circle approximation for a natural shipping lane
const PRIMARY_ROUTE = {
  type: 'FeatureCollection',
  features: [{ 
    type: 'Feature', 
    geometry: { 
      type: 'LineString', 
      coordinates: [
        [45.0, 23.0],   // Saudi Arabia
        [51.0, 25.5],   // Curve point 1 (Persian Gulf)
        [56.4, 26.5],   // Strait of Hormuz
        [63.0, 24.0],   // Curve point 2 (Arabian Sea)
        [70.0, 22.4]    // Jamnagar Port
      ] 
    } 
  }]
};

// 2. The alternative route that appears when the optimizer finishes
const ALTERNATIVE_ROUTE = {
  type: 'FeatureCollection',
  features: [{ 
    type: 'Feature', 
    geometry: { 
      type: 'LineString', 
      coordinates: [
        [45.0, 23.0], 
        [40.0, -15.0], // Waypoint: Cape of Good Hope logic
        [70.0, 22.4]
      ] 
    } 
  }]
};

export default function MapView({ isDisrupted, showReroute, isSimulating }) {
  const mapRef = useRef(null);
  const rotationRef = useRef(null);

  // --- CAMERA ROTATION ---
  // Ambient Camera Rotation (0.2 degrees per frame update)
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current.getMap();

    const rotateCamera = (timestamp) => {
      // Pause rotation if actively running a simulation to focus operator attention
      if (!isSimulating && map.isStyleLoaded()) {
        map.rotateTo((timestamp / 150) % 360, { duration: 0 });
      }
      rotationRef.current = requestAnimationFrame(rotateCamera);
    };

    map.on('load', () => {
      rotateCamera(0);
    });

    return () => cancelAnimationFrame(rotationRef.current);
  }, [isSimulating]);

  // --- GEOPOLITICAL COMPLIANCE FIX ---
  // Forces Mapbox to use the Indian worldview (IN) for correct borders 
  // around Jammu & Kashmir and Arunachal Pradesh.
  const handleMapLoad = (e) => {
    const map = e.target;
    const style = map.getStyle();
    
    if (!style || !style.layers) return;

    style.layers.forEach((layer) => {
      const filter = map.getFilter(layer.id);
      
      if (filter) {
        const filterStr = JSON.stringify(filter);
        if (filterStr.includes('"US"')) {
          try {
            const indianFilter = JSON.parse(filterStr.replace(/"US"/g, '"IN"'));
            map.setFilter(layer.id, indianFilter);
          } catch (err) {
            console.error('Failed to update worldview for layer', layer.id);
          }
        }
      }
    });
  };

  return (
    <div className="w-full h-full relative">
      <Map
        ref={mapRef}
        initialViewState={{ 
          longitude: 62.0, 
          latitude: 19.0,  
          zoom: 3.8,       
          bearing: 0, 
          pitch: 35 
        }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
        dragRotate={true}
        interactive={!isSimulating}
        onLoad={handleMapLoad}
      >
        <NavigationControl position="bottom-right" showCompass={false} />

        {/* --- MAP LAYERS --- */}

        {/* 1. Primary Route Base (Solid Line) */}
        <Source id="route-base" type="geojson" data={PRIMARY_ROUTE}>
          <Layer 
            id="route-line-base" type="line" 
            paint={{ 
              'line-color': isDisrupted ? '#ff003c' : '#1e293b', 
              'line-width': isDisrupted ? 1 : 2 
            }} 
          />
        </Source>

        {/* 2. Primary Route Flow (Dashed Overlay) */}
        <Source id="route-flow" type="geojson" data={PRIMARY_ROUTE}>
          <Layer 
            id="route-line-flow" type="line" 
            paint={{ 
              'line-color': isDisrupted ? '#ff003c' : '#00f3ff', 
              'line-width': 2, 
              'line-dasharray': [1, 3]
            }} 
          />
        </Source>

        {/* 3. Alternative Reroute (Only visible after Optimization phase) */}
        {showReroute && (
          <Source id="route-alt-flow" type="geojson" data={ALTERNATIVE_ROUTE}>
            <Layer 
              id="route-line-alt-flow" type="line" 
              paint={{ 
                'line-color': '#00f3ff', 
                'line-width': 2.5, 
                'line-dasharray': [2, 4] 
              }} 
            />
          </Source>
        )}

        {/* --- NATIVE HTML MARKERS --- */}
        
        {/* SUPPLIER: Saudi Arabia */}
        <Marker longitude={45.0} latitude={23.0} anchor="center">
          <div className="flex flex-col items-center cursor-pointer group">
            <span className="text-tactical-cyan text-lg drop-shadow-[0_0_8px_rgba(0,243,255,0.8)]">◉</span>
            <span className="font-mono text-[9px] uppercase tracking-widest text-slate-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity bg-panel/80 px-1 rounded">Saudi Arabia</span>
          </div>
        </Marker>

        {/* CORRIDOR: Strait of Hormuz */}
        <Marker longitude={56.4} latitude={26.5} anchor="center">
          <div className="flex flex-col items-center cursor-crosshair group relative">
            {/* The Threat Pulse */}
            {isDisrupted && (
              <div className="absolute inset-0 -m-4 rounded-full border border-tactical-red animate-ping opacity-75" />
            )}
            <span className={`text-xl transition-colors duration-1000 ${isDisrupted ? 'text-tactical-red drop-shadow-[0_0_12px_rgba(255,0,60,1)] scale-125' : 'text-slate-300 drop-shadow-[0_0_4px_rgba(203,213,225,0.8)]'}`}>
              ◎
            </span>
            <span className={`font-mono text-[10px] font-bold uppercase tracking-widest mt-1 px-1.5 py-0.5 rounded transition-colors duration-1000 ${isDisrupted ? 'text-tactical-red bg-tactical-red/10 border border-tactical-red/50' : 'text-slate-300 bg-panel/80'}`}>
              Hormuz
            </span>
          </div>
        </Marker>

        {/* PORT: Jamnagar */}
        <Marker longitude={70.0} latitude={22.4} anchor="center">
          <div className="flex flex-col items-center cursor-pointer group">
            <span className="text-tactical-green text-lg drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]">⬢</span>
            <span className="font-mono text-[9px] uppercase tracking-widest text-slate-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity bg-panel/80 px-1 rounded">Jamnagar Port</span>
          </div>
        </Marker>

      </Map>
      
      <Legend />
    </div>
  );
}
