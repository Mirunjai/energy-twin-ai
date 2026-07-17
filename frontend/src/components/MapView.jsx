import Map, { NavigationControl } from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'

const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN || import.meta.env.MAPBOX_TOKEN || ''

function MapView() {
  return (
    <div className="h-[460px] w-full">
      <Map
        mapboxAccessToken={mapboxToken}
        initialViewState={{ longitude: 72.8777, latitude: 19.076, zoom: 3.5 }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
      >
        <NavigationControl position="top-right" />
      </Map>
    </div>
  )
}

export default MapView
