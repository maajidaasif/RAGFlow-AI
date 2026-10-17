import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { BrainCircuit, User, Mail, Lock } from "lucide-react";
import { registerUser } from "../services/authService";
import toast from "react-hot-toast";

function Register() {

  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleRegister = async () => {

    if (!fullName || !email || !password || !confirmPassword) {
      toast.error("Please fill all fields");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters long.");
      return;
    }

    try {

      await registerUser({
        full_name: fullName,
        email,
        password,
      });

      toast.success("Registration Successful 🎉");

      setTimeout(() => {
        navigate("/");
      }, 1000);

    } catch (error) {

      toast.error(
        error.response?.data?.message ||
        "Registration Failed"
      );

    }

  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center p-6">

      <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl p-8">

        <div className="flex justify-center mb-6">
          <div className="bg-indigo-600 p-4 rounded-full">
            <BrainCircuit
              size={40}
              className="text-white"
            />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-center text-white">
          Create Account
        </h1>

        <p className="text-center text-gray-300 mt-2 mb-8">
          Join ResearchMind AI
        </p>

        <div className="space-y-5">

          <div className="flex items-center bg-white/10 rounded-xl px-4">

            <User
              className="text-gray-400"
              size={20}
            />

            <input
              type="text"
              placeholder="Full Name"
              autoComplete="off"
              value={fullName}
              onChange={(e) =>
                setFullName(e.target.value)
              }
              className="w-full bg-transparent outline-none text-white px-3 py-4"
            />

          </div>

          <div className="flex items-center bg-white/10 rounded-xl px-4">

            <Mail
              className="text-gray-400"
              size={20}
            />

            <input
              type="email"
              placeholder="Email"
              autoComplete="off"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              className="w-full bg-transparent outline-none text-white px-3 py-4"
            />

          </div>

          <div className="flex items-center bg-white/10 rounded-xl px-4">

            <Lock
              className="text-gray-400"
              size={20}
            />

            <input
              type="password"
              placeholder="Password"
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              className="w-full bg-transparent outline-none text-white px-3 py-4"
            />

          </div>

          <div className="flex items-center bg-white/10 rounded-xl px-4">

            <Lock
              className="text-gray-400"
              size={20}
            />

            <input
              type="password"
              placeholder="Confirm Password"
              minLength={8}
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              className="w-full bg-transparent outline-none text-white px-3 py-4"
            />

          </div>

          <button
            onClick={handleRegister}
            className="w-full bg-indigo-600 hover:bg-indigo-700 rounded-xl py-4 text-white font-semibold"
          >
            Create Account
          </button>

          <p className="text-center text-gray-300">
            Already have an account?

            <Link
              to="/"
              className="text-indigo-400 ml-2 hover:underline"
            >
              Login
            </Link>

          </p>

        </div>

      </div>

    </div>
  );
}

export default Register;