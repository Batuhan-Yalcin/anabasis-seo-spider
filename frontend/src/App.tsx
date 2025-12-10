import { Routes, Route } from 'react-router-dom'
import { MainLayout } from '@/components/layout/MainLayout'
import { Dashboard } from '@/pages/Dashboard'
import { ProjectList } from '@/pages/ProjectList'
import { ScanDetail } from '@/pages/ScanDetail'
import { FileDiffViewer } from '@/pages/FileDiffViewer'
import { History } from '@/pages/History'
import { Settings } from '@/pages/Settings'
import { Monitoring } from '@/pages/Monitoring'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="scans/:jobId" element={<ScanDetail />} />
        <Route path="scans/:jobId/file/:fileId" element={<FileDiffViewer />} />
        <Route path="history" element={<History />} />
        <Route path="settings" element={<Settings />} />
        <Route path="monitoring" element={<Monitoring />} />
      </Route>
    </Routes>
  )
}

export default App

