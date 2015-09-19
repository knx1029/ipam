set terminal postscript
set output "princeton-bits.ps"
set tmargin 0
set bmargin 3
set lmargin 5.5
set rmargin 0

set style data histogram
set style histogram cluster gap 2
set style fill solid border rgb "black"

set xlabel "#Dimensions" font "Times-Roman Bold, 40" offset -0.5, -1.5
set ylabel "#Bits" font "Times-Roman Bold, 40" offset -1.5, 0
set xtics font "Times-Roman Bold, 35" offset 0,-0.5
set ytics font "Times-Roman, 25"
set yrange[0:30]
set grid ytics
show grid


set key font "Times-Roman Bold, 30" spacing 5 at 4.5, 29.5 width 2 maxrows 3

#plot 'princeton_bits.dat' using 2:xtic(1) title col linecolor 3 fs pattern 2, \
#'' using 5:xtic(1) title col linecolor 1 fs pattern 1, \
#'' using 6:xtic(1) title col linecolor 4 fs pattern 7, \
#'' using 4:xtic(1) title col linecolor 7 fs pattern 3, \
#'' using 3:xtic(1) title col linecolor 9 fs pattern 3

plot 'princeton_bits.dat' using 4:xtic(1) title col linecolor 1 fs pattern 1, \
'' using 2:xtic(1) title col linecolor 3 fs pattern 2, \
'' using 3:xtic(1) title col linecolor 7 fs pattern 3
