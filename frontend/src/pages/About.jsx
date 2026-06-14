/**
 * About Page — Project overview and technology stack.
 */
import { motion } from 'framer-motion';
import {
  Brain, Database, Server, Monitor,
  Code2, Layers, ChevronRight,
} from 'lucide-react';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const TECH_STACK = [
  {
    category: 'Data & ML',
    icon: Brain,
    color: 'from-violet-500 to-purple-600',
    items: ['Python', 'Pandas', 'Scikit-learn', 'CatBoost', 'XGBoost', 'LightGBM'],
  },
  {
    category: 'Explainability',
    icon: Layers,
    color: 'from-emerald-500 to-teal-600',
    items: ['SHAP (TreeExplainer)', 'Feature Importance', 'Waterfall Charts'],
  },
  {
    category: 'Backend API',
    icon: Server,
    color: 'from-blue-500 to-cyan-600',
    items: ['FastAPI', 'Pydantic', 'Uvicorn', 'Joblib'],
  },
  {
    category: 'Frontend',
    icon: Monitor,
    color: 'from-amber-500 to-orange-600',
    items: ['React + Vite', 'Tailwind CSS', 'Framer Motion', 'Recharts', 'Axios'],
  },
];

const PIPELINE_STEPS = [
  { step: '1', title: 'Data Collection', desc: '4,340 listings from CarDekho' },
  { step: '2', title: 'Preprocessing', desc: 'Cleaning, encoding, feature engineering' },
  { step: '3', title: 'Model Training', desc: '6 models compared, CatBoost wins' },
  { step: '4', title: 'Explainability', desc: 'SHAP values for transparent predictions' },
  { step: '5', title: 'API Deployment', desc: 'FastAPI serves predictions in <1s' },
  { step: '6', title: 'Frontend', desc: 'React dashboard for interactive use' },
];

export default function About() {
  return (
    <div className="min-h-screen py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            About CarValueAI
          </h1>
          <p className="text-gray-500 max-w-2xl mx-auto leading-relaxed">
            A final-year engineering project that builds an end-to-end machine learning
            pipeline for predicting second-hand car prices in India — from raw data to
            an interactive, explainable AI dashboard.
          </p>
        </motion.div>

        {/* Pipeline */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
          className="mb-20"
        >
          <h2 className="text-2xl font-bold text-gray-800 text-center mb-10">
            The Pipeline
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {PIPELINE_STEPS.map((s, i) => (
              <motion.div
                key={s.step}
                variants={fadeUp}
                className="relative"
              >
                <motion.div
                  whileHover={{ y: -4 }}
                  className="glass-card rounded-2xl p-5 text-center h-full"
                >
                  <div className="w-10 h-10 mx-auto mb-3 bg-gradient-to-br from-primary-500 to-primary-700
                                  rounded-xl flex items-center justify-center text-white font-bold text-sm">
                    {s.step}
                  </div>
                  <h4 className="font-semibold text-gray-800 text-sm mb-1">{s.title}</h4>
                  <p className="text-xs text-gray-400">{s.desc}</p>
                </motion.div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ChevronRight className="hidden lg:block absolute top-1/2 -right-3 
                                           w-5 h-5 text-gray-300 -translate-y-1/2" />
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Tech Stack */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{ visible: { transition: { staggerChildren: 0.15 } } }}
        >
          <h2 className="text-2xl font-bold text-gray-800 text-center mb-10">
            Technology Stack
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {TECH_STACK.map((tech) => (
              <motion.div
                key={tech.category}
                variants={fadeUp}
              >
                <motion.div
                  whileHover={{ y: -4 }}
                  className="glass-card rounded-2xl p-6 h-full"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tech.color} 
                                   flex items-center justify-center mb-4 
                                   shadow-lg shadow-gray-200`}>
                    <tech.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-bold text-gray-800 mb-3">{tech.category}</h3>
                  <div className="flex flex-wrap gap-2">
                    {tech.items.map((item) => (
                      <span
                        key={item}
                        className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-md font-medium"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Credit */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mt-20 text-center"
        >
          <div className="inline-flex items-center gap-2 text-sm text-gray-400">
            <Code2 className="w-4 h-4" />
            <Database className="w-4 h-4" />
            <span>Final Year Engineering Project — {new Date().getFullYear()}</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
