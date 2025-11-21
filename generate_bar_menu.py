from fpdf import FPDF, XPos, YPos

# Elegant black & gold Elements Bar Menu PDF (A4)
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Background
pdf.set_fill_color(0, 0, 0)
pdf.rect(0, 0, 210, 297, 'F')

# Gold text color
gold = (212, 175, 55)
pdf.set_text_color(*gold)

# Header with logo and title
try:
    pdf.image("static/logo.PNG", x=85, y=10, w=40)
except:
    print("⚠️ Logo not found — skipping image.")

pdf.ln(50)
pdf.set_font("Helvetica", "B", 20)
pdf.cell(0, 10, "Elements by Chef Sultan", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.set_font("Helvetica", "I", 15)
pdf.cell(0, 10, "Bar Menu", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.ln(10)

# Divider function
def divider():
    pdf.set_draw_color(*gold)
    pdf.set_line_width(0.4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)

# Menu structure
menu = {
    "RED WINES": [
        "BEEFSTEAK CLUB MALBEC ...... (BTL) £29.00 ...... (GLS) £7.25",
        "LFE GRAN RES Merlot ......... (BTL) £27.00 ...... (GLS) £6.75"
    ],
    "WHITE WINES": [
        "Emma Marris Sauvignon Blanc . (BTL) £27.95 ..... (GLS) £7.00",
        "PINOT GRIGIO BREGANZE ....... (BTL) £26.00 ..... (GLS) £6.50"
    ],
    "SPIRITS": {
        "GIN": [
            "Tanqueray London Dry Gin ....................... £9.00",
            "Marlow Gin Green ................................ £8.50",
            "Marlow Gin Blue ................................. £9.00"
        ],
        "VODKA": [
            "Absolut Vodka ................................. £8.40",
            "Stoli Vodka, Latvia ........................... £8.20"
        ],
        "WHISKY": [
            "Johnnie Walker Black Label ..................... £9.50",
            "Glenmorangie Original 12YO ..................... £9.60"
        ]
    },
    "DESSERT WINE, PORT & COGNAC": [
        "Luis Felipe Edwards 'Late Harvest' Viognier/Sauvignon Blanc .... £5.00",
        "Croft Reserve Tawny Port ....................................... £11.00",
        "Hennessy V ..................................................... £14.00"
    ],
    "SOFT DRINKS": [
        "Coca Cola / Diet Coke .......................... £2.50",
        "Still / Sparkling Water ......................... £1.50",
        "Tonic / Slimline Tonic ......................... £3.00",
        "Soda ........................................... £1.50",
        "Lemonade ....................................... £2.00"
    ],
    "BAR SNACKS": [
        "Elements Mezze (Chef's Selection) .............. £10.00",
        "Olives & Nuts Selection ........................ £5.50"
    ]
}

# Generate PDF content
for section, content in menu.items():
    divider()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, section, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("Helvetica", "", 12)

    if isinstance(content, dict):  # Subsections (like spirits)
        for sub, items in content.items():
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, f"-- {sub} --", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
            pdf.set_font("Helvetica", "", 12)
            for item in items:
                pdf.cell(0, 8, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
            pdf.ln(3)
    else:
        for item in content:
            pdf.cell(0, 8, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(4)

divider()

# Footer note
pdf.ln(10)
pdf.set_font("Helvetica", "I", 10)
pdf.cell(0, 10, "All prices include VAT. Please ask staff for allergen information.", new_x=XPos.LMARGIN, new_y=YPos.NEXT, 
align="C")

# Save file
output_path = "Elements_Bar_Menu_BlackGold_A4_Final.pdf"
pdf.output(output_path)
print(f"✅ PDF saved as {output_path}")

