import streamlit as st
from fpdf import FPDF
from io import BytesIO
from tempfile import NamedTemporaryFile
from PIL import Image
from google import genai

# Inicializar cliente Gemini usando la API key del entorno
client = genai.Client()

# ---------------- FUNCIONES ----------------
def generar_texto(titulo):
    """Genera historia con Gemini a partir de un título"""
    prompt = f"Escribe una historia creativa basada en el título: '{titulo}'."
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    return resp.text


def generar_pdf(titulo, pages_data, fuente, tamano, hoja):
    """Genera PDF con título en la primera página + texto e imágenes"""
    pdf = FPDF(format=hoja)
    font_map = {'Helvetica': 'helvetica', 'Times': 'times', 'Courier': 'courier'}

    for i, page in enumerate(pages_data):
        pdf.add_page()
        pdf.set_font(font_map.get(fuente, 'helvetica'), size=tamano)

        x = pdf.l_margin
        y = pdf.t_margin

        # En la primera página poner título arriba
        if i == 0:
            pdf.set_font(font_map.get(fuente, 'helvetica'), 'B', size=tamano + 4)
            pdf.cell(0, 10, titulo, ln=True, align="C")
            pdf.ln(10)  # salto de línea
            pdf.set_font(font_map.get(fuente, 'helvetica'), size=tamano)
            y = pdf.get_y()

        # Imagen si existe
        if page.get('imagen'):
            img = Image.open(BytesIO(page['imagen']))
            max_width = pdf.w - 2*pdf.l_margin
            with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                img.save(tmp.name, format="PNG")
                tmp_path = tmp.name
            pdf.image(tmp_path, x=x, y=y, w=max_width)
            orig_w, orig_h = img.size
            img_height_mm = orig_h * max_width / orig_w
            y = y + img_height_mm + 10
            pdf.set_xy(x, y)

        # Texto si existe
        if page.get('texto'):
            pdf.multi_cell(0, tamano * 0.5 + 2, page['texto'])

    return bytes(pdf.output(dest="S"))


# ---------------- INTERFAZ ----------------
st.set_page_config(page_title="Generador de PDF con Gemini", layout="centered")
st.title("Generador de PDF con Texto e Imágenes")

# Configuración básica en la misma página
titulo = st.text_input("Título del PDF")
num_pages = st.number_input("Número de páginas", min_value=1, max_value=10, value=1)
tamano = st.slider("Tamaño de texto", 8, 36, 12)
fuente = st.selectbox("Fuente", ["Helvetica", "Times", "Courier"])
hoja = st.radio("Tamaño de hoja", ["A4", "Letter"])

# Inicializar estado
if "pages_data" not in st.session_state:
    st.session_state.pages_data = [{"texto": "", "imagen": None} for _ in range(num_pages)]

# Ajustar tamaño si cambia
if len(st.session_state.pages_data) != num_pages:
    st.session_state.pages_data = [{"texto": "", "imagen": None} for _ in range(num_pages)]

# Formulario por página
for i in range(num_pages):
    st.subheader(f"Página {i+1}")

    # Botón para generar texto con IA
    if st.button(f"Generar historia con Gemini (página {i+1})"):
        generado = generar_texto(titulo)
        st.session_state.pages_data[i]["texto"] = generado
        st.rerun()

    # Entrada manual de texto (se puede combinar con IA)
    texto_manual = st.text_area(
        f"Texto de la página {i+1}",
        value=st.session_state.pages_data[i]["texto"],
        key=f"text_{i}"
    )
    st.session_state.pages_data[i]["texto"] = texto_manual

    # Subir imagen
    archivo = st.file_uploader(f"Subir imagen para la página {i+1}", type=["png", "jpg", "jpeg"], key=f"img_{i}")
    if archivo:
        st.session_state.pages_data[i]["imagen"] = archivo.read()

    # Vista previa
    if st.session_state.pages_data[i]["imagen"]:
        st.image(st.session_state.pages_data[i]["imagen"], caption=f"Vista previa página {i+1}", use_column_width=True)

st.markdown("---")

# Botón final para PDF
if st.button("Generar PDF"):
    if not titulo:
        st.error("Debes ingresar un título antes de generar el PDF.")
    else:
        pdf_bytes = generar_pdf(titulo, st.session_state.pages_data, fuente, tamano, hoja)
        st.download_button("Descargar PDF", data=pdf_bytes, file_name="documento.pdf", mime="application/pdf")
