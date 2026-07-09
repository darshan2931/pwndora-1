# Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Mistral API unavailable | High | Medium | Cache demo responses and provide fallback messages |
| Resume parsing fails | High | Medium | Allow manual skill selection |
| Merge conflicts | Medium | High | Separate module ownership |
| Database unavailable | High | Low | Local SQLite fallback during development |
| Internet failure during demo | High | Medium | Keep offline demo dataset |
| Scope creep | High | High | Freeze MVP features after Sprint 2 |
| Time shortage | High | High | Prioritize core workflow over polish |
| Invalid AI output | Medium | Medium | Validate JSON before use |