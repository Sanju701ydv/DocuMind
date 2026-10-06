import { useEffect, useRef, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const NOT_FOUND_MESSAGE =
  "I could not find this information in the uploaded documents.";

const suggestedQuestions = [
  "What vector database does DocuMind use?",
  "What embedding model does DocuMind use?",
  "What file formats are supported?",
  "How does DocuMind reduce hallucinations?",
];

/* =========================================================
   DOCUMIND LOGO
   Custom D + document + connected nodes
========================================================= */

function DocuMindLogo({ size = "normal" }) {
  const dimensions =
    size === "small"
      ? "h-9 w-9"
      : size === "large"
      ? "h-16 w-16"
      : "h-10 w-10";

  return (
    <div
      className={`${dimensions} relative flex shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-indigo-600 shadow-sm`}
    >
      <svg
        viewBox="0 0 48 48"
        className="h-[70%] w-[70%]"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Document outline */}

        <path
          d="M13 7.5H29L36 14.5V39C36 40.1 35.1 41 34 41H13C11.9 41 11 40.1 11 39V9.5C11 8.4 11.9 7.5 13 7.5Z"
          stroke="white"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Fold */}

        <path
          d="M29 8V15H36"
          stroke="white"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* D shape */}

        <path
          d="M17 20H21.5C26 20 28.5 22.5 28.5 27C28.5 31.5 26 34 21.5 34H17V20Z"
          stroke="white"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* RAG connection line */}

        <path
          d="M29.5 19.5L33 17"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />

        {/* Nodes */}

        <circle
          cx="34"
          cy="16"
          r="2.5"
          fill="white"
        />

        <circle
          cx="32.5"
          cy="22"
          r="2"
          fill="white"
        />

        <path
          d="M30 27H33"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />

        <circle
          cx="34"
          cy="27"
          r="2"
          fill="white"
        />
      </svg>
    </div>
  );
}

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [documents, setDocuments] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [loadingDocuments, setLoadingDocuments] =
    useState(false);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // ==================================================
  // AUTO SCROLL
  // ==================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, sending]);

  // ==================================================
  // LOAD DOCUMENTS
  // ==================================================

  const loadDocuments = async () => {
    try {
      setLoadingDocuments(true);

      const response = await fetch(
        `${API_URL}/api/documents`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load documents"
        );
      }

      const data = await response.json();

      setDocuments(data.documents || []);
    } catch (error) {
      console.error(
        "Document loading error:",
        error
      );
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // ==================================================
  // NEW CHAT
  // ==================================================

  const handleNewChat = () => {
    setMessages([]);
    setQuestion("");
  };

  // ==================================================
  // FILE PICKER
  // ==================================================

  const openFilePicker = () => {
    if (!uploading) {
      fileInputRef.current?.click();
    }
  };

  // ==================================================
  // FILE SELECT
  // ==================================================

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const allowedTypes = [
      ".pdf",
      ".docx",
      ".txt",
    ];

    const fileName =
      file.name.toLowerCase();

    const isAllowed =
      allowedTypes.some((extension) =>
        fileName.endsWith(extension)
      );

    if (!isAllowed) {
      alert(
        "Please select a PDF, DOCX or TXT file."
      );

      event.target.value = "";
      return;
    }

    await uploadDocument(file);

    event.target.value = "";
  };

  // ==================================================
  // UPLOAD DOCUMENT
  // ==================================================

  const uploadDocument = async (file) => {
    try {
      setUploading(true);

      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed"
        );
      }

      await loadDocuments();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            `I've successfully processed "${data.filename}".\n\n` +
            `Created ${data.chunks_created} document chunks. ` +
            `You can now ask me questions about the document.`,
          sources: [],
        },
      ]);
    } catch (error) {
      console.error(
        "Upload error:",
        error
      );

      alert(
        error.message ||
          "Failed to upload document."
      );
    } finally {
      setUploading(false);
    }
  };

  // ==================================================
  // DELETE DOCUMENT
  // ==================================================

  const handleDelete = async (
    filename
  ) => {
    const confirmed =
      window.confirm(
        `Delete "${filename}"?`
      );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/documents/${encodeURIComponent(
          filename
        )}`,
        {
          method: "DELETE",
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Delete failed"
        );
      }

      await loadDocuments();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            `"${filename}" has been removed from your documents.`,
          sources: [],
        },
      ]);
    } catch (error) {
      console.error(
        "Delete error:",
        error
      );

      alert(
        error.message ||
          "Failed to delete document."
      );
    }
  };

  // ==================================================
  // SEND MESSAGE
  // ==================================================

  const handleSend = async () => {
    const trimmedQuestion =
      question.trim();

    if (
      !trimmedQuestion ||
      sending
    ) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");
    setSending(true);

    try {
      const response = await fetch(
        `${API_URL}/api/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            question:
              trimmedQuestion,
            history: messages,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Chat request failed"
        );
      }

      const answer =
        data.answer ||
        "No answer returned.";

      const isNotFound =
        answer
          .trim()
          .toLowerCase() ===
        NOT_FOUND_MESSAGE.toLowerCase();

      const sources =
        isNotFound
          ? []
          : Array.isArray(
              data.sources
            )
          ? data.sources
          : [];

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: answer,
          sources,
          notFound: isNotFound,
        },
      ]);
    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't process your request. Please make sure the backend is running.",
          sources: [],
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  // ==================================================
  // SUGGESTED QUESTION
  // ==================================================

  const askSuggestedQuestion = (
    text
  ) => {
    setQuestion(text);

    setTimeout(() => {
      document
        .getElementById(
          "chat-input"
        )
        ?.focus();
    }, 50);
  };

  // ==================================================
  // ENTER KEY
  // ==================================================

  const handleKeyDown = (
    event
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      handleSend();
    }
  };

  // ==================================================
  // RELEVANCE
  // ==================================================

  const getRelevanceLabel = (
    relevance
  ) => {
    if (
      relevance === undefined ||
      relevance === null
    ) {
      return null;
    }

    return `${Math.round(
      relevance
    )}%`;
  };

  // ==================================================
  // RENDER
  // ==================================================

  return (
    <div className="flex h-screen overflow-hidden bg-[#f8fafc] text-slate-900">

      {/* ==================================================
          SIDEBAR
      ================================================== */}

      <aside className="hidden w-[285px] flex-col border-r border-slate-200 bg-white md:flex">

        {/* BRAND */}

        <div className="border-b border-slate-100 px-5 py-5">

          <div className="flex items-center gap-3">

            <DocuMindLogo />

            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">
                DocuMind
              </h1>

              <p className="text-xs text-slate-400">
                Document Intelligence
              </p>
            </div>

          </div>

        </div>

        {/* NEW CHAT */}

        <div className="p-4">

          <button
            type="button"
            onClick={handleNewChat}
            className="flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition hover:border-teal-200 hover:bg-teal-50/40"
          >

            <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-teal-50 text-sm font-semibold text-teal-600">
              +
            </span>

            New chat

          </button>

        </div>

        {/* DOCUMENT AREA */}

        <div className="flex-1 overflow-y-auto px-4">

          <div className="mb-3 flex items-center justify-between px-1">

            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Your documents
            </span>

            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500">
              {documents.length}
            </span>

          </div>

          {/* FILE INPUT */}

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={
              handleFileSelect
            }
            className="hidden"
          />

          {/* UPLOAD BUTTON */}

          <button
            type="button"
            onClick={
              openFilePicker
            }
            disabled={uploading}
            className="mb-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-teal-600 to-indigo-600 px-4 py-3 text-sm font-medium text-white shadow-sm transition hover:from-teal-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >

            <span className="text-base">
              {uploading
                ? "⏳"
                : "↑"}
            </span>

            {uploading
              ? "Processing..."
              : "Upload document"}

          </button>

          {/* DOCUMENTS */}

          {loadingDocuments ? (

            <div className="space-y-2">

              {[1, 2].map(
                (item) => (
                  <div
                    key={item}
                    className="h-14 animate-pulse rounded-xl bg-slate-100"
                  />
                )
              )}

            </div>

          ) : documents.length ===
            0 ? (

            <div className="rounded-xl border border-dashed border-slate-200 p-4 text-center">

              <div className="mb-2 text-2xl">
                📄
              </div>

              <p className="text-xs leading-5 text-slate-400">
                No documents yet.
                <br />
                Upload one to get started.
              </p>

            </div>

          ) : (

            <div className="space-y-2">

              {documents.map(
                (document) => (

                  <div
                    key={
                      document.filename
                    }
                    className="group rounded-xl border border-transparent p-3 transition hover:border-teal-100 hover:bg-teal-50/30"
                  >

                    <div className="flex items-center gap-3">

                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-teal-50 to-indigo-50 text-sm">
                        📄
                      </div>

                      <div className="min-w-0 flex-1">

                        <p className="truncate text-sm font-medium text-slate-700">
                          {
                            document.filename
                          }
                        </p>

                        <p className="mt-0.5 text-[11px] text-slate-400">
                          {
                            document.file_type
                          }
                          {" • "}
                          {(
                            document.size_bytes /
                            1024
                          ).toFixed(
                            1
                          )}
                          {" KB"}
                        </p>

                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          handleDelete(
                            document.filename
                          )
                        }
                        title="Delete document"
                        className="hidden text-lg leading-none text-slate-300 transition hover:text-red-500 group-hover:block"
                      >
                        ×
                      </button>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </div>

        {/* SIDEBAR FOOTER */}

        <div className="border-t border-slate-100 p-4">

          <div className="flex items-center gap-3 rounded-xl bg-gradient-to-r from-teal-50 to-indigo-50 p-3">

            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm">
              <span className="text-xs font-bold text-teal-600">
                D
              </span>
            </div>

            <div>

              <p className="text-xs font-semibold text-slate-700">
                DocuMind AI
              </p>

              <p className="text-[11px] text-green-600">
                ● System online
              </p>

            </div>

          </div>

        </div>

      </aside>

      {/* ==================================================
          MAIN
      ================================================== */}

      <main className="flex min-w-0 flex-1 flex-col">

        {/* MOBILE HEADER */}

        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 md:hidden">

          <div className="flex items-center gap-2">

            <DocuMindLogo size="small" />

            <div>
              <span className="font-bold text-slate-900">
                DocuMind
              </span>

              <p className="text-[10px] text-slate-400">
                Document AI
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={
              openFilePicker
            }
            disabled={uploading}
            className="rounded-lg bg-gradient-to-r from-teal-600 to-indigo-600 px-3 py-2 text-xs font-medium text-white"
          >
            Upload
          </button>

        </header>

        {/* CHAT HEADER */}

        <div className="hidden h-16 items-center justify-between border-b border-slate-200 bg-white px-6 md:flex">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50">
              <svg
                viewBox="0 0 24 24"
                className="h-5 w-5 text-teal-600"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path
                  d="M5 4.5A2.5 2.5 0 0 1 7.5 2H15l4 4v13.5A2.5 2.5 0 0 1 16.5 22h-9A2.5 2.5 0 0 1 5 19.5v-15Z"
                />
                <path d="M15 2v5h4" />
                <path d="M8.5 12h7M8.5 15.5h5" />
              </svg>
            </div>

            <div>

              <h2 className="text-sm font-semibold text-slate-800">
                Document Chat
              </h2>

              <p className="text-xs text-slate-400">
                Ask questions grounded in your documents
              </p>

            </div>

          </div>

          <div className="flex items-center gap-2 rounded-full bg-green-50 px-3 py-1.5 text-xs font-medium text-green-700">

            <span className="h-2 w-2 rounded-full bg-green-500" />

            API Online

          </div>

        </div>

        {/* ==================================================
            CHAT CONTENT
        ================================================== */}

        <div className="flex-1 overflow-y-auto">

          {messages.length ===
          0 ? (

            <div className="flex min-h-full items-center justify-center px-5 py-12">

              <div className="w-full max-w-2xl text-center">

                {/* LARGE LOGO */}

                <div className="mx-auto mb-6">

                  <DocuMindLogo size="large" />

                </div>

                <div className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-teal-600">
                  Document Intelligence
                </div>

                <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
                  Ask your documents.
                </h2>

                <p className="mx-auto mt-4 max-w-lg text-sm leading-6 text-slate-500">
                  Upload your documents and ask questions
                  in natural language. DocuMind retrieves
                  relevant information and keeps answers
                  grounded in your files.
                </p>

                {/* SUGGESTIONS */}

                <div className="mt-8 grid gap-3 sm:grid-cols-2">

                  {suggestedQuestions.map(
                    (suggestion) => (

                      <button
                        key={suggestion}
                        type="button"
                        onClick={() =>
                          askSuggestedQuestion(
                            suggestion
                          )
                        }
                        className="group rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-teal-200 hover:shadow-md"
                      >

                        <div className="mb-2 flex items-center justify-between">

                          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                            Try asking
                          </span>

                          <span className="text-slate-300 transition group-hover:text-teal-500">
                            →
                          </span>

                        </div>

                        <span className="text-sm leading-5 text-slate-600">
                          {suggestion}
                        </span>

                      </button>

                    )
                  )}

                </div>

                <p className="mt-8 text-xs text-slate-400">
                  Answers are generated from your uploaded documents.
                </p>

              </div>

            </div>

          ) : (

            <div className="mx-auto w-full max-w-4xl space-y-9 px-4 py-8 md:px-8">

              {messages.map(
                (message, index) => {

                  const isUser =
                    message.role ===
                    "user";

                  return (

                    <div
                      key={index}
                      className={
                        isUser
                          ? "flex justify-end"
                          : "flex items-start gap-3"
                      }
                    >

                      {/* AI AVATAR */}

                      {!isUser && (

                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-indigo-600 shadow-sm">

                          <svg
                            viewBox="0 0 48 48"
                            className="h-6 w-6"
                            fill="none"
                          >

                            <path
                              d="M13 7.5H29L36 14.5V39C36 40.1 35.1 41 34 41H13C11.9 41 11 40.1 11 39V9.5C11 8.4 11.9 7.5 13 7.5Z"
                              stroke="white"
                              strokeWidth="3"
                              strokeLinejoin="round"
                            />

                            <path
                              d="M29 8V15H36"
                              stroke="white"
                              strokeWidth="3"
                            />

                            <path
                              d="M17 20H21.5C26 20 28.5 22.5 28.5 27C28.5 31.5 26 34 21.5 34H17V20Z"
                              stroke="white"
                              strokeWidth="3"
                            />

                          </svg>

                        </div>

                      )}

                      <div
                        className={
                          isUser
                            ? "max-w-[85%]"
                            : "min-w-0 max-w-[90%]"
                        }
                      >

                        {/* LABEL */}

                        <div
                          className={
                            isUser
                              ? "mb-1 text-right text-[11px] font-medium text-slate-400"
                              : "mb-1 text-xs font-semibold text-slate-500"
                          }
                        >
                          {isUser
                            ? "You"
                            : "DocuMind"}
                        </div>

                        {/* MESSAGE */}

                        <div
                          className={
                            isUser
                              ? "rounded-2xl rounded-br-md bg-gradient-to-r from-teal-600 to-indigo-600 px-4 py-3 text-sm leading-6 text-white shadow-sm"
                              : "text-sm leading-7 text-slate-700"
                          }
                        >
                          {message.content}
                        </div>

                        {/* NOT FOUND */}

                        {!isUser &&
                          message.notFound && (

                            <div className="mt-4 flex items-center gap-3 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-xs text-amber-700">

                              <span className="text-base">
                                🔎
                              </span>

                              <span>
                                No relevant information
                                was found in your
                                uploaded documents.
                              </span>

                            </div>

                          )}

                        {/* SOURCES */}

                        {!isUser &&
                          !message.notFound &&
                          message.sources &&
                          message.sources
                            .length >
                            0 && (

                            <div className="mt-5">

                              <div className="mb-2 flex items-center gap-2">

                                <span className="text-xs font-semibold text-slate-500">
                                  Sources
                                </span>

                                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-400">
                                  {
                                    message
                                      .sources
                                      .length
                                  }
                                </span>

                              </div>

                              <div className="space-y-2">

                                {message.sources.map(
                                  (
                                    source,
                                    sourceIndex
                                  ) => (

                                    <div
                                      key={
                                        sourceIndex
                                      }
                                      className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition hover:border-teal-100"
                                    >

                                      <div className="flex items-center justify-between gap-3">

                                        <div className="flex min-w-0 items-center gap-3">

                                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-teal-50 to-indigo-50 text-xs">
                                            📄
                                          </div>

                                          <div className="min-w-0">

                                            <p className="truncate text-xs font-semibold text-slate-700">
                                              {
                                                source.filename
                                              }
                                            </p>

                                            <p className="mt-0.5 text-[10px] text-slate-400">
                                              Page{" "}
                                              {source.page ??
                                                "N/A"}
                                              {" • "}
                                              Chunk{" "}
                                              {
                                                source.chunk_id
                                              }
                                            </p>

                                          </div>

                                        </div>

                                        {getRelevanceLabel(
                                          source.relevance
                                        ) && (

                                          <span className="shrink-0 rounded-full bg-teal-50 px-2 py-1 text-[10px] font-semibold text-teal-700">
                                            {
                                              getRelevanceLabel(
                                                source.relevance
                                              )
                                            }
                                          </span>

                                        )}

                                      </div>

                                    </div>

                                  )
                                )}

                              </div>

                            </div>

                          )}

                      </div>

                    </div>

                  );
                }
              )}

              {/* THINKING */}

              {sending && (

                <div className="flex items-start gap-3">

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-indigo-600">

                    <span className="text-xs font-bold text-white">
                      D
                    </span>

                  </div>

                  <div>

                    <div className="mb-2 text-xs font-semibold text-slate-500">
                      DocuMind
                    </div>

                    <div className="flex items-center gap-1">

                      <span className="h-2 w-2 animate-bounce rounded-full bg-teal-500" />

                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-indigo-500"
                        style={{
                          animationDelay:
                            "0.15s",
                        }}
                      />

                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-teal-500"
                        style={{
                          animationDelay:
                            "0.3s",
                        }}
                      />

                    </div>

                  </div>

                </div>

              )}

              <div ref={messagesEndRef} />

            </div>

          )}

        </div>

        {/* ==================================================
            INPUT
        ================================================== */}

        <div className="border-t border-slate-200 bg-white px-4 py-4 md:px-6">

          <div className="mx-auto max-w-4xl">

            <div className="relative rounded-2xl border border-slate-300 bg-white shadow-sm transition focus-within:border-teal-400 focus-within:ring-4 focus-within:ring-teal-50">

              <textarea
                id="chat-input"
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleKeyDown
                }
                placeholder="Ask anything about your documents..."
                rows={1}
                disabled={sending}
                className="min-h-[56px] w-full resize-none bg-transparent px-4 py-4 pr-14 text-sm outline-none placeholder:text-slate-400 disabled:opacity-50"
              />

              <button
                type="button"
                onClick={
                  handleSend
                }
                disabled={
                  sending ||
                  !question.trim()
                }
                className="absolute bottom-2.5 right-2.5 flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-indigo-600 text-lg font-medium text-white shadow-sm transition hover:from-teal-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400"
                title="Send message"
              >
                ↑
              </button>

            </div>

            <p className="mt-2 text-center text-[11px] text-slate-400">
              DocuMind answers using your uploaded documents
              {" • "}
              Enter to send
              {" • "}
              Shift + Enter for a new line
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}

export default App;