import unicodedata

def substituir_invisiveis_por_espaco(texto):
    """
    Trocar caracteres invisiveis por espaço, para que os mesmos não sejam escritos como '?' nos campos de texto

    Args:
    - O texto que terá os invisiveis removidos

    Returns: 
    - O texto formatado
    """
    
    caracteres_invisiveis = set()
    texto_tratado = ''

    for c in texto:
        # Cf = "Other, Format" | Zl = "Line Separator" | Zp = "Paragraph Separator"
        if unicodedata.category(c) in ['Cf', 'Zl', 'Zp']:
            caracteres_invisiveis.add(f'U+{ord(c):04X}')
            texto_tratado += ' '  
        else:
            texto_tratado += c

    return texto_tratado

EQUIVALENTES = {
    '–': '-',     
    '—': '-',    
    '“': '"',
    '”': '"',
    '‘': "'",
    '’': "'",
    '\n':'',
    '´': "'",     
    '•': '-',     
    '…': '...',   
    '\u00A0': ' ',  
}

def normalizar_texto_ascii(texto):
    """
    Trocar caracteres especiais por equivalentes, para que os mesmos não sejam escritos como '?' nos campos de texto

    Args:
    - O texto que terá os invisiveis removidos
    
    Returns: 
    - O texto formatado
    """
    substituidos = set()
    texto_normalizado = ''

    for c in texto:
        if c in EQUIVALENTES:
            texto_normalizado += EQUIVALENTES[c]
            substituidos.add(f"'{c}' → '{EQUIVALENTES[c]}'")
        else:
            texto_normalizado += c

    return texto_normalizado