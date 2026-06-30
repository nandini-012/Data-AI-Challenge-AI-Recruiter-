import { useState, useEffect, useCallback, useRef } from 'react'
import api from '../services/api'

export function useApi(url, options = {}) {
  const { immediate = true } = options
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const controllerRef = useRef(null)

  const fetchData = useCallback(async (fetchUrl, fetchParams) => {
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    controllerRef.current = new AbortController()

    setLoading(true)
    setError(null)
    try {
      const res = await api.get(fetchUrl || url, {
        params: fetchParams,
        signal: controllerRef.current.signal,
      })
      setData(res.data)
      return res.data
    } catch (err) {
      if (err.name !== 'CanceledError' && err.code !== 'ERR_CANCELED') {
        const message = err.response?.data?.detail || err.message || 'Something went wrong'
        setError(message)
      }
    } finally {
      setLoading(false)
    }
  }, [url])

  useEffect(() => {
    if (immediate && url) {
      fetchData(url)
    }
    return () => {
      if (controllerRef.current) {
        controllerRef.current.abort()
      }
    }
  }, [url, immediate])

  return { data, loading, error, refetch: fetchData, setData }
}
