import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function Navbar() {
  const { user, logout } = useAuth(); const navigate = useNavigate()
  return <header className="nav"><Link className="brand" to="/">WorkSphere <span>HRMS</span></Link><nav><Link to="/">Dashboard</Link>{user && <><Link to="/attendance">Attendance</Link><Link to="/leaves">Leaves</Link><Link to="/payroll">Payroll</Link>{['HR','ADMIN'].includes(user.role) && <Link to="/employees">Employees</Link>}{user.role === 'ADMIN' && <Link to="/admin">Admin</Link>}</>}</nav><div className="nav-user">{user ? <><span>{user.username} · {user.role}</span><button className="secondary" onClick={() => { logout(); navigate('/login') }}>Log out</button></> : <Link to="/login">Login</Link>}</div></header>
}
