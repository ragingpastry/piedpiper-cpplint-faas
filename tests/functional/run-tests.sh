#!/bin/bash


## Supress output from pushd and popd
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

errors=0
for project in \
    success; do

    echo "Running tests on project $project in $(dirname $0)/$project"
	pushd $(dirname $0)
	if [[ -f "${project}.zip" ]]; then
	  echo "Removing leftover zipfile ${project}.zip"
	  rm -f "${project}.zip"
	fi
    zip -qr "${project}".zip $project/*
	results=$(curl -s -F "files=@${project}.zip" http://127.0.0.1:8080/function/piedpiper-cpplint-function)
	expected=(
      'success/src/io_thread.h:5:  #ifndef header guard has wrong style, please use: SRC_IO_THREAD_H_  [build/header_guard] [5]'
      'success/src/io_thread.h:565:  #endif line should be "#endif  // SRC_IO_THREAD_H_"  [build/header_guard] [5]'
      'success/src/io_thread.cc:1148:  Closing ) should be moved to the previous line  [whitespace/parens] [2]'
      'success/src/io_thread.cc:1547:  Missing space around colon in range-based for loop  [whitespace/forcolon] [2]'
      'success/src/io_thread.cc:5:  src/io_thread.cc should include its header file src/io_thread.h  [build/include] [5]'
      'success/src/chrome_content_renderer_client.cc:113:  Include the directory when naming .h files  [build/include_subdir] [4]'
      'success/src/chrome_content_renderer_client.cc:1156:  Use int16/int64/etc, rather than the C type long  [runtime/int] [4]'
      'success/src/chrome_content_renderer_client.cc:1161:  Use int16/int64/etc, rather than the C type long  [runtime/int] [4]'
      'success/src/io_thread.h:5:  #ifndef header guard has wrong style, please use: SRC_IO_THREAD_H_  [build/header_guard] [5]'
      'success/src/io_thread.h:565:  #endif line should be "#endif  // SRC_IO_THREAD_H_"  [build/header_guard] [5]'
      'success/src/io_thread.cc:1148:  Closing ) should be moved to the previous line  [whitespace/parens] [2]'
      'success/src/io_thread.cc:1547:  Missing space around colon in range-based for loop  [whitespace/forcolon] [2]'
      'success/src/io_thread.cc:5:  src/io_thread.cc should include its header file src/io_thread.h  [build/include] [5]'
      'success/src/chrome_content_renderer_client.cc:113:  Include the directory when naming .h files  [build/include_subdir] [4]'
      'success/src/chrome_content_renderer_client.cc:1156:  Use int16/int64/etc, rather than the C type long  [runtime/int] [4]'
	)
    while read -r line ; do
	  found=false
	  for i in "${!expected[@]}"; do
	    if [[ "${line}" == "${expected[i]}" ]]; then
		  unset 'expected[i]'
		  found=true
		fi
	  done
	  if [[ "${found}" == false ]]; then
	    echo "Match not found for line ${line}"
		errors=$((errors+1))
	  fi
    done <<< "${results}"
	if [[ "${#expected[@]}" -ne 0 ]]; then
	  echo "Not all expected results found. ${#expected[@]} leftover"
	  for line in "${expected[@]}"; do
	    echo "Not found: "
		echo "${line}"
	  done
	  errors=$((errors+1))
	fi
    if [[ -f "${project}.zip" ]]; then
      echo "Removing leftover zipfile ${project}.zip"
      rm -f "${project}.zip"
    fi
	popd
done

if [[ "${errors}" == 0 ]]; then
    echo "Tests ran successfully";
    exit 0;
else
    echo "Tests failed";
	exit 1;
fi
