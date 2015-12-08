set terminal postscript
set output 'princeton-update.ps'

set tmargin 0
set bmargin 3
set lmargin 5.5
set rmargin 0

set key font "Times-Roman Bold, 30" spacing 5 at 4, 195 maxrows 2 width 15 #right top
set key autotitle columnhead nobox

set boxwidth 0.5 absolute
set style fill  solid 1.00 border lt -1
#set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
#set key invert samplen 4 spacing 1 width 0 height 0
set style histogram rowstacked title textcolor lt -1
set datafile missing '-'
set style data histograms

set xlabel font "Times-Roman Bold, 45" offset -0.5, -2.5
set ylabel "#Rules" font "Times-Roman Bold, 40" offset -1.5, 0
set xtics font "Times-Roman Bold, 30" offset 8, -1
set ytics font "Times-Roman, 25"
set grid ytics
set yrange[0:200]
show grid

#unset xtics

plot 'princeton_update.dat' using 2:xtic(1) linecolor 1 fs pattern 1,\
'' using 3:xtic(1) linecolor 9 fs pattern 3, \
'' using 4:xtic(1) linecolor 7 fs pattern 3, \
'' using 5:xtic(1) linecolor 3 fs pattern 2


#plot newhistogram "ALP_PFX", 'princeton_update.dat' using "PFX_UPDATE":xtic(1) t col, '' u "PFX_OPT" t col, \
#newhistogram "ALP_WC", '' u "WC_UPDATE":xtic(1) t col, '' u "WC_OPT" t col 
