if [ "$1" == "gatech" ]; then
    name=gatech
    input=../data/gdata/gatech.m_summary
    if [ "$2" == "slack" ]; then
	for o in sd sdw ; do # sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    for mode in mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_${name}.${o}
		ipam_output=${mode}_slack_${name}.${o}.ipam
		ipam_summary=${mode}_slack_${name}.${o}.perf.csv
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
	for o in sd sdw ; do # sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    ipam_output=${name}.${o}.ipam
	    ipam_summary=${name}.${o}.perf.csv
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
#	for o in sd sdw ; do #sj sjw ; do
	for o in sj sjw; do
	    echo "option=${o}"
	    input=../data/${name}_all.m_summary
	    ipam_input=${input}.${o}
	    ipam_output=${name}_all.${o}.ipam
	    echo "run ipam"
	    python main.py ${ipam_input} mc > ${ipam_output}
	    for mode in mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_${name}_all.${o}
		ipam_output=${mode}_slack_${name}_all.${o}.ipam
		echo "add slack"
		python slack.py ${ipam_input} ${mode} > ${slack_input}
		echo "run ipam"
		python main.py ${slack_input} mc > ${ipam_output}
	    done
	done
     fi
fi

if [ "$1" == "purdue" ]; then
    name=purdue
    input=../data/pdata/${name}.m_summary
    if [ "$2" == "slack" ]; then
	for o in sd sdw ; do #sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    for mode in mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_${name}.${o}
		ipam_output=${mode}_slack_${name}.${o}.ipam
		ipam_summary=${mode}_slack_${name}.${o}.perf.csv
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
	for o in sd sdw ; do #sj sjw ; do
	    echo "option=${o}"
	    ipam_input=${input}.${o}
	    ipam_output=${name}.${o}.ipam
	    ipam_summary=${name}.${o}.perf.csv
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
	for o in sd sdw ; do #sj sjw ; do
	    echo "option=${o}"
	    input=../data/${name}_all.m_summary
	    ipam_input=${input}.${o}
	    ipam_output=${name}_all.${o}.ipam
	    echo "run ipam"
	    python main.py ${ipam_input} mc > ${ipam_output}
	    for mode in mca mce ; do
		echo "mode=${mode}"
		slack_input=${mode}_slack_${name}_all.${o}
		ipam_output=${mode}_slack_${name}_all.${o}.ipam
		echo "add slack"
		python slack.py ${ipam_input} ${mode} > ${slack_input}
		echo "run ipam"
		python main.py ${slack_input} mc > ${ipam_output}
	    done
	done
     fi
fi


if [ "$1" == "princeton" ]; then
    echo "ipam"
    name=princeton_prod
    ipam_input=../data/ptdata/${name}
    ipam_output=${name}.ipam
    python main.py ${ipam_input} mc > ${ipam_output}
    for mode in  mce ; do #mci
	echo "mode=${mode}"
	slack_input=${mode}_slack_${name}
	ipam_output=${mode}_slack_${name}.ipam
	echo "slack"
#	python slack.py ${ipam_input} ${mode} > ${slack_input}
	echo "ipam"
#	python main.py ${slack_input} mc > ${ipam_output}
    done
fi