import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import MessageSender from './components/MessageSender'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <MessageSender />
    </>
  )
}

export default App
