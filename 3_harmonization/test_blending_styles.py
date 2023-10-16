import blending_styles_module as bsm

piece_idx = 0
style_type = 'harmonic'
style_subtype = 'Tonal'

b, s = bsm.blend_piece_with_style( piece_idx, style_type, style_subtype )

print(b)
print(s) # this contains the string to be printed on the browser