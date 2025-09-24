import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'

const DIETS = ['vegan', 'vegetarian', 'keto', 'paleo', 'gluten-free']

export default function RecipeSearch({ onSelectRecipe, healthProfile }) {
  const [q, setQ] = useState('')
  const [diet, setDiet] = useState('')
  const [ingredients, setIngredients] = useState('')

  const { data, isFetching, isError, refetch } = useQuery({
    queryKey: ['recipes', q, diet, ingredients],
    queryFn: async () => {
      const res = await api.get('/api/recipes/search', { params: { q, diet, ingredients } })
      return res.data || []
    },
    enabled: false,
  })

  const applyProfile = () => {
    if (!healthProfile) return
    if (healthProfile.diet) setDiet(healthProfile.diet)
    if (healthProfile.allergens) setQ((prev) => prev)
  }

  const onSearch = () => {
    if (!q && !ingredients) return
    refetch()
  }

  return (
    <div className="bg-white rounded-xl shadow p-3 sm:p-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base sm:text-lg font-semibold">Find recipes</h2>
        <button onClick={applyProfile} className="text-xs sm:text-sm text-indigo-600 hover:underline">Apply health profile</button>
      </div>

      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="q">Search</label>
      <input
        id="q"
        placeholder="e.g. quick pasta, paneer curry, avocado toast"
        className="w-full border rounded px-3 py-3 text-sm sm:text-base"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />

      <div className="mt-3">
        <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="ingredients">Ingredients (optional)</label>
        <input
          id="ingredients"
          placeholder="comma separated, e.g. tomato, basil, olive oil"
          className="w-full border rounded px-3 py-3 text-sm sm:text-base"
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
        />
      </div>

      <div className="mt-3">
        <span className="block text-sm font-medium text-gray-700 mb-2">Diet (optional)</span>
        <div className="flex flex-wrap gap-2">
          {DIETS.map((d) => {
            const active = diet === d
            return (
              <button
                key={d}
                type="button"
                onClick={() => setDiet(active ? '' : d)}
                className={`px-3 py-2 rounded-full text-sm border ${active ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                aria-pressed={active}
              >
                {d}
              </button>
            )
          })}
        </div>
      </div>

      <div className="mt-4">
        <button
          onClick={onSearch}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded min-w-[96px]"
          disabled={isFetching}
        >
          {isFetching ? 'Searching…' : 'Search'}
        </button>
      </div>

      <div className="mt-4">
        {isError && (
          <div role="alert" className="text-sm text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2">
            Failed to fetch recipes.
          </div>
        )}

        {!isFetching && (data?.length ?? 0) === 0 && (
          <p className="text-sm text-gray-600">No results yet. Try a search above.</p>
        )}

        {isFetching && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="border rounded-lg p-3 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        )}

        {!isFetching && (data?.length ?? 0) > 0 && (
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4" role="list">
            {data.map((r, idx) => (
              <li key={r.sourceUrl || idx}>
                <button
                  onClick={() => onSelectRecipe(r)}
                  className="w-full text-left border rounded-lg p-3 hover:shadow focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <div className="font-medium">{r.title}</div>
                  {r.summary && <p className="text-sm text-gray-600 mt-1 line-clamp-3">{r.summary}</p>}
                  {r.sourceUrl && (
                    <a
                      href={r.sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-block text-indigo-600 text-sm mt-2 hover:underline"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Open source
                    </a>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
