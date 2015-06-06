if [ "$1" == "cat_gatech" ]; then
    rm gatech.all
    for f in ../../../QoS/GaTechAcl/*
    do
	echo $f >> gatech.all
	cat $f >> gatech.all
    done
fi

if [ "$1" == "gatech_s" ]; then
    echo "" > gatech.m_summary
    for f in  ../../../QoS/GaTechAcl/*
    do
	echo $f >> gatech.m_summary
	python policy_unit.py $f m g >> gatech.m_summary
    done
fi

if [ "$1" == "gatech_m" ]; then
    f=gatech.all
    echo "" >  gatech_all.m_summary_
    python policy_unit.py $f am g >> gatech.all_m_summary_
fi


if [ "$1" == "cat_purdue" ]; then
    rm purdue.all
    for f in ../../../QoS/PurdueAcl/configs/config*
    do
	echo $f >> purdue.all
	cat $f >> purdue.all
    done
fi

if [ "$1" == "purdue" ]; then
    for f in  ../../../QoS/PurdueAcl/configs/config*
    do
	echo "config $f" >> purdue.m_summary
	python policy_unit.py $f m p >> purdue.m_summary
    done

fi

if [ "$1" == "purdue_m" ]; then
    f=purdue.all
    echo "" > purdue_all.m_summary_
    python policy_unit.py $f am p >> purdue_all.m_summary_
fi