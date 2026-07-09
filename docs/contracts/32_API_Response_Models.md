# API Response Models

## Standard Response

{
    "success":true,
    "message":"",
    "data":{}
}

---

# Career Analysis Response

{
    "profile":{
        "skills":[],
        "projects":[],
        "certifications":[]
    },

    "career_readiness":72,

    "matched_skills":[],

    "missing_skills":[],

    "roadmap":[],

    "projects":[],

    "mentor_summary":""
}

---

# Mentor Response

{
    "response":"..."
}

---

# Error Response

{
    "success":false,
    "message":"Validation Error",
    "errors":[]
}

---

# Status Codes

200

201

400

401

404

500