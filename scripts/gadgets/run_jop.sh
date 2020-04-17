scripts_path=$1
results_path=$2

for div in ${results_path}/divs_*_[0-3]
do
    sh -c "
    path=$div
    for i in \$path/divs_?/*.*;
    do
        echo \$i
        bench=\"\${i##*/}\"; $scripts_path/create_o.sh \$bench \$path $scripts_path
    done" &
done

