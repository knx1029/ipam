if [ "$1" == "gatech" ]; then
    for f in  ../../GaTechAcl/*
    do
	echo $f
#       python Acl2Attr.py $f s > ${f}_s.summary
#       python Acl2Attr.py $f d > ${f}_d.summary
	python PolicyUnit.py $f s g > ${f}_unit_s.summary
    done

    echo "mv"
    mv ../../GaTechAcl/*.summary ./
fi

if [ "$1" == "purdue" ]; then
    echo "" > purdue.s_summary
    echo "" > purdue.d_summary

    for f in  ../../PurdueAcl/configs/config*
    do
	echo "config $f" >> purdue.d_summary
	python PolicyUnit.py $f d p >> purdue.d_summary
	echo "config $f" >> purdue.s_summary
	python PolicyUnit.py $f s p >> purdue.s_summary
    done

fi