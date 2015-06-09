# lb-load-line
out_p="$1.p"
out_ps="$1.ps"
out_pdf="$1.pdf"
save_option="save"
gnuplot $out_p
ps2pdf $out_ps $out_pdf
open -a Preview $out_pdf