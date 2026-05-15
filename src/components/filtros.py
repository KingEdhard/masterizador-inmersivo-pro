def construir_filtro(idx_sel, pistas, canales_salida=8):
    """
    Construye el filtro completo (dynaudnorm + firequalizer + pan).
    canales_salida: 6 para 5.1, 8 para 7.1.
    """
    layout_sel = ''
    canales_sel = 2
    for idx, desc, ch_count, ch_layout in pistas:
        if idx == idx_sel:
            layout_sel = ch_layout
            canales_sel = ch_count
            break

    def construir_pan(layout, canales_orig, canales_out):
        """Genera la cadena pan adecuada para el número de canales de salida deseado."""
        if canales_out == 6:  # 5.1
            # Si la fuente ya es 5.1 o superior, usamos los canales reales; si no, mezclamos estéreo
            if '5.1' in (layout or '').lower() or canales_orig >= 6:
                return "pan=5.1|FL=FL|FR=FR|FC=FC|LFE=LFE|BL=BL|BR=BR"
            else:
                # Estéreo u otro → generar centro y LFE desde FL/FR
                return ("pan=5.1|FL=FL|FR=FR|FC=0.5*FL+0.5*FR|"
                        "LFE=0.5*FL+0.5*FR|BL=FL|BR=FR")
        else:  # 7.1 (por defecto)
            if '7.1' in (layout or '').lower() or canales_orig >= 8:
                return ("pan=7.1|FL=FL|FR=FR|FC=FC|LFE=LFE|"
                        "BL=BL|BR=BR|SL=SL|SR=SR")
            elif '5.1' in (layout or '').lower() or canales_orig >= 6:
                return ("pan=7.1|FL=FL|FR=FR|FC=FC|LFE=LFE|"
                        "BL=BL|BR=BR|SL=BL|SR=BR")
            else:
                return ("pan=7.1|FL=FL|FR=FR|FC=0.5*FL+0.5*FR|"
                        "LFE=0.5*FL+0.5*FR|BL=FL|BR=FR|SL=FL|SR=FR")

    pan_map = construir_pan(layout_sel, canales_sel, canales_salida)
    firequal = "firequalizer=gain=if(gte(f\\,400)\\,if(lte(f\\,4000)\\,2\\,0)\\,0)"
    filtro = f"dynaudnorm=f=150:g=31:p=0.95,{firequal},{pan_map}"
    return filtro
