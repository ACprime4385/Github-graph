"""
DevGraph — Internship Pitch Document Generator
Generates a professional PDF for HR/Interview presentations
"""

from fpdf import FPDF
import os


class PitchPDF(FPDF):
    def header(self):
        # Gradient-like top bar
        self.set_fill_color(221, 42, 123)  # Instagram rose
        self.rect(0, 0, 210, 4, 'F')
        self.set_fill_color(129, 52, 175)  # Instagram purple
        self.rect(0, 4, 210, 2, 'F')

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'DevGraph - Internship Pitch Document  |  Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title, emoji=''):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(221, 42, 123)
        self.cell(0, 10, f'{emoji}  {title}', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(221, 42, 123)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.l_margin + 60, self.get_y())
        self.ln(4)

    def body_text(self, text, bold=False):
        style = 'B' if bold else ''
        self.set_font('Helvetica', style, 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(5, 5.5, '-')
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def key_value(self, key, value, indent=15):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(80, 80, 80)
        x = self.get_x()
        self.set_x(x + indent)
        key_w = self.get_string_width(key + ':  ') + 2
        self.cell(key_w, 5.5, key + ':')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, value)
        self.ln(1)

    def stat_box(self, label, value):
        self.set_fill_color(245, 245, 250)
        self.set_draw_color(220, 220, 230)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 42, 22, 'DF')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(221, 42, 123)
        self.set_xy(x, y + 2)
        self.cell(42, 10, str(value), align='C')
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        self.set_xy(x, y + 12)
        self.cell(42, 8, label, align='C')
        self.set_xy(x + 46, y)


def generate_pdf():
    pdf = PitchPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===== PAGE 1: Cover =====
    pdf.add_page()
    pdf.ln(40)

    # Title
    pdf.set_font('Helvetica', 'B', 32)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 14, 'DevGraph', align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(221, 42, 123)
    pdf.cell(0, 10, 'GitHub Developer Network Explorer', align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(8)

    # Tagline
    pdf.set_font('Helvetica', 'I', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, '"Mapping the hidden connections between developers on GitHub"', align='C', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(20)

    # Metadata box
    pdf.set_fill_color(248, 248, 252)
    pdf.set_draw_color(220, 220, 230)
    box_x = 40
    box_y = pdf.get_y()
    pdf.rect(box_x, box_y, 130, 50, 'DF')

    pdf.set_xy(box_x + 10, box_y + 8)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(40, 7, 'Project:')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(70, 7, 'GitHub Developer Network Explorer')

    pdf.set_xy(box_x + 10, box_y + 18)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(40, 7, 'Domain:')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(70, 7, 'Full-Stack Web Development + Graph Databases')

    pdf.set_xy(box_x + 10, box_y + 28)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(40, 7, 'Stack:')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(70, 7, 'Python, Flask, Neo4j, Vanilla JS, HTML/CSS')

    pdf.set_xy(box_x + 10, box_y + 38)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(40, 7, 'Status:')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(70, 7, 'Live & Fully Functional')

    # ===== PAGE 2: Problem & Solution =====
    pdf.add_page()
    pdf.section_title('THE PROBLEM', '>')
    pdf.body_text(
        'In todays developer ecosystem, understanding professional networks is crucial for '
        'collaboration, hiring, and open-source contributions. However, GitHub provides no native '
        'way to explore the social graph between developers -- who follows whom, what languages '
        'connect them, and who might be a valuable second-degree connection.'
    )
    pdf.body_text(
        'Traditional follower lists are flat and one-dimensional. They dont reveal the deeper '
        'network topology that makes developer communities vibrant and interconnected.'
    )

    pdf.ln(4)
    pdf.section_title('THE SOLUTION', '*')
    pdf.body_text(
        'DevGraph is a full-stack web application that transforms GitHub developer data into an '
        'interactive network graph using a graph database (Neo4j/CognoDB). It enables developers '
        'to discover:'
    )
    pdf.bullet('Direct followers and their profiles (1-hop traversal)')
    pdf.bullet('Second-degree connections -- followers of followers (2-hop traversal)')
    pdf.bullet('Language-based networks -- developers who share programming languages')
    pdf.bullet('Aggregated network statistics and metrics')

    pdf.ln(4)
    pdf.section_title('WHY IT MATTERS', '+')
    pdf.body_text(
        'This project demonstrates advanced skills in graph database design, API integration, '
        'real-time data processing, and full-stack development -- skills that are highly valued '
        'in modern software engineering roles.'
    )

    # ===== PAGE 3: Technical Architecture =====
    pdf.add_page()
    pdf.section_title('TECHNICAL ARCHITECTURE', '#')

    pdf.key_value('Frontend', 'Vanilla JavaScript (ES6+), HTML5, CSS3 with responsive design')
    pdf.key_value('Backend', 'Python 3.11, Flask 2.3.0 with RESTful API design')
    pdf.key_value('Database', 'Neo4j (CognoDB Cloud) -- Graph database for network traversal')
    pdf.key_value('API Integration', 'GitHub REST API v3 with rate-limit handling & retry logic')
    pdf.key_value('Deployment', 'Render.com with auto-deploy from GitHub')
    pdf.key_value('Security', 'Parameterized Cypher queries, input validation, env-based secrets')

    pdf.ln(4)
    pdf.section_title('KEY TECHNICAL FEATURES', '!')

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, '1. Graph Database Modeling', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    pdf.body_text(
        'Designed a property graph model with Developer, Language, and Repository nodes '
        'connected by FOLLOWS, PROGRAMS_IN, and OWNS relationships. Implemented unique '
        'constraints and performance indexes for efficient querying.'
    )

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, '2. Multi-Hop Graph Traversal', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    pdf.body_text(
        'Implemented Cypher queries for 1-hop (direct followers) and 2-hop (followers-of-followers, '
        'shared-language networks) traversals with DISTINCT filtering, mutual connection counting, '
        'and ORDER BY ranking.'
    )

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, '3. Real-Time Data Pipeline', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    pdf.body_text(
        'Built a lazy-loading architecture that fetches from GitHub API on first search, persists '
        'to the graph database, and serves cached results on subsequent queries. Includes '
        'exponential backoff for API rate limits.'
    )

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, '4. RESTful API Design', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    pdf.body_text(
        '6 well-documented endpoints with consistent error handling, input validation (regex-based '
        'GitHub username validation), parameterized queries (injection-safe), and standardized '
        'JSON responses with timestamps.'
    )

    # ===== PAGE 4: Impact & Skills =====
    pdf.add_page()
    pdf.section_title('PROJECT IMPACT & METRICS', '%')

    # Stats boxes
    y = pdf.get_y()
    pdf.stat_box('API Endpoints', '6')
    pdf.stat_box('Cypher Queries', '12+')
    pdf.stat_box('Frontend Components', '15+')
    pdf.stat_box('Test Cases', '30+')
    pdf.ln(16)
    pdf.stat_box('Database Queries', 'Parameterized')
    pdf.stat_box('Error Codes Handled', '200/400/404/500/503')
    pdf.stat_box('API Rate Limit', 'Retry + Backoff')
    pdf.stat_box('Deployment', 'Auto-Deploy')

    pdf.ln(10)
    pdf.section_title('SKILLS DEMONSTRATED', '@')

    skills = [
        ('Backend Development', 'Python, Flask, REST API design, error handling, middleware'),
        ('Database Engineering', 'Neo4j graph modeling, Cypher queries, indexing, constraints'),
        ('Frontend Development', 'Vanilla JS (ES6+), responsive CSS, DOM manipulation'),
        ('API Integration', 'GitHub API, rate limiting, retry logic, JSON processing'),
        ('DevOps & Deployment', 'Render.com, Procfile, environment variables, CI/CD'),
        ('Security', 'Parameterized queries, input validation, secret management'),
        ('Software Design', 'MVC architecture, separation of concerns, DRY principles'),
        ('Testing', 'Manual testing, API validation, input sanitization checks'),
    ]

    for skill, detail in skills:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(221, 42, 123)
        pdf.cell(55, 6, skill)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, detail, new_x='LMARGIN', new_y='NEXT')

    # ===== PAGE 5: Why This Intern =====
    pdf.add_page()
    pdf.section_title('WHY THIS PROJECT MATTERS FOR THE INTERNSHIP', '=')

    pdf.body_text(
        'This project goes beyond a typical tutorial or coursework assignment. It demonstrates:'
    )

    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Self-Driven Learning', new_x='LMARGIN', new_y='NEXT')
    pdf.body_text(
        'I independently researched graph databases, learned Cypher query language, and designed '
        'a complete data pipeline from GitHub API to Neo4j -- all without formal instruction.'
    )

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Full-Stack Ownership', new_x='LMARGIN', new_y='NEXT')
    pdf.body_text(
        'From database schema design to frontend polish, I built every layer of this application. '
        'This shows I can own a feature end-to-end -- a critical skill for any engineering intern.'
    )

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Production Thinking', new_x='LMARGIN', new_y='NEXT')
    pdf.body_text(
        'The app includes proper error handling, input validation, rate limiting, environment-based '
        'configuration, and deployment automation -- production-grade practices, not just a prototype.'
    )

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Modern Tech Awareness', new_x='LMARGIN', new_y='NEXT')
    pdf.body_text(
        'Choosing a graph database over a traditional RDBMS for network data shows I understand '
        'when to use the right tool for the job -- a sign of mature engineering judgment.'
    )

    pdf.ln(8)
    pdf.section_title('CLOSING STATEMENT', '"')

    pdf.set_font('Helvetica', 'I', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6,
        'DevGraph is not just a project -- it is a demonstration of my ability to learn rapidly, '
        'architect complex systems, and deliver production-quality software. I am eager to bring '
        'this same energy, curiosity, and technical rigor to your team as an intern.'
    )

    pdf.ln(10)

    # Contact section
    pdf.set_fill_color(248, 248, 252)
    pdf.set_draw_color(220, 220, 230)
    pdf.rect(30, pdf.get_y(), 150, 30, 'DF')
    pdf.set_xy(30, pdf.get_y() + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(221, 42, 123)
    pdf.cell(150, 8, 'Ready to discuss further?', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_x(30)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(150, 8, 'Live Demo: http://127.0.0.1:7070  |  GitHub: github.com/ACprime4385', align='C')

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'DevGraph_Internship_Pitch.pdf')
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')
    return output_path


if __name__ == '__main__':
    generate_pdf()
