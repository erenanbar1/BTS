import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <div className="text-center w-full max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-center space-x-8 mb-8">
          <a href="https://vite.dev" target="_blank" className="hover:opacity-80 transition-opacity">
            <img src={viteLogo} className="h-24 w-24" alt="Vite logo" />
          </a>
          <a href="https://react.dev" target="_blank" className="hover:opacity-80 transition-opacity">
            <img src={reactLogo} className="h-24 w-24 motion-safe:animate-spin-slow" alt="React logo" />
          </a>
        </div>
        
        <h1 className="text-4xl font-bold text-red-600 mb-8">
          Vite + React
        </h1>
        
        <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6">
          <button 
            onClick={() => setCount((count) => count + 1)}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors mb-4"
          >
            count is {count}
          </button>
          
          <p className="text-red-600">
            Edit <code className="bg-gray-100 rounded px-2 py-1">src/App.tsx</code> and save to test HMR
          </p>
        </div>
        
        <p className="text-red-600 mt-8">
          Click on the Vite and React logos to learn more
        </p>
      </div>
    </div>
  )
}

export default App
