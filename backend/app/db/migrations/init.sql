1|1|-- Extensions (created manually as postgres superuser)
2|2|-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
3|3|-- CREATE EXTENSION IF NOT EXISTS vector;
4|4|
5|5|-- Companies
6|6|CREATE TABLE IF NOT EXISTS IF NOT EXISTS companies (
7|7|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
8|8|    name        TEXT NOT NULL,
9|9|    plan        TEXT NOT NULL DEFAULT 'free',
10|10|    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
11|11|);
12|12|
13|13|-- Users
14|14|CREATE TABLE IF NOT EXISTS users (
15|15|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
16|16|    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
17|17|    email       TEXT NOT NULL UNIQUE,
18|18|    hashed_password TEXT NOT NULL,
19|19|    role        TEXT NOT NULL DEFAULT 'member',
20|20|    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
21|21|    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
22|22|);
23|23|
24|24|-- Sessions (refresh token store)
25|25|CREATE TABLE IF NOT EXISTS sessions (
26|26|    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
27|27|    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
28|28|    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
29|29|    refresh_token   TEXT NOT NULL UNIQUE,
30|30|    expires_at      TIMESTAMPTZ NOT NULL,
31|31|    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
32|32|);
33|33|
34|34|-- Knowledge documents (metadata)
35|35|CREATE TABLE IF NOT EXISTS knowledge_documents (
36|36|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
37|37|    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
38|38|    filename    TEXT NOT NULL,
39|39|    doc_type    TEXT NOT NULL,
40|40|    status      TEXT NOT NULL DEFAULT 'pending',
41|41|    s3_key      TEXT,
42|42|    chunk_count INT,
43|43|    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
44|44|);
45|45|
46|46|-- Document chunks (vector store)
47|47|CREATE TABLE IF NOT EXISTS document_chunks (
48|48|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
49|49|    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
50|50|    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
51|51|    namespace   TEXT NOT NULL,
52|52|    chunk_index INT NOT NULL,
53|53|    content     TEXT NOT NULL,
54|54|    embedding   vector(1536),
55|55|    metadata    JSONB DEFAULT '{}',
56|56|    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
57|57|);
58|58|
59|59|-- Strategies
60|60|CREATE TABLE IF NOT EXISTS strategies (
61|61|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
62|62|    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
63|63|    user_id     UUID NOT NULL REFERENCES users(id),
64|64|    session_id  UUID NOT NULL,
65|65|    status      TEXT NOT NULL DEFAULT 'generating',
66|66|    payload     JSONB,
67|67|    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
68|68|    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
69|69|);
70|70|
71|71|-- Content assets
72|72|CREATE TABLE IF NOT EXISTS content_assets (
73|73|    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
74|74|    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
75|75|    strategy_id     UUID REFERENCES strategies(id) ON DELETE SET NULL,
76|76|    content_type    TEXT NOT NULL,
77|77|    title           TEXT NOT NULL,
78|78|    body            TEXT NOT NULL,
79|79|    validation_status TEXT NOT NULL DEFAULT 'pending',
80|80|    brand_alignment_score FLOAT,
81|81|    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
82|82|);
83|83|
84|84|-- Company memory (persistent context across sessions)
85|85|CREATE TABLE IF NOT EXISTS company_memory (
86|86|    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
87|87|    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
88|88|    key         TEXT NOT NULL,
89|89|    value       JSONB NOT NULL,
90|90|    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
91|91|    UNIQUE(company_id, key)
92|92|);
93|93|
94|94|-- HNSW index for fast cosine similarity search
95|95|CREATE INDEX IF NOT EXISTS ON document_chunks USING hnsw (embedding vector_cosine_ops)
96|96|    WITH (m = 16, ef_construction = 64);
97|97|
98|98|CREATE INDEX IF NOT EXISTS ON document_chunks (company_id, namespace);
99|99|
100|100|-- Row-Level Security
101|101|ALTER TABLE companies           ENABLE ROW LEVEL SECURITY;
102|102|ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
103|103|ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
104|104|ALTER TABLE document_chunks     ENABLE ROW LEVEL SECURITY;
105|105|ALTER TABLE strategies          ENABLE ROW LEVEL SECURITY;
106|106|ALTER TABLE content_assets      ENABLE ROW LEVEL SECURITY;
107|107|ALTER TABLE company_memory      ENABLE ROW LEVEL SECURITY;
108|108|
109|109|-- RLS policies (reads current_setting set by tenant middleware)
110|110|CREATE POLICY IF NOT EXISTS tenant_isolation ON companies
111|111|    USING (id = current_setting('app.current_company_id', TRUE)::UUID);
112|112|
113|113|CREATE POLICY IF NOT EXISTS tenant_isolation ON users
114|114|    USING (
115|115|        company_id = current_setting('app.current_company_id', TRUE)::UUID
116|116|        OR current_setting('app.current_company_id', TRUE) IS NULL
117|117|    );
118|118|
119|119|CREATE POLICY IF NOT EXISTS tenant_isolation ON knowledge_documents
120|120|    USING (company_id = current_setting('app.current_company_id', TRUE)::UUID);
121|121|
122|122|CREATE POLICY IF NOT EXISTS tenant_isolation ON document_chunks
123|123|    USING (company_id = current_setting('app.current_company_id', TRUE)::UUID);
124|124|
125|125|CREATE POLICY IF NOT EXISTS tenant_isolation ON strategies
126|126|    USING (company_id = current_setting('app.current_company_id', TRUE)::UUID);
127|127|
128|128|CREATE POLICY IF NOT EXISTS tenant_isolation ON content_assets
129|129|    USING (company_id = current_setting('app.current_company_id', TRUE)::UUID);
130|130|
131|131|CREATE POLICY IF NOT EXISTS tenant_isolation ON company_memory
132|132|    USING (company_id = current_setting('app.current_company_id', TRUE)::UUID);
133|133|
134|134|-- Superuser bypass for migrations and internal services
135|135|-- NOTE: Removed because Railway connects as postgres (superuser),
136|136|-- which lets all tenants see each other's data.
137|137|-- RLS alone is sufficient for tenant isolation.
138|138|