if [ "$1" == "gatech" ]; then
    if [ "$2" == "slack" ]; then
	o=jpu
	echo "add slack"
	python slack.py ../data/gdata/gatech.m_summary.${o} m > slack_gatech.m_summary.${o}
	echo "run ipam"
	python main.py slack_gatech.m_summary.${o} m > slack_gatech_${o}_all.ipam
	echo "gen csv"
	python ../data/gen_input.py ../data/gdata/gatech.m_summary e slack_gatech_${o}_all.ipam > slack_gatech_${o}.ipam_perf.csv
    else    
	echo "empty"
#    echo python ipam.py ../data/gdata/gatech.m_summary.dpu m > ../data/gdata/gatech_dpu_all.ipam
#    python ipam.py ../data/gdata/gatech.m_summary.dpu m > ../data/gdata/gatech_dpu_all.ipam
#    echo python ipam.py ../data/gdata/gatech.m_summary.jpu m > ../data/gdata/gatech_jpu_all.ipam
#    python ipam.py ../data/gdata/gatech.m_summary.jpu m > ../data/gdata/gatech_jpu_all.ipam
     fi

fi

if [ "$1" == "purdue" ]; then
    echo python ipam.py ../data/pdata/purdue.m_summary.dpu m > ../data/pdata/purdue_dpu_all.ipam
    python ipam.py ../data/pdata/purdue.m_summary.dpu m > ../data/pdata/purdue_dpu_all.ipam
    echo python ipam.py ../data/pdata/purdue.m_summary.jpu m > ../data/pdata/purdue_jpu_all.ipam
    python ipam.py ../data/pdata/purdue.m_summary.jpu m > ../data/pdata/purdue_jpu_all.ipam
fi
