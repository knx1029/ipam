if [ "$1" == "gen" ]; then
    python gen_input.py gdata/gatech.m_summary s
fi

if [ "$1" == "eval" ]; then
    python gen_input.py gdata/gatech.m_summary e gdata/gatech_dpu_all.ipam > gdata/gatech_dpu.ipam_eq_perf
    python gen_input.py gdata/gatech.m_summary e gdata/gatech_jpu_all.ipam > gdata/gatech_jpu.ipam_eq_perf
fi
