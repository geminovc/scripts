cd ../../post_experiment_process

for person in "needle_drop" "xiran" "kayleigh" "fancy_fueko"
do
    python make_structure_comparison_strip.py --resolution 1024 --person ${person}
done


for person in "tucker" "jen_psaki" "xiran" "xiran_close_up" "needle_drop" "fancy_fueko" "seth_meyer"  "kayleigh" "trever_noah"
do
    python make_structure_comparison_strip.py  --resolution 512 --person ${person} 
done
