import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { BrainCircuit, Mail, Lock } from "lucide-react";
import { loginUser } from "../services/authService";
import toast from "react-hot-toast";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const response = await loginUser({
        email,
        password,
      });

      // Save Complete User Object
      localStorage.setItem(
        "user",
        JSON.stringify(response.data.user)
      );

      // (Temporary compatibility with existing Dashboard/Navbar)
      localStorage.setItem(
        "userName",
        response.data.user.full_name
      );

      toast.success("Welcome back, " + response.data.user.full_name + " 🎉");

      navigate("/dashboard");

    } catch (error) {

      toast.error(
        error.response?.data?.message || "Login Failed"
      );

    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center p-6">

      <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl p-8">

        {/* Logo */}

        <div className="flex justify-center mb-6">

          <div className="bg-indigo-600 p-4 rounded-full">

            <BrainCircuit
              size={40}
              className="text-white"
            />

          </div>

        </div>

        {/* Heading */}

        <h1 className="text-3xl font-bold text-center text-white">
          ResearchMind AI
        </h1>

        <p className="text-center text-gray-300 mt-2 mb-8">
          AI-Powered Research Assistant
        </p>

        {/* Form */}

        <div className="space-y-5">

          {/* Email */}

          <div>

            <label className="text-gray-300 text-sm">
              Email
            </label>

            <div className="flex items-center bg-white/10 rounded-xl px-4 mt-2">

              <Mail
                className="text-gray-400"
                size={20}
              />

              <input
                type="email"
                placeholder="Enter your email"
                autoComplete="off"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-transparent outline-none text-white px-3 py-4"
              />

            </div>

          </div>

          {/* Password */}

          <div>

            <label className="text-gray-300 text-sm">
              Password
            </label>

            <div className="flex items-center bg-white/10 rounded-xl px-4 mt-2">

              <Lock
                className="text-gray-400"
                size={20}
              />

              <input
                type="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-transparent outline-none text-white px-3 py-4"
              />

            </div>

          </div>

          {/* Login Button */}

          <button
            onClick={handleLogin}
            className="w-full bg-indigo-600 hover:bg-indigo-700 transition duration-300 rounded-xl py-4 text-white font-semibold"
          >
            Sign In
          </button>

          {/* Register */}

          <p className="text-center text-gray-300">

            Don't have an account?

            <Link
              to="/register"
              className="text-indigo-400 ml-2 hover:underline"
            >
              Register
            </Link>

          </p>

        </div>

      </div>

    </div>
  );
}

export default Login;