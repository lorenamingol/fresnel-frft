from io import BytesIO
import os
import zipfile
import streamlit as st
import numpy as np
from app.ui_helpers import render_image_section, crop_center_square, select_video_channel, choose_fps, render_video_download_button
from src.image_utils import array_to_image_bytes, recombine_rgb_channels
from src.video_utils import generate_video_from_arrays
from concurrent.futures import ProcessPoolExecutor, as_completed


def _run_fresnel_grayscale(args):
    img, z, D = args
    from src.fresnel_transform import fresnel_frft_square_input
    from src.image_utils import normalize_result
    return normalize_result(fresnel_frft_square_input(img, z, D, 530e-9))

def compute_grayscale_outputs(img, z_vals, D):
    futures = []
    outs = [None] * len(z_vals)

    with ProcessPoolExecutor() as executor:
        for i, z in enumerate(z_vals):
            future = executor.submit(_run_fresnel_grayscale, (img, z, D))
            futures.append((i, future))

        progress_bar = st.progress(0, text="Calculando escala de Grises...")
        completadas = 0
        total = len(z_vals)

        for f in as_completed([f for _, f in futures]):
            idx = next(i for i, fut in futures if fut == f)
            outs[idx] = f.result()
            completadas += 1
            progress_bar.progress(completadas / total, text=f"Grises: {completadas}/{total}")

    return outs


def _run_fresnel_rgb(args):
    channel, z, D, wl = args
    from src.fresnel_transform import fresnel_frft_square_input
    from src.image_utils import normalize_result
    return normalize_result(fresnel_frft_square_input(channel, z, D, wl))

def compute_rgb_outputs(r, g, b, z_vals, D):
    def compute_channel(channel, wl, label):
        futures = []
        outs = [None] * len(z_vals)

        with ProcessPoolExecutor() as executor:
            for i, z in enumerate(z_vals):
                future = executor.submit(_run_fresnel_rgb, (channel, z, D, wl))
                futures.append((i, future))

            progress_bar = st.progress(0, text=f"Calculando canal {label}...")
            completadas = 0
            total = len(z_vals)

            for f in as_completed([f for _, f in futures]):
                idx = next(i for i, fut in futures if fut == f)
                outs[idx] = f.result()
                completadas += 1
                progress_bar.progress(completadas / total, text=f"Canal {label}: {completadas}/{total}")

        return outs

    r_outs = compute_channel(r, 560e-9, "Rojo")
    g_outs = compute_channel(g, 530e-9, "Verde")
    b_outs = compute_channel(b, 430e-9, "Azul")

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
        render_image_section(
            titulo_izq,
            original,
            f"{key_prefix.lower()}_original.png"
        )
    with col2:
        if outs is not None and idx < len(outs):
            z_val_str = str(z_vals[idx]).replace(".", "-")
            file_name = f"{key_prefix.lower()}_resultado_z_{z_val_str}.png"
            render_image_section(
                titulo_der,
                outs[idx],
                file_name
            )

    st.markdown("<br>", unsafe_allow_html=True)


def process_grayscale_mode(img, z_vals, D, apply_button, idx):
    crop_center_square(img)
    if apply_button:
        st.session_state['gray_outs'] = compute_grayscale_outputs(img, z_vals, D)

    display_image_pair_at_z("Imagen en escala de grises", img, st.session_state.get('gray_outs'), z_vals, "grises", idx)


def process_rgb_mode(data, z_vals, D, apply_button, idx):
    r, g, b = data
    r = crop_center_square(r)
    g = crop_center_square(g)
    b = crop_center_square(b)

    if apply_button:
        st.session_state.update(compute_rgb_outputs(r, g, b, z_vals, D))

    rgb_img = (recombine_rgb_channels(r, g, b) * 255).astype(np.uint8)
    st.session_state['rgb_original'] = rgb_img

    display_image_pair_at_z("Imagen RGB", rgb_img, st.session_state.get('rgb_outs'), z_vals, "rgb", idx)

    for nombre, canal, key_prefix in [('Rojo', r, 'rojo'), ('Verde', g, 'verde'), ('Azul', b, 'azul')]:
        key_lookup = {"rojo": "r_outs", "verde": "g_outs", "azul": "b_outs"}
        outs = st.session_state.get(key_lookup[key_prefix])
        display_image_pair_at_z(nombre, canal, outs, z_vals, key_prefix, idx)

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

    canal = st.selectbox("Canal", disponibles if disponibles else list(canales.keys()), key="image_channel")
    z = st.select_slider("Selecciona z", options=z_vals, format_func=lambda z: f"{z:.3f} m", key="z_selector_img")
    idx = z_vals.index(z)

    key_data = canales.get(canal)
    outs = st.session_state.get(key_data)

    if outs and idx < len(outs):
        img = outs[idx]
    else:
        img = None

    if img is not None:
        z_val_str = str(z).replace(".", "-")
        nombre = f"{canal.lower()}_z_{z_val_str}.png"
        st.download_button(
            "⬇️ Descargar imagen",
            data=array_to_image_bytes(img),
            file_name=nombre,
            mime="image/png",
            key=nombre
        )
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

    if st.button("🎞️ Generar vídeo"):
        ruta = generate_video_from_arrays(outs, fps, z_vals=z_vals)
        render_video_download_button(ruta, canal)

def process_zip_export():
    def create_channel_zip(channel_name, key, z_vals):
        outs = st.session_state.get(key)
        if not outs or not z_vals:
            return None

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for i, img in enumerate(outs):
                img_bytes = array_to_image_bytes(img).getvalue()
                z_val = z_vals[i]
                z_label = f"z_{str(z_val).replace('.', '-')}"
                filename = f"{z_label}.png"
                zipf.writestr(filename, img_bytes)

        zip_buffer.seek(0)
        return zip_buffer

    canales = {
        "Grises": "gray_outs",
        "RGB": "rgb_outs",
        "Rojo": "r_outs",
        "Verde": "g_outs",
        "Azul": "b_outs"
    }

    disponibles = [nombre for nombre, key in canales.items() if key in st.session_state]
    z_vals = st.session_state.get("z_vals", [])

    canal_elegido = st.selectbox("Canal", disponibles, key="zip_channel_select")

    if st.button("🗃️ Generar ZIP", key="zip_generate_button"):
        key_interno = canales[canal_elegido]
        st.session_state["zip_buffer"] = create_channel_zip(canal_elegido, key_interno, z_vals)
        st.session_state["zip_ready"] = True

    if st.session_state.get("zip_ready") and "zip_buffer" in st.session_state:
        st.download_button(
            "⬇️ Descargar ZIP",
            data=st.session_state["zip_buffer"],
            file_name=f"{canal_elegido.lower()}.zip",
            mime="application/zip",
            key="zip_download_button"
        )
        st.session_state.pop("zip_ready")
        st.session_state.pop("zip_buffer")




    