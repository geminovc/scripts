cd ..

for person in "needle_drop" "xiran"
do
    python make_structure_comparison_strip.py --generate_video --compute_metrics --resolution 1024 --person ${person}
done


for person in "kayleigh" "xiran_close_up"
do
    python make_structure_comparison_strip.py --generate_video --compute_metrics --resolution 512 --person ${person} 
done
