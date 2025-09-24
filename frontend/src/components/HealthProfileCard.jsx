import { useEffect, useState } from 'react'
import api from '../lib/api'

export default function HealthProfileCard({ onChange }) {
  const [diet, setDiet] = useState('')
  const [allergens, setAllergens] = useState('')
  const [goals, setGoals] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/api/profile')
        const p = res.data || {}
        setDiet(p.diet || '')
        setAllergens(p.allergens || '')
        setGoals(p.goals || '')
        onChange && onChange(p)
      } catch {
        // ignore for MVP
      }
    })()
  }, [])

  const save = async () => {
    setSaving(true)
    const body = { diet, allergens, goals }
    try {
      await api.post('/api/profile', body)
      onChange && onChange(body)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-3 sm:p-4 mb-4">
      <h2 className="text-base sm:text-lg font-semibold">Your Health Preferences</h2>
      <p className="text-xs sm:text-sm text-gray-600 mb-3">Personalize results using diet, allergens, and goals.</p>
      <div className="grid gap-2">
        <input className="border rounded px-3 py-3 text-sm sm:text-base" value={diet} onChange={(e)=>setDiet(e.target.value)} placeholder="Diet e.g. vegan, keto, heart-healthy" />
        <input className="border rounded px-3 py-3 text-sm sm:text-base" value={allergens} onChange={(e)=>setAllergens(e.target.value)} placeholder="Allergens e.g. peanuts, gluten" />
        <input className="border rounded px-3 py-3 text-sm sm:text-base" value={goals} onChange={(e)=>setGoals(e.target.value)} placeholder="Goals e.g. weight loss, low-sodium" />
      </div>
      <div className="mt-3">
        <button onClick={save} disabled={saving} className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded min-w-[96px]">
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
    </div>
  )
}
