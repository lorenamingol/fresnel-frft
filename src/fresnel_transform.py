import numpy as np


def fresnel_frft_square_input(f, z, D, l):
    """
    Calcula la Integral de Fresnel usando la Transformada de Fresnel Fraccionaria (FRFT) en 2D.
    
    Parámetros:
    - f: Matriz 2D cuadrada de entrada (imagen o campo óptico).
    - z: Distancia de propagación.
    - D: Tamaño físico de la entrada cuadrada (D = Dx = Dy).
    - l: Longitud de onda de la luz.

    Retorna:
    - out: Patrón de Fresnel calculado en 2D.
    """

    # Tamaño de la imagen
    # TO DO: Código actual para imágenes cuadradas
    #        Comprobar si es factible código con N!=M y Dx!=Dy
    N, M = f.shape  

    # Cálculo del parámetro f1 (criterio de muestreo de Fresnel)
    f1 = D**2 / (l * N)

    # Ángulo de rotación fraccionaria
    phi = np.arctan(z / f1)

    # Índices de coordenadas espaciales 2D
    n = np.arange(-N/2, N/2).reshape(-1, 1)  # Dirección X
    m = np.arange(-N/2, N/2).reshape(1, -1)  # Dirección Y


    #### Efecto de la primera lente
    
    # Factor de fase primera lente
    factor_L = np.exp(-1j * np.pi * (n**2 + m**2) / N * np.tan(phi / 2))

    out = factor_L * f

    #### Efecto de la propagación (aproximación campo cercano)

    # Transformada de Fourier 2D
    out = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(out)))

    # Transformada de Fourier del núcleo de Fresnel
    tf_nucleo = np.exp(-1j * np.pi * (n**2 + m**2) / N * np.sin(phi))

    # Multiplicar la transformada de la entrada por la transformada del nucleo
    out = tf_nucleo * out

    # Transformada de Fourier inversa 2D
    out = np.fft.fftshift(np.fft.ifft2(np.fft.fftshift(out)))

    # Factor constante de la integral de Fresnel
    c = D**2 / (l**2 * N) * np.sin(phi)
    factor_cte_fresnel = np.exp(1j * 2 * np.pi * c) / (1j * c)

    out = factor_cte_fresnel * out

    #### Efecto de la segunda lente

    out = factor_L * out 

    #### Relación Fresnel - Sistema Lohmann

    # Factor para pasar de Lohmann a Fresnel
    factor_fresnel_lohmann = np.cos(phi) * np.exp(1j * np.pi * np.tan(phi) / N * (n**2 + m**2))

    out = factor_fresnel_lohmann * out

    # Intensidad
    out = np.abs(out)**2

    return out

