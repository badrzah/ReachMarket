from fpdf import FPDF
import os

desktop = os.path.expanduser("~/Desktop")
filename = "AI_Go-To-Market_Strategy_Agent_Group01_Report_v1.pdf"
path = os.path.join(desktop, filename)

pdf = FPDF()
pdf.add_page()
pdf.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf")
pdf.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf")
pdf.add_font("Arial", "I", "C:/Windows/Fonts/ariali.ttf")

pdf.set_font("Arial", "B", 22)
pdf.cell(0, 15, "ReachGTM", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "I", 12)
pdf.cell(0, 7, "AI-Powered Go-To-Market Strategy Agent", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "Project Report - Group 01", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)

def heading(text):
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")

def body(text):
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5.5, text)
    pdf.ln(3)

pdf.set_text_color(60, 60, 60)

heading("1. What We Built")
body(
    "ReachGTM is a web-based platform that uses AI agents to automate the creation of "
    "Go-To-Market strategies for B2B SaaS companies. Users enter basic company information "
    "(name, industry, stage, description) and the system produces a complete GTM strategy "
    "including market research, competitive analysis, ICP definition, channel prioritization, "
    "growth loops, a 90-day execution plan, and ready-to-use content assets such as cold "
    "emails, LinkedIn posts, blog outlines, and ad copy. A chat interface allows users to "
    "query their uploaded knowledge base documents using RAG."
)

heading("2. Who It Is For")
body(
    "The platform targets startup founders, growth marketers, and product leaders at "
    "early-stage B2B SaaS companies (Seed to Series A) who need actionable GTM strategies "
    "but lack the budget or time for traditional strategy consultants. A demo mode gives "
    "instant access without requiring account creation."
)

heading("3. How It Works")
body(
    "The frontend is built with Next.js and deployed on Cloudflare Workers. The backend "
    "consists of two Python FastAPI services running on Railway:\n\n"
    "- A backend service handling user auth, strategy CRUD, knowledge base management, "
    "and content library operations.\n\n"
    "- An agents service running a multi-agent LangGraph pipeline. The pipeline has four "
    "stages: Research (market analysis), Strategy (GTM plan generation), Content (assets "
    "production), and Brand Alignment (consistency validation).\n\n"
    "A Cloudflare Workers reverse proxy sits in front of both services to handle CORS "
    "and route requests correctly.\n\n"
    "Users upload PDF or DOCX documents (brand guides, competitor analysis) which are "
    "extracted, chunked, embedded using OpenAI's text-embedding-3-small, and stored in "
    "pgvector for similarity search. Both the AI Chat and strategy generation query these "
    "embeddings to provide context-aware responses."
)

heading("4. AI Components Used")
body(
    "- GPT-4o-mini (OpenAI): Primary LLM for research, strategy formulation, and content generation\n"
    "- text-embedding-3-small (OpenAI): Generates vector embeddings for RAG document retrieval\n"
    "- LangGraph (LangChain): Multi-agent orchestration with state management and conditional routing\n"
    "- pgvector (PostgreSQL): Vector similarity search for knowledge base document chunks\n"
    "- LangSmith: Pipeline tracing for debugging agent behavior\n"
    "- Perplexity MCP adapter: Optional integration for real-time market data (requires API key)"
)

heading("5. What Worked Well")
body(
    "- The multi-agent pipeline produces coherent, well-structured GTM strategies with "
    "specific, actionable recommendations in about 30-60 seconds.\n\n"
    "- RAG-based chat successfully retrieves and reasons over uploaded documents, enabling "
    "context-aware Q&A (e.g., identifying user details from a CV).\n\n"
    "- The Cloudflare Workers proxy reliably handles cross-origin requests and routes "
    "traffic between the frontend and both backend services.\n\n"
    "- The knowledge base pipeline (PDF/DOCX extraction, chunking, embedding, and vector "
    "search) processes documents correctly once configured.\n\n"
    "- The demo login flow provides a frictionless onboarding experience for evaluators."
)

heading("6. Challenges and Areas for Improvement")
body(
    "- Railway's build process was sensitive to the monorepo structure. Dependency conflicts "
    "occasionally required source reconnection to trigger clean builds. A production deployment "
    "would benefit from Docker-based builds or separate service repositories.\n\n"
    "- CORS configuration required more iteration than expected - the agents service's "
    "wildcard origin combined with credentials flag did not behave consistently across "
    "all environments.\n\n"
    "- Some UI elements (like the usage progress indicator and notification button) were "
    "implemented on the frontend without corresponding backend logic, and were eventually removed.\n\n"
    "- The strategy deletion endpoint and a few other API features are implemented in code "
    "but pending deployment due to build pipeline timing."
)

heading("7. Future Improvements")
body(
    "- Enhance the knowledge base pipeline to support additional document types (web scraping, "
    "images via OCR, Notion exports).\n\n"
    "- Add user authentication flows (email verification, password reset, team invites).\n\n"
    "- Implement usage tracking to support tiered subscription plans.\n\n"
    "- Add strategy versioning, comparison views, and export options.\n\n"
    "- Build a public API for programmatic strategy generation.\n\n"
    "- Add notification webhooks (Slack, email) for strategy completion events."
)

pdf.output(path)
print(f"Report saved to: {path}")
