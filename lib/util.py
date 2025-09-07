import secrets

def is_dark(rgb: str) -> bool:
    """
    Determines if a hex RGB color is dark or light.
    
    Args:
        rgb (str): A hex color string like "#123456" or "123456".
    
    Returns:
        bool: True if the color is dark, False if light.
    """
    rgb = rgb.lstrip('#')
    if len(rgb) != 6:
        raise ValueError("Invalid RGB format. Expected 6 hex digits.")

    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)

    # Perceived luminance formula (ITU-R BT.709)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    return luminance < 128

def color_variant(rgb: str, percent: float = 10) -> str:
    """
    Adjusts brightness of a hex color by a percentage.
    Lightens if dark, darkens if light.
    
    Args:
        rgb (str): Hex color string like "#123456" or "123456".
        percent (float): Percentage to adjust brightness.
    
    Returns:
        str: New hex color string.
    """
    rgb = rgb.lstrip('#')
    if len(rgb) != 6:
        raise ValueError("Invalid RGB format. Expected 6 hex digits.")

    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)

    def adjust(value, lighten):
        factor = percent / 100
        if lighten:
            return min(int(value + (255 - value) * factor), 255)
        else:
            return max(int(value * (1 - factor)), 0)

    lighten = is_dark(rgb)
    r_new = adjust(r, lighten)
    g_new = adjust(g, lighten)
    b_new = adjust(b, lighten)

    return "#{:02x}{:02x}{:02x}".format(r_new, g_new, b_new)

def rand_token():
    import secrets
    hex_string = secrets.token_hex(32)  # 32 bytes × 2 hex chars = 64 characters
    return(hex_string[0:32])

def print_random_tokens():
    import secrets
    for i in range(20):
        hex_string = str(secrets.token_hex(32))[0:32]
        print(hex_string)

if __name__ == '__main__':
    print_random_tokens()
