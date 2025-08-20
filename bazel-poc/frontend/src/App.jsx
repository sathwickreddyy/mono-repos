import { useState } from 'react'
import ItemsList from './components/ItemsList'
import './App.css'

function App() {
    const [activeService, setActiveService] = useState('java')

    return (
        <div className="App">
            <header className="App-header">
                <h1>Bazel Monorepo Demo</h1>
                <p>Multi-language services orchestrated by Bazel</p>

                <div className="service-selector">
                    <button
                        onClick={() => setActiveService('java')}
                        className={activeService === 'java' ? 'active' : ''}
                    >
                        Java Spring Service
                    </button>
                    <button
                        onClick={() => setActiveService('python')}
                        className={activeService === 'python' ? 'active' : ''}
                    >
                        Python FastAPI Service
                    </button>
                </div>

                <ItemsList service={activeService} />
            </header>
        </div>
    )
}

export default App
