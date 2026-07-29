import {
  LayoutDashboard,
  Upload,
  FolderOpen,
  History,
  SearchCheck,
  BookOpen,
  Settings,
  CircleHelp,
  BrainCircuit,
  LogOut,
} from "lucide-react";

import {
  NavLink,
  useNavigate,
} from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  // Logged-in user
  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const userName =
    user?.full_name || "Researcher";

  const firstLetter =
    userName.charAt(0).toUpperCase();

  // Logout
  const logout = () => {
    localStorage.clear();

    navigate("/");
  };

  // Active / Inactive Menu Style
  const menuClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
      isActive
        ? "bg-[var(--active-bg)] text-[var(--active-text)]"
        : "text-[var(--secondary-text)] hover:bg-[var(--card-hover)] hover:text-[var(--primary-text)]"
    }`;

  return (
    <aside
      className="
        w-72
        min-h-screen
        bg-[var(--sidebar-bg)]
        border-r
        border-[var(--border-color)]
        flex
        flex-col
        transition-colors
        duration-300
      "
    >

      {/* Logo */}

      <div className="px-6 py-7">

        <div className="flex items-center gap-3">

          {/* Logo Icon */}

          <div
            className="
              w-11
              h-11
              rounded-xl
              bg-[var(--button-bg)]
              flex
              items-center
              justify-center
              transition-colors
              duration-300
            "
          >

            <BrainCircuit
              size={25}
              className="text-[var(--button-text)]"
            />

          </div>

          {/* Logo Text */}

          <div>

            <h1
              className="
                text-xl
                font-semibold
                tracking-tight
                text-[var(--primary-text)]
              "
            >
              ResearchMind
            </h1>

            <p
              className="
                text-xs
                text-[var(--muted-text)]
                mt-1
              "
            >
              AI Research Platform
            </p>

          </div>

        </div>

      </div>

      {/* Divider */}

      <div
        className="
          mx-5
          border-t
          border-[var(--border-color)]
        "
      />

      {/* Navigation */}

      <nav className="flex-1 px-4 py-6 space-y-1">

        {/* Workspace Label */}

        <p
          className="
            px-4
            mb-3
            text-xs
            font-medium
            uppercase
            tracking-wider
            text-[var(--muted-text)]
          "
        >
          Workspace
        </p>

        <NavLink
          to="/dashboard"
          className={menuClass}
        >

          <LayoutDashboard size={19} />

          Dashboard

        </NavLink>

        <NavLink
          to="/upload"
          className={menuClass}
        >

          <Upload size={19} />

          Upload Papers

        </NavLink>

        <NavLink
          to="/papers"
          className={menuClass}
        >

          <FolderOpen size={19} />

          My Papers

        </NavLink>

        <NavLink
  to="/research-gap"
  className={menuClass}
>

  <SearchCheck size={19} />

  Research Gap

</NavLink>

        <NavLink
          to="/history"
          className={menuClass}
        >
<NavLink
  to="/literature-survey"
  className={menuClass}
>

  <BookOpen size={19} />

  Literature Survey

</NavLink>
          <History size={19} />

          Analysis History

        </NavLink>

        {/* Divider */}

        <div
          className="
            border-t
            border-[var(--border-color)]
            my-5
          "
        />

        {/* Account Label */}

        <p
          className="
            px-4
            mb-3
            text-xs
            font-medium
            uppercase
            tracking-wider
            text-[var(--muted-text)]
          "
        >
          Account
        </p>

        <NavLink
          to="/settings"
          className={menuClass}
        >

          <Settings size={19} />

          Settings

        </NavLink>

        <NavLink
          to="/help"
          className={menuClass}
        >

          <CircleHelp size={19} />

          Help & Support

        </NavLink>

      </nav>

      {/* User Card */}

      <div className="px-4 pb-4">

        <div
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-4
            transition-colors
            duration-300
          "
        >

          <div className="flex items-center gap-3">

            {/* Avatar */}

            <div
              className="
                w-11
                h-11
                rounded-full
                bg-[var(--button-bg)]
                text-[var(--button-text)]
                flex
                items-center
                justify-center
                font-semibold
                text-lg
              "
            >
              {firstLetter}
            </div>

            {/* User Information */}

            <div className="min-w-0 flex-1">

              <h3
                className="
                  text-sm
                  font-medium
                  text-[var(--primary-text)]
                  truncate
                "
              >
                {userName}
              </h3>

              <p
                className="
                  text-xs
                  text-[var(--muted-text)]
                  mt-1
                "
              >
                Researcher
              </p>

            </div>

          </div>

          {/* Logout */}

          <button
            onClick={logout}
            className="
              mt-4
              w-full
              flex
              items-center
              justify-center
              gap-2
              rounded-xl
              border
              border-[var(--border-color)]
              py-2.5
              text-sm
              font-medium
              text-[var(--secondary-text)]
              transition-all
              duration-200
              hover:bg-[var(--active-bg)]
              hover:text-[var(--active-text)]
            "
          >

            <LogOut size={17} />

            Logout

          </button>

        </div>

      </div>

      {/* Footer */}

      <div
        className="
          border-t
          border-[var(--border-color)]
          px-5
          py-5
          text-center
        "
      >

        <p
          className="
            text-xs
            font-medium
            text-[var(--secondary-text)]
          "
        >
          ResearchMind AI v1.0.0
        </p>

        <p
          className="
            text-xs
            text-[var(--muted-text)]
            mt-2
          "
        >
          Built with React + Flask
        </p>

        <p
          className="
            text-[11px]
            text-[var(--muted-text)]
            mt-2
          "
        >
          © 2026 All Rights Reserved
        </p>

      </div>

    </aside>
  );
}

export default Sidebar;