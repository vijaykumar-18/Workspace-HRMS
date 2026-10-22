import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function Login() {
 const [username,setUsername]=useState('admin'); const [password,setPassword]=useState('Admin123!'); const [error,setError]=useState(''); const {login,register}=useAuth(); const navigate=useNavigate()
 async function submit(e){e.preventDefault();setError('');try{const u=await login(username,password);navigate(u.role==='EMPLOYEE'?'/portal':'/')}catch(err){setError(err.response?.data?.detail||'Login failed')}}
 return <main className="auth-wrap"><form className="panel auth-card" onSubmit={submit}><div className="eyebrow">WORKSPHERE · PEOPLE OPERATIONS</div><h1>Welcome back</h1><p className="muted">Sign in to your HR workspace.</p>{error&&<div className="error">{error}</div>}<label>Username<input value={username} onChange={e=>setUsername(e.target.value)} required /></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required /></label><button className="primary full">Sign in</button><p className="muted small">New employee? <Link to="/register">Create an account</Link></p><div className="demo">Demo admin: <b>admin</b> / <b>Admin123!</b></div></form></main>
}
