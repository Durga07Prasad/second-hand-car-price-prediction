/**
 * Dashboard Page — Coming soon placeholder with feature importance chart.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Loader2 } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { getFeatureImportance, getModelInfo } from '../services/api';

export default function Dashboard() {
  const [features, setFeatures] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getFeatureImportance(), getModelInfo()])
      .then(([fi, mi]) => {
        setFeatures(fi);
        setModelInfo(mi);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Gradient colors for the bars
  const BAR_COLORS = [
    '#4F46E5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe',
    '#6d28d9', '#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd',
    '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe',
  ];

  return (
    <div className="min-h-screen py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Model Dashboard
          </h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            Explore the model&apos;s performance metrics and feature importance.
          </p>
        </motion.div>

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-10 h-10 text-primary-600 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Model Metrics */}
            {modelInfo && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass-card rounded-2xl p-6 space-y-4"
              >
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary-600" />
                  Model Metrics
                </h3>
                {[
                  { label: 'Model', val: modelInfo.model_name },
                  { label: 'R² Score', val: modelInfo.r2_score?.toFixed(4) },
                  { label: 'RMSE', val: `₹${Math.round(modelInfo.rmse).toLocaleString()}` },
                  { label: 'MAE', val: `₹${Math.round(modelInfo.mae).toLocaleString()}` },
                  { label: 'CV R² Mean', val: modelInfo.cv_r2_mean?.toFixed(4) },
                  { label: 'Features', val: modelInfo.feature_count },
                  { label: 'Trained', val: modelInfo.training_date?.slice(0, 10) },
                ].map((m) => (
                  <div key={m.label} className="flex justify-between items-center py-2 
                                                 border-b border-gray-100 last:border-0">
                    <span className="text-sm text-gray-500">{m.label}</span>
                    <span className="text-sm font-semibold text-gray-800">{m.val}</span>
                  </div>
                ))}
              </motion.div>
            )}

            {/* Feature Importance Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="lg:col-span-2 glass-card rounded-2xl p-6"
            >
              <h3 className="text-lg font-bold text-gray-800 mb-4">
                Global Feature Importance
              </h3>
              <ResponsiveContainer width="100%" height={500}>
                <BarChart
                  data={features}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
                >
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis
                    type="category"
                    dataKey="feature"
                    width={110}
                    tick={{ fontSize: 10 }}
                  />
                  <Tooltip
                    formatter={(v) => v.toFixed(4)}
                    contentStyle={{
                      background: 'rgba(255,255,255,0.9)',
                      border: '1px solid #e5e7eb',
                      borderRadius: '12px',
                    }}
                  />
                  <Bar dataKey="importance" radius={[0, 8, 8, 0]} barSize={24}>
                    {features.map((_, idx) => (
                      <Cell key={idx} fill={BAR_COLORS[idx % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
