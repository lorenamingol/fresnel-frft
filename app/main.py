import sys
import os
import streamlit as st
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ui_helpers import (
    get_physical_parameters_range,
    handle_uploaded_image,
    handle_example_image_selection,
    clear_previous_results,
)
from app.processing_flows import (
    process_grayscale_mode,
    process_rgb_mode,
    process_image_export,
    process_video_export,
    process_zip_export
)
from app.ui_texts import INTRO_TEXT, HELP_TEXT

st.set_page_config(
    page_title="Fresnel - FrFT",
    page_icon="💡",
    layout="wide"
)

st.title("Patrón de Intensidad de un Frente de Onda")

tab1, tab2 = st.tabs(["📘 Inicio", "🖥️ Simulación"])

with tab1:
    with st.expander("ℹ️ ¿Qué hace este programa?", expanded=True):
        st.markdown(INTRO_TEXT)

    with st.expander("🧭 ¿Cómo se usa?", expanded=True):
        st.markdown(HELP_TEXT)

with tab2:
    z_min, z_max, z_step, D, apply_clicked = get_physical_parameters_range()
    current_params = (z_min, z_max, z_step, D)
    if st.session_state.get("last_params") != current_params:
        clear_previous_results()
        st.session_state["last_params"] = current_params

    num_z = int(round((z_max - z_min) / z_step)) + 1
    z_vals = np.linspace(z_min, z_max, num_z).tolist()
    st.session_state["z_vals"] = z_vals

    st.markdown("## 🖼️ Selección de Imagen")
    with st.container():
        image_option = st.radio("Elige una opción:", ["Subir imagen", "Usar imagen de ejemplo"])
        mode, data = handle_uploaded_image() if image_option == "Subir imagen" else handle_example_image_selection()


    if data is not None:
        results_ready = (
            (mode == 'L' and 'gray_outs' in st.session_state)
            or (mode == 'RGB' and 'rgb_outs' in st.session_state)
        )

        st.markdown("## 🔍 Imagen original y resultados")

        if (
            data is not None
            and not (
                ('gray_outs' in st.session_state)
                or ('rgb_outs' in st.session_state)
            )
            and not apply_clicked
        ):
            st.info("ℹ️ Selecciona los **Parámetros físicos** en el panel izquierdo y pulsa **Calcular** para visualizar los resultados.")

        z_actual = st.select_slider(
            "Selecciona z",
            options=z_vals,
            format_func=lambda z: f"{z:.3f} m",
            disabled=not results_ready
        )
        slider_idx = z_vals.index(z_actual if results_ready else z_vals[0])
        st.session_state["z_actual"] = z_actual

        if apply_clicked:
            if mode == 'L':
                process_grayscale_mode(data[0], z_vals, D, True, slider_idx)
            elif mode == 'RGB':
                process_rgb_mode(data, z_vals, D, True, slider_idx)
            st.rerun()

        if mode == 'L':
            process_grayscale_mode(data[0], z_vals, D, False, slider_idx)
        elif mode == 'RGB':
            process_rgb_mode(data, z_vals, D, False, slider_idx)


    with st.sidebar.expander("🖼️ Descargar imagen"):
        if any(k in st.session_state for k in ["gray_outs", "rgb_outs", "r_outs", "g_outs", "b_outs"]):
            process_image_export()
        else:
            st.info("⚠️ No hay resultados disponibles para descargar imágenes.")
    
    with st.sidebar.expander("📦 Descargar ZIP"):
        if any(k in st.session_state for k in ["gray_outs", "rgb_outs", "r_outs", "g_outs", "b_outs"]):
            process_zip_export()
        else:
            st.info("⚠️ No hay resultados disponibles para descargar ZIP.")
    
    with st.sidebar.expander("🎬 Descargar vídeo"):
        if any(k in st.session_state for k in ["gray_outs", "rgb_outs", "r_outs", "g_outs", "b_outs"]):
            process_video_export()
        else:
            st.info("⚠️ No hay resultados disponibles para descargar vídeo.")


