import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import api from '../../services/api'

export default function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const setAccessToken = useAuthStore((s) => s.setAccessToken)
  const setUser = useAuthStore((s) => s.setUser)

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      setAccessToken(token)
      // Fetch user info
      api.get('/api/auth/me')
        .then((res) => {
          setUser(res.data)
          navigate('/', { replace: true })
        })
        .catch(() => {
          navigate('/login', { replace: true })
        })
    } else {
      navigate('/login', { replace: true })
    }
  }, [])

  return (
    <div className="login-page">
      <div className="login-card glass-card">
        <h1>🔄</h1>
        <p>กำลังเข้าสู่ระบบ...</p>
      </div>
    </div>
  )
}
