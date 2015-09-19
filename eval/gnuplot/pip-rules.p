set terminal postscript
set output "pip-rules.ps"
set tmargin 0
set bmargin 0
set lmargin 5.5
set rmargin 0

set style data histogram
set style histogram cluster gap 1.5
set style fill solid border rgb "black"

set xlabel font "Times-Roman Bold, 45" offset -0.5, -2.5
set ylabel "#Rules" font "Times-Roman Bold, 40" offset -1.5, 0
set xtics font "Times-Roman Bold, 35" offset 0, -1
set ytics font "Times-Roman, 25"
set grid ytics
set yrange[0:]
show grid


set key font "Times-Roman Bold, 30" spacing 5 right top

plot 'pip_rules.dat' using 2:xtic(1) title col linecolor 1 fs pattern 1, \
'' using 3:xtic(1) title col linecolor 3 fs pattern 2, \
'' using 5:xtic(1) title col linecolor 7 fs pattern 3, \
'' using 7:xtic(1) title col linecolor 9 fs pattern 3
