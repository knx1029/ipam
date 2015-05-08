if [ "$1" == "gatech" ]; then
    echo "" > gatech.m_summary
    for f in  ../../../QoS/GaTechAcl/*
    do
	echo $f >> gatech.m_summary
#       python Acl2Attr.py $f s > ${f}_s.summary
#       python Acl2Attr.py $f d > ${f}_d.summary
#	python policy_unit.py $f s g > ${f}_unit_s.summary
	python policy_unit.py $f m g >> gatech.m_summary
    done

#    echo "mv"
#    mv ../../GaTechAcl/*.summary ./
fi

if [ "$1" == "purdue" ]; then
#    echo "" > purdue.s_summary
#    echo "" > purdue.d_summary
#    echo "" > purdue.m_summary

    for f in  ../../../QoS/PurdueAcl/configs/config*
    do
#	echo "config $f" >> purdue.d_summary
#	python policy_unit.py $f d p >> purdue.d_summary
#	echo "config $f" >> purdue.s_summary
#	python policy_unit.py $f s p >> purdue.s_summary
	echo "config $f" >> purdue.m_summary
	python policy_unit.py $f m p >> purdue.m_summary
    done

fi