# CyberPath AI Frontend

Next.js application for the career intelligence dashboard.

## Structure

```
app/
  page.tsx          # Landing page
  dashboard/        # Dashboard pages
  mentor/           # AI mentor chat
components/
  Navbar.tsx
  CareerCard.tsx
  RoadmapTimeline.tsx
  SkillCard.tsx
  ProjectCard.tsx
  ChatWindow.tsx
hooks/
  useAssessment.ts
  useChat.ts
services/
  api.ts            # API client
lib/
  utils.ts
types/
  index.ts
public/
  images/
```

## Local Development

```
npm install
npm run dev
```