export default function Home() {
  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-bold mb-6 text-primary">CyberPath AI</h1>
      <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        AI-powered Cybersecurity Career Intelligence Platform.
        Identify your skills, discover career paths, and get personalized learning recommendations.
      </p>
      <div className="flex gap-4 justify-center">
        <a href="/explore" className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-700">
          Explore Careers
        </a>
        <a href="/upload" className="border border-primary text-primary px-6 py-3 rounded-lg hover:bg-blue-50">
          Upload Resume
        </a>
      </div>
      <div className="grid grid-cols-3 gap-8 mt-16 max-w-4xl mx-auto">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-2">Skill Assessment</h3>
          <p className="text-sm text-gray-600">Upload your resume or select skills manually</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-2">Career Intelligence</h3>
          <p className="text-sm text-gray-600">See your readiness score and skill gaps</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-2">AI Mentor</h3>
          <p className="text-sm text-gray-600">Get personalized guidance from an AI mentor</p>
        </div>
      </div>
    </div>
  );
}
