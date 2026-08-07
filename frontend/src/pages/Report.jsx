import { useState } from "react";

import MainLayout from "../layouts/MainLayout";

import {
  FileText,
  Download,
  Copy,
  Sparkles,
  Cpu,
  CheckCircle,
  File,
} from "lucide-react";

import ReactMarkdown from "react-markdown";

import jsPDF from "jspdf";

import {
  Document,
  Packer,
  Paragraph,
} from "docx";

import { saveAs } from "file-saver";

import axios from "axios";

function Report() {

  // -----------------------------
  // States
  // -----------------------------

  const [loading, setLoading] = useState(false);

  const [report, setReport] = useState("");

  const [generated, setGenerated] = useState(false);

  // -----------------------------
  // Generate Report
  // -----------------------------

  const generateReport = async () => {

    try {

      setLoading(true);

      setGenerated(false);

      const response = await axios.post(
        "http://127.0.0.1:5000/generate-report"
      );

      setReport(response.data.report);

      setGenerated(true);

    }

    catch (error) {

      console.error(error);

      alert("Unable to generate report.");

    }

    finally {

      setLoading(false);

    }

  };

  // -----------------------------
  // Download PDF
  // -----------------------------

  const downloadPDF = () => {

    if (!report) {

      alert("Please generate a report first.");

      return;

    }

    const pdf = new jsPDF();

    pdf.setFont("helvetica", "bold");

    pdf.setFontSize(20);

    pdf.text("ResearchMind AI", 20, 20);

    pdf.setFontSize(14);

    pdf.text("Research Report", 20, 30);

    pdf.setFont("helvetica", "normal");

    pdf.setFontSize(10);

    pdf.text(
      `Generated On : ${new Date().toLocaleString()}`,
      20,
      38
    );

    pdf.line(20, 42, 190, 42);

    pdf.setFontSize(12);

    const cleanReport = report
      .replace(/```markdown/g, "")
      .replace(/```/g, "");

    const lines = pdf.splitTextToSize(
      cleanReport,
      170
    );

    let y = 52;

    lines.forEach((line) => {

      if (y > 280) {

        pdf.addPage();

        y = 20;

      }

      pdf.text(line, 20, y);

      y += 7;

    });

    pdf.save("Research_Report.pdf");

  };

  // -----------------------------
  // Download Word
  // -----------------------------

  const downloadWord = async () => {

    if (!report) {

      alert("Please generate a report first.");

      return;

    }

    const cleanReport = report
      .replace(/```markdown/g, "")
      .replace(/```/g, "");

    const paragraphs = cleanReport

      .split("\n")

      .filter(line => line.trim() !== "")

      .map(

        line =>

          new Paragraph({

            text: line,

          })

      );

    const document = new Document({

      sections: [

        {

          children: paragraphs,

        },

      ],

    });

    const blob = await Packer.toBlob(document);

    saveAs(blob, "Research_Report.docx");

  };

  // -----------------------------
  // Copy Report
  // -----------------------------

  const copyReport = async () => {

    if (!report) return;

    await navigator.clipboard.writeText(report);

    alert("Report copied successfully.");

  };

  return (

    <MainLayout>

            {/* ========================================= */}
      {/* Header */}
      {/* ========================================= */}

      <div className="flex items-center gap-5">

        <div
          className="
            rounded-2xl
            bg-[var(--button-bg)]
            p-4
          "
        >

          <FileText
            size={38}
            className="text-[var(--button-text)]"
          />

        </div>

        <div>

          <h1
            className="
              text-4xl
              font-bold
              text-[var(--primary-text)]
            "
          >

            Research Report Generator

          </h1>

          <p
            className="
              mt-2
              text-[var(--secondary-text)]
            "
          >

            Generate a complete AI-powered research report
            by combining Literature Survey, Paper Comparison
            and Research Gap Analysis.

          </p>

        </div>

      </div>

      {/* ========================================= */}
      {/* Generate Button */}
      {/* ========================================= */}

      <div className="mt-10">

        <button
          onClick={generateReport}
          disabled={loading}
          className="
            flex
            items-center
            gap-3
            rounded-xl
            bg-[var(--button-bg)]
            px-7
            py-3
            font-semibold
            text-[var(--button-text)]
            transition
            hover:opacity-90
            disabled:opacity-50
          "
        >

          <Sparkles size={18} />

          {

            loading

              ?

              "Generating Research Report..."

              :

              "Generate Research Report"

          }

        </button>

      </div>

      {/* ========================================= */}
      {/* AI Status */}
      {/* ========================================= */}

      <div
        className="
          mt-10
          grid
          grid-cols-1
          md:grid-cols-2
          xl:grid-cols-4
          gap-5
        "
      >

        {/* Literature Survey */}

        <div
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
          "
        >

          <CheckCircle
            size={30}
            className="text-green-500"
          />

          <h3
            className="
              mt-5
              text-lg
              font-semibold
              text-[var(--primary-text)]
            "
          >

            Literature Survey

          </h3>

          <p
            className="
              mt-2
              text-sm
              text-[var(--muted-text)]
            "
          >

            Ready

          </p>

        </div>

        {/* Paper Comparison */}

        <div
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
          "
        >

          <CheckCircle
            size={30}
            className="text-green-500"
          />

          <h3
            className="
              mt-5
              text-lg
              font-semibold
              text-[var(--primary-text)]
            "
          >

            Paper Comparison

          </h3>

          <p
            className="
              mt-2
              text-sm
              text-[var(--muted-text)]
            "
          >

            Ready

          </p>

        </div>

        {/* Research Gap */}

        <div
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
          "
        >

          <CheckCircle
            size={30}
            className="text-green-500"
          />

          <h3
            className="
              mt-5
              text-lg
              font-semibold
              text-[var(--primary-text)]
            "
          >

            Research Gap

          </h3>

          <p
            className="
              mt-2
              text-sm
              text-[var(--muted-text)]
            "
          >

            Ready

          </p>

        </div>

        {/* AI Engine */}

        <div
          className="
            rounded-2xl
            border
            border-[var(--border-color)]
            bg-[var(--card-bg)]
            p-6
          "
        >

          <Cpu
            size={30}
            className="text-blue-500"
          />

          <h3
            className="
              mt-5
              text-lg
              font-semibold
              text-[var(--primary-text)]
            "
          >

            AI Report Engine

          </h3>

          <p
            className="
              mt-2
              text-sm
              text-[var(--muted-text)]
            "
          >

            Local Qwen 2.5 • CPU

          </p>

        </div>

      </div>

      {/* ========================================= */}
      {/* Loading */}
      {/* ========================================= */}

      {

        loading && (

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

            <h2
              className="
                text-2xl
                font-bold
                text-[var(--primary-text)]
              "
            >

              AI is Generating Your Research Report...

            </h2>

            <p
              className="
                mt-3
                text-[var(--secondary-text)]
              "
            >

              ResearchMind AI is reading the Literature
              Survey, Paper Comparison and Research Gap,
              then combining them into a professional
              research report.

            </p>

          </div>

        )

      }

            {/* ========================================= */}
      {/* AI Generated Report */}
      {/* ========================================= */}

      {

        !loading && report && (

          <div
            className="
              mt-10
              rounded-2xl
              border
              border-[var(--border-color)]
              bg-[var(--card-bg)]
              overflow-hidden
            "
          >

            {/* Header */}

            <div
              className="
                border-b
                border-[var(--border-color)]
                p-6
                flex
                items-center
                justify-between
                flex-wrap
                gap-4
              "
            >

              <div>

                <h2
                  className="
                    text-2xl
                    font-bold
                    text-[var(--primary-text)]
                  "
                >

                  AI Generated Research Report

                </h2>

                <p
                  className="
                    mt-2
                    text-sm
                    text-[var(--secondary-text)]
                  "
                >

                  Generated using Literature Survey,
                  Paper Comparison and Research Gap Analysis.

                </p>

              </div>

              <span
                className="
                  rounded-full
                  bg-green-500/20
                  px-4
                  py-2
                  text-sm
                  font-medium
                  text-green-500
                "
              >

                Report Ready

              </span>

            </div>

            {/* Action Buttons */}

            <div
              className="
                flex
                flex-wrap
                gap-3
                p-6
                border-b
                border-[var(--border-color)]
              "
            >

              <button
                onClick={copyReport}
                className="
                  flex
                  items-center
                  gap-2
                  rounded-xl
                  border
                  border-[var(--border-color)]
                  px-5
                  py-2.5
                  font-medium
                  text-[var(--primary-text)]
                  hover:bg-[var(--card-hover)]
                "
              >

                <Copy size={18} />

                Copy

              </button>

              <button
                onClick={downloadPDF}
                className="
                  flex
                  items-center
                  gap-2
                  rounded-xl
                  border
                  border-[var(--border-color)]
                  px-5
                  py-2.5
                  font-medium
                  text-[var(--primary-text)]
                  hover:bg-[var(--card-hover)]
                "
              >

                <Download size={18} />

                PDF

              </button>

              <button
                onClick={downloadWord}
                className="
                  flex
                  items-center
                  gap-2
                  rounded-xl
                  border
                  border-[var(--border-color)]
                  px-5
                  py-2.5
                  font-medium
                  text-[var(--primary-text)]
                  hover:bg-[var(--card-hover)]
                "
              >

                <File size={18} />

                Word

              </button>

            </div>

            {/* Markdown Report */}

            <div
              className="
                p-8
                max-h-[750px]
                overflow-y-auto
                prose
                prose-invert
                max-w-none
                prose-headings:text-[var(--primary-text)]
                prose-p:text-[var(--secondary-text)]
                prose-li:text-[var(--secondary-text)]
                prose-strong:text-[var(--primary-text)]
                prose-code:text-green-500
              "
            >

              <ReactMarkdown>

                {

                  report
                    .replace(/```markdown/g, "")
                    .replace(/```/g, "")

                }

              </ReactMarkdown>

            </div>

          </div>

        )

      }
            {/* ========================================= */}
      {/* Empty State */}
      {/* ========================================= */}

      {

        !loading && !report && (

          <div
            className="
              mt-12
              rounded-2xl
              border
              border-dashed
              border-[var(--border-color)]
              bg-[var(--card-bg)]
              p-16
              text-center
            "
          >

            <div className="flex justify-center">

              <div
                className="
                  w-24
                  h-24
                  rounded-full
                  bg-[var(--button-bg)]
                  flex
                  items-center
                  justify-center
                "
              >

                <FileText
                  size={42}
                  className="text-[var(--button-text)]"
                />

              </div>

            </div>

            <h2
              className="
                mt-8
                text-3xl
                font-bold
                text-[var(--primary-text)]
              "
            >

              No Research Report Generated

            </h2>

            <p
              className="
                mt-4
                max-w-3xl
                mx-auto
                leading-8
                text-[var(--secondary-text)]
              "
            >

              Click <strong>Generate Research Report</strong> to
              combine your Literature Survey, Paper Comparison
              and Research Gap Analysis into a single
              professional AI-generated research report.

            </p>

            <button
              onClick={generateReport}
              className="
                mt-8
                flex
                items-center
                gap-3
                mx-auto
                rounded-xl
                bg-[var(--button-bg)]
                px-7
                py-3
                font-semibold
                text-[var(--button-text)]
                transition
                hover:opacity-90
              "
            >

              <Sparkles size={18} />

              Generate Report

            </button>

          </div>

        )

      }

    </MainLayout>

  );

}

export default Report;