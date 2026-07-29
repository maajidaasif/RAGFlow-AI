import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Upload,
  Library,
  History,
  Sparkles,
  FileText,
  BrainCircuit,
  FileOutput,
  Search,
  ArrowRight,
  Plus,
} from "lucide-react";

import MainLayout from "../layouts/MainLayout";

function Dashboard() {
  const navigate = useNavigate();

  // Logged-in user
  const user = JSON.parse(localStorage.getItem("user"));

  const userName = user?.full_name || "Researcher";

  // Greeting
  const hour = new Date().getHours();

  let greeting = "";

  if (hour < 12) {
    greeting = "Good Morning";
  } else if (hour < 17) {
    greeting = "Good Afternoon";
  } else {
    greeting = "Good Evening";
  }

  // Dashboard Data
  const [dashboard, setDashboard] = useState({
    total_papers: 0,
    total_analysis: 0,
    paper_comparisons: 0,
    research_gap: 0,
    literature_surveys: 0,
    domains: [],
    recent_activity: [],
  });

  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/dashboard"
      );

      if (!response.ok) {
        throw new Error("Failed to load dashboard");
      }

      const data = await response.json();

      setDashboard(data);
    } catch (error) {
      console.error("Dashboard Error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-[70vh]">
          <h2 className="text-xl font-semibold">
            Loading Dashboard...
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>

      {/* Welcome Section */}

      <section
        className="
          rounded-3xl
          border
          border-[var(--border-color)]
          bg-[var(--card-bg)]
          p-10
          transition-colors
          duration-300
        "
      >

        <div className="max-w-4xl">

          <p
            className="
              text-sm
              font-medium
              uppercase
              tracking-[0.2em]
              text-[var(--muted-text)]
            "
          >
            Research Workspace
          </p>

          <h1
            className="
              mt-4
              text-4xl
              font-semibold
              tracking-tight
              text-[var(--primary-text)]
              md:text-5xl
            "
          >
            {greeting}, {userName} 👋
          </h1>

          <p
            className="
              mt-5
              max-w-3xl
              text-lg
              leading-8
              text-[var(--secondary-text)]
            "
          >
            Upload research papers, organize your
            sources, generate literature surveys,
            discover research gaps, and work with
            your local AI research assistant.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">

            <button
              onClick={() =>
                navigate("/upload")
              }
              className="
                flex
                items-center
                gap-2
                rounded-xl
                bg-[var(--button-bg)]
                px-6
                py-3
                font-semibold
                text-[var(--button-text)]
                transition
                hover:opacity-80
              "
            >

              <Plus size={19} />

              New Research

            </button>

            <button
              onClick={() =>
                navigate("/papers")
              }
              className="
                flex
                items-center
                gap-2
                rounded-xl
                border
                border-[var(--border-color)]
                bg-transparent
                px-6
                py-3
                font-semibold
                text-[var(--primary-text)]
                transition
                hover:bg-[var(--card-hover)]
              "
            >

              <Library size={19} />

              My Papers

            </button>

          </div>

        </div>

      </section>

      {/* Statistics */}

<section className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">

  {/* Research Papers */}

  <div
    className="
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-6
      transition
      hover:bg-[var(--card-hover)]
    "
  >

    <div className="flex items-center justify-between">

      <p className="text-sm font-medium text-[var(--secondary-text)]">

        Research Papers

      </p>

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--card-hover)]">

        <FileText
          size={22}
          className="text-[var(--primary-text)]"
        />

      </div>

    </div>

    <h2 className="mt-6 text-4xl font-bold text-[var(--primary-text)]">

      {dashboard.total_papers}

    </h2>

    <p className="mt-2 text-sm text-[var(--muted-text)]">

      Uploaded papers

    </p>

  </div>

  {/* AI Analyses */}

  <div
    className="
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-6
      transition
      hover:bg-[var(--card-hover)]
    "
  >

    <div className="flex items-center justify-between">

      <p className="text-sm font-medium text-[var(--secondary-text)]">

        AI Analyses

      </p>

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--card-hover)]">

        <BrainCircuit
          size={22}
          className="text-[var(--primary-text)]"
        />

      </div>

    </div>

    <h2 className="mt-6 text-4xl font-bold text-[var(--primary-text)]">

      {dashboard.total_analysis}

    </h2>

    <p className="mt-2 text-sm text-[var(--muted-text)]">

      Completed analyses

    </p>

  </div>

  {/* Literature Surveys */}

  <div
    className="
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-6
      transition
      hover:bg-[var(--card-hover)]
    "
  >

    <div className="flex items-center justify-between">

      <p className="text-sm font-medium text-[var(--secondary-text)]">

        Literature Surveys

      </p>

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--card-hover)]">

        <FileOutput
          size={22}
          className="text-[var(--primary-text)]"
        />

      </div>

    </div>

    <h2 className="mt-6 text-4xl font-bold text-[var(--primary-text)]">

      {dashboard.literature_surveys}

    </h2>

    <p className="mt-2 text-sm text-[var(--muted-text)]">

      Generated surveys

    </p>

  </div>

  {/* Research Gaps */}

  <div
    className="
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-6
      transition
      hover:bg-[var(--card-hover)]
    "
  >

    <div className="flex items-center justify-between">

      <p className="text-sm font-medium text-[var(--secondary-text)]">

        Research Gaps

      </p>

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--card-hover)]">

        <Search
          size={22}
          className="text-[var(--primary-text)]"
        />

      </div>

    </div>

    <h2 className="mt-6 text-4xl font-bold text-[var(--primary-text)]">

      {dashboard.research_gap}

    </h2>

    <p className="mt-2 text-sm text-[var(--muted-text)]">

      Gap detection analyses

    </p>

  </div>

</section>

      {/* Start Research */}

      {dashboard.total_papers === 0 && (

        <section
          className="
            mt-8
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-8
          "
        >

          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">

            <div>

              <h2 className="text-2xl font-semibold text-[var(--primary-text)]">

                Start your research workspace

              </h2>

              <p className="mt-3 max-w-2xl leading-7 text-[var(--secondary-text)]">

                Upload your first research paper to
                begin organizing sources and preparing
                for AI-powered research analysis.

              </p>

            </div>

            <button
              onClick={() =>
                navigate("/upload")
              }
              className="
                flex
                shrink-0
                items-center
                justify-center
                gap-2
                rounded-xl
                bg-[var(--button-bg)]
                px-6
                py-3
                font-semibold
                text-[var(--button-text)]
                transition
                hover:opacity-80
              "
            >

              <Upload size={19} />

              Upload Paper

            </button>

          </div>

        </section>

      )}
    {/* Research Overview */}

<section className="mt-10">

  <div className="flex items-center justify-between">

    <div>

      <h2 className="text-2xl font-semibold text-[var(--primary-text)]">
        Research Overview
      </h2>

      <p className="mt-2 text-sm text-[var(--muted-text)]">
        Domains analyzed by ResearchMind AI.
      </p>

    </div>

  </div>

  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">

    {dashboard.domains.length === 0 ? (

      <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--card-bg)] p-8">

        <p className="text-[var(--muted-text)]">
          No research domains available.
        </p>

      </div>

    ) : (

      dashboard.domains.map((item, index) => (

        <div
          key={index}
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
            transition
            hover:bg-[var(--card-hover)]
          "
        >

          <BrainCircuit
            size={30}
            className="text-[var(--primary-text)]"
          />

          <h3 className="mt-4 text-lg font-semibold text-[var(--primary-text)]">
            {item.domain}
          </h3>

          <p className="mt-2 text-sm text-[var(--muted-text)]">
            {item.count} Analysis
          </p>

        </div>

      ))

    )}

  </div>

</section>
    

      {/* AI Research Modules */}

<section className="mt-12">

  <div>

    <h2 className="text-2xl font-semibold text-[var(--primary-text)]">

      AI Research Modules

    </h2>

    <p className="mt-2 text-sm text-[var(--muted-text)]">

      Access the core AI features available in ResearchMind AI.

    </p>

  </div>

  <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">

    {/* Upload Papers */}

    <button
      onClick={() => navigate("/upload")}
      className="
        group
        rounded-2xl
        border
        border-[var(--border-color)]
        bg-[var(--card-bg)]
        p-6
        text-left
        transition
        hover:bg-[var(--card-hover)]
      "
    >

      <Upload
        size={36}
        className="text-[var(--primary-text)]"
      />

      <h3 className="mt-5 text-lg font-semibold text-[var(--primary-text)]">

        Upload Papers

      </h3>

      <p className="mt-2 text-sm leading-6 text-[var(--muted-text)]">

        Upload one or more research papers for AI analysis.

      </p>

    </button>

    {/* Literature Survey */}

    <button
      onClick={() => navigate("/literature-survey")}
      className="
        group
        rounded-2xl
        border
        border-[var(--border-color)]
        bg-[var(--card-bg)]
        p-6
        text-left
        transition
        hover:bg-[var(--card-hover)]
      "
    >

      <FileOutput
        size={28}
        className="text-[var(--primary-text)]"
      />

      <h3 className="mt-5 text-lg font-semibold text-[var(--primary-text)]">

        Literature Survey

      </h3>

      <p className="mt-2 text-sm leading-6 text-[var(--muted-text)]">

        Generate a structured literature survey from uploaded papers.

      </p>

    </button>

    {/* Research Gap */}

    <button
      onClick={() => navigate("/research-gap")}
      className="
        group
        rounded-2xl
        border
        border-[var(--border-color)]
        bg-[var(--card-bg)]
        p-6
        text-left
        transition
        hover:bg-[var(--card-hover)]
      "
    >

      <Search
        size={28}
        className="text-[var(--primary-text)]"
      />

      <h3 className="mt-5 text-lg font-semibold text-[var(--primary-text)]">

        Research Gap Detection

      </h3>

      <p className="mt-2 text-sm leading-6 text-[var(--muted-text)]">

        Identify unexplored areas and future research opportunities.

      </p>

    </button>

    {/* Analysis History */}

    <button
      onClick={() => navigate("/history")}
      className="
        group
        rounded-2xl
        border
        border-[var(--border-color)]
        bg-[var(--card-bg)]
        p-6
        text-left
        transition
        hover:bg-[var(--card-hover)]
      "
    >

      <History
        size={28}
        className="text-[var(--primary-text)]"
      />

      <h3 className="mt-5 text-lg font-semibold text-[var(--primary-text)]">

        Analysis History

      </h3>

      <p className="mt-2 text-sm leading-6 text-[var(--muted-text)]">

        View previous literature surveys, comparisons and research gaps.

      </p>

    </button>

  </div>

</section>

      {/* Recent Activity */}

      <section className="mt-12">

        <div className="flex items-center justify-between">

          <div>

            <h2 className="text-2xl font-semibold text-[var(--primary-text)]">

              Recent Activity

            </h2>

            <p className="mt-2 text-sm text-[var(--muted-text)]">

              Your latest research activity will appear here.

            </p>

          </div>

          <button
            onClick={() =>
              navigate("/history")
            }
            className="
              flex
              items-center
              gap-2
              text-sm
              font-medium
              text-[var(--secondary-text)]
              transition
              hover:text-[var(--primary-text)]
            "
          >

            View History

            <ArrowRight size={16} />

          </button>

        </div>

   {dashboard.recent_activity.length === 0 ? (

  <div
    className="
      mt-6
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      px-8
      py-14
      text-center
    "
  >

    <History
      size={40}
      className="mx-auto text-[var(--secondary-text)]"
    />

    <h3 className="mt-6 text-xl font-semibold text-[var(--primary-text)]">

      No Recent Activity

    </h3>

    <p className="mt-3 text-[var(--muted-text)]">

      Your completed AI analyses will appear here.

    </p>

  </div>

) : (

  <div className="mt-6 space-y-4">

    {dashboard.recent_activity.map((activity) => (

      <div
        key={activity.id}
        className="
          rounded-2xl
          border
          border-[var(--border-color)]
          bg-[var(--card-bg)]
          p-5
        "
      >

        <h3 className="font-semibold text-[var(--primary-text)]">

          {activity.analysis_type}

        </h3>

        <p className="mt-1 text-sm text-[var(--secondary-text)]">

          Domain: {activity.domain}

        </p>

        <p className="mt-1 text-xs text-[var(--muted-text)]">

          {activity.created_at}

        </p>

      </div>

    ))}

  </div>

)}

        

      </section>

    </MainLayout>
  );
}

export default Dashboard;