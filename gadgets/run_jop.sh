for div in divs_*_[0-3]
do
    sh -c "
    path=$div
    for i in \$path/divs_?/*.*;
    do
        echo \$i
        bench=\"\${i##*/}\"; ./create_o.sh \$bench \$path 
    done" &
done

