import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useUIStore } from '../../stores/uiStore'

export default function Layout() {
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
