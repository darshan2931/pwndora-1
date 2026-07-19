import Link from 'next/link';

const CAREER_PATHS = [
  { title: 'Penetration Tester', category: 'Offensive', desc: 'Find and exploit vulnerabilities in systems and applications.', certs: ['eJPT', 'OSCP'], weeks: 24 },
  { title: 'SOC Analyst', category: 'Defensive', desc: 'Monitor, detect, and respond to security incidents in real-time.', certs: ['Security+', 'CySA+'], weeks: 16 },
  { title: 'Cloud Security', category: 'Infrastructure', desc: 'Secure cloud workloads across AWS, Azure, and GCP environments.', certs: ['CCSP', 'AZ-500'], weeks: 20 },
  { title: 'DFIR Specialist', category: 'Forensics', desc: 'Investigate breaches, recover evidence, and respond to incidents.', certs: ['GCFE', 'GCFA'], weeks: 28 },
  { title: 'AppSec Engineer', category: 'Development', desc: 'Secure software through code review, SAST, and threat modeling.', certs: ['GWEB', 'CSSLP'], weeks: 22 },
  { title: 'GRC Analyst', category: 'Compliance', desc: 'Manage governance, risk, and regulatory compliance programs.', certs: ['CISM', 'CISA'], weeks: 18 },
];

const FEATURES = [
  { title: 'Context-Aware AI Mentor', desc: 'Knows your career goal, your progress, your gaps. Never starts from zero. Always picks up where you left off.', icon: '🤖' },
  { title: 'Persistent Cyber Profile', desc: 'Upload your resume once. Your skills, projects, and progress are tracked forever — building your career story.', icon: '🧬' },
  { title: 'Adaptive Roadmap', desc: 'A living learning plan that updates as you grow. Skills, projects, and certifications — sequenced for your exact goal.', icon: '🗺️' },
  { title: 'Daily Missions', desc: 'Every day, your mission is pre-selected. No decision fatigue. Just focused, progressive learning.', icon: '🎯' },
  { title: 'Career Readiness Score', desc: 'A live percentage that climbs as you learn. Transparent, skill-by-skill tracking of your job readiness.', icon: '📊' },
  { title: 'Cert Preparation', desc: 'From eJPT to OSCP — your mentor knows the exam objectives and aligns your roadmap to hit them.', icon: '🏆' },
];

const HOW = [
  { n: '01', title: 'Upload Your Resume', desc: 'Drop your resume and pick a career track. Our AI maps your existing skills in 30 seconds.' },
  { n: '02', title: 'Confirm Your Skills', desc: 'Review what the AI detected. Add, remove, or edit — you train your own profile.' },
  { n: '03', title: 'Get Your Roadmap', desc: 'A personalized, sequenced learning plan with projects and certs is generated for your exact goal.' },
  { n: '04', title: 'Meet Your Mentor', desc: 'Your AI mentor knows your history. Ask it anything. It always knows what you should do next.' },
];

export default function LandingPage() {
  return (
    <div className="pt-14">
      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="grid-pattern relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-28 md:py-40 text-center">
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 border border-white/10 bg-white/[0.04] px-3 py-1 rounded-full text-xs font-medium text-zinc-400 mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Cybersecurity Career Copilot — Early Access
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-[#fafafa] mb-6 leading-[1.05] max-w-5xl mx-auto">
            The AI mentor that guides you to a{' '}
            <span className="gradient-text">cybersecurity career.</span>
          </h1>

          <p className="text-lg sm:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload your resume once. Get a persistent profile, daily learning missions, a living roadmap, and an AI mentor that remembers everything about your journey.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/onboarding"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-white text-zinc-900 font-semibold text-sm hover:bg-zinc-100 transition-colors shadow-lg"
            >
              Start Your Cyber Journey
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-white/10 bg-white/[0.04] text-zinc-300 font-medium text-sm hover:bg-white/[0.08] transition-colors"
            >
              View Live Demo
            </Link>
          </div>

          {/* Social proof */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-zinc-600">
            {['No credit card', '30-second resume analysis', '6 career tracks', 'Context-aware AI'].map(t => (
              <div key={t} className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                {t}
              </div>
            ))}
          </div>
        </div>

        {/* Preview card */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 pb-20">
          <div className="rounded-xl border border-white/[0.08] bg-[#111113] overflow-hidden shadow-xl">
            {/* Fake chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0f0f10]">
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
              <span className="ml-4 text-xs text-zinc-600 font-mono">cyberpath.ai / dashboard</span>
            </div>
            {/* Fake dashboard */}
            <div className="p-6 grid grid-cols-3 gap-4">
              <div className="col-span-2 space-y-3">
                <div className="h-6 w-48 skeleton rounded" />
                <div className="h-4 w-64 skeleton rounded" />
                <div className="grid grid-cols-4 gap-2 mt-4">
                  {[...Array(4)].map((_, i) => <div key={i} className="h-16 skeleton rounded-lg" />)}
                </div>
                <div className="h-32 skeleton rounded-lg mt-2" />
              </div>
              <div className="space-y-3">
                <div className="h-4 w-24 skeleton rounded" />
                <div className="h-44 skeleton rounded-xl" />
                <div className="h-4 w-32 skeleton rounded" />
                <div className="h-20 skeleton rounded-xl" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <p className="text-xs font-semibold text-zinc-600 uppercase tracking-widest mb-4">Platform</p>
            <h2 className="text-4xl font-bold text-[#fafafa] tracking-tight mb-4">Not a chatbot. A career system.</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">Every feature is built around one goal: getting you hired in cybersecurity.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map(f => (
              <div key={f.title} className="p-6 rounded-xl border border-white/[0.06] bg-[#111113] hover:border-white/[0.12] hover:bg-[#131315] transition-all duration-150">
                <div className="text-2xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-[#fafafa] mb-2">{f.title}</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Career Paths ──────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <p className="text-xs font-semibold text-zinc-600 uppercase tracking-widest mb-4">Career Tracks</p>
            <h2 className="text-4xl font-bold text-[#fafafa] tracking-tight mb-4">Which path are you on?</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">Six cybersecurity specializations. One AI mentor that knows them all.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {CAREER_PATHS.map(path => (
              <Link
                key={path.title}
                href="/onboarding"
                className="group p-6 rounded-xl border border-white/[0.06] bg-[#111113] hover:border-white/[0.12] hover:bg-[#131315] transition-all duration-150"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xs font-semibold text-zinc-600 uppercase tracking-wider">{path.category}</span>
                  <svg className="w-4 h-4 text-zinc-700 group-hover:text-zinc-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
                <h3 className="font-bold text-[#fafafa] text-lg mb-2">{path.title}</h3>
                <p className="text-sm text-zinc-400 mb-4 leading-relaxed">{path.desc}</p>
                <div className="flex items-center justify-between">
                  <div className="flex gap-1.5 flex-wrap">
                    {path.certs.map(c => <span key={c} className="badge-gray">{c}</span>)}
                  </div>
                  <span className="text-xs text-zinc-600">{path.weeks}wk avg</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <p className="text-xs font-semibold text-zinc-600 uppercase tracking-widest mb-4">Process</p>
            <h2 className="text-4xl font-bold text-[#fafafa] tracking-tight mb-4">From resume to roadmap in 2 minutes.</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {HOW.map((s, i) => (
              <div key={s.n} className="relative p-6 rounded-xl border border-white/[0.06] bg-[#111113]">
                <div className="text-4xl font-black text-white/[0.04] font-mono mb-4">{s.n}</div>
                <h3 className="font-semibold text-[#fafafa] mb-2">{s.title}</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">{s.desc}</p>
                {i < HOW.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 text-zinc-800">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-[#fafafa] tracking-tight mb-4">
            Start your cyber journey today.
          </h2>
          <p className="text-zinc-400 max-w-xl mx-auto mb-8">
            Upload your resume, get your profile, and meet your AI mentor — all in under 5 minutes.
          </p>
          <Link
            href="/onboarding"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-white text-zinc-900 font-semibold text-sm hover:bg-zinc-100 transition-colors shadow-lg"
          >
            Get Started — It&apos;s Free
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/[0.06] py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm font-semibold text-[#fafafa]">CyberPath AI</div>
          <p className="text-xs text-zinc-600">Built for cybersecurity learners. Powered by Mistral AI.</p>
          <div className="flex gap-4 text-xs text-zinc-600">
            <Link href="/dashboard" className="hover:text-zinc-300 transition-colors">Dashboard</Link>
            <Link href="/roadmap" className="hover:text-zinc-300 transition-colors">Roadmap</Link>
            <Link href="/mentor" className="hover:text-zinc-300 transition-colors">Mentor</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
