# basic printing of chart string in ugly ascii format
s = "style~Swing,tempo~180,tonality~Bb,bar~4/4,chord~Bb7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~Ebm7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~EbmΔ7@0.0,bar~4/4,chord~Gb @0.0,bar~4/4,chord~Go7@0.0,bar~4/4,chord~Cø7@0.0,bar~4/4,chord~F13#11@0.0,end"
def print_ascii_chart(s):
    # initialise chart
    chart_out = ''
    comma_split = s.split(',')
    i = 0
    bar_counter = 0
    while comma_split[i] != 'end' or i < len(comma_split):
        c = comma_split[i]
        if 'style' in c or 'tempo' in c or 'tonality' in c or 'section' in c:
            chart_out += c + '\n'
            i += 1
            if i >= len(comma_split):
                break
        elif 'bar' in c:
            if bar_counter == 4:
                chart_out += '|\n'
                bar_counter = 0
            bar_counter += 1
            tilde_split = c.split('~')
            chart_out += '|' + tilde_split[1] + ' '*3
            i += 1
            if i >= len(comma_split):
                break
            c = comma_split[i]
            bar_spaces = 20 # 10 per chord - 4 chords max
            bar_chord_symbols = []
            bar_chord_times = []
            # gather chords
            while 'chord' in c and i <len(comma_split):
                tilde_split = c.split('~')
                at_split = tilde_split[1].split('@')
                bar_chord_symbols.append(at_split[0])
                bar_chord_times.append(float(at_split[1]))
                i += 1
                if i >= len(comma_split):
                    break
                c = comma_split[i]
            # build bar
            for chord_symbol in bar_chord_symbols:
                chart_out += chord_symbol + (10 - len(chord_symbol))*' '
                bar_spaces -= 10
            chart_out += ' '*bar_spaces
        else:
            i += 1
            if i >= len(comma_split):
                break
    chart_out += '|'
    return chart_out
# end print_ascii_chart

# chart_out = print_ascii_chart(s)
# print(chart_out)