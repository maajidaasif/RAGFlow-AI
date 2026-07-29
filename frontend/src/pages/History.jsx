import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

import {
  History,
  Upload,
  X,
} from "lucide-react";

import MainLayout from "../layouts/MainLayout";

function AnalysisHistory() {

  const navigate = useNavigate();

  const [history, setHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  useEffect(() => {

    fetch("http://127.0.0.1:5000/analysis-history")
      .then((res) => res.json())
      .then((data) => {
        setHistory(data);
      })
      .catch((err) => {
        console.log(err);
      });

  }, []);

const downloadPDF = () => {

  if (!selectedAnalysis) return;

  const doc = new jsPDF();

doc.setFontSize(22);
doc.text("ResearchMind AI", 55, 20);

doc.setFontSize(14);
doc.text("Research Analysis Report", 60, 28);

  autoTable(doc, {
    startY: 35,
    head: [["Field", "Value"]],
    body: [
      ["Analysis Name", selectedAnalysis.analysis_name],
      ["Analysis Type", selectedAnalysis.analysis_type],
      ["Domain", selectedAnalysis.domain || "Not Available"],
      ["Papers", selectedAnalysis.papers],
      [
        "Created",
        new Date(selectedAnalysis.created_at).toLocaleString(),
      ],
    ],
    theme: "grid",
  });

  let y = doc.lastAutoTable.finalY + 15;

 doc.setFontSize(18);
doc.text("Detailed AI Analysis", 20, y);

  y += 10;

  const pageHeight = doc.internal.pageSize.height;

  const lines = doc.splitTextToSize(
    selectedAnalysis.result,
    170
  );

  lines.forEach((line) => {

    if (y > pageHeight - 20) {
      doc.addPage();
      y = 20;
    }

    doc.text(line, 20, y);
    y += 7;

  });

 const totalPages = doc.getNumberOfPages();

for (let i = 1; i <= totalPages; i++) {

  doc.setPage(i);

  doc.setFontSize(10);

  doc.text(
    `Page ${i} of ${totalPages}`,
    170,
    290
  );

}

doc.save(
  `${selectedAnalysis.analysis_name.replace(/\s+/g, "_")}.pdf`
);

};
const deleteAnalysis = async (id) => {

  const confirmDelete = window.confirm(
    "Are you sure you want to delete this analysis?"
  );

  if (!confirmDelete) return;

  try {

    const response = await fetch(
      `http://127.0.0.1:5000/analysis-history/${id}`,
      {
        method: "DELETE",
      }
    );

    const data = await response.json();

    if (response.ok) {

      setHistory((prev) =>
        prev.filter((item) => item.id !== id)
      );

      if (
        selectedAnalysis &&
        selectedAnalysis.id === id
      ) {
        setSelectedAnalysis(null);
      }

      alert(data.message);

    } else {

      alert(data.message);

    }

  } catch (error) {

    console.error(error);
    alert("Failed to delete analysis.");

  }

};
const filteredHistory = history.filter((item) => {

  const search = searchTerm.toLowerCase();

  return (
    item.analysis_name.toLowerCase().includes(search) ||
    item.analysis_type.toLowerCase().includes(search) ||
    (item.domain || "").toLowerCase().includes(search) ||
    (item.papers || "").toLowerCase().includes(search)
  );

});

  return (
  <MainLayout>

  {/* Header */}

  <div className="flex items-center justify-between">

    <div>

      <h1 className="text-4xl font-bold text-[var(--primary-text)]">
        Analysis History
      </h1>

      <p className="mt-2 text-[var(--secondary-text)]">
        View all your previous AI research analyses.
      </p>

    </div>

    <button
      onClick={() => navigate("/upload")}
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
      <Upload size={18} />
      New Analysis
    </button>

  </div>

  <div className="mt-8">

  <input
    type="text"
    placeholder="Search by analysis name, domain or paper..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="
      w-full
      rounded-xl
      border
      border-[var(--border-color)]
      bg-[var(--card-bg)]
      px-5
      py-3
      text-[var(--primary-text)]
      outline-none
      focus:ring-2
      focus:ring-blue-500
    "
  />

</div>

  {/* Empty State */}

  {filteredHistory.length === 0 ? (

    <div
      className="
        mt-10
        rounded-3xl
        border
        border-[var(--border-color)]
        bg-[var(--card-bg)]
        p-16
        text-center
      "
    >

      <div
        className="
          mx-auto
          flex
          h-24
          w-24
          items-center
          justify-center
          rounded-full
          bg-[var(--button-bg)]
        "
      >

        <History
          size={48}
          className="text-[var(--button-text)]"
        />

      </div>

      <h2 className="mt-8 text-3xl font-bold">
        No Analysis History
      </h2>

      <p className="mt-4 text-[var(--secondary-text)]">
        Complete your first AI analysis.
      </p>

    </div>

  ) : (

    <div className="mt-10 space-y-6">

    {filteredHistory.map((item) => (

        <div
          key={item.id}
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
          "
        >

          <h2 className="text-2xl font-bold">
            {item.analysis_name}
          </h2>

          <p className="mt-2 text-sm text-[var(--secondary-text)]">
            {new Date(item.created_at).toLocaleString()}
          </p>

          <p className="mt-4 text-sm">
            <strong>Type:</strong> {item.analysis_type}
          </p>

          <p className="mt-2 text-sm">
            <strong>Domain:</strong>{" "}
            {item.domain || "Not Available"}
          </p>

          <p className="mt-2 text-sm">
            <strong>Papers:</strong>{" "}
            {item.papers || "Not Available"}
          </p>

          <p
            className="
              mt-5
              text-sm
              leading-7
              text-[var(--secondary-text)]
            "
          >
            {item.result.substring(0, 250)}...
          </p>

          <div className="mt-6 flex gap-3">

  <button
    onClick={() => setSelectedAnalysis(item)}
    className="
      rounded-xl
      bg-[var(--button-bg)]
      px-5
      py-2
      font-medium
      text-[var(--button-text)]
      transition
      hover:opacity-80
    "
  >
    View Full Analysis
  </button>

  <button
    onClick={() => deleteAnalysis(item.id)}
    className="
      rounded-xl
      bg-red-600
      px-5
      py-2
      font-medium
      text-white
      transition
      hover:bg-red-700
    "
  >
    Delete
  </button>

</div>

        </div>

      ))}

    </div>

  )}
<button
  onClick={() => deleteAnalysis(item.id)}
  className="
    mt-3
    ml-3
    rounded-xl
    bg-red-600
    px-5
    py-2
    font-medium
    text-white
    transition
    hover:bg-red-700
  "
>
  Delete
</button>


  {/* Modal */}
  {selectedAnalysis && (

  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

    <div
      className="
        w-[90%]
        max-w-5xl
        max-h-[85vh]
        overflow-hidden
        rounded-2xl
        bg-[var(--card-bg)]
        shadow-2xl
      "
    >

      <div
        className="
          flex
          items-center
          justify-between
          border-b
          border-[var(--border-color)]
          p-6
        "
      >

        <div>

          <h2 className="text-2xl font-bold">
            {selectedAnalysis.analysis_name}
          </h2>

          <p className="mt-1 text-sm text-[var(--secondary-text)]">
            {selectedAnalysis.analysis_type}
          </p>

          <p className="mt-2 text-sm">
            <strong>Domain:</strong>{" "}
            {selectedAnalysis.domain || "Not Available"}
          </p>

          <p className="mt-2 text-sm">
            <strong>Papers:</strong>{" "}
            {selectedAnalysis.papers}
          </p>

        </div>

        <div className="flex items-center gap-3">

          <button
            onClick={downloadPDF}
            className="
              rounded-lg
              bg-[var(--button-bg)]
              px-4
              py-2
              font-medium
              text-[var(--button-text)]
              transition
              hover:opacity-80
            "
          >
            Download PDF
          </button>

          <button
            onClick={() => setSelectedAnalysis(null)}
            className="
              rounded-lg
              p-2
              hover:bg-[var(--card-hover)]
            "
          >
            <X size={22} />
          </button>

        </div>

      </div>

      <div
        className="
          max-h-[65vh]
          overflow-y-auto
          whitespace-pre-wrap
          p-6
          leading-8
          text-[var(--primary-text)]
        "
      >
        {selectedAnalysis.result}
      </div>

    </div>

  </div>

)}

</MainLayout>

);

}

export default AnalysisHistory;