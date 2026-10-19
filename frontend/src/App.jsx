import { useEffect, useState } from 'react';
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import api from './api';
import './styles.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [register, setRegister] = useState(false);
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  async function submit(e) {
    e.preventDefault(); setError('');
    try {
      const { data } = await api.post(register ? '/auth/register' : '/auth/login',
        register ? { username, email, password } : { username, password });
      localStorage.setItem('worksphere_token', data.access_token);
      localStorage.setItem('worksphere_user', JSON.stringify(data.user));
      onLogin(data.user); navigate('/');
    } catch (err) { setError(err.response?.data?.detail || 'Unable to sign in. Check the backend and your details.'); }
  }
  return <div className="auth-wrap"><form className="panel auth" onSubmit={submit}>
    <div className="brand-mark">W</div><h1>{register ? 'Create your account' : 'Welcome back'}</h1><p className="muted">WorkSphere · People, made simpler</p>
    <label>Username<input required minLength="3" value={username} onChange={e=>setUsername(e.target.value)} /></label>
    {register && <label>Email<input required type="email" value={email} onChange={e=>setEmail(e.target.value)} /></label>}
    <label>Password<input required minLength="8" type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label>
    {error && <p className="error">{String(error)}</p>}<button className="primary wide">{register ? 'Create account' : 'Sign in'}</button>
    <button type="button" className="link-button" onClick={()=>setRegister(!register)}>{register ? 'Already registered? Sign in' : 'New here? Create employee account'}</button>
    {register && <p className="hint">Public registration creates an EMPLOYEE account. HR and ADMIN roles must be assigned by an administrator.</p>}
  </form></div>;
}

function App({}) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem('worksphere_user')); } catch { return null; } });
  const [section, setSection] = useState('overview');
  const [employees, setEmployees] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [payroll, setPayroll] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const canManage = ['HR','ADMIN'].includes(user?.role);
  async function load() {
    if (!user) return;
    setError('');
    try {
      const requests = await Promise.allSettled([
        api.get('/employees/'), api.get('/attendance/'), api.get('/leaves/'), api.get('/payroll/'), api.get('/notifications/'),
        canManage ? api.get('/dashboard/summary') : Promise.resolve({data:null})
      ]);
      const setters = [setEmployees,setAttendance,setLeaves,setPayroll,setNotifications,setSummary];
      requests.forEach((r,i)=> { if (r.status==='fulfilled') setters[i](r.value.data); });
      const failed = requests.find((r,i)=>r.status==='rejected' && i<5);
      if (failed) setError(failed.reason.response?.data?.detail || 'Some information could not be loaded.');
    } catch { setError('Unable to load data.'); }
  }
  useEffect(()=>{ load(); }, [user, section]);
  function logout() { localStorage.removeItem('worksphere_token'); localStorage.removeItem('worksphere_user'); setUser(null); }
  if (!user) return <Routes><Route path="*" element={<Login onLogin={setUser}/>} /></Routes>;
  const nav = [
    ['overview','Overview'], ['employees','Employees'], ['attendance','Attendance'], ['leaves','Leaves'], ['payroll','Payroll'], ['notifications','Notifications']
  ];
  return <div className="layout">
    <aside className="sidebar"><div className="brand"><span className="brand-mark small">W</span><div><b>WorkSphere</b><small>HR MANAGEMENT</small></div></div>
      <p className="nav-label">WORKSPACE</p>{nav.map(([key,label])=><button key={key} className={'nav-item '+(section===key?'selected':'')} onClick={()=>setSection(key)}>{label}{key==='notifications' && notifications.some(n=>!n.is_read) ? <span className="dot"/> : null}</button>)}
      <div className="sidebar-bottom"><div className="avatar">{user.username?.[0]?.toUpperCase()}</div><div className="user-meta"><b>{user.username}</b><small>{user.role}</small></div><button className="logout" onClick={logout}>↗</button></div>
    </aside>
    <main className="main"><header className="topbar"><div><span className="muted">Workspace / </span><b>{nav.find(n=>n[0]===section)?.[1]}</b></div><button className="secondary" onClick={load}>↻ Refresh</button></header>
      <div className="content"><div className="welcome"><div><p className="eyebrow">PEOPLE OPERATIONS</p><h1>{section==='overview'?'Good to see you, '+user.username:nav.find(n=>n[0]===section)?.[1]}</h1><p className="muted">Your team's workday, all in one place.</p></div><span className="role-pill">{user.role}</span></div>
      {error && <div className="alert">{error}</div>}
      {section==='overview' && <><div className="kpis">{(canManage ? [['Total employees',summary?.total_employees ?? employees.length,'People in the directory'],['Active employees',summary?.active_employees ?? '—','Currently active'],['Pending leaves',summary?.leave_summary?.PENDING ?? leaves.filter(l=>l.status==='PENDING').length,'Awaiting review'],['Payroll total',summary ? '₹'+Number(summary.total_payroll_amount).toLocaleString('en-IN') : '—','All generated payroll']] : [['My attendance',attendance.length,'Attendance records'],['My leave requests',leaves.length,'Requests submitted'],['Payslips',payroll.length,'Payroll records'],['Notifications',notifications.filter(n=>!n.is_read).length,'Unread updates']]).map(([title,value,sub])=><div className="panel kpi" key={title}><p>{title}</p><strong>{value}</strong><small>{sub}</small></div>)}</div><div className="panel section-panel"><div className="section-heading"><div><h2>Quick actions</h2><p className="muted">Common tasks in your workspace</p></div></div><div className="quick-actions"><button onClick={()=>setSection('attendance')}>＋ Check attendance</button><button onClick={()=>setSection('leaves')}>＋ Apply for leave</button>{canManage&&<button onClick={()=>setSection('employees')}>＋ Manage employees</button>}</div></div></>}
      {section==='employees' && <Employees employees={employees} reload={load} canManage={canManage}/>}
      {section==='attendance' && <Attendance employees={employees} records={attendance} reload={load} user={user}/>}
      {section==='leaves' && <Leaves employees={employees} records={leaves} reload={load} user={user} canManage={canManage}/>}
      {section==='payroll' && <Payroll employees={employees} records={payroll} reload={load} canManage={canManage}/>}
      {section==='notifications' && <Notifications records={notifications} reload={load}/>}
      </div>
    </main>
  </div>;
}

function Table({headers, rows}) {
  return <div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row,i)=><tr key={row.id ?? i}>{row.cells.map((cell,j)=><td key={j}>{cell}</td>)}</tr>) : <tr><td colSpan={headers.length} className="empty">No records found yet.</td></tr>}</tbody></table></div>;
}
function Employees({employees,reload,canManage}) {
  const [search,setSearch]=useState(''); const [form,setForm]=useState({full_name:'',designation:'',department:'',joining_date:new Date().toISOString().slice(0,10),salary:'',status:'ACTIVE',user_id:''}); const [editing,setEditing]=useState(null); const [error,setError]=useState('');
  async function submit(e){e.preventDefault();setError('');try{const data={...form,salary:Number(form.salary),user_id:form.user_id?Number(form.user_id):null}; if(editing) await api.put(`/employees/${editing}`,data); else await api.post('/employees/',data);setEditing(null);setForm({full_name:'',designation:'',department:'',joining_date:new Date().toISOString().slice(0,10),salary:'',status:'ACTIVE',user_id:''});await reload();}catch(err){setError(err.response?.data?.detail||'Could not save employee.');}}
  const filtered=employees.filter(e=>(e.full_name+' '+e.department+' '+e.designation).toLowerCase().includes(search.toLowerCase()));
  return <div className="panel section-panel"><div className="section-heading"><div><h2>Employee directory</h2><p className="muted">{employees.length} employee records</p></div><input className="search" placeholder="Search employees…" value={search} onChange={e=>setSearch(e.target.value)}/></div>
  {canManage&&<form className="inline-form" onSubmit={submit}><h3>{editing?'Edit employee':'Add employee'}</h3><div className="form-grid"><label>Full name<input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label><label>Designation<input required value={form.designation} onChange={e=>setForm({...form,designation:e.target.value})}/></label><label>Department<input required value={form.department} onChange={e=>setForm({...form,department:e.target.value})}/></label><label>Joining date<input required type="date" value={form.joining_date} onChange={e=>setForm({...form,joining_date:e.target.value})}/></label><label>Salary (₹)<input required min="0" type="number" value={form.salary} onChange={e=>setForm({...form,salary:e.target.value})}/></label><label>Linked user ID (optional)<input type="number" min="1" value={form.user_id} onChange={e=>setForm({...form,user_id:e.target.value})}/></label></div>{error&&<p className="error">{error}</p>}<div className="form-actions"><button className="primary">{editing?'Save changes':'Add employee'}</button>{editing&&<button type="button" className="secondary" onClick={()=>setEditing(null)}>Cancel</button>}</div></form>}
  <Table headers={['Employee','Department','Designation','Joining date','Salary','Status',...(canManage?['Actions']:[])]} rows={filtered.map(e=>({id:e.id,cells:[<b>{e.full_name}</b>,e.department,e.designation,e.joining_date,'₹'+Number(e.salary).toLocaleString('en-IN'),<span className={'status '+e.status.toLowerCase()}>{e.status}</span>,...(canManage?[<button className="table-action" onClick={()=>{setEditing(e.id);setForm({...e,salary:String(e.salary),user_id:e.user_id||''});window.scrollTo({top:0,behavior:'smooth'});}}>Edit</button>]:[])]}))}/></div>;
}
function Attendance({employees,records,reload,user}) {
  const [employeeId,setEmployeeId]=useState(''); const [error,setError]=useState('');
  const own=employees.find(e=>e.user_id===user.id); const target=user.role==='EMPLOYEE' ? own?.id : Number(employeeId);
  async function checkIn(){try{setError('');await api.post('/attendance/check-in',{employee_id:target});await reload();}catch(e){setError(e.response?.data?.detail||'Check-in failed');}}
  async function checkOut(id){try{setError('');await api.post(`/attendance/check-out/${id}`);await reload();}catch(e){setError(e.response?.data?.detail||'Check-out failed');}}
  return <div className="panel section-panel"><div className="section-heading"><div><h2>Attendance tracker</h2><p className="muted">Check in, check out, and review work hours.</p></div></div>{user.role!=='EMPLOYEE'&&<label className="compact-label">Employee<select value={employeeId} onChange={e=>setEmployeeId(e.target.value)}><option value="">Select employee</option>{employees.map(e=><option value={e.id} key={e.id}>{e.full_name} (#{e.id})</option>)}</select></label>}{error&&<p className="error">{error}</p>}<button className="primary" disabled={!target} onClick={checkIn}>Check in today</button><Table headers={['Date','Employee ID','Check in','Check out','Status','Action']} rows={records.map(r=>({id:r.id,cells:[r.date,'#'+r.employee_id,r.check_in?new Date(r.check_in).toLocaleTimeString():'—',r.check_out?new Date(r.check_out).toLocaleTimeString():'—',<span className={'status '+r.status.toLowerCase()}>{r.status}</span>,r.check_in&&!r.check_out?<button className="table-action" onClick={()=>checkOut(r.id)}>Check out</button>:'—']}))}/><p className="hint">Working hours are calculated from the check-in and check-out timestamps. HR/Admin can record an absent day through the API docs.</p></div>;
}
function Leaves({employees,records,reload,user,canManage}) {
  const own=employees.find(e=>e.user_id===user.id);
  const [form,setForm]=useState({employee_id:'',leave_type:'CASUAL',start_date:'',end_date:'',reason:''});const [error,setError]=useState('');
  async function submit(e){e.preventDefault();try{setError('');await api.post('/leaves/',{...form,employee_id:user.role==='EMPLOYEE'?own?.id:Number(form.employee_id)});setForm({...form,start_date:'',end_date:'',reason:''});await reload();}catch(err){setError(err.response?.data?.detail||'Could not submit leave request. Make sure your account is linked to an employee profile.');}}
  async function decide(id,decision){try{await api.patch(`/leaves/${id}/decision`,null,{params:{decision}});await reload();}catch(e){setError(e.response?.data?.detail||'Unable to update leave status');}}
  return <div className="panel section-panel"><div className="section-heading"><div><h2>Leave management</h2><p className="muted">Submit requests and track decisions.</p></div></div><form className="inline-form" onSubmit={submit}><h3>Apply for leave</h3><div className="form-grid">{canManage&&<label>Employee<select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Select employee</option>{employees.map(e=><option key={e.id} value={e.id}>{e.full_name}</option>)}</select></label>}<label>Leave type<select value={form.leave_type} onChange={e=>setForm({...form,leave_type:e.target.value})}><option>CASUAL</option><option>SICK</option><option>PAID</option></select></label><label>Start date<input required type="date" value={form.start_date} onChange={e=>setForm({...form,start_date:e.target.value})}/></label><label>End date<input required type="date" min={form.start_date||undefined} value={form.end_date} onChange={e=>setForm({...form,end_date:e.target.value})}/></label><label className="span-two">Reason<textarea required minLength="3" value={form.reason} onChange={e=>setForm({...form,reason:e.target.value})}/></label></div>{error&&<p className="error">{error}</p>}<button className="primary">Submit request</button></form><Table headers={['Employee ID','Type','Dates','Reason','Status',...(canManage?['Review']:[])]} rows={records.map(r=>({id:r.id,cells:['#'+r.employee_id,r.leave_type,`${r.start_date} → ${r.end_date}`,r.reason,<span className={'status '+r.status.toLowerCase()}>{r.status}</span>,...(canManage?[r.status==='PENDING'?<><button className="table-action" onClick={()=>decide(r.id,'APPROVED')}>Approve</button> <button className="table-action danger-text" onClick={()=>decide(r.id,'REJECTED')}>Reject</button></>:'Reviewed']:[])]}))}/></div>;
}
function Payroll({employees,records,reload,canManage}) {
 const [form,setForm]=useState({employee_id:'',basic_salary:'',deductions:'0',bonus:'0',month:new Date().toISOString().slice(0,7)});const [error,setError]=useState('');
 async function submit(e){e.preventDefault();try{setError('');await api.post('/payroll/',{...form,employee_id:Number(form.employee_id),basic_salary:Number(form.basic_salary),deductions:Number(form.deductions),bonus:Number(form.bonus)});await reload();}catch(err){setError(err.response?.data?.detail||'Could not generate payroll');}}
 return <div className="panel section-panel"><div className="section-heading"><div><h2>Payroll</h2><p className="muted">Salary calculations and payroll history.</p></div></div>{canManage&&<form className="inline-form" onSubmit={submit}><h3>Generate payroll</h3><div className="form-grid"><label>Employee<select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Select employee</option>{employees.map(e=><option key={e.id} value={e.id}>{e.full_name}</option>)}</select></label><label>Month<input required type="month" value={form.month} onChange={e=>setForm({...form,month:e.target.value})}/></label><label>Basic salary<input required min="0" type="number" value={form.basic_salary} onChange={e=>setForm({...form,basic_salary:e.target.value})}/></label><label>Deductions<input min="0" type="number" value={form.deductions} onChange={e=>setForm({...form,deductions:e.target.value})}/></label><label>Bonus<input min="0" type="number" value={form.bonus} onChange={e=>setForm({...form,bonus:e.target.value})}/></label></div>{error&&<p className="error">{error}</p>}<button className="primary">Generate payroll</button></form>}<Table headers={['Employee ID','Month','Basic salary','Deductions','Bonus','Net salary']} rows={records.map(r=>({id:r.id,cells:['#'+r.employee_id,r.month,'₹'+Number(r.basic_salary).toLocaleString('en-IN'),'₹'+Number(r.deductions).toLocaleString('en-IN'),'₹'+Number(r.bonus).toLocaleString('en-IN'),<b>₹{Number(r.net_salary).toLocaleString('en-IN')}</b>]}))}/></div>;
}
function Notifications({records,reload}) {
 async function markRead(id){await api.patch(`/notifications/${id}/read`);await reload();}
 return <div className="panel section-panel"><div className="section-heading"><div><h2>Notifications</h2><p className="muted">Updates about leave and payroll activity.</p></div></div><div className="notification-list">{records.length?records.map(n=><div className={'notification '+(!n.is_read?'unread':'')} key={n.id}><div><b>{n.title}</b><p>{n.message}</p><small>{new Date(n.created_at).toLocaleString()}</small></div>{!n.is_read&&<button className="table-action" onClick={()=>markRead(n.id)}>Mark read</button>}</div>):<p className="empty">You're all caught up.</p>}</div></div>;
}
export default App;
