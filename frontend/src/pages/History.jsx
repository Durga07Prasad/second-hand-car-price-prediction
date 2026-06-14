/**
 * History Page — Displays recent prediction history with animated cards.
 */
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Clock, Car, Fuel, Settings, User, RefreshCw,
  Loader2, History as HistoryIcon,
} from 'lucide-react';
import { getPredictionHistory } from '../services/api';

// ─── Indian currency formatter ──────────────────────────────────────
function formatINR(num) {
  const n = Math.round(Math.abs(num));
  const str = n.toString();
  if (str.length <= 3) return str;
  let result = str.slice(-3);
  let remaining = str.slice(0, -3);
  while (remaining.length > 0) {
    result = remaining.slice(-2) + ',' + result;
    remaining = remaining.slice(0, -2);
  }
  return result;
}

// ─── Relative time helper ───────────────────────────────────────────
function timeAgo(dateString) {
  const now = new Date();
  const date = new Date(dateString);
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return 'Just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
  const months = Math.floor(days / 30);
  return `${months} month${months > 1 ? 's' : ''} ago`;
}

// ─── Skeleton Loader ────────────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="glass-card rounded-2xl p-6 animate-pulse">
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="h-6 w-32 bg-gray-200 rounded-lg mb-2" />
          <div className="h-4 w-20 bg-gray-100 rounded-lg" />
        </div>
        <div className="h-8 w-28 bg-gray-200 rounded-lg" />
      </div>
      <div className="flex gap-2">
        <div className="h-6 w-16 bg-gray-100 rounded-full" />
        <div className="h-6 w-16 bg-gray-100 rounded-full" />
        <div className="h-6 w-20 bg-gray-100 rounded-full" />
      </div>
    </div>
  );
}

export default function History() {
  const [predictions, setPredictions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHistory = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const data = await getPredictionHistory(20);
      setPredictions(data.predictions || []);
      setTotal(data.total || 0);
    } catch {
      // silent fail, show empty state
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="min-h-screen py-10">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Prediction History
          </h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            Browse your recent car price predictions. {total > 0 && (
              <span className="font-medium text-primary-600">{total} total</span>
            )}
          </p>
        </motion.div>

        {/* Refresh Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex justify-end mb-6"
        >
          <button
            onClick={() => fetchHistory(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium
                       text-primary-600 bg-primary-50 hover:bg-primary-100 
                       transition-all duration-200 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </motion.div>

        {/* Loading State */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && predictions.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-16 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-2xl 
                            flex items-center justify-center">
              <HistoryIcon className="w-10 h-10 text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-600 mb-2">
              No Predictions Yet
            </h3>
            <p className="text-gray-400 mb-6">
              Head over to the Predict page and estimate your first car&apos;s value!
            </p>
            <a
              href="/predict"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm 
                         font-semibold text-white bg-gradient-to-r from-primary-600 
                         to-primary-700 shadow-lg shadow-primary-600/25 
                         hover:shadow-xl transition-all"
            >
              <Car className="w-4 h-4" />
              Try Predict Page
            </a>
          </motion.div>
        )}

        {/* Prediction Cards */}
        {!loading && predictions.length > 0 && (
          <div className="space-y-4">
            {predictions.map((pred, index) => (
              <motion.div
                key={pred.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: index * 0.05, duration: 0.4 }}
                className="glass-card rounded-2xl p-5 sm:p-6 hover:shadow-lg 
                           transition-shadow duration-300"
              >
                <div className="flex flex-col sm:flex-row sm:items-center 
                                sm:justify-between gap-3 mb-3">
                  {/* Brand + Year */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">
                      {pred.brand} {pred.year}
                    </h3>
                    <p className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {timeAgo(pred.created_at)}
                    </p>
                  </div>

                  {/* Price */}
                  <div className="text-right">
                    <p className="text-2xl font-extrabold text-primary-600">
                      ₹{formatINR(pred.predicted_price)}
                    </p>
                  </div>
                </div>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full 
                                   text-xs font-medium bg-blue-50 text-blue-600">
                    <Fuel className="w-3 h-3" />
                    {pred.fuel}
                  </span>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full 
                                   text-xs font-medium bg-purple-50 text-purple-600">
                    <Settings className="w-3 h-3" />
                    {pred.transmission}
                  </span>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full 
                                   text-xs font-medium bg-amber-50 text-amber-600">
                    <User className="w-3 h-3" />
                    {pred.owner}
                  </span>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full 
                                   text-xs font-medium bg-gray-100 text-gray-600">
                    {pred.km_driven?.toLocaleString()} km
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
