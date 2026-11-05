from reportlab.pdfgen import canvas
def create_pdf(path):
    c = canvas.Canvas(path)
    c.drawString(100, 750, "Sample Hackathon Document")
    c.drawString(100, 700, "Section 1: Revenue")
    c.drawString(100, 680, "The revenue in 2024 was $10M.")
    c.showPage()
    c.drawString(100, 750, "Section 2: Employees")
    c.drawString(100, 700, "The company has 42 employees across 3 branches.")
    c.save()
create_pdf("test_doc.pdf")
