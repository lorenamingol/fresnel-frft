import numpy as np

def fresnel_frft_square_input(input_field, z, D, l):
    """
    Computes the intensity pattern of the Fresnel Integral
    using the Fractional Fourier Transform (FrFT) in 2D.
    
    Parameters:
    - input_field: 2D square input matrix (image or optical field).
    - z: Propagation distance.
    - D: Physical size of the square input (D = Dx = Dy).
    - l: Wavelength of the light.

    Returns:
    - out: 2D Fresnel intensity pattern.
    """

    N, M = input_field.shape # Image size

    f1 = D**2 / (l * N) # Fresnel sampling parameter

    phi = np.arctan(z / f1) # Fractional rotation angle

    # 2D spatial coordinate indices
    n = np.arange(-N/2, N/2).reshape(-1, 1) 
    m = np.arange(-N/2, N/2).reshape(1, -1) 

    #### Effect of the first lens
    
    # Phase factor of the lens
    factor_L = np.exp(-1j * np.pi * (n**2 + m**2) / N * np.tan(phi / 2))

    out = factor_L * input_field

    #### Propagation effect (near-field approximation)

    # 2D Fourier Transform
    out = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(out)))

    # Fourier Transform of the Fresnel kernel
    ft_kernel = np.exp(-1j * np.pi * (n**2 + m**2) / N * np.sin(phi))

    out = ft_kernel * out

    # Inverse 2D Fourier Transform
    out = np.fft.fftshift(np.fft.ifft2(np.fft.fftshift(out)))

    #### Effect of the second lens

    out = factor_L * out 

    #### Fresnel - Lohmann relation

    # Conversion factor from Lohmann system to Fresnel
    factor_fresnel_lohmann = np.cos(phi) * np.exp(1j * np.pi * np.tan(phi) / N * (n**2 + m**2))

    out = factor_fresnel_lohmann * out

    # Intensity
    out = np.abs(out)**2

    return out

