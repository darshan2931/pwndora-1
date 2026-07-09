# Database Models

## Users

id

UUID

name

email

created_at

---

## Assessment

id

UUID

user_id

career_goal

study_hours

career_readiness

assessment_date

---

## Roadmap

id

assessment_id

roadmap_json

estimated_weeks

---

## ChatHistory

id

assessment_id

question

answer

timestamp

---

# Relationships

User

1

↓

Many

Assessment

↓

1

Roadmap

↓

Many

ChatHistory