if [ "$1" == "gatech" ]; then
    input=../data/gdata/gatech.m_summary
    if [ "$2" == "slack" ]; then
	for o in sd sdw sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    for mode in mci mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_gatech.${o}
		ipam_output=${mode}_slack_gatech.${o}.ipam
		ipam_summary=${mode}_slack_gatech.${o}.perf.csv
		echo "add slack"
		python slack.py ${ipam_input} ${mode} > ${slack_input}
		echo "run ipam"
		python main.py ${slack_input} mc > ${ipam_output}
		echo "gen csv"
		if [[ "$o" == "sdw"  ||  "$o" == "sjw" ]]; then
		    python ../data/gen_input.py ${input} ew ${ipam_output} > ${ipam_summary}
		else
		    python ../data/gen_input.py ${input} e ${ipam_output} > ${ipam_summary}
		fi
	    done
	done
    fi
    if [ "$2" == "regular" ]; then
	echo "ipam"
	for o in sd sdw sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    ipam_output=gatech.${o}.ipam
	    ipam_summary=gatech.${o}.perf.csv
	    echo "run ipam"
	    python main.py ${ipam_input} mc > ${ipam_output}
	    echo "gen csv"
	    if [[ "$o" == "sdw"  ||  "$o" == "sjw" ]]; then
		python ../data/gen_input.py ${input} ew ${ipam_output} > ${ipam_summary}
	    else
		python ../data/gen_input.py ${input} e ${ipam_output} > ${ipam_summary}
	    fi
	done
     fi
    if [ "$2" == "all" ]; then
	echo "ipam"
	for o in sd sdw sj sjw ; do
	    echo "option=${o}"
	    input=../data/gatech_one_all.m_summary
	    ipam_input=${input}.${o}
	    ipam_output=gatech_all.${o}.ipam
	    ipam_summary=gatech_all.${o}.perf.csv
	    echo "run ipam"
	    python main.py ${ipam_input} mc > ${ipam_output}
	    for mode in mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_gatech_all.${o}
		ipam_output=${mode}_slack_gatech_all.${o}.ipam
#		ipam_summary=${mode}_slack_gatech.${o}.perf.csv
		echo "add slack"
		python slack.py ${ipam_input} ${mode} > ${slack_input}
		echo "run ipam"
		python main.py ${slack_input} mc > ${ipam_output}
	    done
#	    echo "gen csv"
#	    if [[ "$o" == "sdw"  ||  "$o" == "sjw" ]]; then
#		python ../data/gen_input.py ${input} ew ${ipam_output} > ${ipam_summary}
#	    else
#		python ../data/gen_input.py ${input} e ${ipam_output} > ${ipam_summary}
#	    fi
	done
     fi
fi

if [ "$1" == "purdue" ]; then
    input=../data/pdata/purdue.m_summary
    if [ "$2" == "slack" ]; then
	for o in sd sdw sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    for mode in mci mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_purdue.${o}
		ipam_output=${mode}_slack_purdue.${o}.ipam
		ipam_summary=${mode}_slack_purdue.${o}.perf.csv
		echo "add slack"
		python slack.py ${ipam_input} ${mode} > ${slack_input}
		echo "run ipam"
		python main.py ${slack_input} mc > ${ipam_output}
		echo "gen csv"
		if [[ "$o" == "sdw"  ||  "$o" == "sjw" ]]; then
		    python ../data/gen_input.py ${input} ew ${ipam_output} > ${ipam_summary}
		else
		    python ../data/gen_input.py ${input} e ${ipam_output} > ${ipam_summary}
		fi
	    done
	done
    fi
    if [ "$2" == "regular" ]; then
	echo "ipam"
	for o in sd sdw sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    ipam_output=purdue.${o}.ipam
	    ipam_summary=purdue.${o}.perf.csv
	    echo "run ipam"
	    python main.py ${ipam_input} mc > ${ipam_output}
	    echo "gen csv"
	    if [[ "$o" == "sdw"  ||  "$o" == "sjw" ]]; then
		python ../data/gen_input.py ${input} ew ${ipam_output} > ${ipam_summary}
	    else
		python ../data/gen_input.py ${input} e ${ipam_output} > ${ipam_summary}
	    fi
	done
     fi
fi
