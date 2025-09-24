import { useState, useEffect } from 'react'
import Chatbot from './components/Chatbot.jsx'
import RecipeSearch from './components/RecipeSearch.jsx'
import HealthProfileCard from './components/HealthProfileCard.jsx'

export default function App() {
  const [sessionId, setSessionId] = useState(localStorage.getItem('session_id'))
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [healthProfile, setHealthProfile] = useState(null)

  useEffect(() => {
    async function ensureSession() {
      if (!sessionId) {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/sessions`, { method: 'POST' })
        const data = await res.json()
        localStorage.setItem('session_id', data.session_id)
        setSessionId(data.session_id)
      }
    }
    ensureSession()
  }, [sessionId])

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-white border-b">
        <div className="mx-auto max-w-6xl px-4 py-4">
          <h1 className="text-2xl font-semibold">Personalized Healthy Recipes</h1>
          <p className="text-sm text-gray-600 mt-1">Search recipes and chat with a nutrition-aware assistant</p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2">
          <HealthProfileCard onChange={setHealthProfile} />
          <RecipeSearch onSelectRecipe={setSelectedRecipe} healthProfile={healthProfile} />
        </section>
        <aside className="lg:col-span-1">
          {sessionId && (
            <Chatbot sessionId={sessionId} selectedRecipe={selectedRecipe} healthProfile={healthProfile} />
          )}
        </aside>
      </main>
    </div>
  )
}
