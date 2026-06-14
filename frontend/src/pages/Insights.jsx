/**
 * Insights Page — Placeholder for market analytics.
 */
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, PieChart } from 'lucide-react';

export default function Insights() {
  return (
    <div className="min-h-screen py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Market Insights
          </h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            Deep-dive analytics into the Indian second-hand car market.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl p-16 text-center max-w-2xl mx-auto"
        >
          <div className="flex justify-center gap-4 mb-6">
            {[TrendingUp, BarChart3, PieChart].map((Icon, i) => (
              <motion.div
                key={i}
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
                className="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center"
              >
                <Icon className="w-7 h-7 text-primary-600" />
              </motion.div>
            ))}
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Coming Soon</h3>
          <p className="text-gray-400">
            We&apos;re building brand-level price trends, depreciation curves,
            and segment comparisons. Stay tuned!
          </p>
        </motion.div>
      </div>
    </div>
  );
}
