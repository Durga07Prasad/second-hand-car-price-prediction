/**
 * Predict Page — Two-column form + result layout.
 * LEFT:  Input form with dropdowns and sliders.
 * RIGHT: Animated prediction result with SHAP waterfall chart.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Car, Fuel, User, Settings, Calendar, Gauge,
  Loader2, AlertCircle, TrendingUp, TrendingDown, Sparkles,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine,
} from 'recharts';
import AnimatedCounter from '../components/AnimatedCounter';
import { predictWithExplanation } from '../services/api';

// ─── Valid Options ───────────────────────────────────────────────────
const BRANDS = [
  'Maruti', 'Hyundai', 'Mahindra', 'Tata', 'Ford', 'Honda', 'Toyota',
  'Chevrolet', 'Renault', 'Other', 'Volkswagen', 'Nissan', 'Skoda',
  'Fiat', 'Audi',
];
const FUELS = ['Petrol', 'Diesel', 'CNG', 'LPG', 'Electric'];
const SELLER_TYPES = ['Individual', 'Dealer', 'Trustmark Dealer'];
const TRANSMISSIONS = ['Manual', 'Automatic'];
const OWNERS = [
  'First Owner', 'Second Owner', 'Third Owner',
  'Fourth & Above Owner', 'Test Drive Car',
];

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

// ─── Custom SHAP Tooltip ────────────────────────────────────────────
function SHAPTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="glass-card rounded-lg px-4 py-3 shadow-xl border border-gray-200">
      <p className="font-semibold text-gray-800 text-sm">{d.feature}</p>
      <p className={`text-sm font-medium ${d.value > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
        {d.value > 0 ? '+' : '-'}₹{formatINR(d.value)}
      </p>
      <p className="text-xs text-gray-400 mt-1">
        {d.value > 0 ? 'Increases' : 'Decreases'} the predicted price
      </p>
    </div>
  );
}

export default function Predict() {
  // ─── Form State ──────────────────────────────────────────────────
  const [form, setForm] = useState({
    brand: '',
    year: 2018,
    km_driven: 40000,
    fuel: '',
    seller_type: '',
    transmission: '',
    owner: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const isFormValid =
    form.brand && form.fuel && form.seller_type &&
    form.transmission && form.owner;

  // ─── Submit Handler ──────────────────────────────────────────────
  const handlePredict = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await predictWithExplanation({
        brand: form.brand,
        year: form.year,
        km_driven: form.km_driven,
        fuel: form.fuel,
        seller_type: form.seller_type,
        transmission: form.transmission,
        owner: form.owner,
      });
      setResult(data);
    } catch (err) {
      setError(err.message || 'Prediction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ─── Prepare chart data ──────────────────────────────────────────
  const chartData = result?.top_factors
    ?.map((f) => ({
      feature: f.feature,
      value: f.shap_value,
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value)) || [];

  return (
    <div className="min-h-screen py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Predict Your Car&apos;s Value
          </h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            Enter your car&apos;s details below and our AI will estimate its
            market value with a full SHAP explanation.
          </p>
        </motion.div>

        {/* ─── Two-Column Layout ───────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">

          {/* ============================================================
              LEFT COLUMN — Input Form
              ============================================================ */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <form
              onSubmit={handlePredict}
              className="glass-card rounded-2xl p-6 sm:p-8 space-y-5"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700
                                flex items-center justify-center">
                  <Car className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-gray-800">Car Details</h2>
              </div>

              {/* Brand */}
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1.5">
                  <Car className="w-4 h-4 inline mr-1" /> Brand
                </label>
                <select
                  className="select-field"
                  value={form.brand}
                  onChange={(e) => handleChange('brand', e.target.value)}
                >
                  <option value="">Select brand...</option>
                  {BRANDS.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <Calendar className="w-4 h-4 inline mr-1" /> Year
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    min="1990"
                    max="2024"
                    value={form.year}
                    onChange={(e) => handleChange('year', parseInt(e.target.value))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <Gauge className="w-4 h-4 inline mr-1" /> KM Driven
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    min="0"
                    max="300000"
                    step="1000"
                    value={form.km_driven}
                    onChange={(e) => handleChange('km_driven', parseInt(e.target.value))}
                  />
                </div>
              </div>

              {/* KM Slider */}
              <input
                type="range"
                min="0"
                max="300000"
                step="5000"
                value={form.km_driven}
                onChange={(e) => handleChange('km_driven', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
                           accent-primary-600"
              />
              <p className="text-xs text-gray-400 text-right -mt-3">
                {form.km_driven.toLocaleString()} km
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <Fuel className="w-4 h-4 inline mr-1" /> Fuel Type
                  </label>
                  <select
                    className="select-field"
                    value={form.fuel}
                    onChange={(e) => handleChange('fuel', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {FUELS.map((f) => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <Settings className="w-4 h-4 inline mr-1" /> Transmission
                  </label>
                  <select
                    className="select-field"
                    value={form.transmission}
                    onChange={(e) => handleChange('transmission', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {TRANSMISSIONS.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <User className="w-4 h-4 inline mr-1" /> Seller Type
                  </label>
                  <select
                    className="select-field"
                    value={form.seller_type}
                    onChange={(e) => handleChange('seller_type', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {SELLER_TYPES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">
                    <User className="w-4 h-4 inline mr-1" /> Owner
                  </label>
                  <select
                    className="select-field"
                    value={form.owner}
                    onChange={(e) => handleChange('owner', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {OWNERS.map((o) => (
                      <option key={o} value={o}>{o}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={!isFormValid || loading}
                whileHover={isFormValid && !loading ? { scale: 1.02 } : {}}
                whileTap={isFormValid && !loading ? { scale: 0.98 } : {}}
                className={`w-full py-4 rounded-xl text-white font-semibold text-lg
                  flex items-center justify-center gap-2 transition-all duration-300
                  ${isFormValid && !loading
                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 shadow-lg shadow-primary-600/25 hover:shadow-xl'
                    : 'bg-gray-300 cursor-not-allowed'
                  }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Predict Price
                  </>
                )}
              </motion.button>
            </form>
          </motion.div>

          {/* ============================================================
              RIGHT COLUMN — Results Panel
              ============================================================ */}
          <div className="lg:sticky lg:top-24">
            <AnimatePresence mode="wait">
              {/* Empty State */}
              {!result && !error && !loading && (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass-card rounded-2xl p-10 text-center"
                >
                  <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-2xl 
                                  flex items-center justify-center">
                    <Car className="w-10 h-10 text-gray-300" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-400 mb-2">
                    No Prediction Yet
                  </h3>
                  <p className="text-sm text-gray-400">
                    Fill in the details on the left and click &quot;Predict Price&quot;
                    to see AI-powered results here.
                  </p>
                </motion.div>
              )}

              {/* Loading State */}
              {loading && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass-card rounded-2xl p-16 flex flex-col items-center justify-center"
                >
                  <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
                  <p className="text-gray-500 font-medium">Running AI prediction...</p>
                </motion.div>
              )}

              {/* Error State */}
              {error && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -30 }}
                  className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center"
                >
                  <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-red-700 mb-2">
                    Prediction Failed
                  </h3>
                  <p className="text-sm text-red-500">{error}</p>
                </motion.div>
              )}

              {/* Success State */}
              {result && !loading && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, x: 40 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -40 }}
                  transition={{ duration: 0.5, type: 'spring', stiffness: 100 }}
                  className="space-y-6"
                >
                  {/* Price Card */}
                  <div className="relative overflow-hidden rounded-2xl 
                                  bg-gradient-to-br from-primary-600 to-primary-800 
                                  p-8 text-white shadow-2xl shadow-primary-600/30">
                    {/* Background decoration */}
                    <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 
                                    rounded-full -translate-y-10 translate-x-10" />
                    <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 
                                    rounded-full translate-y-8 -translate-x-8" />

                    <p className="text-primary-200 text-sm font-medium mb-1 relative z-10">
                      Estimated Market Value
                    </p>
                    <div className="text-4xl sm:text-5xl font-extrabold relative z-10 mb-2">
                      <AnimatedCounter
                        target={result.predicted_price}
                        prefix="₹"
                        duration={1.5}
                        triggerOnView={false}
                      />
                    </div>

                    {/* Confidence Range */}
                    {result.lower_bound != null && result.upper_bound != null && (
                      <p className="text-primary-200/80 text-sm font-medium mb-4 relative z-10">
                        Expected Range: ₹{formatINR(result.lower_bound)} – ₹{formatINR(result.upper_bound)}
                      </p>
                    )}

                    <div className="flex items-center gap-3 relative z-10">
                      <span className="inline-flex items-center gap-1 bg-white/20 
                                       px-3 py-1 rounded-full text-xs font-medium">
                        <TrendingUp className="w-3 h-3" />
                        R² = {result.model_r2_score?.toFixed(4)}
                      </span>
                      <span className="text-primary-200 text-xs">
                        Model: {result.model_used}
                      </span>
                    </div>
                  </div>

                  {/* SHAP Chart Card */}
                  {chartData.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="glass-card rounded-2xl p-6"
                    >
                      <h3 className="text-lg font-bold text-gray-800 mb-1">
                        Why This Price?
                      </h3>
                      <p className="text-sm text-gray-400 mb-4">
                        Top factors driving the prediction (SHAP values in ₹)
                      </p>

                      <ResponsiveContainer width="100%" height={chartData.length * 50 + 20}>
                        <BarChart
                          data={chartData}
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
                          <Tooltip content={<SHAPTooltip />} />
                          <ReferenceLine x={0} stroke="#9ca3af" strokeDasharray="3 3" />
                          <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={22}>
                            {chartData.map((entry, idx) => (
                              <Cell
                                key={idx}
                                fill={entry.value > 0 ? '#10b981' : '#ef4444'}
                                fillOpacity={0.85}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>

                      {/* Legend */}
                      <div className="flex items-center gap-6 mt-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3 text-emerald-500" />
                          Green = Increases price
                        </span>
                        <span className="flex items-center gap-1">
                          <TrendingDown className="w-3 h-3 text-red-500" />
                          Red = Decreases price
                        </span>
                      </div>
                    </motion.div>
                  )}

                  {/* Explanation Text */}
                  {result.explanation_text && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 }}
                      className="glass-card rounded-2xl p-6"
                    >
                      <h3 className="text-sm font-bold text-gray-600 mb-2">
                        AI Explanation
                      </h3>
                      <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
                        {result.explanation_text}
                      </p>
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
