INSERT INTO companies (id, name) VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Company')
ON CONFLICT (id) DO NOTHING;
INSERT INTO users (id, company_id, email, hashed_password, role)
VALUES ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'demo@demo.com', 'does-not-matter', 'owner')
ON CONFLICT (id) DO NOTHING;
