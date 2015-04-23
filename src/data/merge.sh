echo "merge"
for f in  ../../GaTechAcl/*
do
    python merge.py $f
done
