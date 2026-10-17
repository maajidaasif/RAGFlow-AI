import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import {
  UploadCloud,
  Upload,
  Loader2,
  CheckCircle,
  FileText,
  ArrowRight,
} from "lucide-react";

import MainLayout from "../layouts/MainLayout";
import API from "../services/authService";


function UploadPage() {
  const navigate = useNavigate();

  const fileInputRef = useRef(null);

  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [openPicker, setOpenPicker] = useState(false);


  useEffect(() => {
    if (openPicker && fileInputRef.current) {
      fileInputRef.current.click();
      setOpenPicker(false);
    }
  }, [openPicker]);


  const openFilePicker = () => {
    fileInputRef.current?.click();
  };


  const uploadMore = () => {
    setUploadSuccess(false);
    setUploadedFiles([]);
    setMessage("");
    setError("");

    setOpenPicker(true);
  };


  const handleFileChange = async (event) => {
    const files = event.target.files;

    if (!files || files.length === 0) {
      return;
    }

    setUploading(true);
    setUploadSuccess(false);
    setError("");
    setMessage("");

    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      formData.append("papers", files[i]);
    }


    try {
      // API automatically adds JWT token
      const response = await API.post(
        "/upload-paper",
        formData
      );

      const data = response.data;


      if (data.success) {
        setUploadSuccess(true);

        setUploadedFiles(
          Array.isArray(data.papers)
            ? data.papers
            : []
        );

        setMessage(data.message);

      } else {
        setError(
          data.message ||
            "Unable to upload papers."
        );
      }

    } catch (err) {
      console.log("Upload Error:", err);

      if (err.response) {
        setError(
          err.response.data?.message ||
            "Upload failed. Please try again."
        );
      } else {
        setError(
          "Upload failed. Please try again."
        );
      }

    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };


  return (
    <MainLayout>

      <div className="max-w-6xl mx-auto">

        {/* Header */}

        <h1 className="text-4xl font-bold text-[var(--primary-text)]">

          Upload Research Papers

        </h1>

        <p className="text-[var(--secondary-text)] mt-3">

          Upload one or more research papers to begin
          AI-powered analysis.

        </p>


        {!uploadSuccess ? (

          <>

            {/* Upload Card */}

            <div
              className="
                mt-10
                bg-[var(--card-bg)]
                rounded-3xl
                border
                border-[var(--border-color)]
                p-8
                md:p-14
                transition-colors
                duration-300
              "
            >

              <div className="flex flex-col items-center text-center">

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

                  {uploading ? (

                    <Loader2
                      size={48}
                      className="
                        text-[var(--button-text)]
                        animate-spin
                      "
                    />

                  ) : (

                    <UploadCloud
                      size={48}
                      className="text-[var(--button-text)]"
                    />

                  )}

                </div>


                <h2 className="text-3xl font-bold text-[var(--primary-text)] mt-8">

                  {uploading
                    ? "Uploading Research Papers..."
                    : "Drag & Drop your PDF here"}

                </h2>


                <p className="text-[var(--secondary-text)] mt-4">

                  Supported format: PDF (.pdf)

                </p>


                <button
                  onClick={openFilePicker}
                  disabled={uploading}
                  className="
                    mt-8
                    bg-[var(--button-bg)]
                    text-[var(--button-text)]
                    border
                    border-[var(--border-color)]
                    px-8
                    py-3
                    rounded-xl
                    font-semibold
                    flex
                    items-center
                    gap-2
                    transition
                    hover:opacity-80
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                  "
                >

                  <Upload size={20} />

                  {uploading
                    ? "Uploading..."
                    : "Browse Files"}

                </button>


                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  hidden
                  ref={fileInputRef}
                  onChange={handleFileChange}
                />

              </div>

            </div>


            {/* Supported Files */}

            <div
              className="
                mt-10
                bg-[var(--card-bg)]
                rounded-3xl
                border
                border-[var(--border-color)]
                p-8
                transition-colors
                duration-300
              "
            >

              <div className="flex items-center gap-4">

                <FileText
                  size={30}
                  className="text-[var(--primary-text)]"
                />

                <div>

                  <h2 className="text-[var(--primary-text)] text-xl font-semibold">

                    Supported Files

                  </h2>

                  <p className="text-[var(--secondary-text)] mt-2">

                    • Research Papers (.pdf)

                  </p>

                  <p className="text-[var(--secondary-text)]">

                    • Multiple PDF Upload Supported

                  </p>

                  <p className="text-[var(--secondary-text)]">

                    • AI Ready Processing

                  </p>

                </div>

              </div>

            </div>

          </>

        ) : (

          <>

            {/* Upload Success */}

            <div
              className="
                mt-10
                bg-[var(--card-bg)]
                border
                border-green-500
                rounded-3xl
                p-10
                transition-colors
                duration-300
              "
            >

              <div className="flex flex-col items-center text-center">

                <CheckCircle
                  size={80}
                  className="text-green-500"
                />


                <h2 className="text-3xl font-bold text-[var(--primary-text)] mt-6">

                  Research Papers Uploaded Successfully!

                </h2>


                <p className="text-green-500 mt-3">

                  {message}

                </p>


                {/* Uploaded Papers */}

                <div
                  className="
                    mt-8
                    w-full
                    bg-[var(--card-hover)]
                    border
                    border-[var(--border-color)]
                    rounded-2xl
                    p-6
                  "
                >

                  <h3 className="text-[var(--primary-text)] text-xl font-semibold mb-5">

                    Uploaded Papers

                  </h3>


                  {uploadedFiles.map(
                    (paper, index) => (

                      <div
                        key={index}
                        className="
                          flex
                          justify-between
                          items-center
                          bg-[var(--card-bg)]
                          border
                          border-[var(--border-color)]
                          rounded-xl
                          px-4
                          py-3
                          mb-3
                        "
                      >

                        <div className="flex items-center gap-3">

                          <FileText
                            size={22}
                            className="text-[var(--primary-text)]"
                          />

                          <span className="text-[var(--primary-text)]">

                            {paper.filename}

                          </span>

                        </div>


                        <CheckCircle
                          size={22}
                          className="text-green-500"
                        />

                      </div>

                    )
                  )}

                </div>


                {/* Ready Status */}

                <div
                  className="
                    mt-8
                    w-full
                    bg-green-500/10
                    border
                    border-green-500
                    rounded-2xl
                    p-6
                  "
                >

                  <h3 className="text-green-500 text-xl font-semibold">

                    Ready for AI Analysis ✓

                  </h3>

                  <p className="text-[var(--secondary-text)] mt-3">

                    Your research papers have been
                    uploaded successfully and are ready
                    for the next AI processing modules.

                  </p>

                </div>


                {/* Buttons */}

                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 w-full">

                  <button
                    onClick={uploadMore}
                    className="
                      bg-[var(--button-bg)]
                      text-[var(--button-text)]
                      border
                      border-[var(--border-color)]
                      py-3
                      rounded-xl
                      font-semibold
                      flex
                      justify-center
                      items-center
                      gap-2
                      transition
                      hover:opacity-80
                    "
                  >

                    <Upload size={20} />

                    Upload More Papers

                  </button>


                  <button
                    onClick={() =>
                      navigate("/papers")
                    }
                    className="
                      bg-green-600
                      hover:bg-green-700
                      transition
                      py-3
                      rounded-xl
                      text-white
                      font-semibold
                      flex
                      justify-center
                      items-center
                      gap-2
                    "
                  >

                    View My Papers

                    <ArrowRight size={20} />

                  </button>

                </div>

              </div>

            </div>

          </>

        )}


        {/* Error */}

        {error && (

          <div
            className="
              mt-6
              bg-red-500/10
              border
              border-red-500
              rounded-xl
              p-4
              text-center
              text-red-500
            "
          >

            {error}

          </div>

        )}

      </div>

    </MainLayout>
  );
}


export default UploadPage;