import React, { useState } from 'react';
import { Shield, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('officer1');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      if (username === 'admin') {
        navigate('/audit');
      } else {
        navigate('/dashboard');
      }
    }, 1000);
  };

  return (
    <div className="login-page">
      <div className="login-header">
        <Shield size={32} className="login-logo-icon" />
        <h1 className="login-title">FaceForge</h1>
        <p className="login-subtitle">FORENSIC SUITE</p>
      </div>

      <div className="login-card">
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <input 
              type="text" 
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="login-input" 
              required
            />
          </div>

          <div className="form-group password-group">
            <input 
              type={showPassword ? "text" : "password"} 
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input" 
              required
            />
            <button 
              type="button" 
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          <button type="submit" className="btn-primary login-btn" disabled={isLoading}>
            {isLoading ? <Loader2 size={16} className="spinner" /> : "Sign In"}
          </button>
        </form>

        <div className="demo-credentials mono">
          <p>officer1 / password123</p>
          <p>admin / admin123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
