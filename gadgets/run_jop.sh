for div in divs_*_[0-3]
do
    path=$div
    for i in $path/divs_?/*.*;
    do
        bench="${i##*/}"; ./create_o.sh $bench $path
    done
done

