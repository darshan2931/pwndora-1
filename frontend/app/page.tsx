import Link from 'next/link';
import Button from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

const features = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
      </svg>
    ),
    title: 'Resume Intelligence',
    description: 'Upload your resume and instantly extract your skills, experience, and certifications with AI-powered analysis.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </svg>
    ),
    title: 'Career Intelligence',
    description: 'Get a personalized readiness score, skill gap analysis, and prioritized learning recommendations for your target career.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
      </svg>
    ),
    title: 'Personalized Roadmap',
    description: 'Receive a step-by-step learning plan with skill dependencies, time estimates, and hands-on project recommendations.',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 00-3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 002.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 001.423 1.423z" />
      </svg>
    ),
    title: 'AI Career Mentor',
    description: 'Chat with an AI mentor that understands your profile, answers career questions, and provides explainable guidance.',
  },
];

const steps = [
  { number: '01', title: 'Upload Your Resume', description: 'Or manually select your skills from our comprehensive cybersecurity taxonomy.' },
  { number: '02', title: 'Get Your Assessment', description: 'Instantly see your readiness score, matched skills, and skill gaps for any career.' },
  { number: '03', title: 'Follow Your Roadmap', description: 'Get a personalized, step-by-step learning plan with projects and certifications.' },
  { number: '04', title: 'Grow Your Career', description: 'Chat with your AI mentor, track progress, and continuously improve your skills.' },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 dark:from-primary/10 dark:via-secondary/10 dark:to-accent/10">
      <section className="py-20 md:py-28 text-center">
        <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          AI-Powered Career Intelligence
        </div>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-gray-50 mb-6 max-w-3xl mx-auto leading-none tracking-tight">
          Your Personalized Path to a{' '}
          <span className="text-primary">Cybersecurity Career</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-2xl mx-auto">
          Identify your skills, discover the right career path, and get a customized learning roadmap
          powered by artificial intelligence.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/explore">
            <Button
              variant="outline"
              size="lg"
              fullWidth
              className="sm:w-auto hover:shadow-lg hover:-translate-y-1 transition-all"
            >
              Explore Careers
              <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
          </Link>
          <Link href="/upload">
            <Button
              size="lg"
              fullWidth
              className="sm:w-auto hover:shadow-lg hover:-translate-y-1 transition-all"
            >
              Upload Resume
            </Button>
          </Link>
        </div>
      </section>

      <section className="py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-50 mb-3">How It Works</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-xl mx-auto">Four steps to your personalized cybersecurity career plan</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step) => (
            <div key={step.number} className="text-center p-6 hover:shadow-lg hover:-translate-y-1 transition-all">
              <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl flex items-center justify-center text-xl font-bold mx-auto mb-4 hover:bg-primary/20 transition-all">
                {step.number}
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">{step.title}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-50 mb-3">Everything You Need</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-xl mx-auto">Comprehensive tools to guide your cybersecurity journey</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature) => (
            <Card
              key={feature.title}
              variant="elevated"
              className="hover:shadow-xl hover:-translate-y-1 transition-all group"
            >
              <div className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-all">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="py-16">
        <div className="bg-gradient-to-r from-primary to-primary-dark dark:from-primary/80 dark:to-secondary/60 text-white text-center p-12 rounded-xl">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Journey?</h2>
          <p className="text-blue-100 mb-8 max-w-lg mx-auto">
            Join thousands of cybersecurity professionals who started with a simple skill assessment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/upload">
              <Button
                variant="accent"
                size="lg"
                className="sm:w-auto hover:shadow-lg hover:-translate-y-1 transition-all"
              >
                Get Started Now
              </Button>
            </Link>
            <Link href="/explore">
              <Button
                variant="outline"
                size="lg"
                className="sm:w-auto text-white border-white hover:bg-white/10 hover:shadow-lg hover:-translate-y-1 transition-all"
              >
                Browse Careers
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
