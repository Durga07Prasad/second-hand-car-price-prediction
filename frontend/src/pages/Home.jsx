/**
 * Home Page — Hero section, feature cards, and stats.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Brain, Shield, Zap, Car, ArrowRight,
  BarChart3, Users, Cpu, TrendingUp,
} from 'lucide-react';
import AnimatedCounter from '../components/AnimatedCounter';
import { getModelInfo } from '../services/api';

// ─── Animation Variants ──────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
};

export default function Home() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    getModelInfo()
      .then(setModelInfo)
      .catch(() => {}); // silently fail, use defaults
  }, []);

  const r2Display = modelInfo
    ? `${(modelInfo.r2_score * 100).toFixed(0)}%`
    : '80%';

  return (
    <div className="overflow-hidden">

      {/* ═══════════════════════════════════════════════════════════════
          HERO SECTION
          ═══════════════════════════════════════════════════════════ */}
      <section className="relative min-h-[85vh] flex items-center">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full 
                          mix-blend-multiply filter blur-3xl opacity-30 animate-float" />
          <div className="absolute top-40 right-10 w-96 h-96 bg-purple-200 rounded-full 
                          mix-blend-multiply filter blur-3xl opacity-20 animate-float" 
               style={{ animationDelay: '2s' }} />
          <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-pink-200 rounded-full 
                          mix-blend-multiply filter blur-3xl opacity-20 animate-float"
               style={{ animationDelay: '4s' }} />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="text-center max-w-4xl mx-auto"
          >
            {/* Badge */}
            <motion.div variants={fadeUp} transition={{ duration: 0.6 }}>
              <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full 
                               bg-primary-50 border border-primary-200 text-primary-700 
                               text-sm font-medium mb-6">
                <Cpu className="w-4 h-4" />
                Powered by CatBoost &amp; SHAP AI
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={fadeUp}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-7xl font-extrabold tracking-tight 
                         text-gray-900 leading-tight mb-6"
            >
              Get the <span className="gradient-text">Fair Price</span>{' '}
              for Your Car, <span className="gradient-text">Instantly</span>
            </motion.h1>

            {/* Subheading */}
            <motion.p
              variants={fadeUp}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-base sm:text-lg lg:text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed"
            >
              Our AI model, trained on thousands of Indian car listings, predicts your 
              car&apos;s market value with {r2Display} accuracy — and explains exactly why.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={fadeUp}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full px-4 sm:px-0"
            >
              <Link to="/predict" className="w-full sm:w-auto">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.97 }}
                  className="btn-primary text-base sm:text-lg w-full px-8 py-4 flex items-center justify-center gap-2"
                >
                  Predict My Car&apos;s Price
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              <Link
                to="/about"
                className="text-gray-500 hover:text-primary-600 font-medium 
                           transition-colors flex items-center justify-center gap-1 w-full sm:w-auto py-2 sm:py-0"
              >
                Learn how it works →
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
          FEATURE CARDS
          ═══════════════════════════════════════════════════════════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={stagger}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {[
              {
                icon: Brain,
                title: 'AI-Powered Predictions',
                desc: `CatBoost model with ${r2Display} R² accuracy on test data.`,
                color: 'from-primary-500 to-indigo-600',
                badge: `R² ${r2Display}`,
              },
              {
                icon: Shield,
                title: 'Explainable AI',
                desc: 'SHAP values reveal exactly which factors drive each price prediction.',
                color: 'from-emerald-500 to-teal-600',
                badge: 'SHAP',
              },
              {
                icon: Zap,
                title: 'Instant Results',
                desc: 'Get a prediction in under 1 second. No sign-ups, no waiting.',
                color: 'from-amber-500 to-orange-600',
                badge: '<1s',
              },
              {
                icon: Car,
                title: '15+ Brands Supported',
                desc: 'Maruti, Hyundai, Toyota, Audi and 11 more Indian market brands.',
                color: 'from-pink-500 to-rose-600',
                badge: '15',
              },
            ].map((card, i) => (
              <motion.div
                key={card.title}
                variants={fadeUp}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <motion.div
                  whileHover={{ y: -6, scale: 1.02 }}
                  transition={{ type: 'spring', stiffness: 300 }}
                  className="relative glass-card rounded-2xl p-6 h-full cursor-default"
                >
                  {/* Badge */}
                  <span className="absolute top-4 right-4 text-xs font-bold 
                                   bg-gray-100 text-gray-600 px-2 py-1 rounded-md">
                    {card.badge}
                  </span>

                  {/* Icon */}
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} 
                                   flex items-center justify-center mb-4 
                                   shadow-lg shadow-gray-200`}>
                    <card.icon className="w-6 h-6 text-white" />
                  </div>

                  <h3 className="text-lg font-bold text-gray-800 mb-2">{card.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{card.desc}</p>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
          STATS SECTION
          ═══════════════════════════════════════════════════════════ */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={stagger}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {[
              {
                value: 3577,
                label: 'Cars Analyzed',
                icon: BarChart3,
                suffix: '+',
                prefix: '',
              },
              {
                value: modelInfo ? Math.round(modelInfo.r2_score * 100) : 80,
                label: 'Model Accuracy',
                icon: TrendingUp,
                suffix: '%',
                prefix: '',
              },
              {
                value: 6,
                label: 'ML Models Compared',
                icon: Cpu,
                suffix: '',
                prefix: '',
              },
              {
                value: 15,
                label: 'Brands Supported',
                icon: Users,
                suffix: '',
                prefix: '',
              },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                variants={fadeUp}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="text-center"
              >
                <stat.icon className="w-8 h-8 text-primary-200 mx-auto mb-3" />
                <div className="text-4xl sm:text-5xl font-extrabold text-white mb-1">
                  <AnimatedCounter
                    target={stat.value}
                    prefix={stat.prefix}
                    suffix={stat.suffix}
                    duration={2}
                    className=""
                  />
                </div>
                <p className="text-primary-200 text-sm font-medium">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
          BOTTOM CTA
          ═══════════════════════════════════════════════════════════ */}
      <section className="py-24">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
          >
            <motion.h2
              variants={fadeUp}
              className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4"
            >
              Ready to find your car&apos;s value?
            </motion.h2>
            <motion.p variants={fadeUp} className="text-gray-500 mb-8 text-lg">
              Enter a few details and get an AI-powered estimate in seconds.
            </motion.p>
            <motion.div variants={fadeUp}>
              <Link to="/predict">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.97 }}
                  className="btn-primary text-lg px-10 py-4"
                >
                  Start Predicting →
                </motion.button>
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
