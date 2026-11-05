from reportlab.pdfgen import canvas

def create_pdf(path, doc_name, revenue):
    c = canvas.Canvas(path)
    c.drawString(100, 750, f"{doc_name}")
    c.drawString(100, 700, "Section 1: Financials")
    c.drawString(100, 680, f"The revenue in 2024 was ${revenue} million.")
    c.save()

create_pdf("Document_A.pdf", "Document A", "100")
create_pdf("Document_B.pdf", "Document B", "150")
