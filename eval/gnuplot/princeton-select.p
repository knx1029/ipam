set terminal postscript
set output "princeton-select.ps"
set tmargin 0
set bmargin 3
set lmargin 5.5
set rmargin 0

set style data histogram
set style histogram cluster gap 2
set style fill solid border rgb "black"

set ylabel "#Rules" font "Times-Roman Bold, 40" offset -1.5, 0
#set y2label "" font "Times-Roman Bold, 40" offset 0, 0
set xtics font "Times-Roman Bold, 25" offset -4,-3 rotate by 20
set ytics font "Times-Roman, 25"
#set y2tics font "Times-Roman, 25" offset -0.5, 0
set yrange[0:]
#set y2range[0:]
set grid ytics
show grid

set linestyle 1 pt 5 ps 2.5 lc 7 lt 1 lw 10
set key font "Times-Roman Bold, 30" spacing 5 right top

plot 'princeton_select.dat' using 3:xtic(5) title col linecolor 9 fs pattern 3, \
'' using 2:xtic(5) title col linecolor 7 fs pattern 3
#'' using 6:4 axes x1y2 title '#Attribute cominations' w linespoints ls 1
