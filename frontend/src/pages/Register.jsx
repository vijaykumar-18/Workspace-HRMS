import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function Register(){
 const [form,setForm]=useState({username:'',email:'',password:''});const [error,setError]=useState('');const {register}=useAuth();const navigate=useNavigate()
 async function submit(e){e.preventDefault();try{await register(form);alert('Registration successful. Please sign in.');navigate('/login')}catch(err){setError(err.response?.data?.detail||'Registration failed')}}
 return <main className="auth-wrap"><form className="panel auth-card" onSubmit={submit}><div className="eyebrow">JOIN WORKSPHERE</div><h1>Create account</h1>{error&&<div className="error">{error}</div>}{[['username','Username'],['email','Email'],['password','Password']].map(([key,label])=><label key={key}>{label}<input type={key==='password'?'password':'text'} value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})} required minLength={key==='password'?8:undefined}/></label>)}<button className="primary full">Register</button><p className="small muted">Already registered? <Link to="/login">Sign in</Link></p><p className="small muted">New registrations receive the EMPLOYEE role. An admin can assign HR/Admin roles.</p></form></main>
}
