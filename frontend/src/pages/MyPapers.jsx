import { useEffect, useState } from "react";

import {
  FolderOpen,
  Upload,
  Trash2,
  FileText,
  Search,
  Files,
  Calendar,
  Copy,
  Download,
  BrainCircuit,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

function MyPapers() {

  const navigate = useNavigate();

  // ==========================================
  // States
  // ==========================================

  const [papers, setPapers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const [comparisonResult, setComparisonResult] = useState("");
  const [comparisonDomain, setComparisonDomain] = useState("");

  const [loadingComparison, setLoadingComparison] =
    useState(false);

  const [savingAnalysis, setSavingAnalysis] =
    useState(false);

  const [downloadingReport, setDownloadingReport] =
    useState(false);

  // ==========================================
  // Load Papers
  // ==========================================

  const loadPapers = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/papers"
      );

      const data = await response.json();

      setPapers(Array.isArray(data) ? data : []);

    }

    catch (error) {

      console.log(error);

      setPapers([]);

    }

  };

  // ==========================================
  // Delete Paper
  // ==========================================

  const deletePaper = async (id) => {

    const confirmDelete = window.confirm(
      "Delete this paper?"
    );

    if (!confirmDelete) return;

    try {

      const response = await fetch(

        `http://127.0.0.1:5000/paper/${id}`,

        {
          method: "DELETE",
        }

      );

      const data = await response.json();

      alert(data.message);

      loadPapers();

    }

    catch (error) {

      console.log(error);

      alert("Unable to delete paper.");

    }

  };

  // ==========================================
  // Compare Papers
  // ==========================================

  const comparePapers = async () => {

    try {

      setLoadingComparison(true);

      const response = await fetch(
        "http://127.0.0.1:5000/compare-papers"
      );

      const data = await response.json();

      if (data.success) {

        setComparisonDomain(data.domain || "");

        setComparisonResult(
          data.comparison || ""
        );

      }

      else {

        alert(data.message);

      }

    }

    catch (error) {

      console.log(error);

      alert("Comparison failed.");

    }

    finally {

      setLoadingComparison(false);

    }

  };

  // ==========================================
  // Copy Result
  // ==========================================

  const copyResult = () => {

    navigator.clipboard.writeText(
      comparisonResult
    );

    alert("Copied successfully.");

  };

  // ==========================================
  // Save Analysis
  // ==========================================

  const saveAnalysis = async () => {

    try {

      setSavingAnalysis(true);

      alert(
        "Backend integration coming next."
      );

    }

    finally {

      setSavingAnalysis(false);

    }

  };

  // ==========================================
  // Download Report
  // ==========================================

  const downloadReport = async () => {

    try {

      setDownloadingReport(true);

      alert(
        "Backend integration coming next."
      );

    }

    finally {

      setDownloadingReport(false);

    }

  };

  // ==========================================
  // Initial Load
  // ==========================================

  useEffect(() => {

    loadPapers();

  }, []);

  // ==========================================
  // Search Filter
  // ==========================================

  const filteredPapers = papers.filter((paper) =>

    paper.filename
      .toLowerCase()
      .includes(searchTerm.toLowerCase())

  );

  return (

  <MainLayout>
    {/* ==========================================
    Header
========================================== */}

<div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-8">

  <div>

    <h1 className="text-4xl font-bold text-[var(--primary-text)]">
      My Papers
    </h1>

    <p className="mt-3 text-[var(--secondary-text)]">
      Manage your uploaded research papers and compare them using ResearchMind AI.
    </p>

  </div>

  <div className="flex flex-wrap gap-3">

    <button
      onClick={() => navigate("/upload")}
      className="
        flex
        items-center
        gap-2
        rounded-xl
        bg-[var(--button-bg)]
        text-[var(--button-text)]
        px-6
        py-3
        font-semibold
        transition
        hover:opacity-90
      "
    >

      <Upload size={18} />

      Upload Paper

    </button>

    <button
      onClick={comparePapers}
      disabled={loadingComparison}
      className="
        flex
        items-center
        gap-2
        rounded-xl
        bg-blue-600
        text-white
        px-6
        py-3
        font-semibold
        transition
        hover:bg-blue-700
        disabled:opacity-60
      "
    >

      <BrainCircuit size={18} />

      {loadingComparison
        ? "Comparing..."
        : "Compare Papers"}

    </button>

  </div>

</div>

{/* ==========================================
    Statistics
========================================== */}

<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

  <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--card-bg)] p-6">

    <Files
      size={32}
      className="text-[var(--primary-text)]"
    />

    <h2 className="mt-4 text-3xl font-bold text-[var(--primary-text)]">
      {papers.length}
    </h2>

    <p className="text-[var(--secondary-text)]">
      Total Papers
    </p>

  </div>

  <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--card-bg)] p-6">

    <Calendar
      size={32}
      className="text-[var(--primary-text)]"
    />

    <h2 className="mt-4 text-3xl font-bold text-[var(--primary-text)]">
      {papers.length > 0 ? "Available" : "None"}
    </h2>

    <p className="text-[var(--secondary-text)]">
      Research Collection
    </p>

  </div>

  <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--card-bg)] p-6">

    <div className="flex items-center gap-3">

      <Search
        size={22}
        className="text-[var(--secondary-text)]"
      />

      <input
        type="text"
        placeholder="Search papers..."
        value={searchTerm}
        onChange={(e) =>
          setSearchTerm(e.target.value)
        }
        className="
          w-full
          bg-transparent
          outline-none
          text-[var(--primary-text)]
          placeholder:text-[var(--secondary-text)]
        "
      />

    </div>

  </div>

</div>

{/* ==========================================
    Empty State
========================================== */}

{papers.length === 0 && (

  <div
    className="
      rounded-3xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-14
      text-center
    "
  >

    <div className="flex justify-center">

      <div
        className="
          h-24
          w-24
          rounded-full
          bg-[var(--card-hover)]
          flex
          items-center
          justify-center
        "
      >

        <FolderOpen
          size={50}
          className="text-[var(--primary-text)]"
        />

      </div>

    </div>

    <h2 className="mt-6 text-3xl font-bold text-[var(--primary-text)]">

      No Research Papers Found

    </h2>

    <p className="mt-3 text-[var(--secondary-text)]">

      Upload your first research paper to start AI analysis.

    </p>

    <button
      onClick={() => navigate("/upload")}
      className="
        mt-8
        inline-flex
        items-center
        gap-3
        rounded-xl
        bg-[var(--button-bg)]
        text-[var(--button-text)]
        px-8
        py-3
        font-semibold
        hover:opacity-90
      "
    >

      <Upload size={20} />

      Upload First Paper

    </button>

  </div>

)}
{/* ==========================================
    Paper Cards
========================================== */}

{papers.length > 0 && (

  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

    {filteredPapers.map((paper) => (

      <div
        key={paper.id}
        className="
          rounded-2xl
          border
          border-[var(--border-color)]
          bg-[var(--card-bg)]
          p-6
          transition-all
          duration-300
          hover:-translate-y-1
          hover:shadow-xl
          hover:bg-[var(--card-hover)]
        "
      >

        {/* Top */}

        <div className="flex items-center justify-between">

          <div
            className="
              h-14
              w-14
              rounded-xl
              bg-[var(--card-hover)]
              flex
              items-center
              justify-center
            "
          >

            <FileText
              size={30}
              className="text-[var(--primary-text)]"
            />

          </div>

          <span
            className="
              rounded-full
              bg-blue-600/20
              text-blue-400
              px-3
              py-1
              text-xs
              font-semibold
            "
          >

            PDF

          </span>

        </div>

        {/* File Name */}

        <h2
          className="
            mt-5
            text-lg
            font-semibold
            text-[var(--primary-text)]
            break-words
          "
        >

          {paper.filename}

        </h2>

        {/* Upload Date */}

        <p
          className="
            mt-2
            text-sm
            text-[var(--secondary-text)]
          "
        >

          Uploaded : {paper.uploaded_at}

        </p>

        {/* Buttons */}

        <div className="mt-6 flex gap-3">

          <a
            href={`http://127.0.0.1:5000/uploads/${encodeURIComponent(
              paper.filename
            )}`}
            target="_blank"
            rel="noopener noreferrer"
            className="
              flex-1
              rounded-lg
              bg-[var(--button-bg)]
              text-[var(--button-text)]
              text-center
              py-2.5
              font-medium
              transition
              hover:opacity-90
            "
          >

            View PDF

          </a>

          <button
            onClick={() => deletePaper(paper.id)}
            className="
              rounded-lg
              border
              border-red-500
              px-4
              text-red-500
              transition
              hover:bg-red-600
              hover:text-white
            "
          >

            <Trash2 size={18} />

          </button>

        </div>

      </div>

    ))}

  </div>

)}

{/* ==========================================
    AI Comparison Report
========================================== */}

{comparisonResult && (

  <div
    className="
      mt-10
      rounded-2xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      p-8
    "
  >

    <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

      <div>

        <h2 className="text-2xl font-bold text-[var(--primary-text)]">

          AI Comparison Report

        </h2>

        <p className="mt-2 text-[var(--secondary-text)]">

          Generated by ResearchMind AI

        </p>

      </div>

      <div className="flex flex-wrap gap-3">

        <button
          onClick={copyResult}
          className="
            flex
            items-center
            gap-2
            rounded-xl
            border
            border-[var(--border-color)]
            px-4
            py-2
            hover:bg-[var(--card-hover)]
          "
        >

          <Copy size={18} />

          Copy

        </button>

        <button
          onClick={saveAnalysis}
          disabled={savingAnalysis}
          className="
            rounded-xl
            bg-green-600
            px-5
            py-2
            font-medium
            text-white
            transition
            hover:bg-green-700
            disabled:opacity-60
          "
        >

          {savingAnalysis
            ? "Saving..."
            : "Save Analysis"}

        </button>

        <button
          onClick={downloadReport}
          disabled={downloadingReport}
          className="
            flex
            items-center
            gap-2
            rounded-xl
            bg-blue-600
            px-5
            py-2
            font-medium
            text-white
            transition
            hover:bg-blue-700
            disabled:opacity-60
          "
        >

          <Download size={18} />

          {downloadingReport
            ? "Downloading..."
            : "Download"}

        </button>

      </div>

    </div>

    {comparisonDomain && (

      <div
        className="
          mt-6
          inline-flex
          rounded-full
          bg-blue-600/15
          px-4
          py-2
          text-sm
          font-semibold
          text-blue-500
        "
      >

        Research Domain : {comparisonDomain}

      </div>

    )}

    <div
      className="
        mt-8
        rounded-xl
        bg-[var(--app-bg)]
        p-6
        whitespace-pre-wrap
        leading-8
        text-[var(--primary-text)]
      "
    >

      {comparisonResult}

    </div>

  </div>

)}

    </MainLayout>

  );

}

export default MyPapers;