# ADR-003: JSON Knowledge Base over Neo4j

## Context

The cybersecurity taxonomy (roles, skills, projects, certifications) needs to be structured, version-controlled, and easy to edit without database migrations.

## Decision

Store the knowledge base as JSON files instead of a graph database.

## Rationale

- No operational overhead — files are committed to git, reviewed in PRs
- Human-readable and editable by non-engineers
- Easy to seed test data without migrations
- Neo4j graph traversal benefits are unnecessary for the small, finite taxonomy
- The Career Engine traverses relationships programmatically in Python, not via graph queries
- Faster development iteration — edit JSON, reload service

## Consequences

- Relationship queries are implemented in Python logic, not in Cypher
- JSON must be kept in sync with code changes (version controlled, same as code)
- Not suitable if taxonomy grows beyond ~10K nodes — unlikely for MVP