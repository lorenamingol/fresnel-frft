# Fresnel - FrFT

Esta aplicación calcula el **patrón de intensidad** de un frente de onda al propagarse a distintas distancias z en espacio libre, resolviendo numéricamente la **integral de Fresnel** mediante la **Transformada de Fourier Fraccionaria (FrFT)**, implementada usando un sistema de **Lohmann tipo II**.

---

## ✨ Características

- Soporta imágenes en **escala de grises** y **RGB**
- Permite elegir imágenes de ejemplo o subir las tuyas
- Visualización de la evolución espacial de la intensidad
- Control deslizante para explorar resultados en distintas distancias z
- Descarga de imágenes y vídeos generados
- Interfaz intuitiva construida con Streamlit

---

## 🐍 Requisitos previos

Antes de ejecutar la aplicación, asegúrate de tener instalado:

- **Python 3.8 o superior**  
  Puedes instalarlo desde: https://www.python.org/downloads/  
  
- **pip**, el gestor de paquetes de Python (suele instalarse junto con Python)

- (Opcional) Se recomienda usar un **entorno virtual** para aislar las dependencias.  
  Crea el entorno en la **raíz del proyecto** (donde está la carpeta `app`) con:

```bash
python -m venv venv      # o bien python3 -m venv venv
```

- Luego actívalo:

```bash
source venv/bin/activate   # En Linux/macOS
venv\Scripts\activate      # En Windows
```

---

## 📦 Instalación de dependencias

Desde la **raíz del proyecto** (donde está `requirements.txt`), ejecuta:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cómo lanzar la aplicación

Desde la **raíz del proyecto** (donde está la carpeta `app`), ejecuta el siguiente comando:

```bash
streamlit run app/main.py
```

Esto abrirá la app en tu navegador por defecto, normalmente en:

```
http://localhost:8501
```
