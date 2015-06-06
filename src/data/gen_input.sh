if [ "$1" == "gcat" ]; then
    for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 ; do
	cat $2 >> $3
    done
fi


if [ "$1" == "pcat" ]; then
    for i in 1 2 3 ; do
	for o in sd sdw ; do
	    f1=../algorithm/purdue_all.${o}.ipam
	    f2=../algorithm/purdue_all_all.${o}.ipam
	    cat ${f1} >> ${f2}
	    for mode in mca mce ; do
		f1=../algorithm/${mode}_slack_purdue_all.${o}.ipam
		f2=../algorithm/${mode}_slack_purdue_all_all.${o}.ipam
		cat ${f1} >> ${f2}
	    done
	done
    done
fi

if [ "$1" == "gen" ]; then
    if [ "$2" == "gatech" ]; then
	input=gdata/gatech.m_summary
	echo "dpu weighted"
	python gen_input.py ${input} sdw
	echo "dpu"
	python gen_input.py ${input} sd
	echo "jpu weighted"
	python gen_input.py ${input} sjw
	echo "jpu"
	python gen_input.py ${input} sj
    fi

    if [ "$2" == "gall" ]; then
	input=gatech_all.m_summary
	echo "dpu weighted"
	python gen_input.py ${input} sdw
	echo "dpu"
	python gen_input.py ${input} sd
	echo "jpu weighted"
	python gen_input.py ${input} sjw
	echo "jpu"
	python gen_input.py ${input} sj
    fi

    if [ "$2" == "purdue" ]; then
	input=pdata/purdue.m_summary
	echo "dpu weighted"
	python gen_input.py ${input} sdw
	echo "dpu"
	python gen_input.py ${input} sd
	echo "jpu weighted"
	python gen_input.py ${input} sjw
	echo "jpu"
	python gen_input.py ${input} sj
    fi


    if [ "$2" == "pall" ]; then
	input=purdue_all.m_summary
	echo "dpu weighted"
	python gen_input.py ${input} sdw
	echo "dpu"
	python gen_input.py ${input} sd
#	echo "jpu weighted"
#	python gen_input.py ${input} sjw
#	echo "jpu"
#	python gen_input.py ${input} sj
    fi
fi

if [ "$1" == "eval" ]; then

    if [ "$2" == "gatech" ]; then
	echo "dpu"
	python gen_input.py gdata/gatech.m_summary e gdata/gatech_dpu.ipam > gdata/gatech_dpu.ipam_eq_perf
	echo "dpu weighted"
	python gen_input.py gdata/gatech.m_summary ew gdata/gatech_dpu.ipam > gdata/gatech_dpu.ipam_perf
	echo "jpu"
	python gen_input.py gdata/gatech.m_summary e gdata/gatech_dpu.ipam > gdata/gatech_dpu.ipam_perf
	echo "jpu weighted"
	python gen_input.py gdata/gatech.m_summary ew gdata/gatech_jpu.ipam > gdata/gatech_jpu.ipam_eq_perf
    fi

    if [ "$2" == "gall" ]; then
	input=gatech_all_all.m_summary

	mode=sd
	output=gatech_all_all.${mode}.ipam
	perf_output=gatech_all_all.${mode}.perf.csv
	echo ${mode}
	python gen_input.py ${input} e ../algorithm/${output} > ../algorithm/${perf_output}
	for o in mce mca ; do
	    echo $o
	    python gen_input.py ${input} e ../algorithm/${o}_slack_${output} > ../algorithm/${o}_slack_${perf_output}
	done

	mode=sdw
	output=gatech_all_all.${mode}.ipam
	perf_output=gatech_all_all.${mode}.perf.csv
	echo ${mode}
	python gen_input.py ${input} ew ../algorithm/${output} > ${perf_output}
	for o in mce mca ; do
	    echo ${o}
	    python gen_input.py ${input} ew ../algorithm/${o}_slack_${output} > ../algorithm/${o}_slack_${perf_output}
	done
    fi

    if [ "$2" == "pall" ]; then
	input=purdue_all_all.m_summary

	mode=sd
	output=purdue_all_all.${mode}.ipam
	perf_output=purdue_all_all.${mode}.perf.csv
	echo ${mode}
	python gen_input.py ${input} e ../algorithm/${output} > ../algorithm/${perf_output}
	for o in mce mca ; do
	    echo $o
	    python gen_input.py ${input} e ../algorithm/${o}_slack_${output} > ../algorithm/${o}_slack_${perf_output}
	done

	mode=sdw
	output=purdue_all_all.${mode}.ipam
	perf_output=purdue_all_all.${mode}.perf.csv
	echo ${mode}
	python gen_input.py ${input} ew ../algorithm/${output} > ../algorithm/${perf_output}
	for o in mce mca ; do
	    echo ${o}
	    python gen_input.py ${input} ew ../algorithm/${o}_slack_${output} > ../algorithm/${o}_slack_${perf_output}
	done
    fi

fi
