import { useState, useEffect } from 'react'

const ItemsList = ({ service }) => {
    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const serviceEndpoints = {
        java: 'http://localhost:8080/api/items',
        python: 'http://localhost:8000/api/items'
    }

    useEffect(() => {
        const fetchItems = async () => {
            try {
                setLoading(true)
                setError(null)

                const response = await fetch(serviceEndpoints[service])
                if (!response.ok) {
                    throw new Error(`Failed to fetch from ${service} service`)
                }

                const data = await response.json()
                setItems(data)
            } catch (err) {
                setError(err.message)
                console.error('Error fetching items:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchItems()
    }, [service])

    if (loading) return <div>Loading items from {service} service...</div>
    if (error) return <div>Error: {error}</div>

    return (
        <div className="items-container">
            <h2>Items from {service.charAt(0).toUpperCase() + service.slice(1)} Service</h2>
            <div className="items-grid">
                {items.map(item => (
                    <div key={item.id} className="item-card">
                        <h3>{item.name}</h3>
                        <p>{item.description}</p>
                        <small>Service: {service}</small>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default ItemsList
