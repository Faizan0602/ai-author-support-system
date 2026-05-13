import React, { useState } from 'react';
import axios from 'axios';
import {
  Play,
  CheckCircle,
  AlertCircle,
  Clock,
  Info,
  UserSearch,
} from 'lucide-react';

export default function App() {
  // =========================
  // Workflow State
  // =========================

  const [channel, setChannel] = useState('email');
  const [identifier, setIdentifier] = useState('');
  const [query, setQuery] = useState('');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // =========================
  // Identity Resolution State
  // =========================

  const [identityInput, setIdentityInput] =
    useState('');

  const [identityLoading, setIdentityLoading] =
    useState(false);

  const [identityResult, setIdentityResult] =
    useState(null);

  const [identityError, setIdentityError] =
    useState('');

  // =========================
  // Workflow Simulation
  // =========================

  const handleSimulate = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/api/v1/simulate-channel-query',
        {
          source_channel: channel,
          author_identifier: identifier,
          user_query: query,
        }
      );

      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'An error occurred during simulation.'
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // Identity Resolution
  // =========================

  const handleResolveIdentity = async (e) => {
    e.preventDefault();

    setIdentityLoading(true);
    setIdentityError('');
    setIdentityResult(null);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/api/v1/resolve-identity',
        {
          identifier: identityInput,
        }
      );

      setIdentityResult(response.data);
    } catch (err) {
      setIdentityError(
        err.response?.data?.detail ||
          err.message ||
          'Identity resolution failed.'
      );
    } finally {
      setIdentityLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 font-sans selection:bg-indigo-500/30 p-8">
      <div className="max-w-6xl mx-auto space-y-16">

        {/* ========================= */}
        {/* Header */}
        {/* ========================= */}

        <header className="border-b border-neutral-800 pb-6">
          <h1 className="text-4xl font-bold text-white tracking-tight">
            AI Author Support System
          </h1>

          <p className="text-neutral-400 mt-3">
            Multi-channel AI workflow automation
            and identity resolution platform.
          </p>
        </header>

        {/* ========================= */}
        {/* Workflow Pipeline */}
        {/* ========================= */}

        <div className="bg-neutral-900/40 border border-neutral-800 rounded-xl p-4">
          <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-neutral-300">

            <span className="bg-neutral-800 px-3 py-2 rounded-lg">
              Identify User
            </span>

            <span className="text-neutral-500">→</span>

            <span className="bg-neutral-800 px-3 py-2 rounded-lg">
              Classify Intent
            </span>

            <span className="text-neutral-500">→</span>

            <span className="bg-neutral-800 px-3 py-2 rounded-lg">
              Query DB / KB
            </span>

            <span className="text-neutral-500">→</span>

            <span className="bg-neutral-800 px-3 py-2 rounded-lg">
              Generate Response
            </span>

            <span className="text-neutral-500">→</span>

            <span className="bg-neutral-800 px-3 py-2 rounded-lg">
              Log Conversation
            </span>

          </div>
        </div>

        {/* ========================= */}
        {/* Workflow Automation */}
        {/* ========================= */}

        <section className="space-y-6">

          <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
            <Play className="w-5 h-5 text-indigo-400" />

            <h2 className="text-2xl font-semibold text-white">
              Workflow Automation Simulator
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            {/* Left Form */}

            <div className="space-y-6">
              <form
                onSubmit={handleSimulate}
                className="space-y-5"
              >

                {/* Channel */}

                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-300">
                    Source Channel
                  </label>

                  <select
                    value={channel}
                    onChange={(e) =>
                      setChannel(e.target.value)
                    }
                    className="w-full bg-neutral-900 border border-neutral-800 text-white rounded-lg px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  >
                    <option value="email">Email</option>
                    <option value="whatsapp">
                      WhatsApp
                    </option>
                    <option value="instagram">
                      Instagram
                    </option>
                    <option value="dashboard_chat">
                      Dashboard Chat
                    </option>
                  </select>
                </div>

                {/* Identifier */}

                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-300">
                    Author Identifier
                  </label>

                  <input
                    type="text"
                    value={identifier}
                    onChange={(e) =>
                      setIdentifier(e.target.value)
                    }
                    placeholder="rahul@example.com"
                    className="w-full bg-neutral-900 border border-neutral-800 text-white rounded-lg px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                    required
                  />
                </div>

                {/* Query */}

                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-300">
                    User Query
                  </label>

                  <textarea
                    value={query}
                    onChange={(e) =>
                      setQuery(e.target.value)
                    }
                    placeholder="When will I get my royalty?"
                    rows={5}
                    className="w-full bg-neutral-900 border border-neutral-800 text-white rounded-lg px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none"
                    required
                  />
                </div>

                {/* Example Queries */}

                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-wider text-neutral-500">
                    Example Queries
                  </p>

                  <div className="flex flex-wrap gap-2">

                    {[
                      'When will I get my royalty?',
                      'Is my book live yet?',
                      'Where is my author copy?',
                      'Why is my book not Prime?',
                      'How do I join the 21-Day Writing Challenge?',
                    ].map((example) => (
                      <button
                        key={example}
                        type="button"
                        onClick={() =>
                          setQuery(example)
                        }
                        className="text-xs bg-neutral-800 hover:bg-neutral-700 transition-colors px-3 py-2 rounded-lg border border-neutral-700"
                      >
                        {example}
                      </button>
                    ))}

                  </div>
                </div>

                {/* Button */}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-white text-black hover:bg-neutral-200 font-medium py-3 px-4 rounded-lg text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Simulate Workflow
                    </>
                  )}
                </button>
              </form>

              {/* Error */}

              {error && (
                <div className="p-4 bg-red-950/30 border border-red-900/50 rounded-lg flex gap-3 text-red-200 text-sm">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />

                  <p>{error}</p>
                </div>
              )}
            </div>

            {/* Right Result */}

            <div className="bg-neutral-900/40 border border-neutral-800 rounded-xl p-6 min-h-[420px]">

              {result ? (
                <div className="space-y-6">

                  {/* Header */}

                  <div className="flex items-center justify-between border-b border-neutral-800 pb-4">

                    <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
                      Workflow Result
                    </h3>

                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        result.processing_status ===
                        'success'
                          ? 'bg-green-950/50 text-green-400 border border-green-900/50'
                          : 'bg-amber-950/50 text-amber-400 border border-amber-900/50'
                      }`}
                    >
                      {result.processing_status}
                    </span>
                  </div>

                  {/* Grid */}

                  <div className="grid grid-cols-2 gap-4 text-sm">

                    <div>
                      <span className="text-neutral-500 text-xs uppercase block mb-1">
                        Workflow ID
                      </span>

                      <span className="font-mono text-xs">
                        {result.workflow_id}
                      </span>
                    </div>

                    <div>
                      <span className="text-neutral-500 text-xs uppercase block mb-1">
                        Channel
                      </span>

                      <span className="capitalize">
                        {result.source_channel}
                      </span>
                    </div>

                    <div>
                      <span className="text-neutral-500 text-xs uppercase block mb-1">
                        Intent
                      </span>

                      <span className="capitalize">
                        {result.intent}
                      </span>
                    </div>

                    <div>
                      <span className="text-neutral-500 text-xs uppercase block mb-1">
                        Confidence
                      </span>

                      <span>
                        {(
                          result.confidence * 100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>
                  </div>

                  {/* Escalation */}

                  <div className="pt-4 border-t border-neutral-800">
                    <div className="flex items-center gap-2">

                      {result.escalation_required ? (
                        <AlertCircle className="w-4 h-4 text-amber-500" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}

                      <span className="text-sm font-medium">
                        {result.escalation_required
                          ? 'Escalated to Human Agent'
                          : 'Handled Automatically'}
                      </span>
                    </div>
                  </div>

                  {/* Response */}

                  <div className="pt-4 border-t border-neutral-800">
                    <span className="text-neutral-500 text-xs uppercase tracking-wider block mb-3">
                      Final Response
                    </span>

                    <div className="bg-neutral-950 border border-neutral-800 p-4 rounded-lg whitespace-pre-wrap text-sm text-neutral-300">
                      {result.final_response}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-neutral-500 gap-3">
                  <Info className="w-8 h-8 opacity-50" />

                  <p className="text-sm">
                    Run a workflow simulation to
                    view results.
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ========================= */}
        {/* Identity Resolution */}
        {/* ========================= */}

        <section className="space-y-6">

          <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
            <UserSearch className="w-5 h-5 text-indigo-400" />

            <h2 className="text-2xl font-semibold text-white">
              Identity Resolution Demo
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            {/* Left */}

            <div>
              <form
                onSubmit={handleResolveIdentity}
                className="space-y-5"
              >

                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-300">
                    Identifier
                  </label>

                  <input
                    type="text"
                    value={identityInput}
                    onChange={(e) =>
                      setIdentityInput(
                        e.target.value
                      )
                    }
                    placeholder="@rahulwrites or rahul@example.com"
                    className="w-full bg-neutral-900 border border-neutral-800 text-white rounded-lg px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={identityLoading}
                  className="w-full bg-white text-black hover:bg-neutral-200 font-medium py-3 px-4 rounded-lg text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {identityLoading ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" />
                      Resolving...
                    </>
                  ) : (
                    <>
                      <UserSearch className="w-4 h-4" />
                      Resolve Identity
                    </>
                  )}
                </button>
              </form>

              {/* Error */}

              {identityError && (
                <div className="mt-4 p-4 bg-red-950/30 border border-red-900/50 rounded-lg flex gap-3 text-red-200 text-sm">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />

                  <p>{identityError}</p>
                </div>
              )}
            </div>

            {/* Right */}

            <div className="bg-neutral-900/40 border border-neutral-800 rounded-xl p-6 min-h-[320px]">

              {identityResult ? (
                <div className="space-y-6">

                  {/* Header */}

                  <div className="flex items-center justify-between border-b border-neutral-800 pb-4">

                    <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
                      Resolution Result
                    </h3>

                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        identityResult.matched
                          ? 'bg-green-950/50 text-green-400 border border-green-900/50'
                          : 'bg-red-950/50 text-red-400 border border-red-900/50'
                      }`}
                    >
                      {identityResult.matched
                        ? 'Matched'
                        : 'No Match'}
                    </span>
                  </div>

                  {/* Confidence */}

                  <div>
                    <span className="text-neutral-500 text-xs uppercase block mb-1">
                      Confidence
                    </span>

                    <span>
                      {(
                        identityResult.confidence *
                        100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>

                  {/* Verification */}

                  <div className="pt-4 border-t border-neutral-800">

                    <div className="flex items-center gap-2">

                      {identityResult.escalation_required ? (
                        <AlertCircle className="w-4 h-4 text-amber-500" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}

                      <span className="text-sm font-medium">
                        {identityResult.escalation_required
                          ? 'Manual Verification Required'
                          : 'Auto Verified'}
                      </span>
                    </div>
                  </div>

                  {/* Author */}

                  {identityResult.matched_author && (
                    <div className="pt-4 border-t border-neutral-800 space-y-4">

                      <h4 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                        Matched Author
                      </h4>

                      <div className="bg-neutral-950 border border-neutral-800 rounded-lg p-4 space-y-3">

                        <div>
                          <span className="text-neutral-500 text-xs uppercase block mb-1">
                            Name
                          </span>

                          <span>
                            {
                              identityResult
                                .matched_author
                                .author_name
                            }
                          </span>
                        </div>

                        <div>
                          <span className="text-neutral-500 text-xs uppercase block mb-1">
                            Email
                          </span>

                          <span>
                            {
                              identityResult
                                .matched_author
                                .email
                            }
                          </span>
                        </div>

                        <div>
                          <span className="text-neutral-500 text-xs uppercase block mb-1">
                            Author ID
                          </span>

                          <span className="font-mono text-xs">
                            {
                              identityResult
                                .matched_author
                                .id
                            }
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-neutral-500 gap-3">
                  <Info className="w-8 h-8 opacity-50" />

                  <p className="text-sm">
                    Resolve an author identity to
                    view results.
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ========================= */}
        {/* Footer */}
        {/* ========================= */}

        <footer className="border-t border-neutral-800 pt-6 text-center text-sm text-neutral-500">
          FastAPI • Gemini AI • Supabase • React • Tailwind CSS
        </footer>
      </div>
    </div>
  );
}