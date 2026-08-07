import Sidebar from "../components/Sidebar";
import DashboardNavbar from "../components/DashboardNavbar";

function MainLayout({ children }) {
  return (
    <div
      className="
        flex
        min-h-screen
        bg-[var(--app-bg)]
        transition-colors
        duration-300
      "
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Right Side */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Navbar */}
        <DashboardNavbar />

        {/* Page Content */}
        <main
          className="
            flex-1
            bg-[var(--app-bg)]
            p-8
            overflow-y-auto
            transition-colors
            duration-300
          "
        >
          {children}
        </main>

      </div>
    </div>
  );
}

export default MainLayout;