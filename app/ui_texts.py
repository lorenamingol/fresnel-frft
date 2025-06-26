INTRO_TEXT = """
Esta aplicación calcula el **patrón de intensidad** de un frente de onda al propagarse a distintas distancias z 
en espacio libre. Para ello, se resuelve de forma numérica la **integral de Fresnel**.

El cálculo se realiza mediante la **Transformada de Fourier Fraccionaria (FrFT)**, implementada según un **sistema de Lohmann tipo II**.

El resultado es una serie de imágenes que muestran cómo evoluciona la distribución de intensidad con la distancia z.
"""

HELP_TEXT = """
1. **Elige una imagen**:
   - Puedes subir tu propia imagen (en escala de grises o RGB).
   - O seleccionar una de las imágenes de ejemplo disponibles.
2. **Selecciona los parámetros físicos** desde el panel lateral.
3. Pulsa **Calcular** para aplicar la transformación.
4. Usa el **control deslizante** para visualizar los resultados.
5. Descarga imágenes o vídeos desde el panel lateral.

⚠️ La imagen de entrada debe ser **cuadrada** (mismo ancho y alto) para que la transformación sea válida.
"""
