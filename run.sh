if [ ! -d "./log/" ];then
  mkdir ./log
fi

# app run
core_num=${CORE_NUM:-5}
time_out=${TIME_OUT:-600}
param_str=${PARAM_STR}

echo "core_num:$core_num"
echo "time_out:$time_out"
echo "param_str:$param_str"

gunicorn -w $core_num -t $time_out -k uvicorn.workers.UvicornWorker $param_str -b 0.0.0.0:39527 main:app