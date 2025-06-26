import streamlit as st
import numpy as np
from app.ui_helpers import render_image_section, check_square_image, select_video_channel, choose_fps, render_video_download_button
from src.image_utils import array_to_image_bytes, normalize_result, recombine_rgb_channels
from src.fresnel_transform import fresnel_frft_square_input
from src.video_utils import generate_video_from_arrays


def compute_grayscale_outputs(img, z_vals, D):
    return [normalize_result(fresnel_frft_square_input(img, z, D, 530e-9)) for z in z_vals]


def compute_rgb_outputs(r, g, b, z_vals, D):
    def channel(c, wl):
        return [normalize_result(fresnel_frft_square_input(c, z, D, wl)) for z in z_vals]

    r_outs = channel(r, 560e-9)
    g_outs = channel(g, 530e-9)
    b_outs = channel(b, 430e-9)

    rgb_outs = [
        (np.stack([r_outs[i], g_outs[i], b_outs[i]], axis=-1) * 255).astype(np.uint8)
        for i in range(len(z_vals))
    ]

    return {
        'r_outs': r_outs,
        'g_outs': g_outs,
        'b_outs': b_outs,
        'rgb_outs': rgb_outs,
    }



def display_image_pair_at_z(label, original, outs, z_vals, key_prefix, idx):
    col1, col2 = st.columns(2)

    if label.startswith("Imagen") or label.startswith("Escala"):
        titulo_izq = f"{label} (original)"
        titulo_der = f"{label} (z = {z_vals[idx]:.3f} m)"
    else:
        titulo_izq = f"Canal {label} (original)"
        titulo_der = f"Canal {label} (z = {z_vals[idx]:.3f} m)"

    with col1:
        render_image_section(titulo_izq, original, f"{key_prefix}_original.png")
    with col2:
        if outs is not None and idx < len(outs):
            render_image_section(
                titulo_der,
                outs[idx],
                f"{key_prefix}_transformed_{idx}.png"
            )

    # Añadir separación al final de cada par
    st.markdown("<br>", unsafe_allow_html=True)






def process_grayscale_mode(img, z_vals, D, apply_button, idx):
    if not check_square_image(img):
        return
    if apply_button:
        st.session_state['gray_outs'] = compute_grayscale_outputs(img, z_vals, D)

    display_image_pair_at_z("Imagen en escala de grises", img, st.session_state.get('gray_outs'), z_vals, "gray", idx)


def process_rgb_mode(data, z_vals, D, apply_button, idx):
    r, g, b = data
    if not check_square_image(r, "la imagen RGB"):
        return

    if apply_button:
        st.session_state.update(compute_rgb_outputs(r, g, b, z_vals, D))

    rgb_img = (recombine_rgb_channels(r, g, b) * 255).astype(np.uint8)
    st.session_state['rgb_original'] = rgb_img

    display_image_pair_at_z("Imagen RGB", rgb_img, st.session_state.get('rgb_outs'), z_vals, "rgb", idx)

    for nombre, canal, key in [('Rojo', r, 'r'), ('Verde', g, 'g'), ('Azul', b, 'b')]:
        outs = st.session_state.get(f"{key}_outs")
        display_image_pair_at_z(nombre, canal, outs, z_vals, key, idx)


def process_image_export():
    canales = {
        "Grises": "gray_outs",
        "RGB": "rgb_outs",
        "Rojo": "r_outs",
        "Verde": "g_outs",
        "Azul": "b_outs"
    }

    disponibles = [nombre for nombre, key in canales.items() if key in st.session_state]
    z_vals = st.session_state.get("z_vals", [])

    if not z_vals:
        st.info("⚠️ No hay valores de z disponibles.")
        return

    # Mostrar aunque no haya resultados disponibles todavía
    canal = st.selectbox("Canal:", disponibles if disponibles else list(canales.keys()), key="image_channel")
    z = st.select_slider("Selecciona z", options=z_vals, format_func=lambda z: f"{z:.3f} m", key="z_selector_img")
    idx = z_vals.index(z)

    key_data = canales.get(canal)
    outs = st.session_state.get(key_data)

    # Solo si hay resultados en ese canal
    if canal == "RGB" and idx == 0 and "rgb_original" in st.session_state:
        img = st.session_state["rgb_original"]
    elif outs and idx < len(outs):
        img = outs[idx]
    else:
        img = None

    if img is not None:
        nombre = f"{canal.lower()}_z_{idx}.png"
        st.download_button("⬇️ Descargar imagen", data=array_to_image_bytes(img), file_name=nombre, mime="image/png", key=nombre)
    else:
        st.warning("⚠️ No hay datos disponibles para este canal.")

def process_video_export():
    canales = {
        "Grises": "gray_outs",
        "RGB": "rgb_outs",
        "Rojo": "r_outs",
        "Verde": "g_outs",
        "Azul": "b_outs"
    }

    disponibles = [nombre for nombre, key in canales.items() if key in st.session_state]
    z_vals = st.session_state.get("z_vals", [])

    if not disponibles or not z_vals:
        st.sidebar.info("⚠️ No hay resultados para exportar como vídeo.")
        return

    canal = select_video_channel(disponibles)
    fps = choose_fps()
    key = canales[canal]
    outs = st.session_state.get(key)

    if outs:
        duracion = len(outs) / fps
        st.caption(f"Duración estimada: {duracion:.2f} segundos")

    if st.button("🎬 Generar vídeo"):
        ruta = generate_video_from_arrays(outs, fps, z_vals=z_vals)
        render_video_download_button(ruta, canal)


    