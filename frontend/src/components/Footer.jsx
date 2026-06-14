/**
 * Footer — Simple, clean footer with project credits and links.
 */
import { Code2, Heart } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-gray-200/60 bg-white/50 backdrop-blur-sm mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">

          {/* ─── Left: Project info ──────────────────────────── */}
          <div className="flex flex-col items-center md:items-start gap-1">
            <p className="text-sm font-semibold text-gray-700">CarValueAI</p>
            <p className="text-xs text-gray-500">
              Built with React, FastAPI, CatBoost &amp; SHAP
            </p>
          </div>

          {/* ─── Center: Made with love ─────────────────────── */}
          <p className="text-xs text-gray-400 flex items-center gap-1">
            Made with <Heart className="w-3 h-3 text-red-400 fill-red-400" /> for
            Final Year Project {currentYear}
          </p>

          {/* ─── Right: GitHub link ─────────────────────────── */}
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            <Code2 className="w-4 h-4" />
            <span>View Source Code</span>
          </a>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-100 text-center">
          <p className="text-xs text-gray-400">
            © {currentYear} CarValueAI — Second-Hand Car Price Prediction Platform
          </p>
        </div>
      </div>
    </footer>
  );
}
