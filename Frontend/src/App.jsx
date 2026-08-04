import { BrowserRouter, Routes, Route } from 'react-router'
import Layout from './components/Layout'
import { AuthProvider } from './auth/AuthContext'
import Home from './pages/Home'
import ChallengesList from './pages/ChallengesList'
import ChallengeDetail from './pages/ChallengeDetail'
import SubmissionHistory from './pages/SubmissionHistory'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import ApiTest from './pages/ApiTest'

function App(){
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home/>} />
            <Route path="/login" element={<Login/>} />
            <Route path="/register" element={<Register/>} />
            <Route path="/challenges" element={<ChallengesList/>} />
            <Route path="/challenges/:id" element={<ChallengeDetail/>} />
            <Route path="/submissions" element={<SubmissionHistory/>} />
            <Route path="/dashboard" element={<Dashboard/>} />
            <Route path="/api-test" element={<ApiTest/>} />
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
