import streamlit as st
from PIL import Image
from src.image_utils import array_to_image_bytes, load_image_auto_channels
import os
import glob


def clear_previous_results():
    for key in ['gray_outs', 'rgb_outs', 'r_outs', 'g_outs', 'b_outs', 'z_vals']:
        st.session_state.pop(key, None)

def crop_center_square(img):
    h, w = img.shape[:2]
    min_dim = min(h, w)
    top = (h - min_dim) // 2
    left = (w - min_dim) // 2
    return img[top:top + min_dim, left:left + min_dim]

def get_physical_parameters_range():
    with st.sidebar.expander("⚙️ Parámetros físicos", expanded=False):
        z_min = st.number_input("Distancia z mínima (m)", min_value=0.01, max_value=1.0, value=0.1, step=0.1)
        z_max = st.number_input("Distancia z máxima (m)", min_value=z_min + 0.01, max_value=10.0, value=1.0, step=0.1)
        z_step = st.number_input("Paso (m)", min_value=0.01, max_value=1.0, value=0.1, step=0.05)
        D = st.number_input("Tamaño lateral D (m)", min_value=1e-4, max_value=0.1, value=1e-2, step=1e-4)
        apply_clicked = st.button("🖥️ Calcular", key="apply")
    return z_min, z_max, z_step, D, apply_clicked


def handle_uploaded_image():
    uploaded_file = st.file_uploader("📁 Sube una imagen (RGB / Escala de grises)", type=["png", "jpg", "jpeg", "bmp"], key="upload")

    if uploaded_file is None and "last_image_name" in st.session_state:
        clear_previous_results()
        st.session_state.pop("last_image_name", None)
        st.session_state.pop("mode", None)
        st.session_state.pop("data", None)
        st.rerun()

    if uploaded_file is not None:
        if "last_image_name" not in st.session_state or uploaded_file.name != st.session_state["last_image_name"]:
            clear_previous_results()
            st.session_state["last_image_name"] = uploaded_file.name

        try:
            img = Image.open(uploaded_file)
            if img.mode not in ["RGB", "L"]:
                st.error("❌ La imagen debe estar en formato RGB o en escala de grises.")
                return None, None

            mode, data = load_image_auto_channels(uploaded_file)
            st.session_state["mode"] = mode
            st.session_state["data"] = data
            return mode, data
        except Exception as e:
            st.error(f"❌ Error al procesar la imagen: {e}")
            return None, None

    elif "mode" in st.session_state and "data" in st.session_state:
        return st.session_state["mode"], st.session_state["data"]

    return None, None


def handle_example_image_selection():
    nombres_traducidos = {
        "circle.png": "Círculo",
        "double_slit.png": "Doble rendija",
        "grating.png": "Rejilla",
        "mixed_figures_colors.png": "Figuras coloreadas",
        "slit.png": "Rendija",
        "square_rgb.png": "Cuadrado RGB",
        "square.png": "Cuadrado",
        "star.png": "Estrella",
        "triangle.png": "Triángulo",
    }

    imagenes_ejemplo = [os.path.basename(f) for f in glob.glob("assets/*.png")]
    if not imagenes_ejemplo:
        st.warning("⚠️ No se encontraron imágenes de ejemplo.")
        return None, None

    opciones_mostradas = ["-- Selecciona una imagen --"] + [nombres_traducidos.get(nombre, nombre) for nombre in imagenes_ejemplo]

    seleccion_mostrada = st.selectbox("📂 Elige una imagen de ejemplo:", opciones_mostradas)

    if seleccion_mostrada == "-- Selecciona una imagen --":
        return None, None

    idx = opciones_mostradas.index(seleccion_mostrada) - 1  
    path_ejemplo = os.path.join("assets", imagenes_ejemplo[idx])
    if "last_image_name" not in st.session_state or path_ejemplo != st.session_state["last_image_name"]:
        clear_previous_results()
        st.session_state["last_image_name"] = path_ejemplo
    return load_image_auto_channels(path_ejemplo)


def render_image_section(title, image_array, filename):
    if "(" in title and ")" in title:
        main, extra = title.split("(", 1)
        line1 = main.strip()
        line2 = f"({extra.strip()}"
    else:
        line1 = title
        line2 = ""

    cols = st.columns([0.12, 0.88])

    with cols[0]:
        st.download_button(
            label="⬇️",
            data=array_to_image_bytes(image_array),
            file_name=filename,
            mime="image/png",
            key=filename,
            help="Descargar imagen"
        )

    with cols[1]:
        st.markdown(f"{line1}  \n{line2}")

    st.image(image_array, clamp=True)


def select_video_channel(options):
    return st.selectbox("Canal", options)

def choose_fps():
    return st.number_input("FPS (fotogramas por segundo)", 1, 60, value=5)

def render_video_download_button(file_path, nombre):
    with open(file_path, "rb") as f:
        st.download_button(
            label="⬇️ Descargar vídeo",
            data=f,
            file_name=f"{nombre.lower()}.mp4",
            mime="video/mp4"
        )
