set terminal postscript
set output "princeton-scale.ps"
set tmargin 0
set bmargin 3
set lmargin 6.5
set rmargin 0

set style data histogram
set style histogram cluster gap 1.5
set style fill solid border rgb "black"

#set xlabel "Scale" font "Times-Roman Bold, 40" offset -0.5, -1.5
set xlabel "#Hosts" font "Times-Roman Bold, 40" offset -0.5, -1.5
set ylabel "#Rules" font "Times-Roman Bold, 40" offset -1, 0
set xtics font "Times-Roman Bold, 20" offset 0,-0.5
set ytics font "Times-Roman, 25"
set grid ytics
show grid


set key font "Times-Roman Bold, 30" spacing 5 at 1, 16000

plot 'princeton_scale.dat' using 4:xtic(1) title col linecolor 1 fs pattern 1, \
'' using 2:xtic(1) title col linecolor 7 fs pattern 3, \
'' using 3:xtic(1) title col linecolor 9 fs pattern 3
