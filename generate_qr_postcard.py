from PIL import Image, ImageDraw, ImageFont
import qrcode

# === SETTINGS ===
url = "https://elements-by-chef-sultan.onrender.com/static/Bar_Menu.pdf"
logo_path = "logo.PNG"
output_path = "QR_Bar_Menu_PostCard_Size.png"

# === QR CODE CREATION ===
qr = qrcode.QRCode(
    version=4,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=2,
)
qr.add_data(url)
qr.make(fit=True)

# Gold on black
qr_img = qr.make_image(fill_color="gold", back_color="black").convert("RGB")

# === EMBED LOGO ===
logo = Image.open(logo_path)
qr_width, qr_height = qr_img.size
logo_size = int(qr_width * 0.25)
logo = logo.resize((logo_size, logo_size))
pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

# === ADD TEXT BELOW ===
text = "Scan for Bar Menu"
font_size = 22
font_color = (212, 175, 55)
try:
    font = ImageFont.truetype("Arial.ttf", font_size)
except:
    font = ImageFont.load_default()

# Postcard size canvas (A6 ~ 148x105mm → 1748x1240px at 300dpi)
canvas_width, canvas_height = 1240, 1748
canvas = Image.new("RGB", (canvas_width, canvas_height), "black")

# Center QR
qr_resized = qr_img.resize((700, 700))
qr_x = (canvas_width - qr_resized.width) // 2
qr_y = 500
canvas.paste(qr_resized, (qr_x, qr_y))

# Add logo at top
logo_top = logo.resize((200, 200))
logo_x = (canvas_width - logo_top.width) // 2
canvas.paste(logo_top, (logo_x, 150), mask=logo_top if logo_top.mode == "RGBA" else None)

# Add text
draw = ImageDraw.Draw(canvas)
text_width = draw.textlength(text, font=font)
draw.text(((canvas_width - text_width) / 2, qr_y + qr_resized.height + 30), text, fill=font_color, font=font)

# === SAVE FINAL FILE ===
canvas.save(output_path)
print(f"✅ QR postcard saved as {output_path}")

