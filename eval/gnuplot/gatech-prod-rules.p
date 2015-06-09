set terminal postscript
set output "gatech-prod-rules.ps"
set tmargin 0
set bmargin 3
set lmargin 5.5
set rmargin 0

set style data histogram
set style histogram cluster gap 1.5
set style fill solid border rgb "black"

set xlabel font "Times-Roman Bold, 45" offset -0.5, -2.5
set ylabel "#Rules" font "Times-Roman Bold, 40" offset -0.5, 0
set xtics font "Times-Roman, 20" offset 0, -0.5
set ytics font "Times-Roman, 25"
set grid ytics
show grid


set key font "Times-Roman Bold, 30" spacing 5  at 5, 12000

plot 'gatech_prod_rules.dat' using 2:xtic(1) title col linecolor 1 fs pattern 1, \
'' using 3:xtic(1) title col linecolor 3 fs pattern 2, \
'' using 4:xtic(1) title col linecolor 7 fs pattern 3
