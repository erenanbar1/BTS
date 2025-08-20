import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import NavBar from './components/SideBar'
import SendMessage from './components/SendMessage'
function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex min-h-screen bg-gray-100">
      <NavBar />
      <SendMessage/>
    </div>
  )
}

export default App
